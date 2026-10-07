# ISLS Research Repository & Agentic Review System (2016–2026)

## System Overview
A researcher-first review system bridging 10 years of learning sciences scholarship (5,402 peer-reviewed papers across ISLS, CSCL, and ICLS from 2016 to 2026). The repository combines a local SQLite FTS5 lexical BM25 search database, deterministic Python ingestion/extraction pipelines, and an interactive Literature Review Web Viewer.

## Fast Setup & Common Commands

- **Initial Setup**: Type or paste **`setup`** into the agent chat in Google Antigravity or Claude Desktop. The `setup` skill handles full automated initialization.
- **Pull Core Updates**: Type **`update`** to pull the latest core code, UI, and corpus updates from GitHub (`origin main`) while guaranteeing all your saved reviews and observations in `workspace/` remain intact.
- **Import Shared Review**: Type **`import <path/to/review>`** to integrate an external review bundle (`.isls-review.json` or `.zip`) into your local workspace.

Alternatively, execute the manual setup commands:

```bash
# 1. Environment Setup (Python 3.11+)
python3 -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -e .

# 2. Database & Cache Population (~15 seconds)
# Rebuilds proceedings.db (5,402 papers, authors, 36,871 full-text sections, FTS5 index)
python3 scripts/populate_10yr_database.py

# Precomputes sample & workspace review viewer caches
python3 scripts/build_all_reviews_cache.py

# 3. Launch Literature Review Viewer Server
python3 server.py --port 8888
# Viewer opens at: http://localhost:8888/viewer (Cover at: http://localhost:8888)
```

## Agent Workflows & Skills Index

All 16 agent skills are defined in `.agents/skills/` and can be invoked directly by Antigravity or executed via terminal commands with Claude Desktop / Claude Code:

| Skill Name | Location | Primary Command / Procedure |
| :--- | :--- | :--- |
| `plan-data-requirements` | `.agents/skills/plan-data-requirements/SKILL.md` | Pre-flight data requirements audit & query projection planning |
| `setup` | `.agents/skills/setup/SKILL.md` | 1-click full system initialization: type `setup` |
| `update` | `.agents/skills/update/SKILL.md` | Safely pull core updates from git: type `update` |
| `import-review` | `.agents/skills/import-review/SKILL.md` | Import external review bundle: type `import <file>` |
| `dipstick-review` | `.agents/skills/dipstick-review/SKILL.md` | Launch viewer with pre-populated keywords: `http://localhost:8888/viewer?keywords=...` |
| `launch-review-viewer` | `.agents/skills/launch-review-viewer/SKILL.md` | Ensure server is running on port 8888: `python3 server.py --port 8888` (Viewer: `http://localhost:8888/viewer`) |
| `manage-literature-review` | `.agents/skills/manage-literature-review/SKILL.md` | Create, update, or extend reviews in `workspace/reviews/*.json` |
| `search-literature` | `.agents/skills/search-literature/SKILL.md` | Run lexical BM25 / FTS5 search via `proceedings_ingest.lexical_search` |
| `extract-research-property` | `.agents/skills/extract-research-property/SKILL.md` | Extract candidate section observations with verbatim evidence quotes |
| `define-research-property` | `.agents/skills/define-research-property/SKILL.md` | Author typed property definitions in `workspace/properties/*.yaml` |
| `query-repository-data` | `.agents/skills/query-repository-data/SKILL.md` | Query SQLite `proceedings.db` directly for statistics, papers, and authors |
| `audit-research-data` | `.agents/skills/audit-research-data/SKILL.md` | Audit paper boundaries, evidence integrity, and metadata schema compliance |
| `ingest-proceedings` | `.agents/skills/ingest-proceedings/SKILL.md` | Ingest new conference PDFs via `proceedings ingest <file.pdf>` |
| `manage-python-services` | `.agents/skills/manage-python-services/SKILL.md` | Kill stale processes (`pkill -f server.py`) and check port health |
| `publish-research-views` | `.agents/skills/publish-research-views/SKILL.md` | Export validated observations to CSV, Excel, and JSON dashboards |
| `profile-proceedings` | `.agents/skills/profile-proceedings/SKILL.md` | Profile and tune proceedings layout extraction rules in `profiles/*.yaml` |
| `ingest-baseline-review` | `.agents/skills/ingest-baseline-review/SKILL.md` | Ingest external human coding & seal immutable baseline review |
| `execute-agentic-review` | `.agents/skills/execute-agentic-review/SKILL.md` | Execute in-context qualitative review with parallel workers & fresh context |
| `compare-literature-reviews` | `.agents/skills/compare-literature-reviews/SKILL.md` | Compare any two reviews, compute Cohen's Kappa, and synthesize findings |

