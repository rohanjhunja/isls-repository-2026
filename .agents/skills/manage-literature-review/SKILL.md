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
2. **Review Routing Architecture & Explicit Triggers**:
   - **Pathway 1: Deterministic Dipstick Review**:
     - *Triggers*: `'dipstick'`, `'dipstick review'`, `'quick search'`, `'sweep'`, `'bm25'`, `'fts5 search'`, `'title/abstract'`, `'title search'`, `'fast scan'`, `'reconnaissance'`, `'keyword search'`.
     - Rapid title & abstract sweep via local SQLite FTS5 lexical BM25 search (0 LLM tokens, $< 3\text{ ms}$).
   - **Pathway 2: Deterministic Section Extraction**:
     - *Triggers*: `'extract property'`, `'property extraction'`, `'regex extract'`, `'sample size'`, `'sample sizes'`, `'factual metadata'`, `'grade levels'`, `'named tools'`, `'extract numbers'`, `'count occurrences'`, `'demographics'`.
     - Targeted candidate sections (`methods`, `results`) via regex patterns or controlled vocabularies for discrete factual attributes.
   - **Pathway 3: Full In-Context Agentic Review**:
     - *Triggers*: `'agentic review'`, `'agentic reviews'`, `'ai-search'`, `'dual agent'`, `'consider the full text'`, `'read full text'`, `'read sections'`, `'qualitative coding'`, `'interpretive review'`, `'thematic analysis'`, `'attribution test'`, `'code-design framework'`, `'agency analysis'`.
     - Ingest unabridged paper prose directly into prompt context (~4k–10k tokens/paper). Scoped to full paper or explicitly specified sections (`--sections`).
     - Strict prohibition on Python regex mocking of qualitative codes; LLM cognitive deduction in context. Dual agent reviews (`'dual agent'`) MUST ALWAYS be executed as full in-context agentic reviews with Coder and Auditor agents, never via scripted regex simulation.
   - **Pathway 4: Staged Hybrid Review**:
     - *Triggers*: `'hybrid review'`, `'screen and synthesize'`, `'filter and read'`, `'dipstick then review'`, `'two-stage review'`, `'sweep then code'`, `'screen then analyze'`, `'filter then code'`.
     - Two-stage pipeline: Stage 1 deterministic screening sweep to resolve $N$ candidates $\rightarrow$ Stage 2 in-context qualitative coding of the qualified candidates.
   - **Step 0: Contextual Methodological Triage (When Triggers Are Absent)**:
     - Factual/statistical/counts $\rightarrow$ Pathway 1 or 2.
     - Interpretive/qualitative/theoretical $\rightarrow$ Pathway 3.
     - Scaled corpus synthesis $\rightarrow$ Pathway 4.

3. **Downstream Deterministic Data Governance**:
   - The sigil system enforces data quality across storage (`workspace/reviews/*.json` typed `column_definitions` and verified evidence objects) and output (unambiguous column header badges and zero-hallucination parity checks against SQLite context).
   - Ingestion: Only canonical Mode A projections from SQLite `proceedings.db`.
   - Verification: All textual quotes asserted via `assert instr(full_text, quote) > 0`.
   - Persistence: All reviews must pass schema validation and trigger `python3 scripts/build_all_reviews_cache.py`.

4. **Mandatory Method Reporting on Completion**:
   - Every completed review, summary table, or chat response MUST emit an **Execution Method Badge**:
     - `Execution Method: ◈ Full In-Context Agentic Review` | `◈ Deterministic Dipstick` | `◈ Deterministic Section Extraction` | `◈ Staged Hybrid Review`
     - `Text Coverage`: Full Paper Prose (All Sections) | Specified Sections Only (`<sections>`) | Title/Abstract Only | Candidate Sections Only
     - `Epistemic Standard`: `⌕ 100% Exact DB Substring Match Verified` | `◇ Lexical BM25 Ranking`
     - `Attribution Status`: Disaggregated Teacher Agency Verified (4-Part Attribution Test Applied) | N/A (Factual/Search)
5. **Markdown Views & Metadata Files**:
   - Reviews are saved as `.json` metadata files in `workspace/reviews/<review_id>.json` (git-protected).
   - Every saved/updated review automatically syncs a human-readable Markdown view in `workspace/reviews/<review_id>.md`.
6. **Interactive Web Viewer & Python Service Initialization**:
   - All saved literature reviews in `workspace/reviews/` and curated templates in `data/sample_reviews/` can be interactively inspected using the `launch-review-viewer` skill (`http://localhost:8888/viewer?review=<review_id>`).
   - **Auto-Initialization Procedure**: Upon creating or starting a new literature review:
     1. **Check Web Server**: Verify if the Python web server is running on port 8888 (`curl -s --noproxy '*' http://localhost:8888/api/reviews`). If inactive or stale, clear old processes (`pkill -f "server.py"`) and launch `python3 server.py --port 8888` (skipping port 8080).
     2. **Initialise Python Data & Cache Scripts**: Verify and execute `python3 scripts/build_all_reviews_cache.py` so the new review is indexed in the cache.
     3. **Ensure Timely Localhost Rendering**: Guarantee `http://localhost:8888/viewer?review=<review_id>` immediately serves and displays the newly created review in time.

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
   - Conducted via Pathway 3 with full paper prose (or explicitly specified sections) in context, qualitative coding schemas, and dual-agent verification.
   - Example: `Agentic Review - embodied cognition, multimodal interaction`.
4. **`Hybrid Review - <keyword(s)>`**:
   - Conducted via Pathway 4 combining wide-corpus deterministic screening sweeps with downstream in-context qualitative coding.
   - Example: `Hybrid Review - teacher co-design, learning analytics`.

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
# Open direct review link: http://localhost:8888/viewer?review=<review_id>
```

