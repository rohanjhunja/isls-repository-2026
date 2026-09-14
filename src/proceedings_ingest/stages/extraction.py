import json
import os
import re
import pypdf
from typing import Dict, Any, List, Tuple
from proceedings_ingest.utils.memory import check_memory, force_garbage_collection


class ExtractionStage:

    def __init__(self, data_dir: str, max_memory_gb: float = 8.0):
        self.data_dir = data_dir
        self.max_memory_gb = max_memory_gb

    def extract_blocks_and_markdown(
        self, pdf_path: str, doc_id: str, profile: Dict[str, Any]
    ) -> Tuple[str, str, Dict[str, Any]]:
        """Extract layout blocks, filter page furniture, and save clean Markdown.

        High-performance stream processing using pypdf. Returns
        (markdown_path, manifest_path, audit_summary).
        """
        output_dir = os.path.join(self.data_dir, "derived", doc_id)
        os.makedirs(output_dir, exist_ok=True)

        markdown_path = os.path.join(output_dir, "proceedings.md")
        manifest_path = os.path.join(output_dir, "blocks_manifest.jsonl")

        furniture_rules = profile.get("page_furniture", {})
        header_patterns = [
            re.compile(p, re.IGNORECASE)
            for p in furniture_rules.get("header_patterns", [])
        ]
        footer_patterns = [
            re.compile(p, re.IGNORECASE)
            for p in furniture_rules.get("footer_patterns", [])
        ]

        markdown_lines = []
        removed_furniture_count = 0
        total_blocks_count = 0

        check_memory(self.max_memory_gb)
        reader = pypdf.PdfReader(pdf_path)
        total_pages = len(reader.pages)

        with open(manifest_path, "w", encoding="utf-8") as manifest_file:
            for page_idx in range(total_pages):
                if page_idx % 50 == 0:
                    check_memory(self.max_memory_gb)

                pdf_page_num = page_idx + 1
                page_text = reader.pages[page_idx].extract_text() or ""
                lines = [l.strip() for l in page_text.split("\n") if l.strip()]

                page_line_texts = []
                printed_page_str = None

                for line_idx, line_text in enumerate(lines):
                    total_blocks_count += 1
                    is_furniture = False
                    furniture_reason = None

                    # Check edge positions (first 3 or last 3 lines on page)
                    is_edge_line = (line_idx <= 2) or (line_idx >= len(lines) - 3)

                    if is_edge_line:
                        for pattern in header_patterns + footer_patterns:
                            if pattern.search(line_text):
                                is_furniture = True
                                furniture_reason = f"Matched furniture pattern: {pattern.pattern}"
                                break

                        if not is_furniture and re.match(
                            r"^(\d+|[ivxlcdm]+)$", line_text, re.IGNORECASE
                        ):
                            is_furniture = True
                            printed_page_str = line_text
                            furniture_reason = "Isolated edge page number"

                    if (
                        "proceedings" in line_text.lower()
                        or "© isls" in line_text.lower()
                    ) and is_edge_line:
                        is_furniture = True
                        furniture_reason = "Matched proceedings edge header"
                        page_match = re.search(
                            r"\b(\d+|[ivxlcdm]+)\b", line_text, re.IGNORECASE
                        )
                        if page_match:
                            printed_page_str = page_match.group(1)

                    block_record = {
                        "block_id": f"p{pdf_page_num:04d}-b{line_idx:04d}",
                        "pdf_page": pdf_page_num,
                        "printed_page": printed_page_str or str(pdf_page_num),
                        "text": line_text,
                        "is_furniture": is_furniture,
                        "furniture_reason": furniture_reason,
                    }
                    manifest_file.write(json.dumps(block_record) + "\n")

                    if is_furniture:
                        removed_furniture_count += 1
                    else:
                        page_line_texts.append(line_text)

                printed_disp = printed_page_str or str(pdf_page_num)
                markdown_lines.append(
                    f"<!-- page: pdf={pdf_page_num} printed={printed_disp} -->"
                )
                markdown_lines.extend(page_line_texts)
                markdown_lines.append("")

        with open(markdown_path, "w", encoding="utf-8") as f:
            f.write("\n".join(markdown_lines))

        # Explicitly clean up reader objects and trigger GC
        del reader
        force_garbage_collection()

        audit_summary = {
            "total_blocks": total_blocks_count,
            "removed_furniture": removed_furniture_count,
            "retained_blocks": total_blocks_count - removed_furniture_count,
            "markdown_path": markdown_path,
            "manifest_path": manifest_path,
        }
        return markdown_path, manifest_path, audit_summary