## Core Rules & Guardrails
- **Workspace Boundary & Root Change Warning**: All user reviews, extracted evidence, custom properties, and exports MUST be created inside `workspace/`. Antigravity and Claude agents MUST ALWAYS warn the user before editing any core system files outside `workspace/` (e.g. `src/`, `web/`, `scripts/`, `data/sample_reviews/`) that such edits will cause merge conflicts or be overwritten upon running `update` (`git pull`), and MUST require explicit user confirmation before proceeding.
- **Zero-Hallucination Metadata & Full-Text Invariant (Strict Presentation-Query Parity)**: Any database attribute rendered in user-facing tables, cards, lists, or citations (Author, Year, Venue, DOI, Handle, Page numbers, Section text) MUST exist in the tool execution result within context. Agents are strictly forbidden from generating ungrounded metadata from parametric memory. If an output field is missing, the agent MUST run a secondary point lookup or omit the field. Pre-flight query planning via `plan-data-requirements` is mandatory before tabular or analytical synthesis.
- **Dual-Mode Query Scoping**:
  - *Mode A (User-Facing Tables & Selections)*: Mandatory Tier 1 Canonical Projection (`p.id, p.title, p.citation, p.year, p.conference, p.paper_type, p.doi, p.handle_url, p.start_page, p.end_page`) ensuring complete author and bibliographic grounding (~40 tokens/paper).
  - *Mode B (Bulk Aggregation, Counts & Screening)*: Mandatory lightweight projections (`SELECT id, year, conference FROM papers`) to eliminate context window waste.
  - *Mode C (Full-Text Extraction)*: Secondary bounded text slices (`substr(text, 1, N)`) or FTS5 BM25 `snippet()` targeted by `normalized_section`.
- **The Source Sigil System (Highest Structural Level & Epistemic Warnings)**:
  - `◈` **Database Ground Truth**: Direct, unmodified record from `proceedings.db`.
  - `◇` **Database-Derived Metric**: Deterministic quantitative calculation/aggregation over DB records.
  - `⌕` **Verbatim Evidence Quote**: Exact text extracted directly from paper sections or abstracts.
  - `✦` **Agentic Synthesis / Inferred**: Review alert for AI-inferred qualitative codes, frameworks, or summaries.
  - *Structural Rule*: Place sigils at the highest structural level (column headers for homogeneous table columns; trailing end-of-paragraph/sentence for prose). Never place sigils mid-sentence or within dedicated brackets (use `✦⌕`, not `[✦⌕]`).
  - *Key Label*: Always label the explanatory key as `Source: ◈ Database Record | ◇ Database-Derived Metric | ⌕ Verbatim Section Evidence | ✦ Agent-Synthesized Coding`.
  - *Storage & Output Governance*: The sigil system enforces data quality across storage (`workspace/reviews/*.json` typed `column_definitions` and verified evidence objects) and output (unambiguous column header badges and zero-hallucination parity checks against SQLite context).
- **Port 8080 Conflict**: NEVER bind to port `8080` (reserved by macOS Control Center / AirPlay Receiver). Always use port `8888` (or `8889` / `8085`).
- **Contextual Reconnaissance (Dipstick Principle)**: Fast title/abstract dipstick review is the recommended first step for open, exploratory broad-corpus scans, but must not artificially block immediate in-context qualitative evaluation when the inquiry is targeted or interpretive.
- **Traceable Verbatim Evidence**: Never invent or hallucinate values. Every extracted observation requires exact verbatim source text from candidate sections verified via downstream substring assertion (`assert instr(full_text, quote) > 0`).
- **Immutable Source Seed**: `data/derived/ground_truth_registry.json` is the 10-year golden dataset. `proceedings.db` can be recomputed at any time in ~15s without loss.
- **Saved Review Naming Rule**: All saved reviews in `workspace/reviews/` MUST strictly follow the protocol naming format: `'<Review Protocol> - <keyword(s)>'`.
  - `Dipstick Review - <keyword(s)>`: Fast title & abstract screening sweep across 100% of corpus papers (0 tokens, $< 3\text{ ms}$).
  - `Expanded Scope - <keyword(s)>`: Scope expanded beyond Title & Abstract into candidate sections (`Methodology`, `Findings`, `Discussion`, `Full Text`) or section-targeted FTS5 BM25 search.
  - `Agentic Review - <keyword(s)>`: When an AI agent conducts a review and modifies the default protocol (custom inclusion/exclusion criteria, qualitative section extractions, theoretical coding schemas, or comparative matrix synthesis).
  - `Hybrid Review - <keyword(s)>`: Two-stage reviews combining wide-corpus deterministic screening sweeps with downstream in-context qualitative coding.
  - Multiple keywords must be cleanly comma-separated (e.g. `Dipstick Review - generative AI, collaborative learning`).

## The Multi-Modal Review Architecture & Contextual Planning

The repository provides four review pathways. **The agent first determines the pathway via explicit trigger words; if no triggers are present, the agent conducts Step 0: Contextual Methodological Triage to select the best action from context while enforcing the downstream deterministic data check:**

### Explicit Pathway Trigger Words

When any of the following trigger phrases appear in user instructions, the agent immediately activates the designated pathway:

