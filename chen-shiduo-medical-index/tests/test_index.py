from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from index_core import build_index, load_index, search  # noqa: E402


class IndexTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index = build_index()

    def test_catalog_has_eight_works(self) -> None:
        self.assertEqual(len(self.index["works"]), 8)
        self.assertEqual(self.index["collection_title"], "陈士铎医学全书")

    def test_headache_returns_verified_reference(self) -> None:
        result = search("头痛", self.index)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["results"][0]["work"], "石室秘录")
        self.assertEqual(result["results"][0]["chapter"], "上治法")
        self.assertIn("神经内科", result["navigation"][0]["departments"])

    def test_alias_for_insomnia(self) -> None:
        result = search("最近失眠", self.index)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["results"][0]["topic"], "怔忡不寐")

    def test_emergency_overrides_literature_search(self) -> None:
        result = search("头痛并突然言语不清", self.index)
        self.assertEqual(result["status"], "emergency")
        self.assertIn("120", result["message"])
        self.assertEqual(result["results"], [])

    def test_unknown_query_fails_closed(self) -> None:
        result = search("不存在的测试词xyz", self.index)
        self.assertEqual(result["status"], "no_match")
        self.assertEqual(result["navigation"], [])

    def test_empty_query_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            search("  ", self.index)

    def test_long_query_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            search("痛" * 101, self.index)

    def test_no_treatment_fields_in_source_entries(self) -> None:
        forbidden = {"prescription", "formula", "dosage", "treatment_advice"}
        for entry in self.index["entries"]:
            self.assertFalse(forbidden.intersection(entry))

    def test_static_index_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "index.json"
            path.write_text(
                json.dumps(self.index, ensure_ascii=False), encoding="utf-8"
            )
            loaded = load_index(path)
            self.assertEqual(search("头痛", loaded)["status"], "ok")

    def test_book_title_can_locate_sample_entries(self) -> None:
        result = search("辨证录", self.index)
        self.assertEqual(result["status"], "ok")
        self.assertTrue(all(item["work"] == "辨证录" for item in result["results"]))


if __name__ == "__main__":
    unittest.main()
