#!/usr/bin/env python3
"""
Sync Full Paper Sections from Existing Derived Markdown to SQLite proceedings.db
Avoids re-pulling or rewriting existing data.
Tracks provenance for all matched papers.
"""

import os
import re
import glob
import json
import sqlite3
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DERIVED_DIR = os.path.join(DATA_DIR, "derived")
DB_PATH = os.path.join(BASE_DIR, "proceedings.db")
MANIFEST_PATH = os.path.join(DERIVED_DIR, "paper_sources_manifest.json")


def norm(s: str) -> str:
    return re.sub(r'[^a-z0-9]', '', (s or '').lower())


def parse_markdown_paper(md_path: str):
    """Parses a markdown paper into title, authors, and canonical/heading sections."""
    with open(md_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    lines = content.split('\n')
    title = ''
    authors = ''
    sections = []
    current_sec = None

    for line in lines:
        if line.startswith('# ') and not title:
            title = line[2:].strip()
        elif line.startswith('**Authors:**') and not authors:
            authors = line.replace('**Authors:**', '').strip()
        elif line.startswith('## '):
            if current_sec:
                current_sec['text'] = '\n'.join(current_sec['lines']).strip()
                del current_sec['lines']
                if current_sec['text']:
                    sections.append(current_sec)
            heading = line[3:].strip()
            current_sec = {
                'original_heading': heading,
                'normalized_section': heading.lower(),
                'order_index': len(sections) + 1,
                'lines': []
            }
        elif current_sec is not None:
            current_sec['lines'].append(line)

    if current_sec:
        current_sec['text'] = '\n'.join(current_sec['lines']).strip()
        del current_sec['lines']
        if current_sec['text']:
            sections.append(current_sec)

    return title, authors, sections, content


def main():
    print("=== Step 1: Ingesting Existing Derived Markdown Papers into DB ===")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Load all papers from DB
    c.execute("SELECT id, title, year, conference, filename, full_text_status FROM papers")
    db_papers = [dict(r) for r in c.fetchall()]
    print(f"Total papers in proceedings.db: {len(db_papers)}")

    db_by_id = {p["id"]: p for p in db_papers}
    db_by_norm_title = {norm(p["title"]): p for p in db_papers if p.get("title")}

    # Scan all derived markdown files
    md_files = glob.glob(os.path.join(DERIVED_DIR, "*-proceedings", "papers", "*.md"))
    print(f"Found {len(md_files)} existing derived markdown paper files.")

    # Load existing manifest if present
    manifest = {}
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            manifest = {}

    updated_papers_count = 0
    inserted_sections_count = 0
    now = datetime.datetime.now().isoformat()

    for md_path in md_files:
        rel_md_path = os.path.relpath(md_path, BASE_DIR)
        fname = os.path.basename(md_path)

        parsed_title, parsed_authors, sections, raw_content = parse_markdown_paper(md_path)
        if not sections and not raw_content.strip():
            continue

        matched_paper = None
        # Try filename stem match (e.g. paper-0010)
        stem = os.path.splitext(fname)[0]
        for db_id, p in db_by_id.items():
            if stem in db_id or db_id in stem:
                matched_paper = p
                break

        # Fallback to normalized title match
        if not matched_paper and parsed_title:
            matched_paper = db_by_norm_title.get(norm(parsed_title))

        if not matched_paper:
            # Try fuzzy/substring match
            norm_p_title = norm(parsed_title)
            if len(norm_p_title) > 20:
                for n_title, p in db_by_norm_title.items():
                    if norm_p_title[:30] in n_title or n_title[:30] in norm_p_title:
                        matched_paper = p
                        break

        if matched_paper:
            pid = matched_paper["id"]
            yr = matched_paper.get("year")

            # If 2026 and already complete with real sections, only record provenance
            if yr == 2026 and matched_paper.get("full_text_status") == "complete":
                manifest[pid] = {
                    "id": pid,
                    "title": matched_paper["title"],
                    "year": yr,
                    "conference": matched_paper["conference"],
                    "source_type": "proceedings_volume_pdf",
                    "source_url": rel_md_path,
                    "full_text_status": "complete",
                    "sections_count": len(sections),
                    "total_chars": len(raw_content),
                    "extracted_at": matched_paper.get("extracted_at") or now
                }
                continue

            # Replace sections in DB with full sections from markdown
            c.execute("DELETE FROM sections WHERE paper_id = ?", (pid,))

            if sections:
                for s_idx, sec in enumerate(sections):
                    sec_id = f"{pid}-sec-{s_idx+1:02d}"
                    c.execute("""
                        INSERT INTO sections (id, paper_id, original_heading, normalized_section, level, order_index, text)
                        VALUES (?, ?, ?, ?, 1, ?, ?)
                    """, (sec_id, pid, sec["original_heading"], sec["normalized_section"], sec["order_index"], sec["text"]))
                    inserted_sections_count += 1
            else:
                sec_id = f"{pid}-sec-01"
                c.execute("""
                    INSERT INTO sections (id, paper_id, original_heading, normalized_section, level, order_index, text)
                    VALUES (?, ?, ?, ?, 1, 1, ?)
                """, (sec_id, pid, "Full Text", "full_text", raw_content))
                inserted_sections_count += 1

            # Update papers record with provenance
            c.execute("""
                UPDATE papers
                SET source_type = 'proceedings_volume_pdf',
                    source_url = ?,
                    full_text_status = 'complete',
                    extracted_at = ?
                WHERE id = ?
            """, (rel_md_path, now, pid))
            updated_papers_count += 1

            manifest[pid] = {
                "id": pid,
                "title": matched_paper["title"],
                "year": yr,
                "conference": matched_paper["conference"],
                "source_type": "proceedings_volume_pdf",
                "source_url": rel_md_path,
                "full_text_status": "complete",
                "sections_count": len(sections) or 1,
                "total_chars": len(raw_content),
                "extracted_at": now
            }

    conn.commit()
    conn.close()

    # Save manifest
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Sync complete! Updated {updated_papers_count} papers in DB with {inserted_sections_count} section records.")
    print(f"Provenance recorded in {MANIFEST_PATH} ({len(manifest)} entries).")


if __name__ == "__main__":
    main()
