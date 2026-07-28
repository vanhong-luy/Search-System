"""
Ingestion: load raw documents from disk and split them into overlapping chunks.

This version walks category subfolders (e.g. data/terraria/bosses,
data/terraria/items, data/terraria/events) and tags every document with its
folder name as `category`, so retrieval, citations, and the UI can all filter
or display by category later without any extra bookkeeping.

Upgrade path (for your final project):
- Add PDF/HTML loaders (e.g. pypdf, BeautifulSoup) alongside .txt/.md
- Swap the naive word-count chunker below for a sentence- or token-aware chunker
- Store more document metadata (source URL, author, date) alongside each chunk
"""

import os
from dataclasses import dataclass
from typing import List, Optional, Tuple

SUPPORTED_EXTENSIONS = (".txt", ".md")


@dataclass
class Chunk:
    chunk_id: str
    doc_title: str
    category: str
    section: Optional[str]
    text: str


def load_documents(folder: str) -> List[dict]:
    """Load every .txt/.md file under `folder`, walking one level of category
    subfolders, into {"title": ..., "category": ..., "text": ...} dicts.

    Expected layout:
        folder/
            bosses/king_slime.md
            items/...
            events/...

    Files directly in `folder` (no subfolder) get category "general".
    """
    docs = []
    for root, _dirs, filenames in os.walk(folder):
        for filename in sorted(filenames):
            if not filename.endswith(SUPPORTED_EXTENSIONS):
                continue
            path = os.path.join(root, filename)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read().strip()
            title = os.path.splitext(filename)[0].replace("_", " ").title()
            ext = os.path.splitext(filename)[1]
            rel_dir = os.path.relpath(root, folder)
            category = "general" if rel_dir == "." else rel_dir.replace(os.sep, "/")
            docs.append({"title": title, "category": category, "text": text, "ext": ext})
    return docs


def chunk_text(text: str, chunk_size: int = 80, overlap: int = 20) -> List[str]:
    """Split text into overlapping word-count chunks (simple, dependency-free).
    Used as the fallback for plain .txt files with no header structure."""
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = end - overlap
    return chunks


def chunk_markdown_sections(text: str) -> List[Tuple[str, str]]:
    """Section-aware chunking for '## '-structured markdown (e.g. wiki-style docs).

    One '## ' section (its header + everything under it, up to the next '## ')
    becomes one chunk. This keeps each chunk topically coherent (e.g. "Spawn
    Condition" never gets split mid-thought the way fixed word-count chunking
    would), which matters for a domain like this where the header itself is
    half the meaning.

    Returns a list of (section_title, section_text) tuples. Any content before
    the first '## ' header (e.g. a '# Title' line or intro line) is folded into
    the first real section rather than kept as its own near-empty chunk.
    """
    lines = text.split("\n")
    sections: List[Tuple[str, List[str]]] = []
    preamble: List[str] = []

    for line in lines:
        if line.startswith("## "):
            sections.append((line[3:].strip(), [line]))
        elif sections:
            sections[-1][1].append(line)
        else:
            preamble.append(line)

    if not sections:
        # No '## ' headers at all - treat the whole doc as one section.
        return [("Overview", text.strip())] if text.strip() else []

    if preamble and preamble[0].strip():
        sections[0] = (sections[0][0], preamble + sections[0][1])

    return [(title, "\n".join(body).strip()) for title, body in sections if "\n".join(body).strip()]


def build_chunk_records(docs: List[dict], chunk_size: int = 80, overlap: int = 20) -> List[Chunk]:
    """Turn loaded documents into a flat list of Chunk records ready for embedding.

    .md docs use section-aware chunking (split on '## ' headers).
    .txt docs fall back to fixed-size word-count chunking.
    """
    records = []
    for doc in docs:
        if doc.get("ext") == ".md":
            sections = chunk_markdown_sections(doc["text"])
            for i, (section_title, piece) in enumerate(sections):
                records.append(Chunk(
                    chunk_id=f"{doc['category']}/{doc['title']}::{i}",
                    doc_title=doc["title"],
                    category=doc["category"],
                    section=section_title,
                    text=piece,
                ))
        else:
            pieces = chunk_text(doc["text"], chunk_size=chunk_size, overlap=overlap)
            for i, piece in enumerate(pieces):
                records.append(Chunk(
                    chunk_id=f"{doc['category']}/{doc['title']}::{i}",
                    doc_title=doc["title"],
                    category=doc["category"],
                    section=None,
                    text=piece,
                ))
    return records
