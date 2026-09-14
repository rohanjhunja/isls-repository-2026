import sqlite3
import json
import re
import os
import shutil

DATABASE_NAMES = [
    'Web of Science', 'Scopus', 'ERIC', 'PsycINFO', 'PubMed', 'ACM Digital Library', 
    'IEEE Xplore', 'Google Scholar', 'SpringerLink', 'ScienceDirect', 'Wiley',
    'Taylor & Francis', 'JSTOR', 'SAGE', 'ProQuest', 'CINAHL'
]

PATTERN_KEYWORDS = [
    'Systematic Review', 'Scoping Review', 'Meta-Analysis', 'Umbrella Review', 'Systematic Scoping Review',
    'PRISMA', 'Bibliographic Coupling', 'Participatory Design', 'Empirical Synthesis',
    'Generative AI', 'Large Language Models', 'ChatGPT', 'Learning Analytics', 'Virtual Reality',
    'Electrodermal Activity', 'Biosensors', 'Digital Learning Games', 'Wearable Technology',
    'Collaborative Learning', 'Self-Regulated Learning', 'Executive Functions', 'Growth Mindset',
    'Intersubjectivity', 'Computational Thinking', 'Teacher Noticing', 'Algorithmic Literacy',
    'Socioscientific Issues', 'Digital Literacy', 'Open Educational Resources', 'Student Agency',
    'K-12 Education', 'Higher Education', 'Algebra Domain', 'Arts Learning', 'Physical Education',
    'Inclusive Education', 'Climate Change Education'
]

COLUMN_DEFINITIONS = {
    "title": {"label": "Paper Title", "width": 260},
    "authors": {"label": "Authors", "width": 180},
    "year": {"label": "Year", "width": 80},
    "conference": {"label": "Conference", "width": 100},
    "databases_searched": {"label": "Databases Searched", "width": 160},
    "summary": {"label": "~50-Word Summary (RQ, Finding, Relevance)", "width": 320},
    "keywords": {"label": "Keywords (Up to 5)", "width": 200},
    "abstract": {"label": "Abstract", "width": 340}
}

