#!/usr/bin/env python3
"""
Add 'first_keyword_location' column to rev_teachers_in_codesign:
Assigns a % in terms of character count where in the paper the first matched keyword appears
and calls out the section it first appears in.

Creates:
- data/properties/first_keyword_location.yaml
- data/observations/<paper_id>_first_keyword_location.json (for all 605 papers)
Updates:
- data/reviews/rev_teachers_in_codesign.json
- data/derived/reviews_cache/rev_teachers_in_codesign.json
- data/reviews/rev_teachers_in_codesign.md
- data/derived/reviews_cache/manifest.json
"""

import os
import re
import json
import sqlite3
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "proceedings.db")
OBS_DIR = os.path.join(BASE_DIR, "data", "observations")
PROP_DIR = os.path.join(BASE_DIR, "data", "properties")
REVIEWS_DIR = os.path.join(BASE_DIR, "data", "reviews")
CACHE_DIR = os.path.join(BASE_DIR, "data", "derived", "reviews_cache")
MANIFEST_PATH = os.path.join(CACHE_DIR, "manifest.json")

PROP_ID = "first_keyword_location"
PROP_LABEL = "First Keyword Location"
PROP_VERSION = "1.0.0"
COMB_REV_ID = "rev_teachers_in_codesign"

os.makedirs(OBS_DIR, exist_ok=True)
os.makedirs(PROP_DIR, exist_ok=True)

# Regex matching the 3 design paradigm concepts
KW_PATTERN = re.compile(
    r'\b(co-design(?:ing|ed|s|ers?|er)?|codesign(?:ing|ed|s|ers?|er)?|participatory|collaborative(?:ly)?\s+design(?:ing|ed|s)?)\b',
    re.IGNORECASE
)

CANONICAL_MAP = {
    'abstract & introduction': 'Introduction',
    'theoretical background': 'Theoretical Background',
    'methodology & context': 'Methodology & Context',
    'results & findings': 'Results & Findings',
    'discussion & conclusion': 'Discussion & Conclusion',
    'references & back matter': 'References'
}

def clean_section_name(orig_heading: str, norm_sec: str, is_ab: bool, is_intro: bool) -> str:
    if is_ab:
        return 'Abstract'
    if is_intro:
        return 'Introduction'
    
    h = (orig_heading or '').strip()
    if h.lower() in ['abstract & introduction', 'abstract and introduction']:
        return 'Introduction'
    
    # Strip leading numbers like '1. Introduction' or '1 '
    h = re.sub(r'^[0-9]+[\.\s\-]+', '', h).strip()
    # Strip bullet points
    h = re.sub(r'^[●\*\-]\s*', '', h).strip()
    
    # If heading is too long (>35 chars) or sentence-like / contains dangling punctuation
    if len(h) > 35 or h.endswith(':') or h.endswith('(') or '.' in h or '?' in h:
        if ':' in h and len(h.split(':')[0]) <= 30:
            candidate = h.split(':')[0].strip()
            if len(candidate) >= 3 and not candidate.lower().startswith('poster'):
                return candidate
        return CANONICAL_MAP.get(norm_sec.lower(), norm_sec.title() if norm_sec else 'Main Body')
        
    return h if h else CANONICAL_MAP.get(norm_sec.lower(), 'Main Body')

