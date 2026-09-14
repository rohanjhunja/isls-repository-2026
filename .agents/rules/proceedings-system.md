# Proceedings Research System Rules

- **Dipstick Pre-Check Mandatory**: Dipstick review is the foundational first step for all literature reviews. The system MUST check if the target review is a dipstick review (or verify that an initial dipstick review has been conducted) before performing any further actions, such as deep property extractions, section parsing, or synthesis reports.
- Source PDFs are immutable. Profiles, schemas, properties, and views are version-controlled.
- Enforce the standard naming convention `<conference>-<year>-proceedings.pdf` and matching volume ID `<conference>-<year>-proceedings` for all incoming/ingested PDFs, derived directories, datasets, and audit reports.
- Use the supported Python CLI for ingestion, extraction, validation, indexing, and export.
- Do not directly edit generated JSON, observations, SQLite, dashboards, or spreadsheets.
- Prefer YAML/profile changes over Python; add code only for a new reusable strategy.
- Preserve exact source text and original headings. Never invent missing values.
- Every datapoint requires traceable evidence and a valid extraction state.
- Query indexed candidate sections before opening complete papers or proceedings.
- OCR only pages without usable embedded text.
- A new research question normally creates a property definition, not a core schema field.
- Version rule and property changes; rerun only affected stages or records.
- Do not overwrite manually verified observations automatically.
- Dashboards and spreadsheets are generated views, not authoritative sources.
- Run relevant tests and validation after every rule, schema, property, or code change.
- Report targeted, extracted, not-present, unresolved, ambiguous, and warning counts.
