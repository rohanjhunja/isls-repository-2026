#!/usr/bin/env python3
"""
Repair 2026 Proceedings: Clean Leaked Titles and Re-assign Authors.

Fixes the issue where multi-line author overflow from the preceding paper
in the 2026 Table of Contents leaked into the title of the next paper.
Synchronizes proceedings.db, data/derived/papers/*.md, ground_truth_registry.json,
paper_sources_manifest.json, tableau_papers_master.csv, and literature review files.
"""

import os
import re
import csv
import json
import sqlite3
from typing import Dict, List, Tuple, Any, Optional

from proceedings_ingest.utils.text_cleanup import (
    sanitize_title_string,
    sanitize_author_list
)

DB_PATH = "proceedings.db"
REGISTRY_PATH = "data/derived/ground_truth_registry.json"
MANIFEST_PATH = "data/derived/paper_sources_manifest.json"
TABLEAU_PATH = "export/tableau/tableau_papers_master.csv"
REVIEWS_DIR = "data/reviews"
CACHE_DIR = "data/derived/reviews_cache"
DERIVED_PAPERS_DIR = "data/derived/papers"

VOL_MD = {
    "CSCL": "proceedings_md/cscl-2026.md",
    "ICLS": "proceedings_md/icls-2026.md",
    "ISLS": "proceedings_md/isls-2026.md"
}

INST_PATTERN = re.compile(
    r'\b(University|College|Institute|School|Department|Center|Corporation|Ltd|LLC|Inc|Foundation|Lab|Academy)\b',
    re.IGNORECASE
)


def get_canonical_page_title(md_text: str, pdf_page: int) -> str:
    """Extract canonical paper title from top of its PDF start page in markdown."""
    m = re.search(rf'<!-- page: pdf={pdf_page} .*?-->(.*?)(?:<!-- page:|$)', md_text, re.DOTALL)
    if not m:
        return ""
    lines = [l.strip() for l in m.group(1).strip().split('\n') if l.strip()]
    if not lines:
        return ""
    start_i = 1 if lines[0] in [
        'Keynotes', 'Special Session', 'Long Papers', 'Short Papers',
        'Posters', 'Symposia', 'Pre-Conference Workshops'
    ] else 0

    t_lines = []
    mode = 'title'
    for i in range(start_i, min(len(lines), start_i + 15)):
        l = lines[i]
        if l.startswith('Abstract:') or l.startswith('Abstract :') or l.startswith('Overview') or l.startswith('Introduction'):
            break
        if mode == 'title':
            if '@' in l or INST_PATTERN.search(l):
                if t_lines and (',' in t_lines[-1] or '&' in t_lines[-1]):
                    t_lines.pop()
                break
            elif ',' in l and any(w[0].isupper() for w in l.split()):
                if i + 1 < len(lines) and ('@' in lines[i + 1] or INST_PATTERN.search(lines[i + 1])):
                    break
                else:
                    t_lines.append(l)
            else:
                t_lines.append(l)
        else:
            break

    raw_t = ' '.join(t_lines)
    # Check if raw_t has curly quotes
    has_curly_open = raw_t.startswith('“')
    clean = sanitize_title_string(raw_t)
    if has_curly_open and not clean.startswith('“'):
        clean = f'“{clean}'
    return clean


def get_predecessor_id(pid: str) -> Optional[str]:
    """Calculate the true predecessor ID based on numeric sequence paper-(N-1)."""
    m = re.match(r'^(.*?-)(\d+)$', pid)
    if not m:
        return None
    prefix = m.group(1)
    num = int(m.group(2))
    pad = len(m.group(2))
    if num <= 1:
        return None
    return f"{prefix}{num - 1:0{pad}d}"


