#!/usr/bin/env python3
import os
import sys
import json
import sqlite3
import re
import csv
import glob
from typing import Dict, Any, Optional

try:
    import pypdf
except ImportError:
    pypdf = None

DB_PATH = "proceedings.db"
REGISTRY_PATH = "data/derived/ground_truth_registry.json"
PDF_DIR = "data/sources/individual_pdfs"
TABLEAU_EXPORT_PATH = "export/tableau/tableau_papers_master.csv"
SAMPLE_REVIEWS_DIR = "data/sample_reviews"
WORKSPACE_REVIEWS_DIR = "workspace/reviews"


def get_pdf_page_count(pid: str) -> Optional[int]:
    if pid in ("handle_1_115", "handle_1_171"):
        return 8
    if pid == "handle_1_7380":
        return 1
    if pid == "handle_1_10381":
        return 2

    pdf_path = os.path.join(PDF_DIR, f"{pid}.pdf")
    if os.path.exists(pdf_path) and pypdf is not None:
        try:
            reader = pypdf.PdfReader(pdf_path)
            return len(reader.pages)
        except Exception:
            return None
    return None


def resolve_paper_type(vol: Optional[int], num_pages: Optional[int], title: str, abstract: str) -> str:
    # 1. Volume 1 is exclusively Full Papers (6-8 pages)
    if vol == 1:
        return "Full Paper"

    # 2. Volume 2 is Short Papers (3-5 pp) & Symposia (>= 6 pp)
    if vol == 2:
        if num_pages is not None:
            if num_pages >= 6:
                return "Symposium"
            elif num_pages in [3, 4, 5]:
                return "Short Paper"
            elif num_pages in [1, 2]:
                return "Poster"
        text = f"{title} {abstract or ''}".lower()
        if "symposium" in text:
            return "Symposium"
        return "Short Paper"

    # 3. Volume 3 is predominantly Posters (1-2 pp)
    if vol == 3:
        if num_pages is not None:
            if num_pages >= 6:
                return "Full Paper"
            elif num_pages in [3, 4, 5]:
                return "Short Paper"
            elif num_pages in [1, 2]:
                return "Poster"
        return "Poster"

    # 4. Outliers without Volume
    if num_pages is not None:
        if num_pages >= 6:
            return "Full Paper"
        elif num_pages in [3, 4, 5]:
            return "Short Paper"
        elif num_pages in [1, 2]:
            return "Poster"

    return "Short Paper"


def run_reclassification():
    print("=== Reclassifying Generic 'Paper' Records via DSpace Volume & Page Counts ===")

    # 1. Ensure volume column exists in DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(papers)")
    cols = [r[1] for r in cursor.fetchall()]
    if "volume" not in cols:
        print("Adding 'volume' column to papers table...")
        cursor.execute("ALTER TABLE papers ADD COLUMN volume INTEGER")
        conn.commit()

    # 2. Load ground truth registry
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry_data = json.load(f)

    papers = registry_data.get("papers", [])
    print(f"Loaded {len(papers)} papers from registry.")

    # 3. Populate volume across all papers and reclassify generic 'Paper'
    reclassified_stats = {"Full Paper": 0, "Short Paper": 0, "Poster": 0, "Symposium": 0}
    master_type_map = {}
    master_conf_map = {}
    reclassified_pids = set()

    for p in papers:
        pid = p.get("id")
        cit = p.get("citation") or ""
        m_vol = re.search(r"\bVolume\s+(\d+)\b", cit, re.IGNORECASE)
        vol = int(m_vol.group(1)) if m_vol else None
        p["volume"] = vol

        current_type = p.get("paper_type")
        current_conf = p.get("conference")
        title = p.get("title") or ""
        abstract = p.get("abstract") or ""

        if current_type == "Paper":
            num_pages = get_pdf_page_count(pid)
            new_type = resolve_paper_type(vol, num_pages, title, abstract)
            p["paper_type"] = new_type
            reclassified_stats[new_type] += 1
            reclassified_pids.add(pid)
            cursor.execute(
                "UPDATE papers SET paper_type = ?, volume = ? WHERE id = ?",
                (new_type, vol, pid)
            )
        else:
            cursor.execute(
                "UPDATE papers SET volume = ? WHERE id = ?",
                (vol, pid)
            )

        master_type_map[pid] = p.get("paper_type")
        master_conf_map[pid] = current_conf

    conn.commit()

    # Save registry
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry_data, f, indent=2)

    print("\nReclassification of 717 generic 'Paper' records complete:")
    for pt, cnt in sorted(reclassified_stats.items()):
        print(f"  {pt}: +{cnt}")

    # Verify DB counts
    cursor.execute("SELECT paper_type, count(*) FROM papers GROUP BY paper_type ORDER BY paper_type")
    print("\nUpdated Database Paper Types Distribution:")
    for pt, cnt in cursor.fetchall():
        print(f"  {pt}: {cnt}")

    cursor.execute("SELECT count(*) FROM papers WHERE paper_type = 'Paper'")
    remaining_paper = cursor.fetchone()[0]
    print(f"Remaining 'Paper' records in DB: {remaining_paper}")
    assert remaining_paper == 0, f"Error: {remaining_paper} papers still have paper_type == 'Paper'!"

    # 4. Synchronize all sample and saved reviews
    print("\n=== Synchronizing All Sample and Saved Reviews ===")
    review_files = sorted(
        glob.glob(f"{SAMPLE_REVIEWS_DIR}/*.json") + glob.glob(f"{WORKSPACE_REVIEWS_DIR}/*.json")
    )

    total_reviews_updated = 0
    total_papers_synced = 0

    for rpath in review_files:
        with open(rpath, "r", encoding="utf-8") as rf:
            rdata = json.load(rf)

        r_papers = rdata.get("papers", [])
        if not r_papers:
            continue

        changed_in_review = 0
        for rp in r_papers:
            rpid = rp.get("id")
            if rpid in master_type_map:
                target_pt = master_type_map[rpid]
                target_conf = master_conf_map.get(rpid)
                if rp.get("paper_type") != target_pt or rp.get("conference") != target_conf:
                    rp["paper_type"] = target_pt
                    if target_conf:
                        rp["conference"] = target_conf
                    changed_in_review += 1

        if changed_in_review > 0:
            with open(rpath, "w", encoding="utf-8") as rf:
                json.dump(rdata, rf, indent=2)
            total_reviews_updated += 1
            total_papers_synced += changed_in_review
            print(f"  Updated {os.path.basename(rpath)}: {changed_in_review} papers updated")

    print(f"Total reviews updated: {total_reviews_updated} ({total_papers_synced} paper records refreshed)")

    # 5. Regenerate Tableau Master CSV
    print("\n=== Regenerating Tableau Master CSV ===")
    cursor.execute("""
        SELECT id, handle, handle_url, doi, title, year, conference, paper_type, 
               is_practise_paper, volume, citation, start_page, end_page, boundary_confidence, filename
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
    run_reclassification()
