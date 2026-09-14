# Workflow: /audit-research-data

## Inputs
- `doc_id` or `collection`: Scope of audit

## Execution Steps
1. Run `proceedings audit ingestion <doc_id>`.
2. Inspect boundary confidence, unmatched pages, missing metadata, unmapped headings, and stale versions.
3. Report issues cleanly without mutating production JSON files.