def extract_authors_from_page_header(md_text: str, pdf_page: int) -> List[str]:
    """Extract full author names from the paper's first page before Abstract."""
    m = re.search(rf'<!-- page: pdf={pdf_page} .*?-->(.*?)(?:<!-- page:|$)', md_text, re.DOTALL)
    if not m:
        return []
    lines = [l.strip() for l in m.group(1).strip().split('\n') if l.strip()]
    if not lines:
        return []

    # Find where title ends and authors begin, up to Abstract/Overview
    author_lines = []
    found_authors = False
    for i in range(len(lines[:25])):
        l = lines[i]
        if l.startswith('Abstract:') or l.startswith('Abstract :') or l.startswith('Overview') or l.startswith('Introduction'):
            break
        if '@' in l or INST_PATTERN.search(l):
            found_authors = True
            # The line itself might have author names before comma/institution
            # Or the previous line had author names
            continue
        if ',' in l and any(w[0].isupper() for w in l.split()):
            # If line is followed by email/affiliation, it's author line
            if i + 1 < len(lines) and ('@' in lines[i + 1] or INST_PATTERN.search(lines[i + 1])):
                found_authors = True
                author_lines.append(l)
            elif found_authors:
                author_lines.append(l)
        elif found_authors and any(w[0].isupper() for w in l.split() if w.isalpha()):
            # Author name line without comma (single author)
            if not ('@' in l or INST_PATTERN.search(l)):
                author_lines.append(l)

    extracted = []
    for al in author_lines:
        # Strip roles like (Co-chair), (Discussant), (Organizer), etc.
        clean_al = re.sub(r'\(.*?\)', '', al).strip()
        names = sanitize_author_list(clean_al)
        for n in names:
            n_clean = n.strip()
            # Filter out non-names
            if n_clean and len(n_clean) > 2 and not ('@' in n_clean or INST_PATTERN.search(n_clean)):
                if n_clean not in extracted:
                    extracted.append(n_clean)
    return extracted


