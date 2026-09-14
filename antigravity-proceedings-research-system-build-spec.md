# Antigravity Proceedings Research System — Build Specification

## 1. Purpose

Build a local-first system that lets Antigravity:

1. Add conference proceedings PDFs.
2. Convert each PDF into clean, searchable Markdown.
3. identify and separate papers within each proceedings document.
4. Extract paper metadata and section text into a common JSON structure.
5. Add new research datapoints for selected papers or sections using reusable rules.
6. Create and refresh dashboards, CSV files, and Excel workbooks from validated data.

The system must scale across at least ten years and multiple conferences. Routine ingestion and extraction must be deterministic, auditable, and economical in model-token use. Antigravity should orchestrate the system and help author rules; Python should perform production extraction.

## 2. Design principles

- Preserve source PDFs unchanged.
- Extract all available text before considering AI-generated or inferred fields.
- Process each PDF fully only once; cache reusable derivatives.
- Do not use Markdown as the only intermediate because it loses page layout and typography.
- Prefer headings, labels, Markdown structure, keyword search, regex, document inheritance, and indexed retrieval.
- Open only candidate sections when adding a new datapoint; do not repeatedly parse complete proceedings or papers.
- Preserve the paper's original headings while mapping them to a small common section vocabulary.
- Keep question-specific observations separate from core paper data.
- Store evidence and provenance for every extracted datapoint.
- Flag ambiguity; never invent unavailable values.
- Treat dashboards and spreadsheets as generated views, not sources of truth.

## 3. System boundary

### Antigravity is responsible for

- Selecting and invoking supported CLI operations.
- Sampling new document layouts and proposing extraction profiles.
- Creating or updating versioned YAML rules and fixtures.
- Defining new research properties from user questions.
- Reviewing dry runs, validation reports, and low-confidence cases.
- Updating view definitions and requesting exports.
- Changing Python only when the existing strategy registry cannot express a required rule.

### The Python system is responsible for

- File registration, hashing, caching, and stage invalidation.
- PDF preflight, OCR selection, layout extraction, and Markdown creation.
- Header, footer, and page-number cleanup.
- Paper segmentation, metadata extraction, and section mapping.
- Search indexing and targeted property extraction.
- Schema validation, audit reporting, and export generation.

Antigravity must not directly edit production JSON, SQLite databases, observations, spreadsheets, or dashboards to insert extracted values.

## 4. Recommended technology

Use Python 3.11 or newer with `uv` for dependency and command management.

| Need | Default | Notes |
|---|---|---|
| Layout-aware PDF extraction | Docling | Primary PDF-to-structured-data and Markdown converter |
| Selective OCR | OCRmyPDF + Tesseract | Use only on pages without usable text |
| PDF inspection/debugging | pdfplumber | Coordinates and low-level diagnostics |
| Scholarly metadata fallback | GROBID | Optional; run on split, low-confidence papers only |
| Data models/schema | Pydantic | Python models are the canonical schema source |
| YAML configuration | PyYAML or ruamel.yaml | Profiles, properties, and views |
| Fuzzy matching | RapidFuzz | TOC-to-title and heading matching |
| Search/catalogue | SQLite with FTS5 | One local index across documents and papers |
| Tabular processing | Polars or Pandas | View materialisation |
| Excel output | openpyxl | Formatted workbooks |
| Local dashboard | Streamlit | Reads prepared SQLite views only |
| Tests | pytest | Unit, profile, golden, and integration tests |

GROBID and OCR are optional local services. The core system must still ingest clean born-digital PDFs without them.

## 5. Repository structure

