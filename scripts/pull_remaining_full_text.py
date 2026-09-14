#!/usr/bin/env python3
"""
Pull and Ingest Remaining Full Paper PDFs & Sections (2016–2022 + remaining)
Saves source PDFs under data/sources/individual_pdfs/<paper_id>.pdf
Saves formatted Markdown under data/derived/papers/<paper_id>.md
Inserts parsed canonical sections into proceedings.db
Tracks full data provenance and updates paper_sources_manifest.json
"""

import os
import io
import re
import json
import time
import sqlite3
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from curl_cffi import requests
from pypdf import PdfReader

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DERIVED_DIR = os.path.join(DATA_DIR, "derived")
PDFS_DIR = os.path.join(DATA_DIR, "sources", "individual_pdfs")
PAPERS_MD_DIR = os.path.join(DERIVED_DIR, "papers")
REGISTRY_PATH = os.path.join(DERIVED_DIR, "ground_truth_registry.json")
DB_PATH = os.path.join(BASE_DIR, "proceedings.db")
MANIFEST_PATH = os.path.join(DERIVED_DIR, "paper_sources_manifest.json")

os.makedirs(PDFS_DIR, exist_ok=True)
os.makedirs(PAPERS_MD_DIR, exist_ok=True)

SECTION_HEADING_PATTERNS = [
    ("References & Back Matter", re.compile(r'^(?:references|bibliography|works cited|acknowledgments|acknowledgements|appendi[cx])\b', re.IGNORECASE)),
    ("Discussion & Conclusion", re.compile(r'^(?:discussion|conclusion|concluding remarks|summary and conclusion|limitations|implications)\b', re.IGNORECASE)),
    ("Results & Findings", re.compile(r'^(?:results|findings|case study|empirical analysis|data analysis)\b', re.IGNORECASE)),
    ("Methodology & Context", re.compile(r'^(?:method|methods|methodology|participants|context|setting|study design|procedure|data collection|pedagogical design)\b', re.IGNORECASE)),
    ("Abstract & Introduction", re.compile(r'^(?:abstract|introduction|background|theoretical framework|literature review|problem statement|overview)\b', re.IGNORECASE))
]


def clean_heading_candidate(line: str) -> str:
    line = line.strip()
    line = re.sub(r'^(?:[0-9IVX]+(?:\.[0-9]+)*|\([0-9]+\))\s*', '', line)
    return line.strip()


def segment_paper_text(full_text: str, abstract: str = "") -> list:
    """Segments extracted paper text into canonical sections with original heading, normalized name, and text."""
    lines = full_text.split('\n')
    sections_text = {
        "Abstract & Introduction": [],
        "Methodology & Context": [],
        "Results & Findings": [],
        "Discussion & Conclusion": [],
        "References & Back Matter": []
    }
    current_sec = "Abstract & Introduction"
    if abstract:
        sections_text["Abstract & Introduction"].append(f"### Abstract\n{abstract}\n\n")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if len(stripped) <= 60 and not stripped.endswith('.'):
            c_head = clean_heading_candidate(stripped)
            matched_sec = None
            for sec_name, pattern in SECTION_HEADING_PATTERNS:
                if pattern.match(c_head):
                    matched_sec = sec_name
                    break
            if matched_sec:
                current_sec = matched_sec
                continue

        sections_text[current_sec].append(stripped)

    result = []
    for order_idx, (sec_name, s_lines) in enumerate(sections_text.items(), start=1):
        txt = "\n\n".join(s_lines).strip()
        if txt:
            result.append({
                "original_heading": sec_name,
                "normalized_section": sec_name.lower(),
                "order_index": order_idx,
                "text": txt
            })

    if not result and full_text.strip():
        result.append({
            "original_heading": "Full Text",
            "normalized_section": "full_text",
            "order_index": 1,
            "text": full_text.strip()
        })

    return result


