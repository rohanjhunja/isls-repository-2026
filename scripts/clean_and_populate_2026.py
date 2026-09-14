#!/usr/bin/env python3
import os
import json
import sqlite3
import re
from typing import Dict, List, Any, Optional

from proceedings_ingest.utils.text_cleanup import repair_title_and_authors, sanitize_title_string, sanitize_author_list
from proceedings_ingest.database import get_db_connection, insert_paper_record, DEFAULT_DB_PATH

REGISTRY_PATH = "data/derived/ground_truth_registry.json"

VOLUMES_CONFIG = [
    {
        "vol_id": "cscl-2026-proceedings",
        "json_path": "data/derived/cscl-2026-proceedings/cscl-2026-proceedings.json",
        "md_path": "proceedings_md/cscl-2026.md",
        "conference": "CSCL",
        "pdf_filename": "cscl-2026-proceedings.pdf"
    },
    {
        "vol_id": "icls-2026-proceedings",
        "json_path": "data/derived/icls-2026-proceedings/icls-2026-proceedings.json",
        "md_path": "proceedings_md/icls-2026.md",
        "conference": "ICLS",
        "pdf_filename": "icls-2026-proceedings.pdf"
    },
    {
        "vol_id": "isls-2026-proceedings",
        "json_path": "data/derived/isls-2026-proceedings/isls-2026-proceedings.json",
        "md_path": "proceedings_md/isls-2026.md",
        "conference": "ISLS",
        "pdf_filename": "isls-2026-proceedings.pdf"
    }
]

SECTION_TYPE_MAP = {
    "Long Papers": "Full Paper",
    "Short Papers": "Short Paper",
    "Posters": "Poster",
    "Symposia": "Symposium",
    "Special Session": "Special Session",
    "Pre-Conference Workshops": "Workshop",
    "Keynotes": "Keynote"
}


INST_PATTERN = re.compile(
    r'(University|Institute|College|School|Academy|Department|Center|Centre|Laboratory|Lab|Faculty|Polytechnic|Consortium)',
    re.IGNORECASE
)


def get_canonical_page_title(md_text: str, pdf_page: int) -> str:
    """Extract ground truth title directly from the paper's first page in markdown."""
    m = re.search(rf'<!-- page: pdf={pdf_page} .*?-->(.*?)(?:<!-- page:|$)', md_text, re.DOTALL)
    if not m:
        return ""
    page_text = m.group(1).strip()
    lines = [l.strip() for l in page_text.split('\n') if l.strip()]
    if not lines:
        return ""
    start_i = 1 if lines[0] in [
        'Keynotes', 'Special Session', 'Long Papers', 'Short Papers',
        'Posters', 'Symposia', 'Pre-Conference Workshops'
    ] else 0

    t_lines = []
    mode = 'title'
    for i in range(start_i, min(len(lines), start_i + 15)):
        l = lines[i]
        if l.startswith('Abstract:') or l.startswith('Abstract :') or l.startswith('Overview') or l.startswith('Introduction'):
            break
        if mode == 'title':
            if '@' in l or INST_PATTERN.search(l):
                if t_lines and (',' in t_lines[-1] or '&' in t_lines[-1]):
                    t_lines.pop()
                break
            elif ',' in l and any(w[0].isupper() for w in l.split()):
                if i + 1 < len(lines) and ('@' in lines[i + 1] or INST_PATTERN.search(lines[i + 1])):
                    break
                else:
                    t_lines.append(l)
            else:
                t_lines.append(l)
        else:
            break

    raw_t = ' '.join(t_lines)
    has_curly_open = raw_t.startswith('“')
    clean = sanitize_title_string(raw_t)
    if has_curly_open and not clean.startswith('“'):
        clean = f'“{clean}'
    return clean


def extract_authors_from_page_header(md_text: str, pdf_page: int) -> List[str]:
    """Extract full author names from the paper's first page before Abstract."""
    m = re.search(rf'<!-- page: pdf={pdf_page} .*?-->(.*?)(?:<!-- page:|$)', md_text, re.DOTALL)
    if not m:
        return []
    lines = [l.strip() for l in m.group(1).strip().split('\n') if l.strip()]
    if not lines:
        return []

    author_lines = []
    found_authors = False
    for i in range(len(lines[:25])):
        l = lines[i]
        if l.startswith('Abstract:') or l.startswith('Abstract :') or l.startswith('Overview') or l.startswith('Introduction'):
            break
        if '@' in l or INST_PATTERN.search(l):
            found_authors = True
            continue
        if ',' in l and any(w[0].isupper() for w in l.split()):
            if i + 1 < len(lines) and ('@' in lines[i + 1] or INST_PATTERN.search(lines[i + 1])):
                found_authors = True
                author_lines.append(l)
            elif found_authors:
                author_lines.append(l)
        elif found_authors and any(w[0].isupper() for w in l.split() if w.isalpha()):
            if not ('@' in l or INST_PATTERN.search(l)):
                author_lines.append(l)

    extracted = []
    for al in author_lines:
        clean_al = re.sub(r'\(.*?\)', '', al).strip()
        names = sanitize_author_list(clean_al)
        for n in names:
            n_clean = n.strip()
            if n_clean and len(n_clean) > 2 and not ('@' in n_clean or INST_PATTERN.search(n_clean)):
                if n_clean not in extracted:
                    extracted.append(n_clean)
    return extracted


