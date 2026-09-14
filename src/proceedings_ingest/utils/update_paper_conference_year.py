import os
import json
import re
from typing import Dict, Any, Tuple
from proceedings_ingest.models import Collection, ConferenceInfo, Paper
from proceedings_ingest.stages.indexing import IndexingStage

CONF_MAPPING = {
    "cscl": {
        "acronym": "CSCL",
        "name": "Computer-Supported Collaborative Learning"
    },
    "icls": {
        "acronym": "ICLS",
        "name": "International Conference of the Learning Sciences"
    },
    "isls": {
        "acronym": "ISLS",
        "name": "International Society of the Learning Sciences"
    },
    "general": {
        "acronym": "ISLS",
        "name": "International Society of the Learning Sciences"
    }
}


def parse_conference_and_year(filename_or_vol: str) -> Tuple[Dict[str, str], int]:
    """Parse conference name/acronym and year by splitting/matching the filename or volume string."""
    s = filename_or_vol.lower()
    
    # Extract 4-digit year starting with 20
    year_match = re.search(r"\b(20\d{2})\b", s)
    year = int(year_match.group(1)) if year_match else 2026

    # Extract conference acronym by splitting/searching filename tokens
    conf_key = None
    for token in ["cscl", "icls", "isls", "general"]:
        if token in s:
            conf_key = token
            break
            
    if not conf_key:
        conf_key = "isls"

    conf_meta = CONF_MAPPING[conf_key]
    return conf_meta, year


def update_all_papers(base_dir: str):
    data_dir = os.path.join(base_dir, "data")
    derived_dir = os.path.join(data_dir, "derived")
    
    if not os.path.exists(derived_dir):
        print(f"Error: Derived directory {derived_dir} does not exist.")
        return

    volumes = [d for d in os.listdir(derived_dir) if os.path.isdir(os.path.join(derived_dir, d))]
    indexing_stage = IndexingStage(data_dir)

    total_papers_updated = 0

    for vol_id in sorted(volumes):
        vol_json_path = os.path.join(derived_dir, vol_id, f"{vol_id}.json")
        if not os.path.exists(vol_json_path):
            continue

        with open(vol_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        src_filename = data.get("source", {}).get("filename", "")
        # Split/parse filename or volume ID to get specific conference and year
        conf_meta, year = parse_conference_and_year(f"{vol_id} {src_filename}")

        conf_info = {
            "name": conf_meta["name"],
            "acronym": conf_meta["acronym"],
            "year": year
        }

        # Update top-level collection conference
        data["conference"] = conf_info

        # Update each paper in collection
        papers = data.get("papers", [])
        for paper in papers:
            # Set paper-level conference and year specifically based on source file
            paper["conference"] = conf_info
            paper["year"] = year
            
            # Ensure filename is present
            if not paper.get("filename"):
                paper["filename"] = src_filename or f"{vol_id}.pdf"

        # Write updated JSON back to file
        with open(vol_json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        # Parse Collection model and re-index into SQLite proceedings.db
        collection = Collection(**data)
        indexing_stage.build_index(collection)

        total_papers_updated += len(papers)
        print(f"Updated {vol_id}: {len(papers)} papers set to {conf_meta['acronym']} ({year})")

    print(f"\nSuccessfully updated data for all {total_papers_updated} papers across {len(volumes)} volumes!")


if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    update_all_papers(base_dir)
