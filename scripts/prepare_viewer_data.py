import sqlite3
import json
import re
import os

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from proceedings_ingest.utils.text_cleanup import repair_title_and_authors, clean_section_blocks

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
        role = (sec.get('canonical_role') or '').lower()
        text = sec.get('text') or ''
        
        # Priority check in methods, search strategy, literature review or methodology sections
        search_blob = f"{heading} {text}"
        for db in DATABASE_NAMES:
            if re.search(r'\b' + re.escape(db) + r'\b', search_blob, re.I):
                if db not in found_dbs:
                    found_dbs.append(db)
                    
    return found_dbs if found_dbs else ["Not specified in paper text"]

def extract_title_abstract_keywords(title, abstract, raw_keywords_field):
    text_source = f"{title} {abstract}".lower()
    found = []

    # Check explicit keywords field if present
    if isinstance(raw_keywords_field, list):
        for k in raw_keywords_field:
            if isinstance(k, str) and k.strip():
                clean_k = k.strip().title()
                if clean_k.lower() != 'education research' and clean_k.lower() not in [x.lower() for x in found]:
                    found.append(clean_k)

    # Match pattern keywords from Title and Abstract ONLY
    for pattern in PATTERN_KEYWORDS:
        if len(found) >= 5:
            break
        if pattern.lower() in text_source and pattern.lower() not in [x.lower() for x in found]:
            found.append(pattern)

    # Return up to 5 unique keywords (no generic fillers)
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

def main():
    db_path = 'data/index/proceedings.db'
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open('data/processed_sys_reviews.json', 'r', encoding='utf-8') as f:
        processed_papers = json.load(f)

    viewer_papers = []

    for p in processed_papers:
        pid = p['id']
        row = cursor.execute('SELECT data_json FROM papers WHERE id = ?', (pid,)).fetchone()
        data = json.loads(row[0]) if row and row[0] else {}

        sec_rows = cursor.execute(
            'SELECT section_id, heading_original, canonical_roles, text, pdf_page_start, pdf_page_end FROM sections_fts WHERE paper_id = ? ORDER BY section_id ASC',
            (pid,)
        ).fetchall()

        raw_sections = []
        for s in sec_rows:
            raw_sections.append({
                'section_id': s[0],
                'heading': s[1],
                'canonical_role': s[2],
                'text': clean_text_artifacts(s[3]),
                'pdf_page_start': s[4],
                'pdf_page_end': s[5]
            })

        first_sec_text = raw_sections[0]['text'] if raw_sections else ''
        repaired_title, repaired_authors = repair_title_and_authors(
            p['title'], p['authors'], first_sec_text
        )
        sections = clean_section_blocks(raw_sections)

        databases_searched = extract_databases_searched(sections)
        keywords = extract_title_abstract_keywords(repaired_title, p['abstract'], p.get('keywords_field'))
        summary_50 = generate_50_word_summary(repaired_title, p['abstract'])

        full_text = "\n\n".join([
            f"### {sec['heading'] or 'Section'} (Pages {sec['pdf_page_start']}-{sec['pdf_page_end']})\n{sec['text']}"
            for sec in sections
        ])

        viewer_papers.append({
            'id': pid,
            'title': repaired_title,
            'authors': repaired_authors,
            'year': p['year'],
            'conference': data.get('conference', {}).get('acronym', 'ISLS') if isinstance(data.get('conference'), dict) else 'ISLS',
            'abstract': p['abstract'],
            'summary': summary_50,
            'keywords': keywords,
            'proceedings_section': data.get('proceedings_section', 'General'),
            'databases_searched': databases_searched,
            'matched_search_terms': p['matched_search_terms'],
            'sections': sections,
            'full_text': full_text,
            'filename': data.get('filename', ''),
            'pages': f"{data.get('pages', {}).get('start', '')}-{data.get('pages', {}).get('end', '')}"
        })

    os.makedirs('data/derived', exist_ok=True)
    with open('data/viewer_papers.json', 'w', encoding='utf-8') as f:
        json.dump(viewer_papers, f, indent=2)

    print(f"Successfully updated viewer_papers.json with {len(viewer_papers)} papers.")

if __name__ == '__main__':
    main()
