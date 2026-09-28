#!/usr/bin/env python3
import os
import sys
import json
import sqlite3
import re
import csv
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from proceedings_ingest.dspace_harvester import parse_conference

DB_PATH = "proceedings.db"
REGISTRY_PATH = "data/derived/ground_truth_registry.json"
PAPERS_MD_DIR = "data/derived/papers"
TABLEAU_EXPORT_PATH = "export/tableau/tableau_papers_master.csv"

REVIEWS_TO_UPDATE = [
    "workspace/reviews/rev_dipstick_eff7613c.json",
    "workspace/reviews/rev_agentic_teacher_codesign.json",
    "workspace/reviews/rev_agentic_teacher_codesign_tel.json",
]


def realign_conferences():
    print("=== Realigning 2021–2025 Conference Attribution from 'ISLS' to CSCL & ICLS ===")

    # 1. Load ground truth registry
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry_data = json.load(f)

    papers = registry_data.get("papers", [])
    print(f"Loaded {len(papers)} papers from registry.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {"CSCL": 0, "ICLS": 0, "unchanged": 0}
    paper_conf_map = {}
    updated_md_count = 0

    for p in papers:
        pid = p.get("id")
        year = p.get("year")
        current_conf = p.get("conference")
        citation = p.get("citation")
        doi = p.get("doi")

        if 2021 <= year <= 2025:
            resolved_conf = parse_conference(citation, doi, current_conf or "ISLS")
            p["conference"] = resolved_conf
            paper_conf_map[pid] = resolved_conf
            stats[resolved_conf] += 1

            # Update DB
            cursor.execute("UPDATE papers SET conference = ? WHERE id = ?", (resolved_conf, pid))

            # Update Markdown header if exists
            md_path = os.path.join(PAPERS_MD_DIR, f"{pid}.md")
            if os.path.exists(md_path):
                with open(md_path, "r", encoding="utf-8", errors="ignore") as mf:
                    md_text = mf.read()
                new_md_text = re.sub(
                    r"\*\*Conference:\*\*\s*ISLS\s+(\d{4})",
                    rf"**Conference:** {resolved_conf} \1",
                    md_text,
                    count=1,
                )
                if new_md_text != md_text:
                    with open(md_path, "w", encoding="utf-8") as mf:
                        mf.write(new_md_text)
                    updated_md_count += 1
        else:
            paper_conf_map[pid] = current_conf
            stats["unchanged"] += 1

    conn.commit()

    # Save updated registry
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry_data, f, indent=2)

    print(f"Registry and DB updated:")
    print(f"  CSCL reattributed: {stats['CSCL']}")
    print(f"  ICLS reattributed: {stats['ICLS']}")
    print(f"  Pre-2021 / 2026 unchanged: {stats['unchanged']}")
    print(f"  Updated Markdown headers: {updated_md_count}")

    # Verify DB counts
    cursor.execute("SELECT conference, count(*) FROM papers GROUP BY conference ORDER BY conference")
    db_counts = cursor.fetchall()
    print("\nCurrent Database Conference Totals:")
    for conf, cnt in db_counts:
        print(f"  {conf}: {cnt}")

    cursor.execute("SELECT count(*) FROM papers WHERE conference = 'ISLS'")
    isls_remaining = cursor.fetchone()[0]
    print(f"  Remaining 'ISLS' papers in DB: {isls_remaining}")
    assert isls_remaining == 0, f"Error: {isls_remaining} papers still labeled ISLS!"

    # 2. Update reviews
    print("\n=== Updating Reviews Metadata ===")
    for rev_path in REVIEWS_TO_UPDATE:
        if not os.path.exists(rev_path):
            print(f"Warning: {rev_path} does not exist.")
            continue

        with open(rev_path, "r", encoding="utf-8") as rf:
            rev_data = json.load(rf)

        rev_papers = rev_data.get("papers", [])
        rev_conf_stats = {"CSCL": 0, "ICLS": 0}
        remapped_in_review = 0

        for rp in rev_papers:
            rpid = rp.get("id")
            old_c = rp.get("conference")
            if rpid in paper_conf_map:
                new_c = paper_conf_map[rpid]
                rp["conference"] = new_c
                if old_c != new_c:
                    remapped_in_review += 1
            conf_val = rp.get("conference")
            if conf_val in rev_conf_stats:
                rev_conf_stats[conf_val] += 1

        with open(rev_path, "w", encoding="utf-8") as rf:
            json.dump(rev_data, rf, indent=2)

        print(f"Updated {os.path.basename(rev_path)} ({len(rev_papers)} papers):")
        print(f"  Remapped from 'ISLS': {remapped_in_review}")
        print(f"  Breakdown: {rev_conf_stats}")

    # 3. Regenerate tableau_papers_master.csv
    print("\n=== Regenerating Tableau Master CSV ===")
    cursor.execute("""
        SELECT id, handle, handle_url, doi, title, year, conference, paper_type, 
               is_practise_paper, citation, start_page, end_page, boundary_confidence, filename
        FROM papers
        ORDER BY year, conference, id
    """)
    rows = cursor.fetchall()
    col_names = [d[0] for d in cursor.description]

    os.makedirs(os.path.dirname(TABLEAU_EXPORT_PATH), exist_ok=True)
    with open(TABLEAU_EXPORT_PATH, "w", newline="", encoding="utf-8") as cf:
        writer = csv.writer(cf)
        writer.writerow(col_names)
        writer.writerows(rows)

    print(f"Successfully exported {len(rows)} rows to {TABLEAU_EXPORT_PATH}.")
    conn.close()


if __name__ == "__main__":
    realign_conferences()
