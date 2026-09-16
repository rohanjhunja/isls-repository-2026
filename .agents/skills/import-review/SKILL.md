---
name: import-review
description: Integrate an external literature review file, .isls-review.json bundle, or .zip archive into the user's local workspace. Triggers when the user inputs 'import', 'import review', or provides an external review file path.
---

# Skill: import-review

## Purpose & Responsibility
Allows a researcher to seamlessly integrate an external literature review shared by a colleague into their local ISLS repository. Validates paper IDs against the 10-year corpus (5,402 papers), unpacks custom property definitions into `workspace/properties/`, unpacks observation evidence quotes into `workspace/observations/`, saves the review manifest into `workspace/reviews/`, rebuilds the local cache, and opens the review in the Viewer.

## Trigger Phrasing
This skill is triggered whenever the user types:
- `import` or `import review`
- `import <filepath>` (e.g., `import /path/to/my_review.isls-review.json`)
- "Import a shared review"
- "Load external review bundle"

## Execution Procedure

When this skill is triggered, perform these steps sequentially:

### Step 1: Identify the Review File
- If the user provided a file path in their prompt (e.g., `import sample.isls-review.json`), use that path.
- If no path was provided, prompt the user for the absolute or relative path to the `.json`, `.isls-review.json`, or `.zip` review file.

### Step 2: Execute Import Pipeline
Run the deterministic review import script:
```bash
python3 scripts/import_review.py "<filepath>"
```
The script will:
1. Validate the review structure.
2. Cross-reference paper IDs against `proceedings.db`.
3. Unpack custom properties into `workspace/properties/`.
4. Unpack observations into `workspace/observations/`.
5. Save the review JSON and Markdown into `workspace/reviews/`.
6. Automatically rebuild the local review cache (`scripts/build_all_reviews_cache.py`).

### Step 3: Ensure Viewer Server is Active
Check if port `8888` is running. If not, launch the server:
```bash
if ! curl -s http://localhost:8888/api/health >/dev/null 2>&1 && ! lsof -i :8888 >/dev/null 2>&1; then
  python3 server.py --port 8888
fi
```

### Step 4: Confirm Import to User
Provide a clean confirmation with the imported review details and a direct viewer link:
- **Review Name**: Name of the imported review
- **Papers**: Number of papers matched
- **Properties & Evidence**: Custom properties and observations unpacked
- **Launch Link**: [http://localhost:8888/?review=<review_id>](http://localhost:8888/?review=<review_id>)

## Guardrails
- **Workspace Isolation**: External reviews and evidence MUST be unpacked into `workspace/`. Never write imported reviews to core system directories.
- **Port Conflict**: Server must run on port `8888`. Never use `8080`.
