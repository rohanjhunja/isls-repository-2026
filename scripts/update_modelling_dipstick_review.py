import sqlite3
import json
import re
import os
import sys
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from proceedings_ingest.utils.text_cleanup import repair_title_and_authors

REVIEW_ID = "rev_dipstick_af404c7e"
PROP_ID = "modelling_usage"
PROP_VERSION = "1.0.0"

def synthesize_paper_modelling(pid, title, abstract):
    text = f"{title}. {abstract}"
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    m_sents = [s for s in sents if re.search(r'\b(model|models|modeling|modelling|modeled|modelled)\b', s, re.I)]
    
    # Extract abstract-specific matches for richer evidence if available
    abstract_sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', abstract) if s.strip()]
    abstract_m_sents = [s for s in abstract_sents if re.search(r'\b(model|models|modeling|modelling|modeled|modelled)\b', s, re.I)]

    if abstract_m_sents:
        # Pick the most informative abstract sentence
        best_sent = abstract_m_sents[0]
        for s in abstract_m_sents:
            if len(s) > len(best_sent):
                best_sent = s
    elif m_sents:
        best_sent = m_sents[0]
    else:
        best_sent = title

    clean_quote = best_sent.replace("\n", " ").strip()
    if len(clean_quote) > 190:
        clean_quote = clean_quote[:187] + "..."

    # Check Paradigms in priority order
    if re.search(r'\b(foundation|foundational|generative ai|llm|large language|chatgpt)\b.*\b(model|models|modeling|modelling)\b', text, re.I):
        paradigm = "AI & Foundation Models"
        focus = "Investigates foundational text generation and large language model architectures to examine AI literacy, model transparency, and learner interactions."
    elif re.search(r'\b(embodied|embodiment|mixed reality|virtual reality|\bmr\b|\bvr\b|dance|role-play|physical movement)\b.*\b(model|models|modeling|modelling)\b', text, re.I):
        paradigm = "Embodied & Participatory Modeling"
        focus = "Leverages embodied, mixed-reality, or physical role-play activities to ground learners' sense-making and computational modeling of complex systems."
    elif re.search(r'\b(structural equation|\bsem\b|multilevel|hierarchical linear|markov|\bena\b|epistemic network|predictive|regression|statistical|quantitative|transactivity|latent class|machine learning|topic model)\b[a-z\s\-]*\b(model|models|modeling|modelling)\b', text, re.I) or re.search(r'\b(model|models|modeling|modelling)\b[a-z\s\-]*\b(sem|markov|multilevel|regression|predictive|statistical|transactivity)\b', text, re.I):
        paradigm = "Statistical, Machine Learning & Quantitative Modeling"
        focus = "Applies quantitative, statistical, or machine learning models (e.g., SEM, multilevel analysis, Markov, or network modeling) to examine learning processes and empirical outcomes."
    elif re.search(r'\b(agent-based|abm|netlogo|block-based|computational|simulation|programmable|programming|coding|computational thinking)\b[a-z\s\-]*\b(model|models|modeling|modelling)\b', text, re.I) or re.search(r'\b(model|models|modeling|modelling)\b[a-z\s\-]*\b(code|coding|netlogo|agent-based|simulation|block-based|programming)\b', text, re.I):
        paradigm = "Computational & Agent-Based Modeling"
        focus = "Engages students in constructing, programming, or debugging computational and agent-based simulation models to explore dynamic scientific or social phenomena."
    elif re.search(r'\b(model|models|modeling|modelling)\b[a-z\s\-]*\b(tool|tools|software|environment|environments|platform|automated feedback|scaffold|meme)\b', text, re.I):
        paradigm = "Learning Technologies & Modeling Environments"
        focus = "Examines software environments, automated feedback systems, or digital scaffolding designed to facilitate iterative student modeling practices."
    elif re.search(r'\b(scientific|explanatory|science|inquiry|phenomenon|phenomena|cellular|genetics|biology|chemistry|physics|ecosystem|diffusion)\b[a-z\s\-]*\b(model|models|modeling|modelling|model-based)\b', text, re.I) or re.search(r'\b(model|models|modeling|modelling)\b[a-z\s\-]*\b(practice|practices|inquiry|scientific|evidence|revision|evaluate|critique|natural world)\b', text, re.I):
        paradigm = "Scientific Inquiry & Explanatory Modeling"
        focus = "Focuses on student practices of generating, testing, evaluating, and iteratively revising explanatory scientific models using empirical evidence."
    elif re.search(r'\b(dialogue|dialogues|facilitat|instructor|teacher|peer|collaborat|discourse|intergroup)\b[a-z\s\-]*\b(model|models|modeling|modelling)\b', text, re.I) or re.search(r'\b(model|models|modeling|modelling)\b[a-z\s\-]*\b(dialogue|dialogues|facilitat|discourse|interaction|intergroup)\b', text, re.I):
        paradigm = "Pedagogical & Collaborative Dialogue Modeling"
        focus = "Examines how pedagogical facilitation, instructor moves, or collaborative tools model productive discourse and interpersonal inquiry strategies."
    elif re.search(r'\b(data|storytelling|socioeconomic|unstructured)\b[a-z\s\-]*\b(model|models|modeling|modelling)\b', text, re.I):
        paradigm = "Data & Comparative Modeling"
        focus = "Investigates how learners build comparative models from large, unstructured, or socioeconomic datasets to construct evidence-based narratives."
    elif re.search(r'\b(mathematical|spatial|3d|cad|geometry|chance)\b[a-z\s\-]*\b(model|models|modeling|modelling)\b', text, re.I):
        paradigm = "Mathematical & Digital Design Modeling"
        focus = "Engages students in mathematical, probabilistic, or 3D digital design modeling to develop spatial and quantitative reasoning."
    else:
        paradigm = "Conceptual & Theoretical Modeling"
        focus = "Proposes or applies a conceptual framework or theoretical model to structure understanding of learning mechanisms, collaboration, or disciplinary practices."

    cell_value = f"**{paradigm}**: {focus} Evidence: \"{clean_quote}\""
    return paradigm, cell_value, clean_quote

