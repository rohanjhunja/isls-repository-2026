# Workflow: /add-proceedings

## Inputs
- `pdf_path`: Path to source PDF in `data/incoming/`
- `collection`: Collection / Conference acronym (e.g., `ISLS`)
- `year`: Conference year (e.g., `2026`)
- `doc_type`: `conference_proceedings` or `journal`

## Execution Steps
1. Register source PDF (`proceedings register <pdf_path>`).
2. Run preflight to inspect layout & select profile (`proceedings preflight <doc_id>`).
3. If no matching profile exists, invoke `profile-proceedings` skill.
4. Execute ingestion (`proceedings ingest <doc_id>`).
5. Run audit (`proceedings audit ingestion <doc_id>`).
6. Update search index (`proceedings index update`).
7. Output summary report & low-confidence boundary warnings.
