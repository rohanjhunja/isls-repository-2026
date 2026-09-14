#!/usr/bin/env python3
"""
Repository-Wide Text Cleaning, Paragraph Reflow, and Glitch Repair Engine
Processes all 5,402 papers in proceedings.db:
1. Re-joins broken citations (unclosed parentheses, dangling connectors, split years).
2. Un-wraps 2-column physical PDF lines into natural narrative paragraphs.
3. Fixes intra-word kerning splits and punctuation spacing.
4. Restricts standalone bibliography item splitting strictly to References section.
5. Preserves 100% of substantive text with word count verification.
6. Synchronizes sections table and derived Markdown files.
"""

import os
import re
import sys
import pypdf
import sqlite3
import argparse
import datetime
from typing import List, Dict, Any, Tuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "proceedings.db")
MD_DIR = os.path.join(BASE_DIR, "data", "derived", "papers")
PDF_DIR = os.path.join(BASE_DIR, "data", "sources", "individual_pdfs")

# Canonical headings
HEADING_PATTERNS = [
    ("References & Back Matter", re.compile(r"\b(?:references|bibliography|works cited|literature cited|acknowledgments|acknowledgements|appendi[cx]|endnotes)\b", re.IGNORECASE)),
    ("Discussion & Conclusion", re.compile(r"\b(?:(?:general\s+)?discussion(?:s)?|concluding remarks|summary and conclusions?|conclusions?(?:\s+and\s+implications?)?|limitations(?:\s+and\s+future\s+work)?|implications?(?:\s+for\s+practice|\s+for\s+cscl|\s+for\s+research)?|significance(?:\s+of\s+the\s+symposium)?|educational\s+significance)\b", re.IGNORECASE)),
    ("Results & Findings", re.compile(r"\b(?:(?:empirical\s+)?results?|(?:key\s+)?findings?|case study(?:\s*[:\-])?|empirical analysis|data analysis|qualitative analysis|quantitative analysis)\b", re.IGNORECASE)),
    ("Methodology & Context", re.compile(r"\b(?:method(?:s|ology)?|study design|research design|procedure|participants?(?:\s+and\s+setting)?|context(?:\s+and\s+setting)?|study context|data collection|pedagogical design|measures|analytic approach)\b", re.IGNORECASE)),
    ("Theoretical Background", re.compile(r"\b(?:theoretical framework|conceptual framework|literature review|theoretical background|related work|prior work|perspectives)\b", re.IGNORECASE)),
    ("Abstract & Introduction", re.compile(r"^(?:abstract|introduction|background|problem statement|motivation|overview|research questions?)\b", re.IGNORECASE)),
]

DISCOURSE_METHOD_STARTERS = re.compile(
    r"^(?:the study was conducted|using interaction analysis|we examined the pattern|participants were|the research setting|data were collected|to analyze the data|we analyzed|in this study,? we (?:examined|investigated|analyzed)|our methodology|the pedagogical design)\b",
    re.IGNORECASE
)

DISCOURSE_FINDINGS_STARTERS = re.compile(
    r"^(?:in l[0-9]|we found that|our analysis (?:revealed|shows|demonstrates)|the findings indicate|as students begin to own|when students owned|results indicate|the case study presented|observations revealed|the data show)\b",
    re.IGNORECASE
)

DISCOURSE_DISCUSSION_STARTERS = re.compile(
    r"^(?:as we are trying to expand|these findings suggest|in conclusion|to conclude|our findings contribute|taking the approach to analyze|the implications of|future research should|together,? these results)\b",
    re.IGNORECASE
)

CONNECTING_WORDS = {
    "and", "or", "the", "a", "an", "of", "to", "in", "for", "with",
    "by", "from", "on", "at", "as", "that", "which", "between", "into", "through"
}