def clean_text_artifacts(text):
    if not text:
        return ""
    text = re.sub(r'\.{3,}', '...', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def extract_databases_searched(sections):
    found_dbs = []
    for sec in sections:
        heading = (sec.get('heading') or '').lower()
        text = sec.get('text') or ''
        search_blob = f"{heading} {text}"
        for db in DATABASE_NAMES:
            if re.search(r'\b' + re.escape(db) + r'\b', search_blob, re.I):
                if db not in found_dbs:
                    found_dbs.append(db)
    return found_dbs if found_dbs else ["Not specified in paper text"]

def extract_title_abstract_keywords(title, abstract, raw_keywords_field):
    text_source = f"{title} {abstract}".lower()
    found = []

    if isinstance(raw_keywords_field, list):
        for k in raw_keywords_field:
            if isinstance(k, str) and k.strip():
                clean_k = k.strip().title()
                if clean_k.lower() != 'education research' and clean_k.lower() not in [x.lower() for x in found]:
                    found.append(clean_k)

    for pattern in PATTERN_KEYWORDS:
        if len(found) >= 5:
            break
        if pattern.lower() in text_source and pattern.lower() not in [x.lower() for x in found]:
            found.append(pattern)

    return found[:5]

def generate_50_word_summary(title, abstract):
    abstract = abstract or ''
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', abstract) if s.strip()]

    obj_sentence = sentences[0] if sentences else title

    finding_sentence = ''
    for s in sentences[1:]:
        if any(w in s.lower() for w in ['find', 'result', 'reveal', 'show', 'identify', 'indicate', 'demonstrate', 'conclude']):
            finding_sentence = s
            break
    if not finding_sentence and len(sentences) > 1:
        finding_sentence = sentences[1]

    rel_sentence = ''
    for s in sentences:
        if any(w in s.lower() for w in ['highlight', 'suggest', 'provide', 'implication', 'recommend', 'practice', 'guidance', 'design', 'future', 'policy']):
            if s != obj_sentence and s != finding_sentence:
                rel_sentence = s
                break

    parts = [f"**RQ/Objective**: {obj_sentence}"]
    if finding_sentence:
        parts.append(f"**Finding**: {finding_sentence}")
    if rel_sentence:
        parts.append(f"**Relevance**: {rel_sentence}")

    combined = " ".join(parts).strip()
    words = combined.split()

    if len(words) > 60:
        combined = " ".join(words[:52]) + "..."
    elif len(words) < 35 and len(abstract.split()) > 35:
        combined = " ".join(abstract.split()[:50]) + "..."

    return combined

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from proceedings_ingest.utils.text_cleanup import repair_title_and_authors, clean_section_blocks

def fetch_paper_full_obj(pid, cursor):
    row = cursor.execute('SELECT data_json FROM papers WHERE id = ?', (pid,)).fetchone()
    if not row or not row[0]:
        return None
    db_data = json.loads(row[0])

    sec_rows = cursor.execute(
        'SELECT section_id, heading_original, canonical_roles, text, pdf_page_start, pdf_page_end FROM sections_fts WHERE paper_id = ? ORDER BY section_id ASC',
        (pid,)
    ).fetchall()

    raw_sections = [{
        'section_id': s[0], 'heading': s[1], 'canonical_role': s[2],
        'text': clean_text_artifacts(s[3]), 'pdf_page_start': s[4], 'pdf_page_end': s[5]
    } for s in sec_rows]

    first_sec_text = raw_sections[0]['text'] if raw_sections else ''
    raw_title = db_data.get('title', pid)
    raw_authors = ", ".join([a.get('display_name', '') if isinstance(a, dict) else str(a) for a in db_data.get('authors', [])])
    r_title, r_authors = repair_title_and_authors(raw_title, raw_authors, first_sec_text)
    sections = clean_section_blocks(raw_sections)

    abstract = db_data.get('abstract') or ""
    databases_searched = extract_databases_searched(sections)
    keywords = extract_title_abstract_keywords(r_title, abstract, db_data.get('keywords', []))
    summary = generate_50_word_summary(r_title, abstract)

    full_text = "\n\n".join([
        f"### {sec['heading'] or 'Section'} (Pages {sec['pdf_page_start']}-{sec['pdf_page_end']})\n{sec['text']}"
        for sec in sections
    ])

    return {
        'id': pid,
        'title': r_title,
        'authors': r_authors,
        'year': db_data.get('year', ''),
        'conference': db_data.get('conference', {}).get('acronym', 'ISLS') if isinstance(db_data.get('conference'), dict) else 'ISLS',
        'abstract': abstract,
        'summary': summary,
        'keywords': keywords,
        'databases_searched': databases_searched,
        'matched_search_terms': ['literature review'],
        'sections': sections,
        'full_text': full_text,
        'filename': db_data.get('filename', ''),
        'pages': f"{db_data.get('pages', {}).get('start', '')}-{db_data.get('pages', {}).get('end', '')}"
    }

def main():
    reviews_dir = 'data/reviews'
    cache_dir = 'data/derived/reviews_cache'

    # Clean up test reviews
    test_files = ['rev_a1394665.json', 'rev_a1394665.md', 'rev_a0f560c6.json', 'rev_a0f560c6.md', 'rev_6d2907a6.json', 'rev_6d2907a6.md']
    for tf in test_files:
        p = os.path.join(reviews_dir, tf)
        if os.path.exists(p):
            os.remove(p)
            print(f"Removed test review artifact: {tf}")

    conn = sqlite3.connect('data/index/proceedings.db')
    cursor = conn.cursor()

    # 1. Review 1: Systematic Review Literature Review (2023-2026)
    with open('data/viewer_papers.json', 'r', encoding='utf-8') as f:
        sys_papers = json.load(f)

    rev1 = {
        'id': 'rev_systematic_review_2026',
        'name': 'Systematic Review Literature Review (2023-2026)',
        'description': 'Comprehensive literature review of 68 papers focusing on systematic reviews, scoping reviews, meta-analyses, and umbrella reviews.',
        'created_at': '2026-07-24T14:50:00',
        'selected_columns': ["title", "authors", "year", "databases_searched", "summary", "keywords", "abstract"],
        'column_definitions': COLUMN_DEFINITIONS,
        'paper_count': len(sys_papers),
        'papers': sys_papers
    }
    with open(os.path.join(reviews_dir, 'systematic_review_lit_review.json'), 'w', encoding='utf-8') as f:
        json.dump(rev1, f, indent=2)

    # 2. Review 2: ISLS 2023 Scoped Learning Review
    rows_2023 = cursor.execute('SELECT id, data_json FROM papers').fetchall()
    pids_2023 = []
    for pid, dj in rows_2023:
        data = json.loads(dj) if dj else {}
        if data.get('year') == 2023 or data.get('year') == '2023':
            t = (data.get('title') or '').lower()
            a = (data.get('abstract') or '').lower()
            if 'learning' in t or 'learning' in a:
                pids_2023.append(pid)

    papers_rev2 = []
    for pid in pids_2023[:100]:
        pobj = fetch_paper_full_obj(pid, cursor)
        if pobj: papers_rev2.append(pobj)

    rev2 = {
        'id': 'rev_isls_2023_learning',
        'name': 'ISLS 2023 Collaborative Learning Review',
        'description': 'Scoped literature review of 100 featured ISLS 2023 papers investigating collaborative learning, epistemic artifacts, and peer interaction.',
        'created_at': '2026-07-24T16:00:00',
        'selected_columns': ["title", "authors", "year", "conference", "keywords", "abstract"],
        'column_definitions': COLUMN_DEFINITIONS,
        'paper_count': len(papers_rev2),
        'papers': papers_rev2
    }
    with open(os.path.join(reviews_dir, 'rev_isls_2023_learning.json'), 'w', encoding='utf-8') as f:
        json.dump(rev2, f, indent=2)

    # 3. Review 3: Generative AI & LLM Applications Review
    pids_genai = []
    for pid, dj in rows_2023:
        data = json.loads(dj) if dj else {}
        t = (data.get('title') or '').lower()
        a = (data.get('abstract') or '').lower()
        text = t + ' ' + a
        if any(kw in text for kw in ['generative ai', 'large language model', 'chatgpt', 'llm', 'artificial intelligence']):
            pids_genai.append(pid)

    papers_rev3 = []
    for pid in pids_genai:
        pobj = fetch_paper_full_obj(pid, cursor)
        if pobj: papers_rev3.append(pobj)

    rev3 = {
        'id': 'rev_genai_llm_2024_2026',
        'name': 'Generative AI & LLM Education Review',
        'description': 'Targeted literature review of papers investigating Large Language Models, ChatGPT feedback, and generative AI tools in K-12 and higher education.',
        'created_at': '2026-07-24T16:15:00',
        'selected_columns': ["title", "authors", "year", "databases_searched", "summary", "keywords"],
        'column_definitions': COLUMN_DEFINITIONS,
        'paper_count': len(papers_rev3),
        'papers': papers_rev3
    }
    with open(os.path.join(reviews_dir, 'rev_genai_llm_2024_2026.json'), 'w', encoding='utf-8') as f:
        json.dump(rev3, f, indent=2)

    # Rebuild cache and manifest
    os.makedirs(cache_dir, exist_ok=True)
    manifest = []
    for r in [rev1, rev2, rev3]:
        cache_path = os.path.join(cache_dir, f"{r['id']}.json")
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(r, f, indent=2)
        manifest.append({
            'id': r['id'],
            'name': r['name'],
            'description': r['description'],
            'created_at': r['created_at'],
            'paper_count': r['paper_count'],
            'selected_columns': r['selected_columns'],
            'column_definitions': r['column_definitions']
        })

    with open(os.path.join(cache_dir, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print("Cleaned test reviews and generated 3 distinct literature review collections with unique column configurations!")

if __name__ == '__main__':
    main()
