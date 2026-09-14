---
name: publish-research-views
description: Create or update view definitions in YAML and generate dashboard data tables, CSV, and Excel workbooks from validated records.
---

# Skill: publish-research-views

## Purpose & Responsibility
Create or update view definitions in YAML and generate dashboard data tables, CSV, and Excel workbooks from validated records.

## Required Inputs
- View name / ID.
- Row grain, requested columns, filters, and export formats.

## Procedure
1. Create or update view YAML in `views/<view_id>.yaml`.
2. Materialize view from FTS5 index and observation store.
3. Export CSV files and openpyxl formatted XLSX workbooks.
4. Support Streamlit dashboard data source updates.

## Supported CLI Commands
- `python3 -m proceedings_ingest.cli view build <view_id>`
- `python3 -m proceedings_ingest.cli export csv <review_id> --max-memory-gb 8.0`
- `python3 -m proceedings_ingest.cli export xlsx <view_id> --max-memory-gb 8.0`

## Memory Safety & High Data Volume Guidelines
- **Chunked Exporting**: Stream CSV/DataFrame output rows in chunks (`chunksize=500` or generator-based table building) when exporting large literature reviews.
- **Resource Cleanup**: Release temporary table DataFrames and call garbage collection (`gc.collect()`) prior to writing large output files or ZIP bundles.

## Guardrails
- Views are derived from canonical JSON/observations and SQLite index; views are never sources of truth.
- Always monitor process RSS memory when generating large exported workbooks or ZIP archives.

