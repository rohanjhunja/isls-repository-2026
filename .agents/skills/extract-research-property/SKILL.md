---
name: extract-research-property
description: Resolve targets, preview candidate sections via FTS search, extract observations incrementally, and validate evidence.
---

# Skill: extract-research-property

## Purpose & Responsibility
Resolve targets, preview candidate sections via FTS search, extract observations incrementally, and validate evidence.

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

## Guardrails
- Do not process full paper text when candidate sections suffice.
- Preserve manually verified observations.
- Halt property extraction safely if process RSS memory exceeds `--max-memory-gb`.

