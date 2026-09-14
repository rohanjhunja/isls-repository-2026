import unittest
from proceedings_ingest.utils.memory import get_rss_memory_gb, check_memory, force_garbage_collection


class TestMemoryUtils(unittest.TestCase):

    def test_get_rss_memory_gb(self):
        rss = get_rss_memory_gb()
        self.assertIsInstance(rss, float)
        self.assertGreater(rss, 0.0)

    def test_check_memory_within_limit(self):
        rss = check_memory(max_memory_gb=100.0)
        self.assertIsInstance(rss, float)

    def test_check_memory_exceeds_limit(self):
        with self.assertRaises(MemoryError):
            check_memory(max_memory_gb=0.000001)

    def test_force_garbage_collection(self):
        rss = force_garbage_collection()
        self.assertIsInstance(rss, float)


if __name__ == "__main__":
    unittest.main()