def extract_toc(md_path: str) -> Dict[int, Dict[str, Any]]:
    """Extract table of contents mapping from proceedings markdown with multi-line author support."""
    if not os.path.exists(md_path):
        return {}

    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    start_idx = -1
    for i, l in enumerate(lines[:2500]):
        if "table of contents" in l.lower():
            start_idx = i
            break

    if start_idx == -1:
        return {}

    toc_lines = lines[start_idx:start_idx + 4000]
    toc_by_page = {}
    curr_section = "Paper"

    i = 0
    while i < len(toc_lines):
        line = toc_lines[i].strip()
        line = re.sub(r'<!--.*?-->', '', line).strip()
        if not line or "table of contents" in line.lower() or "isls proceedings" in line.lower():
            i += 1
            continue

        if line in SECTION_TYPE_MAP:
            curr_section = SECTION_TYPE_MAP[line]
            i += 1
            continue

        # Pattern 1: Single line with dots or spaces ending in page number
        m = re.search(r'^(.*?)(?:\.{3,}|\s{3,})\s*(\d+)$', line)
        if m:
            title = m.group(1).strip()
            page = int(m.group(2))
            author_parts = []
            while i + 1 < len(toc_lines):
                next_line = re.sub(r'<!--.*?-->', '', toc_lines[i + 1]).strip()
                if not next_line:
                    i += 1
                    continue
                if next_line in SECTION_TYPE_MAP or re.search(r'(?:\.{3,}|\s{3,})\s*\d+$', next_line):
                    break
                # Check if next_line might be line 1 of next title or author continuation
                if i + 2 < len(toc_lines) and re.search(r'(?:\.{3,}|\s{3,})\s*\d+$', toc_lines[i + 2]):
                    # If it has author indicators (comma between names, starts with 'and ', ends with comma)
                    if ',' in next_line or next_line.endswith(',') or next_line.lower().startswith('and '):
                        author_parts.append(next_line)
                        i += 1
                        continue
                    else:
                        break
                author_parts.append(next_line)
                i += 1

            authors = ", ".join(author_parts)
            if page not in toc_by_page:
                toc_by_page[page] = {"title": title, "authors": authors, "paper_type": curr_section}

        # Pattern 2: Multi-line title where line 1 is continuation and line 2 has dots/spaces + page
        elif i + 1 < len(toc_lines) and re.search(r'(?:\.{3,}|\s{3,})\s*\d+$', toc_lines[i + 1]):
            m2 = re.search(r'^(.*?)(?:\.{3,}|\s{3,})\s*(\d+)$', toc_lines[i + 1].strip())
            # Check if line 1 is actually an orphan author continuation from previous paper
            is_orphan_author = (
                ',' in line or line.endswith(',') or line.lower().startswith('and ')
            )
            if is_orphan_author:
                if toc_by_page:
                    prev_p = list(toc_by_page.keys())[-1]
                    cur_auth = toc_by_page[prev_p].get("authors", "")
                    toc_by_page[prev_p]["authors"] = f"{cur_auth}, {line}" if cur_auth else line
                title = m2.group(1).strip()
            else:
                title = f"{line} {m2.group(1).strip()}"
            page = int(m2.group(2))
            i += 1
            author_parts = []
            while i + 1 < len(toc_lines):
                next_line = re.sub(r'<!--.*?-->', '', toc_lines[i + 1]).strip()
                if not next_line:
                    i += 1
                    continue
                if next_line in SECTION_TYPE_MAP or re.search(r'(?:\.{3,}|\s{3,})\s*\d+$', next_line):
                    break
                if i + 2 < len(toc_lines) and re.search(r'(?:\.{3,}|\s{3,})\s*\d+$', toc_lines[i + 2]):
                    if ',' in next_line or next_line.endswith(',') or next_line.lower().startswith('and '):
                        author_parts.append(next_line)
                        i += 1
                        continue
                    else:
                        break
                author_parts.append(next_line)
                i += 1

            authors = ", ".join(author_parts)
            if page not in toc_by_page:
                toc_by_page[page] = {"title": title, "authors": authors, "paper_type": curr_section}

        i += 1

    return toc_by_page


