#!/usr/bin/env python3
"""
Comprehensive Data Audit across All System Fields in proceedings.db
Audits core bibliographic metadata, source files, provenance, section counts,
line fragmentation, and search index coverage across all 5,402 papers.
Emits detailed report to data/reports/full_system_data_audit.json
"""

import os
import re
import json
import sqlite3
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "proceedings.db")
REPORTS_DIR = os.path.join(BASE_DIR, "data", "reports")
PDF_DIR = os.path.join(BASE_DIR, "data", "sources", "individual_pdfs")
MD_DIR = os.path.join(BASE_DIR, "data", "derived", "papers")

os.makedirs(REPORTS_DIR, exist_ok=True)


def run_full_system_audit():
    print("=== Running Comprehensive All-Field Data Audit ===")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    total_papers = c.execute("SELECT count(*) FROM papers").fetchone()[0]
    print(f"Total Papers in Database: {total_papers}")

    core_fields = [
        "id", "title", "year", "conference", "paper_type", "abstract",
        "citation", "doi", "handle_url", "start_page", "end_page",
        "source_type", "source_url", "full_text_status", "extracted_at"
    ]

    field_counts = {}
    for f in core_fields:
        count = c.execute(f"SELECT count(*) FROM papers WHERE {f} IS NOT NULL AND trim({f}) != ''").fetchone()[0]
        field_counts[f] = {
            "populated": count,
            "total": total_papers,
            "percentage": round(count / total_papers * 100, 2)
        }

    # Authors linked
    c.execute("""
        SELECT p.id
        FROM papers p
        WHERE NOT EXISTS (SELECT 1 FROM paper_authors pa WHERE pa.paper_id = p.id)
    """)
    missing_author_ids = [r[0] for r in c.fetchall()]

    # Missing or short abstracts
    c.execute("SELECT id, title, year, paper_type FROM papers WHERE abstract IS NULL OR trim(abstract) = ''")
    missing_abstract_papers = [dict(r) for r in c.fetchall()]

    c.execute("SELECT id, title, year, length(trim(abstract)) as len FROM papers WHERE abstract IS NOT NULL AND length(trim(abstract)) > 0 AND length(trim(abstract)) < 150")
    short_abstract_papers = [dict(r) for r in c.fetchall()]

    # Section counts and low section papers
    c.execute("""
        SELECT 
            p.id, p.title, p.year, p.conference, p.paper_type,
            count(s.id) as section_count,
            sum(length(s.text)) as total_text_len
        FROM papers p
        LEFT JOIN sections s ON s.paper_id = p.id
        GROUP BY p.id
    """)
    paper_section_rows = c.fetchall()

    section_distribution = {
        "1_section": [],
        "2_sections": [],
        "3_4_sections": [],
        "5_plus_sections": []
    }

    papers_with_excessive_linebreaks = 0
    total_sections_checked = 0

    c.execute("SELECT id, paper_id, length(text), text FROM sections WHERE length(text) > 400")
    all_sections = c.fetchall()

    for sec in all_sections:
        total_sections_checked += 1
        lines = [l.strip() for l in sec["text"].splitlines() if l.strip()]
        if len(lines) > 5:
            non_terminal = sum(1 for l in lines[:-1] if not l.endswith(('.', '!', '?', ':')))
            if (non_terminal / max(1, len(lines) - 1)) > 0.4:
                papers_with_excessive_linebreaks += 1

    for r in paper_section_rows:
        cnt = r["section_count"]
        p_info = {
            "id": r["id"],
            "title": r["title"],
            "year": r["year"],
            "conference": r["conference"],
            "paper_type": r["paper_type"],
            "sections": cnt,
            "total_chars": r["total_text_len"] or 0
        }
        if cnt == 1:
            section_distribution["1_section"].append(p_info)
        elif cnt == 2:
            section_distribution["2_sections"].append(p_info)
        elif 3 <= cnt <= 4:
            section_distribution["3_4_sections"].append(p_info)
        else:
            section_distribution["5_plus_sections"].append(p_info)

    # Local files audit
    local_pdf_missing = []
    local_md_missing = []

    c.execute("SELECT id, source_type, full_text_status FROM papers")
    for r in c.fetchall():
        pid = r["id"]
        status = r["full_text_status"]
        stype = r["source_type"]
        if status == "complete" and stype == "isls_repository_bitstream":
            pdf_path = os.path.join(PDF_DIR, f"{pid}.pdf")
            md_path = os.path.join(MD_DIR, f"{pid}.md")
            if not os.path.exists(pdf_path):
                local_pdf_missing.append(pid)
            if not os.path.exists(md_path):
                local_md_missing.append(pid)

    c.execute("SELECT count(DISTINCT paper_id) FROM papers_fts")
    fts_paper_count = c.fetchone()[0]

    c.execute("SELECT count(DISTINCT paper_id) FROM paper_labels")
    labels_paper_count = c.fetchone()[0]

    report = {
        "audit_timestamp": datetime.datetime.now().isoformat(),
        "total_papers": total_papers,
        "core_fields": field_counts,
        "missing_author_ids": missing_author_ids,
        "missing_abstracts_count": len(missing_abstract_papers),
        "missing_abstract_samples": missing_abstract_papers[:10],
        "short_abstracts_count": len(short_abstract_papers),
        "section_counts_summary": {
            "1_section_count": len(section_distribution["1_section"]),
            "2_sections_count": len(section_distribution["2_sections"]),
            "3_to_4_sections_count": len(section_distribution["3_4_sections"]),
            "5_plus_sections_count": len(section_distribution["5_plus_sections"])
        },
        "target_low_section_papers": (section_distribution["1_section"] + section_distribution["2_sections"]),
        "line_break_fragmentation": {
            "sections_checked": total_sections_checked,
            "sections_with_fragmented_lines": papers_with_excessive_linebreaks,
            "fragmentation_percentage": round(papers_with_excessive_linebreaks / max(1, total_sections_checked) * 100, 2)
        },
        "file_presence": {
            "missing_individual_pdfs_count": len(local_pdf_missing),
            "missing_individual_mds_count": len(local_md_missing)
        },
        "search_and_taxonomy": {
            "papers_in_fts": fts_paper_count,
            "fts_coverage_pct": round(fts_paper_count / total_papers * 100, 2),
            "papers_with_labels": labels_paper_count,
            "labels_coverage_pct": round(labels_paper_count / total_papers * 100, 2)
        }
    }

    report_path = os.path.join(REPORTS_DIR, "full_system_data_audit.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\nAudit complete! Report saved to {report_path}")
    print(f"  Field Completeness: Title={field_counts['title']['percentage']}%, Abstract={field_counts['abstract']['percentage']}%")
    print(f"  Missing Abstracts: {len(missing_abstract_papers)}")
    print(f"  Missing Authors: {len(missing_author_ids)}")
    print(f"  Low Section Papers (<=2): {len(section_distribution['1_section']) + len(section_distribution['2_sections'])}")
    print(f"  Line Fragmentation: {report['line_break_fragmentation']['fragmentation_percentage']}%")
    print(f"  FTS Index Coverage: {report['search_and_taxonomy']['fts_coverage_pct']}%")

    conn.close()
    return report


if __name__ == "__main__":
    run_full_system_audit()
