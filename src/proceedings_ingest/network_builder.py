#!/usr/bin/env python3
"""Builds author collaboration network and cross-citation links across 2016-2026."""

import os
import re
import glob
import sqlite3
from collections import defaultdict

DB_PATH = "proceedings.db"

def build_author_collaborations(db_path: str = DB_PATH):
    print("Building author collaboration edges...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("DELETE FROM author_collaborations;")

    cur.execute("""
        SELECT 
            pa1.author_id AS a1_id,
            pa2.author_id AS a2_id,
            a1.display_name AS a1_name,
            a2.display_name AS a2_name,
            p.year,
            p.id AS paper_id,
            1.0 AS weight
        FROM paper_authors pa1
        JOIN paper_authors pa2 ON pa1.paper_id = pa2.paper_id AND pa1.author_id < pa2.author_id
        JOIN authors a1 ON pa1.author_id = a1.id
        JOIN authors a2 ON pa2.author_id = a2.id
        JOIN papers p ON pa1.paper_id = p.id;
    """)

    collab_rows = cur.fetchall()
    print(f"Discovered {len(collab_rows)} co-authorship instances across 2016-2026.")

    cur.executemany("""
        INSERT OR REPLACE INTO author_collaborations (
            author_1_id, author_2_id, author_1_name, author_2_name, year, paper_id, weight
        ) VALUES (?, ?, ?, ?, ?, ?, ?);
    """, collab_rows)

    conn.commit()
    conn.close()
    print("Successfully populated author_collaborations table.")

def build_citation_links(db_path: str = DB_PATH):
    print("Building cross-citation links across proceedings...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("DELETE FROM paper_citations;")

    # 1. Fetch all candidate target papers
    cur.execute("SELECT id, year, title FROM papers WHERE year IS NOT NULL;")
    all_papers = cur.fetchall()

    # Index target papers by significant title words
    target_lookup = []
    for pid, yr, title in all_papers:
        clean_t = re.sub(r'[^a-zA-Z0-9 ]', '', title).lower().strip()
        words = [w for w in clean_t.split() if len(w) > 4]
        if len(words) >= 3:
            target_lookup.append((pid, yr, title, set(words[:6])))

    print(f"Indexed {len(target_lookup)} target papers for cross-reference matching.")

    md_files = glob.glob("proceedings_md/*.md")
    print(f"Scanning {len(md_files)} proceedings markdown files...")

    citation_rows = []
    seen_pairs = set()

    for fpath in md_files:
        fname = os.path.basename(fpath)
        # Infer citing year from filename e.g. cscl-2024.md -> 2024
        yr_m = re.search(r"\b(20[12][0-9])\b", fname)
        citing_year = int(yr_m.group(1)) if yr_m else 2024

        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        current_citing_paper_id = f"proc_{fname.replace('.md', '')}"
        in_ref = False

        for idx, line in enumerate(lines):
            l_strip = line.strip()
            # Detect paper title headers in markdown
            if l_strip.startswith("# ") and len(l_strip) > 10 and not l_strip.lower().startswith("# references"):
                current_citing_paper_id = f"proc_{fname}_{idx}"

            if l_strip.lower() == "references" or l_strip.lower().startswith("## references"):
                in_ref = True
                continue

            if in_ref:
                # End of reference section
                if l_strip.startswith("# ") or (l_strip.startswith("## ") and "references" not in l_strip.lower()):
                    in_ref = False
                    continue

                if len(l_strip) < 20:
                    continue

                # Check if citation mentions ISLS / ICLS / CSCL
                l_lower = l_strip.lower()
                if any(sig in l_lower for sig in ["icls", "cscl", "isls", "learning sciences", "proceedings of"]):
                    l_words = set(re.sub(r'[^a-zA-Z0-9 ]', '', l_lower).split())
                    for cited_id, cited_yr, cited_title, p_words in target_lookup:
                        if cited_yr <= citing_year:
                            if len(p_words.intersection(l_words)) >= 3:
                                pair = (current_citing_paper_id, cited_id)
                                if pair not in seen_pairs:
                                    seen_pairs.add(pair)
                                    snippet = l_strip[:150]
                                    citation_rows.append((
                                        current_citing_paper_id, cited_id, citing_year, cited_yr,
                                        snippet, "extracted_from_md_references",
                                        "Extracted via 0-cost reference block parsing from proceedings markdown; 2016-2022 proceedings reference extraction can be generated via Tier 3 PDF reference parsing."
                                    ))
                                break

    print(f"Extracted {len(citation_rows)} cross-citation connections across proceedings.")

    cur.executemany("""
        INSERT OR REPLACE INTO paper_citations (
            citing_paper_id, cited_paper_id, citing_year, cited_year, context_snippet, status, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?);
    """, citation_rows)

    conn.commit()
    conn.close()
    print("Successfully populated paper_citations table.")

if __name__ == "__main__":
    build_author_collaborations()
    build_citation_links()
