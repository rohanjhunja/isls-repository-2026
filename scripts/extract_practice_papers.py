#!/usr/bin/env python3
"""
Extract Practice-Oriented Papers from 2025 and 2026 Proceedings PDFs
and update data/derived/ground_truth_registry.json.
"""

import os
import sys
import json
import re
from typing import List, Dict, Any

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REGISTRY_PATH = os.path.join(BASE_DIR, "data", "derived", "ground_truth_registry.json")
OUTPUT_PATH = os.path.join(BASE_DIR, "workspace", "data", "practice_papers.json")

# Verified canonical IDs identified from proceedings Table of Contents
ICLS_2025_PRACTICE_IDS = [
    "handle_1_11446", "handle_1_11448", "handle_1_11449", "handle_1_11450",
    "handle_1_11451", "handle_1_11452", "handle_1_11453", "handle_1_11454",
    "handle_1_11455", "handle_1_11456", "handle_1_11457", "handle_1_11458",
    "handle_1_11459", "handle_1_11460", "handle_1_11461", "handle_1_11462",
    "handle_1_11463", "handle_1_11464"
]

ICLS_2026_PRACTICE_IDS = [
    "icls-volume-2026-paper-0328", "icls-volume-2026-paper-0329", "icls-volume-2026-paper-0330",
    "icls-volume-2026-paper-0331", "icls-volume-2026-paper-0332", "icls-volume-2026-paper-0333",
    "icls-volume-2026-paper-0334", "icls-volume-2026-paper-0335", "icls-volume-2026-paper-0336",
    "icls-volume-2026-paper-0337", "icls-volume-2026-paper-0338", "icls-volume-2026-paper-0339"
]

ALL_PRACTICE_IDS = set(ICLS_2025_PRACTICE_IDS + ICLS_2026_PRACTICE_IDS)


def main():
    print(f"Loading registry from {REGISTRY_PATH}...")
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)

    papers = registry.get("papers", [])
    print(f"Total papers in registry: {len(papers)}")

    annotated_count = 0
    practice_records: List[Dict[str, Any]] = []

    for p in papers:
        pid = p.get("id")
        if pid in ALL_PRACTICE_IDS:
            p["is_practise_paper"] = True
            annotated_count += 1
            practice_records.append({
                "id": pid,
                "title": p.get("title"),
                "authors": p.get("authors"),
                "year": p.get("year"),
                "conference": p.get("conference"),
                "start_page": p.get("start_page"),
                "end_page": p.get("end_page"),
                "paper_type": p.get("paper_type"),
                "is_practise_paper": True
            })

    print(f"Annotated {annotated_count} papers as Practice Papers (is_practise_paper=True).")

    # Sort practice records by year, start_page
    practice_records.sort(key=lambda x: (x["year"], x.get("start_page") or 0))

    # Write back to ground_truth_registry.json
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    print(f"Updated {REGISTRY_PATH} successfully.")

    # Save reference bundle in workspace/data/practice_papers.json
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "description": "Practice-Oriented Papers (ISLS/ICLS 2025-2026) extracted from proceedings indices",
            "total_count": len(practice_records),
            "by_year": {
                2025: len([p for p in practice_records if p["year"] == 2025]),
                2026: len([p for p in practice_records if p["year"] == 2026])
            },
            "papers": practice_records
        }, f, indent=2, ensure_ascii=False)
    print(f"Saved reference dataset to {OUTPUT_PATH}.")


if __name__ == "__main__":
    main()
