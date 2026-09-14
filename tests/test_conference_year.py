import os
import json
import sqlite3
import unittest
from proceedings_ingest.utils.update_paper_conference_year import parse_conference_and_year
from proceedings_ingest.review_service import ReviewService


class TestConferenceYearUpdate(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cls.data_dir = os.path.join(cls.base_dir, "data")
        cls.derived_dir = os.path.join(cls.data_dir, "derived")
        cls.db_path = os.path.join(cls.data_dir, "index", "proceedings.db")

    def test_parse_conference_and_year(self):
        conf_cscl, year_2024 = parse_conference_and_year("cscl-2024-proceedings.pdf")
        self.assertEqual(conf_cscl["acronym"], "CSCL")
        self.assertEqual(year_2024, 2024)

        conf_icls, year_2025 = parse_conference_and_year("icls-2025-proceedings.pdf")
        self.assertEqual(conf_icls["acronym"], "ICLS")
        self.assertEqual(year_2025, 2025)

        conf_isls, year_2026 = parse_conference_and_year("isls-2026-proceedings.pdf")
        self.assertEqual(conf_isls["acronym"], "ISLS")
        self.assertEqual(year_2026, 2026)

    def test_all_derived_papers_have_valid_conference_and_year(self):
        volumes = [d for d in os.listdir(self.derived_dir) if os.path.isdir(os.path.join(self.derived_dir, d)) and d not in ('reviews_cache', 'legacy_backup')]
        self.assertEqual(len(volumes), 12)

        total_papers = 0
        for vol_id in volumes:
            vol_json_path = os.path.join(self.derived_dir, vol_id, f"{vol_id}.json")
            self.assertTrue(os.path.exists(vol_json_path), f"Missing JSON for {vol_id}")

            with open(vol_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            coll_conf = data.get("conference")
            self.assertIsNotNone(coll_conf, f"Collection conference is None for {vol_id}")
            self.assertIn("acronym", coll_conf)
            self.assertIn("year", coll_conf)

            papers = data.get("papers", [])
            self.assertGreater(len(papers), 0, f"No papers found in {vol_id}")

            for p in papers:
                p_conf = p.get("conference")
                p_year = p.get("year")
                self.assertIsNotNone(p_conf, f"Paper {p.get('id')} has null conference")
                self.assertEqual(p_conf["year"], p_year)
                self.assertIn(p_conf["acronym"], ["CSCL", "ICLS", "ISLS"])
                total_papers += 1

        self.assertEqual(total_papers, 2791)

    def test_sqlite_db_indexing(self):
        self.assertTrue(os.path.exists(self.db_path))
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM papers")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 2791)

        # Check sample paper JSON from DB
        cursor.execute("SELECT data_json FROM papers LIMIT 1")
        sample_json_str = cursor.fetchone()[0]
        sample_paper = json.loads(sample_json_str)

        self.assertIsNotNone(sample_paper.get("conference"))
        self.assertIn(sample_paper.get("conference", {}).get("acronym"), ["CSCL", "ICLS", "ISLS"])
        conn.close()

    def test_review_service_conference_field(self):
        from proceedings_ingest.review_models import PaperScope
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM papers LIMIT 5")
        pids = [row[0] for row in cursor.fetchall()]
        conn.close()

        service = ReviewService(self.data_dir)
        review = service.create_review(name="Test Conference Review", scope=PaperScope(explicit_paper_ids=pids))
        table = service.build_review_table(review.id)
        self.assertGreater(len(table), 0)
        self.assertIn("year", table[0])


if __name__ == "__main__":
    unittest.main()
