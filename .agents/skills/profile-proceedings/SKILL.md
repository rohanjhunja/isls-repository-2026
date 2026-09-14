---
name: profile-proceedings
description: Discover, tune, and test deterministic rules for a new or changed proceedings layout; update profile YAML files and fixtures using standardized naming conventions.
---

# Skill: profile-proceedings

## Purpose & Responsibility
Discover, tune, and test deterministic rules for a new or changed proceedings layout; update profile YAML files and fixtures following standardized volume naming conventions.

## Naming & Path Conventions
- Document IDs must follow standard volume format: `<conference>-<year>-proceedings` (e.g. `cscl-2025-proceedings`, `icls-2026-proceedings`, `isls-2026-proceedings`).
- Profiles live under `profiles/conferences/<conference>-<year>.yaml` or `profiles/conferences/<profile_id>.yaml`.

## Required Inputs
- Target proceedings PDF or document ID (conforming to `<conference>-<year>-proceedings`).
- Sample page range or document sample.
- Target conference acronym, year, and template family.

## Procedure
1. Sample PDF layout, font sizing, line heights, and margin boundaries using PyMuPDF.
2. Cross-reference paper title headers with DSpace ground truth registry (`data/derived/ground_truth_registry.json`).
3. Identify repeating headers, footers, and page-number patterns.
4. Determine title typography rules (e.g. font size ratio relative to body text).
5. Identify paper start signatures and section heading patterns (`#`, `##`, bold headings).
6. Map section headings to dual section labels (`original_heading` + `normalized_section`).
7. Draft or update YAML profile in `profiles/conferences/<profile_id>.yaml`.
8. Test profile rules using `proceedings profile test <profile_id>`. Use GROBID container fallback only if PyMuPDF heading confidence is below 0.7.

## Supported CLI Commands
- `python3 -m proceedings_ingest.cli preflight <doc_id> --sample`
- `python3 -m proceedings_ingest.cli profile suggest <doc_id>`
- `python3 -m proceedings_ingest.cli profile test <profile_id>`

## Guardrails
- Do not hardcode magic offsets without structural justification.
- Ensure title ratio and boundary rules match across sampled papers.
