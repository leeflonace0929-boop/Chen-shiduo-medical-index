#!/usr/bin/env python3
"""Search the literature index and return machine-readable JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from index_core import load_index, search


def main() -> None:
    parser = argparse.ArgumentParser(description="检索陈士铎医学文献索引")
    parser.add_argument("query", help="症状、篇名或论题词，例如：头痛")
    parser.add_argument("--index", type=Path, help="可选的静态索引路径")
    parser.add_argument("--limit", type=int, default=5, help="返回条数，默认5")
    args = parser.parse_args()

    index = load_index(args.index) if args.index else None
    result = search(args.query, index=index, limit=args.limit)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