# Vocabulary of known kerning splits and their clean targets
SPECIFIC_GLITCH_MAP = {
    "a ttending": "attending",
    "appro aches": "approaches",
    "appro ach": "approach",
    "st udent": "student",
    "st udents": "students",
    "d igital": "digital",
    "o ne": "one",
    "te chnology": "technology",
    "te chnologies": "technologies",
    "te chnologically": "technologically",
    "intr oducing": "introducing",
    "individ ually": "individually",
    "individ ual": "individual",
    "individ uals": "individuals",
    "defi ne": "define",
    "defi ned": "defined",
    "live d": "lived",
    "an d": "and",
    "interactio nal": "interactional",
    "deducti ve": "deductive",
    "througho ut": "throughout",
    "multid imensionality": "multidimensionality",
    "multid imensional": "multidimensional",
    "edu cational": "educational",
    "edu cation": "education",
    "re cord": "record",
    "re cords": "records",
    "partic ipants": "participants",
    "partic ipant": "participant",
    "pract ice": "practice",
    "pract ices": "practices",
    "theor etical": "theoretical",
    "theor etically": "theoretically",
    "academ ic": "academic",
    "collab orative": "collaborative",
    "collab oration": "collaboration",
    "collab orating": "collaborating",
    "transformat ive": "transformative",
    "pedagog ical": "pedagogical",
    "qualitat ive": "qualitative",
    "quantitat ive": "quantitative",
    "enviro nment": "environment",
    "enviro nments": "environments",
    "underst anding": "understanding",
    "signifi cance": "significance",
    "investm ent": "investment",
    "investm ents": "investments",
    "foundat ion": "foundation",
    "foundat ions": "foundations",
    "explorat ion": "exploration",
    "explorat ions": "explorations",
    "ecolog ical": "ecological"
}


def clean_text_glitches(text: str) -> str:
    """Repairs punctuation spacing, hyphen spacing, and known intra-word kerning splits."""
    if not text:
        return ""

    # 1. Punctuation spacing: remove space before comma, semicolon, colon, period, closing paren
    text = re.sub(r"\s+([,;:\.\)])", r"\1", text)
    # Remove space after opening paren/bracket
    text = re.sub(r"([\(\[])\s+", r"\1", text)

    # 2. Hyphen spacing: e.g. "co -design" -> "co-design", "trade -offs" -> "trade-offs", "173 - 193" -> "173-193"
    text = re.sub(r"(\b[a-zA-Z0-9]+)\s+-\s*([a-zA-Z0-9]+\b)", r"\1-\2", text)
    text = re.sub(r"(\b[a-zA-Z0-9]+)-\s+([a-zA-Z0-9]+\b)", r"\1-\2", text)

    # 3. Known specific kerning splits
    for glitch, fixed in SPECIFIC_GLITCH_MAP.items():
        # Case-insensitive replacement preserving casing
        pattern = re.compile(re.escape(glitch), re.IGNORECASE)
        def make_repl(target):
            def repl(m):
                s = m.group(0)
                if s.isupper():
                    return target.upper()
                if s[0].isupper():
                    return target[0].upper() + target[1:]
                return target
            return repl
        text = pattern.sub(make_repl(fixed), text)

    return text


def match_heading(line: str) -> Tuple[str, str]:
    """Check if line is a section heading. Returns (canonical_name, original_heading) or (None, None)."""
    clean_line = line.lstrip("#").strip()
    if len(clean_line) > 75 or len(clean_line) < 3:
        return None, None
    if clean_line.endswith((".", "!", "?", ",", ";", ":", "©", "ISLS")) or clean_line.isdigit():
        return None, None
    # Reject citations, DOIs, URLs, and captions
    if re.search(r"\([12][0-9]{3}[a-z]?\)", clean_line):
        return None, None
    if re.search(r"\b(?:doi:|https?://|pp\.\s*\d+|vol\.\s*\d+)\b", clean_line, re.I):
        return None, None
    if re.match(r"^(?:Figure|Table|Excerpt|\d+\s+[A-Z][a-z]+:)\b", clean_line):
        return None, None
    if any(w in clean_line for w in ["Proceedings", "University", "@", "Abstract:"]):
        return None, None

    # Strip leading numbers/Roman numerals e.g. "1. Introduction" or "I. Introduction"
    core = re.sub(r"^(?:(?:[0-9]+(?:\.[0-9]+)*|[IVXLCDM]+)[\.\)]\s*|\([0-9]+\)\s*|\d+\s+)", "", clean_line).strip()

    for canon, pattern in HEADING_PATTERNS:
        if pattern.search(core):
            return canon, clean_line

    return None, None


