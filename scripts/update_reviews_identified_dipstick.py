import os
import json
import re
import datetime
import sqlite3

REVIEW_ID = "rev_dipstick_8bd32a4b"
PROP_ID = "reviews_identified"
PROP_VERSION = "1.0.0"

REVIEW_INDICATORS = [
    r"\breviews?\b",
    r"\bmeta-analys",
    r"\bsystematic review\b",
    r"\bscoping review\b",
    r"\bliterature review\b",
    r"\bsynthesis\b",
    r"\bsurvey\b",
    r"\bstate of the art\b",
    r"\breview of educational research\b",
    r"\bharvard educational review\b",
    r"\beducational research review\b",
    r"\bannual review\b",
    r"\beducational psychology review\b",
    r"\bacademy of management review\b",
    r"\breview of research in education\b"
]

def get_reference_text(data):
    sections = data.get("sections", [])
    ref_texts = []
    for s in sections:
        ho = str(s.get("heading_original") or "")
        hn = str(s.get("heading_normalized") or "")
        if any(term in ho.lower() or term in hn.lower() for term in ["reference", "citation", "bibliography", "works cited"]):
            ref_texts.append(s.get("text", ""))
    if ref_texts:
        return "\n".join(ref_texts)
        
    full_text = "\n".join([s.get("text", "") for s in sections])
    m = re.search(r"(?:\n|\A)\s*(?:#+\s*)?(?:References|REFERENCES|Bibliography|Citations)\s*(?:\n|\Z)", full_text)
    if m:
        return full_text[m.start():]
        
    if sections:
        return sections[-1].get("text", "")
    return ""

def clean_reference(ref):
    return re.sub(r"\s+", " ", ref).strip()

def split_references(ref_text):
    ref_text = re.sub(r"^\s*(?:#+\s*)?(?:References|REFERENCES|Bibliography|Citations)\s*", "", ref_text)
    ack_match = re.search(r"\n\s*(?:#+\s*)?(?:Acknowledgements?|ACKNOWLEDGEMENTS?)\s*\n", ref_text)
    if ack_match:
        ref_text = ref_text[:ack_match.start()]
        
    ack_match2 = re.search(r"\b(?:Acknowledgements?|ACKNOWLEDGEMENTS?)\b", ref_text)
    if ack_match2 and ack_match2.start() > len(ref_text) * 0.7:
        ref_text = ref_text[:ack_match2.start()]

    lines = ref_text.split("\n")
    entries = []
    curr = []
    ref_start_pattern = re.compile(
        r"^(?:\[\d+\]|\d+\.|\b[A-Z][a-zA-Z\-\'\s]+,\s+[A-Z]\.|\b[A-Z][a-zA-Z\-\'\s]+,\s+[A-Z][a-z]+)"
    )
    for line in lines:
        line_s = line.strip()
        if not line_s:
            if curr:
                entries.append(" ".join(curr))
                curr = []
        elif curr and ref_start_pattern.match(line_s):
            entries.append(" ".join(curr))
            curr = [line_s]
        else:
            curr.append(line_s)
    if curr:
        entries.append(" ".join(curr))
        
    cleaned = []
    for e in entries:
        c = clean_reference(e)
        if len(c) > 15:
            cleaned.append(c)
    return cleaned

def is_possibly_review_paper(ref_clean):
    ref_lower = ref_clean.lower()
    for pat in REVIEW_INDICATORS:
        if re.search(pat, ref_lower):
            return True
    return False

def format_apa_citation(ref_clean):
    ref_stripped = re.sub(r"^(?:\[\d+\]|\d+\.)\s*", "", ref_clean).strip()
    return ref_stripped

