import os
import pytest
from proceedings_ingest.database import init_database, get_db_connection, insert_paper_record
from proceedings_ingest.lexical_search import search_lexical_bm25

TEST_DB_PATH = "test_proceedings.db"

@pytest.fixture(autouse=True)
def setup_teardown_db():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    init_database(TEST_DB_PATH)
    yield
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

def test_database_insert_and_bm25_search():
    conn = get_db_connection(TEST_DB_PATH)
    
    paper_1 = {
        "id": "handle_1_11207",
        "handle": "1/11207",
        "handle_url": "https://repository.isls.org/handle/1/11207",
        "doi": "10.22318/icls2024.497890",
        "title": "Resolving Expert Disagreement by Evaluating Misrepresentations",
        "year": 2024,
        "conference": "ISLS Annual Meeting 2024",
        "paper_type": "Poster / Short Note",
        "abstract": "This study investigates expert disagreement in scientific learning.",
        "authors": ["Chinn, Clark A.", "Mochizuki, Toshio"],
    }
    sec_1 = [
        {"original_heading": "Abstract", "normalized_section": "introduction", "text": "This study investigates expert disagreement in scientific learning."},
        {"original_heading": "Methods", "normalized_section": "methods", "text": "Eighty-four students used interactive agent-based simulations to model systems thinking."},
    ]

    paper_2 = {
        "id": "handle_1_10381",
        "handle": "1/10381",
        "title": "Collaborative Knowledge Building in Science Classrooms",
        "year": 2023,
        "conference": "ISLS Annual Meeting 2023",
        "paper_type": "Full Paper",
        "abstract": "We analyze collaborative problem solving and knowledge building.",
        "authors": ["Scardamalia, Marlene", "Bereiter, Carl"],
    }
    sec_2 = [
        {"original_heading": "Abstract", "normalized_section": "introduction", "text": "We analyze collaborative problem solving and knowledge building."},
        {"original_heading": "Study Design", "normalized_section": "methods", "text": "Participants engaged in online Knowledge Forum discussions."},
    ]

    insert_paper_record(conn, paper_1, sec_1)
    insert_paper_record(conn, paper_2, sec_2)
    conn.close()

    # Query 1: BM25 search for "agent-based simulations"
    hits = search_lexical_bm25("agent-based simulations", db_path=TEST_DB_PATH)
    assert len(hits) == 1
    assert hits[0]["paper_id"] == "handle_1_11207"
    assert hits[0]["title"] == "Resolving Expert Disagreement by Evaluating Misrepresentations"

    # Query 2: Filter by section "methods"
    hits_methods = search_lexical_bm25("Knowledge Forum", normalized_section="methods", db_path=TEST_DB_PATH)
    assert len(hits_methods) == 1
    assert hits_methods[0]["paper_id"] == "handle_1_10381"

    # Query 3: Filter by min_year 2024
    hits_year = search_lexical_bm25("learning", min_year=2024, db_path=TEST_DB_PATH)
    assert len(hits_year) == 1
    assert hits_year[0]["year"] == 2024
