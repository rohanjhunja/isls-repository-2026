import pytest
from proceedings_ingest.parser import normalize_section_heading, extract_sections_from_markdown

def test_normalize_section_heading():
    assert normalize_section_heading("3. Methodological Approach") == "methods"
    assert normalize_section_heading("Study Design and Data Collection") == "methods"
    assert normalize_section_heading("4. Results and Findings") == "results"
    assert normalize_section_heading("5. Concluding Remarks") == "discussion_conclusion"
    assert normalize_section_heading("Theoretical Framework") == "theoretical_background"
    assert normalize_section_heading("References") == "references"
    assert normalize_section_heading("Custom Acknowledgments Header") == "other"

def test_extract_sections_from_markdown():
    md = """# Introduction
This is the intro text.

## 2. Theoretical Framework
We draw on socio-cultural theory.

## 3. Methods & Context
Eighty-four students participated.

## 4. Findings
We observed significant gains.

## 5. Discussion
Results suggest high engagement.

# References
Smith, J. (2024). Learning in Context.
"""
    sections = extract_sections_from_markdown(md)
    assert len(sections) == 6
    assert sections[0][1] == "introduction"
    assert sections[1][1] == "theoretical_background"
    assert sections[2][1] == "methods"
    assert sections[3][1] == "results"
    assert sections[4][1] == "discussion_conclusion"
    assert sections[5][1] == "references"
