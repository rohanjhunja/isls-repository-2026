#!/usr/bin/env python3
"""
Update title and author fields for 2026 papers across all saved reviews.

Updates:
1. data/reviews/*.json
2. data/derived/reviews_cache/*.json
3. data/derived/reviews_cache/manifest.json
4. data/reviews/*.md
5. data/reports/*.md
"""

import os
import re
import json
import sqlite3
import datetime
from typing import Dict, List, Any, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "proceedings.db")
REVIEWS_DIR = os.path.join(BASE_DIR, "data", "reviews")
CACHE_DIR = os.path.join(BASE_DIR, "data", "derived", "reviews_cache")
MANIFEST_PATH = os.path.join(CACHE_DIR, "manifest.json")
REPORTS_DIR = os.path.join(BASE_DIR, "data", "reports")

def clean_spacing(s: Any) -> str:
    if not s:
        return ""
    return re.sub(r'\s+', ' ', str(s)).strip()

def load_canonical_2026_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    raw_titles = c.execute("SELECT id, title, conference FROM papers WHERE year = 2026").fetchall()
    db_titles = {}
    db_confs = {}
    for pid, t, conf in raw_titles:
        if t:
            db_titles[pid] = clean_spacing(t)
        db_confs[pid] = conf or "ISLS"

    author_rows = c.execute("""
        SELECT pa.paper_id, a.display_name
        FROM paper_authors pa
        JOIN authors a ON pa.author_id = a.id
        WHERE pa.paper_id IN (SELECT id FROM papers WHERE year = 2026)
        ORDER BY pa.paper_id, pa.author_order ASC
    """).fetchall()

    db_authors_list = {}
    for pid, dname in author_rows:
        cn = clean_spacing(dname)
        if cn:
            if pid not in db_authors_list:
                db_authors_list[pid] = []
            db_authors_list[pid].append(cn)

    db_authors = {pid: ", ".join(names) for pid, names in db_authors_list.items()}
    conn.close()
    return db_titles, db_authors, db_confs

def update_review_json_files(db_titles: Dict[str, str], db_authors: Dict[str, str], db_confs: Dict[str, str]):
    now_iso = datetime.datetime.now().isoformat()
    modified_reviews = set()
    total_title_updates = 0
    total_author_updates = 0

    all_review_ids = set()
    for d in [REVIEWS_DIR, CACHE_DIR]:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.endswith('.json') and f != 'manifest.json':
                    all_review_ids.add(f[:-5])

    for rev_id in sorted(all_review_ids):
        rev_path = os.path.join(REVIEWS_DIR, f"{rev_id}.json")
        cache_path = os.path.join(CACHE_DIR, f"{rev_id}.json")

        target_file = rev_path if os.path.exists(rev_path) else cache_path
        with open(target_file, 'r', encoding='utf-8') as fp:
            data = json.load(fp)

        papers = data.get('papers', []) if isinstance(data, dict) else []
        file_changed = False
        t_updates = 0
        a_updates = 0

        for p in papers:
            if not isinstance(p, dict):
                continue
            pid = p.get('id')
            is_2026 = (pid in db_titles) or (str(p.get('year')) == '2026') or ('2026' in str(pid))
            if not is_2026 or pid not in db_titles:
                continue

            can_title = db_titles[pid]
            can_authors = db_authors.get(pid, '')

            old_title = p.get('title', '')
            if old_title != can_title:
                p['title'] = can_title
                t_updates += 1
                file_changed = True

            old_authors = p.get('authors', '')
            if old_authors != can_authors:
                p['authors'] = can_authors
                if 'author' in p:
                    p['author'] = can_authors
                a_updates += 1
                file_changed = True

            if 'citation' in p:
                conf = p.get('conference') or db_confs.get(pid, 'ISLS')
                p['citation'] = f"{can_authors} (2026). {can_title}. {conf}."

        if file_changed:
            data['updated_at'] = now_iso
            modified_reviews.add(rev_id)
            total_title_updates += t_updates
            total_author_updates += a_updates

            # Save in reviews dir
            if os.path.exists(REVIEWS_DIR):
                with open(rev_path, 'w', encoding='utf-8') as fp:
                    json.dump(data, fp, indent=2, ensure_ascii=False)

            # Save in cache dir
            if os.path.exists(CACHE_DIR):
                with open(cache_path, 'w', encoding='utf-8') as fp:
                    json.dump(data, fp, indent=2, ensure_ascii=False)

            print(f"Updated {rev_id}.json: {t_updates} titles, {a_updates} authors updated.")

    return modified_reviews, total_title_updates, total_author_updates, now_iso

def update_manifest(modified_reviews: set, now_iso: str):
    if not os.path.exists(MANIFEST_PATH):
        return
    with open(MANIFEST_PATH, 'r', encoding='utf-8') as fp:
        manifest = json.load(fp)

    changed = False
    for item in manifest:
        if item.get('id') in modified_reviews:
            item['updated_at'] = now_iso
            changed = True

    if changed:
        with open(MANIFEST_PATH, 'w', encoding='utf-8') as fp:
            json.dump(manifest, fp, indent=2, ensure_ascii=False)
        print("Updated manifest.json with fresh timestamps.")

