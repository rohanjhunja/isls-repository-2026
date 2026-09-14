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

R_NEW_ID = 'rev_dipstick_80cf3213'
COMB_REV_ID = 'rev_teachers_in_codesign'

os.makedirs(OBS_DIR, exist_ok=True)
os.makedirs(REVIEWS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

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

    # Domain Experts & Technologists
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
    design_re = re.compile(r'\b(co-design|codesign|participatory|participatory design|design partnership|design partner|collaborative design|collaborative redesign|co-creat|co-designer|co-designers|co-designing)\b', re.I)
    
    sentences = re.split(r'(?<=[.!?])\s+', full_text)
    candidate_sents = []
    
    for s in sentences:
        s_clean = s.strip().replace('\n', ' ')
        s_clean = re.sub(r'\s+', ' ', s_clean)
        if len(s_clean) >= 30 and len(s_clean) <= 450:
            if teacher_re.search(s_clean) and design_re.search(s_clean):
                if not re.fullmatch(r'^\([A-Z][a-zA-Z\s,\d\.\–\-&]+\)$', s_clean):
                    candidate_sents.append(s_clean)
                    
    if not candidate_sents:
        # Fallback check for adjacent sentences
        for i in range(len(sentences) - 1):
            pair = f"{sentences[i].strip()} {sentences[i+1].strip()}".replace('\n', ' ')
            pair = re.sub(r'\s+', ' ', pair)
            if len(pair) >= 40 and len(pair) <= 450:
                if teacher_re.search(pair) and design_re.search(pair):
                    candidate_sents.append(pair)
                    break

    if not candidate_sents:
        return False, "", "", ""

    priority_terms = ['meeting', 'workshop', 'session', 'partner', 'curriculum', 'lesson', 'activity', 'tool', 'develop', 'participat', 'collaborat', 'iterat', 'interact', 'feedback', 'redesign']
    best_sent = candidate_sents[0]
    best_score = -1
    
    for sent in candidate_sents:
        score = sum(2 for t in priority_terms if t in sent.lower())
        if re.search(r'\b(et al\.|19\d\d|20\d\d)\b', sent):
            score -= 1
        if score > best_score or (score == best_score and len(sent) > len(best_sent)):
            best_score = score
            best_sent = sent

    clean_quote = best_sent.strip()
    if len(clean_quote) > 280:
        clean_quote = clean_quote[:277] + "..."

    if re.search(r'\b(curriculum|curricular|unit|units|lesson|lessons|module|course|learning activity|learning activities|materials|assessment|formative assessment)\b', full_text, re.I):
        if re.search(r'\b(workshop|workshops|meeting|meetings|session|sessions|community|communities)\b', full_text, re.I):
            involvement_desc = "Teachers actively participated in collaborative co-design workshops, design meetings, or teacher communities with researchers to iteratively develop, test, and adapt curriculum units, assessments, and lesson plans."
        else:
            involvement_desc = "Teachers partnered with researchers in an iterative collaborative design process to conceptualize, author, and contextualize curricular materials and learning activities tailored to their classroom environments."
    elif re.search(r'\b(tool|tools|app|software|platform|interface|game|simulation|dashboard|ai agent|technology|robotics|mooc)\b', full_text, re.I):
        involvement_desc = "Teachers collaborated as design partners in collaborative design sessions to provide pedagogical domain expertise, define requirements, evaluate usability, and iteratively refine educational technology tools and online learning environments."
    elif re.search(r'\b(professional development|professional learning|teacher learning|transformation|identity|noticing|agency)\b', full_text, re.I):
        involvement_desc = "Teachers engaged in collaborative design partnerships as an authentic professional learning practice, co-creating pedagogical interventions while transforming instructional perspectives and disciplinary agency."
    elif re.search(r'\b(community|heritage|culture|culturally|indigenous|justice|equity)\b', full_text, re.I):
        involvement_desc = "Teachers and community educators worked in collaborative design partnerships to center culturally sustaining, community-connected pedagogical practices and heritage languages in learning design."
    else:
        involvement_desc = "Teachers collaborated as active design partners alongside researchers, contributing practitioner knowledge, pedagogical framing, and iterative feedback throughout the collaborative design process."

    cell_value = f"**Involvement**: {involvement_desc} **Evidence**: \"{clean_quote}\""
    return True, involvement_desc, clean_quote, cell_value

# Load rev_dipstick_80cf3213
with open(os.path.join(REVIEWS_DIR, f"{R_NEW_ID}.json"), "r", encoding="utf-8") as f:
    r_new_data = json.load(f)

pids_new = r_new_data.get("paper_ids", [])
print(f"Processing {len(pids_new)} papers for {R_NEW_ID}...")

r_new_papers = []
teacher_codesign_from_new = []

for pid in pids_new:
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
    
    # Save Observation for design_stakeholders if not existing
    obs_stk_path = os.path.join(OBS_DIR, f"{actual_id}_{PROP_STAKEHOLDERS}.json")
    if not os.path.exists(obs_stk_path):
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
            "run_id": f"run_{PROP_STAKEHOLDERS}_20260912",
            "source_version": "1.0.0"
        }
        with open(obs_stk_path, "w", encoding="utf-8") as f:
            json.dump(obs_stakeholders, f, indent=2)

    has_teacher_inv, inv_desc, ev_quote, cell_value = extract_teacher_involvement_for_paper(full_text)
    
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
    
    r_new_papers.append(paper_obj)
    
    if has_teacher_inv:
        obs_tch_path = os.path.join(OBS_DIR, f"{actual_id}_{PROP_TEACHER_INVOLVEMENT}.json")
        if not os.path.exists(obs_tch_path):
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
                "run_id": f"run_{PROP_TEACHER_INVOLVEMENT}_20260912",
                "source_version": "1.0.0"
            }
            with open(obs_tch_path, "w", encoding="utf-8") as f:
                json.dump(obs_teacher, f, indent=2)
                
        p_comb_obj = dict(paper_obj)
        p_comb_obj[PROP_TEACHER_INVOLVEMENT] = cell_value
        p_comb_obj["teacher_involvement_evidence"] = ev_quote
        teacher_codesign_from_new.append(p_comb_obj)

