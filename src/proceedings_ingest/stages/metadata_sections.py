import os
import re
import pypdf
from typing import Dict, Any, List, Tuple
from proceedings_ingest.models import Paper, Author, Section, PageRange, ExtractionMetadata
from proceedings_ingest.profiles import ProfileManager


class MetadataSectionsStage:

    def __init__(self, data_dir: str, profile_manager: ProfileManager):
        self.data_dir = data_dir
        self.profile_manager = profile_manager

    def process_paper_boundaries(
        self,
        pdf_path: str,
        doc_id: str,
        boundaries: List[Dict[str, Any]],
        profile: Dict[str, Any],
    ) -> List[Paper]:
        papers_dir = os.path.join(self.data_dir, "derived", doc_id, "papers")
        os.makedirs(papers_dir, exist_ok=True)

        canonical_map = profile.get("canonical_sections", {})
        papers = []

        reader = pypdf.PdfReader(pdf_path)
        total_pages = len(reader.pages)

        for b in boundaries:
            paper_id = b["paper_id"]
            p_start = b["pdf_start"]
            p_end = b["pdf_end"]

            paper_lines = []
            for p_idx in range(p_start - 1, min(p_end, total_pages)):
                page_text = reader.pages[p_idx].extract_text() or ""
                for line in page_text.split("\n"):
                    line_s = line.strip()
                    if not line_s:
                        continue
                    if (
                        "proceedings" in line_s.lower()
                        or "© isls" in line_s.lower()
                    ):
                        continue
                    paper_lines.append(line_s)

            if not paper_lines:
                continue

            title = b.get("title") or paper_lines[0]
            authors = []
            abstract_text = None
            keywords = []

            abstract_idx = -1
            for idx, line in enumerate(paper_lines):
                if re.match(r"^abstract:?", line, re.IGNORECASE):
                    abstract_idx = idx
                    break

            if abstract_idx != -1:
                abs_lines = []
                curr_idx = abstract_idx
                line_abs = paper_lines[curr_idx]
                abs_body = re.sub(r"^abstract:?", "", line_abs, flags=re.IGNORECASE).strip()
                if abs_body:
                    abs_lines.append(abs_body)

                curr_idx += 1
                while curr_idx < len(paper_lines):
                    l = paper_lines[curr_idx]
                    if re.match(r"^(keywords|introduction|background|methods?|1\.)", l, re.IGNORECASE):
                        break
                    abs_lines.append(l)
                    curr_idx += 1

                abstract_text = " ".join(abs_lines).strip()

                author_raw_lines = paper_lines[1:abstract_idx]
                for a_line in author_raw_lines:
                    parts = re.split(r"[,;]", a_line)
                    for p in parts:
                        p_clean = p.strip()
                        if p_clean and not any(char.isdigit() for char in p_clean) and "@" not in p_clean and "university" not in p_clean.lower():
                            names = p_clean.split()
                            if len(names) >= 2:
                                authors.append(
                                    Author(
                                        display_name=p_clean,
                                        given_name=names[0],
                                        family_name=names[-1],
                                    )
                                )

            sections = []
            canonical_sections_map: Dict[str, List[str]] = {
                "introduction": [],
                "method": [],
                "analysis": [],
                "results": [],
                "discussion": [],
                "conclusion": [],
            }

            heading_regex = re.compile(
                r"^(\d+[\.\d]*\s+)?"
                r"(introduction|background|methodology|methods|study context|data collection|analysis|results|findings|discussion|conclusion|references)",
                re.IGNORECASE,
            )

            sec_chunks: List[Tuple[str, List[str]]] = []
            current_heading = "Introduction"
            current_text_lines = []

            for l in paper_lines:
                m = heading_regex.match(l.strip())
                if m:
                    if current_text_lines:
                        sec_chunks.append((current_heading, current_text_lines))
                    current_heading = l.strip()
                    current_text_lines = []
                else:
                    current_text_lines.append(l)

            if current_text_lines:
                sec_chunks.append((current_heading, current_text_lines))

            sec_id_counter = 1
            for h_orig, txt_lines in sec_chunks:
                mapped_roles = self.profile_manager.map_heading_to_canonical_roles(
                    h_orig, canonical_map
                )
                sec_id = f"sec-{sec_id_counter:03d}"
                sec_text = "\n".join(txt_lines).strip()

                section_obj = Section(
                    id=sec_id,
                    heading_original=h_orig,
                    heading_normalized=h_orig.strip(),
                    level=1,
                    canonical_roles=mapped_roles,
                    text=sec_text,
                    pages=PageRange(pdf_start=p_start, pdf_end=p_end),
                )
                sections.append(section_obj)

                for role in mapped_roles:
                    canonical_sections_map.setdefault(role, []).append(sec_id)

                sec_id_counter += 1

            from proceedings_ingest.utils.update_paper_conference_year import parse_conference_and_year
            from proceedings_ingest.models import ConferenceInfo
            conf_meta, doc_year = parse_conference_and_year(f"{doc_id} {os.path.basename(pdf_path)}")

            paper_obj = Paper(
                id=f"{doc_id}-{paper_id}",
                title=title,
                authors=authors,
                keywords=keywords,
                abstract=abstract_text,
                proceedings_section=b.get("proceedings_section") or b.get("section"),
                conference=ConferenceInfo(
                    name=conf_meta["name"],
                    acronym=conf_meta["acronym"],
                    year=doc_year,
                ),
                year=doc_year,
                filename=os.path.basename(pdf_path),
                pages=PageRange(
                    pdf_start=p_start,
                    pdf_end=p_end,
                    printed_start=b.get("printed_start"),
                    printed_end=b.get("printed_end"),
                ),
                canonical_sections=canonical_sections_map,
                sections=sections,
                extraction=ExtractionMetadata(
                    profile_id=profile.get("profile", {}).get("id", "common-base"),
                    profile_version=profile.get("profile", {}).get("version", "1.0.0"),
                    paper_boundary_confidence=b.get("confidence", 0.90),
                    field_status={
                        "title": "extracted" if title else "not_present",
                        "authors": "extracted" if authors else "not_present",
                        "abstract": "extracted" if abstract_text else "not_present",
                    },
                ),
            )
            papers.append(paper_obj)

            paper_md_path = os.path.join(papers_dir, f"{paper_id}.md")
            with open(paper_md_path, "w", encoding="utf-8") as f:
                f.write(f"# {title}\n\n")
                if authors:
                    f.write(f"**Authors:** {'; '.join(a.display_name for a in authors)}\n\n")
                if abstract_text:
                    f.write(f"## Abstract\n\n{abstract_text}\n\n")
                for s in sections:
                    f.write(f"## {s.heading_original}\n\n{s.text}\n\n")

        return papers