```text
proceedings-research/
├── .agents/
│   ├── rules/
│   │   └── proceedings-system.md
│   └── skills/
│       ├── profile-proceedings/SKILL.md
│       ├── ingest-proceedings/SKILL.md
│       ├── define-research-property/SKILL.md
│       ├── extract-research-property/SKILL.md
│       ├── audit-research-data/SKILL.md
│       └── publish-research-views/SKILL.md
├── agent-workflows/
│   ├── add-proceedings.md
│   ├── add-datapoint.md
│   ├── refresh-research-view.md
│   └── audit-research-data.md
├── src/proceedings_ingest/
│   ├── cli.py
│   ├── pipeline.py
│   ├── models.py
│   ├── profiles.py
│   ├── stages/
│   └── extractors/
├── profiles/
│   ├── common.yaml
│   └── conferences/
├── properties/
├── views/
├── schemas/
├── tests/
│   ├── fixtures/
│   ├── golden/
│   └── profiles/
├── data/
│   ├── incoming/
│   ├── sources/
│   ├── derived/
│   ├── observations/
│   ├── reports/
│   └── index/
├── apps/dashboard.py
├── pyproject.toml
├── compose.yaml
├── Makefile
└── README.md
```

Keep large PDFs and generated data outside Git. Version-control code, profiles, property definitions, view definitions, schemas, tests, and representative small fixtures.

## 6. Data layers

Maintain five distinct layers:

1. **Sources:** immutable PDFs and their registry records.
2. **Derivatives:** clean Markdown, layout manifests, paper Markdown, and paper JSON.
3. **Properties:** versioned definitions of additional research datapoints.
4. **Observations:** extracted property values with evidence and extractor version.
5. **Views:** dashboard, CSV, and workbook configurations built from validated records.

SQLite is a generated search and reporting index. It must be rebuildable from files in the first four layers.

## 7. Ingestion pipeline

```text
PDF
→ register and fingerprint
→ preflight and OCR decision
→ layout-aware block extraction
→ page-furniture cleanup
→ clean proceedings Markdown + layout manifest
→ paper-boundary detection
→ per-paper Markdown
→ metadata and section extraction
→ validated paper JSON
→ SQLite FTS index
```

### 7.1 Register

For every source, store:

- Stable document ID.
- Original filename and location.
- SHA-256 hash.
- File size and PDF page count.
- Conference or journal, year, and document type when known.
- Selected profile ID and version.
- Pipeline version and processing status.

Deduplicate by hash. Cache stages using source hash, pipeline version, profile version, and stage version.

### 7.2 Preflight

Inspect PDF metadata, bookmarks, the first pages, likely contents/index pages, sample internal pages, and the final pages. Determine:

- Whether embedded text is usable.
- Whether the layout is single-column, multi-column, mixed, or scanned.
- Likely TOC and paper-start patterns.
- Repeated page-edge content.
- Font-size and heading patterns.

OCR only pages whose text layer is absent or unusable.

### 7.3 Layout extraction

Retain a compact block manifest beside the Markdown. Each block should contain only the data required for reconstruction and auditing:

```json
{
  "block_id": "p012-b008",
  "pdf_page": 12,
  "printed_page": "87",
  "bbox": [72.4, 104.2, 516.7, 138.1],
  "type": "heading",
  "text": "3. Research Method",
  "font_size": 13.0,
  "is_bold": true,
  "column": 1,
  "reading_order": 17
}
```

Store as compressed JSON Lines if size warrants it.

### 7.4 Clean page furniture

Detect headers, footers, and page numbers using both position and repetition. Do not remove text merely because it is near a page edge.

- A likely header/footer recurs across pages at a stable vertical position.
- Normalisation may ignore changing page numbers, years, or running paper titles.
- A likely page number lies in an edge zone and follows a sequence or repeated pattern.
- Retain recognised printed page numbers as metadata.
- Preserve non-recurring footnotes.
- Record why every removed block was removed.

### 7.5 Markdown output

Create readable Markdown with page provenance:

```markdown
<!-- page: pdf=12 printed=87 -->

# Paper title

**Authors:** Author One; Author Two

## Abstract

Exact source text...
```

Create one full proceedings Markdown file and one Markdown file per detected paper.

### 7.6 Paper boundaries

Score several signals rather than relying on one regex:

- PDF bookmarks.
- TOC title and printed-page matches.
- Large or distinctive title typography.
- Title → authors/affiliations → abstract/keywords sequence.
- DOI, copyright, citation, or conference-template markers.
- References/appendix ending followed by a new title.

Store boundary confidence and contributing signals. Send low-confidence or unmatched regions to review. No text may silently disappear.

