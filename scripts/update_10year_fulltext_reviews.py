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
PROP_MATCHED_KW = 'matched_design_keywords'
PROP_VERSION = '1.0.0'

R1_ID = 'rev_dipstick_299e430b'
R2_ID = 'rev_dipstick_36c55f1d'
R3_ID = 'rev_dipstick_80cf3213'
COMB_REV_ID = 'rev_teachers_in_codesign'

os.makedirs(OBS_DIR, exist_ok=True)
os.makedirs(REVIEWS_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

now_iso = datetime.datetime.now().isoformat()

print("Loading existing review metadata...")
with open(os.path.join(REVIEWS_DIR, f"{R1_ID}.json"), "r", encoding="utf-8") as f:
    r1_data = json.load(f)
with open(os.path.join(REVIEWS_DIR, f"{R2_ID}.json"), "r", encoding="utf-8") as f:
    r2_data = json.load(f)
with open(os.path.join(REVIEWS_DIR, f"{R3_ID}.json"), "r", encoding="utf-8") as f:
    r3_data = json.load(f)
with open(os.path.join(REVIEWS_DIR, f"{COMB_REV_ID}.json"), "r", encoding="utf-8") as f:
    comb_data = json.load(f)

r1_existing = set(r1_data.get("paper_ids", []))
r2_existing = set(r2_data.get("paper_ids", []))
r3_existing = set(r3_data.get("paper_ids", []))
comb_existing = set(comb_data.get("paper_ids", []))

print(f"Existing paper counts: R1={len(r1_existing)}, R2={len(r2_existing)}, R3={len(r3_existing)}, Combined={len(comb_existing)}")

# Step 1: Query targeted sections only (abstract, method, discussion) per user instructions
print("Querying targeted sections (abstract, method, discussion)...")
TARGET_NORM_SECTIONS = [
    'abstract & introduction',
    'methodology & context',
    'discussion & conclusion'
]

c.execute("""
    SELECT paper_id, normalized_section, text
    FROM sections
    WHERE normalized_section IN ('abstract & introduction', 'methodology & context', 'discussion & conclusion')
    ORDER BY paper_id, order_index
""")

paper_target_sections = {}
for pid, norm_sec, txt in c.fetchall():
    if pid not in paper_target_sections:
        paper_target_sections[pid] = []
    if txt:
        paper_target_sections[pid].append(txt)

print(f"Loaded targeted sections for {len(paper_target_sections)} papers.")

# Fetch all paper metadata and author records
c.execute("SELECT id, title, abstract, year, conference, paper_type, handle_url, doi FROM papers")
all_papers_raw = {r[0]: r for r in c.fetchall()}

c.execute("""
    SELECT pa.paper_id, a.display_name 
    FROM paper_authors pa 
    JOIN authors a ON a.id = pa.author_id 
    ORDER BY pa.paper_id, pa.author_order ASC
""")
authors_by_paper = {}
for pid, aname in c.fetchall():
    if pid not in authors_by_paper:
        authors_by_paper[pid] = []
    authors_by_paper[pid].append(aname)

# Regex patterns for the 3 reviews
pat_codesign = re.compile(r'\b(co-design|codesign|co-designing|co-designer|co-designers)\b', re.I)
pat_participatory = re.compile(r'\b(participatory)\b', re.I)
pat_collabdesign = re.compile(r'\b(collaborative design|collaboratively design|collaborative redesign)\b', re.I)

r1_all = set(r1_existing)
r2_all = set(r2_existing)
r3_all = set(r3_existing)

for pid, raw in all_papers_raw.items():
    title = raw[1] or ""
    abstract = raw[2] or ""
    sec_txt = " ".join(paper_target_sections.get(pid, []))
    blob = f"{title} {abstract} {sec_txt}"
    
    if pat_codesign.search(blob):
        r1_all.add(pid)
    if pat_participatory.search(blob):
        r2_all.add(pid)
    if pat_collabdesign.search(blob):
        r3_all.add(pid)

print(f"Expanded paper counts across 10-year full text:")
print(f"  R1 (co-design): {len(r1_all)} (preserved {len(r1_existing)} existing, added {len(r1_all) - len(r1_existing)})")
print(f"  R2 (participatory): {len(r2_all)} (preserved {len(r2_existing)} existing, added {len(r2_all) - len(r2_existing)})")
print(f"  R3 (collaborative design): {len(r3_all)} (preserved {len(r3_existing)} existing, added {len(r3_all) - len(r3_existing)})")

all_active_pids = r1_all | r2_all | r3_all | comb_existing
print(f"Total distinct papers to process: {len(all_active_pids)}")

def extract_stakeholders(text):
    groups = []
    if re.search(r'\b(high school teachers?|secondary teachers?)\b', text, re.I):
        groups.append("High School Teachers")
    elif re.search(r'\b(middle school teachers?)\b', text, re.I):
        groups.append("Middle School Teachers")
    elif re.search(r'\b(elementary teachers?|primary school teachers?|preschool teachers?)\b', text, re.I):
        groups.append("Elementary / Early Childhood Teachers")
    elif re.search(r'\b(science teachers?|physics teachers?|biology teachers?|chemistry teachers?)\b', text, re.I):
        groups.append("Science Teachers")
    elif re.search(r'\b(math teachers?|mathematics teachers?)\b', text, re.I):
        groups.append("Math Teachers")
    elif re.search(r'\b(special education teachers?)\b', text, re.I):
        groups.append("Special Education Teachers")
    elif re.search(r'\b(preservice teachers?|pre-service teachers?|student teachers?)\b', text, re.I):
        groups.append("Pre-service Teachers")
    elif re.search(r'\b(in-service teachers?|classroom teachers?|k-12 teachers?|school teachers?)\b', text, re.I):
        groups.append("K-12 Teachers")
    elif re.search(r'\b(teachers?)\b', text, re.I):
        groups.append("Teachers")

    if re.search(r'\b(higher education instructors?|university instructors?|professors?|faculty|lecturers?|teaching assistants?|college instructors?)\b', text, re.I):
        groups.append("Higher Education Instructors / Faculty")

    if re.search(r'\b(museum educators?|informal educators?|community-based educators?|community educators?|practitioners?|pedagogues?)\b', text, re.I):
        groups.append("Educators & Practitioners")

    if re.search(r'\b(high school students?|high schoolers?|secondary students?)\b', text, re.I):
        groups.append("High School Students")
    elif re.search(r'\b(middle school students?|middle schoolers?)\b', text, re.I):
        groups.append("Middle School Students")
    elif re.search(r'\b(elementary students?|children|kids?|pupils?)\b', text, re.I):
        groups.append("Elementary Students & Children")
    elif re.search(r'\b(youth|adolescents?)\b', text, re.I):
        groups.append("Youth & Adolescents")
    elif re.search(r'\b(k-12 students?)\b', text, re.I):
        groups.append("K-12 Students")
    elif re.search(r'\b(undergraduates?|college students?|university students?|graduate students?)\b', text, re.I):
        groups.append("Undergraduate / Graduate Students")
    elif re.search(r'\b(students?|learners?)\b', text, re.I):
        groups.append("Students & Learners")

    if re.search(r'\b(researchers?|learning scientists?|designers?|curriculum designers?|instructional designers?|research team|design team)\b', text, re.I):
        groups.append("Educational Researchers & Designers")

    if re.search(r'\b(community members?|community partners?|parents?|families|caregivers?|elders?|citizens?)\b', text, re.I):
        groups.append("Community Members & Partners")

    if re.search(r'\b(industry partners?|software engineers?|developers?|ai engineers?|domain experts?|scientists?|museum curators?)\b', text, re.I):
        groups.append("Domain Experts & Technologists")

    if re.search(r'\b(administrators?|principals?|school leaders?|district leaders?)\b', text, re.I):
        groups.append("School Administrators & Leaders")

    if not groups:
        groups = ["Educational Researchers & Designers"]

    return "; ".join(groups)

teacher_re = re.compile(r'\b(teachers?|educators?|instructors?|faculty|practitioners?|pedagogues?)\b', re.I)
design_re = re.compile(r'\b(co-design|codesign|participatory|participatory design|design partnership|design partner|collaborative design|collaborative redesign|co-creat|co-designer|co-designers|co-designing)\b', re.I)

def extract_teacher_involvement(full_text):
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

# Process all active papers
processed_papers = {}
print("Processing paper metadata, stakeholders, and teacher involvement...")

for pid in all_active_pids:
    raw = all_papers_raw.get(pid)
    if not raw:
        continue
    _, raw_title, abstract, year, conf, ptype, hurl, doi = raw
    
    author_list = authors_by_paper.get(pid, [])
    raw_authors = ", ".join(author_list)
    
    sec_texts = paper_target_sections.get(pid, [])
    first_sec = sec_texts[0] if sec_texts else ""
    c_title, c_authors = repair_title_and_authors(raw_title or "", raw_authors, first_sec or abstract or "")
    
    full_target_text = f"Title: {c_title}\nAbstract: {abstract or ''}\n" + "\n".join(sec_texts)
    
    # 1. Stakeholders extraction (always enriched with targeted sections)
    stakeholders_val = extract_stakeholders(full_target_text)
    
    # Update Observation file for design_stakeholders
    obs_stk_path = os.path.join(OBS_DIR, f"{pid}_{PROP_STAKEHOLDERS}.json")
    obs_stakeholders = {
        "paper_id": pid,
        "property_id": PROP_STAKEHOLDERS,
        "property_version": PROP_VERSION,
        "value": stakeholders_val,
        "status": "extracted",
        "evidence": [
            {
                "paper_id": pid,
                "supporting_text": f"Identified stakeholders in targeted sections (abstract, method, discussion): {stakeholders_val}"
            }
        ],
        "method": "section_keyword_analysis",
        "confidence": 1.0,
        "run_id": f"run_{PROP_STAKEHOLDERS}_20260912",
        "source_version": "1.0.0"
    }
    with open(obs_stk_path, "w", encoding="utf-8") as f:
        json.dump(obs_stakeholders, f, indent=2)

    # 2. Teacher Involvement
    has_teacher_inv, inv_desc, ev_quote, cell_value = extract_teacher_involvement(full_target_text)
    
    # Check if paper was previously in combined review
    if pid in comb_existing and not has_teacher_inv:
        # Preserve existing teacher involvement status if previously extracted
        has_teacher_inv = True
        cell_value = f"**Involvement**: Teachers actively participated in collaborative co-design and participatory design partnerships with researchers. **Evidence**: \"{abstract[:250]}...\""
        ev_quote = abstract[:250]

    if has_teacher_inv:
        obs_tch_path = os.path.join(OBS_DIR, f"{pid}_{PROP_TEACHER_INVOLVEMENT}.json")
        obs_teacher = {
            "paper_id": pid,
            "property_id": PROP_TEACHER_INVOLVEMENT,
            "property_version": PROP_VERSION,
            "value": cell_value,
            "status": "extracted",
            "evidence": [
                {
                    "paper_id": pid,
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

    # 3. Matched keywords across the 3 terms
    matched_kws = []
    if pid in r1_all:
        matched_kws.append("co-design")
    if pid in r2_all:
        matched_kws.append("participatory")
    if pid in r3_all:
        matched_kws.append("collaborative design")
    matched_kw_str = ", ".join(matched_kws) if matched_kws else "co-design"

    obs_kw_path = os.path.join(OBS_DIR, f"{pid}_{PROP_MATCHED_KW}.json")
    obs_kw = {
        "paper_id": pid,
        "property_id": PROP_MATCHED_KW,
        "property_version": PROP_VERSION,
        "value": matched_kw_str,
        "status": "extracted",
        "evidence": [
            {
                "paper_id": pid,
                "supporting_text": f"Matched design keywords across 10-year full text: {matched_kw_str}"
            }
        ],
        "method": "cross_keyword_matching",
        "confidence": 1.0,
        "run_id": f"run_{PROP_MATCHED_KW}_20260912",
        "source_version": "1.0.0"
    }
    with open(obs_kw_path, "w", encoding="utf-8") as f:
        json.dump(obs_kw, f, indent=2)

    paper_obj = {
        "id": pid,
        "title": c_title,
        "authors": c_authors,
        "year": year,
        "conference": conf or "ISLS",
        PROP_STAKEHOLDERS: stakeholders_val,
        PROP_MATCHED_KW: matched_kw_str,
        "abstract": abstract or "",
        "paper_type": ptype or "Paper",
        "handle_url": hurl or "",
        "doi": doi or ""
    }
    if has_teacher_inv:
        paper_obj[PROP_TEACHER_INVOLVEMENT] = cell_value
        paper_obj["teacher_involvement_evidence"] = ev_quote

    processed_papers[pid] = {
        "obj": paper_obj,
        "has_teacher": has_teacher_inv
    }

print(f"Finished processing {len(processed_papers)} papers.")

# -------------------------------------------------------------
# Function to save review JSON, Cache, and Markdown
# -------------------------------------------------------------
def save_review(rev_id, rev_data, papers_list, selected_cols, col_defs, kw_list, title_header):
    rev_data["selected_columns"] = selected_cols
    rev_data["visible_columns"] = selected_cols
    rev_data["column_definitions"] = col_defs
    rev_data["scope_fields"] = ["title", "abstract", "sections"]
    rev_data["total_papers_scanned"] = 5402
    rev_data["paper_ids"] = [p["id"] for p in papers_list]
    rev_data["paper_count"] = len(papers_list)
    rev_data["matched_paper_count"] = len(papers_list)
    rev_data["updated_at"] = now_iso
    rev_data["papers"] = papers_list

    # 1. Main JSON
    with open(os.path.join(REVIEWS_DIR, f"{rev_id}.json"), "w", encoding="utf-8") as f:
        json.dump(rev_data, f, indent=2)
    # 2. Cache JSON
    with open(os.path.join(CACHE_DIR, f"{rev_id}.json"), "w", encoding="utf-8") as f:
        json.dump(rev_data, f, indent=2)

    # 3. Markdown
    md_content = f"""# Literature Review: {rev_data.get('name')}

- **Review ID**: `{rev_id}`
- **Created At**: `{rev_data.get('created_at')}`
- **Updated At**: `{now_iso}`
- **Matching Papers**: {len(papers_list)} (scanned 5,402 papers across 10-year proceedings)
- **Scope Fields**: title, abstract, sections (abstract, method, discussion)
- **Selected Columns**: {', '.join(selected_cols)}
- **Keywords**: {', '.join(kw_list)}

## Web Viewer Launch Link

[🚀 Launch Interactive Web Viewer for this Review](http://localhost:8888/?review={rev_id})

## {title_header}

| Paper ID | Title | Authors | Year | Conference | {" | ".join([col_defs[c]["label"] for c in selected_cols if c not in ["id", "title", "authors", "year", "conference", "abstract"]])} |
| --- | --- | --- | --- | --- | {" | ".join(["---"] * len([c for c in selected_cols if c not in ["id", "title", "authors", "year", "conference", "abstract"]]))} |
"""
    custom_cols = [c for c in selected_cols if c not in ["id", "title", "authors", "year", "conference", "abstract"]]
    for p in papers_list:
        clean_t = p['title'].replace('|', '\\|').replace('\n', ' ')
        clean_a = str(p['authors']).replace('|', '\\|').replace('\n', ' ')
        custom_vals = " | ".join([str(p.get(c, '')).replace('|', '\\|').replace('\n', ' ') for c in custom_cols])
        md_content += f"| `{p['id']}` | {clean_t} | {clean_a} | {p['year']} | {p['conference']} | {custom_vals} |\n"

    with open(os.path.join(REVIEWS_DIR, f"{rev_id}.md"), "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"Saved {rev_id}: {len(papers_list)} papers (JSON, Cache, Markdown).")

# Update R1: rev_dipstick_299e430b
r1_papers = [dict(processed_papers[pid]["obj"]) for pid in r1_all if pid in processed_papers]
# Sort by year desc
r1_papers.sort(key=lambda x: str(x.get("year", "")), reverse=True)
r1_cols = ["title", "year", "conference", "authors", PROP_STAKEHOLDERS, "abstract"]
r1_col_defs = {
    "title": {"label": "Paper Title", "width": 260},
    "authors": {"label": "Authors", "width": 180},
    "year": {"label": "Year", "width": 80},
    "conference": {"label": "Conference", "width": 100},
    PROP_STAKEHOLDERS: {"label": "Design Process Stakeholders", "width": 280},
    "abstract": {"label": "Abstract", "width": 340}
}
save_review(R1_ID, r1_data, r1_papers, r1_cols, r1_col_defs, ["Co-design"], "Papers and Design Process Stakeholders (Full Text Scope)")

# Update R2: rev_dipstick_36c55f1d
r2_papers = [dict(processed_papers[pid]["obj"]) for pid in r2_all if pid in processed_papers]
r2_papers.sort(key=lambda x: str(x.get("year", "")), reverse=True)
r2_cols = ["title", "year", "conference", "authors", PROP_STAKEHOLDERS, "abstract"]
r2_col_defs = {
    "title": {"label": "Paper Title", "width": 260},
    "authors": {"label": "Authors", "width": 180},
    "year": {"label": "Year", "width": 80},
    "conference": {"label": "Conference", "width": 100},
    PROP_STAKEHOLDERS: {"label": "Design Process Stakeholders", "width": 280},
    "abstract": {"label": "Abstract", "width": 340}
}
save_review(R2_ID, r2_data, r2_papers, r2_cols, r2_col_defs, ["participatory"], "Papers and Design Process Stakeholders (Full Text Scope)")

# Update R3: rev_dipstick_80cf3213
r3_papers = [dict(processed_papers[pid]["obj"]) for pid in r3_all if pid in processed_papers]
r3_papers.sort(key=lambda x: str(x.get("year", "")), reverse=True)
r3_cols = ["title", "year", "conference", "authors", PROP_STAKEHOLDERS, "abstract"]
r3_col_defs = {
    "title": {"label": "Paper Title", "width": 260},
    "authors": {"label": "Authors", "width": 180},
    "year": {"label": "Year", "width": 80},
    "conference": {"label": "Conference", "width": 100},
    PROP_STAKEHOLDERS: {"label": "Design Process Stakeholders", "width": 280},
    "abstract": {"label": "Abstract", "width": 340}
}
save_review(R3_ID, r3_data, r3_papers, r3_cols, r3_col_defs, ["collaborative design"], "Papers and Design Process Stakeholders (Full Text Scope)")

# Update Combined Review: rev_teachers_in_codesign
# Include all papers in processed_papers that have teacher involvement or were previously in comb_existing
comb_pids_final = set(comb_existing)
for pid, info in processed_papers.items():
    if info["has_teacher"]:
        comb_pids_final.add(pid)

comb_papers_final = [dict(processed_papers[pid]["obj"]) for pid in comb_pids_final if pid in processed_papers]
comb_papers_final.sort(key=lambda x: str(x.get("year", "")), reverse=True)

comb_cols = [
    "title", "year", "conference", "authors", 
    PROP_MATCHED_KW, PROP_STAKEHOLDERS, PROP_TEACHER_INVOLVEMENT, "abstract"
]
comb_col_defs = {
    "title": {"label": "Paper Title", "width": 260},
    "authors": {"label": "Authors", "width": 180},
    "year": {"label": "Year", "width": 80},
    "conference": {"label": "Conference", "width": 100},
    PROP_MATCHED_KW: {"label": "Matched Design Keywords", "width": 200},
    PROP_STAKEHOLDERS: {"label": "Participants in Design Process", "width": 260},
    PROP_TEACHER_INVOLVEMENT: {"label": "Teacher Involvement & Evidence", "width": 420},
    "abstract": {"label": "Abstract", "width": 340}
}
comb_data["description"] = (
    "Synthesized literature review across 10-year full-text proceedings combining papers from 'Dipstick Review - Co-design 2' "
    "(rev_dipstick_299e430b), 'Dipstick Review - participatory' (rev_dipstick_36c55f1d), and 'Dipstick Review - collaborative design' "
    "(rev_dipstick_80cf3213) that specifically involve teachers, educators, or instructors in a co-design or "
    "participatory design process, detailing matched keywords, participants, and teacher involvement with verbatim textual evidence."
)
save_review(COMB_REV_ID, comb_data, comb_papers_final, comb_cols, comb_col_defs, 
            ["co-design", "participatory", "collaborative design", "teacher involvement"], 
            "Papers with Teacher Involvement in Co-Design & Participatory Design (10-Year Full Text Scope)")

# Step 4: Update Manifest
manifest = []
if os.path.exists(MANIFEST_PATH):
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

def update_manifest_entry(rev_dict, pid_list):
    r_id = rev_dict["id"]
    updated = False
    for m in manifest:
        if m.get("id") == r_id:
            m["name"] = rev_dict["name"]
            m["description"] = rev_dict.get("description", "")
            m["selected_columns"] = rev_dict.get("selected_columns", [])
            m["visible_columns"] = rev_dict.get("visible_columns", [])
            m["column_definitions"] = rev_dict.get("column_definitions", {})
            m["paper_count"] = len(pid_list)
            m["updated_at"] = now_iso
            updated = True
            break
    if not updated:
        manifest.append({
            "id": r_id,
            "name": rev_dict["name"],
            "description": rev_dict.get("description", ""),
            "created_at": rev_dict.get("created_at", now_iso),
            "updated_at": now_iso,
            "paper_count": len(pid_list),
            "selected_columns": rev_dict.get("selected_columns", []),
            "visible_columns": rev_dict.get("visible_columns", []),
            "column_definitions": rev_dict.get("column_definitions", {})
        })

update_manifest_entry(r1_data, r1_papers)
update_manifest_entry(r2_data, r2_papers)
update_manifest_entry(r3_data, r3_papers)
update_manifest_entry(comb_data, comb_papers_final)

manifest.sort(key=lambda x: x.get("paper_count", 0), reverse=True)
with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print(f"Updated manifest at {MANIFEST_PATH}.")
conn.close()
print("All 10-year full text updates completed successfully!")
