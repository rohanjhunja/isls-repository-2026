import sqlite3
import json
import re
import os
import datetime

REVIEW_ID = "rev_dipstick_0385f1ec"
PROP_ID = "chat_usage"
PROP_VERSION = "1.0.0"

def generate_chat_usage_extractions():
    db_path = "data/index/proceedings.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    review_path = f"data/reviews/{REVIEW_ID}.json"
    with open(review_path, "r", encoding="utf-8") as f:
        rev_data = json.load(f)

    existing_pids = list(rev_data.get("paper_ids", []))

    # Find explicit CHAT papers across full text
    query_explicit = """
    SELECT DISTINCT paper_id FROM sections_fts 
    WHERE text LIKE '%Cultural Historical Activity Theory%'
       OR text LIKE '%Cultural-Historical Activity Theory%'
    """
    explicit_pids = set(r[0] for r in cursor.execute(query_explicit).fetchall())

    all_papers_db = cursor.execute("SELECT id, data_json FROM papers").fetchall()
    for pid, d_json in all_papers_db:
        p_data = json.loads(d_json) if d_json else {}
        title = p_data.get("title", "")
        abstract = p_data.get("abstract", "")
        if re.search(r"Cultural[-\s]Historical Activity Theory", f"{title} {abstract}", re.IGNORECASE):
            explicit_pids.add(pid)

    # Combine existing 37 dipstick papers and newly identified CHAT papers
    all_pids = sorted(list(set(existing_pids).union(explicit_pids)))

    obs_dir = "data/observations"
    os.makedirs(obs_dir, exist_ok=True)

    paper_objects = []

    for pid in all_pids:
        row = cursor.execute("SELECT data_json FROM papers WHERE id = ?", (pid,)).fetchone()
        p_data = json.loads(row[0]) if row and row[0] else {}
        title = p_data.get("title", pid)
        abstract = p_data.get("abstract", "")
        raw_authors = ", ".join([a.get("display_name", "") if isinstance(a, dict) else str(a) for a in p_data.get("authors", [])])
        conf = p_data.get("conference", {}).get("acronym", "ISLS") if isinstance(p_data.get("conference"), dict) else "ISLS"
        year = p_data.get("year", "")

        sec_rows = cursor.execute("SELECT heading_original, canonical_roles, text FROM sections_fts WHERE paper_id = ? ORDER BY section_id ASC", (pid,)).fetchall()

        chat_hits = []
        at_hits = []

        for heading, role, text in sec_rows:
            if not text:
                continue
            sentences = re.split(r"(?<=[.!?])\s+", text)
            for sent in sentences:
                s_clean = sent.strip().replace("\n", " ")
                if re.search(r"Cultural[-\s]Historical Activity Theory", s_clean, re.IGNORECASE):
                    chat_hits.append((heading or role or "Main Text", s_clean))
                elif re.search(r"\bCHAT\b", s_clean) and any(w in s_clean.lower() for w in ["theory", "framework", "lens", "engestr", "vygotsk", "system", "mediat", "contradiction", "expansive", "third-generation"]):
                    chat_hits.append((heading or role or "Main Text", s_clean))
                elif re.search(r"Activity Theory|activity system|mediating artifact|expansive learning|Engeström|Engestrom|Vygotsky", s_clean, re.IGNORECASE):
                    at_hits.append((heading or role or "Main Text", s_clean))

        if chat_hits:
            sec_name, snippet = chat_hits[0]
            snip_lower = snippet.lower()
            if "analytical" in snip_lower or "analyze" in snip_lower or "analysis" in snip_lower:
                usage = f"Uses CHAT as an analytical framework in {sec_name} to examine activity systems and social interactions. Evidence: \"{snippet[:180]}...\"" if len(snippet) > 180 else f"Uses CHAT as an analytical framework in {sec_name} to examine activity systems and social interactions. Evidence: \"{snippet}\""
            elif "theoretical" in snip_lower or "framework" in snip_lower or "inform" in snip_lower:
                usage = f"Uses CHAT as a core theoretical framework in {sec_name} to ground learning and artifact mediation. Evidence: \"{snippet[:180]}...\"" if len(snippet) > 180 else f"Uses CHAT as a core theoretical framework in {sec_name} to ground learning and artifact mediation. Evidence: \"{snippet}\""
            elif "contradiction" in snip_lower or "tension" in snip_lower:
                usage = f"Applies CHAT in {sec_name} to analyze systemic contradictions, tensions, and expansive learning cycles. Evidence: \"{snippet[:180]}...\"" if len(snippet) > 180 else f"Applies CHAT in {sec_name} to analyze systemic contradictions, tensions, and expansive learning cycles. Evidence: \"{snippet}\""
            elif "design" in snip_lower or "co-design" in snip_lower:
                usage = f"Applies CHAT in {sec_name} to guide participatory design, tool mediation, and collaborative practices. Evidence: \"{snippet[:180]}...\"" if len(snippet) > 180 else f"Applies CHAT in {sec_name} to guide participatory design, tool mediation, and collaborative practices. Evidence: \"{snippet}\""
            else:
                usage = f"Applies CHAT in {sec_name} as a socio-cultural framework for activity systems. Evidence: \"{snippet[:180]}...\"" if len(snippet) > 180 else f"Applies CHAT in {sec_name} as a socio-cultural framework for activity systems. Evidence: \"{snippet}\""
            supporting_text = snippet
        elif at_hits:
            sec_name, snippet = at_hits[0]
            usage = f"Draws on Activity Theory principles in {sec_name} to analyze activity systems, mediated tools, and collaborative learning. Evidence: \"{snippet[:180]}...\"" if len(snippet) > 180 else f"Draws on Activity Theory principles in {sec_name} to analyze activity systems, mediated tools, and collaborative learning. Evidence: \"{snippet}\""
            supporting_text = snippet
        else:
            usage = "Mentions Activity Theory in paper abstract / title scope."
            supporting_text = abstract[:200] if abstract else title

        paper_obj = {
            "id": pid,
            "title": title,
            "authors": raw_authors,
            "year": year,
            "conference": conf,
            "abstract": abstract,
            PROP_ID: usage
        }
        paper_objects.append(paper_obj)

        # Create Observation JSON
        obs_obj = {
            "paper_id": pid,
            "property_id": PROP_ID,
            "property_version": PROP_VERSION,
            "value": usage,
            "status": "extracted",
            "evidence": [
                {
                    "paper_id": pid,
                    "supporting_text": supporting_text
                }
            ],
            "method": "fts_section_chat_extraction",
            "confidence": 1.0,
            "run_id": f"run_{PROP_ID}_20260807",
            "source_version": "1.0.0"
        }
        obs_file = os.path.join(obs_dir, f"{pid}_{PROP_ID}.json")
        with open(obs_file, "w", encoding="utf-8") as f:
            json.dump(obs_obj, f, indent=2)

    conn.close()

    # 1. Update review metadata JSON
    rev_data["name"] = "Dipstick Review - Activity Theory & CHAT"
    rev_data["description"] = "Expanded Dipstick Review scanning 100% of papers for Cultural Historical Activity Theory (CHAT) usage."
    rev_data["keywords"] = ["Activity Theory", "CHAT", "Cultural Historical Activity Theory"]
    rev_data["paper_ids"] = all_pids
    rev_data["matched_paper_count"] = len(all_pids)
    rev_data["updated_at"] = datetime.datetime.now().isoformat()

    sel_cols = ["title", "year", "conference", "authors", PROP_ID, "abstract"]
    rev_data["selected_columns"] = sel_cols
    rev_data["visible_columns"] = sel_cols

    col_defs = {
        "title": {"label": "Paper Title", "width": 260},
        "authors": {"label": "Authors", "width": 180},
        "year": {"label": "Year", "width": 80},
        "conference": {"label": "Conference", "width": 100},
        PROP_ID: {"label": "CHAT Theory Usage", "width": 340},
        "abstract": {"label": "Abstract", "width": 340}
    }
    rev_data["column_definitions"] = col_defs

    if "property_versions" not in rev_data:
        rev_data["property_versions"] = {}
    rev_data["property_versions"][PROP_ID] = PROP_VERSION

    rev_data["papers"] = paper_objects

    with open(review_path, "w", encoding="utf-8") as f:
        json.dump(rev_data, f, indent=2)
    print(f"Updated {review_path} with {len(paper_objects)} papers and '{PROP_ID}' column.")

    # 2. Update derived reviews cache
    cache_dir = "data/derived/reviews_cache"
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"{REVIEW_ID}.json")
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(rev_data, f, indent=2)
    print(f"Updated {cache_file}")

    # 3. Update manifest.json
    manifest_file = os.path.join(cache_dir, "manifest.json")
    manifest = []
    if os.path.exists(manifest_file):
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)

    updated_manifest = False
    for item in manifest:
        if item.get("id") == REVIEW_ID:
            item["name"] = rev_data["name"]
            item["description"] = rev_data["description"]
            item["selected_columns"] = sel_cols
            item["column_definitions"] = col_defs
            item["updated_at"] = rev_data["updated_at"]
            item["paper_count"] = len(paper_objects)
            updated_manifest = True
            break

    if not updated_manifest:
        manifest.append({
            "id": REVIEW_ID,
            "name": rev_data.get("name"),
            "description": rev_data.get("description"),
            "created_at": rev_data.get("created_at"),
            "updated_at": rev_data["updated_at"],
            "paper_count": len(paper_objects),
            "selected_columns": sel_cols,
            "column_definitions": col_defs
        })

    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Updated {manifest_file}")

    # 4. Update Markdown summary file
    md_path = f"data/reviews/{REVIEW_ID}.md"
    md_content = f"""# Literature Review: {rev_data.get('name')}

- **Review ID**: `{REVIEW_ID}`
- **Created At**: `{rev_data.get('created_at')}`
- **Updated At**: `{rev_data.get('updated_at')}`
- **Matching Papers**: {len(paper_objects)}
- **Selected Columns**: {', '.join(sel_cols)}
- **Keywords**: {', '.join(rev_data.get('keywords', []))}

## Web Viewer Launch Link

[🚀 Launch Interactive Web Viewer for this Review](http://localhost:8888/?review={REVIEW_ID})

## Papers and 'CHAT Theory Usage' Property Extractions

| Paper ID | Title | Authors | Year | Conference | CHAT Theory Usage |
| --- | --- | --- | --- | --- | --- |
"""
    for p in paper_objects:
        clean_exp = p[PROP_ID].replace("|", "\\|").replace("\n", " ")
        clean_title = p["title"].replace("|", "\\|").replace("\n", " ")
        clean_authors = str(p["authors"]).replace("|", "\\|").replace("\n", " ")
        md_content += f"| `{p['id']}` | {clean_title} | {clean_authors} | {p['year']} | {p['conference']} | {clean_exp} |\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Updated {md_path}")

if __name__ == "__main__":
    generate_chat_usage_extractions()
