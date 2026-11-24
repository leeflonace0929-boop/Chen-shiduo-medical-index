#!/usr/bin/env python3
"""Deterministic keyword index for Chen Shiduo literature navigation."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DEFAULT_INDEX = ROOT / "dist" / "index.json"
DISCLAIMER = (
    "本结果仅用于古籍文献定位与就医导航，不构成诊断、治疗或用药建议。"
    "古籍病名不等同于现代疾病，请以医疗机构专业人员的判断为准。"
)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    return re.sub(r"[\W_]+", "", text, flags=re.UNICODE)


def build_index(data_dir: Path = DATA_DIR) -> dict[str, Any]:
    works_data = load_json(data_dir / "works.json")
    entries_data = load_json(data_dir / "entries.json")
    navigation = load_json(data_dir / "navigation.json")
    emergency = load_json(data_dir / "emergency.json")
    works = {item["id"]: item for item in works_data["works"]}
    entries = entries_data["entries"]
    entry_ids = [item["id"] for item in entries]

    if len(entry_ids) != len(set(entry_ids)):
        raise ValueError("entries.json 中存在重复 id")
    if len(works) != 8:
        raise ValueError("works.json 应包含陈士铎医学全书收录的八部著作")

    forbidden_fields = {"prescription", "formula", "dosage", "treatment_advice"}
    keyword_index: dict[str, list[dict[str, Any]]] = {}

    for entry in entries:
        if forbidden_fields.intersection(entry):
            raise ValueError(f"{entry['id']} 含有不允许的诊疗建议字段")
        if entry["work_id"] not in works:
            raise ValueError(f"{entry['id']} 引用了未知 work_id")
        if not entry.get("source_url") or not entry.get("verification"):
            raise ValueError(f"{entry['id']} 缺少来源或核对状态")
        for navigation_id in entry["navigation_ids"]:
            if navigation_id not in navigation["rules"]:
                raise ValueError(f"{entry['id']} 引用了未知 navigation_id")

        index_terms = set(entry["keywords"])
        index_terms.update(
            [entry["topic"], entry["chapter"], works[entry["work_id"]]["title"]]
        )
        for term in index_terms:
            normalized = normalize(term)
            if not normalized:
                continue
            keyword_index.setdefault(normalized, []).append(
                {"entry_id": entry["id"], "term": term}
            )

    return {
        "schema_version": "1.0",
        "collection_title": works_data["collection_title"],
        "content_type": entries_data["content_type"],
        "works": works_data["works"],
        "entries": entries,
        "keyword_index": keyword_index,
        "navigation": navigation,
        "emergency": emergency,
        "disclaimer": DISCLAIMER,
        "entry_count": len(entries),
    }


def load_index(index_path: Path | None = None) -> dict[str, Any]:
    path = index_path or DEFAULT_INDEX
    if path.exists():
        return load_json(path)
    return build_index()


def detect_emergency(query: str, emergency: dict[str, Any]) -> list[dict[str, str]]:
    normalized_query = normalize(query)
    matches = []
    for rule in emergency["rules"]:
        for keyword in rule["keywords"]:
            if normalize(keyword) in normalized_query:
                matches.append({"rule_id": rule["id"], "matched_keyword": keyword})
                break
    return matches


def search(
    query: str,
    index: dict[str, Any] | None = None,
    limit: int = 5,
) -> dict[str, Any]:
    if not query or not query.strip():
        raise ValueError("查询内容不能为空")
    if len(query) > 100:
        raise ValueError("查询内容不能超过100个字符")
    if not 1 <= limit <= 20:
        raise ValueError("limit 必须在1到20之间")

    index = index or load_index()
    normalized_query = normalize(query)
    emergency_matches = detect_emergency(query, index["emergency"])
    if emergency_matches:
        return {
            "status": "emergency",
            "query": query,
            "message": index["emergency"]["message"],
            "emergency_matches": emergency_matches,
            "results": [],
            "navigation": [],
            "disclaimer": index["disclaimer"],
        }

    scored: dict[str, dict[str, Any]] = {}
    for normalized_term, references in index["keyword_index"].items():
        if normalized_term not in normalized_query:
            continue
        for reference in references:
            entry_id = reference["entry_id"]
            score = 2 + min(len(normalized_term), 12)
            if entry_id not in scored:
                scored[entry_id] = {"score": 0, "matched_terms": []}
            scored[entry_id]["score"] += score
            if reference["term"] not in scored[entry_id]["matched_terms"]:
                scored[entry_id]["matched_terms"].append(reference["term"])

    entries_by_id = {entry["id"]: entry for entry in index["entries"]}
    works_by_id = {work["id"]: work for work in index["works"]}
    ordered = sorted(
        scored.items(), key=lambda item: (-item[1]["score"], item[0])
    )[:limit]
    results = []
    navigation_map: dict[str, dict[str, Any]] = {}

    for entry_id, match in ordered:
        entry = entries_by_id[entry_id]
        work = works_by_id[entry["work_id"]]
        results.append(
            {
                "entry_id": entry_id,
                "reference": f"《{work['title']}》{entry['juan']}·{entry['chapter']}·{entry['topic']}",
                "work": work["title"],
                "juan": entry["juan"],
                "chapter": entry["chapter"],
                "topic": entry["topic"],
                "source_url": entry["source_url"],
                "verification": entry["verification"],
                "matched_terms": match["matched_terms"],
                "score": match["score"],
            }
        )
        for navigation_id in entry["navigation_ids"]:
            navigation_map[navigation_id] = index["navigation"]["rules"][navigation_id]

    if not results:
        return {
            "status": "no_match",
            "query": query,
            "message": "未找到已核对的索引。请更换症状关键词，或咨询医院预检分诊人员。",
            "results": [],
            "navigation": [],
            "disclaimer": index["disclaimer"],
        }

    navigation = [
        {"navigation_id": navigation_id, **rule}
        for navigation_id, rule in navigation_map.items()
    ]
    return {
        "status": "ok",
        "query": query,
        "message": "以下是文献出处与通用就医导航，不是疾病判断。",
        "results": results,
        "navigation": navigation,
        "disclaimer": index["disclaimer"],
    }
