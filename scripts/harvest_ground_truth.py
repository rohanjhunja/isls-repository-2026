#!/usr/bin/env python3
import sys
import logging
from proceedings_ingest.dspace_harvester import DSpaceHarvester, save_ground_truth_registry

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    print("Starting DSpace Ground-Truth Harvesting for 2023, 2024, and 2025...")
    harvester = DSpaceHarvester()
    registry = harvester.harvest_all_years(years=[2023, 2024, 2025])
    out_path = save_ground_truth_registry(registry, "data/derived/ground_truth_registry.json")
    print(f"\nSuccessfully harvested Ground Truth Registry:")
    print(f"  Total Papers: {registry.total_papers}")
    for yr, count in registry.papers_by_year.items():
        print(f"  Year {yr}: {count} papers")
    print(f"  Output saved to: {out_path}")

if __name__ == "__main__":
    main()