def clean_paper(p: Dict[str, Any], conf: str, pdf_filename: str, toc_by_page: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
    raw_t = p.get("title", "")
    pid = p.get("id")

    # Printed page
    ps = p.get("pages", {}).get("printed_start")
    p_num = int(ps) if ps and str(ps).isdigit() else None

    toc_entry = toc_by_page.get(p_num) if p_num is not None else None

    # Determine title
    if toc_entry and toc_entry.get("title"):
        clean_t = sanitize_title_string(toc_entry["title"])
    else:
        clean_t = sanitize_title_string(raw_t)

    # Determine authors
    clean_authors = []
    if toc_entry and toc_entry.get("authors"):
        clean_authors = sanitize_author_list(toc_entry["authors"])
    
    if not clean_authors:
        # Fallback to extracting from paper's authors array
        raw_authors_list = p.get("authors", [])
        raw_auth_names = []
        for a in raw_authors_list:
            if isinstance(a, dict):
                disp = a.get("display_name") or a.get("name") or ""
                if disp:
                    raw_auth_names.append(disp)
            elif isinstance(a, str):
                raw_auth_names.append(a)

        # Spillover check
        reparsed_auths = []
        for a_name in raw_auth_names:
            a_str = a_name.strip()
            is_spillover = (
                re.match(r'^(and|in|the|of|for|with|through|to|from|by|on|at)\b', a_str, re.I)
                or a_str in [
                    'Visual Novels', 'the Learning Sciences', 'Quantitative Data Analysis',
                    'The Concord Consortium', 'and Resistance', 'through Kinesthetic Modality',
                    'and Teacher Responsivity to', 'Investigate Complex Phenomena',
                    'With a Reflective AI Agent', 'and Between Research-Practice Partnerships',
                    'the Future of AI in Education', 'on Heterogeneous Interaction Network Analysis (HINA)',
                    'through Co-design', 'and Research', 'Collaborative Learning: Learning',
                    'and Multimodality', 'Effects of Conceptual Congruence and Sensorimotor Engagement',
                    'on Geometric Reasoning', 'with Parents and Young Children',
                    'of a Near-Peer Mentorship Model within a Maker Camp', 'and Social Praxis'
                ]
            )
            if is_spillover:
                if not clean_t.endswith(a_str) and a_str.lower() not in clean_t.lower():
                    clean_t = f"{clean_t} {a_str}".strip()
            else:
                reparsed_auths.append(a_str)

        raw_auth_str = ", ".join(reparsed_auths)
        clean_authors = sanitize_author_list(raw_auth_str)

    # Special handling for known irregular items in 2026 proceedings
    if "Humanizing Institutional Landscapes" in clean_t:
        clean_authors = ["Cathery Yeh", "Erin McCloskey", "Alfredo J. Artiles", "Mimi Ito"]
    elif "vibes" in clean_t.lower():
        clean_authors = ["Ananda Marin"]
    elif "prolepsis" in clean_t.lower():
        clean_authors = ["Kareem Edouard"]

    clean_auth_str = ", ".join(clean_authors)

    # Abstract cleanup
    abstract = p.get("abstract") or ""
    if abstract:
        abstract = re.sub(r'(\w+)-\n\s*(\w+)', r'\1-\2', abstract)
        abstract = re.sub(r'[ \t]+', ' ', abstract).strip()

    # Paper type
    paper_type = "Paper"
    if toc_entry and toc_entry.get("paper_type"):
        paper_type = toc_entry["paper_type"]
    else:
        # Fallback from page count or title
        start_p = p.get("pages", {}).get("start") or p.get("pages", {}).get("pdf_start")
        end_p = p.get("pages", {}).get("end") or p.get("pages", {}).get("pdf_end")
        if start_p and end_p:
            span = int(end_p) - int(start_p) + 1
            if span >= 6:
                paper_type = "Full Paper"
            elif span >= 3:
                paper_type = "Short Paper"
            else:
                paper_type = "Poster"

    citation = f"{clean_auth_str} (2026). {clean_t}. Proceedings of {conf} 2026."

    return {
        "id": pid,
        "title": clean_t,
        "year": 2026,
        "conference": conf,
        "paper_type": paper_type,
        "doi": None,
        "handle": None,
        "handle_url": None,
        "citation": citation,
        "start_page": p.get("pages", {}).get("start") or p.get("pages", {}).get("pdf_start"),
        "end_page": p.get("pages", {}).get("end") or p.get("pages", {}).get("pdf_end"),
        "abstract": abstract,
        "authors": clean_authors,
        "filename": pdf_filename,
        "raw_sections": p.get("sections", [])
    }


def heal_volume_papers(vol_cleaned: List[Dict[str, Any]], md_path: str, conf: str) -> None:
    """Validate and heal any leaked author names in paper titles against ground truth first page."""
    if not os.path.exists(md_path):
        return
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    for idx, p in enumerate(vol_cleaned):
        sp = p.get("start_page")
        if not sp:
            continue
        try:
            sp_int = int(sp)
        except ValueError:
            continue

        pt = get_canonical_page_title(md_text, sp_int)
        if not pt:
            continue

        clean_curr = re.sub(r'^[“\"\']|[”\"\']$', '', p["title"].strip())
        clean_pt = re.sub(r'^[“\"\']|[”\"\']$', '', pt.strip())

        match_pos = -1
        if clean_pt and clean_pt in clean_curr:
            match_pos = clean_curr.find(clean_pt)
        else:
            pt_words = clean_pt.split()
            if len(pt_words) >= 3:
                probe = ' '.join(pt_words[:3])
                if probe.lower() in clean_curr.lower():
                    match_pos = clean_curr.lower().find(probe.lower())

        if match_pos > 0:
            leaked_prefix = clean_curr[:match_pos].strip()
            repaired_t = clean_curr[match_pos:].strip()
            if p["title"].strip().startswith('“') or p["title"].strip().startswith('"'):
                if not (repaired_t.startswith('“') or repaired_t.startswith('"')):
                    repaired_t = f'“{repaired_t}'

            p["title"] = repaired_t
            p["citation"] = f"{', '.join(p['authors'])} (2026). {repaired_t}. Proceedings of {conf} 2026."

            if idx > 0:
                prev_p = vol_cleaned[idx - 1]
                prev_sp = int(prev_p.get("start_page")) if prev_p.get("start_page") else None
                page_authors = extract_authors_from_page_header(md_text, prev_sp) if prev_sp else []
                if page_authors and len(page_authors) >= len(prev_p["authors"]):
                    prev_p["authors"] = list(page_authors)
                else:
                    clean_leaked = re.sub(
                        r'^(Community Workshops|Early Career Workshops|Keynotes|Interactive Tools and Demos)\b',
                        '',
                        leaked_prefix,
                        flags=re.IGNORECASE
                    ).strip()
                    leaked_authors = sanitize_author_list(clean_leaked)
                    for la in leaked_authors:
                        if la not in prev_p["authors"]:
                            prev_p["authors"].append(la)

                prev_auth_str = ", ".join(prev_p["authors"])
                prev_p["citation"] = f"{prev_auth_str} (2026). {prev_p['title']}. Proceedings of {conf} 2026."


def clean_and_populate_2026():
    print("=== Cleaning and Ingesting ALL 2026 Proceedings (CSCL, ICLS, ISLS) ===")

    all_2026_cleaned = []

    for cfg in VOLUMES_CONFIG:
        vol_id = cfg["vol_id"]
        json_path = cfg["json_path"]
        md_path = cfg["md_path"]
        conf = cfg["conference"]
        pdf_fn = cfg["pdf_filename"]

        if not os.path.exists(json_path):
            print(f"Error: JSON path {json_path} does not exist.")
            continue

        with open(json_path, "r", encoding="utf-8") as f:
            v_data = json.load(f)

        raw_papers = v_data.get("papers", [])
        print(f"\nProcessing {vol_id}: {len(raw_papers)} papers...")

        toc_by_page = extract_toc(md_path)
        print(f"  Extracted {len(toc_by_page)} TOC entries from {md_path}")

        vol_cleaned = []
        for p in raw_papers:
            cleaned = clean_paper(p, conf, pdf_fn, toc_by_page)
            vol_cleaned.append(cleaned)

        heal_volume_papers(vol_cleaned, md_path, conf)

        print(f"  Cleaned and validated {len(vol_cleaned)} papers for {vol_id}.")
        all_2026_cleaned.extend(vol_cleaned)

    print(f"\nTotal Cleaned 2026 Papers across all volumes: {len(all_2026_cleaned)}")

    # 1. Update ground_truth_registry.json
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
            registry = json.load(f)

        existing_papers = registry.get("papers", [])
        # Exclude any previous 2026 records
        existing_non_2026 = [p for p in existing_papers if p.get("year") != 2026]

        # Prepare registry format (without raw_sections)
        registry_2026_papers = []
        for p in all_2026_cleaned:
            p_copy = {k: v for k, v in p.items() if k != "raw_sections"}
            registry_2026_papers.append(p_copy)

        combined_papers = existing_non_2026 + registry_2026_papers

        by_year = {}
        for p in combined_papers:
            yr = p.get("year")
            by_year[yr] = by_year.get(yr, 0) + 1

        registry["papers"] = combined_papers
        registry["total_papers"] = len(combined_papers)
        registry["papers_by_year"] = by_year

        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2)

        print(f"\nUpdated {REGISTRY_PATH}:")
        print(f"  Total Papers: {len(combined_papers)}")
        print("  Breakdown by year:")
        for yr in sorted(by_year.keys()):
            print(f"    Year {yr}: {by_year[yr]} papers")

    # 2. Update SQLite proceedings.db
    conn = get_db_connection(DEFAULT_DB_PATH)
    cursor = conn.cursor()

    print("\nPurging previous 2026 records from proceedings.db...")
    cursor.execute("SELECT id FROM papers WHERE year = 2026")
    old_2026_ids = [r[0] for r in cursor.fetchall()]
    print(f"  Found {len(old_2026_ids)} old 2026 paper IDs to clear.")

    for oid in old_2026_ids:
        cursor.execute("DELETE FROM paper_labels WHERE paper_id = ?", (oid,))
        cursor.execute("DELETE FROM paper_authors WHERE paper_id = ?", (oid,))
        cursor.execute("DELETE FROM sections WHERE paper_id = ?", (oid,))
        cursor.execute("DELETE FROM papers_fts WHERE paper_id = ?", (oid,))
        cursor.execute("DELETE FROM author_collaborations WHERE paper_id = ?", (oid,))
        cursor.execute("DELETE FROM paper_citations WHERE citing_paper_id = ? OR cited_paper_id = ?", (oid, oid))
        cursor.execute("DELETE FROM papers WHERE id = ?", (oid,))
    conn.commit()

    print(f"Inserting {len(all_2026_cleaned)} clean 2026 papers into proceedings.db...")
    inserted_count = 0
    total_sections_count = 0

    for gt_p in all_2026_cleaned:
        raw_secs = gt_p.get("raw_sections", [])
        sec_data = []

        if raw_secs:
            for s_idx, sec in enumerate(raw_secs):
                sec_id = f"{gt_p['id']}-sec-{s_idx+1:02d}"
                orig_h = sec.get("heading_original") or f"Section {s_idx+1}"
                norm_h = sec.get("heading_normalized") or orig_h.lower().strip()
                s_text = sec.get("text") or ""
                p_start = sec.get("pages", {}).get("pdf_start") or gt_p.get("start_page")
                p_end = sec.get("pages", {}).get("pdf_end") or gt_p.get("end_page")
                sec_data.append({
                    "id": sec_id,
                    "original_heading": orig_h,
                    "normalized_section": norm_h,
                    "level": sec.get("level", 1),
                    "text": s_text,
                    "pdf_start_page": p_start,
                    "pdf_end_page": p_end
                })
        else:
            sec_data.append({
                "id": f"{gt_p['id']}-sec-01",
                "original_heading": "Abstract / Intro",
                "normalized_section": "introduction",
                "level": 1,
                "text": f"### Abstract\n{gt_p['abstract']}",
                "pdf_start_page": gt_p.get("start_page"),
                "pdf_end_page": gt_p.get("end_page")
            })

        p_dict = {
            "id": gt_p["id"],
            "handle": None,
            "handle_url": None,
            "doi": None,
            "title": gt_p["title"],
            "year": 2026,
            "conference": gt_p["conference"],
            "paper_type": gt_p["paper_type"],
            "citation": gt_p.get("citation"),
            "start_page": gt_p.get("start_page"),
            "end_page": gt_p.get("end_page"),
            "abstract": gt_p.get("abstract"),
            "boundary_confidence": 0.95,
            "filename": gt_p.get("filename"),
            "authors": gt_p.get("authors", [])
        }

        insert_paper_record(conn, p_dict, sec_data)
        inserted_count += 1
        total_sections_count += len(sec_data)

        if inserted_count % 100 == 0 or inserted_count == len(all_2026_cleaned):
            print(f"  Inserted {inserted_count}/{len(all_2026_cleaned)} papers (Indexed {total_sections_count} sections)...")

    conn.commit()
    conn.close()

    print(f"\nSuccessfully populated proceedings.db:")
    print(f"  Inserted {inserted_count} papers for 2026.")
    print(f"  Indexed {total_sections_count} sections for 2026.")


if __name__ == "__main__":
    clean_and_populate_2026()
