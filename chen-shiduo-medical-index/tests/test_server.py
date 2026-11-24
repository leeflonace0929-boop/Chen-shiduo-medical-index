from __future__ import annotations

import json
import sys
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from server import NavigationHandler  # noqa: E402


class ServerTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), NavigationHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def get_json(self, path: str) -> dict:
        with urlopen(self.base_url + path, timeout=2) as response:
            self.assertEqual(response.headers.get("Cache-Control"), "no-store")
            return json.loads(response.read().decode("utf-8"))

    def test_health(self) -> None:
        result = self.get_json("/health")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["entry_count"], 14)

    def test_search_endpoint(self) -> None:
        result = self.get_json("/v1/navigation/search?" + urlencode({"q": "头痛"}))
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["results"][0]["chapter"], "上治法")

    def test_empty_query_returns_400(self) -> None:
        with self.assertRaises(HTTPError) as context:
            self.get_json("/v1/navigation/search")
        self.assertEqual(context.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
