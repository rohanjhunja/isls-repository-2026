import json
import os
import re
from datetime import datetime
from typing import Dict, Any, Tuple

from proceedings_ingest.models import Collection, ConferenceInfo, SourceInfo, IngestionReport
from proceedings_ingest.profiles import ProfileManager
from proceedings_ingest.stages.register import RegisterStage
from proceedings_ingest.stages.preflight import PreflightStage
from proceedings_ingest.stages.extraction import ExtractionStage
from proceedings_ingest.stages.segmentation import SegmentationStage
from proceedings_ingest.stages.metadata_sections import MetadataSectionsStage
from proceedings_ingest.stages.indexing import IndexingStage
from proceedings_ingest.utils.update_paper_conference_year import parse_conference_and_year


class Pipeline:

    def __init__(self, base_dir: str, max_memory_gb: float = 8.0):
        self.base_dir = base_dir
        self.max_memory_gb = max_memory_gb
        self.data_dir = os.path.join(base_dir, "data")
        self.profiles_dir = os.path.join(base_dir, "profiles")
        self.reports_dir = os.path.join(self.data_dir, "reports")
        os.makedirs(self.reports_dir, exist_ok=True)

        self.profile_manager = ProfileManager(self.profiles_dir)
        self.register_stage = RegisterStage(self.data_dir)
        self.preflight_stage = PreflightStage(self.profile_manager)
        self.extraction_stage = ExtractionStage(self.data_dir, max_memory_gb=max_memory_gb)
        self.indexing_stage = IndexingStage(self.data_dir)

    def run_ingestion(
        self, pdf_path: str, collection_id: str = "isls-2026", year: int = 2026
    ) -> Tuple[Collection, IngestionReport]:
        check_memory(self.max_memory_gb)
        filename = os.path.basename(pdf_path)
        doc_id = os.path.splitext(filename)[0].lower().replace(" ", "-")
        doc_id = re.sub(r"-+", "-", doc_id).strip("-")

        conf_meta, parsed_year = parse_conference_and_year(f"{doc_id} {filename}")
        if year == 2026 and parsed_year:
            year = parsed_year
        if collection_id == "isls-2026":
            collection_id = f"{conf_meta['acronym'].lower()}-{year}"

        # 1. Register file
        reg_record = self.register_stage.register_file(
            pdf_path, collection_id=collection_id, year=year
        )
        source_pdf_path = reg_record["source_path"]

        # 2. Preflight
        check_memory(self.max_memory_gb)
        preflight_res = self.preflight_stage.inspect(source_pdf_path)
        toc_entries = preflight_res.get("toc_entries", [])

        # Load profile
        profile = self.profile_manager.get_profile_for_filename(filename)

        # 3. Extraction & page furniture cleanup
        check_memory(self.max_memory_gb)
        md_path, manifest_path, audit_summary = self.extraction_stage.extract_blocks_and_markdown(
            source_pdf_path, doc_id, profile
        )
        force_garbage_collection()

        # 4. Segmentation
        check_memory(self.max_memory_gb)
        segmentation = SegmentationStage(profile)
        boundaries = segmentation.detect_paper_boundaries(source_pdf_path, toc_entries)

        # 5. Metadata & Canonical Section extraction
        check_memory(self.max_memory_gb)
        metadata_stage = MetadataSectionsStage(self.data_dir, self.profile_manager)
        papers = metadata_stage.process_paper_boundaries(
            source_pdf_path, doc_id, boundaries, profile
        )
        force_garbage_collection()

        # 6. Build Collection Pydantic Model
        collection = Collection(
            id=collection_id,
            kind="conference_proceedings",
            title=f"Proceedings of {collection_id.upper()}",
            conference=ConferenceInfo(
                name=conf_meta["name"],
                acronym=conf_meta["acronym"],
                year=year,
            ),
            source=SourceInfo(
                filename=filename,
                sha256=reg_record["sha256"],
                pdf_page_count=reg_record["pdf_page_count"],
                markdown_path=md_path,
            ),
            papers=papers,
        )

        # Save Collection JSON in data/derived/
        collection_json_path = os.path.join(
            self.data_dir, "derived", doc_id, f"{doc_id}.json"
        )
        with open(collection_json_path, "w", encoding="utf-8") as f:
            f.write(collection.model_dump_json(indent=2))

        # 7. SQLite FTS Indexing
        check_memory(self.max_memory_gb)
        self.indexing_stage.build_index(collection)
        force_garbage_collection()

        # 8. Ingestion Report
        conf_scores = [p.extraction.paper_boundary_confidence for p in papers]
        avg_conf = sum(conf_scores) / max(1, len(conf_scores))

        missing_fields = {"title": 0, "authors": 0, "abstract": 0}
        unmapped_headings = 0
        for p in papers:
            if not p.title:
                missing_fields["title"] += 1
            if not p.authors:
                missing_fields["authors"] += 1
            if not p.abstract:
                missing_fields["abstract"] += 1

            for sec in p.sections:
                if not sec.canonical_roles:
                    unmapped_headings += 1

        report = IngestionReport(
            source_filename=filename,
            sha256=reg_record["sha256"],
            pdf_page_count=reg_record["pdf_page_count"],
            detected_papers_count=len(papers),
            expected_toc_count=len(toc_entries),
            boundaries_confidence_avg=round(avg_conf, 3),
            unmapped_headings_count=unmapped_headings,
            missing_fields_summary=missing_fields,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

        report_path = os.path.join(self.reports_dir, f"ingestion_{doc_id}.json")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report.model_dump_json(indent=2))

        return collection, report