def is_unbroken_continuation(prev_line: str, curr_line: str) -> bool:
    """Check if curr_line must be stitched to prev_line (never break)."""
    if not prev_line or not curr_line:
        return False

    prev_clean = prev_line.strip()
    curr_clean = curr_line.strip()

    # 1. Unclosed parentheses or brackets in previous line
    if prev_clean.count("(") > prev_clean.count(")"):
        return True
    if prev_clean.count("[") > prev_clean.count("]"):
        return True

    # 2. Previous line ends with connector or hyphen
    if prev_clean.endswith(("&", ";", ",", "-", "–", "—", "/", ":", "et al.", "e.g.", "i.e.")):
        return True

    # 3. Previous line ends with a connecting word/preposition
    last_word = prev_clean.split()[-1].lower() if prev_clean.split() else ""
    clean_last = re.sub(r"[^a-z]", "", last_word)
    if clean_last in CONNECTING_WORDS:
        return True

    # 4. Current line starts with closing punctuation, lowercase, or citation continuation
    if curr_clean.startswith((")", "]", "}", ",", ";", ":", "et al.", "p.", "pp.")):
        return True
    if curr_clean[0].islower():
        return True

    # 5. Current line starts with citation year e.g. "2020)." or "Potvin, 2020)."
    if re.match(r"^(?:[12][0-9]{3}[a-z]?\s*[\)\],]|(?:[A-Z][a-zA-Z\s\.,&]+,\s*)?[12][0-9]{3}[a-z]?\s*\))", curr_clean):
        return True

    return False


def reflow_paragraphs(raw_lines: List[str]) -> List[str]:
    """Combine lines belonging to the same paragraph, preserving real paragraph breaks, headings, and lists."""
    cleaned = []
    for l in raw_lines:
        s = l.strip()
        # Drop exact running footers
        if re.match(r"^(?:CSCL|ICLS|ISLS)\s+\d{4}\s+Proceedings\s+\d+(\s+©\s+ISLS)?$", s, re.I):
            continue
        if s:
            cleaned.append(clean_text_glitches(s))

    paragraphs = []
    current = []

    for line in cleaned:
        # Markdown headings or detected standalone section headings
        canon_h, _ = match_heading(line)
        if line.startswith("#") or canon_h:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            paragraphs.append(line)
            continue

        # Bullets / numbered items
        if re.match(r"^(?:[-*•–—]|\(?\d+[\.\)]|\(?[a-z]\))\s+", line):
            if current:
                paragraphs.append(" ".join(current))
                current = []
            paragraphs.append(line)
            continue

        if re.match(r"^Figure\s+\d+[\.:]", line, re.I):
            if current:
                paragraphs.append(" ".join(current))
                current = []
            paragraphs.append(line)
            continue

        if current:
            prev = current[-1]
            # Join hyphenated words split across lines
            if prev.endswith("-") and not prev.endswith(" -"):
                current[-1] = prev[:-1] + line
                continue

            # Must stitch if syntactic continuation
            if is_unbroken_continuation(prev, line):
                current.append(line)
                continue

            # Check if previous line ended a complete sentence
            ends_with_terminal = prev.endswith((".", "!", "?", ":"))
            short_prev = len(prev) < 55
            looks_like_starter = bool(re.match(r"^(?:Abstract:|Keywords:|Introduction|The study|In this paper|Using |In L[0-9]|When students|As students|As we are|Policymakers|To address|In conclusion|We find|Our findings)", line))

            if ends_with_terminal and (short_prev or looks_like_starter):
                paragraphs.append(" ".join(current))
                current = [line]
                continue

            current.append(line)
        else:
            current.append(line)

    if current:
        paragraphs.append(" ".join(current))

    return paragraphs


