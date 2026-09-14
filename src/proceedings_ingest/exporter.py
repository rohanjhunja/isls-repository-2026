import os
import csv
import io
import zipfile
from typing import Dict, Any, List
from proceedings_ingest.review_service import ReviewService


class ReviewExporter:
    def __init__(self, review_service: ReviewService):
        self.review_service = review_service

    def export_literature_review_csv(self, review_id: str) -> str:
        review = self.review_service.get_review(review_id)
        if not review:
            raise ValueError(f"Review {review_id} not found")

        table_data = self.review_service.build_review_table(review_id)
        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        writer.writerow(review.selected_columns)

        # Data rows
        for row in table_data:
            line = []
            for col in review.selected_columns:
                val = row.get(col)
                if isinstance(val, dict):
                    line.append(val.get("value") or "")
                else:
                    line.append(val or "")
            writer.writerow(line)

        return output.getvalue()

    def export_evidence_csv(self, review_id: str) -> str:
        review = self.review_service.get_review(review_id)
        if not review:
            raise ValueError(f"Review {review_id} not found")

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Paper ID", "Property ID", "Property Version", "Status", "Method", "Section ID", "PDF Page", "Supporting Text"])

        for pid in review.paper_ids:
            for col in review.selected_columns:
                if col in ["paper_id", "title", "authors", "year", "abstract", "keywords", "filename"]:
                    continue
                obs = self.review_service._load_observation(pid, col)
                if obs:
                    status_str = obs.status.value if hasattr(obs.status, "value") else str(obs.status)
                    if obs.evidence:
                        for ev in obs.evidence:
                            writer.writerow([
                                pid, col, obs.property_version, status_str, obs.method,
                                ev.section_id or "", ev.pdf_page or "", ev.supporting_text
                            ])
                    else:
                        writer.writerow([pid, col, obs.property_version, status_str, obs.method, "", "", ""])

        return output.getvalue()

    def export_search_definition_csv(self, review_id: str) -> str:
        review = self.review_service.get_review(review_id)
        if not review:
            raise ValueError(f"Review {review_id} not found")

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Field", "Value"])

        search_def = review.search_definition
        if search_def:
            writer.writerow(["Version", search_def.version])
            writer.writerow(["Original Prompt", search_def.original_prompt or ""])
            writer.writerow(["Keywords", ", ".join(search_def.original_keywords)])
            writer.writerow(["Expansions", ", ".join(search_def.accepted_expansions)])
            writer.writerow(["Exclusions", ", ".join(search_def.exclusions)])
        else:
            writer.writerow(["Scope Prompt", review.scope.review_prompt or ""])
            writer.writerow(["Scope Keywords", ", ".join(review.scope.keywords)])
            writer.writerow(["Scope Exclusions", ", ".join(review.scope.exclusions)])

        return output.getvalue()

    def export_data_dictionary_csv(self, review_id: str) -> str:
        review = self.review_service.get_review(review_id)
        if not review:
            raise ValueError(f"Review {review_id} not found")

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Column ID", "Kind", "Label / Description", "Version"])

        for col in review.selected_columns:
            if col in ["paper_id", "title", "authors", "year", "abstract", "keywords", "filename"]:
                writer.writerow([col, "canonical_paper_field", col.capitalize(), "1.0.0"])
            else:
                prop = self.review_service.property_registry.get_property(col)
                if prop:
                    writer.writerow([col, "extracted_property", prop.label, prop.version])
                else:
                    writer.writerow([col, "unknown_property", col, "1.0.0"])

        return output.getvalue()

    def export_bundle_zip(self, review_id: str, output_path: str):
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("Literature Review.csv", self.export_literature_review_csv(review_id))
            zf.writestr("Search Definition.csv", self.export_search_definition_csv(review_id))
            zf.writestr("Evidence.csv", self.export_evidence_csv(review_id))
            zf.writestr("Data Dictionary.csv", self.export_data_dictionary_csv(review_id))
