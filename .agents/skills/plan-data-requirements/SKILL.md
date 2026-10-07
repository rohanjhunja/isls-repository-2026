---
name: plan-data-requirements
description: Pre-flight data requirements audit and query projection planning. Systematically maps required user-facing presentation fields to database attributes and selects query modes before executing repository queries.
---

# Skill: plan-data-requirements

## Purpose & Responsibility
Execute a mandatory pre-flight planning routine before running SQLite database queries or synthesizing analytical outputs. This skill audits the presentation requirements of the user request, maps every display field to its database source, selects the appropriate query mode, and guarantees **Strict Presentation-Query Parity** to eliminate metadata and full-text hallucinations.

## When to Invoke
- Whenever an agent is tasked with listing, tabulating, synthesizing, or reviewing literature from `proceedings.db`.
- Before formulating SQL queries in `query-repository-data`, `search-literature`, or `extract-research-property`.
- Whenever compiling academic tables, paper references, or review matrices.

## Pre-Flight Checklist Procedure

### Step 0: Contextual Methodological Triage & Approach Planning
Before designing queries or tables, the agent plans the overall review methodology:

1. **Explicit Trigger Word Evaluation**:
   Check if the user request contains explicit pathway triggers:
   - **Pathway 1 (Deterministic Dipstick)**: `'dipstick'`, `'dipstick review'`, `'quick search'`, `'sweep'`, `'bm25'`, `'fts5 search'`, `'title/abstract'`, `'title search'`, `'fast scan'`, `'reconnaissance'`, `'keyword search'`.
   - **Pathway 2 (Deterministic Section Extraction)**: `'extract property'`, `'property extraction'`, `'regex extract'`, `'sample size'`, `'sample sizes'`, `'factual metadata'`, `'grade levels'`, `'named tools'`, `'extract numbers'`, `'count occurrences'`, `'demographics'`.
   - **Pathway 3 (Full In-Context Agentic Review)**: `'agentic review'`, `'agentic reviews'`, `'ai-search'`, `'dual agent'`, `'consider the full text'`, `'read full text'`, `'read sections'`, `'qualitative coding'`, `'interpretive review'`, `'thematic analysis'`, `'attribution test'`, `'code-design framework'`, `'agency analysis'`.
   - **Pathway 4 (Staged Hybrid Review)**: `'hybrid review'`, `'screen and synthesize'`, `'filter and read'`, `'dipstick then review'`, `'two-stage review'`, `'sweep then code'`, `'screen then analyze'`, `'filter then code'`.

2. **Contextual Epistemic Triage (When Triggers Are Absent)**:
   If no explicit trigger words are present, assess the nature of the inquiry from context:
   - *Factual / Statistical / Bibliographic* (Counts, distributions, author collaborations, explicit tool names, years) $\rightarrow$ Plan **Pathway 1 or 2**.
   - *Interpretive / Qualitative / Conceptual* (Teacher agency, design tensions, theoretical coding, inclusion rationales, discourse nuance) $\rightarrow$ Plan **Pathway 3**.
   - *Broad Topic Survey with Qualitative Synthesis* $\rightarrow$ Plan **Pathway 4 (Staged Hybrid)**.

3. **Methodological Declaration**:
   Formulate a concise planning note stating the chosen pathway and rationale.

### Step 1: Output Presentation Specification
Explicitly enumerate every field that will be displayed in the final user-facing output (e.g., in tables, cards, citations, or narrative text):
- Primary identifiers: Paper ID, Title, DOI, Handle URL.
- Authorship: Author list, author order, first author.
- Publication context: Year, Conference venue, Paper type, Start/End pages.
- Evidence & Text: Section headings, PDF page provenance, verbatim quotes.
- Analytical codes: Thematic classifications, review frameworks, quantitative counts.

