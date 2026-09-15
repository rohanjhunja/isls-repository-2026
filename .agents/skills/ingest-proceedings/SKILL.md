---
name: ingest-proceedings
description: Register a new PDF, select/profile its template, ingest into structured layout & Markdown, detect paper boundaries, extract metadata & canonical sections, validate against Pydantic schemas, and build the SQLite FTS5 search index following repository naming conventions.
---

# Skill: ingest-proceedings

## Purpose & Responsibility
Register a new PDF, select/profile its template, ingest into structured layout & Markdown, detect paper boundaries, extract metadata & canonical sections, validate against Pydantic schemas, and build the SQLite FTS5 search index following standardized naming conventions.

## Naming & Path Conventions (MANDATORY)
Before registering or ingesting any new document, enforce these strict naming rules:
1. **Source PDF Filename**: Must be renamed to kebab-case `<conference>-<year>-proceedings.pdf` (e.g. `cscl-2025-proceedings.pdf`, `icls-2026-proceedings.pdf`, `isls-2026-proceedings.pdf`).
2. **Volume ID**: Must match the stem `<conference>-<year>-proceedings` (e.g. `cscl-2025-proceedings`).
3. **Source Storage**: Saved under `data/sources/<conference>-<year>-proceedings.pdf` and copied to `pdf/<conference>-<year>-proceedings.pdf`.
4. **Derived Directory & JSON**: `data/derived/<volume_id>/` containing `<volume_id>.json` where every paper's `filename` attribute is set to `<conference>-<year>-proceedings.pdf`.
5. **Ingestion Audit Report**: Saved as `data/reports/ingestion_<volume_id>.json` with `source_filename` set to `<conference>-<year>-proceedings.pdf`.

## Required Inputs
- PDF file path or filename in `data/incoming/` or `pdf/`.
## Procedure

### A. Fast 10-Year Database Population (Local Setup / Rebuild)
To build the complete SQLite FTS5 database (~112 MB) and review viewer caches from the bundled 10-year golden dataset (`data/derived/ground_truth_registry.json`, ~10 MB):
```bash
# 1. Populate proceedings.db (5,402 papers, authors, sections, FTS5 index)
python3 scripts/populate_10yr_database.py

# 2. Precompute review viewer caches and aggregations
python3 scripts/build_all_reviews_cache.py
```

### B. Upstream 10-Year Corpus Re-Harvest & Extraction (From Scratch)
If re-harvesting the 10-year corpus (2016–2026) directly from DSpace and raw source PDFs:
1. **DSpace Ground-Truth Harvesting (2016–2025)**: Execute `python3 scripts/harvest_2016_2025.py` to harvest clean Dublin Core metadata (titles, authors, DOIs, page ranges, handle URLs) directly from DSpace repository into `data/derived/ground_truth_registry.json`.
2. **Pre-2023 Section Extraction**: Run `python3 scripts/ingest_pre2023_sections.py` to extract canonical section hierarchies from harvested papers.
3. **2026 Boundary Harvesting & Repair**: For 2026 monolithic proceedings PDFs, run `python3 scripts/clean_and_populate_2026.py` and `python3 scripts/repair_2026_leaked_titles_and_authors.py` to segment and verify paper boundaries against TOC entries.
4. **Text Reflow & Glitch Repair**: Run `python3 scripts/clean_and_reflow_all_repository_text.py` to remove hyphenation splits and OCR artifacts.
5. **Populate Database**: Execute `python3 scripts/populate_10yr_database.py` and `python3 scripts/build_all_reviews_cache.py`.

### C. Ingesting a New Single Volume (e.g. Future Conference)
- `python3 -m proceedings_ingest.cli register <pdf_path>`
- `python3 -m proceedings_ingest.cli preflight <doc_id>`
- `python3 -m proceedings_ingest.cli ingest <doc_id> --max-memory-gb 8.0`
- `python3 -m proceedings_ingest.cli audit ingestion <doc_id>`

## Memory Safety & High Data Volume Guidelines
- **Process RSS Memory Limits**: Always specify `--max-memory-gb` (default 8.0 GB) during large PDF ingestion to prevent OS memory exhaustion.
- **Stream Manifest Writes**: Write block manifests directly to disk line-by-line rather than accumulating raw block arrays in RAM.
- **Eager Cleanup**: Explicitly release `pypdf.PdfReader` handles and trigger `gc.collect()` after extracting page layout blocks.
- **Low Concurrency**: Use single-process execution or `max_workers=1` for PDF parsing on macOS to prevent RAM duplication.
- **IDE Watcher Exclusions**: Ensure `.vscode/settings.json` excludes `data/`, `pdf/`, and `derived/` from file watching and indexing.

## Guardrails
- Source PDFs are immutable once registered.
- Never use spaces, uppercase letters, or arbitrary text (like `- Oct3`) in PDF filenames or volume IDs.
- Never silently drop unmapped text; log unassigned regions.
- Ensure every paper has exact page provenance.
- Enforce hard RSS memory checks during multi-stage ingestion loops.

