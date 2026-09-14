---
name: search-literature
description: Store search criteria, translate search prompts into keywords, score matches, resolve review paper scopes, and initialise required Python servers and cache scripts so localhost displays reviews in time.
---

# Skill: search-literature

## Purpose & Responsibility
Store search criteria, translate search prompts into keywords, score matches, and resolve review paper scopes.

## Scoping & Translation Rules

1. **Keyword Translation**:
   - Translate research queries into explicit keywords for deterministic search unless AI search (`ai_search_enabled=True`) is requested.
2. **Search Scope Default**:
   - Scope search targets to **Title** and **Abstract** (`title,abstract`) by default.
   - Expand to full text / sections search (`sections`) only when explicitly requested.
3. **Metadata Filtering**:
   - Apply strict filtering on year, conference acronym/name, journal, and collection.

## Workflow

1. Accept natural language research prompt or query terms.
2. Execute **Zero-Token Lexical BM25 Search** (`search_lexical_bm25`) against SQLite `proceedings.db` with fielded weights (`title × 8`, `keywords × 6`, `abstract × 5`, `section_title × 3`, `body × 1`).
3. Apply metadata filters (`min_year`, `max_year`, `conference`, `paper_type`, `normalized_section`).
4. Apply dual sorting: `sort_by='relevance'` (BM25 / cross-encoder rank score) or `sort_by='year'` (publication year DESC/ASC).
5. Apply local Cross-Encoder Reranker (`rerank_candidates` using `cross-encoder/ms-marco-MiniLM-L-6-v2`) over top 50 candidates to produce top 10–20 high-precision matches.
6. Resolve matching candidate papers with section snippets, page numbers, and DOI/handle URLs for Dipstick review tables.
7. Save resolved scope, paper IDs, and search definition to review metadata (`.json`) and Markdown summary (`.md`).
5. **Python Script Auto-Initialization**:
   - Check if web server (`server.py`) is running on port 8888 (`curl -s --noproxy '*' http://localhost:8888/api/reviews`). If inactive, start `python3 server.py --port 8888` with `BypassSandbox: true`.
   - Initialise required data preparation scripts (`python3 scripts/prepare_viewer_data.py`) so the new search scope and review display immediately on localhost.

