---
name: query-repository-data
description: Directly query, search, filter, and summarize papers, proceedings metadata, observations, and index tables in the repository using standardized volume naming conventions.
---

# Skill: query-repository-data

## Purpose & Responsibility
Perform fast, direct lookups across ingested proceedings, paper collections, SQLite FTS index, and research observations. Use this skill whenever inspecting available papers, retrieving paper metadata, searching for topics, or summarizing repository holdings.

## Naming & Path Conventions
- Volume IDs and dataset directories follow standard format: `<conference>-<year>-proceedings` (e.g. `cscl-2025-proceedings`, `icls-2026-proceedings`, `isls-2026-proceedings`).
- Volume JSON files follow: `data/derived/<volume_id>/<volume_id>.json`.
- PDF filenames follow: `<conference>-<year>-proceedings.pdf`.

## Required Inputs
- Target scope (all volumes, specific volume, or query string).
- Optional metadata filters (year, conference, author, topic keyword).

## Procedure
1. Inspect available proceedings volumes under `proceedings.db` and ground truth registry under `data/derived/ground_truth_registry.json`.
2. Query `proceedings.db` SQLite database (`papers`, `authors`, `paper_authors`, `sections`, `papers_fts`).
3. Retrieve title, authors, DOIs, dual section headings (`original_heading`, `normalized_section`), page provenance, and abstract content.
4. Format output clearly as markdown summaries or comparative metrics.

## Direct Query Commands
- Search indexed FTS5 BM25: `python3 -c "from proceedings_ingest.lexical_search import search_lexical_bm25; print(search_lexical_bm25('<query>'))"`
- Query relational database: `sqlite3 proceedings.db "SELECT id, title, year, doi FROM papers WHERE year >= 2023 LIMIT 10;"`

## Memory Safety & High Data Volume Guidelines
- **Indexed Search First**: Always prefer SQLite FTS5 queries against `data/index/proceedings.db` instead of loading entire volume JSON or Markdown files into memory.
- **Selective Field Loading**: Fetch specific columns/fields required for queries rather than reading full paper section text objects into context.

## Guardrails
- Prefer indexed SQLite queries over loading full markdown proceedings files into context.
- Report exact confidence scores and page ranges when referencing paper evidence.
- Avoid holding multi-volume raw text collections in RAM simultaneously during query evaluation.

