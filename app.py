"""
RAG-Based AI Search System — starter interface.

Run with:
    streamlit run app.py

This gives you a working, end-to-end demo today: document loading, TF-IDF based
retrieval, and an extractive answer — all wired into a real web interface. Build
your final project by upgrading each piece (see the TODOs in rag/embed_store.py
and rag/generate.py) without needing to touch this file's overall structure.
"""

import streamlit as st

from rag.ingest import load_documents, build_chunk_records
from rag.embed_store import VectorStore
from rag.generate import generate_answer

DATA_FOLDER = "data/terraria"

st.set_page_config(page_title="RAG Search", page_icon="🌳", layout="wide")


@st.cache_resource(show_spinner="Loading and indexing documents...")
def load_store():
    docs = load_documents(DATA_FOLDER)
    chunks = build_chunk_records(docs)
    store = VectorStore()
    store.build(chunks)
    return store, docs, chunks


store, docs, chunks = load_store()

categories = sorted({d["category"] for d in docs})

with st.sidebar:
    st.header("Settings")
    top_k = st.slider("Number of chunks to retrieve", min_value=1, max_value=10, value=3)
    mode = st.radio("Answer mode", ["llm", "extractive"], index=0,
                     help="LLM gives a real grounded answer (needs GEMINI_API_KEY). "
                          "Extractive just shows raw retrieved passages, useful for debugging retrieval.")
    category_filter = st.selectbox("Category", ["All"] + categories,
                                    help="Limit retrieval to a single category, e.g. just bosses.")
    st.divider()
    st.caption(f"Indexed **{len(docs)}** documents \u2192 **{len(chunks)}** chunks")
    with st.expander("Documents in this index"):
        for d in docs:
            st.write(f"- [{d['category']}] {d['title']}")

st.title("TERRA")
st.caption("🔎 A RAG-Based AI Search System.  \n Ask a question about the indexed documents below.")

query = st.text_input("Your question", placeholder="e.g. Help me prepare for Eye of Cthulhu")
search_clicked = st.button("Search", type="primary")

if search_clicked and query.strip():
    # Retrieve extra candidates when a category filter is active, since we
    # filter after ranking rather than re-searching a narrowed index.
    fetch_k = top_k if category_filter == "All" else max(top_k * 5, 20)
    raw_retrieved = store.query(query, top_k=fetch_k)
    if category_filter != "All":
        raw_retrieved = [(c, s) for c, s in raw_retrieved if c.category == category_filter]
    retrieved = raw_retrieved[:top_k]

    answer = generate_answer(query, retrieved, mode=mode)

    st.subheader("Answer")
    st.write(answer)

    st.subheader("Sources")
    if not retrieved:
        st.info("No relevant sources found for that query.")
    for chunk, score in retrieved:
        section_label = f" \u2013 {chunk.section}" if chunk.section else ""
        with st.expander(f"[{chunk.category}] {chunk.doc_title}{section_label}  \u00b7  similarity {score:.2f}"):
            st.write(chunk.text)
elif search_clicked:
    st.warning("Type a question first.  \n I suggest something related to boss prepation.  \n Or go play the game first.")
