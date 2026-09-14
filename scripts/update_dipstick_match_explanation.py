import os
import json
import re
import datetime
import sqlite3

REVIEW_ID = "rev_dipstick_2c2e4af5"
PROP_ID = "match_explanation"
PROP_VERSION = "1.0.0"

def get_sentence_with_keyword(text, kw):
    if not text:
        return ""
    pattern = re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    for sentence in sentences:
        if pattern.search(sentence):
            s_clean = sentence.strip()
            if len(s_clean) > 160:
                m = pattern.search(s_clean)
                start = max(0, m.start() - 40)
                end = min(len(s_clean), m.end() + 80)
                sub = s_clean[start:end]
                if start > 0: sub = "..." + sub
                if end < len(s_clean): sub = sub + "..."
                return sub
            return s_clean
    return ""

def generate_match_explanation(paper, keywords):
    title = paper.get("title", "")
    abstract = paper.get("abstract", "")
    
    matched_title_kws = []
    matched_abs_kws = []
    snippets = []

    for kw in keywords:
        pattern = re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
        title_hit = pattern.search(title)
        abs_hit = pattern.search(abstract) if abstract else None
        
        if title_hit:
            matched_title_kws.append(kw)
        if abs_hit:
            matched_abs_kws.append(kw)
            sent = get_sentence_with_keyword(abstract, kw)
            if sent and sent not in snippets:
                snippets.append(f"\"{sent}\"")

    explanation_parts = []
    if matched_title_kws:
        k_str = ", ".join([f"'{k}'" for k in matched_title_kws])
        explanation_parts.append(f"Title explicitly mentions {k_str}")
    if matched_abs_kws:
        k_str = ", ".join([f"'{k}'" for k in matched_abs_kws])
        explanation_parts.append(f"Abstract discusses {k_str}")
        
    if not explanation_parts:
        return "Matches target keywords in paper text."

    summary_header = "; ".join(explanation_parts) + "."
    if snippets:
        summary_header += " Evidence: " + " ".join(snippets[:2])
        
    return summary_header

def update_review_data():
    review_path = f"data/reviews/{REVIEW_ID}.json"
    if not os.path.exists(review_path):
        print(f"Error: {review_path} not found")
        return

    with open(review_path, "r", encoding="utf-8") as f:
        review_data = json.load(f)

    keywords = review_data.get("keywords", [])
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

    col_defs = review_data.get("column_definitions", {
        "title": {"label": "Paper Title", "width": 260},
        "authors": {"label": "Authors", "width": 180},
        "year": {"label": "Year", "width": 80},
        "conference": {"label": "Conference", "width": 100},
        "abstract": {"label": "Abstract", "width": 340}
    })
    col_defs[PROP_ID] = {"label": "Keyword Match Explanation", "width": 320}
    review_data["column_definitions"] = col_defs

    if "property_versions" not in review_data:
        review_data["property_versions"] = {}
    review_data["property_versions"][PROP_ID] = PROP_VERSION
    review_data["updated_at"] = datetime.datetime.now().isoformat()

    # Query DB directly for paper_ids
    db_path = "data/index/proceedings.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    papers = []
    obs_dir = "data/observations"
    os.makedirs(obs_dir, exist_ok=True)

    for pid in paper_ids:
        row = cursor.execute("SELECT data_json FROM papers WHERE id = ?", (pid,)).fetchone()
        if not row or not row[0]:
            continue
        db_data = json.loads(row[0])
        
        raw_authors = ", ".join([a.get('display_name', '') if isinstance(a, dict) else str(a) for a in db_data.get('authors', [])])
        conf = db_data.get('conference', {}).get('acronym', 'ISLS') if isinstance(db_data.get('conference'), dict) else 'ISLS'

        paper_info = {
            "id": pid,
            "title": db_data.get("title", pid),
            "authors": raw_authors,
            "year": db_data.get("year", ""),
            "conference": conf,
            "abstract": db_data.get("abstract", "")
        }

        match_exp = generate_match_explanation(paper_info, keywords)
        
        paper_obj = {
            "id": pid,
            "title": paper_info["title"],
            "authors": paper_info["authors"],
            "year": paper_info["year"],
            "conference": paper_info["conference"],
            "abstract": paper_info["abstract"],
            PROP_ID: match_exp
        }
        papers.append(paper_obj)

        # Create Observation JSON
        obs_obj = {
            "paper_id": pid,
            "property_id": PROP_ID,
            "property_version": PROP_VERSION,
            "value": match_exp,
            "status": "extracted",
            "evidence": [
                {
                    "paper_id": pid,
                    "supporting_text": match_exp
                }
            ],
            "method": "keyword_context_match",
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
    print(f"Updated {review_path} with {len(papers)} papers and '{PROP_ID}' column.")

    # 3. Update derived reviews cache
    cache_dir = "data/derived/reviews_cache"
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"{REVIEW_ID}.json")
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(review_data, f, indent=2)
    print(f"Updated {cache_file}")

    # Update manifest.json
    manifest_file = os.path.join(cache_dir, "manifest.json")
    manifest = []
    if os.path.exists(manifest_file):
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    
    updated_manifest = False
    for item in manifest:
        if item.get("id") == REVIEW_ID:
            item["selected_columns"] = sel_cols
            item["column_definitions"] = col_defs
            item["updated_at"] = review_data["updated_at"]
            item["paper_count"] = len(papers)
            updated_manifest = True
            break
            
    if not updated_manifest:
        manifest.append({
            "id": REVIEW_ID,
            "name": review_data.get("name"),
            "description": review_data.get("description"),
            "created_at": review_data.get("created_at"),
            "updated_at": review_data["updated_at"],
            "paper_count": len(papers),
            "selected_columns": sel_cols,
            "column_definitions": col_defs
        })
        
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Updated {manifest_file}")

    # 4. Update Markdown summary file
    md_path = f"data/reviews/{REVIEW_ID}.md"
    md_content = f"""# Literature Review: {review_data.get('name')}

- **Review ID**: `{REVIEW_ID}`
- **Created At**: `{review_data.get('created_at')}`
- **Updated At**: `{review_data.get('updated_at')}`
- **Matching Papers**: {len(papers)}
- **Selected Columns**: {', '.join(sel_cols)}
- **Keywords**: {', '.join(keywords)}

## Web Viewer Launch Link

[🚀 Launch Interactive Web Viewer for this Review](http://localhost:8888/?review={REVIEW_ID})

## Papers and 'Keyword Match Explanation' Property Extractions

| Paper ID | Title | Authors | Year | Conference | Keyword Match Explanation |
| --- | --- | --- | --- | --- | --- |
"""
    for p in papers:
        clean_exp = p[PROP_ID].replace("|", "\\|").replace("\n", " ")
        clean_title = p["title"].replace("|", "\\|").replace("\n", " ")
        clean_authors = p["authors"].replace("|", "\\|").replace("\n", " ")
        md_content += f"| `{p['id']}` | {clean_title} | {clean_authors} | {p['year']} | {p['conference']} | {clean_exp} |\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Updated {md_path}")

if __name__ == "__main__":
    update_review_data()
