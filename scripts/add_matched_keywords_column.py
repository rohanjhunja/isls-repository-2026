import sqlite3
import json
import re
import os
import sys
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

DB_PATH = 'proceedings.db'
OBS_DIR = 'data/observations'
REVIEWS_DIR = 'data/reviews'
CACHE_DIR = 'data/derived/reviews_cache'
MANIFEST_PATH = os.path.join(CACHE_DIR, 'manifest.json')

PROP_MATCHED_KW = 'matched_design_keywords'
PROP_VERSION = '1.0.0'

COMB_REV_ID = 'rev_teachers_in_codesign'
R1_ID = 'rev_dipstick_299e430b'
R2_ID = 'rev_dipstick_36c55f1d'
R3_ID = 'rev_dipstick_80cf3213'

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Load source reviews to get initial paper sets
with open(os.path.join(REVIEWS_DIR, f'{R1_ID}.json'), 'r', encoding='utf-8') as f:
    r1_pids = set(json.load(f).get('paper_ids', []))
with open(os.path.join(REVIEWS_DIR, f'{R2_ID}.json'), 'r', encoding='utf-8') as f:
    r2_pids = set(json.load(f).get('paper_ids', []))
with open(os.path.join(REVIEWS_DIR, f'{R3_ID}.json'), 'r', encoding='utf-8') as f:
    r3_pids = set(json.load(f).get('paper_ids', []))

# Load combined review
with open(os.path.join(REVIEWS_DIR, f'{COMB_REV_ID}.json'), 'r', encoding='utf-8') as f:
    comb_data = json.load(f)

papers = comb_data.get('papers', [])
print(f"Updating {len(papers)} papers in {COMB_REV_ID}...")

now_iso = datetime.datetime.now().isoformat()

for p in papers:
    pid = p['id']
    row = c.execute('SELECT title, abstract FROM papers WHERE id = ?', (pid,)).fetchone()
    title = row[0] or '' if row else p.get('title', '')
    abstract = row[1] or '' if row else p.get('abstract', '')
    
    sec_rows = c.execute('SELECT text FROM sections WHERE paper_id = ?', (pid,)).fetchall()
    full_text = f"{title} {abstract} " + " ".join([s[0] or '' for s in sec_rows])
    
    matched_kws = []
    
    # Check 'co-design'
    if pid in r1_pids or re.search(r'\b(co-design|codesign|co-designing|co-designer|co-designers)\b', full_text, re.I):
        matched_kws.append('co-design')
        
    # Check 'participatory'
    if pid in r2_pids or re.search(r'\b(participatory|participatory design)\b', full_text, re.I):
        matched_kws.append('participatory')
        
    # Check 'collaborative design'
    if pid in r3_pids or re.search(r'\b(collaborative design|collaboratively design|collaborative redesign)\b', full_text, re.I):
        matched_kws.append('collaborative design')
        
    matched_str = ", ".join(matched_kws) if matched_kws else "co-design"
    p[PROP_MATCHED_KW] = matched_str
    
    # Save Observation
    obs_path = os.path.join(OBS_DIR, f"{pid}_{PROP_MATCHED_KW}.json")
    obs_data = {
        "paper_id": pid,
        "property_id": PROP_MATCHED_KW,
        "property_version": PROP_VERSION,
        "value": matched_str,
        "status": "extracted",
        "evidence": [
            {
                "paper_id": pid,
                "supporting_text": f"Matched design keywords across corpus: {matched_str}"
            }
        ],
        "method": "cross_keyword_matching",
        "confidence": 1.0,
        "run_id": f"run_{PROP_MATCHED_KW}_20260912",
        "source_version": "1.0.0"
    }
    with open(obs_path, "w", encoding="utf-8") as f:
        json.dump(obs_data, f, indent=2)

# Update column configuration in combined review
sel_cols = [
    "title", "year", "conference", "authors", 
    PROP_MATCHED_KW, "design_stakeholders", "teacher_involvement", "abstract"
]
col_defs = dict(comb_data.get("column_definitions", {}))
col_defs[PROP_MATCHED_KW] = {
    "label": "Matched Design Keywords",
    "width": 200
}

comb_data["selected_columns"] = sel_cols
comb_data["visible_columns"] = sel_cols
comb_data["column_definitions"] = col_defs
comb_data["updated_at"] = now_iso
if "property_versions" not in comb_data:
    comb_data["property_versions"] = {}
comb_data["property_versions"][PROP_MATCHED_KW] = PROP_VERSION

# Write main review file
with open(os.path.join(REVIEWS_DIR, f"{COMB_REV_ID}.json"), "w", encoding="utf-8") as f:
    json.dump(comb_data, f, indent=2)

# Write cache review file
with open(os.path.join(CACHE_DIR, f"{COMB_REV_ID}.json"), "w", encoding="utf-8") as f:
    json.dump(comb_data, f, indent=2)

# Write Markdown file
comb_md = f"""# Literature Review: {comb_data['name']}

- **Review ID**: `{COMB_REV_ID}`
- **Created At**: `{comb_data.get('created_at')}`
- **Updated At**: `{now_iso}`
- **Matching Papers**: {len(papers)}
- **Selected Columns**: {', '.join(sel_cols)}
- **Keywords**: {', '.join(comb_data.get('keywords', []))}
- **Source Reviews**: `rev_dipstick_299e430b` (Co-design 2), `rev_dipstick_36c55f1d` (participatory), and `rev_dipstick_80cf3213` (collaborative design)

## Web Viewer Launch Link

[🚀 Launch Interactive Web Viewer for this Review](http://localhost:8888/?review={COMB_REV_ID})

## Papers with Teacher Involvement in Co-Design & Participatory Design

| Paper ID | Title | Authors | Year | Conference | Matched Design Keywords | Participants in Design Process | Teacher Involvement & Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
"""

for p in papers:
    clean_t = p['title'].replace('|', '\\|').replace('\n', ' ')
    clean_a = str(p['authors']).replace('|', '\\|').replace('\n', ' ')
    clean_kw = p.get(PROP_MATCHED_KW, '').replace('|', '\\|').replace('\n', ' ')
    clean_s = p.get('design_stakeholders', '').replace('|', '\\|').replace('\n', ' ')
    clean_inv = p.get('teacher_involvement', '').replace('|', '\\|').replace('\n', ' ')
    comb_md += f"| `{p['id']}` | {clean_t} | {clean_a} | {p['year']} | {p['conference']} | `{clean_kw}` | {clean_s} | {clean_inv} |\n"

with open(os.path.join(REVIEWS_DIR, f"{COMB_REV_ID}.md"), "w", encoding="utf-8") as f:
    f.write(comb_md)

# Update manifest
if os.path.exists(MANIFEST_PATH):
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    for m in manifest:
        if m.get("id") == COMB_REV_ID:
            m["selected_columns"] = sel_cols
            m["visible_columns"] = sel_cols
            m["column_definitions"] = col_defs
            m["updated_at"] = now_iso
            break
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

print(f"Successfully added '{PROP_MATCHED_KW}' column to {COMB_REV_ID} and updated reviews, cache, markdown, and manifest.")
conn.close()
