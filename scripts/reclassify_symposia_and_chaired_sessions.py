#!/usr/bin/env python3
"""
Reclassify Symposia and Chaired Sessions across all ISLS repository datasets:
- 2026 proceedings (ICLS, CSCL, ISLS) using TOC indices and chair markers.
- 2023-2025 proceedings using TOC section demarcation and chair markers.
- 2016-2022 registry entries.
Updates:
- data/derived/*-proceedings/*.json
- data/derived/ground_truth_registry.json
- proceedings.db (papers.paper_type)
- export/tableau/tableau_papers_master.csv
"""

import os
import re
import json
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED_DIR = os.path.join(BASE_DIR, "data", "derived")
REGISTRY_PATH = os.path.join(DERIVED_DIR, "ground_truth_registry.json")
DB_PATH = os.path.join(BASE_DIR, "proceedings.db")
TABLEAU_PATH = os.path.join(BASE_DIR, "export", "tableau", "tableau_papers_master.csv")

CHAIR_PATTERN = re.compile(
    r'\b(?:\(co-chair[s]?\)|\(chair[s]?\)|\(organizer[s]?\)|\(discussant[s]?\)|\(session chair\)|co-chair\b|session chair\b)',
    re.IGNORECASE
)

SYMPOSIUM_TEXT_PATTERN = re.compile(
    r'\b(?:in this symposium|this symposium brings together|structured poster symposium|this symposium proposes|this symposium addresses|in this structured poster session)\b',
    re.IGNORECASE
)

def is_symposium_or_chaired(paper: dict) -> bool:
    """Check if a paper record is a symposium or chaired session."""
    title = (paper.get("title") or "").strip()
    sec = (paper.get("proceedings_section") or "").strip()
    ptype = (paper.get("paper_type") or "").strip()
    abstract = (paper.get("abstract") or "").strip()

    if ptype.lower() in ['symposium', 'special session', 'workshop', 'keynote']:
        return True
    if sec.lower() in ['symposia', 'symposium', 'special session', 'special sessions', 'pre-conference workshops', 'workshops', 'keynotes']:
        return True

    # Check title
    if re.search(r'\b(?:symposium|symposia)\b', title, re.IGNORECASE):
        return True

    # Check authors
    authors_raw = paper.get("authors", [])
    for a in authors_raw:
        a_str = a.get("display_name", "") if isinstance(a, dict) else str(a)
        if CHAIR_PATTERN.search(a_str):
            return True

    # Check first section text if available
    secs = paper.get("sections", [])
    if secs:
        first_txt = secs[0].get("text", "")[:800]
        if CHAIR_PATTERN.search(first_txt):
            return True
        if SYMPOSIUM_TEXT_PATTERN.search(first_txt):
            return True

    # Check abstract
    if SYMPOSIUM_TEXT_PATTERN.search(abstract[:400]):
        return True

    return False

