import pytest
from proceedings_ingest.verified_chunker import VerifiedMDChunker, clean_title_for_matching

def test_clean_title_for_matching():
    t = "Resolving Expert Disagreement by Evaluating Misrepresentations: A Case Study!"
    assert clean_title_for_matching(t) == "resolving expert disagreement by evaluating misrepresentations a case study"

def test_find_paper_title_in_mds():
    chunker = VerifiedMDChunker()
    year_mds = {
        "isls-2024.md": """# Table of Contents
## Section 1
# Resolving Expert Disagreement by Evaluating Misrepresentations
Author: Clark Chinn
Abstract text here...
# Next Paper Title Here
Author: Jane Smith
"""
    }

    fname, idx, conf = chunker.find_paper_title_in_mds(year_mds, "Resolving Expert Disagreement by Evaluating Misrepresentations")
    assert fname == "isls-2024.md"
    assert idx == 2
    assert conf >= 0.90

def test_chunk_paper_from_gt():
    chunker = VerifiedMDChunker()
    gt_paper = {
        "id": "handle_1_11207",
        "handle": "1/11207",
        "handle_url": "https://repository.isls.org/handle/1/11207",
        "title": "Resolving Expert Disagreement by Evaluating Misrepresentations",
        "authors": ["Chinn, Clark A."],
        "year": 2024,
        "conference": "ISLS Annual Meeting 2024",
        "start_page": 2515,
        "end_page": 2516,
    }
    
    year_mds = {
        "isls-2024.md": """# Resolving Expert Disagreement by Evaluating Misrepresentations
Chinn, Clark A.

## Abstract
This study investigates expert disagreement...

## Methods & Context
We conducted an empirical evaluation with Grade 8 students.

## Results
Findings demonstrate significant resolution of misrepresentations.
"""
    }

    paper = chunker.chunk_paper_from_gt(gt_paper, year_mds)
    assert paper.id == "handle_1_11207"
    assert paper.title == "Resolving Expert Disagreement by Evaluating Misrepresentations"
    assert len(paper.sections) == 3
    assert paper.sections[0].heading_normalized == "introduction"
    assert paper.sections[1].heading_normalized == "methods"
    assert paper.sections[2].heading_normalized == "results"