def main():
    db_path = "proceedings.db"
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    review_path = f"data/reviews/{REVIEW_ID}.json"
    if not os.path.exists(review_path):
        print(f"Error: {review_path} not found.")
        return

    with open(review_path, "r", encoding="utf-8") as f:
        review_data = json.load(f)

    paper_ids = review_data.get("paper_ids", [])
    print(f"Processing {len(paper_ids)} papers for review {REVIEW_ID}...")

    obs_dir = "data/observations"
    os.makedirs(obs_dir, exist_ok=True)

    paper_objects = []

    for pid in paper_ids:
        cursor.execute("SELECT id, title, abstract, year, conference, paper_type, handle_url, doi FROM papers WHERE id = ?", (pid,))
        p_row = cursor.fetchone()
        if not p_row:
            cursor.execute("SELECT id, title, abstract, year, conference, paper_type, handle_url, doi FROM papers WHERE id LIKE ? OR handle_url LIKE ?", (f"%{pid}%", f"%{pid}%"))
            p_row = cursor.fetchone()

        if not p_row:
            print(f"Warning: paper {pid} not found in database.")
            continue

        actual_id = p_row[0]
        raw_title = p_row[1] or ""
        abstract = p_row[2] or ""
        year = p_row[3] or ""
        conf = p_row[4] or "ISLS"
        paper_type = p_row[5] or "Paper"
        handle_url = p_row[6] or ""
        doi = p_row[7] or ""

        # Fetch authors
        cursor.execute("""
            SELECT a.display_name FROM authors a
            JOIN paper_authors pa ON pa.author_id = a.id
            WHERE pa.paper_id = ?
            ORDER BY pa.author_order ASC
        """, (actual_id,))
        author_rows = cursor.fetchall()
        raw_authors = ", ".join([ar[0] for ar in author_rows])

        # Clean title & authors
        c_title, c_authors = repair_title_and_authors(raw_title, raw_authors, abstract)

        # Synthesize modelling usage
        paradigm, cell_value, quote = synthesize_paper_modelling(actual_id, c_title, abstract)

        paper_obj = {
            "id": actual_id,
            "title": c_title,
            "authors": c_authors,
            "year": year,
            "conference": conf,
            PROP_ID: cell_value,
            "abstract": abstract,
            "paper_type": paper_type,
            "handle_url": handle_url,
            "doi": doi
        }
        paper_objects.append(paper_obj)

        # Write observation JSON file
        obs_obj = {
            "paper_id": actual_id,
            "property_id": PROP_ID,
            "property_version": PROP_VERSION,
            "value": cell_value,
            "status": "extracted",
            "evidence": [
                {
                    "paper_id": actual_id,
                    "supporting_text": quote
                }
            ],
            "method": "title_abstract_modelling_synthesis",
            "confidence": 1.0,
            "run_id": f"run_{PROP_ID}_20260909",
            "source_version": "1.0.0"
        }
        obs_path = os.path.join(obs_dir, f"{actual_id}_{PROP_ID}.json")
        with open(obs_path, "w", encoding="utf-8") as f:
            json.dump(obs_obj, f, indent=2)

    conn.close()

    # 1. Update Review JSON
    now_iso = datetime.datetime.now().isoformat()
    review_data["updated_at"] = now_iso

    sel_cols = ["title", "year", "conference", "authors", PROP_ID, "abstract"]
    review_data["selected_columns"] = sel_cols
    review_data["visible_columns"] = sel_cols

    col_defs = {
        "title": {"label": "Paper Title", "width": 260},
        "authors": {"label": "Authors", "width": 180},
        "year": {"label": "Year", "width": 80},
        "conference": {"label": "Conference", "width": 100},
        PROP_ID: {"label": "How Modelling is Used", "width": 380},
        "abstract": {"label": "Abstract", "width": 340}
    }
    review_data["column_definitions"] = col_defs

    if "property_versions" not in review_data:
        review_data["property_versions"] = {}
    review_data["property_versions"][PROP_ID] = PROP_VERSION

    review_data["papers"] = paper_objects
    review_data["matched_paper_count"] = len(paper_objects)

    with open(review_path, "w", encoding="utf-8") as f:
        json.dump(review_data, f, indent=2)
    print(f"Updated {review_path} with {len(paper_objects)} papers and '{PROP_ID}' column.")

    # 2. Update Derived Reviews Cache
    cache_dir = "data/derived/reviews_cache"
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"{REVIEW_ID}.json")
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(review_data, f, indent=2)
    print(f"Updated cache: {cache_file}")

    # 3. Update Manifest in Cache
    manifest_file = os.path.join(cache_dir, "manifest.json")
    manifest = []
    if os.path.exists(manifest_file):
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)

    updated_manifest = False
    for item in manifest:
        if item.get("id") == REVIEW_ID:
            item["name"] = review_data.get("name")
            item["description"] = review_data.get("description")
            item["selected_columns"] = sel_cols
            item["visible_columns"] = sel_cols
            item["column_definitions"] = col_defs
            item["updated_at"] = now_iso
            item["paper_count"] = len(paper_objects)
            updated_manifest = True
            break

    if not updated_manifest:
        manifest.append({
            "id": REVIEW_ID,
            "name": review_data.get("name"),
            "description": review_data.get("description"),
            "created_at": review_data.get("created_at"),
            "updated_at": now_iso,
            "paper_count": len(paper_objects),
            "selected_columns": sel_cols,
            "visible_columns": sel_cols,
            "column_definitions": col_defs
        })

    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Updated cache manifest: {manifest_file}")

    # 4. Update Markdown Summary File
    md_path = f"data/reviews/{REVIEW_ID}.md"
    md_content = f"""# Literature Review: {review_data.get('name')}

- **Review ID**: `{REVIEW_ID}`
- **Created At**: `{review_data.get('created_at')}`
- **Updated At**: `{review_data.get('updated_at')}`
- **Matching Papers**: {len(paper_objects)}
- **Selected Columns**: {', '.join(sel_cols)}
- **Keywords**: {', '.join(review_data.get('keywords', []))}

## Web Viewer Launch Link

[🚀 Launch Interactive Web Viewer for this Review](http://localhost:8888/?review={REVIEW_ID})

## Papers and 'How Modelling is Used' Property Extractions

| Paper ID | Title | Authors | Year | Conference | How Modelling is Used |
| --- | --- | --- | --- | --- | --- |
"""
    for p in paper_objects:
        clean_exp = p[PROP_ID].replace("|", "\\|").replace("\n", " ")
        clean_title = p["title"].replace("|", "\\|").replace("\n", " ")
        clean_authors = str(p["authors"]).replace("|", "\\|").replace("\n", " ")
        md_content += f"| `{p['id']}` | {clean_title} | {clean_authors} | {p['year']} | {p['conference']} | {clean_exp} |\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Updated Markdown summary: {md_path}")

if __name__ == "__main__":
    main()
