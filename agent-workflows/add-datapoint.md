# Workflow: /add-datapoint

## Inputs
- `property_id`: Property identifier
- `collection`: Target collection
- `years`: Target year range

## Execution Steps
1. Reuse or define research property (`define-research-property`).
2. Resolve candidate sections in SQLite index.
3. Run property extraction (`proceedings property extract <property_id>`).
4. Validate observations and evidence.
5. Refresh affected views.