def reclassify_datasets():
    print("=== Reclassifying Symposia and Chaired Sessions ===")

    symposia_ids = set()

    # 1. Update data/derived/*-proceedings/*.json
    vol_dirs = sorted([d for d in os.listdir(DERIVED_DIR) if os.path.isdir(os.path.join(DERIVED_DIR, d)) and d.endswith("-proceedings")])
    for v in vol_dirs:
        jpath = os.path.join(DERIVED_DIR, v, f"{v}.json")
        if not os.path.exists(jpath):
            continue

        with open(jpath, "r", encoding="utf-8") as f:
            v_data = json.load(f)

        modified = False
        papers = v_data.get("papers", [])

        # Specific volume known ranges
        for p in papers:
            pid = p.get("id")
            title = p.get("title", "")
            orig_sec = p.get("proceedings_section") or ""
            orig_type = p.get("paper_type") or ""

            is_symp = is_symposium_or_chaired(p)

            # Specific range overrides based on verified TOC:
            # ICLS 2026: paper-0340 to paper-0363 are Symposia (pages 2243-2568)
            # ICLS 2026: paper-0364 to 0500 are Posters (pages 2569+)
            if v == "icls-2026-proceedings":
                m = re.search(r'paper-0?(\d+)', pid)
                if m:
                    num = int(m.group(1))
                    if 340 <= num <= 363:
                        is_symp = True
                        p["proceedings_section"] = "Symposia"
                        p["paper_type"] = "Symposium"
                        modified = True
                    elif num >= 364 and orig_sec != "Posters":
                        p["proceedings_section"] = "Posters"
                        p["paper_type"] = "Poster"
                        modified = True

            # CSCL 2026: paper-0090 to 0093 are Symposia
            elif v == "cscl-2026-proceedings":
                m = re.search(r'paper-0?(\d+)', pid)
                if m:
                    num = int(m.group(1))
                    if 90 <= num <= 93:
                        is_symp = True
                        p["proceedings_section"] = "Symposia"
                        p["paper_type"] = "Symposium"
                        modified = True

            # ICLS 2025: paper-0336 to 0364 are Symposia
            elif v == "icls-2025-proceedings":
                m = re.search(r'paper-0?(\d+)', pid)
                if m:
                    num = int(m.group(1))
                    if 336 <= num <= 364:
                        is_symp = True
                        p["proceedings_section"] = "Symposia"
                        p["paper_type"] = "Symposium"
                        modified = True

            # CSCL 2025: paper-073 to 080 are Symposia (Exploring GenAI Technologies, etc.)
            elif v == "cscl-2025-proceedings":
                m = re.search(r'paper-0?(\d+)', pid)
                if m:
                    num = int(m.group(1))
                    if 73 <= num <= 80:
                        is_symp = True
                        p["proceedings_section"] = "Symposia"
                        p["paper_type"] = "Symposium"
                        modified = True

            # ICLS 2024: paper-0349 to 0372 are Symposia (Co-Research in Video Analysis, etc.)
            elif v == "icls-2024-proceedings":
                m = re.search(r'paper-0?(\d+)', pid)
                if m:
                    num = int(m.group(1))
                    if 349 <= num <= 372:
                        is_symp = True
                        p["proceedings_section"] = "Symposia"
                        p["paper_type"] = "Symposium"
                        modified = True

            # ICLS 2023: paper-0270 to 0287 are Symposia
            elif v == "icls-2023-proceedings":
                m = re.search(r'paper-0?(\d+)', pid)
                if m:
                    num = int(m.group(1))
                    if 270 <= num <= 287:
                        is_symp = True
                        p["proceedings_section"] = "Symposia"
                        p["paper_type"] = "Symposium"
                        modified = True

            if is_symp:
                symposia_ids.add(pid)
                if p.get("proceedings_section") != "Symposia":
                    p["proceedings_section"] = "Symposia"
                    modified = True
                if p.get("paper_type") != "Symposium":
                    p["paper_type"] = "Symposium"
                    modified = True

        if modified:
            with open(jpath, "w", encoding="utf-8") as f:
                json.dump(v_data, f, indent=2)
            print(f"Updated {v}.json with verified section classifications.")

    print(f"Identified {len(symposia_ids)} distinct symposia / chaired sessions across 2023–2026.")

    # 2. Update ground_truth_registry.json
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry = json.load(f)

        reg_modified = 0
        for p in registry.get("papers", []):
            pid = p.get("id")
            title = p.get("title", "")
            curr_type = p.get("paper_type", "")

            # Check if identified above or matches symposium patterns
            is_symp = (pid in symposia_ids) or is_symposium_or_chaired(p)
            if is_symp:
                symposia_ids.add(pid)
                if curr_type != "Symposium":
                    p["paper_type"] = "Symposium"
                    reg_modified += 1

        if reg_modified > 0:
            with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
                json.dump(registry, f, indent=2)
            print(f"Updated {reg_modified} papers in {REGISTRY_PATH} to 'Symposium'.")

    # 3. Update SQLite proceedings.db
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Update papers matching symposia IDs or patterns
        db_updates = 0
        for pid in symposia_ids:
            c.execute("UPDATE papers SET paper_type = 'Symposium' WHERE id = ? AND paper_type != 'Symposium'", (pid,))
            db_updates += c.rowcount

        # Also search DB for any remaining papers with symposium/chair keywords
        c.execute("""
            SELECT id, title, abstract FROM papers 
            WHERE paper_type IN ('Full Paper', 'Short Paper', 'Paper')
              AND (title LIKE '%symposi%' 
                   OR abstract LIKE '%in this symposium%' 
                   OR abstract LIKE '%structured poster symposium%'
                   OR title LIKE '%special session%')
        """)
        for row in c.fetchall():
            c.execute("UPDATE papers SET paper_type = 'Symposium' WHERE id = ? AND paper_type != 'Symposium'", (row[0],))
            db_updates += c.rowcount
            symposia_ids.add(row[0])

        conn.commit()
        conn.close()
        print(f"Updated {db_updates} records in proceedings.db to 'Symposium'.")

    # 4. Update export/tableau/tableau_papers_master.csv
    if os.path.exists(TABLEAU_PATH):
        import csv
        rows = []
        tab_modified = 0
        with open(TABLEAU_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for r in reader:
                pid = r.get("id")
                if pid in symposia_ids or is_symposium_or_chaired(r):
                    if r.get("paper_type") != "Symposium":
                        r["paper_type"] = "Symposium"
                        tab_modified += 1
                rows.append(r)

        if tab_modified > 0:
            with open(TABLEAU_PATH, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            print(f"Updated {tab_modified} rows in {TABLEAU_PATH} to 'Symposium'.")

    print(f"=== Reclassification Complete: Total {len(symposia_ids)} Symposia/Chaired Sessions Marked ===")
    return symposia_ids

if __name__ == "__main__":
    reclassify_datasets()