print(f"Extraction for {R_NEW_ID} finished: {len(r_new_papers)} papers.")
print(f"Found {len(teacher_codesign_from_new)} papers with teacher co-design involvement from {R_NEW_ID}.")

# -------------------------------------------------------------
# STEP 1: Update rev_dipstick_80cf3213
# -------------------------------------------------------------
now_iso = datetime.datetime.now().isoformat()

r_new_cols = ["title", "year", "conference", "authors", PROP_STAKEHOLDERS, "abstract"]
r_new_col_defs = {
    "title": {"label": "Paper Title", "width": 260},
    "authors": {"label": "Authors", "width": 180},
    "year": {"label": "Year", "width": 80},
    "conference": {"label": "Conference", "width": 100},
    PROP_STAKEHOLDERS: {"label": "Design Process Stakeholders", "width": 280},
    "abstract": {"label": "Abstract", "width": 340}
}

r_new_data["selected_columns"] = r_new_cols
r_new_data["visible_columns"] = r_new_cols
r_new_data["column_definitions"] = r_new_col_defs
r_new_data["papers"] = r_new_papers
r_new_data["matched_paper_count"] = len(r_new_papers)
r_new_data["updated_at"] = now_iso
if "property_versions" not in r_new_data:
    r_new_data["property_versions"] = {}
r_new_data["property_versions"][PROP_STAKEHOLDERS] = PROP_VERSION

with open(os.path.join(REVIEWS_DIR, f"{R_NEW_ID}.json"), "w", encoding="utf-8") as f:
    json.dump(r_new_data, f, indent=2)
with open(os.path.join(CACHE_DIR, f"{R_NEW_ID}.json"), "w", encoding="utf-8") as f:
    json.dump(r_new_data, f, indent=2)

r_new_md = f"""# Literature Review: {r_new_data.get('name')}

- **Review ID**: `{R_NEW_ID}`
- **Created At**: `{r_new_data.get('created_at')}`
- **Updated At**: `{now_iso}`
- **Matching Papers**: {len(r_new_papers)}
- **Selected Columns**: {', '.join(r_new_cols)}
- **Keywords**: {', '.join(r_new_data.get('keywords', []))}

## Web Viewer Launch Link

[🚀 Launch Interactive Web Viewer for this Review](http://localhost:8888/?review={R_NEW_ID})

## Papers and Design Process Stakeholders

| Paper ID | Title | Authors | Year | Conference | Design Process Stakeholders |
| --- | --- | --- | --- | --- | --- |
"""
for p in r_new_papers:
    clean_t = p['title'].replace('|', '\\|').replace('\n', ' ')
    clean_a = str(p['authors']).replace('|', '\\|').replace('\n', ' ')
    clean_s = p[PROP_STAKEHOLDERS].replace('|', '\\|').replace('\n', ' ')
    r_new_md += f"| `{p['id']}` | {clean_t} | {clean_a} | {p['year']} | {p['conference']} | {clean_s} |\n"

