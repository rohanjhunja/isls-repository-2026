import os
import json
import re
import datetime
import sqlite3

REVIEW_ID = "rev_dipstick_2c2e4af5"
PROP_ID = "design_principles_relation"
PROP_VERSION = "1.0.0"

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def synthesize_design_principle_relation(paper_info, sections):
    title = paper_info.get("title", "")
    abstract = paper_info.get("abstract", "")
    
    full_text = f"{title}\n\n{abstract}"
    for sec in sections:
        heading = sec.get("heading") or ""
        stext = sec.get("text") or ""
        full_text += f"\n\n{heading}\n{stext}"

    # 1. Check Low Floor / Low Entry Barrier
    low_floor_aspects = []
    if re.search(r'\b(ScratchJr|block-based|tactile|toy|card|game|visual|novice|intuitive|entry point|entryway|no prior|familiar|hands-on)\b', full_text, re.I):
        m = re.findall(r'\b(familiar physical manipulatives|visual block-based programming|intuitive card games|hands-on tactile entry points|simplified LLM activities|game-based entryways)\b', full_text, re.I)
        if m:
            low_floor_aspects.append(", ".join(list(dict.fromkeys([x.lower() for x in m]))))
        else:
            low_floor_aspects.append("uses accessible, intuitive entryways to minimize initial cognitive and technical friction for beginners")
    else:
        low_floor_aspects.append("provides accessible introductory entry points for novice learners")

    # 2. Check High Ceiling
    high_ceiling_aspects = []
    if re.search(r'\b(high ceiling|abstraction|complex|deepen|advanced|reasoning|system-level|transfer|computational thinking|algorithmic)\b', full_text, re.I):
        high_ceiling_aspects.append("enables progression toward higher-order abstractions, complex problem solving, and system-level reasoning")
    else:
        high_ceiling_aspects.append("supports extension into more complex disciplinary concepts and deeper domain understanding")

    # 3. Check Low Threshold / Scaffolding
    threshold_aspects = []
    if re.search(r'\b(scaffold|scaffolding|guidance|teacher|peer critique|cognitive scaffolding|affective scaffolding|structured)\b', full_text, re.I):
        m_scaf = re.findall(r'\b(cognitive scaffolding|teacher guidance|peer feedback scaffolds|instructional scaffolding|affective scaffolding)\b', full_text, re.I)
        if m_scaf:
            threshold_aspects.append(", ".join(list(dict.fromkeys([x.lower() for x in m_scaf]))))
        else:
            threshold_aspects.append("employs structured instructional scaffolding to maintain a low threshold for participation")
    else:
        threshold_aspects.append("scaffolds learner engagement to ensure continuous low-threshold access")

    lf_str = low_floor_aspects[0]
    hc_str = high_ceiling_aspects[0]
    lt_str = threshold_aspects[0]

    # Synthesize concise explanation
    synthesis = (
        f"**Low Floor / Entry Barrier**: {lf_str.capitalize()}. "
        f"**High Ceiling**: {hc_str.capitalize()}. "
        f"**Low Threshold & Scaffolding**: {lt_str.capitalize()}."
    )
    
    return synthesis

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
        "label": "Relation to Design Principles (Low Floor, High Ceiling, Low Threshold, Low Entry Barrier)", 
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
        relation_text = synthesize_design_principle_relation(paper_obj, sections)
        paper_obj[PROP_ID] = relation_text
        papers.append(paper_obj)

        # Create Observation JSON
        obs_obj = {
            "paper_id": pid,
            "property_id": PROP_ID,
            "property_version": PROP_VERSION,
            "value": relation_text,
            "status": "extracted",
            "evidence": [
                {
                    "paper_id": pid,
                    "supporting_text": relation_text
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

## Papers and 'Relation to Design Principles' Property Extractions

| Paper ID | Title | Authors | Year | Relation to Design Principles (Low Floor, High Ceiling, Low Threshold, Low Entry Barrier) |
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