def identify_repairs(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """Scan all 2026 papers and detect dirty titles and their preceding papers."""
    c = conn.cursor()
    md_texts = {}
    for conf, path in VOL_MD.items():
        with open(path, "r", encoding="utf-8") as f:
            md_texts[conf] = f.read()

    repairs = []
    for conf in ['CSCL', 'ICLS', 'ISLS']:
        c.execute(
            'SELECT id, title, start_page, end_page FROM papers WHERE year=2026 AND conference=? ORDER BY id',
            (conf,)
        )
        papers = c.fetchall()

        for pid, db_title, sp, ep in papers:
            pt = get_canonical_page_title(md_texts[conf], sp)
            if not pt:
                continue

            # Check if db_title contains pt as suffix
            clean_db = re.sub(r'^[“\"\']|[”\"\']$', '', db_title.strip())
            clean_pt = re.sub(r'^[“\"\']|[”\"\']$', '', pt.strip())

            match_pos = -1
            if clean_pt and clean_pt in clean_db:
                match_pos = clean_db.find(clean_pt)
            else:
                pt_words = clean_pt.split()
                if len(pt_words) >= 3:
                    probe = ' '.join(pt_words[:3])
                    if probe.lower() in clean_db.lower():
                        match_pos = clean_db.lower().find(probe.lower())

            if match_pos > 0:
                potential_leaked = clean_db[:match_pos].strip()
                repaired_t = clean_db[match_pos:].strip()
                if db_title.strip().startswith('“') or db_title.strip().startswith('"'):
                    if not (repaired_t.startswith('“') or repaired_t.startswith('"')):
                        repaired_t = f'“{repaired_t}'

                prev_pid = get_predecessor_id(pid)
                # Verify prev_pid exists in DB
                if prev_pid:
                    c.execute('SELECT count(*) FROM papers WHERE id=?', (prev_pid,))
                    if c.fetchone()[0] == 0:
                        prev_pid = None

                repairs.append({
                    'paper_id': pid,
                    'conference': conf,
                    'start_page': sp,
                    'dirty_title': db_title,
                    'clean_title': repaired_t,
                    'leaked_prefix': potential_leaked,
                    'prev_paper_id': prev_pid
                })

    return repairs


def heal_and_reassign_authors(
    conn: sqlite3.Connection,
    prev_pid: str,
    leaked_prefix: str,
    conf: str,
    md_text: str
) -> Tuple[List[str], str]:
    """
    Heal split names and assign missing authors to preceding paper.
    Uses both page header ground truth and sanitized leaked tokens.
    """
    c = conn.cursor()

    # Get current authors in DB for prev_pid
    c.execute(
        '''SELECT pa.author_order, a.id, a.display_name
           FROM paper_authors pa
           JOIN authors a ON pa.author_id = a.id
           WHERE pa.paper_id = ?
           ORDER BY pa.author_order''',
        (prev_pid,)
    )
    current_authors = c.fetchall()
    c.execute('SELECT start_page, title, year FROM papers WHERE id=?', (prev_pid,))
    p_row = c.fetchone()
    prev_sp, prev_title, prev_year = p_row[0], p_row[1], p_row[2]

    # Clean leaked prefix
    clean_leaked = re.sub(
        r'^(Community Workshops|Early Career Workshops|Keynotes|Interactive Tools and Demos)\b',
        '',
        leaked_prefix,
        flags=re.IGNORECASE
    ).strip()
    clean_leaked = re.sub(r'^[“\"\']|[”\"\']$', '', clean_leaked).strip()

    # Extract ground truth authors from preceding paper's start page
    page_authors = extract_authors_from_page_header(md_text, prev_sp)

    # Reconstruct final author list:
    final_authors: List[str] = []

    # 1. If page_authors has a full list, use it as baseline
    if page_authors and len(page_authors) >= len(current_authors):
        final_authors = list(page_authors)
    else:
        # Start from current DB authors
        final_authors = [a[2] for a in current_authors]

    # 2. Heal truncated split name on last author if applicable
    leaked_tokens = sanitize_author_list(clean_leaked) if clean_leaked else []
    if final_authors and leaked_tokens:
        last_name = final_authors[-1].strip()
        last_parts = last_name.split()
        first_leaked = leaked_tokens[0].strip()

        # If last author looks like just a given name (e.g. 'Shiva', 'Mariana', 'Namrata')
        # and first_leaked is a surname (e.g. 'Kalidindi', 'Castro', 'Srivastava')
        if len(last_parts) == 1 and len(first_leaked.split()) == 1:
            healed = f"{last_name} {first_leaked}"
            final_authors[-1] = healed
            leaked_tokens = leaked_tokens[1:]
        elif len(last_parts) == 2 and last_parts[1].endswith('.'):
            healed = f"{last_name} {first_leaked}"
            final_authors[-1] = healed
            leaked_tokens = leaked_tokens[1:]

    # 3. Append remaining leaked tokens not already in final_authors
    for tok in leaked_tokens:
        tok_clean = tok.strip()
        if not tok_clean:
            continue
        # Avoid duplicate
        if not any(tok_clean.lower() == fa.lower() for fa in final_authors):
            final_authors.append(tok_clean)

    # Ensure no trailing quotes or punctuation in author names
    cleaned_final = []
    for fa in final_authors:
        clean_fa = re.sub(r'^[“\"\']|[”\"\']$', '', fa).strip()
        clean_fa = re.sub(r'\(.*?\)', '', clean_fa).strip()
        if clean_fa and clean_fa not in cleaned_final:
            cleaned_final.append(clean_fa)
    final_authors = cleaned_final

    # Update database: delete old paper_authors for prev_pid and re-insert in clean order
    c.execute('DELETE FROM paper_authors WHERE paper_id = ?', (prev_pid,))
    for order, auth_name in enumerate(final_authors):
        c.execute('SELECT id FROM authors WHERE display_name = ?', (auth_name,))
        row = c.fetchone()
        if row:
            a_id = row[0]
        else:
            c.execute('INSERT INTO authors (display_name) VALUES (?)', (auth_name,))
            a_id = c.lastrowid
        c.execute(
            'INSERT INTO paper_authors (paper_id, author_id, author_order) VALUES (?, ?, ?)',
            (prev_pid, a_id, order)
        )

    # Update citation
    cit = f"{', '.join(final_authors)} ({prev_year}). {prev_title}. Proceedings of {conf} {prev_year}."
    c.execute('UPDATE papers SET citation = ? WHERE id = ?', (cit, prev_pid))

    return final_authors, cit


def update_paper_record(conn: sqlite3.Connection, pid: str, clean_title: str, conf: str) -> str:
    """Update title and citation for cleaned paper. Returns new citation."""
    c = conn.cursor()
    c.execute(
        '''SELECT a.display_name FROM paper_authors pa
           JOIN authors a ON pa.author_id = a.id
           WHERE pa.paper_id = ? ORDER BY pa.author_order''',
        (pid,)
    )
    auth_names = [r[0] for r in c.fetchall()]
    c.execute('SELECT year FROM papers WHERE id = ?', (pid,))
    year = c.fetchone()[0]

    cit = f"{', '.join(auth_names)} ({year}). {clean_title}. Proceedings of {conf} {year}."
    c.execute('UPDATE papers SET title = ?, citation = ? WHERE id = ?', (clean_title, cit, pid))
    return cit


def sync_derived_paper_md(pid: str, title: str, authors: List[str], citation: str):
    """Synchronize derived markdown file if it exists."""
    md_file = os.path.join(DERIVED_PAPERS_DIR, f"{pid}.md")
    if not os.path.exists(md_file):
        return

    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()

    content = re.sub(r'^title:\s*.*$', f'title: "{title}"', content, flags=re.MULTILINE)
    content = re.sub(r'^citation:\s*.*$', f'citation: "{citation}"', content, flags=re.MULTILINE)
    content = re.sub(r'^#\s+.*$', f'# {title}', content, flags=re.MULTILINE)

    with open(md_file, "w", encoding="utf-8") as f:
        f.write(content)


def sync_ground_truth_registry(repairs_map: Dict[str, Dict[str, Any]]):
    """Update ground truth registry with clean titles, authors, and citations."""
    if not os.path.exists(REGISTRY_PATH):
        return

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)

    updated_count = 0
    papers_list = registry.get("papers", [])
    for p in papers_list:
        pid = p.get("id")
        if pid in repairs_map:
            rep = repairs_map[pid]
            if "clean_title" in rep:
                p["title"] = rep["clean_title"]
            if "citation" in rep:
                p["citation"] = rep["citation"]
            if "authors" in rep:
                p["authors"] = [{"display_name": a} for a in rep["authors"]]
            updated_count += 1

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    print(f"Synchronized ground_truth_registry.json ({updated_count} entries updated)")


