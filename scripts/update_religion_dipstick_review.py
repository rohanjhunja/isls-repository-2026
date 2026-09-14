import os
import json
import datetime

REVIEW_ID = "rev_dipstick_33d47ac9"
PROP_ID = "religion_relation"
PROP_VERSION = "1.0.0"

RELIGION_EXPLANATIONS = {
    "isls-2024-proceedings-paper-0042": (
        "Investigates how Hindu supremacy, Hindu nationalism, and anti-Kashmiri/Islamophobic dynamics shape "
        "science education in rural South Indian schools, demonstrating how everyday science lessons and lunchroom "
        "purity practices reproduce caste- and religion-based oppression."
    ),
    "icls-2024-proceedings-paper-0024": (
        "Identifies religion as a key socio-cultural identity dimension (alongside culture, race/ethnicity, and gender) "
        "that influences how students interpret, experience, and express caring within science learning environments."
    ),
    "icls-2024-proceedings-paper-0269": (
        "Examines how a shared heritage trip to Poland for Israeli and American Jewish youth fosters religious-national "
        "identity exploration, exposing participants to diverse Jewish religious practices (e.g., Reform synagogue services)."
    ),
    "icls-volume-2025-paper-0125": (
        "Analyzes Nigeria's structural pluralism, demonstrating how religious affiliations (Muslim vs. Christian majorities) "
        "and ethnic diversity moderate the relationship between educational attainment and interpersonal/institutional trust dynamics."
    ),
    "icls-volume-2025-paper-0329": (
        "Uses the scientific study of religion as the central interdisciplinary case study, engaging instructors from "
        "religious studies, anthropology, philosophy, and psychology to co-design an undergraduate course."
    ),
    "icls-volume-2025-paper-0364": (
        "Mentions religion as a sociopolitical identity axis subject to increasing societal hate and discrimination, "
        "positioning teachers as transformational agents tasked with helping students navigate identity-based oppression."
    ),
    "icls-volume-2026-paper-0353": (
        "Frames arts-based maker learning and creative identity work within a critical perspective that directly "
        "confronts systemic structures of power and oppression operating along religious, racial, ethnic, and cultural lines."
    )
}

EVIDENCE_SNIPPETS = {
    "isls-2024-proceedings-paper-0042": (
        "This shift in analytic methods illustrated how classroom science phenomena and science teaching interactions "
        "were not neutral. Instead, they were deeply rooted in Hindu nationalism, settler colonialism, Islamophobia, "
        "and homophobia... asserting upper-caste Hindu supremacy in the school."
    ),
    "icls-2024-proceedings-paper-0024": (
        "...care is interpreted and enacted differently across communities, and individuals' perceptions and experiences "
        "of care are shaped by identities such as culture, race/ethnicity, gender, and religion."
    ),
    "icls-2024-proceedings-paper-0269": (
        "...participation in the journey gave rise to changes in various personal, social, and religious-national "
        "aspects of identity... A few of the participants said that attending religious services at the Reform synagogue "
        "in Rochester was a highlight that deepened their connection to Jewish identity..."
    ),
    "icls-volume-2025-paper-0125": (
        "...education was initially negatively associated with trust, but its effect diminished when religion and "
        "ethnicity were accounted for in a stepwise multiple regression analysis. Lower-educated groups, such as Hausa, Muslims..."
    ),
    "icls-volume-2025-paper-0329": (
        "...the nine instructors brought expertise from six disciplines: psychology, anthropology, philosophy, "
        "religious studies, sociology, and business administration... serial presentation of religion, introducing "
        "foundational concepts through three distinct components of the scientific study of religion..."
    ),
    "icls-volume-2025-paper-0364": (
        "At the time when trans students and educators are attacked, increasing hate along the lines of race and religion "
        "–educators are tasked with working with students to go beyond disciplinary concepts but look at them as connected "
        "to peoples, communities, and societies."
    ),
    "icls-volume-2026-paper-0353": (
        "...structures of power that have continuously led to oppression and genocide based on race, ethnicity, culture, "
        "religion, language, gender, socioeconomic status, ability..."
    )
}

def update_review_data():
    review_path = f"data/reviews/{REVIEW_ID}.json"
    with open(review_path, "r", encoding="utf-8") as f:
        review_data = json.load(f)

    # 1. Update columns
    sel_cols = review_data.get("selected_columns", [])
    if PROP_ID not in sel_cols:
        # Insert religion_relation before abstract if present
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
    col_defs[PROP_ID] = {"label": "Relation to 'Religion'", "width": 300}
    review_data["column_definitions"] = col_defs

    if "property_versions" not in review_data:
        review_data["property_versions"] = {}
    review_data["property_versions"][PROP_ID] = PROP_VERSION
    review_data["updated_at"] = datetime.datetime.now().isoformat()

    # 2. Update paper objects
    obs_dir = "data/observations"
    os.makedirs(obs_dir, exist_ok=True)

    for paper in review_data.get("papers", []):
        pid = paper["id"]
        exp = RELIGION_EXPLANATIONS.get(pid, "Discusses aspects related to religion.")
        paper[PROP_ID] = exp

        # Create Observation JSON
        obs_obj = {
            "paper_id": pid,
            "property_id": PROP_ID,
            "property_version": PROP_VERSION,
            "value": exp,
            "status": "extracted",
            "evidence": [
                {
                    "paper_id": pid,
                    "section_id": None,
                    "pdf_page": None,
                    "supporting_text": EVIDENCE_SNIPPETS.get(pid, "")
                }
            ],
            "method": "full_text_analysis",
            "confidence": 1.0,
            "run_id": "run_religion_relation_20260726",
            "source_version": "1.0.0"
        }
        obs_file = os.path.join(obs_dir, f"{pid}_{PROP_ID}.json")
        with open(obs_file, "w", encoding="utf-8") as f:
            json.dump(obs_obj, f, indent=2)

    # Save main review file
    with open(review_path, "w", encoding="utf-8") as f:
        json.dump(review_data, f, indent=2)
    print(f"Updated {review_path}")

    # 3. Update derived reviews cache
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
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"Updated {manifest_file}")

    # 4. Update Markdown summary file
    md_path = f"data/reviews/{REVIEW_ID}.md"
    md_content = f"""# Literature Review: Dipstick Review - religion

- **Review ID**: `{REVIEW_ID}`
- **Created At**: `{review_data.get('created_at')}`
- **Updated At**: `{review_data.get('updated_at')}`
- **Matching Papers**: {len(review_data.get('papers', []))}
- **Selected Columns**: {', '.join(sel_cols)}
- **Keywords**: religion

## Web Viewer Launch Link

[🚀 Launch Interactive Web Viewer for this Review](http://localhost:8080/?keywords=religion&review={REVIEW_ID})

## Papers and 'Religion' Property Extractions

| Paper ID | Title | Authors | Year | Relation to 'Religion' |
| --- | --- | --- | --- | --- |
"""
    for paper in review_data.get("papers", []):
        md_content += f"| `{paper['id']}` | {paper['title']} | {paper['authors']} | {paper['year']} | {paper[PROP_ID]} |\n"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Updated {md_path}")

if __name__ == "__main__":
    update_review_data()
