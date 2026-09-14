from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field


class ObservationStatus(str, Enum):
    EXTRACTED = "extracted"
    INFERRED = "inferred"
    NOT_PRESENT = "not_present"
    UNRESOLVED = "unresolved"
    AMBIGUOUS = "ambiguous"
    ERROR = "error"


class PaperScope(BaseModel):
    collections: List[str] = Field(default_factory=list)
    conferences: List[str] = Field(default_factory=list)
    journals: List[str] = Field(default_factory=list)
    years: List[int] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    exclusions: List[str] = Field(default_factory=list)
    review_prompt: Optional[str] = None
    explicit_paper_ids: List[str] = Field(default_factory=list)
    search_fields: List[str] = Field(default_factory=lambda: ["title", "abstract"])  # default scope: title and abstract only
    ai_search_enabled: bool = False  # default: deterministic keyword search unless AI search specified


class SearchDefinition(BaseModel):
    version: str = "1.0.0"
    original_prompt: Optional[str] = None
    original_keywords: List[str] = Field(default_factory=list)
    accepted_expansions: List[str] = Field(default_factory=list)
    exclusions: List[str] = Field(default_factory=list)
    search_fields: List[str] = Field(default_factory=lambda: ["title", "abstract"])
    ai_search_enabled: bool = False
    filters: Dict[str, Any] = Field(default_factory=dict)
    scoring_settings: Dict[str, Any] = Field(default_factory=dict)


class QueryConstraint(BaseModel):
    allowed_values: Optional[List[Any]] = None
    maximum_words: Optional[int] = None
    minimum_words: Optional[int] = None
    output_type: str = "string"  # scalar, list, categorical, boolean, number, date, text, structured


class ExtractionConfig(BaseModel):
    preferred_methods: List[str] = Field(
        default_factory=lambda: [
            "existing_paper_field",
            "existing_observation",
            "labelled_value",
            "regex_or_rule",
            "derived_calculation",
            "prompted_analysis",
        ]
    )
    inference_allowed: bool = True


class QueryDefinition(BaseModel):
    question: str
    candidate_sections: List[str] = Field(default_factory=list)
    heading_terms: List[str] = Field(default_factory=list)
    text_terms: List[str] = Field(default_factory=list)


class PropertyDefinition(BaseModel):
    id: str
    version: str = "1.0.0"
    label: str
    description: str
    value_type: str = "text"
    query: Optional[QueryDefinition] = None
    constraints: Optional[QueryConstraint] = None
    extraction: ExtractionConfig = Field(default_factory=ExtractionConfig)
    evidence_required: bool = True


class EvidenceItem(BaseModel):
    paper_id: str
    section_id: Optional[str] = None
    pdf_page: Optional[int] = None
    supporting_text: str


class Observation(BaseModel):
    paper_id: str
    property_id: str
    property_version: str
    value: Any
    status: ObservationStatus
    evidence: List[EvidenceItem] = Field(default_factory=list)
    method: str
    confidence: float = 1.0
    run_id: str
    source_version: Optional[str] = None


class LiteratureReview(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_at: str
    updated_at: str
    scope: PaperScope = Field(default_factory=PaperScope)
    search_definition: Optional[SearchDefinition] = None
    paper_ids: List[str] = Field(default_factory=list)
    selected_columns: List[str] = Field(default_factory=list)
    property_versions: Dict[str, str] = Field(default_factory=dict)
    visible_columns: List[str] = Field(default_factory=list)
    sort_order: List[Dict[str, str]] = Field(default_factory=list)
    table_filters: Dict[str, Any] = Field(default_factory=dict)
