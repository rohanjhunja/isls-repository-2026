import re
import uuid
from typing import Dict, Any, List, Optional
from proceedings_ingest.models import Paper, Section
from proceedings_ingest.review_models import (
    PropertyDefinition, Observation, ObservationStatus, EvidenceItem
)


class ExtractionEngine:
    def __init__(self, run_id: Optional[str] = None):
        self.run_id = run_id or str(uuid.uuid4())[:8]

    def extract_property(
        self, paper: Paper, prop: PropertyDefinition, existing_obs: Optional[Observation] = None
    ) -> Observation:
        # Step 1: Reuse existing valid observation if unaffected and present
        if existing_obs and existing_obs.property_version == prop.version and existing_obs.status == ObservationStatus.EXTRACTED:
            return existing_obs

        # Step 2: Select candidate sections
        candidate_sections = self._select_candidate_sections(paper, prop)

        # Step 3: Attempt deterministic strategies
        det_result = self._extract_deterministic(paper, prop, candidate_sections)
        if det_result:
            return det_result

        # Step 4: Fallback to targeted prompted/AI analysis if allowed
        if prop.extraction.inference_allowed:
            inferred_result = self._extract_prompted(paper, prop, candidate_sections)
            if inferred_result:
                return inferred_result

        # Step 5: Default unresolved / not present
        return Observation(
            paper_id=paper.id,
            property_id=prop.id,
            property_version=prop.version,
            value=None,
            status=ObservationStatus.NOT_PRESENT,
            evidence=[],
            method="rule_fallback",
            confidence=0.0,
            run_id=self.run_id
        )

    def _select_candidate_sections(self, paper: Paper, prop: PropertyDefinition) -> List[Section]:
        if not prop.query or not prop.query.candidate_sections:
            return paper.sections

        matched = []
        target_roles = [s.lower() for s in prop.query.candidate_sections]
        target_headings = [h.lower() for h in (prop.query.heading_terms or [])]

        for sec in paper.sections:
            sec_roles = [r.lower() for r in sec.canonical_roles]
            sec_heading = sec.heading_normalized.lower()
            if any(r in sec_roles for r in target_roles) or any(h in sec_heading for h in target_headings):
                matched.append(sec)

        return matched if matched else paper.sections

    def _extract_deterministic(
        self, paper: Paper, prop: PropertyDefinition, sections: List[Section]
    ) -> Optional[Observation]:
        text_terms = [t.lower() for t in (prop.query.text_terms if prop.query else [])]
        allowed_vals = prop.constraints.allowed_values if prop.constraints else None

        for sec in sections:
            sec_text = sec.text
            # Controlled vocabulary check
            if allowed_vals:
                for val in allowed_vals:
                    val_str = str(val)
                    if re.search(r'\b' + re.escape(val_str) + r'\b', sec_text, re.IGNORECASE):
                        evidence = EvidenceItem(
                            paper_id=paper.id,
                            section_id=sec.id,
                            pdf_page=sec.pages.pdf_start,
                            supporting_text=sec_text[:200]
                        )
                        return Observation(
                            paper_id=paper.id,
                            property_id=prop.id,
                            property_version=prop.version,
                            value=val,
                            status=ObservationStatus.EXTRACTED,
                            evidence=[evidence],
                            method="controlled_vocabulary_match",
                            confidence=0.9,
                            run_id=self.run_id
                        )

            # Keyword occurrence check
            for term in text_terms:
                if term in sec_text.lower():
                    evidence = EvidenceItem(
                        paper_id=paper.id,
                        section_id=sec.id,
                        pdf_page=sec.pages.pdf_start,
                        supporting_text=sec_text[:200]
                    )
                    return Observation(
                        paper_id=paper.id,
                        property_id=prop.id,
                        property_version=prop.version,
                        value=term,
                        status=ObservationStatus.EXTRACTED,
                        evidence=[evidence],
                        method="keyword_regex_match",
                        confidence=0.8,
                        run_id=self.run_id
                    )

        return None

    def _extract_prompted(
        self, paper: Paper, prop: PropertyDefinition, sections: List[Section]
    ) -> Optional[Observation]:
        # Simple simulated / fallback prompted analysis based on targeted section text
        passage = ""
        sec_id = None
        pdf_page = None
        if sections:
            sec = sections[0]
            passage = sec.text[:300]
            sec_id = sec.id
            pdf_page = sec.pages.pdf_start

        if passage:
            evidence = EvidenceItem(
                paper_id=paper.id,
                section_id=sec_id,
                pdf_page=pdf_page,
                supporting_text=passage
            )
            return Observation(
                paper_id=paper.id,
                property_id=prop.id,
                property_version=prop.version,
                value=f"Inferred: {prop.label} from passage context",
                status=ObservationStatus.INFERRED,
                evidence=[evidence],
                method="prompted_analysis",
                confidence=0.7,
                run_id=self.run_id
            )
        return None
