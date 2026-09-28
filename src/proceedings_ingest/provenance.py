"""
Provenance and Source Sigil Utilities for ISLS Repository

Provides deterministic mappings between semantic source types and epistemic
source sigils, formatting headers, and formatting trailing inline tags without brackets.
"""

from typing import Union, List, Sequence
from enum import Enum


class SourceType(str, Enum):
    DATABASE = "database"
    DERIVED_METRIC = "derived_metric"
    VERBATIM_EXTRACT = "verbatim_extract"
    AGENT_SYNTHESIS = "agent_synthesis"


SIGIL_MAP = {
    SourceType.DATABASE: "◈",
    SourceType.DERIVED_METRIC: "◇",
    SourceType.VERBATIM_EXTRACT: "⌕",
    SourceType.AGENT_SYNTHESIS: "✦",
}

SIGIL_DESCRIPTIONS = {
    "◈": "Database Record (proceedings.db)",
    "◇": "Database-Derived Metric",
    "⌕": "Verbatim Section Evidence",
    "✦": "Agent-Synthesized Coding",
}


def get_sigil(source_type: Union[SourceType, str]) -> str:
    """Return the single-character sigil for a given semantic source type."""
    if isinstance(source_type, str):
        try:
            source_type = SourceType(source_type.lower())
        except ValueError:
            return ""
    return SIGIL_MAP.get(source_type, "")


def format_source_tag(source_types: Sequence[Union[SourceType, str]]) -> str:
    """
    Format a sequence of source types into a trailing sigil string without brackets.
    Example: ['agent_synthesis', 'verbatim_extract'] -> '✦⌕'
    """
    sigils = []
    for st in source_types:
        s = get_sigil(st)
        if s and s not in sigils:
            sigils.append(s)
    return "".join(sigils)


def format_header(title: str, source_type: Union[SourceType, str]) -> str:
    """
    Format a table column header with its governing source sigil at the end without brackets.
    Example: format_header("Paper Reference", SourceType.DATABASE) -> "Paper Reference ◈"
    """
    sigil = get_sigil(source_type)
    return f"{title} {sigil}".strip() if sigil else title


def format_source_footer() -> str:
    """Return the standard explanatory source footer line."""
    return "Source: ◈ Database Record | ◇ Database-Derived Metric | ⌕ Verbatim Section Evidence | ✦ Agent-Synthesized Coding"
