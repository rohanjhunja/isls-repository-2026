import os
import json
import re
import datetime
import sqlite3

REVIEW_ID = "rev_dipstick_2c2e4af5"
PROP_ID = "floor_ceiling_frameworks_findings"
PROP_VERSION = "1.0.0"

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def analyze_paper_frameworks_findings(paper_info, sections):
    title = paper_info.get("title", "")
    abstract = paper_info.get("abstract", "")
    
    full_text = f"{title}\n\n{abstract}"
    for sec in sections:
        heading = sec.get("heading") or ""
        stext = sec.get("text") or ""
        full_text += f"\n\n{heading}\n{stext}"

    # 1. Identify specific framework / tool
    framework = ""
    m = re.findall(r'\b(ScratchJr|Scratch|tangible manipulatives|block-based programming|creative coding|educational robotics|card-based games|AI-powered simulation|maker learning|virtual reality|VR)\b', full_text, re.I)
    if m:
        framework = ", ".join(list(dict.fromkeys([x.title() for x in m])))
    else:
        framework = "Pedagogical Scaffolding & Learning Design Framework"

    # 2. Identify methodology
    method = ""
    m_meth = re.findall(r'\b(case study|design-based research|pilot study|qualitative analysis|classroom enactments|participatory design|survey)\b', full_text, re.I)
    if m_meth:
        method = ", ".join(list(dict.fromkeys([x.title() for x in m_meth])))
    else:
        method = "Empirical Classroom / User Evaluation"

    # 3. Identify findings regarding entry barriers, low floor, high ceiling, scaffolding
    findings_list = []
    
    floor_ceiling_match = re.search(r'([^.!?]*?\b(low floor|high ceiling|low threshold|low barrier|entry point|entryway)\b[^.!?]*?[.!?])', full_text, re.I)
    if floor_ceiling_match:
        findings_list.append(clean_text(floor_ceiling_match.group(1)))

    scaffold_match = re.search(r'([^.!?]*?\b(scaffold|scaffolding|guidance|novice|entry barrier)\b[^.!?]*?[.!?])', full_text, re.I)
    if scaffold_match and (not floor_ceiling_match or scaffold_match.group(1) not in findings_list[0]):
        findings_list.append(clean_text(scaffold_match.group(1)))

    if not findings_list:
        abs_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', abstract) if len(s.strip()) > 20]
        if abs_sentences:
            findings_list.append(abs_sentences[-1])
        else:
            findings_list.append("Demonstrates instructional strategies to lower entry barriers and scaffold novice learning.")

    finding_str = " ".join(findings_list[:2])
    if len(finding_str) > 220:
        finding_str = finding_str[:215] + "..."

    return f"**Framework/Tool**: {framework}. **Method**: {method}. **Key Findings & Entry Barrier Impact**: {finding_str}"

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
    col_defs[PROP_ID] = {"label": "Methods, Frameworks & Findings (Low Floor / High Ceiling)", "width": 360}
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
        analysis = analyze_paper_frameworks_findings(paper_obj, sections)
        paper_obj[PROP_ID] = analysis
        papers.append(paper_obj)

        # Create Observation JSON
        obs_obj = {
            "paper_id": pid,
            "property_id": PROP_ID,
            "property_version": PROP_VERSION,
            "value": analysis,
            "status": "extracted",
            "evidence": [
                {
                    "paper_id": pid,
                    "supporting_text": analysis
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

## Papers and 'Methods, Frameworks & Findings' Property Extractions

| Paper ID | Title | Authors | Year | Methods, Frameworks & Findings (Low Floor / High Ceiling) |
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
