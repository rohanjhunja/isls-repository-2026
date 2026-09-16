---
name: update
description: Pull latest core system updates from Git without overwriting user reviews, custom properties, observations, or workspace files. Triggers when the user inputs 'update', 'update repository', 'pull updates', or asks to update the system.
---

# Skill: update

## Purpose & Responsibility
Safely pull and apply the latest core updates from GitHub (`origin main`) while guaranteeing that the user's private workspace (`workspace/`)—including all saved reviews, custom properties, observations, notes, and exports—remains 100% intact and untouched. Automatically checks for dependency changes, rebuilds caches, and restarts the local review server on port `8888`.

## Trigger Phrasing
This skill is triggered whenever the user types:
- `update` or `update repository`
- `pull updates` or `pull from git`
- "Update my ISLS repository"
- "Get the latest version from github"

## Execution Procedure

When this skill is triggered, perform these steps sequentially:

### Step 1: Pre-Update Guardrail Check
Check if any files in the repository have been modified outside `workspace/`:
```bash
git status --porcelain
```
- **If core files outside `workspace/` are modified**:
  ⚠️ **WARN THE USER**:
  > *"Warning: You have uncommitted changes in core system files outside `workspace/`. Updating will overwrite these changes or cause merge conflicts. Please confirm if you wish to proceed or stash your changes first."*
  Obtain user confirmation before pulling.
- Files inside `workspace/` are git-ignored and completely safe.

### Step 2: Pull Core Updates from Git
Execute a clean pull from the main branch:
```bash
git pull origin main
```

### Step 3: Check & Update Dependencies
Ensure virtual environment has the latest dependencies:
```bash
source .venv/bin/activate
pip install -e .
```

### Step 4: Refresh Database & Review Cache
Check if structured papers or ingestion scripts changed, then refresh the review caches:
```bash
# Refresh review caches for both system samples and user workspace reviews
python3 scripts/build_all_reviews_cache.py
```

### Step 5: Restart Review Viewer Server
Restart the local server on port `8888`:
```bash
# Terminate existing server
pkill -f "server.py" 2>/dev/null || true

# Start viewer server on port 8888 in background
python3 server.py --port 8888
```

### Step 6: Verify & Report to User
Verify that `http://localhost:8888` is responding, then present a clean summary:
- **Status**: Core system successfully updated to latest `origin main`.
- **User Workspace Preserved**: All local reviews in `workspace/reviews/` and observations in `workspace/observations/` are intact.
- **Review Viewer**: [http://localhost:8888](http://localhost:8888)

## Guardrails
- **Port Conflict**: NEVER bind to port `8080`. Always use port `8888`.
- **Workspace Protection**: NEVER delete, overwrite, or reset anything inside `workspace/`.
