---
name: setup
description: Initialize, configure, and launch the complete ISLS literature review system on a new computer or fresh workspace. Triggers when the user inputs 'setup', 'set up', 'initialize', or requests repository setup.
---

# Skill: setup

## Purpose & Responsibility
Execute the complete, automated 1-click onboarding and initialization of the ISLS Research Repository & Review System on a new machine or fresh workspace. Automatically configures the Python virtual environment, installs project dependencies, rebuilds the 10-year full-text SQLite database (`proceedings.db`) with BM25 FTS5 search across all 5,402 papers and 36,871 sections from structured Markdown files, precomputes review caches for curated sample reviews, and launches the Literature Review Web Viewer on port `8888`.

## Trigger Phrasing
This skill is triggered whenever the user types:
- `setup` or `set up`
- `initialize` or `initialize system`
- "Set up the system on my computer"
- "Clone and initialize the repository"

## Execution Procedure

When this skill is triggered, perform these steps sequentially:

### Step 1: Workspace Structure & Virtual Environment
Ensure user workspace directories exist and virtual environment is active:
```bash
# 1. Initialize user workspace (protected from git overwrites)
mkdir -p workspace/reviews workspace/observations workspace/properties workspace/exports

# 2. Virtual environment & dependencies
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

### Step 2: Populate 10-Year Full-Text SQLite Database & FTS5 Index
Check if `proceedings.db` exists with full paper count (5,402 papers). If missing or empty, build it from bundled structured Markdown papers (`data/derived/papers/`):
```bash
python3 scripts/populate_10yr_database.py
```
*Expected duration: ~15 seconds. Populates 5,402 papers, 8,946 authors, and 36,871 full-text sections with FTS5 BM25 search.*

### Step 3: Precompute Review Viewer Caches
Generate precomputed caches for curated sample literature reviews (`data/sample_reviews/`) and any local reviews in `workspace/reviews/`:
```bash
python3 scripts/build_all_reviews_cache.py
```

### Step 4: Health Check & Launch Review Viewer Server
Ensure port `8888` is clear of stale processes, then launch the server in the background:
```bash
# Terminate any existing server instances
pkill -f "server.py" 2>/dev/null || true

# Start viewer server on port 8888
python3 server.py --port 8888
```

### Step 5: Confirm Readiness to the User
Verify that `http://localhost:8888` is responding (HTTP 200), then present a clean summary:
- **System Ready**: ISLS Research Repository & Agentic Review System (2016–2026)
- **Corpus**: 5,402 peer-reviewed conference papers, 8,946 authors, 36,871 full-text sections
- **Search**: Offline SQLite FTS5 lexical BM25 indexing active
- **User Workspace**: `workspace/` initialized and git-protected
- **Review Viewer**: [http://localhost:8888](http://localhost:8888)
- **Observatory**: [http://localhost:8888/overview.html](http://localhost:8888/overview.html)

## Guardrails
- **Port Conflict**: NEVER bind to port `8080` (reserved by macOS Control Center). Always use port `8888` (or `8889` / `8085`).
- **No PDF Downloads Needed**: The repository already includes 100% of the structured full-text Markdown files (`data/derived/papers/`). Do not attempt to download raw PDF files.
- **User Space Isolation**: All user-generated reviews, observations, and custom properties must be saved strictly in `workspace/`. Never modify core files outside `workspace/` without user confirmation.
