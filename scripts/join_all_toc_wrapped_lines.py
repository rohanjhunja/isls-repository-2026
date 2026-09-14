import sqlite3
import json
import re
import os
import gc
import sys

print("=== JOINING ALL MULTI-LINE TOC TITLES ACROSS THE REPOSITORY ===")

def get_md_filename(pid):
    pid_lower = pid.lower()
    for year in ['2023', '2024', '2025', '2026']:
        if year in pid_lower:
            if 'cscl' in pid_lower:
                return f"cscl-{year}.md"
            elif 'icls' in pid_lower:
                return f"icls-{year}.md"
            elif 'isls' in pid_lower or 'general' in pid_lower:
                return f"isls-{year}.md"
    return None

md_contents = {}
for year in ['2023', '2024', '2025', '2026']:
    for prefix in ['cscl', 'icls', 'isls']:
        fname = f"{prefix}-{year}.md"
        fpath = os.path.join("proceedings_md", fname)
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                md_contents[fname] = f.read()

conn = sqlite3.connect("data/index/proceedings.db")
c = conn.cursor()
rows = c.execute("SELECT id, title, authors, data_json FROM papers").fetchall()

repaired = 0

for pid, cur_t, cur_a, dj in rows:
    if not cur_t:
        continue

    is_dangling = bool(re.search(r'\b(a|an|the|in|on|at|for|to|of|with|by|from|through|into|about|and|or|as|is|are|during|between|among|using|towards?|-)\s*$', cur_t, re.I))
    if not is_dangling:
        continue

    md_fname = get_md_filename(pid)
    if not md_fname or md_fname not in md_contents:
        continue

    content = md_contents[md_fname]
    d = json.loads(dj) if dj else {}

    # Escape cur_t for regex search
    # Search for multi-line block ending with dots and page number in TOC
    # e.g. "Agency at Scale: Embedding Interpersonal Interaction and Collaboration in\nan Online Professional Development Platform ...... 3"
    esc_t = re.escape(cur_t)
    m = re.search(r'(' + esc_t + r'\s*\n\s*[^\n]+?)\s*\.{3,}\s*\d+', content, re.I)
    if m:
        raw_match = m.group(1).strip()
        lines = [l.strip() for l in raw_match.split('\n') if l.strip()]
        full_t = " ".join(lines)
        full_t = re.sub(r'^\d+\s*', '', full_t).strip()
        full_t = re.sub(r'\.{3,}.*$', '', full_t).strip()
        full_t = re.sub(r'\s+', ' ', full_t)

        if len(full_t) > len(cur_t):
            d["title"] = full_t
            c.execute("UPDATE papers SET title = ?, data_json = ? WHERE id = ?", (full_t, json.dumps(d), pid))
            repaired += 1

conn.commit()
conn.close()

print(f"Joined multi-line TOC titles for {repaired} papers in proceedings.db!")

sys.path.insert(0, '.')
from scripts.sync_cleaned_data import sync_all
sync_all()

print("Repository multi-line TOC title join and review sync complete!")