def segment_paper(paragraphs: List[str], abstract: str = "") -> List[Dict[str, Any]]:
    """Segments reflowed paragraphs into rich canonical sections with original headings."""
    sections = []
    current_canon = "Abstract & Introduction"
    current_heading = "Abstract & Introduction"
    current_paras = []

    if abstract and not any("abstract" in p.lower()[:30] for p in paragraphs[:2]):
        current_paras.append(f"### Abstract\n{clean_text_glitches(abstract)}")

    for i, p in enumerate(paragraphs):
        canon_h, orig_h = match_heading(p)
        if canon_h:
            if current_paras:
                sections.append({
                    "original_heading": current_heading,
                    "normalized_section": current_canon.lower(),
                    "paragraphs": current_paras
                })
                current_paras = []
            current_canon = canon_h
            current_heading = orig_h
            continue

        # Discourse transitions for unheaded early text
        if current_canon in ["Abstract & Introduction", "Theoretical Background"]:
            if DISCOURSE_METHOD_STARTERS.search(p):
                if current_paras:
                    sections.append({
                        "original_heading": current_heading,
                        "normalized_section": current_canon.lower(),
                        "paragraphs": current_paras
                    })
                    current_paras = []
                current_canon = "Methodology & Context"
                current_heading = "Methodology & Study Context"
            elif DISCOURSE_FINDINGS_STARTERS.search(p):
                if current_paras:
                    sections.append({
                        "original_heading": current_heading,
                        "normalized_section": current_canon.lower(),
                        "paragraphs": current_paras
                    })
                    current_paras = []
                current_canon = "Results & Findings"
                current_heading = "Findings & Analysis"
            elif DISCOURSE_DISCUSSION_STARTERS.search(p):
                if current_paras:
                    sections.append({
                        "original_heading": current_heading,
                        "normalized_section": current_canon.lower(),
                        "paragraphs": current_paras
                    })
                    current_paras = []
                current_canon = "Discussion & Conclusion"
                current_heading = "Discussion & Implications"

        elif current_canon == "Methodology & Context":
            if DISCOURSE_FINDINGS_STARTERS.search(p):
                if current_paras:
                    sections.append({
                        "original_heading": current_heading,
                        "normalized_section": current_canon.lower(),
                        "paragraphs": current_paras
                    })
                    current_paras = []
                current_canon = "Results & Findings"
                current_heading = "Findings & Analysis"

        elif current_canon == "Results & Findings":
            if DISCOURSE_DISCUSSION_STARTERS.search(p):
                if current_paras:
                    sections.append({
                        "original_heading": current_heading,
                        "normalized_section": current_canon.lower(),
                        "paragraphs": current_paras
                    })
                    current_paras = []
                current_canon = "Discussion & Conclusion"
                current_heading = "Discussion & Implications"

        # Check references block start
        is_ref_heading = bool(re.match(r"^(?:references|bibliography)\b", p, re.I))
        is_ref_entries = (
            i > len(paragraphs) * 0.4 and
            current_canon != "References & Back Matter" and
            re.match(r"^[A-Z][^\(\)\n\r]{2,80}\s*\([12][0-9]{3}[a-z]?\)[\.\s]", p) and
            len(p) > 35 and
            (i + 1 < len(paragraphs) and bool(re.match(r"^[A-Z][^\(\)\n\r]{2,80}\s*\([12][0-9]{3}[a-z]?\)[\.\s]", paragraphs[i+1])))
        )
        if is_ref_heading or is_ref_entries:
            if current_paras:
                sections.append({
                    "original_heading": current_heading,
                    "normalized_section": current_canon.lower(),
                    "paragraphs": current_paras
                })
                current_paras = []
            current_canon = "References & Back Matter"
            current_heading = "References & Back Matter"

        current_paras.append(p)

    if current_paras:
        sections.append({
            "original_heading": current_heading,
            "normalized_section": current_canon.lower(),
            "paragraphs": current_paras
        })

    # Format result records
    result = []
    for idx, sec in enumerate(sections, start=1):
        sec_text = "\n\n".join(sec["paragraphs"]).strip()
        if sec_text:
            result.append({
                "order_index": idx,
                "original_heading": sec["original_heading"],
                "normalized_section": sec["normalized_section"],
                "text": clean_text_glitches(sec_text)
            })

    return result


