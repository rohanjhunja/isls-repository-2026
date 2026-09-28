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
- Target output format (tabular presentation vs. bulk screening vs. verbatim evidence extraction).

## Procedure
1. Execute pre-flight planning via `plan-data-requirements` to map required output fields to database attributes.
2. Select the appropriate query mode based on the output requirements:
   - **Mode A (User Tables & Paper Selections)**: Project Tier 1 Canonical Projection including `p.citation`.
   - **Mode B (Bulk Aggregation & Screening)**: Project lightweight fields only (`id, year, conference`).
   - **Mode C (Full-Text Evidence Extraction)**: Execute secondary bounded text fetches (`substr(text, 1, N)`).
3. Query SQLite `proceedings.db` (`papers`, `sections`, `authors`, `paper_authors`, `papers_fts`).
4. Apply **Strict Presentation-Query Parity**: Confirm all displayed fields exist in the query result; run secondary point lookups if any presentation field is missing.
5. Format user-facing output using the **Source Sigil System** (`◈`, `◇`, `⌕`, `✦`) at the highest structural level, labeled with `Source:`.

## Query Modes & SQL Templates

### Mode A: User-Facing Tabular Listings & Selections (Tier 1 Canonical Projection)
Mandated whenever presenting papers in markdown tables, selection lists, or review summaries (~40 tokens/paper):
```sql
SELECT p.id, p.title, p.citation, p.year, p.conference, p.paper_type, p.doi, p.handle_url, p.start_page, p.end_page
FROM papers p
WHERE ...
```
*Guarantees*: 100% verified author names, correct author order, volume, and pagination with zero joins.

### Mode B: Bulk Aggregations, Counts, and Screening (Lightweight Projection)
Mandated when computing distributions, counting papers, or running broad screening sweeps across hundreds of papers:
```sql
SELECT p.id, p.year, p.conference
FROM papers p
WHERE ...
```
*Guarantees*: Zero context window bloat during bulk sweeps (~5 tokens/paper).

### Mode C: Full-Text Drilldown & Evidence Extraction (Secondary Bounded Fetches)
Secondary fetch executed only after shortlisting target papers:
```sql
SELECT paper_id, original_heading, pdf_start_page, substr(text, 1, 500) AS bounded_text, length(text) AS full_len
FROM sections
WHERE paper_id IN (?) AND normalized_section = 'methodology';
```
Or for keyword context locating:
```sql
SELECT paper_id, section_title, snippet(papers_fts, 5, '<b>', '</b>', '...', 25) AS match_snippet
FROM papers_fts
WHERE papers_fts MATCH '<keyword>' LIMIT 20;
```

## Memory Safety & High Data Volume Guidelines
- **Dual-Mode Projections**: Use Mode A for presentation tables and Mode B for large-scale filtering/aggregations. Never dump `p.citation` across hundreds of papers unless tabular display is required.
- **Bounded Text Slices**: Always slice section text (`substr(text, 1, N)`) or use FTS5 `snippet()` when extracting evidence. Never execute unbounded `SELECT text FROM sections` across multi-paper sets.
- **Indexed Search First**: Always prefer SQLite FTS5 queries against `proceedings.db` instead of loading entire volume JSON or Markdown files into memory.

## Guardrails
- **Strict Presentation-Query Parity**: Never generate or infer authors, DOIs, page ranges, or paper types from parametric memory. If a field was omitted from the query, run a secondary point lookup or omit the field.
- **Source Sigils at Highest Structural Level**:
  - `◈` Database Ground Truth | `◇` Database-Derived Metric | `⌕` Verbatim Evidence Quote | `✦` Agentic Synthesis.
  - Column headers take sigils for homogeneous columns; trailing end-of-string/paragraph for mixed/prose.
  - Never wrap sigils in dedicated brackets (use `✦⌕`, not `[✦⌕]`).
  - Label explanatory footer as `Source: ◈ Database Record | ◇ Database-Derived Metric | ⌕ Verbatim Section Evidence | ✦ Agent-Synthesized Coding`.

