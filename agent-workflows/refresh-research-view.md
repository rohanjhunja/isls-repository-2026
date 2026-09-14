# Workflow: /refresh-research-view

## Inputs
- `view_id`: View identifier
- `formats`: `csv`, `xlsx`

## Execution Steps
1. Load view definition from `views/<view_id>.yaml`.
2. Re-materialize query against SQLite FTS index & observations.
3. Export CSV and openpyxl formatted XLSX.
