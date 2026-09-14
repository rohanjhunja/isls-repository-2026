import pytest
from proceedings_ingest.dspace_harvester import DSpaceHarvester, parse_page_range, parse_paper_type

def test_parse_page_range():
    citation = "Chinn, C. A. (2024). Resolving Expert Disagreement. In Proceedings of ICLS 2024 (pp. 2515-2516)."
    start, end = parse_page_range(citation, "ICLS2024_2515-2516.pdf")
    assert start == 2515
    assert end == 2516

def test_parse_paper_type():
    ptype = parse_paper_type("Resolving Expert Disagreement", "pp. 2515-2516", 2515, 2516)
    assert ptype == "Poster / Short Note"

    ptype_full = parse_paper_type("Deep Study on Learning", "pp. 100-108", 100, 108)
    assert ptype_full == "Full Paper"

def test_harvest_single_item_metadata():
    harvester = DSpaceHarvester()
    # Test item page handle 1/11207
    paper = harvester.harvest_item_metadata("/handle/1/11207", 2024, "ISLS Annual Meeting 2024")
    assert paper is not None
    assert paper.title == "Resolving Expert Disagreement by Evaluating Misrepresentations"
    assert "Chinn, Clark A." in paper.authors
    assert paper.year == 2024
    assert paper.start_page == 2515
    assert paper.end_page == 2516
    assert paper.doi == "10.22318/icls2024.497890"
    assert paper.pdf_url == "https://repository.isls.org/bitstream/1/11207/1/ICLS2024_2515-2516.pdf"
