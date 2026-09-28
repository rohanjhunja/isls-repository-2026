#!/usr/bin/env python3
"""
Align database paper_type labels with DSpace across all years:
1. Retain DSpace 'Long Paper' as 'Full Paper'.
2. Normalize 'Poster / Short Note' -> 'Poster' across all years.
3. Align 2025 papers directly to DSpace DC.description metadata (recovering ~280 posters and 18 symposia).
4. Execute Option 1 for 2026 proceedings:
   - Purge the 97 ISLS General Volume papers from proceedings.db, ground_truth_registry.json, and isls-2026-proceedings.json.
   - Retain exactly 28 genuine symposia across CSCL (4) and ICLS (24).
   - Ensure total 2026 papers = 658 with valid DSpace labels ('Full Paper', 'Short Paper', 'Poster', 'Symposium').
5. Update export/tableau/tableau_papers_master.csv.
6. Update metadata in the 3 reviews:
   - rev_dipstick_eff7613c
   - rev_agentic_teacher_codesign
   - rev_agentic_teacher_codesign_tel
7. Rebuild all review viewer caches.
"""

import os
import sys
import re
import csv
import json
import sqlite3
import datetime
from concurrent.futures import ThreadPoolExecutor
from curl_cffi import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "proceedings.db")
REGISTRY_PATH = os.path.join(BASE_DIR, "data", "derived", "ground_truth_registry.json")
CACHE_2025_PATH = os.path.join(BASE_DIR, "data", "derived", "dspace_2025_meta_cache.json")
TABLEAU_PATH = os.path.join(BASE_DIR, "export", "tableau", "tableau_papers_master.csv")
ISLS_2026_PATH = os.path.join(BASE_DIR, "data", "derived", "isls-2026-proceedings", "isls-2026-proceedings.json")
CSCL_2026_PATH = os.path.join(BASE_DIR, "data", "derived", "cscl-2026-proceedings", "cscl-2026-proceedings.json")
ICLS_2026_PATH = os.path.join(BASE_DIR, "data", "derived", "icls-2026-proceedings", "icls-2026-proceedings.json")