def fetch_and_process_paper(paper_meta: dict, session: requests.Session) -> dict:
    pid = paper_meta["id"]
    pdf_url = paper_meta.get("pdf_url")
    title = paper_meta.get("title", "")
    abstract = paper_meta.get("abstract", "")
    year = paper_meta.get("year")
    conference = paper_meta.get("conference", "ISLS")
    authors = paper_meta.get("authors", [])
    author_str = "; ".join(authors) if isinstance(authors, list) else str(authors)

    if not pdf_url:
        return {"id": pid, "status": "no_url"}

    pdf_local_path = os.path.join(PDFS_DIR, f"{pid}.pdf")
    md_local_path = os.path.join(PAPERS_MD_DIR, f"{pid}.md")

    content_bytes = None
    if os.path.exists(pdf_local_path) and os.path.getsize(pdf_local_path) > 1000:
        with open(pdf_local_path, "rb") as f:
            content_bytes = f.read()
    else:
        try:
            r = session.get(pdf_url, timeout=25)
            if r.status_code == 200 and len(r.content) > 1000:
                content_bytes = r.content
                with open(pdf_local_path, "wb") as f:
                    f.write(content_bytes)
            else:
                return {"id": pid, "status": f"http_{r.status_code}"}
        except Exception as e:
            return {"id": pid, "status": "download_failed", "error": str(e)}

    # Extract text with pypdf
    try:
        reader = PdfReader(io.BytesIO(content_bytes))
        num_pages = len(reader.pages)
        page_texts = [p.extract_text() or "" for p in reader.pages]
        full_text = "\n\n".join(page_texts).strip()

        if len(full_text) < 200:
            return {"id": pid, "status": "too_short"}

        # Segment sections
        sections = segment_paper_text(full_text, abstract)

        # Write formatted Markdown
        with open(md_local_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            if author_str:
                f.write(f"**Authors:** {author_str}\n\n")
            f.write(f"**Conference:** {conference} {year}\n\n")
            if pdf_url:
                f.write(f"**Source PDF:** [{os.path.basename(pdf_url)}]({pdf_url})\n\n")
            for sec in sections:
                f.write(f"## {sec['original_heading']}\n\n{sec['text']}\n\n")

        return {
            "id": pid,
            "status": "success",
            "title": title,
            "year": year,
            "conference": conference,
            "pdf_url": pdf_url,
            "pdf_local_path": os.path.relpath(pdf_local_path, BASE_DIR),
            "md_local_path": os.path.relpath(md_local_path, BASE_DIR),
            "num_pages": num_pages,
            "total_chars": len(full_text),
            "sections": sections
        }
    except Exception as e:
        return {"id": pid, "status": "extract_failed", "error": str(e)}


def main(max_workers=14, batch_limit=None):
    print("=== Step 2: Pulling Remaining Full Paper PDFs & Ingesting Sections ===")
    
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        registry = json.load(f)

    reg_papers = {p["id"]: p for p in registry.get("papers", [])}

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Find papers that do not have full text complete
    c.execute("SELECT id, title, year, conference, full_text_status FROM papers WHERE full_text_status IS NULL OR full_text_status != 'complete'")
    remaining_papers = [dict(r) for r in c.fetchall()]
    print(f"Total papers in DB needing full text pull: {len(remaining_papers)}")

    # Load existing manifest
    manifest = {}
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            manifest = {}

    to_pull = []
    for p in remaining_papers:
        pid = p["id"]
        reg_entry = reg_papers.get(pid)
        if reg_entry and reg_entry.get("pdf_url"):
            to_pull.append(reg_entry)

    if batch_limit:
        to_pull = to_pull[:batch_limit]

    print(f"Candidate papers with confirmed pdf_url to pull: {len(to_pull)}")
    if not to_pull:
        print("All papers already have complete full text!")
        conn.close()
        return

    now = datetime.datetime.now().isoformat()
    completed = 0
    successes = 0
    t0 = time.time()

    def worker_task(paper_item):
        s = requests.Session(impersonate="chrome120")
        return fetch_and_process_paper(paper_item, s)

    print(f"Starting concurrent bitstream fetch and section extraction ({max_workers} workers)...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_id = {executor.submit(worker_task, item): item["id"] for item in to_pull}

        for future in as_completed(future_to_id):
            res = future.result()
            completed += 1
            pid = res["id"]

            if res.get("status") == "success":
                successes += 1
                sections = res["sections"]

                # Update sections in DB
                c.execute("DELETE FROM sections WHERE paper_id = ?", (pid,))
                for sec in sections:
                    sec_id = f"{pid}-sec-{sec['order_index']:02d}"
                    c.execute("""
                        INSERT INTO sections (id, paper_id, original_heading, normalized_section, level, order_index, text)
                        VALUES (?, ?, ?, ?, 1, ?, ?)
                    """, (sec_id, pid, sec["original_heading"], sec["normalized_section"], sec["order_index"], sec["text"]))

                # Update paper provenance
                c.execute("""
                    UPDATE papers
                    SET source_type = 'isls_repository_bitstream',
                        source_url = ?,
                        full_text_status = 'complete',
                        extracted_at = ?
                    WHERE id = ?
                """, (res["pdf_url"], now, pid))

                manifest[pid] = {
                    "id": pid,
                    "title": res["title"],
                    "year": res["year"],
                    "conference": res["conference"],
                    "source_type": "isls_repository_bitstream",
                    "source_url": res["pdf_url"],
                    "pdf_path": res["pdf_local_path"],
                    "md_path": res["md_local_path"],
                    "full_text_status": "complete",
                    "pages_count": res["num_pages"],
                    "sections_count": len(sections),
                    "total_chars": res["total_chars"],
                    "extracted_at": now
                }
            else:
                # Mark as abstract_only if download failed
                c.execute("""
                    UPDATE papers
                    SET source_type = 'isls_repository_abstract',
                        full_text_status = 'abstract_only',
                        extracted_at = ?
                    WHERE id = ?
                """, (now, pid))

            if completed % 50 == 0 or completed == len(to_pull):
                conn.commit()
                with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
                    json.dump(manifest, f, indent=2)

                elapsed = time.time() - t0
                rate = completed / max(1, elapsed)
                remaining = (len(to_pull) - completed) / max(0.1, rate)
                print(f"  Progress: {completed}/{len(to_pull)} ({rate:.1f} p/s) | Success: {successes} | Remaining: {remaining/60:.1f}m")

    conn.commit()
    conn.close()

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n=== Full Paper Pull Complete! Total: {completed}, Successfully Ingested: {successes} ===")


if __name__ == "__main__":
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    main(max_workers=14, batch_limit=limit)
