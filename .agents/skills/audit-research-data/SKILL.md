---
name: audit-research-data
description: Audit paper boundaries, retained text, core metadata, observations, evidence, and stale profile/property versions across ingested proceedings, enforcing standardized naming conventions.
---

# Skill: audit-research-data

## Purpose & Responsibility
Audit paper boundaries, retained text, core metadata, observations, evidence, naming conventions, and stale profile/property versions.

## Required Inputs
- Collection ID, document ID, or target scope.

## Procedure
1. **Ground-Truth Verification**: Cross-check extracted paper records against `data/derived/ground_truth_registry.json` to verify title accuracy, author list complete matches, DOI presence, and exact page ranges.
2. **Naming Convention Audit**: Verify that all target PDFs follow `<conference>-<year>-proceedings.pdf`, derived folders match `<volume_id>`, and report files match `ingestion_<volume_id>.json`.
3. **Boundary Coverage**: Verify paper boundary coverage (check for gaps or unintentional overlaps against ground-truth paper counts).
4. **Furniture Logs**: Check page furniture removal audit logs.
5. **Metadata Completeness**: Validate presence of core metadata (title, authors, abstract, keywords, pages, DOIs).
6. **Dual Section Labels**: Audit presence of both `original_heading` and `normalized_section` for all paper sections.
7. **Evidence Pointers**: Verify observation evidence pointers match exact section text and PDF pages.
8. **Audit Report**: Generate audit report in `data/reports/audit_<volume_id>.json`.

## Supported CLI Commands
- `python3 -m proceedings_ingest.cli audit ingestion <doc_id>`

## Guardrails
- Do not auto-repair ambiguous boundaries without explicit user instructions.
- Ensure all volume IDs and PDF filenames follow the standardized `<conference>-<year>-proceedings` kebab-case convention.
