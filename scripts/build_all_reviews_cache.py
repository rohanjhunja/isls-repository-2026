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

def process_review_file(filepath, cursor, output_dir, is_sample: bool = False):
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
            row = cursor.execute('SELECT id, title, year, conference, abstract, filename, start_page, end_page FROM papers WHERE id = ?', (pid,)).fetchone()
            auth_rows = cursor.execute(
                'SELECT a.display_name FROM authors a JOIN paper_authors pa ON a.id = pa.author_id WHERE pa.paper_id = ? ORDER BY pa.author_order ASC',
                (pid,)
            ).fetchall()
            db_authors = ", ".join([r[0] for r in auth_rows])

            sec_rows = cursor.execute(
                'SELECT id, original_heading, normalized_section, text, pdf_start_page, pdf_end_page FROM sections WHERE paper_id = ? ORDER BY order_index ASC',
                (pid,)
            ).fetchall()

            raw_sections = [{
                'section_id': s[0], 'heading': s[1], 'canonical_role': s[2],
                'text': clean_text_artifacts(s[3]), 'pdf_page_start': s[4], 'pdf_page_end': s[5]
            } for s in sec_rows]

            first_sec_text = raw_sections[0]['text'] if raw_sections else ''
            orig_title = p.get('title') or (row[1] if row else '')
            orig_authors = p.get('authors') or db_authors
            r_title, r_authors = repair_title_and_authors(orig_title, orig_authors, first_sec_text)
            sections = clean_section_blocks(raw_sections)
            databases_searched = p.get('databases_searched') or extract_databases_searched(sections)
            keywords = p.get('keywords') or extract_title_abstract_keywords(r_title, p.get('abstract') or (row[4] if row else ''), p.get('keywords_field'))
            summary_50 = p.get('summary') or generate_50_word_summary(r_title, p.get('abstract') or (row[4] if row else ''))

            full_text = "\n\n".join([
                f"### {sec['heading'] or 'Section'} (Pages {sec['pdf_page_start']}-{sec['pdf_page_end']})\n{sec['text']}"
                for sec in sections
            ])

            p_obj = dict(p)
            p_obj.update({
                'id': pid,
                'title': r_title,
                'authors': r_authors,
                'year': p.get('year') or (row[2] if row else ''),
                'conference': (row[3] if row else 'ISLS'),
                'abstract': p.get('abstract') or (row[4] if row else ''),
                'summary': summary_50,
                'keywords': keywords,
                'databases_searched': databases_searched,
                'matched_search_terms': p.get('matched_search_terms', []),
                'sections': sections,
                'full_text': full_text,
                'filename': (row[5] if row else ''),
                'pages': f"{row[6] if row and row[6] else ''}-{row[7] if row and row[7] else ''}"
            })
            paper_objs.append(p_obj)

    elif paper_ids:
        for pid in paper_ids:
            row = cursor.execute('SELECT id, title, year, conference, abstract, filename, start_page, end_page FROM papers WHERE id = ?', (pid,)).fetchone()
            if not row:
                continue

            auth_rows = cursor.execute(
                'SELECT a.display_name FROM authors a JOIN paper_authors pa ON a.id = pa.author_id WHERE pa.paper_id = ? ORDER BY pa.author_order ASC',
                (pid,)
            ).fetchall()
            db_authors = ", ".join([r[0] for r in auth_rows])

            sec_rows = cursor.execute(
                'SELECT id, original_heading, normalized_section, text, pdf_start_page, pdf_end_page FROM sections WHERE paper_id = ? ORDER BY order_index ASC',
                (pid,)
            ).fetchall()

            raw_sections = [{
                'section_id': s[0], 'heading': s[1], 'canonical_role': s[2],
                'text': clean_text_artifacts(s[3]), 'pdf_page_start': s[4], 'pdf_page_end': s[5]
            } for s in sec_rows]

            first_sec_text = raw_sections[0]['text'] if raw_sections else ''
            r_title, r_authors = repair_title_and_authors(row[1], db_authors, first_sec_text)
            sections = clean_section_blocks(raw_sections)

            abstract = row[4] or ''
            databases_searched = extract_databases_searched(sections)
            keywords = extract_title_abstract_keywords(r_title, abstract, [])
            summary_50 = generate_50_word_summary(r_title, abstract)

            full_text = "\n\n".join([
                f"### {sec['heading'] or 'Section'} (Pages {sec['pdf_page_start']}-{sec['pdf_page_end']})\n{sec['text']}"
                for sec in sections
            ])

            paper_objs.append({
                'id': pid,
                'title': r_title,
                'authors': r_authors,
                'year': row[2] or '',
                'conference': row[3] or 'ISLS',
                'abstract': abstract,
                'summary': summary_50,
                'keywords': keywords,
                'databases_searched': databases_searched,
                'matched_search_terms': ['literature review'],
                'sections': sections,
                'full_text': full_text,
                'filename': row[5] or '',
                'pages': f"{row[6] or ''}-{row[7] or ''}"
            })

    output_data = dict(data)
    output_data.update({
        'id': review_id,
        'name': review_name,
        'description': description,
        'created_at': data.get('created_at', ''),
        'paper_count': len(paper_objs),
        'is_sample': is_sample,
        'papers': paper_objs
    })

    out_file = os.path.join(output_dir, f"{review_id}.json")
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)

    kind = "Sample" if is_sample else "User Review"
    print(f"Processed [{kind}] '{review_name}' ({review_id}): {len(paper_objs)} papers -> {out_file}")
    return output_data

def main():
    db_path = 'proceedings.db'
    if not os.path.exists(db_path):
        db_path = 'data/index/proceedings.db'
    if not os.path.exists(db_path):
        print(f"Error: proceedings.db not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    samples_dir = 'data/sample_reviews'
    user_reviews_dir = 'workspace/reviews'
    output_dir = 'data/derived/reviews_cache'
    os.makedirs(samples_dir, exist_ok=True)
    os.makedirs(user_reviews_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    reviews_to_process = {}

    # 1. First scan core samples
    if os.path.exists(samples_dir):
        for fname in os.listdir(samples_dir):
            if fname.endswith('.json'):
                rid = fname[:-5]
                reviews_to_process[rid] = (os.path.join(samples_dir, fname), True)

    # 2. Then scan user workspace reviews (overrides sample if same ID)
    if os.path.exists(user_reviews_dir):
        for fname in os.listdir(user_reviews_dir):
            if fname.endswith('.json'):
                rid = fname[:-5]
                reviews_to_process[rid] = (os.path.join(user_reviews_dir, fname), False)

    manifest = []
    for rid, (fpath, is_sample) in reviews_to_process.items():
        res = process_review_file(fpath, cursor, output_dir, is_sample=is_sample)
        m_item = {
            'id': res['id'],
            'name': res['name'],
            'description': res['description'],
            'created_at': res.get('created_at', ''),
            'paper_count': res['paper_count'],
            'is_sample': is_sample
        }
        if 'selected_columns' in res:
            m_item['selected_columns'] = res['selected_columns']
        if 'visible_columns' in res:
            m_item['visible_columns'] = res['visible_columns']
        if 'column_definitions' in res:
            m_item['column_definitions'] = res['column_definitions']
        manifest.append(m_item)

    # Sort manifest: user reviews first, then samples, then by paper count desc
    manifest.sort(key=lambda x: (not x.get('is_sample', False), x['paper_count']), reverse=True)
    with open(os.path.join(output_dir, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f"Successfully rebuilt all reviews cache! ({len(manifest)} reviews indexed)")

if __name__ == '__main__':
    main()
