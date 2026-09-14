# Antigravity Literature Review and Table Update

## 1. Purpose

Update the existing proceedings research system so a user can:

- Start a literature review or continue a saved review.
- Define its paper scope using collections, metadata filters, search criteria, or an explicit paper list.
- Select existing paper data as review columns.
- Define reusable new columns through questions or prompts.
- Extract values with deterministic methods wherever possible and use AI analysis only when required.
- Expand an existing review to more papers, all columns, or selected columns.
- Re-extract selected properties when their queries, rules, constraints, or source data change.
- View, filter, copy, and download read-only review tables.

The table interface is a publishing surface. It must not edit canonical paper data or import changes from exported spreadsheets.

## 2. Required data separation

Preserve the existing distinction between:

1. **Paper records:** bibliographic data, abstract, sections, pages, and extraction metadata already present in paper JSON.
2. **Review definitions:** the review purpose, scope, search criteria, selected papers, selected columns, and display settings.
3. **Property definitions:** reusable questions and extraction requirements for review columns.
4. **Observations:** extracted values with status, evidence, method, confidence, and versions.
5. **Review views and exports:** generated tables, CSV files, and Excel workbooks.

Do not add every review question to the canonical paper schema. Add it as a versioned property definition and store its results as observations.

## 3. Literature review definition

Each saved review must have:

- A stable review ID, name, and optional description.
- Creation and update timestamps.
- A paper scope.
- Stored search criteria.
- An explicit list of included paper IDs after scope resolution.
- Selected columns and their property versions.
- Extraction status by paper and property.
- Table filters, sort order, and visible-column settings.

The paper scope may be defined by any combination of:

- Collections, conferences, journals, years, or other paper metadata.
- Keywords, phrases, exclusions, or a natural-language review prompt.
- Search result thresholds or user-selected search results.
- A list of paper IDs, titles, DOIs, citations, filenames, or uploaded paper files.

When a user shares a paper list, resolve every item to an existing paper where possible. Report unresolved and duplicate items. Ingest or register missing papers only through the existing ingestion workflow.

Search definitions must be saved with the review, including the original prompt, original keywords, accepted keyword expansions, exclusions, filters, scoring settings, and search-definition version.

## 4. Basic review columns

Make the data already present in paper JSON available without new extraction. This should include, where available:

- Paper ID
- Title
- Authors and affiliations
- Abstract
- Author keywords
- Conference or journal
- Year
- Source filename
- PDF and printed page ranges
- Original and canonical section headings
- Section text or links/references to evidence
- Core extraction status and warnings

The user chooses which fields appear. Long source text should remain accessible without making the default table difficult to scan.

## 5. Property/query registry

Every generated review column must refer to a stored, versioned property definition. Store enough information to reproduce the value:

```yaml
property:
  id: study.learning_setting
  version: 1.0.0
  label: Learning setting
  description: Setting in which the reported learning activity occurred.
  value_type: categorical

query:
  question: Where did the learning activity take place?
  candidate_sections: [abstract, method]
  heading_terms: [setting, context, participants, procedure]
  text_terms: [classroom, school, laboratory, online, home]

constraints:
  allowed_values: [classroom, laboratory, home, online, informal, mixed, not_reported]
  maximum_words: null

extraction:
  preferred_methods:
    - existing_paper_field
    - existing_observation
    - labelled_value
    - regex_or_rule
    - derived_calculation
    - prompted_analysis
  inference_allowed: true

evidence:
  required: true
```

A property definition may also constrain:

- Scalar, list, categorical, boolean, number, date, text, or structured output.
- Allowed values and normalisation rules.
- Minimum or maximum length, including word limits.
- Exact extraction versus interpretation or classification.
- Required source sections and evidence.
- Handling of multiple, conflicting, missing, or ambiguous values.

Preserve the user's original question as well as the normalised extraction instructions.

## 6. Reuse before creating a property

Whenever the user requests a new column or changes a column question, Antigravity must:

1. Check canonical paper fields.
2. Search existing property definitions, aliases, observations, capability metadata, extraction strategies, and applicable skills/rules.
3. Show close matches and explain whether the existing property can be used unchanged or extended.
4. Ask for confirmation before creating a separate property when a close existing definition exists.

Use an existing property unchanged when its meaning, output type, constraints, and evidence requirements match. Create a new version when its extraction rules or compatible constraints change. Create a distinct property when the requested concept or meaning differs.

Do not silently broaden the meaning of a property merely to reuse it.

## 7. Deterministic-first extraction

For each paper-property pair, apply this order:

1. Reuse a valid existing paper field or current observation.
2. Select candidate sections using canonical roles, headings, keywords, and the full-text index.
3. Attempt deterministic strategies such as labelled values, regex capture, controlled vocabulary matching, section mapping, document inheritance, or defined calculations.
4. Validate the value against the property schema and constraints.
5. If still unresolved and inference is allowed, retrieve only the most relevant passages and perform prompted analysis.
6. Store the result, evidence, status, extraction method, property version, source version, and run ID.