| Pathway | Primary Role | Explicit Trigger Words & Phrases |
| :--- | :--- | :--- |
| **Pathway 1: Deterministic Dipstick Review** | Fast title & abstract screening across 100% of corpus (5,402 papers, 0 tokens, $< 3\text{ ms}$). | `'dipstick'`, `'dipstick review'`, `'quick search'`, `'sweep'`, `'bm25'`, `'fts5 search'`, `'title/abstract'`, `'title search'`, `'fast scan'`, `'reconnaissance'`, `'keyword search'` |
| **Pathway 2: Deterministic Section Extraction** | Bounded, syntactic extraction of factual/numerical metadata variables using regex. | `'extract property'`, `'property extraction'`, `'regex extract'`, `'sample size'`, `'sample sizes'`, `'factual metadata'`, `'grade levels'`, `'named tools'`, `'extract numbers'`, `'count occurrences'`, `'demographics'` |
| **Pathway 3: Full In-Context Agentic Review** | Deep qualitative, interpretive, or theoretical coding of unabridged text in prompt context. | `'agentic review'`, `'agentic reviews'`, `'ai-search'`, `'dual agent'`, `'consider the full text'`, `'read full text'`, `'read sections'`, `'qualitative coding'`, `'interpretive review'`, `'thematic analysis'`, `'attribution test'`, `'code-design framework'`, `'agency analysis'` |
| **Pathway 4: Staged Hybrid Review** | Wide-corpus deterministic screening followed by in-context qualitative coding of qualified candidates. | `'hybrid review'`, `'screen and synthesize'`, `'filter and read'`, `'dipstick then review'`, `'two-stage review'`, `'sweep then code'`, `'screen then analyze'`, `'filter then code'` |

### Step 0: Contextual Methodological Triage (Pre-Flight Planning Step)
If **none** of the explicit trigger words are present, the agent evaluates the **epistemic nature of the inquiry**:
1. *Factual / Statistical / Bibliographic* (Counts, distributions, author networks, named tools, years) $\rightarrow$ Select **Pathway 1 or 2**.
2. *Interpretive / Qualitative / Conceptual* (Teacher agency, theoretical stances, inclusion rationales, pedagogical discourse) $\rightarrow$ Select **Pathway 3**.
3. *Scaled Corpus Research Question* (Broad inquiry requiring filtering before qualitative synthesis) $\rightarrow$ Select **Pathway 4 (Staged Hybrid)**.

### Downstream Deterministic Data Governance Pipeline (The 4 Invariant Gates)
Reasoning freedom is unlocked upstream, but **data entering or exiting context must pass through four strict deterministic gates**:
1. **Gate 1 (Deterministic Ingestion Invariant)**: All papers and sections queried from `proceedings.db` MUST use canonical Mode A Tier 1 projections (`p.id, p.title, p.citation, p.year, p.conference, p.paper_type, p.doi, p.handle_url, p.start_page, p.end_page`) or unabridged normalized sections (`SELECT normalized_section, original_heading, text FROM sections WHERE paper_id = :id ORDER BY order_index`). Zero ungrounded records from parametric memory.
2. **Gate 2 (Deterministic Evidence Substring Assertion)**: Every qualitative code, observation, or quote MUST be verified by exact Python substring match: `assert instr(paper_full_text, quote) > 0`.
3. **Gate 3 (Deterministic Metric Computation)**: All percentages, frequencies, distributions, and inter-rater reliability scores (Cohen's Kappa $\kappa$) MUST be computed deterministically via Python code (`◇`), never estimated.
4. **Gate 4 (Deterministic Persistence & Egress Invariant)**: All saved reviews in `workspace/reviews/*.json` must conform to schema, designate sigils in `column_definitions`, and automatically execute `python3 scripts/build_all_reviews_cache.py`.

### The Agentic Review In-Context Invariant (Strict Cognitive Reading)
Whenever Pathway 3 or Pathway 4 (Stage 2) is activated:
1. **Mandatory In-Context Prose Ingestion**: Load unabridged text (full paper or explicitly specified sections) directly into prompt context.
2. **Strict Prohibition on Python Regex Mocking**: Python scripts must NEVER contain regular expressions or lemma filters to assign qualitative codes. Python is restricted to SQL retrieval, deterministic substring verification (`assert instr(full_text, quote) > 0`), and persisting JSON/Markdown output.
3. **Cognitive Qualitative Deduction**: The LLM itself reads the complete prose in context, applies the theoretical framework, executes the 4-Part Attribution Test, and produces qualitative findings.
4. **Batch Orchestration via Subagents or Turns**: For multi-paper reviews, process papers sequentially in clean context turns or spawn isolated subagent workers (`invoke_subagent`).

### Mandatory Method Reporting Standard
On completion of ANY review task, query, synthesis, table, or export, the agent MUST emit a standardized **Execution Method Badge** at the top of the summary and within the metadata:
- **Execution Method**: `◈ Full In-Context Agentic Review` | `◈ Deterministic Dipstick` | `◈ Deterministic Section Extraction` | `◈ Staged Hybrid Review`
- **Text Coverage**: Full Paper Prose (All Sections Ingested) | Specified Sections Only (`<sections>`) | Title/Abstract Only | Candidate Sections Only
- **Epistemic Standard**: `⌕ 100% Exact DB Substring Match Verified` | `◇ Lexical BM25 Ranking`
- **Attribution Status**: Disaggregated Teacher Agency Verified (4-Part Attribution Test Applied) | N/A (Factual/Search)



