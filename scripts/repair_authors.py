#!/usr/bin/env python3
"""Repairs author names in authors, paper_authors, and author_collaborations in proceedings.db."""

import json
import sqlite3
import re
from proceedings_ingest.network_builder import build_author_collaborations

DB_PATH = "proceedings.db"
REGISTRY_PATH = "data/derived/ground_truth_registry.json"

def normalize_author_name(name_str: str) -> str:
    if not name_str:
        return ""
    name_str = name_str.strip()
    # If formatted as "Lastname, Firstname" or "Lastname, Firstname Middle"
    if "," in name_str:
        parts = [p.strip() for p in name_str.split(",", 1)]
        if len(parts) == 2 and parts[0] and parts[1]:
            return f"{parts[1]} {parts[0]}"
    return name_str

def repair_authors():
    print(f"Reading {REGISTRY_PATH}...")
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry_data = json.load(f)

    papers = registry_data.get("papers", [])
    print(f"Loaded {len(papers)} papers.")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("Clearing authors and paper_authors...")
    cur.execute("DELETE FROM paper_authors;")
    cur.execute("DELETE FROM authors;")

    author_cache = {}  # name -> author_id

    def get_or_create_author(name: str) -> int:
        if name in author_cache:
            return author_cache[name]
        cur.execute("INSERT OR IGNORE INTO authors (display_name) VALUES (?);", (name,))
        cur.execute("SELECT id FROM authors WHERE display_name = ?;", (name,))
        row = cur.fetchone()
        a_id = row[0]
        author_cache[name] = a_id
        return a_id

    paper_authors_rows = []
    for p in papers:
        pid = p.get("id")
        if not pid:
            continue
        raw_authors = p.get("authors", [])
        if not raw_authors:
            continue

        seen_on_paper = set()
        for order, raw_a in enumerate(raw_authors):
            if isinstance(raw_a, dict):
                raw_a = raw_a.get("display_name", "")
            norm_a = normalize_author_name(str(raw_a))
            if not norm_a or norm_a in seen_on_paper:
                continue
            seen_on_paper.add(norm_a)

            a_id = get_or_create_author(norm_a)
            paper_authors_rows.append((pid, a_id, order))

    print(f"Inserting {len(author_cache)} unique scholars and {len(paper_authors_rows)} paper_author relationships...")
    cur.executemany("""
        INSERT OR REPLACE INTO paper_authors (paper_id, author_id, author_order)
        VALUES (?, ?, ?);
    """, paper_authors_rows)

    conn.commit()
    conn.close()
    print("Authors and paper_authors successfully repaired!")

    # Now rebuild author collaborations table
    build_author_collaborations(DB_PATH)
    print("Author collaborations successfully rebuilt!")

if __name__ == "__main__":
    repair_authors()
