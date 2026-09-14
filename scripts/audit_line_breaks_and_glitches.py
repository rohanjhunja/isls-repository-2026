#!/usr/bin/env python3
"""
Comprehensive Audit of Line Breaks, Broken Citations, and Kerning Glitches
Scans all 5,402 papers in proceedings.db to find:
1. Broken citations (unclosed parentheses, lines ending in & or ; before citation year)
2. Trailing connector breaks (ending in &, ;, ,, -, or prepositions)
3. Mid-sentence breaks (paragraph ending without terminal punctuation followed by lowercase letter)
4. Kerning / spacing glitches (e.g. a ttending, appro aches, st udent, co -design, space before punctuation)
Emits metrics to data/reports/line_breaks_and_glitches_audit.json
"""

import os
import re
import json
import sqlite3
import argparse
import datetime
from typing import Dict, List, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "proceedings.db")
REPORTS_DIR = os.path.join(BASE_DIR, "data", "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

CONNECTING_WORDS = {
    "and", "or", "the", "a", "an", "of", "to", "in", "for", "with",
    "by", "from", "on", "at", "as", "that", "which", "between", "into", "through"
}

KNOWN_GLITCH_WORDS = {
    "attending", "approaches", "approach", "technology", "technologies",
    "technologically", "record", "records", "individual", "individually",
    "collaborative", "collaborating", "collaboration", "learning", "interactions",
    "environment", "environments", "analysis", "qualitative", "quantitative",
    "participants", "understanding", "investments", "foundations", "exploration",
    "explorations", "ecological", "transformative", "pedagogical", "pedagogically",
    "student", "students", "digital", "digitally", "lived", "define", "defined",
    "multidimensionality", "interactional", "deductive", "throughout", "educational"
}


def audit_paper_text(pid: str, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
    broken_citations = []
    trailing_connectors = []
    mid_sentence_breaks = []
    kerning_glitches = []
    punct_space_issues = []

    for sec in sections:
        heading = sec["original_heading"]
        norm_sec = sec["normalized_section"]
        text = sec["text"] or ""
        paras = [p.strip() for p in text.split("\n\n") if p.strip()]

        for i in range(len(paras) - 1):
            p1 = paras[i]
            p2 = paras[i + 1]

            # 1. Unclosed parenthesis / broken citation check
            open_parens = p1.count("(") - p1.count(")")
            if open_parens > 0:
                broken_citations.append({
                    "section": heading,
                    "para_index": i,
                    "p1_tail": p1[-60:],
                    "p2_head": p2[:60],
                    "reason": "unclosed_parenthesis"
                })
            elif p1.rstrip().endswith(("&", ";")) and re.search(r"\b(?:19|20)\d{2}\b", p2[:30]):
                broken_citations.append({
                    "section": heading,
                    "para_index": i,
                    "p1_tail": p1[-60:],
                    "p2_head": p2[:60],
                    "reason": "citation_connector"
                })

            # 2. Trailing connector breaks
            elif p1.rstrip().endswith(("&", ";", ",", "-", "–", "—")):
                trailing_connectors.append({
                    "section": heading,
                    "para_index": i,
                    "p1_tail": p1[-60:],
                    "p2_head": p2[:60]
                })
            else:
                last_word = p1.rstrip().split()[-1].lower() if p1.split() else ""
                clean_last = re.sub(r"[^a-z]", "", last_word)
                if clean_last in CONNECTING_WORDS:
                    trailing_connectors.append({
                        "section": heading,
                        "para_index": i,
                        "p1_tail": p1[-60:],
                        "p2_head": p2[:60],
                        "reason": f"trailing_preposition_{clean_last}"
                    })

            # 3. Mid-sentence breaks
            if not p1.endswith((".", "!", "?", ":", "\"", "”", "’", ")")) and norm_sec != "references & back matter":
                if p2 and (p2[0].islower() or p2.startswith(("et al.", "p.", "pp.", ",", ";", ")"))):
                    mid_sentence_breaks.append({
                        "section": heading,
                        "para_index": i,
                        "p1_tail": p1[-60:],
                        "p2_head": p2[:60]
                    })

        # 4. Kerning and punctuation space issues
        for m in re.finditer(r"\s+[,;:\.\)]", text):
            punct_space_issues.append({
                "section": heading,
                "snippet": text[max(0, m.start() - 15):min(len(text), m.end() + 15)]
            })

        for word in KNOWN_GLITCH_WORDS:
            for split_idx in range(1, len(word)):
                w1, w2 = word[:split_idx], word[split_idx:]
                if len(w1) >= 1 and len(w2) >= 2:
                    pattern = rf"\b{w1}\s+{w2}\b"
                    for match in re.finditer(pattern, text, re.I):
                        kerning_glitches.append({
                            "section": heading,
                            "glitch": match.group(0),
                            "target": word,
                            "snippet": text[max(0, match.start() - 20):min(len(text), match.end() + 20)]
                        })

    return {
        "paper_id": pid,
        "broken_citations_count": len(broken_citations),
        "broken_citations": broken_citations,
        "trailing_connectors_count": len(trailing_connectors),
        "trailing_connectors": trailing_connectors[:5],
        "mid_sentence_breaks_count": len(mid_sentence_breaks),
        "mid_sentence_breaks": mid_sentence_breaks[:5],
        "punct_space_issues_count": len(punct_space_issues),
        "kerning_glitches_count": len(kerning_glitches),
        "kerning_glitches": kerning_glitches[:5]
    }


def main():
    parser = argparse.ArgumentParser(description="Audit line breaks, broken citations, and kerning glitches.")
    parser.add_argument("--report-name", type=str, default="baseline", help="Report identifier name.")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    total_papers = c.execute("SELECT count(*) FROM papers").fetchone()[0]
    print(f"=== Auditing Line Breaks & Glitches across {total_papers} Papers (Report: {args.report_name}) ===", flush=True)

    c.execute("SELECT id FROM papers ORDER BY id")
    pids = [r["id"] for r in c.fetchall()]

    total_broken_citations = 0
    total_trailing_connectors = 0
    total_mid_sentence_breaks = 0
    total_punct_space_issues = 0
    total_kerning_glitches = 0
    papers_with_broken_citations = 0
    papers_with_mid_sentence = 0

    flagged_papers = []

    for i, pid in enumerate(pids, start=1):
        c.execute("SELECT original_heading, normalized_section, text FROM sections WHERE paper_id = ? ORDER BY order_index", (pid,))
        sec_rows = [dict(r) for r in c.fetchall()]

        res = audit_paper_text(pid, sec_rows)
        if res["broken_citations_count"] > 0:
            papers_with_broken_citations += 1
            total_broken_citations += res["broken_citations_count"]
        if res["mid_sentence_breaks_count"] > 0:
            papers_with_mid_sentence += 1
            total_mid_sentence_breaks += res["mid_sentence_breaks_count"]

        total_trailing_connectors += res["trailing_connectors_count"]
        total_punct_space_issues += res["punct_space_issues_count"]
        total_kerning_glitches += res["kerning_glitches_count"]

        if res["broken_citations_count"] > 0 or res["mid_sentence_breaks_count"] > 5 or res["kerning_glitches_count"] > 0:
            flagged_papers.append(res)

        if i % 1000 == 0 or i == total_papers:
            print(f"  Scanned {i}/{total_papers} papers...", flush=True)

    conn.close()

    report_path = os.path.join(REPORTS_DIR, f"line_breaks_and_glitches_{args.report_name}.json")
    summary = {
        "timestamp": datetime.datetime.now().isoformat(),
        "report_name": args.report_name,
        "total_papers": total_papers,
        "total_broken_citations": total_broken_citations,
        "papers_with_broken_citations": papers_with_broken_citations,
        "total_trailing_connectors": total_trailing_connectors,
        "total_mid_sentence_breaks": total_mid_sentence_breaks,
        "papers_with_mid_sentence_breaks": papers_with_mid_sentence,
        "total_punct_space_issues": total_punct_space_issues,
        "total_kerning_glitches": total_kerning_glitches,
        "sample_flagged_papers": flagged_papers[:50]
    }

    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nAudit complete! Report saved to {report_path}", flush=True)
    print(f"  Total Broken Citations: {total_broken_citations} (across {papers_with_broken_citations} papers)")
    print(f"  Total Trailing Connectors: {total_trailing_connectors}")
    print(f"  Total Mid-Sentence Breaks: {total_mid_sentence_breaks} (across {papers_with_mid_sentence} papers)")
    print(f"  Total Punctuation Space Issues: {total_punct_space_issues}")
    print(f"  Total Known Kerning Glitches: {total_kerning_glitches}")


if __name__ == "__main__":
    main()
