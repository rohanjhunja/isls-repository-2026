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

## CLI Usage

```bash
# Create review with scoped criteria (years, conferences, keywords, title/abstract scope)
proceedings review create "STEM AI Review" --years 2023,2024 --conferences ISLS --keywords "collaboration,AI" --search-fields "title,abstract"

# Create full-paper search review
proceedings review create "Deep STEM Review" --keywords "neural network" --search-fields "sections"

# Sync/prepare viewer data for new review
python3 scripts/prepare_viewer_data.py

# List and view reviews
proceedings review list
proceedings review show <review_id>

# Check server status / Launch interactive web viewer on port 8888 (with BypassSandbox: true)
curl -s --noproxy '*' http://localhost:8888/api/reviews || python3 server.py --port 8888
# Open direct review link: http://localhost:8888/?review=<review_id>
```

