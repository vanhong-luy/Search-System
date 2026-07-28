# TERRA

A Retrieval-Augmented Generation (RAG) search system over Terraria wiki-style content - ask questions mainly about bosses and events overview, how to spawn/trigger, strategies and items preparation inlcuding weapons, acessories potions, and armor, with a grounded answers along with the sources.

## Overview

TERRA lets players query a curated Terraria knowledge base in natural language ("How do I beat the Eye of Cthulhu?", "What does the Frost armor set bonus do?") and get an answer generated from the most relevant retrieved passages, rather than a raw wiki dump.

## Stack

- **Interface:** Streamlit
- **Embeddings:** sentence-transformers (`all-MiniLM-L6-v2`)
- **Vector store:** in-memory cosine similarity search
- **Generation:** Gemini (with a list of candidate models and fallback if one is unavailable)

## Project Structure

```
Final Project (with llm)/
├── rag/
│   ├── ingest.py        # loads and chunks markdown docs
│   ├── embed_store.py   # embedding + similarity search, title-match filtering
│   └── generate.py      # prompts Gemini with retrieved context
├── data/
│   └── terraria/
│       ├── bosses/      # 18 files
│       ├── events/      # 12 files
│       ├── items/       # 10 dense files
└── app.py                # Streamlit entry point
```

## Data

Content is organized under `data/terraria/` by category. Each markdown file uses `## `-level section headers per topic (e.g. Overview, Strategies) so chunking stays section-aware rather than splitting mid-topic. Weapon data (413 items) was generated from the Terraria-Dataset-master JSON dataset and grouped alphabetically into 7 files.

### Weapon Dataset source

- A github repository by natan-dot-com and Andrei Alisson
- Link to GitHub: [Click Here](https://github.com/natan-dot-com/Terraria-Dataset/tree/master)

## How Retrieval Works

- A query is embedded with `all-MiniLM-L6-v2`.
- Candidate chunks are ranked by cosine similarity against the in-memory store.
- If the query names a specific entity (e.g. a boss), a title-match filter restricts candidates to that entity's document first - this was added after boss-specific chunks (e.g. Eye of Cthulhu - Strategies) were losing to other bosses' chunks on pure semantic similarity alone.
- The top chunks are passed to Gemini to generate the final answer.

## Known Limitations

- Boss and event drop data exists in the source dataset but due to time constraint and not related to boss preparation itself, the queries will still retrieved them correctly in testing, but will not show any further details for certain items. In a word, it shows you what the boss/event drop, but not what it does.

## Running It

```bash
pip install -r requirements.txt
streamlit run app.py
```

Set Gemini API key as an environment variable before running:

set GEMINI_API_KEY="" # not here actually, use your cmd, also no "" when use api key btw

btw, idk what I just did, but DO NOT delete bread.gif, otherwise everthing will break\n  
Keep it as it is and things will be fine\n  
cheers.
