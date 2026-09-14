---
name: dipstick-review
description: Launch the interactive Literature Review Web Viewer with targeted keywords pre-populated for instant title searching across 100% of repository papers.
---

# Skill: dipstick-review

## Purpose & Responsibility
Launch the interactive Literature Review Web Viewer pre-populated with relevant query keywords. This skill serves as the lightweight first step for all literature reviews.

## Procedure
1. **Server & Python Script Check & Fast Auto-Initiation**:
   - Check if the Python web server is running on the default port 8888 (e.g. `curl -s --noproxy '*' http://localhost:8888/api/reviews`).
   - If not active or stale processes exist, run `pkill -f "server.py"` and initiate `PYTHONUNBUFFERED=1 .venv/bin/python server.py --port 8888` with `BypassSandbox: true` to ensure immediate binding to port 8888.
   - Initialise required python data preparation/cache scripts (`.venv/bin/python scripts/prepare_viewer_data.py`) if cached dipstick review data is missing.
2. **Format Query or Review Link**:
   - For keyword search: Format target keywords into a comma-separated query string (e.g. `Generative AI, Learning Analytics`) and construct:
     `http://localhost:<port>/?keywords=<URL_ENCODED_KEYWORDS>`
   - For a specific saved review: Construct the review identifier URL:
     `http://localhost:<port>/?review=<review_id>`
3. Present the link clearly to the user.
4. **STOP**: Do NOT execute any background CLI tasks, reviews, extractions, or additional processing unless explicitly requested by the user.

## Core Rules & Guardrails
- **NEVER Use Port 8080**: Port 8080 is reserved by macOS Control Center / AirPlay Receiver, which returns 403 / blank responses. Default to port `8888` or next open non-system port (`8889`, `8085`).
- **Sandbox Mode Execution**: ALWAYS start `python3 server.py` with `BypassSandbox: true` so the process binds directly to the host network interface.
- **Server Health Check**: Always verify the server is running on an active port before sharing URLs; initiate `python3 server.py --port 8888` if needed.
- **Review Identifier URLs**: Always use `http://localhost:<port>/?review=<review_id>` when referencing saved reviews so the viewer opens directly to the correct review.
- **Launch Only**: Present the web viewer launcher link and wait for user direction.
- **Instant Client-Side Search**: Opening the keyword link pre-populates the viewer search bar and filters 2,791 repository titles instantly in **$< 3\text{ ms}$**.
- **User-Driven Actions**: Saving a review or expanding section scope (`Abstract`, `Methodology`, `Findings`) is controlled directly by the user via the web interface.
