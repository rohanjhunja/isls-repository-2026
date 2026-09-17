import os
import json
import pytest
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from proceedings_ingest.dipstick_engine import DipstickEngine
from proceedings_ingest.review_service import ReviewService
from proceedings_ingest.review_models import PaperScope


def test_dipstick_engine_review_naming(tmp_path):
    data_dir = str(tmp_path)
    engine = DipstickEngine(data_dir)

    # 1. Default naming with keywords
    m1 = engine.save_dipstick_review(name="", keywords=["collaboration", "AI"], paper_ids=["p1"])
    assert m1["name"] == "Dipstick Review - collaboration, AI"
    assert m1["review_protocol"] == "Dipstick Review"

    # 2. Expanded Scope protocol
    m2 = engine.save_dipstick_review(
        name="", keywords=["feedback"], paper_ids=["p1"], protocol="Expanded Scope"
    )
    assert m2["name"] == "Expanded Scope - feedback"
    assert m2["review_protocol"] == "Expanded Scope"

    # 3. User raw name gets auto-prefixed with protocol
    m3 = engine.save_dipstick_review(
        name="machine learning", keywords=["ml"], paper_ids=["p1"], protocol="Expanded Scope"
    )
    assert m3["name"] == "Expanded Scope - machine learning"
    assert m3["review_protocol"] == "Expanded Scope"

    # 4. Explicit protocol prefix in name aligns review_protocol
    m4 = engine.save_dipstick_review(
        name="Agentic Review - qualitative coding", keywords=["coding"], paper_ids=["p1"]
    )
    assert m4["name"] == "Agentic Review - qualitative coding"
    assert m4["review_protocol"] == "Agentic Review"


def test_review_service_naming(tmp_path):
    data_dir = str(tmp_path)
    service = ReviewService(data_dir)

    # 1. Title/abstract default scope
    r1 = service.create_review(scope=PaperScope(keywords=["stem", "robotics"]))
    assert r1.name == "Dipstick Review - stem, robotics"

    # 2. Sections search scope defaults to Expanded Scope
    r2 = service.create_review(scope=PaperScope(keywords=["scaffolding"], search_fields=["sections"]))
    assert r2.name == "Expanded Scope - scaffolding"

    # 3. Explicit Agentic Review
    r3 = service.create_review(name="Agentic Review - multimodal interaction", scope=PaperScope(keywords=["multimodal"]))
    assert r3.name == "Agentic Review - multimodal interaction"
