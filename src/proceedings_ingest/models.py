from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class GroundTruthPaper(BaseModel):
    id: str
    handle: str
    handle_url: str
    title: str
    authors: List[str] = Field(default_factory=list)
    year: int
    conference: str
    doi: Optional[str] = None
    citation: Optional[str] = None
    start_page: Optional[int] = None
    end_page: Optional[int] = None
    paper_type: Optional[str] = None
    abstract: Optional[str] = None
    pdf_url: Optional[str] = None


class GroundTruthRegistry(BaseModel):
    schema_version: str = "1.0.0"
    created_at: str
    total_papers: int
    papers_by_year: Dict[int, int] = Field(default_factory=dict)
    papers: List[GroundTruthPaper] = Field(default_factory=list)


class ConferenceInfo(BaseModel):
    name: str
    acronym: str
    year: int


class SourceInfo(BaseModel):
    filename: str
    sha256: str
    pdf_page_count: int
    markdown_path: str


class Author(BaseModel):
    display_name: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    affiliations: List[str] = Field(default_factory=list)
    email: Optional[str] = None


class PageRange(BaseModel):
    pdf_start: int
    pdf_end: int
    printed_start: Optional[str] = None
    printed_end: Optional[str] = None


class MarkdownRange(BaseModel):
    start_line: int
    end_line: int


class Section(BaseModel):
    id: str
    heading_original: str
    heading_normalized: str
    level: int = 1
    parent_id: Optional[str] = None
    canonical_roles: List[str] = Field(default_factory=list)
    text: str
    pages: PageRange
    markdown_range: Optional[MarkdownRange] = None


class ExtractionMetadata(BaseModel):
    profile_id: str
    profile_version: str
    paper_boundary_confidence: float = 1.0
    field_status: Dict[str, str] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)


class Paper(BaseModel):
    id: str
    title: str
    authors: List[Author] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    abstract: Optional[str] = None
    proceedings_section: Optional[str] = None
    conference: Optional[ConferenceInfo] = None
    journal: Optional[str] = None
    year: int
    filename: str
    pages: PageRange
    canonical_sections: Dict[str, List[str]] = Field(default_factory=dict)
    sections: List[Section] = Field(default_factory=list)
    extraction: ExtractionMetadata


class Collection(BaseModel):
    schema_version: str = "1.0.0"
    id: str
    kind: str = "conference_proceedings"
    title: str
    conference: Optional[ConferenceInfo] = None
    journal: Optional[str] = None
    source: SourceInfo
    papers: List[Paper] = Field(default_factory=list)


class EvidenceItem(BaseModel):
    section_id: str
    pdf_page: int
    text: str


class ExtractorInfo(BaseModel):
    strategy: str
    version: str = "1.0.0"


class Observation(BaseModel):
    paper_id: str
    property_id: str
    property_version: str
    value: Any
    status: str  # extracted, not_present, unresolved, ambiguous, manually_verified
    evidence: List[EvidenceItem] = Field(default_factory=list)
    extractor: ExtractorInfo
    run_id: str


class PropertyDefinition(BaseModel):
    id: str
    version: str = "1.0.0"
    label: str
    description: str
    entity_scope: str = "paper"
    value_schema: Dict[str, Any]
    targeting: Dict[str, Any]
    extraction: Dict[str, Any]
    evidence_required: bool = True


class IngestionReport(BaseModel):
    source_filename: str
    sha256: str
    pdf_page_count: int
    detected_papers_count: int
    expected_toc_count: int
    boundaries_confidence_avg: float
    unmapped_headings_count: int
    missing_fields_summary: Dict[str, int]
    timestamp: str
