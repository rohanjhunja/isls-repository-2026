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
1. **DSpace Ground-Truth Harvesting (2023–2025)**: Execute `python scripts/harvest_ground_truth.py` to harvest clean Dublin Core metadata (titles, authors, DOIs, page ranges, handle URLs) directly from DSpace using `curl_cffi` into `data/derived/ground_truth_registry.json`.
2. **Fallback Boundary Harvesting (2026)**: For years without individual DSpace item records, extract ground-truth table of contents entries directly from monolithic proceedings PDFs.
3. **Normalize Proceedings Markdown**: Ensure source proceedings Markdown files are saved under `proceedings_md/<conference>-<year>.md`.
4. **Verified Markdown Chunking**: Slice proceedings `.md` files into paper records by matching headers and page ranges against `ground_truth_registry.json`.
5. **Section Parser & Dual Labeling**: Extract section blocks preserving both `original_heading` and `normalized_section`.
6. **Validate Schema**: Validate output records against `Paper` and `GroundTruthPaper` Pydantic schemas.
7. **Update SQLite FTS5 Index**: Index validated paper sections in `proceedings.db`.
8. **Audit Report**: Generate ingestion audit report comparing detected paper count against ground-truth registry.
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

