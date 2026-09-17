---
name: manage-literature-review
description: Create, continue, update, duplicate, archive, and extend saved literature reviews in the repository, automatically initialising required Python servers and cache scripts so localhost displays new reviews in time.
---

# Skill: manage-literature-review

## Purpose & Responsibility
Create, continue, update, duplicate, archive, and extend saved literature reviews in the repository.

## Capabilities & Scoping Rules

1. **Paper Filtering & Scope**:
   - Filter paper scope explicitly by `--years`, `--conferences`, `--journals`, or explicit paper IDs.
2. **Deterministic vs AI Search**:
   - Translate search criteria into explicit keywords.
   - Search across title and abstract by default (`--search-fields title,abstract`).
   - Conduct a full paper search (`--search-fields sections`) only when explicitly requested.
   - Use deterministic keyword search by default; enable AI semantic search only when `--ai-search` is specified.
3. **Markdown Views & Metadata Files**:
   - Reviews are saved as `.json` metadata files in `workspace/reviews/<review_id>.json` (git-protected).
   - Every saved/updated review automatically syncs a human-readable Markdown view in `workspace/reviews/<review_id>.md`.
4. **Interactive Web Viewer & Python Service Initialization**:
   - All saved literature reviews in `workspace/reviews/` and curated templates in `data/sample_reviews/` can be interactively inspected using the `launch-review-viewer` skill (`http://localhost:8888/?review=<review_id>`).
   - **Auto-Initialization Procedure**: Upon creating or starting a new literature review:
     1. **Check Web Server**: Verify if the Python web server is running on port 8888 (`curl -s --noproxy '*' http://localhost:8888/api/reviews`). If inactive or stale, clear old processes (`pkill -f "server.py"`) and launch `PYTHONUNBUFFERED=1 .venv/bin/python server.py --port 8888` with `BypassSandbox: true` (skipping port 8080).
     2. **Initialise Python Data & Cache Scripts**: Verify and execute `python3 scripts/build_all_reviews_cache.py` so the new review is indexed in the cache.
     3. **Ensure Timely Localhost Rendering**: Guarantee `http://localhost:8888/?review=<review_id>` immediately serves and displays the newly created review in time.

## Saved Review Naming Convention
All literature reviews created, saved, or suggested MUST follow the standardized naming format:
**`'<Review Protocol> - <keyword(s)>'`**

### Protocol Taxonomy:
1. **`Dipstick Review - <keyword(s)>`**:
   - Rapid title & abstract sweep across 100% of repository papers (default 0 tokens, $< 3\text{ ms}$).
   - Example: `Dipstick Review - generative AI` or `Dipstick Review - collaborative learning, analytics`.
2. **`Expanded Scope - <keyword(s)>`**:
   - Scope expanded beyond Title & Abstract into candidate sections (`Methodology`, `Findings`, `Discussion`, `Full Text`) or section-targeted FTS5 BM25 search.
   - Example: `Expanded Scope - feedback, scaffolding`.
3. **`Agentic Review - <keyword(s)>`**:
   - Conducted by an AI agent (Antigravity or Claude) with a modified review protocol (e.g. custom inclusion/exclusion criteria, qualitative section extractions, theoretical coding schemas, or comparative matrix synthesis).
   - *Note*: If an agent executes an unmodified standard protocol, the default label (`Dipstick Review` or `Expanded Scope`) may be used.
   - Example: `Agentic Review - embodied cognition, multimodal interaction`.

### Keyword Formatting Rules:
- Multiple keywords must be cleanly comma-separated (e.g. `Dipstick Review - AI, collaboration`).
- Boolean operator queries (`AND`, `OR`, `NOT`) should resolve to clean positive terms.

## CLI Usage

```bash
# Create review following protocol naming convention
proceedings review dipstick --keywords "collaboration,AI"
# Automatically names review: "Dipstick Review - collaboration, AI"

proceedings review create "Expanded Scope - neural network" --keywords "neural network" --search-fields "sections"

# Sync/prepare viewer data for new review
python3 scripts/prepare_viewer_data.py

# List and view reviews
proceedings review list
proceedings review show <review_id>

# Check server status / Launch interactive web viewer on port 8888 (with BypassSandbox: true)
curl -s --noproxy '*' http://localhost:8888/api/reviews || python3 server.py --port 8888
# Open direct review link: http://localhost:8888/?review=<review_id>
```

