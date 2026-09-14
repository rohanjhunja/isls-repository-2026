---
name: manage-python-services
description: Kill, restart, or health-check Python processes, servers, and background services across the entire project repository or scoped to specific literature reviews.
---

# Skill: manage-python-services

## Purpose & Responsibility
Inspect, health-check, terminate, and restart Python background scripts, web servers, and data pipeline functions across the entire repository workspace or scoped to specific literature reviews.

## 1. Project-Wide Python Management

### A. Health Check & Status Inspection
Check active Python processes and web server status across the project:
```bash
# Check if web server is responding on port 8888
curl -s --noproxy '*' http://localhost:8888/api/reviews

# Check port 8888 process binding
lsof -i :8888

# List all active Python processes for the workspace
ps aux | grep -E "python3|server.py|proceedings_ingest" | grep -v grep
```

### B. Kill All Project Python Processes
Safely terminate all Python servers and background workers associated with the workspace:
```bash
# Terminate web server
pkill -f "server.py"

# Terminate active ingest/review CLI tasks
pkill -f "proceedings_ingest"

# Terminate active cache builder tasks
pkill -f "build_all_reviews_cache.py"
```

### C. Restart Whole Project Services
1. Terminate all stale or running Python processes (`pkill -f "server.py"`).
2. Re-initialise the web server on port 8888 (`BypassSandbox: true`):
   ```bash
   .venv/bin/python3 server.py --port 8888
   ```
3. Re-run global cache preparation scripts:
   ```bash
   .venv/bin/python3 scripts/prepare_viewer_data.py
   .venv/bin/python3 scripts/build_all_reviews_cache.py
   ```
4. Confirm server health:
   ```bash
   curl -s --noproxy '*' http://localhost:8888/api/reviews
   ```

---

## 2. Review-Specific Python Management

### A. Scoped Process Inspection & Termination
Inspect and kill background tasks processing a specific review ID (`<review_id>`):
```bash
# Find PIDs associated with the specific review ID
ps aux | grep "<review_id>" | grep -v grep

# Terminate process for specific review ID
pkill -f "<review_id>"
```

### B. Review-Specific Cache Invalidation & Restart Procedure
To restart processing and refresh the web viewer display for a specific review:
1. **Invalidate Cache**: Remove or update stale cache entry for `<review_id>`:
   ```bash
   rm -f data/derived/reviews_cache/<review_id>.json
   ```
2. **Re-run Review Preparation Script**: Initialise Python data builder / sync script:
   ```bash
   python3 scripts/prepare_viewer_data.py
   # Or run review CLI sync:
   python3 -m proceedings_ingest.cli review sync <review_id>
   ```
3. **Verify Web Server Initialization**: Ensure `server.py` is running (`curl -s --noproxy '*' http://localhost:8888/api/reviews/<review_id>`). If inactive, start `python3 server.py --port 8888` with `BypassSandbox: true`.
4. **Timely Localhost Display**: Verify `http://localhost:8888/?review=<review_id>` serves fresh metadata.

---

## Guardrails & Execution Rules

- **Avoid Port 8080**: Port 8080 is reserved by macOS Control Center / AirPlay Receiver (returns 403 / empty response). Always default to port `8888` or next open port (`8889`, `8085`).
- **Sandbox Mode Execution**: ALWAYS launch/restart `python3 server.py` with `BypassSandbox: true` so the process binds directly to the host network interface.
- **Process Verification**: Use `lsof -i :8888` or `ps aux` to locate processes before performing force kills (`kill -9`).
- **Post-Restart Health Check**: Always execute a `curl` endpoint test after restarting services to confirm operational readiness.