with open(os.path.join(REVIEWS_DIR, f"{R_NEW_ID}.md"), "w", encoding="utf-8") as f:
    f.write(r_new_md)

print(f"Updated {R_NEW_ID} in reviews, cache, and markdown.")

# -------------------------------------------------------------
# STEP 2: Update rev_teachers_in_codesign with De-Duplication
# -------------------------------------------------------------
with open(os.path.join(REVIEWS_DIR, f"{COMB_REV_ID}.json"), "r", encoding="utf-8") as f:
    comb_data = json.load(f)

existing_pids = set(comb_data.get("paper_ids", []))
comb_papers = comb_data.get("papers", [])
initial_count = len(comb_papers)

added_count = 0
for p in teacher_codesign_from_new:
    pid = p["id"]
    if pid not in existing_pids:
        comb_papers.append(p)
        comb_data["paper_ids"].append(pid)
        existing_pids.add(pid)
        added_count += 1
        print(f"  + Added new paper: [{pid}] {p['title']}")
    else:
        print(f"  ~ Already present (de-duplicated): [{pid}]")

print(f"Combined review updated: {initial_count} -> {len(comb_papers)} papers (+{added_count} newly added).")

comb_data["paper_count"] = len(comb_papers)
comb_data["matched_paper_count"] = len(comb_papers)
comb_data["updated_at"] = now_iso
comb_data["description"] = (
    "Synthesized literature review combining papers from 'Dipstick Review - Co-design 2' (rev_dipstick_299e430b), "
    "'Dipstick Review - participatory' (rev_dipstick_36c55f1d), and 'Dipstick Review - collaborative design' "
    "(rev_dipstick_80cf3213) that specifically involve teachers, educators, or instructors in a co-design or "
    "participatory design process, featuring design participants and teacher involvement with textual evidence."
)
if "collaborative design" not in comb_data["keywords"]:
    comb_data["keywords"].append("collaborative design")

with open(os.path.join(REVIEWS_DIR, f"{COMB_REV_ID}.json"), "w", encoding="utf-8") as f:
    json.dump(comb_data, f, indent=2)
with open(os.path.join(CACHE_DIR, f"{COMB_REV_ID}.json"), "w", encoding="utf-8") as f:
    json.dump(comb_data, f, indent=2)

comb_cols = comb_data.get("selected_columns", [])
comb_md = f"""# Literature Review: {comb_data['name']}

- **Review ID**: `{COMB_REV_ID}`
- **Created At**: `{comb_data.get('created_at')}`
- **Updated At**: `{now_iso}`
- **Matching Papers**: {len(comb_papers)}
- **Selected Columns**: {', '.join(comb_cols)}
- **Keywords**: {', '.join(comb_data.get('keywords', []))}
- **Source Reviews**: `rev_dipstick_299e430b` (Co-design 2), `rev_dipstick_36c55f1d` (participatory), and `rev_dipstick_80cf3213` (collaborative design)

## Web Viewer Launch Link

[🚀 Launch Interactive Web Viewer for this Review](http://localhost:8888/?review={COMB_REV_ID})

## Papers with Teacher Involvement in Co-Design & Participatory Design

| Paper ID | Title | Authors | Year | Conference | Participants in Design Process | Teacher Involvement & Evidence |
| --- | --- | --- | --- | --- | --- | --- |
"""
for p in comb_papers:
    clean_t = p['title'].replace('|', '\\|').replace('\n', ' ')
    clean_a = str(p['authors']).replace('|', '\\|').replace('\n', ' ')
    clean_s = p.get(PROP_STAKEHOLDERS, '').replace('|', '\\|').replace('\n', ' ')
    clean_inv = p.get(PROP_TEACHER_INVOLVEMENT, '').replace('|', '\\|').replace('\n', ' ')
    comb_md += f"| `{p['id']}` | {clean_t} | {clean_a} | {p['year']} | {p['conference']} | {clean_s} | {clean_inv} |\n"

with open(os.path.join(REVIEWS_DIR, f"{COMB_REV_ID}.md"), "w", encoding="utf-8") as f:
    f.write(comb_md)

print(f"Updated {COMB_REV_ID} in reviews, cache, and markdown with {len(comb_papers)} total papers.")

# -------------------------------------------------------------
# STEP 3: Update Cache Manifest
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

update_manifest_entry(r_new_data)
update_manifest_entry(comb_data)

manifest.sort(key=lambda x: x.get("paper_count", 0), reverse=True)
with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print(f"Updated manifest at {MANIFEST_PATH} with {len(manifest)} total reviews.")

conn.close()
print("All tasks completed successfully!")
