import os
import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from rapidfuzz import fuzz

from proceedings_ingest.models import GroundTruthPaper, Paper, Section, PageRange, MarkdownRange, ExtractionMetadata, Author
from proceedings_ingest.parser import extract_sections_from_markdown

logger = logging.getLogger(__name__)


def clean_title_for_matching(title: str) -> str:
    """Normalize title string for fuzzy boundary matching."""
    if not title:
        return ""
    clean = re.sub(r'[^\w\s]', '', title.lower())
    return " ".join(clean.split())


class VerifiedMDChunker:
    """Slices proceedings Markdown files into paper records verified against DSpace ground truth."""

    def __init__(self, registry_path: str = "data/derived/ground_truth_registry.json", md_dir: str = "proceedings_md"):
        self.registry_path = registry_path
        self.md_dir = md_dir
        self.ground_truth: Dict[str, Any] = {}
        self.md_cache: Dict[str, str] = {}
        self.header_index_cache: Dict[str, List[Tuple[int, str, str]]] = {}
        self._load_registry()

    def _load_registry(self):
        if os.path.exists(self.registry_path):
            with open(self.registry_path, "r", encoding="utf-8") as f:
                self.ground_truth = json.load(f)
            logger.info(f"Loaded ground truth registry from {self.registry_path} ({self.ground_truth.get('total_papers', 0)} papers)")
        else:
            logger.warning(f"Ground truth registry file not found at {self.registry_path}")

    def _build_header_index(self, fname: str, md_text: str) -> List[Tuple[int, str, str]]:
        headers = []
        for idx, line in enumerate(md_text.splitlines()):
            line_s = line.strip()
            if line_s.startswith('#') or len(line_s) > 15:
                clean_t = clean_title_for_matching(line_s)
                if len(clean_t) > 12:
                    headers.append((idx, line_s, clean_t))
        return headers

    def load_proceedings_md_for_year(self, year: int) -> Dict[str, str]:
        """Load all proceedings markdown text files available for a given year (icls, cscl, isls)."""
        year_mds = {}
        for prefix in ["icls", "cscl", "isls"]:
            fname = f"{prefix}-{year}.md"
            fpath = os.path.join(self.md_dir, fname)
            if os.path.exists(fpath):
                if fname not in self.md_cache:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                        self.md_cache[fname] = content
                        self.header_index_cache[fname] = self._build_header_index(fname, content)
                year_mds[fname] = self.md_cache[fname]
        return year_mds

    def find_paper_title_in_mds(self, year_mds: Dict[str, str], target_title: str) -> Tuple[Optional[str], int, float]:
        """Search across indexed header lines for a given year to find matching paper title line."""
        target_clean = clean_title_for_matching(target_title)
        if not target_clean:
            return None, -1, 0.0

        best_fname = None
        best_idx = -1
        best_score = 0.0

        for fname, md_text in year_mds.items():
            if fname not in self.header_index_cache:
                self.header_index_cache[fname] = self._build_header_index(fname, md_text)
            
            headers = self.header_index_cache[fname]

            for idx, line_s, line_clean in headers:
                score = fuzz.ratio(target_clean, line_clean)
                if score > 80 and score > best_score:
                    best_score = score
                    best_idx = idx
                    best_fname = fname
                    if score > 92:
                        return best_fname, best_idx, round(best_score / 100.0, 2)

        if best_score < 70:
            for fname, md_text in year_mds.items():
                headers = self.header_index_cache.get(fname, [])

                for idx, line_s, line_clean in headers:
                    score = fuzz.partial_ratio(target_clean, line_clean)
                    if score > 85 and score > best_score:
                        best_score = score
                        best_idx = idx
                        best_fname = fname
                        if score > 92:
                            return best_fname, best_idx, round(best_score / 100.0, 2)

        return best_fname, best_idx, round(best_score / 100.0, 2)

    def chunk_paper_from_gt(self, gt_paper: Dict[str, Any], year_mds: Dict[str, str]) -> Paper:
        """Chunk a single paper record by finding its title in year proceedings MDs."""
        paper_title = gt_paper["title"]
        fname, title_idx, confidence = self.find_paper_title_in_mds(year_mds, paper_title)

        sections: List[Section] = []

        if fname and title_idx != -1:
            md_lines = year_mds[fname].splitlines()
            end_idx = min(title_idx + 400, len(md_lines))
            paper_raw_lines = md_lines[title_idx:end_idx]
            paper_raw_md = "\n".join(paper_raw_lines)

            extracted_secs = extract_sections_from_markdown(paper_raw_md)
            clean_gt_title = clean_title_for_matching(paper_title)

            for idx, (orig_heading, norm_section, level, sec_text) in enumerate(extracted_secs):
                if clean_title_for_matching(orig_heading) == clean_gt_title and len(sections) == 0:
                    continue

                sec_obj = Section(
                    id=f"{gt_paper['id']}_sec_{len(sections)+1}",
                    heading_original=orig_heading,
                    heading_normalized=norm_section,
                    level=level,
                    text=sec_text,
                    pages=PageRange(
                        pdf_start=gt_paper.get("start_page") or 1,
                        pdf_end=gt_paper.get("end_page") or 1,
                    ),
                    markdown_range=MarkdownRange(
                        start_line=title_idx + 1,
                        end_line=end_idx,
                    ),
                )
                sections.append(sec_obj)

        if not sections:
            sec_text = gt_paper.get("abstract") or gt_paper["title"]
            sections.append(
                Section(
                    id=f"{gt_paper['id']}_sec_1",
                    heading_original="Abstract",
                    heading_normalized="introduction",
                    level=1,
                    text=sec_text,
                    pages=PageRange(
                        pdf_start=gt_paper.get("start_page") or 1,
                        pdf_end=gt_paper.get("end_page") or 1,
                    ),
                )
            )
            confidence = 0.5 if not fname else confidence

        author_objs = [Author(display_name=a) for a in gt_paper.get("authors", [])]

        return Paper(
            id=gt_paper["id"],
            title=gt_paper["title"],
            authors=author_objs,
            abstract=gt_paper.get("abstract"),
            keywords=[],
            year=gt_paper["year"],
            filename=fname or f"isls-{gt_paper['year']}.md",
            pages=PageRange(
                pdf_start=gt_paper.get("start_page") or 1,
                pdf_end=gt_paper.get("end_page") or 1,
            ),
            sections=sections,
            extraction=ExtractionMetadata(
                profile_id="dspace_verified_md",
                profile_version="2.0.0",
                paper_boundary_confidence=confidence,
                field_status={"title": "verified", "authors": "verified", "doi": "verified" if gt_paper.get("doi") else "missing"},
                warnings=[] if confidence >= 0.7 else ["Low boundary confidence (<0.7). Flagged for PyMuPDF/GROBID fallback."],
            ),
        )
