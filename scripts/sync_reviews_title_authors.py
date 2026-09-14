#!/usr/bin/env python3
"""
Sync cleaned title and author metadata from proceedings.db into the 4 reviews:
1. rev_dipstick_299e430b ("Dipstick Review - Co-design 2")
2. rev_dipstick_36c55f1d ("Dipstick Review - participatory")
3. rev_dipstick_80cf3213 ("Dipstick Review - collaborative design")
4. rev_teachers_in_codesign ("Combined Review: Teachers in Co-Design & Participatory Design")

Updates:
- data/reviews/<review_id>.json
- data/derived/reviews_cache/<review_id>.json
- data/reviews/<review_id>.md
- data/derived/reviews_cache/manifest.json
"""

import os
import re
import json
import sqlite3
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "proceedings.db")
REVIEWS_DIR = os.path.join(BASE_DIR, "data", "reviews")
CACHE_DIR = os.path.join(BASE_DIR, "data", "derived", "reviews_cache")
MANIFEST_PATH = os.path.join(CACHE_DIR, "manifest.json")

REVIEW_SPECS = [
    {
        "id": "rev_dipstick_299e430b",
        "keywords": ["Co-design"],
        "header": "Papers and Design Process Stakeholders (Full Text Scope)",
        "cols": ["title", "year", "conference", "authors", "design_stakeholders", "abstract"]
    },
    {
        "id": "rev_dipstick_36c55f1d",
        "keywords": ["participatory"],
        "header": "Papers and Design Process Stakeholders (Full Text Scope)",
        "cols": ["title", "year", "conference", "authors", "design_stakeholders", "abstract"]
    },
    {
        "id": "rev_dipstick_80cf3213",
        "keywords": ["collaborative design"],
        "header": "Papers and Design Process Stakeholders (Full Text Scope)",
        "cols": ["title", "year", "conference", "authors", "design_stakeholders", "abstract"]
    },
    {
        "id": "rev_teachers_in_codesign",
        "keywords": ["co-design", "participatory", "collaborative design", "teacher involvement"],
        "header": "Papers with Teacher Involvement in Co-Design & Participatory Design (10-Year Full Text Scope)",
        "cols": ["title", "year", "conference", "authors", "matched_design_keywords", "design_stakeholders", "teacher_involvement", "abstract"]
    }
]

def clean_spacing(s: str) -> str:
    if not s:
        return ""
    return re.sub(r'\s+', ' ', str(s)).strip()