AI analysis must not receive the entire proceedings or entire paper when targeted passages are sufficient. It must return structured output matching the property schema. Record AI-derived results as inferred or classified, not as exact extraction.

Use these statuses consistently:

- `extracted`
- `inferred`
- `not_present`
- `unresolved`
- `ambiguous`
- `error`

Never invent a value. Evidence should identify the paper, section, page where available, and the supporting source text. Word limits apply to the generated value, not to preserved evidence unless separately configured.

## 8. Re-extraction and scope extension

The user must be able to:

- Re-extract one property, selected properties, or all generated properties.
- Re-extract for selected papers or the entire review.
- Preserve unaffected observations.
- Preview which values will be replaced and why.
- Avoid overwriting manually verified values unless explicitly requested.

Re-extraction is required when a property version, extraction strategy, relevant source paper, or applicable constraint changes.

The user must also be able to extend a saved review:

- To all columns for newly added papers.
- To selected columns only.
- To new columns for all existing papers.
- To new columns for selected papers.

Before a large run, show the paper count, properties affected, values reusable from cache, deterministic strategies, expected AI-analysis cases, and items requiring review.

## 9. Review management

Provide actions to:

- List and open saved reviews.
- Start a new review.
- Continue, rename, duplicate, archive, or update a review.
- Add or remove papers without deleting source paper records.
- Add, remove, reorder, show, or hide review columns.
- Update search criteria and compare the new result set with the previous version.
- Run extraction only for missing or stale cells.
- View review history and the versions used to generate the current table.

Review updates must be incremental. Do not recompute unaffected papers or properties.

## 10. Read-only table capabilities

Provide a local read-only interface, preferably using Streamlit, with:

- One row per paper in the main literature review table.
- Column selection, reordering, filtering, sorting, and text search.
- Clear display of missing, unresolved, ambiguous, and inferred values.
- Access to supporting evidence and extraction provenance.
- Copy of the current table or selected rows as TSV and Markdown.
- Download of the current selection or complete review as CSV and XLSX.

The Excel export should contain:

| Sheet | Contents |
|---|---|
| `Literature Review` | One row per paper with selected columns |
| `Search Definition` | Prompt, keywords, expansions, exclusions, filters, and search version |
| `Evidence` | Property values with source passages, sections, pages, status, and method |
| `Data Dictionary` | Column definitions, types, constraints, and property versions |

Every export must retain stable `paper_id` and property identifiers. Export filenames should include the review name and date. Editing and sharing happen outside the system in Excel, Google Sheets, or another spreadsheet tool; exported edits are not synced back.

## 11. Antigravity operating requirements

Update the always-on workspace rule to require:

- Saved review, search, property, observation, and view definitions.
- Existing-field and existing-property checks before defining a new column.
- Deterministic extraction before prompted analysis.
- Evidence and status for every generated property value.
- Incremental scope extension and version-aware re-extraction.
- Read-only tables and traceable exports.
- No direct insertion of generated values into production JSON, SQLite, or export files by Antigravity.

Add or update focused skills for:

| Skill | Responsibility |
|---|---|
| `manage-literature-review` | Create, continue, update, duplicate, archive, and extend reviews |
| `define-research-property` | Reuse, extend, version, or create column/property definitions |
| `extract-research-property` | Run deterministic-first extraction and targeted AI fallback |
| `search-literature` | Store search criteria, widen keywords, score matches, and resolve scope |
| `publish-research-views` | Build read-only tables and copy/download outputs |

Skills should define required inputs, decision points, relevant CLI operations, validation, and completion reporting. Keep production extraction logic in versioned Python strategies and YAML definitions rather than skill prose.

Antigravity must present a preview before creating a materially different property, running AI analysis across many papers, replacing existing observations, or greatly expanding review scope.

## 12. Suggested command surface

The exact command names may follow the existing CLI conventions, but the system should support equivalents of:

```bash
proceedings review create
proceedings review list
proceedings review show <review-id>
proceedings review update <review-id>
proceedings review add-papers <review-id>
proceedings review extend <review-id>

proceedings property find "<column request>"
proceedings property define
proceedings property preview <property-id> --review <review-id>
proceedings property extract <property-id> --review <review-id>
proceedings property reextract <property-id> --review <review-id>

proceedings review table <review-id>
proceedings export csv <review-id>
proceedings export xlsx <review-id>
```

Antigravity should call the CLI for production changes and inspect its reports. It should not implement one-off extraction by editing data files directly.

## 13. Completion criteria

The update is complete when a user can:

1. Create or resume a named review and define its scope.
2. Populate it from a search or supplied paper list.
3. Select existing paper JSON fields as columns.
4. Request a new column and receive reuse/extension suggestions before a new property is created.
5. Extract constrained values with deterministic methods first and targeted AI analysis only when necessary.
6. Re-extract selected existing properties.
7. Extend a review across selected papers and/or selected columns.
8. Inspect values, evidence, status, and provenance in a read-only table.
9. Copy the displayed table and download traceable CSV/XLSX exports.
10. Reproduce the table from stored review, property, observation, and source versions.
