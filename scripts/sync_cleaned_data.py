import sqlite3
import json
import os
import sys
import gc
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from proceedings_ingest.utils.text_cleanup import repair_title_and_authors, clean_section_blocks, clean_section_text

BATCH_SIZE = 100

def sync_database(db_path):
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT count(*) FROM papers")
    total_papers = cursor.fetchone()[0]
    print(f"Starting database sync for {total_papers} papers...")

    # Fast fetch sec-001 text for all papers in a single query
    print("Pre-fetching first section texts...")
    first_sec_map = {}
    try:
        sec_rows = cursor.execute(
            "SELECT paper_id, text FROM sections_fts WHERE section_id IN ('sec-001', 'sec-1', '1') OR section_id LIKE '%001'"
        ).fetchall()
        for pid, stext in sec_rows:
            if pid not in first_sec_map:
                first_sec_map[pid] = stext or ''
    except Exception as e:
        print(f"Warning fetching first sections: {e}")

    offset = 0
    updated_papers_count = 0

    while True:
        rows = cursor.execute(
            "SELECT id, title, authors, abstract, data_json FROM papers LIMIT ? OFFSET ?",
            (BATCH_SIZE, offset)
        ).fetchall()

        if not rows:
            break

        for pid, raw_title, raw_authors, abstract, data_json_str in rows:
            first_sec_text = first_sec_map.get(pid, '')
            cleaned_title, cleaned_authors = repair_title_and_authors(raw_title, raw_authors, first_sec_text)

            # Update data_json metadata
            data_dict = json.loads(data_json_str) if data_json_str else {}
            data_dict['title'] = cleaned_title
            
            # Format authors into structured dict array or string matching schema
            if cleaned_authors:
                author_names = [a.strip() for a in cleaned_authors.split(',') if a.strip()]
                structured_authors = []
                for a_name in author_names:
                    parts = a_name.split()
                    structured_authors.append({
                        'display_name': a_name,
                        'given_name': parts[0] if parts else a_name,
                        'family_name': parts[-1] if len(parts) > 1 else a_name
                    })
                data_dict['authors'] = structured_authors
            
            new_data_json = json.dumps(data_dict)

            if cleaned_title != raw_title or cleaned_authors != raw_authors or new_data_json != data_json_str:
                cursor.execute(
                    "UPDATE papers SET title = ?, authors = ?, data_json = ? WHERE id = ?",
                    (cleaned_title, cleaned_authors, new_data_json, pid)
                )
                updated_papers_count += 1

        conn.commit()
        offset += BATCH_SIZE
        gc.collect()

    conn.close()
    print(f"Database sync complete. Updated {updated_papers_count} paper records.")


def sync_processed_sys_reviews():
    sys_path = 'data/processed_sys_reviews.json'
    if not os.path.exists(sys_path):
        return

    with open(sys_path, 'r', encoding='utf-8') as f:
        papers = json.load(f)

    db_conn = sqlite3.connect('data/index/proceedings.db')
    cursor = db_conn.cursor()

    cleaned_papers = []
    for p in papers:
        pid = p['id']
        sec_rows = cursor.execute(
            "SELECT text FROM sections_fts WHERE paper_id = ? ORDER BY section_id ASC LIMIT 1",
            (pid,)
        ).fetchone()
        first_sec = sec_rows[0] if sec_rows else ''

        c_title, c_authors = repair_title_and_authors(p['title'], p['authors'], first_sec)
        p['title'] = c_title
        p['authors'] = c_authors
        cleaned_papers.append(p)

    db_conn.close()

    with open(sys_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_papers, f, indent=2)

    print(f"Updated {len(cleaned_papers)} papers in processed_sys_reviews.json")


def sync_derived_proceedings():
    derived_dir = 'data/derived'
    if not os.path.exists(derived_dir):
        return

    db_conn = sqlite3.connect('data/index/proceedings.db')
    cursor = db_conn.cursor()
    db_titles = dict(cursor.execute("SELECT id, title FROM papers").fetchall())
    db_authors = dict(cursor.execute("SELECT id, authors FROM papers").fetchall())
    db_conn.close()

    updated_files_count = 0
    for sub in sorted(os.listdir(derived_dir)):
        subpath = os.path.join(derived_dir, sub)
        if not os.path.isdir(subpath):
            continue

        json_file = os.path.join(subpath, f"{sub}.json")
        if os.path.exists(json_file):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            file_modified = False
            for p in data.get('papers', []):
                pid = p.get('id')
                if pid and pid in db_titles:
                    c_title = db_titles[pid]
                    if p.get('title') != c_title:
                        p['title'] = c_title
                        file_modified = True

                    # Check if paper MD file exists in derived papers subfolder
                    short_pid = pid.split('-')[-1] # e.g. paper-039 or paper-0039
                    paper_md_path = os.path.join(subpath, "papers", f"{short_pid}.md")
                    if os.path.exists(paper_md_path):
                        try:
                            with open(paper_md_path, 'r', encoding='utf-8') as mdf:
                                md_text = mdf.read()
                            if md_text.startswith('# '):
                                md_lines = md_text.split('\n')
                                md_lines[0] = f"# {c_title}"
                                with open(paper_md_path, 'w', encoding='utf-8') as mdf:
                                    mdf.write('\n'.join(md_lines))
                        except Exception:
                            pass

            if file_modified:
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                updated_files_count += 1

        gc.collect()

    print(f"Derived proceedings sync complete. Updated {updated_files_count} derived JSON files.")


def sync_all():
    db_path = 'data/index/proceedings.db'
    sync_database(db_path)
    sync_processed_sys_reviews()
    sync_derived_proceedings()

    # Re-run prepare_viewer_data.py to rebuild viewer_papers.json cleanly
    from scripts.prepare_viewer_data import main as prepare_viewer_main
    prepare_viewer_main()

    # Re-run build_clean_reviews.py to update review collections and cache
    from scripts.build_clean_reviews import main as build_reviews_main
    build_reviews_main()

    # Clean all review markdown and json files (e.g. rev_dipstick_2c2e4af5)
    from scripts.clean_all_review_files import clean_review_files
    clean_review_files()

    print("All datasets successfully synchronized and cleaned across the repository!")

if __name__ == '__main__':
    sync_all()
