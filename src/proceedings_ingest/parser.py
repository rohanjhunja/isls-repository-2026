import re
import logging
from typing import Tuple, Dict, List

logger = logging.getLogger(__name__)

NORMALIZED_SECTIONS = [
    "methods",
    "results",
    "discussion_conclusion",
    "theoretical_background",
    "research_questions",
    "introduction",
    "references",
    "other",
]

# Section normalization keywords mapping - checked in priority order
SECTION_KEYWORDS: Dict[str, List[str]] = {
    "methods": [
        "method",
        "methods",
        "methodology",
        "methodological",
        "methodological approach",
        "methodological framework",
        "study design",
        "data collection",
        "analytical framework",
        "analytical approach",
        "participants",
        "intervention",
        "data sources",
        "data analysis",
        "measures",
        "procedure",
        "methods and context",
        "context and methods",
    ],
    "results": ["results", "findings", "analysis and results", "outcomes", "observations"],
    "discussion_conclusion": [
        "discussion",
        "conclusion",
        "conclusions",
        "implications",
        "concluding remarks",
        "limitations",
        "future work",
        "discussion and conclusion",
        "summary",
    ],
    "theoretical_background": [
        "theoretical framework",
        "conceptual framework",
        "literature review",
        "theoretical background",
        "related work",
        "perspectives",
        "prior work",
    ],
    "research_questions": ["research question", "rq", "objectives", "study focus", "goals"],
    "introduction": ["abstract", "introduction", "background", "overview", "problem statement", "motivation"],
    "references": ["references", "reference", "bibliography", "works cited", "literature cited"],
}


def normalize_section_heading(heading: str) -> str:
    """Map raw section heading string to canonical normalized section label."""
    if not heading or not heading.strip():
        return "other"

    clean = heading.lower().strip()
    # Strip leading section numbers e.g. "3.1 Study Design" -> "study design"
    clean = re.sub(r'^\d+(\.\d+)*\s*', '', clean)
    clean = re.sub(r'^([a-z]|\d+)\.\s*', '', clean)
    clean = clean.strip()

    # Direct match first
    for norm_label, keywords in SECTION_KEYWORDS.items():
        if clean in keywords:
            return norm_label

    # Substring / token match
    for norm_label, keywords in SECTION_KEYWORDS.items():
        for kw in keywords:
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, clean):
                return norm_label

    return "other"


def extract_sections_from_markdown(paper_md: str) -> List[Tuple[str, str, int, str]]:
    """Extract section blocks from a single paper's Markdown text.
    Returns list of tuples: (original_heading, normalized_section, header_level, section_text)."""
    lines = paper_md.splitlines()
    sections: List[Tuple[str, str, int, str]] = []
    
    current_heading = "Abstract / Intro"
    current_level = 1
    current_lines: List[str] = []

    header_regex = re.compile(r'^(#{1,4})\s+(.+)$')

    for line in lines:
        m = header_regex.match(line.strip())
        if m:
            if current_lines:
                sec_text = "\n".join(current_lines).strip()
                if sec_text:
                    norm = normalize_section_heading(current_heading)
                    sections.append((current_heading, norm, current_level, sec_text))
            
            level = len(m.group(1))
            current_heading = m.group(2).strip()
            current_level = level
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sec_text = "\n".join(current_lines).strip()
        if sec_text:
            norm = normalize_section_heading(current_heading)
            sections.append((current_heading, norm, current_level, sec_text))

    return sections