def fetch_dspace_2025_metadata(conn):
    """Fetch or load cached DSpace DC.description for all 2025 papers."""
    if os.path.exists(CACHE_2025_PATH):
        print(f"Loading cached 2025 DSpace metadata from {CACHE_2025_PATH}...")
        with open(CACHE_2025_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    print("Fetching live DSpace Dublin Core metadata for all 2025 papers...")
    c = conn.cursor()
    c.execute("SELECT id, handle_url, start_page, end_page FROM papers WHERE year = 2025 AND handle_url IS NOT NULL")
    rows = c.fetchall()

    cache_data = {}
    def fetch_item(row):
        pid, hurl, sp, ep = row
        s = requests.Session(impersonate="chrome120")
        try:
            r = s.get(hurl, timeout=12)
            desc_matches = re.findall(r'<meta\s+name=\"DC\.description\"\s+content=\"([^\"]+)\"', r.text)
            return pid, desc_matches, None
        except Exception as e:
            return pid, [], str(e)

    with ThreadPoolExecutor(max_workers=15) as executor:
        for pid, desc_matches, err in executor.map(fetch_item, rows):
            cache_data[pid] = {
                "dc_description": desc_matches,
                "error": err
            }

    with open(CACHE_2025_PATH, "w", encoding="utf-8") as f:
        json.dump(cache_data, f, indent=2)
    print(f"Saved {len(cache_data)} items to {CACHE_2025_PATH}")
    return cache_data


def determine_2025_paper_type(pid, desc_list, sp, ep, title, citation):
    """Determine clean paper_type and practice flag from DSpace DC.description."""
    num_pages = (ep - sp + 1) if (sp is not None and ep is not None) else None
    is_practise = any("practice-oriented" in d.lower() for d in desc_list)

    # 1. Primary Dublin Core tag
    for d in desc_list:
        d_clean = d.strip()
        if d_clean == "Long Paper":
            return "Full Paper", is_practise
        elif d_clean == "Short Paper":
            return "Short Paper", is_practise
        elif d_clean == "Poster":
            return "Poster", is_practise
        elif d_clean == "Symposium":
            return "Symposium", is_practise

    # Specific fix for handle_1_11511
    if pid == "handle_1_11511":
        return "Poster", is_practise

    # Fallback if no tag
    txt = f"{title} {citation}".lower()
    if "symposium" in txt:
        return "Symposium", is_practise
    if "poster" in txt:
        return "Poster", is_practise
    if num_pages is not None:
        if num_pages >= 6:
            return "Full Paper", is_practise
        elif num_pages in [3, 4, 5]:
            return "Short Paper", is_practise
        elif num_pages in [1, 2]:
            return "Poster", is_practise

    return "Paper", is_practise


def align_database_and_registry():
    print("=== Aligning DSpace & 2026 Paper Types Across ISLS Repository ===")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. Fetch 2025 DSpace metadata
    dspace_2025_map = fetch_dspace_2025_metadata(conn)

    # 2. Update 2025 papers in DB
    print("Applying true DSpace labels to 2025 papers in proceedings.db...")
    c.execute("SELECT id, start_page, end_page, title, citation FROM papers WHERE year = 2025")
    rows_2025 = c.fetchall()
    updated_2025 = 0
    for pid, sp, ep, title, cit in rows_2025:
        item = dspace_2025_map.get(pid, {})
        desc_list = item.get("dc_description", [])
        ptype, is_practise = determine_2025_paper_type(pid, desc_list, sp, ep, title, cit or "")
        c.execute("UPDATE papers SET paper_type = ?, is_practise_paper = ? WHERE id = ?", (ptype, 1 if is_practise else 0, pid))
        updated_2025 += 1
    print(f"Updated {updated_2025} papers in 2025.")

    # 3. Normalize all 'Poster / Short Note' -> 'Poster' across ALL years
    print("Normalizing 'Poster / Short Note' -> 'Poster' across all years...")
    c.execute("UPDATE papers SET paper_type = 'Poster' WHERE paper_type = 'Poster / Short Note'")
    print(f"Normalized {c.rowcount} 'Poster / Short Note' records to 'Poster'.")

    # 4. Execute Option 1 for 2026: Purge 97 General Volume papers
    print("Purging 97 ISLS 2026 General Volume papers from proceedings.db...")
    c.execute("SELECT id FROM papers WHERE id LIKE 'general-volume-2026-%'")
    purged_ids = [r[0] for r in c.fetchall()]
    print(f"Found {len(purged_ids)} general volume papers to purge.")

    for pid in purged_ids:
        c.execute("DELETE FROM papers_fts WHERE paper_id = ?", (pid,))
        c.execute("DELETE FROM sections WHERE paper_id = ? OR id LIKE ?", (pid, f"{pid}-%"))
        c.execute("DELETE FROM paper_authors WHERE paper_id = ?", (pid,))
        c.execute("DELETE FROM papers WHERE id = ?", (pid,))

    # 5. Fix 2026 CSCL and ICLS papers
    print("Aligning 2026 CSCL and ICLS paper types in proceedings.db...")
    # CSCL 2026: 0090-0093 are Symposia; 0009 is Poster
    c.execute("""
        UPDATE papers SET paper_type = 'Symposium' 
        WHERE id IN (
            'cscl-volume-2026-paper-0090',
            'cscl-volume-2026-paper-0091',
            'cscl-volume-2026-paper-0092',
            'cscl-volume-2026-paper-0093'
        )
    """)
    c.execute("UPDATE papers SET paper_type = 'Poster' WHERE id = 'cscl-volume-2026-paper-0009'")
    
    # ICLS 2026: 0340-0363 are Symposia
    icls_symp_ids = [f"icls-volume-2026-paper-{i:04d}" for i in range(340, 364)]
    placeholders = ",".join(["?"] * len(icls_symp_ids))
    c.execute(f"UPDATE papers SET paper_type = 'Symposium' WHERE id IN ({placeholders})", icls_symp_ids)

    # Any other 2026 papers falsely marked as Symposium reset to length-based type
    c.execute("""
        SELECT id, start_page, end_page, title FROM papers 
        WHERE year = 2026 AND paper_type = 'Symposium'
    """)
    for pid, sp, ep, title in c.fetchall():
        if pid not in [
            'cscl-volume-2026-paper-0090', 'cscl-volume-2026-paper-0091',
            'cscl-volume-2026-paper-0092', 'cscl-volume-2026-paper-0093'
        ] and pid not in icls_symp_ids:
            num_pages = (ep - sp + 1) if (sp is not None and ep is not None) else None
            new_type = "Full Paper" if (num_pages and num_pages >= 6) else ("Short Paper" if (num_pages and num_pages >= 3) else "Poster")
            c.execute("UPDATE papers SET paper_type = ? WHERE id = ?", (new_type, pid))
            print(f"Reset non-symposium 2026 paper {pid} to {new_type}")

    conn.commit()

    # Rebuild papers_fts to match papers table
    print("Synchronizing papers_fts table...")
    from rebuild_fts_and_manifest import rebuild_fts
    rebuild_fts()
    print("papers_fts synchronized.")

    # 6. Update ground_truth_registry.json
    print("Updating ground_truth_registry.json...")
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)

    purged_set = set(purged_ids)
    kept_papers = []
    papers_by_year = {}

    for p in registry.get("papers", []):
        pid = p.get("id")
        year = p.get("year")
        if pid in purged_set or pid.startswith("general-volume-2026-"):
            continue

        # Look up true paper_type from DB
        c.execute("SELECT paper_type, is_practise_paper FROM papers WHERE id = ?", (pid,))
        row = c.fetchone()
        if row:
            p["paper_type"] = row[0]
            p["is_practise_paper"] = bool(row[1])
        elif p.get("paper_type") == "Poster / Short Note":
            p["paper_type"] = "Poster"

        kept_papers.append(p)
        papers_by_year[year] = papers_by_year.get(year, 0) + 1

    registry["papers"] = kept_papers
    registry["total_papers"] = len(kept_papers)
    registry["papers_by_year"] = dict(sorted(papers_by_year.items()))

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
    print(f"Updated ground_truth_registry.json: {len(kept_papers)} total papers.")

    # 7. Update 2026 JSON files
    if os.path.exists(ISLS_2026_PATH):
        # Backup original and set papers to empty (Option 1)
        backup_path = ISLS_2026_PATH.replace(".json", ".purged_backup.json")
        if not os.path.exists(backup_path):
            with open(ISLS_2026_PATH, "r", encoding="utf-8") as f:
                with open(backup_path, "w", encoding="utf-8") as bf:
                    bf.write(f.read())
        with open(ISLS_2026_PATH, "r", encoding="utf-8") as f:
            isls_data = json.load(f)
        isls_data["papers"] = []
        isls_data["purged_reason"] = "Option 1: ISLS General Volume omitted for strict DSpace parity with 2024-2025 standard."
        with open(ISLS_2026_PATH, "w", encoding="utf-8") as f:
            json.dump(isls_data, f, indent=2)
        print("Updated isls-2026-proceedings.json (purged 97 papers).")

    # 8. Update export/tableau/tableau_papers_master.csv
    print("Updating tableau_papers_master.csv...")
    if os.path.exists(TABLEAU_PATH):
        c.execute("""
            SELECT 
                p.id, p.title, p.year, p.conference, p.paper_type, p.doi, p.handle, p.handle_url,
                p.citation, p.start_page, p.end_page, 
                (p.end_page - p.start_page + 1) AS page_span,
                (SELECT COUNT(*) FROM paper_authors pa WHERE pa.paper_id = p.id) AS author_count,
                (SELECT a.display_name FROM paper_authors pa JOIN authors a ON pa.author_id = a.id WHERE pa.paper_id = p.id AND pa.author_order = 1) AS first_author,
                (SELECT GROUP_CONCAT(a.display_name, ', ') FROM paper_authors pa JOIN authors a ON pa.author_id = a.id WHERE pa.paper_id = p.id) AS authors,
                p.abstract
            FROM papers p
            ORDER BY p.year, p.id
        """)
        db_rows = c.fetchall()

        fieldnames = [
            "id", "title", "year", "conference", "paper_type", "doi", "handle", "handle_url",
            "citation", "start_page", "end_page", "page_span", "author_count", "first_author",
            "authors", "abstract"
        ]
        with open(TABLEAU_PATH, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in db_rows:
                writer.writerow({
                    "id": r[0], "title": r[1], "year": r[2], "conference": r[3], "paper_type": r[4],
                    "doi": r[5], "handle": r[6], "handle_url": r[7], "citation": r[8],
                    "start_page": r[9], "end_page": r[10], "page_span": r[11], "author_count": r[12],
                    "first_author": r[13], "authors": r[14], "abstract": r[15]
                })
        print(f"Updated {TABLEAU_PATH} ({len(db_rows)} rows).")

    conn.close()
    return purged_set


def update_target_reviews(purged_set):
    print("=== Updating Metadata in Requested Reviews ===")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    target_reviews = [
        "rev_dipstick_eff7613c",
        "rev_agentic_teacher_codesign",
        "rev_agentic_teacher_codesign_tel"
    ]

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    for rid in target_reviews:
        json_path = os.path.join(BASE_DIR, "workspace", "reviews", f"{rid}.json")
        md_path = os.path.join(BASE_DIR, "workspace", "reviews", f"{rid}.md")

        if not os.path.exists(json_path):
            print(f"Warning: {json_path} not found.")
            continue

        with open(json_path, "r", encoding="utf-8") as f:
            rdata = json.load(f)

        orig_papers = rdata.get("papers", [])
        orig_count = len(orig_papers)

        # Filter out purged papers
        kept_papers = []
        for p in orig_papers:
            pid = p.get("id")
            if pid in purged_set or pid.startswith("general-volume-2026-"):
                continue

            # Query fresh metadata from DB
            c.execute("""
                SELECT p.title, p.year, p.conference, p.paper_type, p.start_page, p.end_page,
                       COALESCE((
                           SELECT GROUP_CONCAT(a.display_name, ', ')
                           FROM paper_authors pa
                           JOIN authors a ON pa.author_id = a.id
                           WHERE pa.paper_id = p.id
                       ), '') AS authors_str
                FROM papers p WHERE p.id = ?
            """, (pid,))
            row = c.fetchone()
            if row:
                p["title"] = row[0]
                p["year"] = row[1]
                p["conference"] = row[2]
                if "paper_type" in p:
                    p["paper_type"] = row[3]
                if "authors" in p and isinstance(p["authors"], str):
                    p["authors"] = row[6]
                if "page_span" in p and row[4] is not None and row[5] is not None:
                    p["page_span"] = f"{row[4]}-{row[5]}"
                if "paper_length_type" in p:
                    p["paper_length_type"] = row[3]

            kept_papers.append(p)

        rdata["papers"] = kept_papers
        if "paper_ids" in rdata:
            rdata["paper_ids"] = [p["id"] for p in kept_papers]
        if "paper_count" in rdata:
            rdata["paper_count"] = len(kept_papers)
        if "matched_paper_count" in rdata:
            rdata["matched_paper_count"] = len(kept_papers)
        if "total_papers_scanned" in rdata:
            rdata["total_papers_scanned"] = 5305
        rdata["updated_at"] = now_iso

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(rdata, f, indent=2)

        print(f"Updated {rid}.json: papers reduced from {orig_count} to {len(kept_papers)}")

        # Also sync markdown table in .md file if present
        if os.path.exists(md_path):
            with open(md_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            # Update header counts in markdown
            md_content = re.sub(r'Total Papers:\s*\*\*\d+\*\*', f'Total Papers: **{len(kept_papers)}**', md_content)
            md_content = re.sub(r'Papers Matched:\s*\*\*\d+\*\*', f'Papers Matched: **{len(kept_papers)}**', md_content)
            md_content = re.sub(r'Total Scanned:\s*\*\*\d+\*\*', 'Total Scanned: **5,305**', md_content)

            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            print(f"Updated {rid}.md header counts.")

    conn.close()


def rebuild_caches():
    print("=== Rebuilding Review Viewer Caches ===")
    import subprocess
    cmd = [os.path.join(BASE_DIR, ".venv", "bin", "python3"), os.path.join(BASE_DIR, "scripts", "build_all_reviews_cache.py")]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print("Stderr:", res.stderr)


if __name__ == "__main__":
    purged = align_database_and_registry()
    update_target_reviews(purged)
    rebuild_caches()
    print("=== Alignment & Review Update Complete ===")
