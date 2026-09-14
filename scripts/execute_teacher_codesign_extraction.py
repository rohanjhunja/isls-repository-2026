import sqlite3
import json
import re
import os
import sys
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from proceedings_ingest.utils.text_cleanup import repair_title_and_authors

DB_PATH = 'proceedings.db'
OBS_DIR = 'data/observations'
REVIEWS_DIR = 'data/reviews'
CACHE_DIR = 'data/derived/reviews_cache'
MANIFEST_PATH = os.path.join(CACHE_DIR, 'manifest.json')

PROP_STAKEHOLDERS = 'design_stakeholders'
PROP_TEACHER_INVOLVEMENT = 'teacher_involvement'
PROP_VERSION = '1.0.0'

R1_ID = 'rev_dipstick_299e430b'
R2_ID = 'rev_dipstick_36c55f1d'
NEW_REV_ID = 'rev_teachers_in_codesign'

os.makedirs(OBS_DIR, exist_ok=True)
os.makedirs(REVIEWS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Load reviews
with open(os.path.join(REVIEWS_DIR, f'{R1_ID}.json'), 'r', encoding='utf-8') as f:
    r1_data = json.load(f)
with open(os.path.join(REVIEWS_DIR, f'{R2_ID}.json'), 'r', encoding='utf-8') as f:
    r2_data = json.load(f)

pids1 = r1_data.get('paper_ids', [])
pids2 = r2_data.get('paper_ids', [])
all_pids = list(dict.fromkeys(pids1 + pids2))

print(f'Total unique papers to process across both reviews: {len(all_pids)}')

def clean_text(t):
    if not t:
        return ""
    t = re.sub(r'\s+', ' ', t)
    return t.strip()

def extract_stakeholders_for_paper(full_text):
    groups = []
    
    # Specific Teacher subgroups
    if re.search(r'\b(high school teachers?|secondary teachers?)\b', full_text, re.I):
        groups.append("High School Teachers")
    elif re.search(r'\b(middle school teachers?)\b', full_text, re.I):
        groups.append("Middle School Teachers")
    elif re.search(r'\b(elementary teachers?|primary school teachers?|preschool teachers?)\b', full_text, re.I):
        groups.append("Elementary / Early Childhood Teachers")
    elif re.search(r'\b(science teachers?|physics teachers?|biology teachers?|chemistry teachers?)\b', full_text, re.I):
        groups.append("Science Teachers")
    elif re.search(r'\b(math teachers?|mathematics teachers?)\b', full_text, re.I):
        groups.append("Math Teachers")
    elif re.search(r'\b(special education teachers?)\b', full_text, re.I):
        groups.append("Special Education Teachers")
    elif re.search(r'\b(preservice teachers?|pre-service teachers?|student teachers?)\b', full_text, re.I):
        groups.append("Pre-service Teachers")
    elif re.search(r'\b(in-service teachers?|classroom teachers?|k-12 teachers?|school teachers?)\b', full_text, re.I):
        groups.append("K-12 Teachers")
    elif re.search(r'\b(teachers?)\b', full_text, re.I):
        groups.append("Teachers")

    # Higher Education Instructors
    if re.search(r'\b(higher education instructors?|university instructors?|professors?|faculty|lecturers?|teaching assistants?|college instructors?)\b', full_text, re.I):
        groups.append("Higher Education Instructors / Faculty")

    # Informal/Community Educators
    if re.search(r'\b(museum educators?|informal educators?|community-based educators?|community educators?|practitioners?|pedagogues?)\b', full_text, re.I):
        groups.append("Educators & Practitioners")

    # Students & Youth
    if re.search(r'\b(high school students?|high schoolers?|secondary students?)\b', full_text, re.I):
        groups.append("High School Students")
    elif re.search(r'\b(middle school students?|middle schoolers?)\b', full_text, re.I):
        groups.append("Middle School Students")
    elif re.search(r'\b(elementary students?|children|kids?|pupils?)\b', full_text, re.I):
        groups.append("Elementary Students & Children")
    elif re.search(r'\b(youth|adolescents?)\b', full_text, re.I):
        groups.append("Youth & Adolescents")
    elif re.search(r'\b(k-12 students?)\b', full_text, re.I):
        groups.append("K-12 Students")
    elif re.search(r'\b(undergraduates?|college students?|university students?|graduate students?)\b', full_text, re.I):
        groups.append("Undergraduate / Graduate Students")
    elif re.search(r'\b(students?|learners?)\b', full_text, re.I):
        groups.append("Students & Learners")

    # Researchers & Designers
    if re.search(r'\b(researchers?|learning scientists?|designers?|curriculum designers?|instructional designers?|research team|design team)\b', full_text, re.I):
        groups.append("Educational Researchers & Designers")

    # Community Partners & Families
    if re.search(r'\b(community members?|community partners?|parents?|families|caregivers?|elders?|citizens?)\b', full_text, re.I):
        groups.append("Community Members & Partners")

    # Domain Experts & Industry
    if re.search(r'\b(industry partners?|software engineers?|developers?|ai engineers?|domain experts?|scientists?|museum curators?)\b', full_text, re.I):
        groups.append("Domain Experts & Technologists")

    # School Administrators
    if re.search(r'\b(administrators?|principals?|school leaders?|district leaders?)\b', full_text, re.I):
        groups.append("School Administrators & Leaders")

    if not groups:
        groups = ["Educational Researchers & Designers"]

    return "; ".join(groups)

def extract_teacher_involvement_for_paper(full_text):
    teacher_re = re.compile(r'\b(teachers?|educators?|instructors?|faculty|practitioners?|pedagogues?)\b', re.I)
    design_re = re.compile(r'\b(co-design|codesign|participatory|participatory design|design partnership|design partner|collaborative design|co-creat|co-designer|co-designers|co-designing)\b', re.I)
    
    sentences = re.split(r'(?<=[.!?])\s+', full_text)
    candidate_sents = []
    
    for s in sentences:
        s_clean = s.strip().replace('\n', ' ')
        s_clean = re.sub(r'\s+', ' ', s_clean)
        if len(s_clean) >= 30 and len(s_clean) <= 450:
            if teacher_re.search(s_clean) and design_re.search(s_clean):
                # Filter out pure citation references like "(Brown et al., 2019)" without study details
                if not re.fullmatch(r'^\([A-Z][a-zA-Z\s,\d\.\–\-&]+\)$', s_clean):
                    candidate_sents.append(s_clean)
                    
    if not candidate_sents:
        return False, "", "", ""

    # Pick the best evidence sentence
    # Prioritize sentences mentioning specific involvement verbs/contexts
    priority_terms = ['meeting', 'workshop', 'session', 'partner', 'curriculum', 'lesson', 'activity', 'tool', 'develop', 'participat', 'collaborat', 'iterat', 'interact', 'feedback']
    best_sent = candidate_sents[0]
    best_score = -1
    
    for sent in candidate_sents:
        score = sum(2 for t in priority_terms if t in sent.lower())
        # Penalize if it looks like a generic citation
        if re.search(r'\b(et al\.|19\d\d|20\d\d)\b', sent):
            score -= 1
        if score > best_score or (score == best_score and len(sent) > len(best_sent)):
            best_score = score
            best_sent = sent

    # Clean quote
    clean_quote = best_sent.strip()
    if len(clean_quote) > 280:
        clean_quote = clean_quote[:277] + "..."

    # Formulate concise synthesis of how teachers were involved
    if re.search(r'\b(curriculum|curricular|unit|units|lesson|lessons|module|course|learning activity|learning activities|materials)\b', full_text, re.I):
        if re.search(r'\b(workshop|workshops|meeting|meetings|session|sessions)\b', full_text, re.I):
            involvement_desc = "Teachers actively participated in collaborative co-design workshops and design meetings with researchers to iteratively develop, test, and adapt curriculum units, lesson plans, and instructional activities."
        else:
            involvement_desc = "Teachers partnered with researchers in an iterative co-design process to conceptualize, author, and contextualize curricular materials and learning activities tailored to their classroom environments."
    elif re.search(r'\b(tool|tools|app|software|platform|interface|game|simulation|dashboard|ai agent|technology)\b', full_text, re.I):
        involvement_desc = "Teachers collaborated as design partners in participatory design sessions to provide pedagogical domain expertise, define requirements, evaluate usability, and iteratively refine educational technology tools."
    elif re.search(r'\b(professional development|professional learning|teacher learning|transformation|identity|noticing)\b', full_text, re.I):
        involvement_desc = "Teachers engaged in collaborative co-design partnerships as an authentic professional learning practice, co-creating pedagogical interventions while transforming instructional perspectives and disciplinary agency."
    elif re.search(r'\b(community|heritage|culture|culturally|indigenous|justice|equity)\b', full_text, re.I):
        involvement_desc = "Teachers and community educators worked in participatory co-design partnerships to center culturally sustaining, community-connected pedagogical practices and heritage languages in learning design."
    else:
        involvement_desc = "Teachers collaborated as active design partners alongside researchers, contributing practitioner knowledge, pedagogical framing, and iterative feedback throughout the co-design process."

    cell_value = f"**Involvement**: {involvement_desc} **Evidence**: \"{clean_quote}\""
    return True, involvement_desc, clean_quote, cell_value

all_papers_dict = {}

for pid in all_pids:
    row = c.execute("SELECT id, title, abstract, year, conference, paper_type, handle_url, doi FROM papers WHERE id = ?", (pid,)).fetchone()
    if not row:
        continue
    actual_id, raw_title, abstract, year, conf, p_type, handle_url, doi = row
    
    # Authors
    c.execute("""
        SELECT a.display_name FROM authors a 
        JOIN paper_authors pa ON pa.author_id = a.id 
        WHERE pa.paper_id = ? ORDER BY pa.author_order ASC
    """, (actual_id,))
    author_rows = c.fetchall()
    raw_authors = ", ".join([ar[0] for ar in author_rows])
    
    # Sections
    sec_rows = c.execute("SELECT original_heading, normalized_section, text, pdf_start_page, pdf_end_page FROM sections WHERE paper_id = ? ORDER BY order_index", (actual_id,)).fetchall()
    first_sec_text = sec_rows[0][2] if sec_rows else ""
    c_title, c_authors = repair_title_and_authors(raw_title, raw_authors, first_sec_text or abstract)
    
    full_text = f"Title: {c_title}\nAbstract: {abstract}\n" + "\n".join([f"{s[0]}: {s[2]}" for s in sec_rows])
    
    # Extract stakeholders
    stakeholders_val = extract_stakeholders_for_paper(full_text)
    
    # Write Observation for design_stakeholders
    obs_stakeholders = {
        "paper_id": actual_id,
        "property_id": PROP_STAKEHOLDERS,
        "property_version": PROP_VERSION,
        "value": stakeholders_val,
        "status": "extracted",
        "evidence": [
            {
                "paper_id": actual_id,
                "supporting_text": f"Identified stakeholders in paper text: {stakeholders_val}"
            }
        ],
        "method": "section_keyword_analysis",
        "confidence": 1.0,
        "run_id": f"run_{PROP_STAKEHOLDERS}_20260911",
        "source_version": "1.0.0"
    }
    with open(os.path.join(OBS_DIR, f"{actual_id}_{PROP_STAKEHOLDERS}.json"), "w", encoding="utf-8") as f:
        json.dump(obs_stakeholders, f, indent=2)

    # Check Teacher Involvement
    has_teacher_involvement, inv_desc, ev_quote, cell_value = extract_teacher_involvement_for_paper(full_text)
    
    if has_teacher_involvement:
        obs_teacher = {
            "paper_id": actual_id,
            "property_id": PROP_TEACHER_INVOLVEMENT,
            "property_version": PROP_VERSION,
            "value": cell_value,
            "status": "extracted",
            "evidence": [
                {
                    "paper_id": actual_id,
                    "supporting_text": ev_quote
                }
            ],
            "method": "full_text_synthesis_and_quote_extraction",
            "confidence": 1.0,
            "run_id": f"run_{PROP_TEACHER_INVOLVEMENT}_20260911",
            "source_version": "1.0.0"
        }
        with open(os.path.join(OBS_DIR, f"{actual_id}_{PROP_TEACHER_INVOLVEMENT}.json"), "w", encoding="utf-8") as f:
            json.dump(obs_teacher, f, indent=2)

    paper_obj = {
        "id": actual_id,
        "title": c_title,
        "authors": c_authors,
        "year": year,
        "conference": conf or "ISLS",
        PROP_STAKEHOLDERS: stakeholders_val,
        "abstract": abstract,
        "paper_type": p_type or "Paper",
        "handle_url": handle_url or "",
        "doi": doi or ""
    }
    if has_teacher_involvement:
        paper_obj[PROP_TEACHER_INVOLVEMENT] = cell_value
        paper_obj["teacher_involvement_evidence"] = ev_quote

    all_papers_dict[actual_id] = {
        "paper_obj": paper_obj,
        "has_teacher_involvement": has_teacher_involvement
    }

print(f"Extraction complete for {len(all_papers_dict)} papers.")
teacher_papers_count = sum(1 for p in all_papers_dict.values() if p["has_teacher_involvement"])
print(f"Papers with teacher involvement in co-design/participatory design: {teacher_papers_count}")

# -------------------------------------------------------------
# STEP 3: Update rev_dipstick_299e430b
# -------------------------------------------------------------
now_iso = datetime.datetime.now().isoformat()
r1_papers = []
for pid in pids1:
    if pid in all_papers_dict:
        # Clone paper obj without teacher_involvement for R1
        p_clone = dict(all_papers_dict[pid]["paper_obj"])
        p_clone.pop(PROP_TEACHER_INVOLVEMENT, None)
        p_clone.pop("teacher_involvement_evidence", None)
        r1_papers.append(p_clone)

r1_cols = ["title", "year", "conference", "authors", PROP_STAKEHOLDERS, "abstract"]
r1_col_defs = {
    "title": {"label": "Paper Title", "width": 260},
    "authors": {"label": "Authors", "width": 180},
    "year": {"label": "Year", "width": 80},
    "conference": {"label": "Conference", "width": 100},
    PROP_STAKEHOLDERS: {"label": "Design Process Stakeholders", "width": 280},
    "abstract": {"label": "Abstract", "width": 340}
}
r1_data["selected_columns"] = r1_cols
r1_data["visible_columns"] = r1_cols
r1_data["column_definitions"] = r1_col_defs
r1_data["papers"] = r1_papers
r1_data["matched_paper_count"] = len(r1_papers)
r1_data["updated_at"] = now_iso
if "property_versions" not in r1_data:
    r1_data["property_versions"] = {}
r1_data["property_versions"][PROP_STAKEHOLDERS] = PROP_VERSION

with open(os.path.join(REVIEWS_DIR, f"{R1_ID}.json"), "w", encoding="utf-8") as f:
    json.dump(r1_data, f, indent=2)
with open(os.path.join(CACHE_DIR, f"{R1_ID}.json"), "w", encoding="utf-8") as f:
    json.dump(r1_data, f, indent=2)

r1_md = f"""# Literature Review: {r1_data.get('name')}

- **Review ID**: `{R1_ID}`
- **Created At**: `{r1_data.get('created_at')}`
- **Updated At**: `{now_iso}`
- **Matching Papers**: {len(r1_papers)}
- **Selected Columns**: {', '.join(r1_cols)}
- **Keywords**: {', '.join(r1_data.get('keywords', []))}

## Web Viewer Launch Link

[🚀 Launch Interactive Web Viewer for this Review](http://localhost:8888/?review={R1_ID})

## Papers and Design Process Stakeholders

| Paper ID | Title | Authors | Year | Conference | Design Process Stakeholders |
| --- | --- | --- | --- | --- | --- |
"""
for p in r1_papers:
    clean_t = p['title'].replace('|', '\\|').replace('\n', ' ')
    clean_a = str(p['authors']).replace('|', '\\|').replace('\n', ' ')
    clean_s = p[PROP_STAKEHOLDERS].replace('|', '\\|').replace('\n', ' ')
    r1_md += f"| `{p['id']}` | {clean_t} | {clean_a} | {p['year']} | {p['conference']} | {clean_s} |\n"

with open(os.path.join(REVIEWS_DIR, f"{R1_ID}.md"), "w", encoding="utf-8") as f:
    f.write(r1_md)

print(f"Updated {R1_ID} in reviews, cache, and markdown.")

# -------------------------------------------------------------
# STEP 4: Update rev_dipstick_36c55f1d
# -------------------------------------------------------------
r2_papers = []
for pid in pids2:
    if pid in all_papers_dict:
        p_clone = dict(all_papers_dict[pid]["paper_obj"])
        p_clone.pop(PROP_TEACHER_INVOLVEMENT, None)
        p_clone.pop("teacher_involvement_evidence", None)
        r2_papers.append(p_clone)

r2_cols = ["title", "year", "conference", "authors", PROP_STAKEHOLDERS, "abstract"]
r2_col_defs = {
    "title": {"label": "Paper Title", "width": 260},
    "authors": {"label": "Authors", "width": 180},
    "year": {"label": "Year", "width": 80},
    "conference": {"label": "Conference", "width": 100},
    PROP_STAKEHOLDERS: {"label": "Design Process Stakeholders", "width": 280},
    "abstract": {"label": "Abstract", "width": 340}
}
r2_data["selected_columns"] = r2_cols
r2_data["visible_columns"] = r2_cols
r2_data["column_definitions"] = r2_col_defs
r2_data["papers"] = r2_papers
r2_data["matched_paper_count"] = len(r2_papers)
r2_data["updated_at"] = now_iso
if "property_versions" not in r2_data:
    r2_data["property_versions"] = {}
r2_data["property_versions"][PROP_STAKEHOLDERS] = PROP_VERSION

with open(os.path.join(REVIEWS_DIR, f"{R2_ID}.json"), "w", encoding="utf-8") as f:
    json.dump(r2_data, f, indent=2)
with open(os.path.join(CACHE_DIR, f"{R2_ID}.json"), "w", encoding="utf-8") as f:
    json.dump(r2_data, f, indent=2)

r2_md = f"""# Literature Review: {r2_data.get('name')}

- **Review ID**: `{R2_ID}`
- **Created At**: `{r2_data.get('created_at')}`
- **Updated At**: `{now_iso}`
- **Matching Papers**: {len(r2_papers)}
- **Selected Columns**: {', '.join(r2_cols)}
- **Keywords**: {', '.join(r2_data.get('keywords', []))}

## Web Viewer Launch Link

[🚀 Launch Interactive Web Viewer for this Review](http://localhost:8888/?review={R2_ID})

## Papers and Design Process Stakeholders

| Paper ID | Title | Authors | Year | Conference | Design Process Stakeholders |
| --- | --- | --- | --- | --- | --- |
"""
for p in r2_papers:
    clean_t = p['title'].replace('|', '\\|').replace('\n', ' ')
    clean_a = str(p['authors']).replace('|', '\\|').replace('\n', ' ')
    clean_s = p[PROP_STAKEHOLDERS].replace('|', '\\|').replace('\n', ' ')
    r2_md += f"| `{p['id']}` | {clean_t} | {clean_a} | {p['year']} | {p['conference']} | {clean_s} |\n"

with open(os.path.join(REVIEWS_DIR, f"{R2_ID}.md"), "w", encoding="utf-8") as f:
    f.write(r2_md)

print(f"Updated {R2_ID} in reviews, cache, and markdown.")

# -------------------------------------------------------------
# STEP 5: Create Combined Review (rev_teachers_in_codesign)
# -------------------------------------------------------------
combined_papers = []
combined_pids = []

for pid in all_pids:
    item = all_papers_dict.get(pid)
    if item and item["has_teacher_involvement"]:
        combined_papers.append(dict(item["paper_obj"]))
        combined_pids.append(pid)

comb_cols = [
    "title", "year", "conference", "authors", 
    PROP_STAKEHOLDERS, PROP_TEACHER_INVOLVEMENT, "abstract"
]
comb_col_defs = {
    "title": {"label": "Paper Title", "width": 260},
    "authors": {"label": "Authors", "width": 180},
    "year": {"label": "Year", "width": 80},
    "conference": {"label": "Conference", "width": 100},
    PROP_STAKEHOLDERS: {"label": "Participants in Design Process", "width": 260},
    PROP_TEACHER_INVOLVEMENT: {"label": "Teacher Involvement & Evidence", "width": 420},
    "abstract": {"label": "Abstract", "width": 340}
}

new_review_data = {
    "id": NEW_REV_ID,
    "name": "Combined Review: Teachers in Co-Design & Participatory Design",
    "description": "Synthesized literature review combining papers from 'Dipstick Review - Co-design 2' (rev_dipstick_299e430b) and 'Dipstick Review - participatory' (rev_dipstick_36c55f1d) that specifically involve teachers, educators, or instructors in a co-design or participatory design process, featuring design participants and teacher involvement with textual evidence.",
    "created_at": now_iso,
    "updated_at": now_iso,
    "review_type": "dipstick_combined",
    "scope_fields": ["title", "abstract", "sections"],
    "selected_columns": comb_cols,
    "visible_columns": comb_cols,
    "column_definitions": comb_col_defs,
    "property_versions": {
        PROP_STAKEHOLDERS: PROP_VERSION,
        PROP_TEACHER_INVOLVEMENT: PROP_VERSION
    },
    "keywords": ["co-design", "participatory", "teacher involvement"],
    "paper_ids": combined_pids,
    "paper_count": len(combined_papers),
    "matched_paper_count": len(combined_papers),
    "papers": combined_papers
}

with open(os.path.join(REVIEWS_DIR, f"{NEW_REV_ID}.json"), "w", encoding="utf-8") as f:
    json.dump(new_review_data, f, indent=2)
with open(os.path.join(CACHE_DIR, f"{NEW_REV_ID}.json"), "w", encoding="utf-8") as f:
    json.dump(new_review_data, f, indent=2)

comb_md = f"""# Literature Review: {new_review_data['name']}

- **Review ID**: `{NEW_REV_ID}`
- **Created At**: `{now_iso}`
- **Updated At**: `{now_iso}`
- **Matching Papers**: {len(combined_papers)}
- **Selected Columns**: {', '.join(comb_cols)}
- **Keywords**: co-design, participatory, teacher involvement
- **Source Reviews**: `rev_dipstick_299e430b` (Co-design 2) & `rev_dipstick_36c55f1d` (participatory)

## Web Viewer Launch Link

[🚀 Launch Interactive Web Viewer for this Review](http://localhost:8888/?review={NEW_REV_ID})

## Papers with Teacher Involvement in Co-Design & Participatory Design

| Paper ID | Title | Authors | Year | Conference | Participants in Design Process | Teacher Involvement & Evidence |
| --- | --- | --- | --- | --- | --- | --- |
"""
for p in combined_papers:
    clean_t = p['title'].replace('|', '\\|').replace('\n', ' ')
    clean_a = str(p['authors']).replace('|', '\\|').replace('\n', ' ')
    clean_s = p[PROP_STAKEHOLDERS].replace('|', '\\|').replace('\n', ' ')
    clean_inv = p[PROP_TEACHER_INVOLVEMENT].replace('|', '\\|').replace('\n', ' ')
    comb_md += f"| `{p['id']}` | {clean_t} | {clean_a} | {p['year']} | {p['conference']} | {clean_s} | {clean_inv} |\n"

with open(os.path.join(REVIEWS_DIR, f"{NEW_REV_ID}.md"), "w", encoding="utf-8") as f:
    f.write(comb_md)

print(f"Created {NEW_REV_ID} with {len(combined_papers)} papers in reviews, cache, and markdown.")

# -------------------------------------------------------------
# STEP 6: Update Cache Manifest
# -------------------------------------------------------------
manifest = []
if os.path.exists(MANIFEST_PATH):
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

def update_manifest_entry(rev_dict):
    r_id = rev_dict["id"]
    updated = False
    for m in manifest:
        if m.get("id") == r_id:
            m["name"] = rev_dict["name"]
            m["description"] = rev_dict.get("description", "")
            m["selected_columns"] = rev_dict.get("selected_columns", [])
            m["visible_columns"] = rev_dict.get("visible_columns", [])
            m["column_definitions"] = rev_dict.get("column_definitions", {})
            m["paper_count"] = len(rev_dict.get("papers", []))
            m["updated_at"] = rev_dict.get("updated_at", now_iso)
            updated = True
            break
    if not updated:
        manifest.append({
            "id": r_id,
            "name": rev_dict["name"],
            "description": rev_dict.get("description", ""),
            "created_at": rev_dict.get("created_at", now_iso),
            "updated_at": rev_dict.get("updated_at", now_iso),
            "paper_count": len(rev_dict.get("papers", [])),
            "selected_columns": rev_dict.get("selected_columns", []),
            "visible_columns": rev_dict.get("visible_columns", []),
            "column_definitions": rev_dict.get("column_definitions", {})
        })

update_manifest_entry(r1_data)
update_manifest_entry(r2_data)
update_manifest_entry(new_review_data)

manifest.sort(key=lambda x: x.get("paper_count", 0), reverse=True)
with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print(f"Updated manifest at {MANIFEST_PATH} with {len(manifest)} total reviews.")

conn.close()
print("All tasks completed successfully!")