### 7.7 Core metadata and sections

Extract exact text where present:

- Title.
- Authors and affiliations when reliably separable.
- Abstract.
- Keywords.
- Conference or journal.
- Year.
- Source filename.
- PDF and printed page range.
- Original headings and subheadings.
- Section text.

Map original headings to canonical roles such as `introduction`, `method`, `analysis`, `results`, `discussion`, and `conclusion`. Preserve every original heading, including unmapped headings. A combined heading may map to multiple roles while its text is stored once.

## 8. Canonical data structures

Pydantic models are the source of truth and should generate JSON Schema. Keep the core schema stable and bibliographic/structural.

### 8.1 Collection and paper JSON

```json
{
  "schema_version": "1.0.0",
  "collection": {
    "id": "isls-2026",
    "kind": "conference_proceedings",
    "title": "Proceedings of ISLS 2026",
    "conference": {
      "name": "International Society of the Learning Sciences",
      "acronym": "ISLS",
      "year": 2026
    },
    "journal": null,
    "source": {
      "filename": "isls-2026.pdf",
      "sha256": "...",
      "pdf_page_count": 842,
      "markdown_path": "data/derived/isls-2026/proceedings.md"
    },
    "papers": [
      {
        "id": "isls-2026-example-paper",
        "title": "Example paper title",
        "authors": [
          {
            "display_name": "First Author",
            "given_name": "First",
            "family_name": "Author",
            "affiliations": []
          }
        ],
        "keywords": ["collaborative learning"],
        "abstract": "Exact extracted text.",
        "conference": {"name": "...", "acronym": "ISLS"},
        "journal": null,
        "year": 2026,
        "filename": "isls-2026.pdf",
        "pages": {
          "pdf_start": 24,
          "pdf_end": 35,
          "printed_start": "11",
          "printed_end": "22"
        },
        "canonical_sections": {
          "introduction": ["sec-001"],
          "method": ["sec-004"],
          "analysis": [],
          "results": ["sec-006"],
          "discussion": ["sec-007"],
          "conclusion": ["sec-007"]
        },
        "sections": [
          {
            "id": "sec-004",
            "heading_original": "3. Methodology",
            "heading_normalized": "Methodology",
            "level": 1,
            "parent_id": null,
            "canonical_roles": ["method"],
            "text": "Exact section text.",
            "pages": {"pdf_start": 28, "pdf_end": 30},
            "markdown_range": {"start_line": 270, "end_line": 410}
          }
        ],
        "extraction": {
          "profile_id": "isls-template-2024-2026",
          "profile_version": "1.0.0",
          "paper_boundary_confidence": 0.97,
          "field_status": {
            "title": "extracted",
            "authors": "extracted",
            "keywords": "extracted",
            "abstract": "extracted"
          },
          "warnings": []
        }
      }
    ]
  }
}
```

Allowed field states should include `extracted`, `not_present`, `unresolved`, `ambiguous`, and `manually_verified`. Use `null` for an unresolved or inapplicable scalar and an empty list for a confirmed empty collection.

### 8.2 Property definition

New research questions normally create versioned property definitions, not new paper-schema fields.

```yaml
property:
  id: study.participant_age_range
  version: 1.0.0
  label: Participant age range
  description: Explicitly reported minimum and maximum participant ages.
  entity_scope: paper

value_schema:
  type: object
  required: [minimum, maximum, unit]

targeting:
  canonical_sections: [method]
  heading_keywords: [participants, sample, population]
  text_keywords:
    any_of: [age, aged, years old, mean age]

extraction:
  mode: exact
  strategies:
    - name: regex_capture
      patterns:
        - '(?i)aged?\s+(?<minimum>\d{1,2})\s*(?:-|–|to)\s*(?<maximum>\d{1,2})'
  inference_allowed: false

evidence:
  required: true
  maximum_characters: 400
  include_section_id: true
  include_pdf_page: true
```

Support initially:

- Explicitly extractable facts.
- Simple derived calculations from extracted facts.
- Paper inclusion/selection rules.

Keep qualitative classifications and AI inference disabled unless a property explicitly permits and labels them.

