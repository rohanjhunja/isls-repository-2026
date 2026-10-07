---
name: search-literature
description: Store search criteria, translate search prompts into keywords, score matches, resolve review paper scopes, and initialise required Python servers and cache scripts so localhost displays reviews in time.
---

# Skill: search-literature

## Purpose & Responsibility
Store search criteria, translate search prompts into keywords, score matches, resolve review paper scopes, and route to the appropriate review pathway.

## Review Routing Architecture & Explicit Triggers

The search system routes queries across four pathways based on explicit triggers or contextual triage:

| Pathway | Explicit Trigger Words & Phrases | Default Operational Behavior |
| :--- | :--- | :--- |
| **Pathway 1: Deterministic Dipstick Review** | `'dipstick'`, `'dipstick review'`, `'quick search'`, `'sweep'`, `'bm25'`, `'fts5 search'`, `'title/abstract'`, `'title search'`, `'fast scan'`, `'reconnaissance'`, `'keyword search'` | Zero-token lexical BM25 search across Titles and Abstracts (`title,abstract`) in SQLite `proceedings.db`. Instantaneous ($< 3\text{ ms}$), zero LLM token consumption. |
| **Pathway 2: Deterministic Section Extraction** | `'extract property'`, `'property extraction'`, `'regex extract'`, `'sample size'`, `'sample sizes'`, `'factual metadata'`, `'grade levels'`, `'named tools'`, `'extract numbers'`, `'count occurrences'`, `'demographics'` | Target specific canonical sections (`methods`, `results`) using FTS5 section roles or regex capture. Strictly factual/numerical. |
| **Pathway 3: Full In-Context Agentic Review** | `'agentic review'`, `'agentic reviews'`, `'ai-search'`, `'dual agent'`, `'consider the full text'`, `'read full text'`, `'read sections'`, `'qualitative coding'`, `'interpretive review'`, `'thematic analysis'`, `'attribution test'`, `'code-design framework'`, `'agency analysis'` | Ingest unabridged paper prose directly into LLM prompt context (~4k–10k tokens/paper). Scoped to full paper or explicitly designated sections (`--sections`). |
| **Pathway 4: Staged Hybrid Review** | `'hybrid review'`, `'screen and synthesize'`, `'filter and read'`, `'dipstick then review'`, `'two-stage review'`, `'sweep then code'`, `'screen then analyze'`, `'filter then code'` | Two-stage pipeline: Stage 1 deterministic BM25 screening sweep across 100% of corpus to isolate $N$ candidate papers $\rightarrow$ Stage 2 in-context qualitative coding of the qualified candidates. |

### Contextual Methodological Triage (When Triggers Are Absent)
When user instructions do not contain explicit trigger words, the agent evaluates the **epistemic nature of the inquiry**:
- If asking for factual statistics, paper counts, author lists, or named tools $\rightarrow$ Route to **Pathway 1 or 2**.
- If asking for interpretive meaning, teacher agency, pedagogical scaffolding, or qualitative rationales $\rightarrow$ Route to **Pathway 3**.
- If asking an open-ended research question across the 10-year corpus $\rightarrow$ Route to **Pathway 4 (Staged Hybrid)**.

## Downstream Deterministic Data Invariants
Regardless of whether upstream routing was deterministic or agentic, all retrieved and persisted records must adhere to strict downstream invariants:
1. **Mode A Tier 1 Projections**: All tabular outputs must project canonical metadata (`p.id, p.title, p.citation, p.year, p.conference, p.paper_type, p.doi, p.handle_url, p.start_page, p.end_page`) from SQLite `proceedings.db`.
2. **Verbatim Substring Assertion**: Any text quote cited in output or persisted in reviews must be verified: `assert instr(full_text, quote) > 0`.
3. **Exact Calculations**: All counts, frequencies, and metrics must be computed deterministically via Python (`◇`).

## Scoping & Translation Rules

1. **Keyword Translation**:
   - Translate research queries into explicit keywords for deterministic search when running Pathway 1, Pathway 2, or Stage 1 of Pathway 4.
2. **Search Scope Default**:
   - Scope search targets to **Title** and **Abstract** (`title,abstract`) for Pathway 1.
   - Expand to full text / sections search (`sections`) for Pathway 2, 3, or 4.
3. **Metadata Filtering**:
   - Apply strict filtering on year, conference acronym/name, journal, and collection.
4. **Saved Review Naming Rule**:
   - Standard title and abstract scope reviews MUST be named: `'Dipstick Review - <keyword(s)>'`.
   - Reviews created from expanded full-text or section searches MUST be named: `'Expanded Scope - <keyword(s)>'`.
   - Reviews involving LLM qualitative coding or agentic review MUST be named: `'Agentic Review - <keyword(s)>'`.
   - Reviews combining screening and qualitative synthesis MUST be named: `'Hybrid Review - <keyword(s)>'`.

## Mandatory Method Reporting Standard
On completion of any search or paper retrieval, report the exact execution method badge:
- **Execution Method**: `◈ Deterministic Dipstick (FTS5 BM25)` | `◈ Deterministic Section Extraction` | `◈ Full In-Context Agentic Review` | `◈ Staged Hybrid Review`
- **Text Coverage**: Title/Abstract Only | Candidate Sections Only | Specified Sections Only (`<sections>`) | Full Paper Prose (All Sections)
- **Epistemic Standard**: `◇ Lexical BM25 Ranking` | `⌕ 100% Exact DB Substring Match Verified`
- **Attribution Status**: N/A (Search/Factual) | Disaggregated Teacher Agency Verified (4-Part Test)

## Workflow

1. Accept natural language research prompt or query terms.
2. Check for **Explicit Pathway Trigger Words**.
   - If a trigger is present, route immediately to the specified pathway.
   - If no trigger is present, conduct **Step 0: Contextual Methodological Triage** to select the optimal pathway.
3. For Pathway 1 (or Stage 1 of Hybrid): Execute **Zero-Token Lexical BM25 Search** (`search_lexical_bm25`) against SQLite `proceedings.db` with fielded weights (`title × 8`, `keywords × 6`, `abstract × 5`, `section_title × 3`, `body × 1`).
4. Apply metadata filters (`min_year`, `max_year`, `conference`, `paper_type`, `normalized_section`).
5. Apply dual sorting: `sort_by='relevance'` (BM25 / cross-encoder rank score) or `sort_by='year'` (publication year DESC/ASC).
6. Apply local Cross-Encoder Reranker over top candidates when relevance ranking is requested.
7. For Pathway 3 (or Stage 2 of Hybrid): Ingest unabridged prose for the qualified paper IDs from SQLite `sections` into prompt context and verify all quotes downstream via `instr()`.
8. Save resolved scope, paper IDs, and search definition to review metadata (`.json`) and Markdown summary (`.md`).
9. **Python Script Auto-Initialization**:
   - Verify web server (`server.py`) is running on port 8888 (`curl -s --noproxy '*' http://localhost:8888/api/reviews`). If inactive, start `python3 server.py --port 8888`.
   - Execute `python3 scripts/build_all_reviews_cache.py` so the new review renders immediately on localhost.