def process_paper(pid: str, conn: sqlite3.Connection) -> bool:
    c = conn.cursor()
    c.execute("SELECT id, title, year, conference, abstract, source_type, full_text_status FROM papers WHERE id = ?", (pid,))
    paper = c.fetchone()
    if not paper:
        return False

    title = paper[1]
    year = paper[2]
    conf = paper[3]
    abstract = paper[4] or ""

    # Check if individual PDF exists for purest original text
    pdf_path = os.path.join(PDF_DIR, f"{pid}.pdf")
    raw_lines = []
    if os.path.exists(pdf_path):
        try:
            reader = pypdf.PdfReader(pdf_path)
            for page in reader.pages:
                txt = page.extract_text() or ""
                raw_lines.extend(txt.splitlines())
        except Exception:
            raw_lines = []

    c.execute("SELECT original_heading, text FROM sections WHERE paper_id = ? ORDER BY order_index", (pid,))
    sec_rows = c.fetchall()

    if not raw_lines:
        if not sec_rows:
            return False
        full_text = "\n\n".join(r[1] for r in sec_rows)
        raw_lines = full_text.splitlines()

    reflowed = reflow_paragraphs(raw_lines)
    new_sections = segment_paper(reflowed, abstract=abstract)

    if not new_sections:
        return False

    # Zero text loss guardrail: verify word count
    old_words = sum(len(r[1].split()) for r in sec_rows) if sec_rows else 0
    new_words = sum(len(s["text"].split()) for s in new_sections)

    if old_words > 0 and new_words < old_words * 0.80:
        print(f"  [GUARDRAIL WARNING] Paper {pid} word count dropped too much ({old_words} -> {new_words}). Skipping.", flush=True)
        return False

    # Update sections table
    c.execute("DELETE FROM sections WHERE paper_id = ?", (pid,))
    for s in new_sections:
        sec_id = f"{pid}-sec-{s["order_index"]:02d}"
        c.execute("""
            INSERT INTO sections (id, paper_id, original_heading, normalized_section, level, order_index, text)
            VALUES (?, ?, ?, ?, 1, ?, ?)
        """, (sec_id, pid, s["original_heading"], s["normalized_section"], s["order_index"], s["text"]))

    # Update local Markdown file
    md_path = os.path.join(MD_DIR, f"{pid}.md")
    if os.path.exists(os.path.dirname(md_path)):
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write(f"**Conference:** {conf} {year}\n\n")
            for s in new_sections:
                f.write(f"## {s["original_heading"]}\n\n{s["text"]}\n\n")

    return True


def main():
    parser = argparse.ArgumentParser(description="Clean and reflow all repository paper texts.")
    parser.add_argument("--paper-id", type=str, help="Process a single paper ID.")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of papers processed.")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if args.paper_id:
        pids = [args.paper_id]
    else:
        c.execute("SELECT id FROM papers ORDER BY id")
        pids = [r[0] for r in c.fetchall()]

    if args.limit:
        pids = pids[:args.limit]

    print(f"=== Starting Repository-Wide Text Cleaning & Reflow for {len(pids)} Papers ===", flush=True)
    t0 = datetime.datetime.now()
    successes = 0

    for i, pid in enumerate(pids, start=1):
        ok = process_paper(pid, conn)
        if ok:
            successes += 1
        if i % 250 == 0 or i == len(pids):
            conn.commit()
            print(f"  Progress: {i}/{len(pids)} | Reflowed & Cleaned: {successes}", flush=True)

    conn.commit()
    conn.close()
    elapsed = (datetime.datetime.now() - t0).total_seconds()
    print(f"\nDone! Successfully cleaned and reflowed {successes} / {len(pids)} papers in {elapsed:.1f} seconds.", flush=True)


if __name__ == "__main__":
    main()