def sync_manifest(repairs_map: Dict[str, Dict[str, Any]]):
    """Update paper sources manifest."""
    if not os.path.exists(MANIFEST_PATH):
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    updated_count = 0
    for pid, rep in repairs_map.items():
        if pid in manifest and "clean_title" in rep:
            manifest[pid]["title"] = rep["clean_title"]
            updated_count += 1

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"Synchronized paper_sources_manifest.json ({updated_count} entries updated)")


def sync_tableau(repairs_map: Dict[str, Dict[str, Any]]):
    """Update tableau export CSV with clean titles and citations."""
    if not os.path.exists(TABLEAU_PATH):
        return

    rows = []
    with open(TABLEAU_PATH, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows.append(header)
        title_idx = header.index("title") if "title" in header else 1
        cit_idx = header.index("citation") if "citation" in header else 8

        for r in reader:
            if not r:
                continue
            pid = r[0]
            if pid in repairs_map:
                rep = repairs_map[pid]
                if "clean_title" in rep:
                    r[title_idx] = rep["clean_title"]
                if "citation" in rep:
                    r[cit_idx] = rep["citation"]
            rows.append(r)

    with open(TABLEAU_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f"Synchronized {TABLEAU_PATH}")


def sync_reviews(repairs_map: Dict[str, Dict[str, Any]]):
    """Update review files and cache files referencing old dirty titles."""
    # JSON reviews
    for folder in [REVIEWS_DIR, CACHE_DIR]:
        if not os.path.exists(folder):
            continue
        for fname in os.listdir(folder):
            if fname.endswith(".json"):
                fpath = os.path.join(folder, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    changed = False
                    papers = data.get("papers", []) if isinstance(data, dict) else []
                    if isinstance(data, list):
                        papers = data
                    for p in papers:
                        if isinstance(p, dict):
                            pid = p.get("id")
                            if pid in repairs_map and "clean_title" in repairs_map[pid]:
                                p["title"] = repairs_map[pid]["clean_title"]
                                changed = True
                    if changed:
                        with open(fpath, "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                except Exception:
                    pass

    # Markdown reviews
    if os.path.exists(REVIEWS_DIR):
        for fname in os.listdir(REVIEWS_DIR):
            if fname.endswith(".md"):
                fpath = os.path.join(REVIEWS_DIR, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        md = f.read()
                    changed = False
                    for pid, rep in repairs_map.items():
                        if "dirty_title" in rep and "clean_title" in rep:
                            dirty = rep["dirty_title"]
                            clean = rep["clean_title"]
                            if dirty in md:
                                md = md.replace(dirty, clean)
                                changed = True
                    if changed:
                        with open(fpath, "w", encoding="utf-8") as f:
                            f.write(md)
                except Exception:
                    pass
    print("Synchronized review files and review caches.")


def main():
    print("=== Repairing 2026 Proceedings: Clean Leaked Titles & Re-assign Authors ===")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")

    md_texts = {}
    for conf, path in VOL_MD.items():
        with open(path, "r", encoding="utf-8") as f:
            md_texts[conf] = f.read()

    repairs = identify_repairs(conn)
    print(f"Detected {len(repairs)} papers requiring title cleanup.")

    sync_map: Dict[str, Dict[str, Any]] = {}

    with conn:
        for r in repairs:
            pid = r['paper_id']
            conf = r['conference']
            dirty_t = r['dirty_title']
            clean_t = r['clean_title']
            leaked = r['leaked_prefix']
            prev_pid = r['prev_paper_id']

            # 1. Clean paper title & update its citation
            clean_cit = update_paper_record(conn, pid, clean_t, conf)

            # Get authors for cleaned paper
            c = conn.cursor()
            c.execute(
                '''SELECT a.display_name FROM paper_authors pa
                   JOIN authors a ON pa.author_id = a.id
                   WHERE pa.paper_id = ? ORDER BY pa.author_order''',
                (pid,)
            )
            clean_auths = [row[0] for row in c.fetchall()]

            sync_map[pid] = {
                "dirty_title": dirty_t,
                "clean_title": clean_t,
                "citation": clean_cit,
                "authors": clean_auths
            }
            sync_derived_paper_md(pid, clean_t, clean_auths, clean_cit)

            # 2. Heal / Re-assign authors to prev_pid
            if prev_pid:
                prev_auths, prev_cit = heal_and_reassign_authors(
                    conn, prev_pid, leaked, conf, md_texts[conf]
                )
                c.execute('SELECT title FROM papers WHERE id=?', (prev_pid,))
                prev_title = c.fetchone()[0]
                sync_map[prev_pid] = {
                    "clean_title": prev_title,
                    "citation": prev_cit,
                    "authors": prev_auths
                }
                sync_derived_paper_md(prev_pid, prev_title, prev_auths, prev_cit)

    print("Database updates committed successfully.")

    # 3. Synchronize derived files
    sync_ground_truth_registry(sync_map)
    sync_manifest(sync_map)
    sync_tableau(sync_map)
    sync_reviews(sync_map)

    print("=== All Title & Author Repairs Completed Successfully ===")


if __name__ == "__main__":
    main()