### 8.3 Observation

```json
{
  "paper_id": "isls-2026-example-paper",
  "property_id": "study.participant_age_range",
  "property_version": "1.0.0",
  "value": {"minimum": 10, "maximum": 14, "unit": "years"},
  "status": "extracted",
  "evidence": [
    {
      "section_id": "sec-method-participants",
      "pdf_page": 17,
      "text": "Participants were aged between 10 and 14 years."
    }
  ],
  "extractor": {"strategy": "regex_capture", "version": "1.0.0"},
  "run_id": "run-2026-07-22-003"
}
```

Never automatically overwrite a manually verified observation.

## 9. Configurable extraction rules

Put document-template rules in YAML profiles. Reuse profile families across conference years when layouts are compatible.

```yaml
profile:
  id: isls-template-2024-2026
  version: 1.0.0
  applies_to:
    filename_regex: '(?i)isls.*20(24|25|26)'

paper_boundary:
  abstract_heading: '(?i)^(abstract|summary)$'
  toc_match_minimum: 92
  title:
    minimum_font_ratio: 1.35
    maximum_lines: 4

canonical_sections:
  introduction: [introduction, background and introduction]
  method: [method, methods, methodology, research design, materials and methods]
  analysis: [analysis, data analysis, analytical approach]
  results: [results, findings]
  discussion: [discussion, interpretation]
  conclusion: [conclusion, conclusions, concluding remarks]
```

Provide a small Python strategy registry, including:

- `labelled_value`
- `between_headings`
- `heading_mapped_sections`
- `font_ranked_title`
- `author_block`
- `toc_page_match`
- `repeated_edge_text`
- `regex_capture`
- `document_inheritance`

Add a Python extractor only when a property or profile cannot be represented by composing these strategies.

## 10. Search and targeted extraction

Index one row per paper section in SQLite FTS5, including:

```text
paper_id, collection_id, conference, year, title, authors, keywords,
section_id, heading_original, canonical_roles, text,
pdf_page_start, pdf_page_end, json_path
```

For a new property:

1. Resolve the requested collection, years, papers, and section roles.
2. Query metadata and FTS5 for candidate sections.
3. Inspect a small positive and negative sample.
4. Run the defined extractor only on candidate text.
5. Store value, evidence, state, property version, extractor version, and run ID.
6. Validate before refreshing affected views.

If AI inference is added later, pass only retrieved passages and required metadata. Record that the value is inferred, the model/prompt version, and the supporting evidence.

## 11. Antigravity workspace rule

Create `.agents/rules/proceedings-system.md` as a short always-on rule containing these requirements:

```markdown
# Proceedings Research System

- Source PDFs are immutable. Profiles, schemas, properties, and views are version-controlled.
- Use the supported Python CLI for ingestion, extraction, validation, indexing, and export.
- Do not directly edit generated JSON, observations, SQLite, dashboards, or spreadsheets.
- Prefer YAML/profile changes over Python; add code only for a new reusable strategy.
- Preserve exact source text and original headings. Never invent missing values.
- Every datapoint requires traceable evidence and a valid extraction state.
- Query indexed candidate sections before opening complete papers or proceedings.
- OCR only pages without usable embedded text.
- A new research question normally creates a property definition, not a core schema field.
- Version rule and property changes; rerun only affected stages or records.
- Do not overwrite manually verified observations automatically.
- Dashboards and spreadsheets are generated views, not authoritative sources.
- Run relevant tests and validation after every rule, schema, property, or code change.
- Report targeted, extracted, not-present, unresolved, ambiguous, and warning counts.
```

Do not place conference-specific extraction rules in the workspace rule.

## 12. Required Antigravity skills

Each skill lives at `.agents/skills/<name>/SKILL.md` and contains: purpose/trigger, required inputs, procedure, supported CLI commands, guardrails, validation, and completion report.