def update_markdown_reviews(db_titles: Dict[str, str], db_authors: Dict[str, str]):
    if not os.path.exists(REVIEWS_DIR):
        return

    md_files = [f for f in os.listdir(REVIEWS_DIR) if f.endswith('.md')]
    for fname in sorted(md_files):
        fpath = os.path.join(REVIEWS_DIR, fname)
        with open(fpath, 'r', encoding='utf-8') as fp:
            lines = fp.readlines()

        table_header_idx = None
        header_cols = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('|') and ('Title' in stripped or 'title' in stripped):
                table_header_idx = i
                header_cols = [c.strip().lower() for c in stripped.split('|')[1:-1]]
                break

        if table_header_idx is None:
            continue

        pid_col = None
        title_col = None
        author_col = None
        for c_idx, col_name in enumerate(header_cols):
            if col_name in ['paper id', 'paper_id', 'id', 'pid']:
                pid_col = c_idx
            elif 'title' in col_name:
                title_col = c_idx
            elif 'author' in col_name:
                author_col = c_idx

        # If review has no PID column (e.g. rev_dipstick_8bd32a4b.md), match using JSON file
        json_papers_map = {}
        rev_id = fname[:-3]
        json_path = os.path.join(REVIEWS_DIR, f"{rev_id}.json")
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as fp:
                jdata = json.load(fp)
            for p in jdata.get('papers', []):
                if p.get('id') in db_titles:
                    clean_t = clean_spacing(p.get('title', ''))
                    json_papers_map[clean_t] = p.get('id')
                    abs_snip = clean_spacing(p.get('abstract', ''))[:50]
                    if abs_snip:
                        json_papers_map[abs_snip] = p.get('id')

        file_changed = False
        new_lines = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if i <= table_header_idx + 1 or not stripped.startswith('|'):
                new_lines.append(line)
                continue

            # It is a table row
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            target_pid = None

            if pid_col is not None and pid_col < len(cells):
                raw_pid = cells[pid_col].strip('` ')
                if raw_pid in db_titles:
                    target_pid = raw_pid

            if not target_pid and title_col is not None and title_col < len(cells):
                raw_t = clean_spacing(cells[title_col])
                if raw_t in json_papers_map:
                    target_pid = json_papers_map[raw_t]
                else:
                    # Try matching abstract
                    for snip, mapped_pid in json_papers_map.items():
                        if snip and snip in stripped:
                            target_pid = mapped_pid
                            break

            if target_pid and target_pid in db_titles:
                can_title = db_titles[target_pid].replace('|', '\\|')
                can_authors = db_authors.get(target_pid, '').replace('|', '\\|')

                if title_col is not None and title_col < len(cells):
                    if cells[title_col] != can_title:
                        cells[title_col] = can_title
                        file_changed = True

                if author_col is not None and author_col < len(cells):
                    if cells[author_col] != can_authors:
                        cells[author_col] = can_authors
                        file_changed = True

                new_line = f"| {' | '.join(cells)} |\n"
                new_lines.append(new_line)
            else:
                new_lines.append(line)

        if file_changed:
            with open(fpath, 'w', encoding='utf-8') as fp:
                fp.writelines(new_lines)
            print(f"Updated Markdown review table: {fname}")

def update_reports(db_titles: Dict[str, str], db_authors: Dict[str, str]):
    sys_json = os.path.join(REVIEWS_DIR, "systematic_review_lit_review.json")
    if not os.path.exists(sys_json):
        return

    with open(sys_json, "r", encoding="utf-8") as fp:
        sys_data = json.load(fp)

    p2026_list = [p for p in sys_data.get("papers", []) if str(p.get("year")) == "2026"]
    abstract_to_pid = {}
    for p in p2026_list:
        pid = p.get("id")
        ab_snip = clean_spacing(p.get("abstract", ""))[:60]
        if ab_snip:
            abstract_to_pid[ab_snip] = pid

    for rname in ["systematic_review_literature_review.md", "sys_review_clean.md"]:
        rpath = os.path.join(REPORTS_DIR, rname)
        if not os.path.exists(rpath):
            continue

        with open(rpath, "r", encoding="utf-8") as fp:
            lines = fp.readlines()

        file_changed = False
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('|') and '2026' in stripped:
                cells = [c.strip() for c in stripped.split('|')[1:-1]]
                matched_pid = None
                for snip, pid in abstract_to_pid.items():
                    if snip in stripped:
                        matched_pid = pid
                        break

                if matched_pid and matched_pid in db_titles:
                    can_title = db_titles[matched_pid].replace('|', '\\|')
                    can_authors = db_authors.get(matched_pid, '').replace('|', '\\|')
                    cells[0] = f"**{can_title}**<br>*Authors*: {can_authors}"
                    file_changed = True
                    new_lines.append(f"| {' | '.join(cells)} |\n")
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        if file_changed:
            with open(rpath, "w", encoding="utf-8") as fp:
                fp.writelines(new_lines)
            print(f"Updated Report Markdown: {rname}")

def main():
    print("=== Updating 2026 Paper Titles and Authors across All Saved Reviews ===")
    db_titles, db_authors, db_confs = load_canonical_2026_data()
    print(f"Loaded {len(db_titles)} canonical 2026 papers and {len(db_authors)} author entries from proceedings.db.")

    modified_reviews, t_count, a_count, now_iso = update_review_json_files(db_titles, db_authors, db_confs)
    print(f"Total JSON title updates: {t_count}")
    print(f"Total JSON author updates: {a_count}")
    print(f"Total JSON reviews modified: {len(modified_reviews)}")

    update_manifest(modified_reviews, now_iso)
    update_markdown_reviews(db_titles, db_authors)
    update_reports(db_titles, db_authors)

    print("=== 2026 Paper Title & Author Sync Completed Successfully! ===")

if __name__ == '__main__':
    main()
