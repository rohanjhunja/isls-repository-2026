import re
import pypdf
from typing import Dict, Any, List
from rapidfuzz import fuzz


class SegmentationStage:

    def __init__(self, profile: Dict[str, Any]):
        self.profile = profile

    def detect_paper_boundaries(
        self, pdf_path: str, preflight_toc: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        detected_papers = []
        reader = pypdf.PdfReader(pdf_path)
        total_pages = len(reader.pages)

        printed_to_pdf: Dict[int, int] = {}
        # Sample printed pages
        for i in range(total_pages):
            pdf_num = i + 1
            text = reader.pages[i].extract_text() or ""
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            for line in lines[:3] + lines[-3:]:
                if line.isdigit():
                    printed_val = int(line)
                    if printed_val not in printed_to_pdf:
                        printed_to_pdf[printed_val] = pdf_num

        # Pre-cache first lines of all pages to avoid re-parsing PDF pages in inner loops
        page_first_lines: List[str] = []
        for p in range(total_pages):
            try:
                t = reader.pages[p].extract_text() or ""
                page_first_lines.append("\n".join(t.split("\n")[:6]).lower())
            except Exception:
                page_first_lines.append("")

        if preflight_toc:
            for idx, entry in enumerate(preflight_toc):
                title = entry["title"]
                printed_p = entry["printed_page"]

                pdf_start = None
                if printed_p.isdigit() and int(printed_p) in printed_to_pdf:
                    pdf_start = printed_to_pdf[int(printed_p)]
                else:
                    # Scan candidate pages using cached page lines
                    best_score = 0
                    best_p = None
                    title_lower = title.lower()
                    for p in range(15, min(total_pages, 3300)):
                        first_lines = page_first_lines[p]
                        if not first_lines:
                            continue
                        score = fuzz.partial_ratio(title_lower, first_lines)
                        if score > 85 and score > best_score:
                            best_score = score
                            best_p = p + 1
                    pdf_start = best_p

                if pdf_start:
                    paper_id = f"paper-{idx+1:04d}"
                    detected_papers.append(
                        {
                            "paper_id": paper_id,
                            "title": title,
                            "pdf_start": pdf_start,
                            "printed_start": printed_p,
                            "confidence": 0.95 if printed_p.isdigit() else 0.85,
                        }
                    )

        if detected_papers:
            detected_papers.sort(key=lambda x: x["pdf_start"])
            for i in range(len(detected_papers)):
                if i < len(detected_papers) - 1:
                    detected_papers[i]["pdf_end"] = max(
                        detected_papers[i]["pdf_start"],
                        detected_papers[i + 1]["pdf_start"] - 1,
                    )
                    detected_papers[i]["printed_end"] = str(
                        detected_papers[i]["pdf_end"]
                    )
                else:
                    detected_papers[i]["pdf_end"] = total_pages
                    detected_papers[i]["printed_end"] = str(total_pages)
        else:
            current_start = 18
            paper_idx = 1
            for p in range(17, total_pages):
                text = reader.pages[p].extract_text() or ""
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                has_abstract = any(
                    l.lower().startswith("abstract") for l in lines[:5]
                )
                if has_abstract and p + 1 > current_start + 1:
                    detected_papers.append(
                        {
                            "paper_id": f"paper-{paper_idx:04d}",
                            "title": lines[0] if lines else f"Paper {paper_idx}",
                            "pdf_start": current_start,
                            "pdf_end": p,
                            "printed_start": str(current_start),
                            "printed_end": str(p),
                            "confidence": 0.80,
                        }
                    )
                    current_start = p + 1
                    paper_idx += 1

            if current_start <= total_pages:
                detected_papers.append(
                    {
                        "paper_id": f"paper-{paper_idx:04d}",
                        "title": f"Paper {paper_idx}",
                        "pdf_start": current_start,
                        "pdf_end": total_pages,
                        "printed_start": str(current_start),
                        "printed_end": str(total_pages),
                        "confidence": 0.80,
                    }
                )

        return detected_papers