| Skill | Trigger and responsibility |
|---|---|
| `profile-proceedings` | Discover and test deterministic rules for a new or changed proceedings layout; update profile YAML and fixtures. |
| `ingest-proceedings` | Register a new PDF, select/profile its template, ingest, validate, and index it. |
| `define-research-property` | Convert a question into a typed, versioned property definition with targeting, evidence, and extraction rules. |
| `extract-research-property` | Resolve targets, preview candidate sections, extract observations incrementally, and validate evidence. |
| `audit-research-data` | Audit paper boundaries, retained text, metadata, observations, evidence, and stale versions. |
| `publish-research-views` | Create or update view YAML and generate dashboard tables, CSV, and Excel output from validated data. |

### Shared skill guardrails

- Use dry runs or previews before broad changes.
- Show the proposed profile/property/view definition before first use.
- Modify production data only through the CLI.
- Do not infer unless explicitly allowed by the property.
- Do not use a complete paper when candidate sections are sufficient.
- Do not accept observations without evidence.
- Preserve manually verified data.
- Report the exact scope and counts changed.

## 13. User-facing workflows

Keep canonical copies in `agent-workflows/` and register them as Antigravity slash workflows.

### `/add-proceedings`

Required inputs: PDF path, collection/conference, year, document type, and expected paper count if known.

Behaviour:

1. Register and fingerprint.
2. Preflight and select the best profile.
3. Invoke `profile-proceedings` if no profile fits.
4. Ingest to Markdown and paper JSON.
5. Validate boundaries, text retention, and core fields.
6. Update the index.
7. Return the ingestion report and unresolved issues.

### `/add-datapoint`

Required inputs: research question/property ID, target collections/years/papers, desired value shape, extraction-only versus allowed inference, and target view.

Behaviour:

1. Reuse an existing property or invoke `define-research-property`.
2. Resolve papers and candidate sections.
3. Preview the definition and a small result sample.
4. Extract across the approved target.
5. Validate observations and evidence.
6. Refresh only affected views.

### `/refresh-research-view`

Required inputs: view name, row grain, columns, filters, and output formats.

Behaviour:

1. Update or create view YAML.
2. Validate requested fields and property versions.
3. Materialise data from the index and observations.
4. Create dashboard tables and requested CSV/XLSX exports.
5. Include stable paper IDs and evidence references.

### `/audit-research-data`

Required input: collection, document, year range, property, or view scope.

Check paper counts, unmatched pages, missing metadata, unknown headings, text retention, evidence coverage, invalid values, stale versions, and view traceability. Report issues without repairing them unless explicitly requested.

## 14. CLI contract

Implement a stable CLI named `proceedings`. Exact internals may vary, but support this command surface:

```bash
# Setup and health
uv sync
uv run proceedings doctor

# Sources and ingestion
uv run proceedings register data/incoming/ISLS-2026.pdf
uv run proceedings preflight ISLS-2026 --sample
uv run proceedings profile suggest ISLS-2026
uv run proceedings profile test isls-template-2024-2026
uv run proceedings ingest ISLS-2026
uv run proceedings audit ingestion ISLS-2026

# Properties
uv run proceedings property validate study.participant_age_range
uv run proceedings property preview study.participant_age_range --collection ISLS --years 2022:2026 --limit 10
uv run proceedings property extract study.participant_age_range --collection ISLS --years 2022:2026

# Index and views
uv run proceedings index update
uv run proceedings view build study-demographics
uv run proceedings export csv study-demographics
uv run proceedings export xlsx study-demographics

# Application and tests
uv run streamlit run apps/dashboard.py
uv run pytest
```

All commands that change data should support a dry-run or preview mode where meaningful and return machine-readable run reports.

## 15. Local setup and operation

### Requirements

- Python 3.11+.
- `uv`.
- SQLite with FTS5.
- Docker only if using GROBID.
- OCRmyPDF and Tesseract only if scanned material is expected.
- Enough disk space for source PDFs, derivatives, OCR copies, and indexes.

### Initial setup

```bash
git clone <repository-url> proceedings-research
cd proceedings-research
uv sync
uv run proceedings doctor
uv run pytest
```

Optional:

```bash
docker compose up -d grobid
```

### Normal use

