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
- **Port 8080 Conflict**: NEVER bind to port `8080` (reserved by macOS Control Center / AirPlay Receiver). Always use port `8888` (or `8889` / `8085`).
- **Dipstick Pre-Check Mandatory**: Dipstick review is the foundational first step. Check or verify that an initial dipstick review has been conducted before performing heavy section parsing or property extractions.
- **Traceable Verbatim Evidence**: Never invent or hallucinate values. Every extracted observation requires exact verbatim source text from candidate sections.
- **Immutable Source Seed**: `data/derived/ground_truth_registry.json` is the 10-year golden dataset. `proceedings.db` can be recomputed at any time in ~15s without loss.
- **Saved Review Naming Rule**: All saved reviews in `workspace/reviews/` MUST strictly follow the protocol naming format: `'<Review Protocol> - <keyword(s)>'`.
  - `Dipstick Review - <keyword(s)>`: Fast title & abstract screening sweep across 100% of corpus papers (0 tokens, $< 3\text{ ms}$).
  - `Expanded Scope - <keyword(s)>`: Scope expanded beyond Title & Abstract into candidate sections (`Methodology`, `Findings`, `Discussion`, `Full Text`) or section-targeted FTS5 BM25 search.
  - `Agentic Review - <keyword(s)>`: When an AI agent in Google Antigravity or Anthropic Claude conducts a review and modifies the default protocol (e.g. custom inclusion/exclusion criteria, qualitative section extractions, theoretical coding schemas, or comparative matrix synthesis). If an agent executes an unmodified standard protocol, the default label (`Dipstick Review` or `Expanded Scope`) may be used.
  - Multiple keywords must be cleanly comma-separated (e.g. `Dipstick Review - generative AI, collaborative learning`).

