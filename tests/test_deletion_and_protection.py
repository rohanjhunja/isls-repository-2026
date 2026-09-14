import os
import json
import pytest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from proceedings_ingest.review_service import ReviewService, STANDARD_PROPERTIES


def test_standard_properties_protection(tmp_path):
    data_dir = str(tmp_path)
    service = ReviewService(data_dir)

    review_id = "test_rev_001"
    rev_json_path = os.path.join(service.reviews_dir, f"{review_id}.json")

    test_data = {
        "id": review_id,
        "name": "Test Protection Review",
        "selected_columns": ["title", "authors", "year", "custom_property_1"],
        "visible_columns": ["title", "authors", "year", "custom_property_1"],
        "paper_ids": ["paper-001", "paper-002"],
        "papers": [{"id": "paper-001", "title": "P1"}, {"id": "paper-002", "title": "P2"}]
    }

    with open(rev_json_path, "w", encoding="utf-8") as f:
        json.dump(test_data, f)

    # 1. Verify standard properties CANNOT be deleted
    for std_prop in ["title", "authors", "year", "abstract"]:
        with pytest.raises(ValueError, match="cannot be deleted"):
            service.delete_column_from_review(review_id, std_prop)

    # 2. Verify custom property CAN be deleted
    success = service.delete_column_from_review(review_id, "custom_property_1")
    assert success is True

    with open(rev_json_path, "r", encoding="utf-8") as f:
        updated = json.load(f)

    assert "custom_property_1" not in updated["selected_columns"]
    assert "custom_property_1" not in updated["visible_columns"]
    assert "title" in updated["selected_columns"]

    # 3. Verify paper row deletion
    p_success = service.delete_paper_from_review(review_id, "paper-001")
    assert p_success is True

    with open(rev_json_path, "r", encoding="utf-8") as f:
        updated = json.load(f)

    assert "paper-001" not in updated["paper_ids"]
    assert len(updated["papers"]) == 1
    assert updated["papers"][0]["id"] == "paper-002"

    # 4. Verify review deletion
    r_success = service.delete_review(review_id)
    assert r_success is True
    assert not os.path.exists(rev_json_path)


if __name__ == "__main__":
    pytest.main([__file__])