1. Place a PDF in `data/incoming/`.
2. Open the repository and data folder in one Antigravity project.
3. Run `/add-proceedings`.
4. Review the ingestion report and low-confidence items.
5. Use `/add-datapoint` for new questions.
6. Use `/refresh-research-view` for dashboard or spreadsheet changes.
7. Use `/audit-research-data` before publishing or after rule changes.

The Streamlit dashboard must read only validated, indexed records and must never trigger PDF parsing during page load or filtering.

### Antigravity permissions

- Scope the project to the repository and its data directory.
- Keep command execution in request-review mode during initial development.
- Disable access outside project folders.
- Prefer sandboxing.
- After dependencies and models are installed, network access should not be required for routine ingestion.
- Allow only documented project commands, tests, version-control inspection, and dashboard startup.

## 16. Validation and audit requirements

Every ingestion report must include:

- Expected TOC entries versus detected papers.
- Unmatched TOC entries and low-confidence boundaries.
- Overlapping paper ranges.
- Pages or blocks not assigned to papers or explicit non-paper regions.
- Source text retained and blocks removed, with removal reasons.
- Samples of removed headers, footers, and page numbers.
- Missing or unresolved core fields.
- Unknown headings and unmapped section roles.
- Profile, property, extractor, pipeline, and schema versions.

Every property extraction report must include:

- Papers targeted and candidate sections searched.
- Values extracted.
- `not_present`, `unresolved`, and `ambiguous` counts.
- Observations missing evidence.
- Validation failures.
- Manually verified values preserved.
- Views refreshed.

Critical invariants:

- Every source block is retained, deliberately removed with a reason, or assigned to an explicit unclassified region.
- Paper ranges do not overlap unintentionally.
- Original headings are never replaced by canonical headings.
- Canonical roles are mappings, not rewritten source structure.
- Every observation is traceable to a paper, property version, extraction run, and evidence passage.
- Generated indexes and views can be rebuilt from file-backed sources of truth.

## 17. Incremental processing

Recompute only affected work:

- Converter change → invalidate layout, Markdown, papers, index, observations, and views.
- Boundary-profile change → rerun segmentation and downstream stages for matching documents.
- Heading-alias change → rerun section mapping and affected properties/views.
- Property-definition change → create a new version and re-extract only that property for its targets.
- View-definition change → rebuild only the view/export.

Parallelise by source document and, after segmentation, by paper where safe.

## 18. Delivery phases

### Phase 1 — Minimum usable system

- Repository and CLI scaffold.
- Source registry and hashing.
- Docling-based extraction and Markdown output.
- Layout manifest and page-furniture cleanup.
- One conference profile.
- Paper segmentation and core JSON.
- Pydantic schema and validation reports.
- SQLite FTS5 index.

### Phase 2 — Research properties

- Property schema and observation store.
- Targeted section retrieval.
- Exact extraction strategies and evidence capture.
- Preview, extract, audit, and versioning commands.
- Required Antigravity skills and workflows.

### Phase 3 — Views and scale

- View definitions, Streamlit dashboard, CSV, and XLSX exports.
- Multiple conferences/years and reusable profile families.
- Selective OCR and optional GROBID fallback.
- Regression fixtures, performance checks, and incremental rebuilds.

Do not add vector databases, distributed services, or AI inference during Phase 1 unless actual scale or document quality demonstrates a need.

## 19. Definition of done

The initial system is complete when it can:

1. Ingest a representative proceedings PDF without altering the source.
2. Produce clean proceedings and per-paper Markdown with page provenance.
3. Detect papers and report uncertain boundaries.
4. Export schema-valid paper JSON containing core metadata, original sections, canonical mappings, pages, and extraction status.
5. Rebuild a cross-document FTS index.
6. Define one new property from a user question and extract it from targeted sections with evidence.
7. Generate a traceable dashboard table, CSV, and Excel workbook.
8. Rerun only affected stages after a profile, property, or view change.
9. Pass automated tests and produce human-readable audit reports.
10. Perform routine ingestion and extraction locally without model calls.

## 20. Final implementation constraint

Build the smallest system that satisfies these contracts. Prefer clear files, typed models, declarative YAML, and composable Python stages over framework-heavy abstractions. Add complexity only when failures in real proceedings documents justify it.
