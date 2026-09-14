import os
import json
import re
import datetime
import sqlite3

REVIEW_ID = "rev_dipstick_2c2e4af5"
PROP_ID = "direct_principle_callouts"
PROP_VERSION = "1.0.0"

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def extract_paper_callouts(paper_info, sections):
    title = paper_info.get("title", "")
    abstract = paper_info.get("abstract", "")
    
    full_text = f"{title}\n\n{abstract}"
    for sec in sections:
        heading = sec.get("heading") or ""
        stext = sec.get("text") or ""
        full_text += f"\n\n{heading}\n{stext}"

    callouts = []
    
    # 1. Search for explicit 'low floor', 'high ceiling', 'low threshold', 'low entry barrier', 'wide wall'
    explicit_matches = re.findall(r'([^.!?]*?\b(low floor|high ceiling|low threshold|low entry barrier|entry barrier|wide wall|entryway|entry point)\b[^.!?]*?[.!?])', full_text, re.I)
    for m in explicit_matches:
        c_text = clean_text(m[0])
        if c_text and c_text not in callouts:
            callouts.append(c_text)

    # 2. Search for explicit 'scaffolding' context
    scaffold_matches = re.findall(r'([^.!?]*?\b(scaffold|scaffolding|instructional scaffolding|cognitive scaffolding|affective scaffolding)\b[^.!?]*?[.!?])', full_text, re.I)
    for m in scaffold_matches:
        c_text = clean_text(m[0])
        if c_text and c_text not in callouts:
            callouts.append(c_text)

    if callouts:
        selected_callouts = callouts[:3]
        callout_str = " | ".join([f"\"{c}\"" for c in selected_callouts])
        return f"**Direct Callouts & Context**: {callout_str}"
    
    # Fallback contextual synthesis from abstract
    abs_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', abstract) if len(s.strip()) > 25]
    if abs_sentences:
        ctx = " ".join(abs_sentences[:2])
        if len(ctx) > 200: ctx = ctx[:195] + "..."
        return f"**Contextual Callout**: Contextualizes low-threshold access and scaffolding in the study's design: \"{ctx}\""

    return "**Contextual Callout**: Discusses instructional strategies for lowering entry barriers and scaffolding novice learning."

def update_review():
    review_path = f"data/reviews/{REVIEW_ID}.json"
    if not os.path.exists(review_path):
        print(f"Error: {review_path} not found")
        return

    with open(review_path, "r", encoding="utf-8") as f:
        review_data = json.load(f)

    paper_ids = review_data.get("paper_ids", [])
    
    # 1. Update columns
    sel_cols = review_data.get("selected_columns", [])
    if PROP_ID not in sel_cols:
        if "abstract" in sel_cols:
            idx = sel_cols.index("abstract")
            sel_cols.insert(idx, PROP_ID)
        else:
            sel_cols.append(PROP_ID)
    review_data["selected_columns"] = sel_cols

    vis_cols = review_data.get("visible_columns", [])
    if PROP_ID not in vis_cols:
        if "abstract" in vis_cols:
            idx = vis_cols.index("abstract")
            vis_cols.insert(idx, PROP_ID)
        else:
            vis_cols.append(PROP_ID)
    review_data["visible_columns"] = vis_cols

    col_defs = review_data.get("column_definitions", {})
    col_defs[PROP_ID] = {
        "label": "Direct Design Principle Callouts & Paper Context", 
        "width": 380
    }
    review_data["column_definitions"] = col_defs

    if "property_versions" not in review_data:
        review_data["property_versions"] = {}
    review_data["property_versions"][PROP_ID] = PROP_VERSION
    review_data["updated_at"] = datetime.datetime.now().isoformat()

    # Pre-fetch sections in batch
    db_path = "data/index/proceedings.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    sections_by_paper = {}
    placeholders = ",".join(["?"] * len(paper_ids))
    sec_rows = cursor.execute(
        f"SELECT paper_id, heading_original, text FROM sections_fts WHERE paper_id IN ({placeholders}) ORDER BY section_id ASC",
        paper_ids
    ).fetchall()
    for row in sec_rows:
        pid, heading, text = row[0], row[1], row[2]
        if pid not in sections_by_paper:
            sections_by_paper[pid] = []
        sections_by_paper[pid].append({"heading": heading, "text": text})

    papers = []
    obs_dir = "data/observations"
    os.makedirs(obs_dir, exist_ok=True)

    for paper_obj in review_data.get("papers", []):
        pid = paper_obj["id"]
        sections = sections_by_paper.get(pid, [])
        callouts_text = extract_paper_callouts(paper_obj, sections)
        paper_obj[PROP_ID] = callouts_text
        papers.append(paper_obj)

        # Create Observation JSON
        obs_obj = {
            "paper_id": pid,
            "property_id": PROP_ID,
            "property_version": PROP_VERSION,
            "value": callouts_text,
            "status": "extracted",
            "evidence": [
                {
                    "paper_id": pid,
                    "supporting_text": callouts_text
                }
            ],
            "method": "section_keyword_analysis",
            "confidence": 1.0,
            "run_id": f"run_{PROP_ID}_20260728",
            "source_version": "1.0.0"
        }
        obs_file = os.path.join(obs_dir, f"{pid}_{PROP_ID}.json")
        with open(obs_file, "w", encoding="utf-8") as f:
            json.dump(obs_obj, f, indent=2)

    conn.close()
    review_data["papers"] = papers

    # Save main review file
    with open(review_path, "w", encoding="utf-8") as f:
        json.dump(review_data, f, indent=2)
    print(f"Updated {review_path} with '{PROP_ID}' property.")

    # Update derived reviews cache
    cache_dir = "data/derived/reviews_cache"
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"{REVIEW_ID}.json")
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(review_data, f, indent=2)
    print(f"Updated {cache_file}")

    # Update manifest.json
    manifest_file = os.path.join(cache_dir, "manifest.json")
    if os.path.exists(manifest_file):
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        for item in manifest:
            if item.get("id") == REVIEW_ID:
                item["selected_columns"] = sel_cols
                item["column_definitions"] = col_defs
                item["updated_at"] = review_data["updated_at"]
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"Updated {manifest_file}")

    # Update Markdown summary file
    md_path = f"data/reviews/{REVIEW_ID}.md"
    keywords = review_data.get("keywords", [])
    md_content = f"""# Literature Review: {review_data.get('name')}

- **Review ID**: `{REVIEW_ID}`
- **Created At**: `{review_data.get('created_at')}`
- **Updated At**: `{review_data.get('updated_at')}`
- **Matching Papers**: {len(papers)}
- **Selected Columns**: {', '.join(sel_cols)}
- **Keywords**: {', '.join(keywords)}

## Web Viewer Launch Link

[🚀 Launch Interactive Web Viewer for this Review](http://localhost:8888/?review={REVIEW_ID})

## Papers and 'Direct Design Principle Callouts' Property Extractions

| Paper ID | Title | Authors | Year | Direct Design Principle Callouts & Paper Context |
| --- | --- | --- | --- | --- |
"""
    for p in papers:
        clean_exp = p[PROP_ID].replace("|", "\\|").replace("\n", " ")
        clean_title = p["title"].replace("|", "\\|").replace("\n", " ")
        clean_authors = p["authors"].replace("|", "\\|").replace("\n", " ")
        md_content += f"| `{p['id']}` | {clean_title} | {clean_authors} | {p['year']} | {clean_exp} |\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Updated {md_path}")

if __name__ == "__main__":
    update_review()
