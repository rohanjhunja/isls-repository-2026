---
name: benchmark-human-coding
description: (DEPRECATED) Please use the 3 decoupled modular skills instead - ingest-baseline-review, execute-agentic-review, and compare-literature-reviews.
---

# Skill: benchmark-human-coding (DEPRECATED)

> [!WARNING]
> **This skill has been deprecated and decomposed into 3 non-overlapping modular skills**:
> 1. `ingest-baseline-review`: For ingesting human/baseline qualitative data, matching database references, and creating an immutable sealed baseline (`workspace/reviews/<id>_baseline.json`).
> 2. `execute-agentic-review`: For executing in-context qualitative literature reviews with parallel workers, independent context per paper, canonical normalized sections, and 5-level evidence taxonomy.
> 3. `compare-literature-reviews`: For comparing any two reviews (baseline vs agentic, or review A vs B), computing Cohen's Kappa, diagnosing divergences, and generating synthesis reports.

Please invoke the respective individual skills based on the required operation.
