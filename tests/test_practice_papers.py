import os
import sqlite3
import json
import pytest
from proceedings_ingest.dipstick_engine import DipstickEngine

DB_PATH = "proceedings.db"
REGISTRY_PATH = "data/derived/ground_truth_registry.json"


def test_database_is_practise_paper_column_and_counts():
    assert os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check column exists
    cursor.execute("PRAGMA table_info(papers)")
    cols = [r[1] for r in cursor.fetchall()]
    assert "is_practise_paper" in cols
    assert "paper_type" in cols

    # Check exactly 30 papers flagged
    cursor.execute("SELECT COUNT(*) FROM papers WHERE is_practise_paper = 1")
    count = cursor.fetchone()[0]
    assert count == 30

    # Check counts by year (18 in 2025, 12 in 2026)
    cursor.execute("SELECT year, COUNT(*) FROM papers WHERE is_practise_paper = 1 GROUP BY year ORDER BY year")
    rows = cursor.fetchall()
    assert rows == [(2025, 18), (2026, 12)]

    conn.close()


def test_ground_truth_registry_annotations():
    assert os.path.exists(REGISTRY_PATH)
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    papers = data.get("papers", [])
    practice_papers = [p for p in papers if p.get("is_practise_paper")]
    assert len(practice_papers) == 30

    # Ensure all have valid ids and titles
    for p in practice_papers:
        assert p.get("year") in (2025, 2026)
        assert len(p.get("title", "")) > 10


def test_dipstick_engine_exposes_practise_papers():
    engine = DipstickEngine("data")
    titles = engine.get_titles_index()
    practice_in_index = [p for p in titles if p.get("is_practise_paper")]
    assert len(practice_in_index) == 30
    for p in practice_in_index:
        assert "paper_type" in p
        assert p["is_practise_paper"] is True


def test_reviews_cache_contains_paper_type_column():
    manifest_path = "data/derived/reviews_cache/manifest.json"
    assert os.path.exists(manifest_path)
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Check sample reviews have paper_type column after conference
    for m in manifest:
        if m.get("is_sample") and "selected_columns" in m:
            cols = m["selected_columns"]
            assert "paper_type" in cols
            conf_idx = cols.index("conference")
            paper_type_idx = cols.index("paper_type")
            assert paper_type_idx == conf_idx + 1
