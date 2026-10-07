---
name: extract-research-property
description: Resolve targets, preview candidate sections via FTS search, extract observations incrementally, and validate evidence.
---

# Skill: extract-research-property

## Purpose & Responsibility
Resolve targets, preview candidate sections via FTS search, extract discrete factual observations incrementally, and validate evidence.

## Tri-Modal Architecture Role: Pathway 2 (Deterministic Metadata Only)

This skill operates strictly within **Pathway 2: Deterministic Section Extraction**:
- **Permitted Scope**: Bounded, deterministic extraction of factual, numerical, or discrete structural variables (e.g., participant sample sizes, age ranges, grade levels, named software tools, study duration, geographic locations).
- **Strict Prohibition on Qualitative Mocking**: This skill and its underlying CLI (`proceedings property extract`) MUST NEVER be used for nuanced qualitative, conceptual, or theoretical coding (e.g. teacher agency, co-design roles, pedagogical frameworks, learning mechanisms). Never use regex, lemma matching, or keyword bag-of-words heuristics to simulate qualitative analysis.
- **Handoff to Pathway 3**: Any qualitative, conceptual, or interpretive analysis requested by the user MUST be routed to **Pathway 3: Full In-Context Agentic Review** (`manage-literature-review`), loading the complete, unabridged prose (full paper or explicitly specified sections) directly into LLM prompt context.

## Required Inputs
- Property ID and version.
- Target collection, years, or paper IDs.

## Procedure
1. Query FTS5 index to find candidate sections matching property targeting keywords.
2. Preview candidate sections on a sample of papers.
3. Run defined extraction strategies against candidate sections only.
4. Validate extracted value shapes and store observations with evidence under `data/observations/`.
5. Return extraction status summary (extracted, not_present, unresolved, ambiguous).

## Supported CLI Commands
- `python3 -m proceedings_ingest.cli property preview <property_id> --review <review_id> --limit 10`
- `python3 -m proceedings_ingest.cli property extract <property_id> --review <review_id> --max-memory-gb 8.0`

## Memory Safety & High Data Volume Guidelines
- **Incremental Extraction**: Process paper records sequentially and release loaded paper JSON objects (`del paper`) immediately after extracting properties.
- **Section Targeting**: Only load candidate sections into memory instead of storing full paper text corpora.
- **Garbage Collection**: Invoke explicit garbage collection (`gc.collect()`) periodically during large batch property extractions across hundreds of papers.

## Mandatory Method Reporting Standard
Every extraction report, summary table, or output artifact MUST report the execution method badge:
- **Execution Method**: `◈ Deterministic Section Extraction`
- **Text Coverage**: Candidate Sections Only (`<normalized_section>`)
- **Epistemic Standard**: `◇ Regex / Controlled Vocabulary Extraction`
- **Attribution Status**: N/A (Factual/Structural Metadata)

## Guardrails
- Do not process full paper text when candidate sections suffice for factual metadata.
- Preserve manually verified observations.
- Halt property extraction safely if process RSS memory exceeds `--max-memory-gb`.
- **Saved Review Naming Rule**: When an AI agent conducts a review and modifies the default protocol (e.g. custom inclusion/exclusion criteria, qualitative section extractions, theoretical coding schemas, or comparative matrix synthesis), the review MUST be named: `'Agentic Review - <keyword(s)>'`. If an unmodified standard protocol is executed, use `'Dipstick Review - <keyword(s)>'` or `'Expanded Scope - <keyword(s)>'`.

