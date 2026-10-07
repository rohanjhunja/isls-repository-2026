---
name: define-research-property
description: Convert a research question or extraction requirement into a typed, versioned property definition YAML file with section targeting, keyword triggers, and extraction strategy rules.
---

# Skill: define-research-property

## Purpose & Responsibility
Convert a research question or factual extraction requirement into a typed, versioned property definition YAML file with section targeting, keyword triggers, and extraction strategy rules.

## Tri-Modal Architecture Scope: Pathway 2 (Deterministic Metadata)
- **Applicable Domains**: This skill defines properties for **Pathway 2: Deterministic Section Extraction**. Properties are strictly for factual, numerical, and categorical attributes with explicit syntactic signatures (e.g., sample sizes, grade levels, participant demographics, tool/software names).
- **Prohibition on Qualitative Regex Schemas**: Qualitative, interpretive, or theoretical constructs (e.g., teacher agency, co-design roles, pedagogical scaffolding, epistemological stances) MUST NOT be modeled as regex patterns or keyword triggers. Such constructs cannot be accurately captured deterministically and will produce severe false-positive ceiling effects.
- **Pathway 3 Handoff**: For qualitative synthesis, define an agentic qualitative prompt schema under `workspace/reviews/` or invoke **Pathway 3: Full In-Context Agentic Review**, in which the full prose (or explicitly specified sections) is evaluated directly within LLM prompt context.

## Required Inputs
- Property identifier (e.g., `study.participant_age_range`).
- Value schema (type, fields, constraints).
- Targeted canonical sections and heading/text keywords.
- Extraction mode (`exact`, `regex_capture`, `labelled_value`, etc. — strictly for factual metadata).

## Procedure
1. Create or update property YAML under `properties/<property_id>.yaml` (or `workspace/properties/<property_id>.yaml`).
2. Target both `normalized_section` (`methods`, `results`, `discussion_conclusion`) and `original_heading` (author's original heading text).
3. Define `entity_scope`, `value_schema`, `targeting`, `extraction`, and `evidence` requirements.
4. Validate property syntax using `proceedings property validate <property_id>`.

## Supported CLI Commands
- `python3 -m proceedings_ingest.cli property validate <property_id>`

## Guardrails
- Restrict `regex_capture` and `exact` modes to factual, syntactic patterns.
- Do not attempt to encode qualitative or theoretical frameworks into regex.
- Require evidence for all extracted datapoints.
