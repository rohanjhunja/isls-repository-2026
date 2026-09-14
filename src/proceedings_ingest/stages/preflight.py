import re
import pdfplumber
from typing import Dict, Any, List


class PreflightStage:

    def __init__(self, profile_manager):
        self.profile_manager = profile_manager

    def inspect(
        self, pdf_path: str, sample_pages: int = 40
    ) -> Dict[str, Any]:
        results = {
            "has_usable_text": True,
            "sample_page_count": sample_pages,
            "toc_entries": [],
            "suggested_profile": None,
            "typography_sample": [],
        }

        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            sample_count = min(sample_pages, total_pages)

            # Check text usability
            text_lengths = []
            for i in range(sample_count):
                page_text = pdf.pages[i].extract_text() or ""
                text_lengths.append(len(page_text.strip()))

            avg_text = sum(text_lengths) / max(1, len(text_lengths))
            if avg_text < 50:
                results["has_usable_text"] = False

            # Extract TOC entries from front matter (pages 5 to 40)
            toc_entries = []
            toc_pattern1 = re.compile(
                r"^(.+?)\s*\.{3,}\s*(\d+|[ivxlcdm]+)$", re.IGNORECASE
            )
            toc_pattern2 = re.compile(
                r"^([A-Z0-9\s\:\,\-\–\—\?\’\'\“\”\(\)]+)\s+(\d+)\s*$", re.IGNORECASE
            )

            for i in range(min(45, total_pages)):
                text = pdf.pages[i].extract_text() or ""
                lines = text.split("\n")
                for line in lines:
                    line_str = line.strip()
                    if not line_str or line_str.startswith(".") or len(line_str) < 12:
                        continue

                    m1 = toc_pattern1.match(line_str)
                    m2 = toc_pattern2.match(line_str) if not m1 else None

                    title_part = None
                    page_part = None

                    if m1:
                        title_part = m1.group(1).strip()
                        page_part = m1.group(2).strip()
                    elif m2:
                        title_part = m2.group(1).strip()
                        page_part = m2.group(2).strip()

                    if title_part and page_part:
                        # Filter non-paper headers
                        lower_t = title_part.lower()
                        if not any(
                            k in lower_t
                            for k in [
                                "table of contents",
                                "isls proceedings",
                                "long papers",
                                "short papers",
                                "posters",
                                "symposia",
                                "keynotes",
                            ]
                        ):
                            toc_entries.append(
                                {
                                    "title": title_part,
                                    "printed_page": page_part,
                                    "toc_pdf_page": i + 1,
                                }
                            )

            results["toc_entries"] = toc_entries
            filename = pdf_path.split("/")[-1]
            profile = self.profile_manager.get_profile_for_filename(filename)
            results["suggested_profile"] = profile.get("profile", {}).get(
                "id", "common-base"
            )

        return results
