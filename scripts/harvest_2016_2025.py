#!/usr/bin/env python3
import os
import json
import logging
from proceedings_ingest.dspace_harvester import DSpaceHarvester, save_ground_truth_registry

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

REGISTRY_PATH = "data/derived/ground_truth_registry.json"

def run_harvest():
    print("=== Phase 6: Harvesting 2016–2025 DSpace Ground Truth ===")
    harvester = DSpaceHarvester()
    
    # Harvest 2016 through 2025
    years_to_harvest = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
    registry = harvester.harvest_all_years(years_to_harvest)
    
    # Read existing 2026 clean papers if present in ground_truth_registry.json
    papers_2026 = []
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            old_reg = json.load(f)
            papers_2026 = [p for p in old_reg.get("papers", []) if p.get("year") == 2026]

    harvested_papers = [p.model_dump() for p in registry.papers]
    all_combined = harvested_papers + papers_2026

    by_year = {}
    for p in all_combined:
        yr = p.get("year")
        by_year[yr] = by_year.get(yr, 0) + 1

    combined_registry = {
        "created_at": registry.created_at,
        "total_papers": len(all_combined),
        "papers_by_year": by_year,
        "papers": all_combined
    }

    os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(combined_registry, f, indent=2)

    print(f"\nSuccessfully saved combined Ground Truth Registry: {len(all_combined)} papers across 2016–2026!")
    print("Papers breakdown by year:")
    for yr in sorted(by_year.keys()):
        print(f"  Year {yr}: {by_year[yr]} papers")

if __name__ == "__main__":
    run_harvest()
