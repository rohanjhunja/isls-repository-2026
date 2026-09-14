import sqlite3
import json
import re
import os

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

def process_review_file(filepath, cursor, output_dir):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    review_id = data.get('id', os.path.basename(filepath).replace('.json', ''))
    review_name = data.get('name', review_id)
    description = data.get('description', '')

    paper_objs = []
    raw_papers = data.get('papers', [])
    paper_ids = data.get('paper_ids', [])

    if raw_papers:
        for p in raw_papers:
            pid = p['id']
            row = cursor.execute('SELECT data_json FROM papers WHERE id = ?', (pid,)).fetchone()
            db_data = json.loads(row[0]) if row and row[0] else {}

            sec_rows = cursor.execute(
                'SELECT section_id, heading_original, canonical_roles, text, pdf_page_start, pdf_page_end FROM sections_fts WHERE paper_id = ? ORDER BY section_id ASC',
                (pid,)
            ).fetchall()

            raw_sections = [{
                'section_id': s[0], 'heading': s[1], 'canonical_role': s[2],
                'text': clean_text_artifacts(s[3]), 'pdf_page_start': s[4], 'pdf_page_end': s[5]
            } for s in sec_rows]

            first_sec_text = raw_sections[0]['text'] if raw_sections else ''
            r_title, r_authors = repair_title_and_authors(p['title'], p['authors'], first_sec_text)
            sections = clean_section_blocks(raw_sections)
            databases_searched = p.get('databases_searched') or extract_databases_searched(sections)
            keywords = p.get('keywords') or extract_title_abstract_keywords(r_title, p.get('abstract', ''), p.get('keywords_field'))
            summary_50 = p.get('summary') or generate_50_word_summary(r_title, p.get('abstract', ''))

            full_text = "\n\n".join([
                f"### {sec['heading'] or 'Section'} (Pages {sec['pdf_page_start']}-{sec['pdf_page_end']})\n{sec['text']}"
                for sec in sections
            ])

            # Start with all existing attributes from p (preserving custom properties like reviews_referenced)
            p_obj = dict(p)
            p_obj.update({
                'id': pid,
                'title': r_title,
                'authors': r_authors,
                'year': p.get('year', db_data.get('year', '')),
                'conference': db_data.get('conference', {}).get('acronym', 'ISLS') if isinstance(db_data.get('conference'), dict) else 'ISLS',
                'abstract': p.get('abstract', db_data.get('abstract', '')),
                'summary': summary_50,
                'keywords': keywords,
                'databases_searched': databases_searched,
                'matched_search_terms': p.get('matched_search_terms', []),
                'sections': sections,
                'full_text': full_text,
                'filename': db_data.get('filename', ''),
                'pages': f"{db_data.get('pages', {}).get('start', '')}-{db_data.get('pages', {}).get('end', '')}"
            })
            paper_objs.append(p_obj)

    elif paper_ids:
        for pid in paper_ids:
            row = cursor.execute('SELECT data_json FROM papers WHERE id = ?', (pid,)).fetchone()
            if not row or not row[0]:
                continue
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

            abstract = db_data.get('abstract', '')
            databases_searched = extract_databases_searched(sections)
            keywords = extract_title_abstract_keywords(r_title, abstract, db_data.get('keywords', []))
            summary_50 = generate_50_word_summary(r_title, abstract)

            full_text = "\n\n".join([
                f"### {sec['heading'] or 'Section'} (Pages {sec['pdf_page_start']}-{sec['pdf_page_end']})\n{sec['text']}"
                for sec in sections
            ])

            paper_objs.append({
                'id': pid,
                'title': r_title,
                'authors': r_authors,
                'year': db_data.get('year', ''),
                'conference': db_data.get('conference', {}).get('acronym', 'ISLS') if isinstance(db_data.get('conference'), dict) else 'ISLS',
                'abstract': abstract,
                'summary': summary_50,
                'keywords': keywords,
                'databases_searched': databases_searched,
                'matched_search_terms': ['literature review'],
                'sections': sections,
                'full_text': full_text,
                'filename': db_data.get('filename', ''),
                'pages': f"{db_data.get('pages', {}).get('start', '')}-{db_data.get('pages', {}).get('end', '')}"
            })

    output_data = dict(data)
    output_data.update({
        'id': review_id,
        'name': review_name,
        'description': description,
        'created_at': data.get('created_at', ''),
        'paper_count': len(paper_objs),
        'papers': paper_objs
    })

    out_file = os.path.join(output_dir, f"{review_id}.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)

    print(f"Processed review '{review_name}' ({review_id}): {len(paper_objs)} papers -> {out_file}")
    return output_data

def main():
    db_path = 'data/index/proceedings.db'
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    reviews_dir = 'data/reviews'
    output_dir = 'data/derived/reviews_cache'
    os.makedirs(output_dir, exist_ok=True)

    manifest = []
    for fname in os.listdir(reviews_dir):
        if fname.endswith('.json'):
            fpath = os.path.join(reviews_dir, fname)
            res = process_review_file(fpath, cursor, output_dir)
            m_item = {
                'id': res['id'],
                'name': res['name'],
                'description': res['description'],
                'created_at': res.get('created_at', ''),
                'paper_count': res['paper_count']
            }
            if 'selected_columns' in res:
                m_item['selected_columns'] = res['selected_columns']
            if 'visible_columns' in res:
                m_item['visible_columns'] = res['visible_columns']
            if 'column_definitions' in res:
                m_item['column_definitions'] = res['column_definitions']
            manifest.append(m_item)

    manifest.sort(key=lambda x: x['paper_count'], reverse=True)
    with open(os.path.join(output_dir, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print("Successfully rebuilt all reviews cache!")

if __name__ == '__main__':
    main()
