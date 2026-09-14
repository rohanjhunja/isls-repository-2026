---
name: launch-review-viewer
description: Launch or manage the locally hosted, interactive Literature Review Web Viewer. Browse literature reviews, resizable tables, auto-wrapping unequal row height views, compact scannable views, left-side review navigation, and resizable full-text paper overlays.
---

# Skill: launch-review-viewer

## Purpose & Responsibility
Launch, manage, and inspect locally hosted literature review tables via an interactive web interface. Enables browsing saved literature reviews in `data/reviews/`, column-width adjustable tables, unequal auto-wrapping row heights (default) vs compact equal row height views, live text selection in table cells, and resizable full-text paper overlays.

## Web Server Architecture & URL Routing
- **Local Server Entrypoint**: `PYTHONUNBUFFERED=1 .venv/bin/python server.py --port 8888` (default port `8888`; automatically skips port `8080` due to macOS Control Center conflicts). Always terminate stale instances (`pkill -f "server.py"`) before starting to guarantee instant binding on port 8888 without port scanning delays.
- **Execution Mode**: ALWAYS run with `BypassSandbox: true` so the server socket is exposed to the local browser on the host machine.
- **URL Formats**:
  - **Specific Literature Review**: `http://localhost:<port>/?review=<review_id>` (e.g. `http://localhost:8888/?review=systematic_review_lit_review`)
  - **Dipstick Keyword Search**: `http://localhost:<port>/?keywords=<URL_ENCODED_KEYWORDS>`
  - **General Web Viewer**: `http://localhost:<port>/`
- **REST Endpoints**:
  - `GET /api/dipstick/search?q=<query>&sort_by=<relevance|year>&sort_order=<desc|asc>`: Fielded FTS5 BM25 search with local cross-encoder reranking.
  - `GET /api/dipstick/expand?keywords=<kw>&section=<sec>`: Section-targeted search expansion stream across candidate papers.
  - `GET /api/reviews`: Returns list of all saved literature reviews in `data/reviews/`.
  - `GET /api/reviews/<review_id>`: Returns metadata and papers populated directly from `proceedings.db`.
  - `DELETE /api/reviews/<review_id>`: Atomic removal of saved review, DB index records, and cache files.
  - `GET /api/paper/<paper_id>`: Returns detailed paper metadata, DOIs, handles, section list, and full text.

## Server Health Check & Fast Auto-Initiation
Before sharing or opening any viewer link:
1. **Check if Server is Running**: Verify if the python server is responding (e.g. `curl -s --noproxy '*' http://localhost:8888/api/reviews`).
2. **Clean Stale Processes & Initiate Server**: If no response or multiple zombie instances exist, clear old instances (`pkill -f "server.py"`) and start the server (`PYTHONUNBUFFERED=1 .venv/bin/python server.py --port 8888` with `BypassSandbox: true`).
3. **Initialise Python Data & Cache Scripts**: Check if data prep/cache for the target review is present in `data/derived/reviews_cache/` or `data/reviews/`. If missing or stale, run `.venv/bin/python scripts/prepare_viewer_data.py` or `.venv/bin/python scripts/build_all_reviews_cache.py` to ensure localhost renders the target review immediately.
4. **Use Direct Review URLs**: Always reference the specific review identifier in shared URLs (`http://localhost:<port>/?review=<review_id>`) so the viewer opens directly to the correct review in time.

## Usage & Execution

```bash
# Clean stale server processes and verify port availability
pkill -f "server.py"
curl -s --noproxy '*' http://localhost:8888/api/reviews

# Start the web viewer server instantly (BypassSandbox: true, default port 8888)
PYTHONUNBUFFERED=1 .venv/bin/python server.py --port 8888

# Verify server endpoints
curl --noproxy '*' http://localhost:8888/api/reviews/systematic_review_lit_review
```

## Key Interactive Features

1. **Left-Side Navigation Menu**:
   - Lists all saved literature reviews in `data/reviews/`.
   - Allows switching between different reviews dynamically.
   - Collapsible via the header toggle button (`☰`).

2. **Auto Wrap vs Compact Row Height Toggle**:
   - **Auto Wrap (Unequal Height - Default)**: Full text wrapping, no line clamping or truncation, unequal row heights expand naturally to content.
   - **Compact (Equal Height)**: Uniform row height with `-webkit-line-clamp: 3` line clamping for fast, scannable reading.

3. **Cell Text Selection & Resizable Columns**:
   - Drag header borders (`.resizer`) to adjust column widths.
   - Text selection (`user-select: text`) enabled across all table cells without accidentally opening the side panel.

4. **Resizable Side Panel Overlay**:
   - Click any row to slide open full paper details, abstract, synthesis summary, keywords, and section text.
   - Drag the left edge of the overlay or use quick preset buttons (`40%`, `60%`, `80%`, `100%`) to adjust reading panel width.