### Step 2: Source Classification & Sigil Mapping (Storage & Output Governance)
Classify each enumerated field under the Source Sigil taxonomy to guarantee data quality and clarity across storage and output:
- `◈` **Database Ground Truth**: Direct attributes from `papers.*`, `authors.*`, `paper_authors.*`.
- `◇` **Database-Derived Metric**: Deterministic counts, frequencies, or percentages computed over DB records via Python code.
- `⌕` **Verbatim Evidence Quote**: Verbatim excerpts from `sections.text` or `papers.abstract` verified via `assert instr(full_text, quote) > 0`.
- `✦` **Agentic Synthesis / Inferred**: Qualitative frameworks, inductive codes, or AI review summaries.

### Step 3: Query Mode Selection
Select the correct query mode based on the task:

1. **Mode A — User-Facing Tabular Listings & Selections (Tier 1 Canonical Projection)**
   - *Trigger*: When generating markdown tables, paper listings, review selections, or formal citations.
   - *Requirement*: MUST project `p.citation` along with core identifiers.
   - *Template*:
     ```sql
     SELECT p.id, p.title, p.citation, p.year, p.conference, p.paper_type, p.doi, p.handle_url, p.start_page, p.end_page
     FROM papers p
     WHERE ...
     ```
   - *Token Footprint*: ~40 tokens per paper. 100% immune to author and bibliographic omissions.

2. **Mode B — Bulk Aggregations, Counts, and Screening Sweeps (Lightweight Projection)**
   - *Trigger*: When calculating corpus distributions, counting papers by year/conference, or broad ID screening sweeps.
   - *Requirement*: Project ONLY minimal filtering fields. Never project `p.citation` or full text.
   - *Template*:
     ```sql
     SELECT p.id, p.year, p.conference FROM papers p WHERE ...
     ```
   - *Token Footprint*: ~5 tokens per paper. Prevents context window exhaustion.

3. **Mode C — Bounded Section Snippets & Evidence Audits (Secondary Bounded Fetches)**
   - *Trigger*: When auditing section presence or retrieving small preview excerpts for metadata tables.
   - *Requirement*: Secondary fetch only after paper selection. Filter strictly by `normalized_section` and bound with `substr(text, 1, N)` or FTS5 `snippet()`.
   - *Template*:
     ```sql
     SELECT paper_id, original_heading, pdf_start_page, substr(text, 1, 500) AS bounded_text, length(text) AS full_len
     FROM sections
     WHERE paper_id IN (?) AND normalized_section = 'methodology';
     ```

4. **Mode D — In-Context Qualitative Review Ingestion (Unabridged Prose for Pathway 3)**
   - *Trigger*: When conducting Pathway 3 Full In-Context Agentic Reviews (`'agentic review'`, `'ai-search'`, `'dual agent'`, `'consider the full text'`, `'read full text'`).
   - *Requirement*: Project complete, unabridged prose in reading order (`order_index`).
   - *Section Scoping Exception*: If the user prompt explicitly designates specific sections (e.g. `--sections methods,results`), filter by those sections; otherwise load all sections.
   - *Template*:
     ```sql
     SELECT normalized_section, section_title, text, pdf_start_page
     FROM sections
     WHERE paper_id = :id
     ORDER BY order_index;
     ```
   - *Invariant*: Never truncate or regex-filter qualitative text in Python; stream complete prose into LLM prompt context for cognitive evaluation.

### Step 4: Anti-Omission Verification
Before writing the final response, verify:
*Are all displayed database fields present in the tool execution result within context?*
- If **YES**: Proceed to format the output.
- If **NO**: Execute an immediate point-lookup query (e.g. `SELECT id, citation FROM papers WHERE id IN (...)`) or explicitly omit the unretrieved field. **NEVER generate ungrounded values from model memory.**

## Source Sigil Formatting Rules
- **Highest Structural Level**: Place sigils in table column headers (e.g. `Paper Reference ◈`, `Review Framework Coded ✦`) whenever the column is homogeneous.
- **Trailing Placement**: Place sigils at the end of the structural unit (end of header, end of cell, or end of paragraph). Never insert mid-sentence.
- **No Dedicated Brackets**: Never wrap sigils in brackets (use `✦⌕`, not `[✦⌕]`).
- **Key Label**: Always label the explanatory key as `Source: ◈ Database Record | ◇ Database-Derived Metric | ⌕ Verbatim Section Evidence | ✦ Agent-Synthesized Coding`.
