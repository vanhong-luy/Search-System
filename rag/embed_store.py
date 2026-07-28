"""
Vector store: turn chunks into vectors and support similarity search over them.

This version uses real sentence embeddings (all-MiniLM-L6-v2, via
sentence-transformers) instead of TF-IDF, so retrieval is based on semantic
meaning rather than literal word overlap. This is what fixes cases like a
query such as "need strategy" failing to rank a section titled "Strategies"
highly under TF-IDF, since there's no literal shared vocabulary for TF-IDF to
latch onto but a real embedding model captures the meaning.

Upgrade path beyond this:
- Swap the in-memory cosine similarity search below for FAISS or Chroma once
  your chunk count grows past a few thousand.
- Keep the VectorStore interface (`build`, `query`) the same so app.py doesn't
  need to change.

Note: the first run will download the model (~90MB) from Hugging Face, so it
needs an internet connection once; after that it's cached locally and loads
offline.
"""

from typing import List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer

from .ingest import Chunk

MODEL_NAME = "all-MiniLM-L6-v2"


class VectorStore:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model = SentenceTransformer(model_name)
        self.embeddings = None  # L2-normalized (n_chunks, dim) matrix
        self.chunks: List[Chunk] = []

    def build(self, chunks: List[Chunk]) -> None:
        """Embed all chunk text and store the resulting normalized matrix."""
        self.chunks = chunks
        texts = [c.text for c in chunks]
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1  # avoid divide-by-zero on any empty chunk
        self.embeddings = embeddings / norms

    def query(self, query_text: str, top_k: int = 3) -> List[Tuple[Chunk, float]]:
        if self.embeddings is None:
            raise RuntimeError("VectorStore.build() must be called before query().")

        query_vec = self.model.encode([query_text], convert_to_numpy=True, show_progress_bar=False)[0]
        norm = np.linalg.norm(query_vec)
        if norm > 0:
            query_vec = query_vec / norm
        scores = self.embeddings @ query_vec

        # If the query clearly names one doc title (e.g. "Eye of Cthulhu"),
        # restrict candidates to that doc's chunks first. This matters because
        # semantic similarity alone can't distinguish "Eye of Cthulhu strategy"
        # from "Brain of Cthulhu strategy" — both are about killing a Cthulhu
        # boss, so word-overlap on the *boss name itself* has to be the tiebreaker.
        query_lower = query_text.lower()
        doc_titles = {c.doc_title for c in self.chunks}
        matched_titles = [t for t in doc_titles if t.lower() in query_lower]

        if matched_titles:
            candidate_idx = [i for i, c in enumerate(self.chunks) if c.doc_title in matched_titles]
        else:
            candidate_idx = list(range(len(self.chunks)))

        ranked = sorted(candidate_idx, key=lambda i: scores[i], reverse=True)[:top_k]
        return [(self.chunks[i], float(scores[i])) for i in ranked]
