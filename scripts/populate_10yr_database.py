#!/usr/bin/env python3
import os
import sys
import json
import sqlite3
import re
import time
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from proceedings_ingest.utils.text_cleanup import repair_title_and_authors
from proceedings_ingest.database import get_db_connection, init_database, DEFAULT_DB_PATH

REGISTRY_PATH = "data/derived/ground_truth_registry.json"
MD_DIR = "data/derived/papers"

HEADING_PATTERNS = [
    ("references", re.compile(r"\b(?:references|bibliography|works cited|literature cited|acknowledgments|acknowledgements|appendi[cx]|endnotes)\b", re.IGNORECASE)),
    ("conclusion", re.compile(r"\b(?:(?:general\s+)?discussion(?:s)?|concluding remarks|summary and conclusions?|conclusions?(?:\s+and\s+implications?)?|limitations(?:\s+and\s+future\s+work)?|implications?(?:\s+for\s+practice|\s+for\s+cscl|\s+for\s+research)?|significance(?:\s+of\s+the\s+symposium)?|educational\s+significance)\b", re.IGNORECASE)),
    ("results", re.compile(r"\b(?:(?:empirical\s+)?results?|(?:key\s+)?findings?|case study(?:\s*[:\-])?|empirical analysis|data analysis|qualitative analysis|quantitative analysis)\b", re.IGNORECASE)),
    ("methodology", re.compile(r"\b(?:method(?:s|ology)?|study design|research design|procedure|participants?(?:\s+and\s+setting)?|context(?:\s+and\s+setting)?|study context|data collection|pedagogical design|measures|analytic approach)\b", re.IGNORECASE)),
    ("theoretical_background", re.compile(r"\b(?:theoretical framework|conceptual framework|literature review|theoretical background|related work|prior work|perspectives)\b", re.IGNORECASE)),
    ("introduction", re.compile(r"^(?:abstract|introduction|background|problem statement|motivation|overview|research questions?)\b", re.IGNORECASE)),
]


def normalize_heading(heading: str) -> str:
    h = heading.strip()
    for norm_name, pattern in HEADING_PATTERNS:
        if pattern.search(h):
            return norm_name
    return re.sub(r"[^a-z0-9_]+", "_", h.lower()).strip("_") or "section"


