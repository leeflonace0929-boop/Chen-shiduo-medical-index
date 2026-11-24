#!/usr/bin/env python3
"""Validate source data and build the distributable static index."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from index_core import DEFAULT_INDEX, build_index


def main() -> None:
    parser = argparse.ArgumentParser(description="构建陈士铎医学文献静态索引")
    parser.add_argument("--output", type=Path, default=DEFAULT_INDEX)
    args = parser.parse_args()

    index = build_index()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(index, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    print(f"已构建 {index['entry_count']} 条索引：{args.output}")


if __name__ == "__main__":
    main()
