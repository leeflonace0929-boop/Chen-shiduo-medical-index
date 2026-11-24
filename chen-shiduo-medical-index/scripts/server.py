#!/usr/bin/env python3
"""Local demonstration API. Deploy behind hospital-approved infrastructure."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from index_core import load_index, search

INDEX = load_index()


class NavigationHandler(BaseHTTPRequestHandler):
    server_version = "ChenShiduoIndex/0.1"

    def send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self.send_json(200, {"status": "ok", "entry_count": INDEX["entry_count"]})
            return
        if parsed.path != "/v1/navigation/search":
            self.send_json(404, {"error": "not_found"})
            return

        query = parse_qs(parsed.query).get("q", [""])[0]
        try:
            result = search(query, INDEX)
        except ValueError as exc:
            self.send_json(400, {"error": "invalid_query", "message": str(exc)})
            return
        self.send_json(200, result)

    def log_message(self, format_string: str, *args: object) -> None:
        # Avoid writing symptom queries to default access logs.
        print(f"{self.address_string()} requested {self.command} endpoint")


def main() -> None:
    parser = argparse.ArgumentParser(description="启动本地文献导航演示接口")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), NavigationHandler)
    print(f"演示接口：http://{args.host}:{args.port}/v1/navigation/search?q=头痛")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