def sync_reviews():
    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Pre-fetch all paper titles and clean spacing
    print("Pre-fetching paper titles from proceedings.db...")
    raw_titles = c.execute("SELECT id, title FROM papers").fetchall()
    db_titles = {pid: clean_spacing(t) for pid, t in raw_titles}

    # Pre-fetch ordered author strings
    print("Pre-fetching canonical author lists from paper_authors & authors...")
    author_rows = c.execute("""
        SELECT pa.paper_id, a.display_name
        FROM paper_authors pa
        JOIN authors a ON pa.author_id = a.id
        ORDER BY pa.paper_id, pa.author_order ASC
    """).fetchall()

    db_authors_list = {}
    for pid, dname in author_rows:
        clean_name = clean_spacing(dname)
        if clean_name:
            if pid not in db_authors_list:
                db_authors_list[pid] = []
            db_authors_list[pid].append(clean_name)

    db_authors = {pid: ", ".join(names) for pid, names in db_authors_list.items()}
    conn.close()

    now_iso = datetime.datetime.now().isoformat()
    total_titles_updated = 0
    total_authors_updated = 0

    for spec in REVIEW_SPECS:
        rev_id = spec["id"]
        review_json_path = os.path.join(REVIEWS_DIR, f"{rev_id}.json")
        cache_json_path = os.path.join(CACHE_DIR, f"{rev_id}.json")
        review_md_path = os.path.join(REVIEWS_DIR, f"{rev_id}.md")

        if not os.path.exists(review_json_path):
            print(f"Warning: Review JSON not found: {review_json_path}")
            continue

        with open(review_json_path, "r", encoding="utf-8") as f:
            rev_data = json.load(f)

        papers = rev_data.get("papers", [])
        title_changes = 0
        author_changes = 0

        for p in papers:
            pid = p.get("id")
            if not pid:
                continue

            # Check and update title
            if pid in db_titles:
                new_title = db_titles[pid]
                old_title = p.get("title", "")
                if old_title != new_title:
                    p["title"] = new_title
                    title_changes += 1

            # Check and update authors
            if pid in db_authors:
                new_authors = db_authors[pid]
                old_authors = p.get("authors", "")
                if old_authors != new_authors:
                    p["authors"] = new_authors
                    author_changes += 1

        rev_data["updated_at"] = now_iso
        total_titles_updated += title_changes
        total_authors_updated += author_changes
        print(f"[{rev_id}] Updated {title_changes} titles and {author_changes} authors.")

        # Save to data/reviews/<rev_id>.json
        with open(review_json_path, "w", encoding="utf-8") as f:
            json.dump(rev_data, f, indent=2)

        # Save to data/derived/reviews_cache/<rev_id>.json
        with open(cache_json_path, "w", encoding="utf-8") as f:
            json.dump(rev_data, f, indent=2)

        # Generate Markdown Table
        selected_cols = spec["cols"]
        col_defs = rev_data.get("column_definitions", {})
        kw_list = spec["keywords"]
        title_header = spec["header"]

        custom_cols = [c for c in selected_cols if c not in ["id", "title", "authors", "year", "conference", "abstract"]]
        custom_header_labels = [col_defs.get(c, {}).get("label", c) for c in custom_cols]

        md_header_parts = ["Paper ID", "Title", "Authors", "Year", "Conference"] + custom_header_labels
        md_sep_parts = ["---"] * len(md_header_parts)

        md_content = f"""# Literature Review: {rev_data.get('name')}

- **Review ID**: `{rev_id}`
- **Created At**: `{rev_data.get('created_at')}`
- **Updated At**: `{now_iso}`
- **Matching Papers**: {len(papers)} (scanned 5,402 papers across 10-year proceedings)
- **Scope Fields**: title, abstract, sections (abstract, method, discussion)
- **Selected Columns**: {', '.join(selected_cols)}
- **Keywords**: {', '.join(kw_list)}

## Web Viewer Launch Link

[🚀 Launch Interactive Web Viewer for this Review](http://localhost:8888/?review={rev_id})

## {title_header}

| {' | '.join(md_header_parts)} |
| {' | '.join(md_sep_parts)} |
"""
        for p in papers:
            clean_t = str(p.get('title', '')).replace('|', '\\|').replace('\n', ' ')
            clean_a = str(p.get('authors', '')).replace('|', '\\|').replace('\n', ' ')
            row_parts = [
                f"`{p['id']}`",
                clean_t,
                clean_a,
                str(p.get('year', '')),
                str(p.get('conference', ''))
            ]
            for c_name in custom_cols:
                val = str(p.get(c_name, '')).replace('|', '\\|').replace('\n', ' ')
                row_parts.append(val)

            md_content += f"| {' | '.join(row_parts)} |\n"

        with open(review_md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        print(f"[{rev_id}] Successfully wrote updated Markdown file.")

    # Update manifest.json
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        rev_id_set = {s["id"] for s in REVIEW_SPECS}
        for entry in manifest:
            if entry.get("id") in rev_id_set:
                entry["updated_at"] = now_iso

        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"Updated {MANIFEST_PATH} with timestamp {now_iso}.")

    print(f"\nCompleted! Total titles updated: {total_titles_updated}, Total authors updated: {total_authors_updated}.")

if __name__ == "__main__":
    sync_reviews()
