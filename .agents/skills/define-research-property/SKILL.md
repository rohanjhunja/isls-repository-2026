---
name: define-research-property
description: Convert a research question or extraction requirement into a typed, versioned property definition YAML file with section targeting, keyword triggers, and extraction strategy rules.
---

# Skill: define-research-property

## Purpose & Responsibility
Convert a research question or extraction requirement into a typed, versioned property definition YAML file with section targeting, keyword triggers, and extraction strategy rules.

## Required Inputs
- Property identifier (e.g., `study.participant_age_range`).
- Value schema (type, fields, constraints).
- Targeted canonical sections and heading/text keywords.
- Extraction mode (`exact`, `regex_capture`, `labelled_value`, etc.).

## Procedure
1. Create or update property YAML under `properties/<property_id>.yaml`.
2. Target both `normalized_section` (`methods`, `results`, `discussion_conclusion`) and `original_heading` (author's original heading text).
3. Define `entity_scope`, `value_schema`, `targeting`, `extraction`, and `evidence` requirements.
4. Validate property syntax using `proceedings property validate <property_id>`.

## Supported CLI Commands
- `python3 -m proceedings_ingest.cli property validate <property_id>`

## Guardrails
- Do not enable AI inference unless explicitly required and marked in the property schema.
- Require evidence for all extracted datapoints.