def parse_markdown_sections(md_path: str, pid: str) -> List[Dict[str, Any]]:
    with open(md_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    sections = []
    parts = re.split(r'\n(?=##\s+)', content)
    order = 1
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part.startswith("## "):
            lines = part.split("\n", 1)
            heading = lines[0][3:].strip()
            body = lines[1].strip() if len(lines) > 1 else ""
            if body:
                norm_sec = normalize_heading(heading)
                sections.append({
                    "id": f"{pid}-sec-{order:02d}",
                    "original_heading": heading,
                    "normalized_section": norm_sec,
                    "level": 1,
                    "order_index": order,
                    "text": body,
                })
                order += 1
    return sections


def populate_database():
    start_time = time.time()
    print("=== Populating SQLite Database for 10-Year Full-Text Corpus (2016–2026) ===")

    if not os.path.exists(REGISTRY_PATH):
        print(f"Error: {REGISTRY_PATH} not found.")
        return

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry_data = json.load(f)

    papers = registry_data.get("papers", [])
    print(f"Loaded {len(papers)} total paper records from {REGISTRY_PATH}.")

    # Ensure schema exists
    init_database(DEFAULT_DB_PATH)

    conn = get_db_connection(DEFAULT_DB_PATH)
    cursor = conn.cursor()

    # Speed up bulk inserts with optimal PRAGMAs
    cursor.execute("PRAGMA foreign_keys = OFF;")
    cursor.execute("PRAGMA synchronous = OFF;")
    cursor.execute("PRAGMA journal_mode = MEMORY;")
    cursor.execute("PRAGMA cache_size = 20000;")

    # Clear existing tables
    print("Clearing existing SQLite tables...")
    cursor.execute("DELETE FROM paper_authors")
    cursor.execute("DELETE FROM sections")
    cursor.execute("DELETE FROM papers_fts")
    cursor.execute("DELETE FROM papers")
    cursor.execute("DELETE FROM authors")
    conn.commit()

    inserted_papers = 0
    inserted_sections = 0

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

        # Check if derived markdown full text file exists
        md_path = os.path.join(MD_DIR, f"{pid}.md")
        sec_data = []
        if os.path.exists(md_path):
            sec_data = parse_markdown_sections(md_path, pid)

        if not sec_data:
            sec_data = [
                {
                    "id": f"{pid}-sec-01",
                    "original_heading": "Abstract / Intro",
                    "normalized_section": "introduction",
                    "level": 1,
                    "order_index": 1,
                    "text": f"### Abstract\n{abstract}",
                    "pdf_start_page": p.get("start_page"),
                    "pdf_end_page": p.get("end_page"),
                }
            ]

        # Insert Paper
        cursor.execute("""
            INSERT OR REPLACE INTO papers (
                id, handle, handle_url, doi, title, year, conference, paper_type, is_practise_paper,
                citation, start_page, end_page, abstract, boundary_confidence, filename
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pid,
            p.get("handle"),
            p.get("handle_url"),
            p.get("doi"),
            clean_t,
            p.get("year"),
            p.get("conference", "ISLS"),
            p.get("paper_type", "Paper"),
            1 if p.get("is_practise_paper") else 0,
            p.get("citation"),
            p.get("start_page"),
            p.get("end_page"),
            abstract,
            0.95,
            f"isls-{p.get('year')}-proceedings.pdf",
        ))

        # Insert Authors & Paper_Authors
        author_text_list = []
        for a_idx, a_name in enumerate(clean_authors_list):
            if not a_name:
                continue
            cursor.execute("INSERT OR IGNORE INTO authors (display_name) VALUES (?)", (a_name,))
            cursor.execute("SELECT id FROM authors WHERE display_name = ?", (a_name,))
            a_row = cursor.fetchone()
            if a_row:
                cursor.execute(
                    "INSERT OR REPLACE INTO paper_authors (paper_id, author_id, author_order) VALUES (?, ?, ?)",
                    (pid, a_row[0], a_idx + 1),
                )
            author_text_list.append(a_name)

        authors_str = ", ".join(author_text_list)

        # Insert Sections & FTS5 entries
        for s in sec_data:
            cursor.execute("""
                INSERT OR REPLACE INTO sections (
                    id, paper_id, original_heading, normalized_section, level, order_index, text, pdf_start_page, pdf_end_page
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                s["id"],
                pid,
                s["original_heading"],
                s["normalized_section"],
                s.get("level", 1),
                s.get("order_index", 1),
                s["text"],
                s.get("pdf_start_page"),
                s.get("pdf_end_page"),
            ))

            cursor.execute("""
                INSERT INTO papers_fts (paper_id, title, abstract, authors_text, section_title, body_text, normalized_section)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                pid,
                clean_t,
                abstract,
                authors_str,
                s["original_heading"],
                s["text"],
                s["normalized_section"],
            ))
            inserted_sections += 1

        inserted_papers += 1
        if inserted_papers % 500 == 0:
            conn.commit()
            print(f"  Indexed {inserted_papers}/{len(papers)} papers ({inserted_sections} sections)...")

    # Final commit and restore safe pragma
    conn.commit()
    cursor.execute("PRAGMA synchronous = NORMAL;")
    cursor.execute("PRAGMA journal_mode = WAL;")
    conn.commit()
    conn.close()

    elapsed = time.time() - start_time
    print(f"\nSUCCESS: Populated proceedings.db in {elapsed:.2f}s!")
    print(f"  Total Papers: {inserted_papers}")
    print(f"  Total Sections: {inserted_sections}")


if __name__ == "__main__":
    populate_database()