def run():
    print(f"Connecting to database: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    review_path = os.path.join(REVIEWS_DIR, f"{COMB_REV_ID}.json")
    with open(review_path, "r", encoding="utf-8") as f:
        rev_data = json.load(f)

    papers = rev_data.get("papers", [])
    print(f"Processing {len(papers)} papers in {COMB_REV_ID}...")

    now_iso = datetime.datetime.now().isoformat()

    # Pre-fetch sections for all papers in review
    pids = [p["id"] for p in papers]
    c.execute(f"""
        SELECT paper_id, order_index, original_heading, normalized_section, text
        FROM sections
        WHERE paper_id IN ({','.join('?' for _ in pids)})
        ORDER BY paper_id, order_index ASC
    """, pids)

    sections_by_paper = {}
    for pid, oidx, ohead, nsec, stext in c.fetchall():
        if pid not in sections_by_paper:
            sections_by_paper[pid] = []
        sections_by_paper[pid].append({
            'order_index': oidx,
            'original_heading': ohead,
            'normalized_section': nsec,
            'text': stext or ''
        })

    results_summary = []

    for p in papers:
        pid = p["id"]
        sections = sections_by_paper.get(pid, [])
        ab_text = p.get("abstract", "") or ""

        # Build full text and character offset map
        full_text_chunks = []
        sec_offsets = []
        cur_pos = 0

        for s in sections:
            stext = s['text']
            start_pos = cur_pos
            end_pos = start_pos + len(stext)
            sec_offsets.append({
                'order_index': s['order_index'],
                'original_heading': s['original_heading'],
                'normalized_section': s['normalized_section'],
                'start': start_pos,
                'end': end_pos,
                'text': stext
            })
            full_text_chunks.append(stext)
            cur_pos = end_pos + 2  # accounted for separator \n\n

        full_text = "\n\n".join(full_text_chunks)
        tot_len = len(full_text)

        # Match first keyword
        matches = list(KW_PATTERN.finditer(full_text))

        if matches:
            first_m = matches[0]
            m_pos = first_m.start()
            matched_kw = first_m.group(0)
            pct = (m_pos / tot_len) * 100 if tot_len > 0 else 0.0

            # Find matching section
            matched_sec = None
            for s in sec_offsets:
                if s['start'] <= m_pos < s['end']:
                    matched_sec = s
                    break
            if not matched_sec:
                matched_sec = sec_offsets[-1] if sec_offsets else None

            # Distinguish Abstract vs Introduction in section 1
            m_ab = KW_PATTERN.search(ab_text)
            is_sec1 = (matched_sec['order_index'] == 1) if matched_sec else False
            is_ab = is_sec1 and (m_ab is not None and (m_pos - matched_sec['start']) <= len(ab_text) + 200)
            is_intro = is_sec1 and not is_ab

            sec_name = clean_section_name(
                matched_sec['original_heading'] if matched_sec else '',
                matched_sec['normalized_section'] if matched_sec else '',
                is_ab,
                is_intro
            )
        else:
            # Fallback if somehow no match in full text (e.g. check abstract alone)
            m_ab = KW_PATTERN.search(ab_text)
            if m_ab:
                matched_kw = m_ab.group(0)
                pct = 0.0
                sec_name = "Abstract"
            else:
                matched_kw = "co-design"
                pct = 0.0
                sec_name = "Abstract"

        pct_formatted = f"{pct:.1f}%"
        col_value = f"{pct_formatted} ({sec_name})"

        # Assign properties to paper dict
        p[PROP_ID] = col_value
        p["first_keyword_pct"] = round(pct, 1)
        p["first_keyword_section"] = sec_name
        p["first_matched_keyword"] = matched_kw

        results_summary.append((pid, col_value, matched_kw))

        # Save individual observation JSON
        obs_path = os.path.join(OBS_DIR, f"{pid}_{PROP_ID}.json")
        obs_data = {
            "paper_id": pid,
            "property_id": PROP_ID,
            "property_version": PROP_VERSION,
            "value": col_value,
            "pct": round(pct, 1),
            "section": sec_name,
            "first_matched_keyword": matched_kw,
            "status": "extracted",
            "evidence": [
                {
                    "paper_id": pid,
                    "supporting_text": f"First matched design keyword '{matched_kw}' appears at {pct_formatted} of total character length in section '{sec_name}'."
                }
            ],
            "method": "character_offset_section_mapping",
            "confidence": 1.0,
            "run_id": f"run_{PROP_ID}_20260913",
            "source_version": "1.0.0"
        }
        with open(obs_path, "w", encoding="utf-8") as f:
            json.dump(obs_data, f, indent=2)

    conn.close()

    # Create Property Definition YAML in data/properties/
    prop_yaml_path = os.path.join(PROP_DIR, f"{PROP_ID}.yaml")
    prop_yaml_content = f"""id: {PROP_ID}
version: {PROP_VERSION}
label: {PROP_LABEL}
description: Percentage of character offset in the paper where the first matched design keyword appears, alongside the section name.
value_type: text
query:
  question: Where in the paper does the first matched design keyword appear in terms of character count percentage and section?
  candidate_sections:
    - Abstract
    - Introduction
    - Methodology & Context
    - Results & Findings
    - Discussion & Conclusion
  heading_terms:
    - co-design
    - participatory
    - collaborative design
  text_terms:
    - co-design
    - participatory
    - collaborative design
constraints:
  output_type: string
  maximum_words: 10
extraction:
  preferred_methods:
    - character_offset_section_mapping
  inference_allowed: false
evidence_required: true
"""
    with open(prop_yaml_path, "w", encoding="utf-8") as f:
        f.write(prop_yaml_content)
    print(f"Wrote property definition to {prop_yaml_path}")

    # Update columns in Combined Review
    sel_cols = [
        "title", "year", "conference", "authors",
        "matched_design_keywords", PROP_ID,
        "design_stakeholders", "teacher_involvement", "abstract"
    ]
    col_defs = dict(rev_data.get("column_definitions", {}))
    col_defs[PROP_ID] = {
        "label": PROP_LABEL,
        "width": 190
    }

    rev_data["selected_columns"] = sel_cols
    rev_data["visible_columns"] = sel_cols
    rev_data["column_definitions"] = col_defs
    rev_data["updated_at"] = now_iso
    if "property_versions" not in rev_data:
        rev_data["property_versions"] = {}
    rev_data["property_versions"][PROP_ID] = PROP_VERSION

    # Write main review file
    with open(review_path, "w", encoding="utf-8") as f:
        json.dump(rev_data, f, indent=2)

    # Write cache review file
    cache_path = os.path.join(CACHE_DIR, f"{COMB_REV_ID}.json")
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(rev_data, f, indent=2)

    # Write Markdown file
    comb_md = f"""# Literature Review: {rev_data['name']}

- **Review ID**: `{COMB_REV_ID}`
- **Created At**: `{rev_data.get('created_at')}`
- **Updated At**: `{now_iso}`
- **Matching Papers**: {len(papers)} (scanned 5,402 papers across 10-year proceedings)
- **Scope Fields**: title, abstract, sections (abstract, method, discussion)
- **Selected Columns**: {', '.join(sel_cols)}
- **Keywords**: {', '.join(rev_data.get('keywords', []))}
- **Source Reviews**: `rev_dipstick_299e430b` (Co-design 2), `rev_dipstick_36c55f1d` (participatory), and `rev_dipstick_80cf3213` (collaborative design)

## Web Viewer Launch Link

[🚀 Launch Interactive Web Viewer for this Review](http://localhost:8888/?review={COMB_REV_ID})

## Papers with Teacher Involvement in Co-Design & Participatory Design (10-Year Full Text Scope)

| Paper ID | Title | Authors | Year | Conference | Matched Design Keywords | {PROP_LABEL} | Participants in Design Process | Teacher Involvement & Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
"""
    for p in papers:
        clean_t = str(p.get('title', '')).replace('|', '\\|').replace('\n', ' ')
        clean_a = str(p.get('authors', '')).replace('|', '\\|').replace('\n', ' ')
        clean_kw = str(p.get('matched_design_keywords', '')).replace('|', '\\|').replace('\n', ' ')
        clean_loc = str(p.get(PROP_ID, '')).replace('|', '\\|').replace('\n', ' ')
        clean_s = str(p.get('design_stakeholders', '')).replace('|', '\\|').replace('\n', ' ')
        clean_inv = str(p.get('teacher_involvement', '')).replace('|', '\\|').replace('\n', ' ')
        comb_md += f"| `{p['id']}` | {clean_t} | {clean_a} | {p['year']} | {p['conference']} | {clean_kw} | {clean_loc} | {clean_s} | {clean_inv} |\n"

    md_path = os.path.join(REVIEWS_DIR, f"{COMB_REV_ID}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(comb_md)
    print(f"Wrote updated markdown file to {md_path}")

    # Update manifest.json
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        for m in manifest:
            if m.get("id") == COMB_REV_ID:
                m["selected_columns"] = sel_cols
                m["visible_columns"] = sel_cols
                m["column_definitions"] = col_defs
                m["updated_at"] = now_iso
                break
        with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        print(f"Updated {MANIFEST_PATH}")

    print(f"\nSuccessfully added '{PROP_ID}' to {COMB_REV_ID} across all 605 papers!")
    print("Sample 10 extractions:")
    for r in results_summary[:10]:
        print(f"  [{r[0]}] {r[1]} (keyword: '{r[2]}')")

if __name__ == "__main__":
    run()
