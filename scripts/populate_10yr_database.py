#!/usr/bin/env python3
import os
import json
import sqlite3
import re
from proceedings_ingest.utils.text_cleanup import repair_title_and_authors, sanitize_title_string, sanitize_author_list
from proceedings_ingest.database import get_db_connection, insert_paper_record, DEFAULT_DB_PATH

REGISTRY_PATH = "data/derived/ground_truth_registry.json"

def populate_database():
    print("=== Phase 7: Populating SQLite Database for 10-Year Corpus (2016–2026) ===")

    if not os.path.exists(REGISTRY_PATH):
        print(f"Error: {REGISTRY_PATH} not found.")
        return

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry_data = json.load(f)

    papers = registry_data.get("papers", [])
    print(f"Loaded {len(papers)} total paper records from ground_truth_registry.json.")

    conn = get_db_connection(DEFAULT_DB_PATH)
    cursor = conn.cursor()

    # Clear existing tables
    print("Clearing existing SQLite tables...")
    cursor.execute("DELETE FROM paper_authors")
    cursor.execute("DELETE FROM sections")
    cursor.execute("DELETE FROM papers_fts")
    cursor.execute("DELETE FROM papers")
    cursor.execute("DELETE FROM authors")
    conn.commit()

    inserted_count = 0
    for idx, p in enumerate(papers):
        pid = p.get("id") or f"paper_{idx+1:05d}"
        raw_t = p.get("title", "")
        raw_authors = p.get("authors", [])

        if isinstance(raw_authors, list):
            auth_str = ", ".join([a.get("display_name") if isinstance(a, dict) else str(a) for a in raw_authors])
        else:
            auth_str = str(raw_authors or "")

        clean_t, clean_auth_str = repair_title_and_authors(raw_t, auth_str, p.get("abstract") or "")
        clean_authors_list = [a.strip() for a in clean_auth_str.split(",") if a.strip()]

        abstract = p.get("abstract") or ""
        if abstract:
            abstract = re.sub(r'(\w+)-\n\s*(\w+)', r'\1-\2', abstract)
            abstract = re.sub(r'[ \t]+', ' ', abstract).strip()

        sec_data = [
            {
                "id": f"{pid}-sec-01",
                "original_heading": "Abstract / Intro",
                "normalized_section": "introduction",
                "level": 1,
                "text": f"### Abstract\n{abstract}",
                "pdf_start_page": p.get("start_page"),
                "pdf_end_page": p.get("end_page"),
            }
        ]

        p_dict = {
            "id": pid,
            "handle": p.get("handle"),
            "handle_url": p.get("handle_url"),
            "doi": p.get("doi"),
            "title": clean_t,
            "year": p.get("year"),
            "conference": p.get("conference", "ISLS"),
            "paper_type": p.get("paper_type", "Paper"),
            "citation": p.get("citation"),
            "start_page": p.get("start_page"),
            "end_page": p.get("end_page"),
            "abstract": abstract,
            "boundary_confidence": 0.95,
            "filename": f"isls-{p.get('year')}-proceedings.pdf",
            "authors": clean_authors_list,
        }

        insert_paper_record(conn, p_dict, sec_data)
        inserted_count += 1

        if (inserted_count) % 500 == 0:
            print(f"Inserted {inserted_count}/{len(papers)} papers into proceedings.db...")

    conn.close()
    print(f"\nSuccessfully populated proceedings.db with {inserted_count} papers across 2016–2026!")

if __name__ == "__main__":
    populate_database()