def extract_reviews_identified_for_paper(data):
    rt = get_reference_text(data)
    refs = split_references(rt)
    apa_matches = []
    for r in refs:
        r_clean = clean_reference(r)
        if len(r_clean) < 15:
            continue
        if "This dissertation employs" in r_clean or "Abstract" in r_clean:
            continue
        if is_possibly_review_paper(r_clean):
            apa = format_apa_citation(r_clean)
            if apa not in apa_matches:
                apa_matches.append(apa)
    return apa_matches

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
    if "review_citations" in sel_cols:
        sel_cols.remove("review_citations")
    if PROP_ID not in sel_cols:
        if "abstract" in sel_cols:
            idx = sel_cols.index("abstract")
            sel_cols.insert(idx, PROP_ID)
        else:
            sel_cols.append(PROP_ID)
    review_data["selected_columns"] = sel_cols

    vis_cols = review_data.get("visible_columns", [])
    if "review_citations" in vis_cols:
        vis_cols.remove("review_citations")
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
    if "review_citations" in col_defs:
        del col_defs["review_citations"]
    col_defs[PROP_ID] = {"label": "Reviews Identified", "width": 380}
    review_data["column_definitions"] = col_defs

    if "property_versions" not in review_data:
        review_data["property_versions"] = {}
    if "review_citations" in review_data["property_versions"]:
        del review_data["property_versions"]["review_citations"]
    review_data["property_versions"][PROP_ID] = PROP_VERSION
    review_data["updated_at"] = datetime.datetime.now().isoformat()

    db_path = "data/index/proceedings.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    papers = []
    obs_dir = "data/observations"
    os.makedirs(obs_dir, exist_ok=True)

    matching_papers_count = 0

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

        matched_apa_citations = extract_reviews_identified_for_paper(db_data)
        if matched_apa_citations:
            val_str = " | ".join(matched_apa_citations)
            status_str = "extracted"
            matching_papers_count += 1
        else:
            val_str = "None found"
            status_str = "not_present"

        paper_obj = {
            "id": pid,
            "title": paper_info["title"],
            "authors": paper_info["authors"],
            "year": paper_info["year"],
            "conference": paper_info["conference"],
            "abstract": paper_info["abstract"],
            PROP_ID: val_str
        }
        papers.append(paper_obj)

        obs_obj = {
            "paper_id": pid,
            "property_id": PROP_ID,
            "property_version": PROP_VERSION,
            "value": val_str,
            "status": status_str,
            "evidence": [
                {
                    "paper_id": pid,
                    "supporting_text": val_str
                }
            ],
            "method": "section_parsing",
            "confidence": 1.0,
            "run_id": f"run_{PROP_ID}_20260807",
            "source_version": "1.0.0"
        }
        obs_file = os.path.join(obs_dir, f"{pid}_{PROP_ID}.json")
        with open(obs_file, "w", encoding="utf-8") as f:
            json.dump(obs_obj, f, indent=2)

    conn.close()
    review_data["papers"] = papers

    with open(review_path, "w", encoding="utf-8") as f:
        json.dump(review_data, f, indent=2)
    print(f"Updated {review_path} with {len(papers)} papers ({matching_papers_count} containing Reviews Identified).")

    cache_dir = "data/derived/reviews_cache"
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"{REVIEW_ID}.json")
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(review_data, f, indent=2)
    print(f"Updated {cache_file}")

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

    md_path = f"data/reviews/{REVIEW_ID}.md"
    md_content = f"""# Literature Review: {review_data.get('name')}

- **Review ID**: `{REVIEW_ID}`
- **Created At**: `{review_data.get('created_at')}`
- **Updated At**: `{review_data.get('updated_at')}`
- **Total Papers**: {len(papers)}
- **Papers with Reviews Identified**: {matching_papers_count}
- **Selected Columns**: {', '.join(sel_cols)}
- **Keywords**: {', '.join(keywords)}

## Web Viewer Launch Link

[🚀 Launch Interactive Web Viewer for this Review](http://localhost:8888/?review={REVIEW_ID})

## Papers and 'Reviews Identified' Extractions

| Paper ID | Title | Authors | Year | Conference | Reviews Identified |
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
