#!/usr/bin/env python3
import os
import json
import logging
from proceedings_ingest.database import init_database, get_db_connection, insert_paper_record, DEFAULT_DB_PATH
from proceedings_ingest.verified_chunker import VerifiedMDChunker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def populate_database(registry_path: str = "data/derived/ground_truth_registry.json", db_path: str = DEFAULT_DB_PATH):
    print(f"Initializing clean database schema in {db_path}...")
    init_database(db_path)

    if not os.path.exists(registry_path):
        print(f"Error: Registry file {registry_path} not found.")
        return

    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    papers = registry.get("papers", [])
    print(f"Found {len(papers)} papers in ground-truth registry across years 2023–2025.")

    chunker = VerifiedMDChunker(registry_path=registry_path)
    conn = get_db_connection(db_path)

    # Group papers by year
    grouped: dict = {}
    for p in papers:
        grouped.setdefault(p["year"], []).append(p)

    total_inserted = 0
    total_sections = 0

    for yr in sorted(grouped.keys()):
        paper_list = grouped[yr]
        logging.info(f"Processing {len(paper_list)} papers for Year {yr}...")
        year_mds = chunker.load_proceedings_md_for_year(yr)
        logging.info(f"Loaded {len(year_mds)} proceedings MD files for Year {yr}: {list(year_mds.keys())}")

        for idx, gt_p in enumerate(paper_list):
            paper_obj = chunker.chunk_paper_from_gt(gt_p, year_mds)
            
            sec_data = [
                {
                    "id": s.id,
                    "original_heading": s.heading_original,
                    "normalized_section": s.heading_normalized,
                    "level": s.level,
                    "text": s.text,
                    "pdf_start_page": s.pages.pdf_start,
                    "pdf_end_page": s.pages.pdf_end,
                }
                for s in paper_obj.sections
            ]

            p_dict = {
                "id": gt_p["id"],
                "handle": gt_p.get("handle"),
                "handle_url": gt_p.get("handle_url"),
                "doi": gt_p.get("doi"),
                "title": gt_p["title"],
                "year": gt_p["year"],
                "conference": gt_p.get("conference", "ISLS"),
                "paper_type": gt_p.get("paper_type", "Paper"),
                "citation": gt_p.get("citation"),
                "start_page": gt_p.get("start_page"),
                "end_page": gt_p.get("end_page"),
                "abstract": gt_p.get("abstract"),
                "boundary_confidence": paper_obj.extraction.paper_boundary_confidence,
                "filename": paper_obj.filename,
                "authors": gt_p.get("authors", []),
            }

            insert_paper_record(conn, p_dict, sec_data)
            total_inserted += 1
            total_sections += len(sec_data)

            if total_inserted % 250 == 0 or idx + 1 == len(paper_list):
                logging.info(f"Inserted {total_inserted}/{len(papers)} papers (Indexed sections so far: {total_sections})...")

    conn.close()
    print(f"\nSuccessfully populated database {db_path}:")
    print(f"  Total Papers Inserted: {total_inserted}")
    print(f"  Total Sections Indexed: {total_sections}")

if __name__ == "__main__":
    populate_database()
