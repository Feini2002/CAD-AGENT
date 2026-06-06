"""Small local RAG pack for CAD asset intelligence.

This module is intentionally lexical and repository-local. It prepares cited
context for downstream agents; it does not call a model, embed text, access the
network, or prove CAD geometry.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from core.assets.semantic_rules import match_semantic_rules
from core.runtime.encoding_guard import detect_text_encoding_corruption


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SYSTEM_LIBRARY_REL = Path("libraries/system_library")
TRAINING_MEMORY_GLOB = "agents/**/training_memory.json"
PROJECT_FAILURE_GLOB = "projects/*/runs/*failure*.json"
PROJECT_LEARNING_GLOB = "projects/*/runs/*learning_promotion.json"
TRAINING_ERRORS_REL = Path("docs/training/training-errors.md")
LEGACY_TRAINING_ERRORS_REL = Path("TRAINING_ERRORS.md")

ALLOWED_SOURCE_KINDS = ["system_asset", "semantic_rule", "training_memory", "failure_sample"]
EXCLUDED_SOURCE_KINDS = ["reference_asset", "external_web", "raw_download", "unreviewed_reference"]


def _relative(path: Path, root: Path) -> str:
    try:
        rel_path = path.relative_to(root)
    except ValueError:
        rel_path = path
    return str(rel_path).replace("\\", "/")


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _compact_text(value: Any) -> str:
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, list):
        return " ".join(_compact_text(item) for item in value)
    if isinstance(value, dict):
        return " ".join(_compact_text(item) for item in value.values())
    return str(value).lower()


def _unique(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def _query_terms(query: str) -> list[str]:
    text = query.lower()
    terms: list[str] = []
    terms.extend(token for token in re.split(r"[^0-9a-zA-Z_\u4e00-\u9fff]+", text) if len(token) >= 2)
    for chunk in re.findall(r"[\u4e00-\u9fff]{2,}", text):
        max_n = min(4, len(chunk))
        for size in range(2, max_n + 1):
            terms.extend(chunk[index : index + size] for index in range(0, len(chunk) - size + 1))
    return _unique(terms)


def _matched_terms(query_terms: list[str], text: str) -> list[str]:
    lowered = text.lower()
    return [term for term in query_terms if term in lowered]


def _snippet(text: str, hits: list[str], *, max_len: int = 180) -> str:
    clean = re.sub(r"\s+", " ", text).strip()
    if not clean:
        return ""
    first_hit = next((clean.lower().find(hit.lower()) for hit in hits if hit.lower() in clean.lower()), -1)
    if first_hit < 0:
        return clean[:max_len]
    start = max(0, first_hit - 40)
    end = min(len(clean), start + max_len)
    return clean[start:end]


def _source_item(
    *,
    source_kind: str,
    source: str,
    title: str,
    text: str,
    matched_terms: list[str],
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "sourceKind": source_kind,
        "source": source,
        "title": title,
        "score": len(matched_terms),
        "matchedTerms": matched_terms[:10],
        "snippet": _snippet(text, matched_terms),
        "payload": payload or {},
    }


def _iter_system_asset_entries(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    library_root = root / SYSTEM_LIBRARY_REL
    if not library_root.exists():
        return []

    entries: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(library_root.rglob("*.json")):
        data = _read_json(path)
        if not data:
            continue
        assets = data.get("assets")
        if isinstance(assets, list):
            entries.extend((path, asset) for asset in assets if isinstance(asset, dict))
        elif data.get("assetId") or data.get("id"):
            entries.append((path, data))
    return entries


def _system_asset_items(root: Path, query_terms: list[str], limit: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    entries = _iter_system_asset_entries(root)
    encoding = detect_text_encoding_corruption([asset for _, asset in entries])
    if encoding.get("status") != "pass":
        return [], {**encoding, "scope": "small_rag_system_asset_text", "assetCount": len(entries)}

    items: list[dict[str, Any]] = []
    for path, asset in entries:
        text = _compact_text(
            {
                "assetId": asset.get("assetId") or asset.get("id"),
                "name": asset.get("name"),
                "category": asset.get("category"),
                "aliases": asset.get("aliases"),
                "tags": asset.get("tags"),
                "useWhen": asset.get("useWhen"),
                "assetKind": asset.get("assetKind"),
                "retrieval": asset.get("retrieval"),
                "verificationStatus": asset.get("verificationStatus") or asset.get("status"),
            }
        )
        hits = _matched_terms(query_terms, text)
        if not hits:
            continue
        asset_id = str(asset.get("assetId") or asset.get("id") or path.stem)
        items.append(
            _source_item(
                source_kind="system_asset",
                source=_relative(path, root),
                title=asset_id,
                text=text,
                matched_terms=hits,
                payload={
                    "assetId": asset_id,
                    "category": asset.get("category", ""),
                    "assetKind": asset.get("assetKind", ""),
                    "verificationStatus": asset.get("verificationStatus") or asset.get("status", ""),
                },
            )
        )
    return _top_items(items, limit), {**encoding, "scope": "small_rag_system_asset_text", "assetCount": len(entries)}


def _semantic_rule_items(query: str, limit: int) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for rule in match_semantic_rules(query):
        text = _compact_text(rule)
        matched = [str(term) for term in rule.get("matchedTerms", [])]
        items.append(
            _source_item(
                source_kind="semantic_rule",
                source="core/assets/semantic_rules.py",
                title=str(rule.get("ruleId", "")),
                text=text,
                matched_terms=matched,
                payload={
                    "ruleId": rule.get("ruleId", ""),
                    "routes": rule.get("routes", []),
                    "requiredGuards": rule.get("requiredGuards", []),
                    "forbiddenBehaviors": rule.get("forbiddenBehaviors", []),
                },
            )
        )
    return _top_items(items, limit)


def _training_memory_items(root: Path, query_terms: list[str], limit: int) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for path in sorted(root.glob(TRAINING_MEMORY_GLOB)):
        data = _read_json(path)
        if not data:
            continue
        agent_id = str(data.get("agentId") or path.parent.name)
        lessons = data.get("lessons")
        if not isinstance(lessons, list):
            continue
        for lesson in lessons:
            if not isinstance(lesson, dict):
                continue
            text = _compact_text(
                {
                    "capabilityId": lesson.get("capabilityId"),
                    "title": lesson.get("title"),
                    "summary": lesson.get("summary"),
                    "promptGuidance": lesson.get("promptGuidance"),
                    "evidence": lesson.get("evidence"),
                }
            )
            hits = _matched_terms(query_terms, text)
            if not hits:
                continue
            title = str(lesson.get("capabilityId") or lesson.get("title") or agent_id)
            items.append(
                _source_item(
                    source_kind="training_memory",
                    source=_relative(path, root),
                    title=title,
                    text=text,
                    matched_terms=hits,
                    payload={"agentId": agent_id, "capabilityId": lesson.get("capabilityId", "")},
                )
            )
    return _top_items(items, limit)


def _failure_json_items(root: Path, query_terms: list[str], limit: int) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    paths = [*root.glob(PROJECT_FAILURE_GLOB), *root.glob(PROJECT_LEARNING_GLOB)]
    for path in sorted(set(paths)):
        data = _read_json(path)
        if not data:
            continue
        text = _compact_text(data)
        hits = _matched_terms(query_terms, text)
        if not hits:
            continue
        title = str(data.get("case_id") or data.get("caseId") or path.stem)
        items.append(
            _source_item(
                source_kind="failure_sample",
                source=_relative(path, root),
                title=title,
                text=text,
                matched_terms=hits,
                payload={"verdict": data.get("verdict", ""), "round": data.get("round", "")},
            )
        )
    return _top_items(items, limit)


def _failure_markdown_items(root: Path, query_terms: list[str], limit: int) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for path in [root / TRAINING_ERRORS_REL, root / LEGACY_TRAINING_ERRORS_REL]:
        if not path.is_file():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            text = line.strip()
            if not text:
                continue
            hits = _matched_terms(query_terms, text.lower())
            if not hits:
                continue
            items.append(
                _source_item(
                    source_kind="failure_sample",
                    source=f"{_relative(path, root)}:{line_number}",
                    title=path.name,
                    text=text,
                    matched_terms=hits,
                    payload={"line": line_number},
                )
            )
    return _top_items(items, limit)


def _top_items(items: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    return sorted(items, key=lambda item: (-int(item.get("score", 0)), str(item.get("source", ""))))[:limit]


def build_local_asset_rag_pack(
    query: str,
    *,
    project_root: Path = PROJECT_ROOT,
    max_items_per_kind: int = 5,
) -> dict[str, Any]:
    """Build a small cited context pack from approved local sources only."""

    root = Path(project_root)
    query_terms = _query_terms(query)
    system_items, encoding = _system_asset_items(root, query_terms, max_items_per_kind)
    semantic_items = _semantic_rule_items(query, max_items_per_kind)
    training_items = _training_memory_items(root, query_terms, max_items_per_kind)
    failure_items = _top_items(
        [
            *_failure_json_items(root, query_terms, max_items_per_kind),
            *_failure_markdown_items(root, query_terms, max_items_per_kind),
        ],
        max_items_per_kind,
    )

    items = _top_items([*system_items, *semantic_items, *training_items, *failure_items], max_items_per_kind * 4)
    source_summary = {
        "system_asset": len(system_items),
        "semantic_rule": len(semantic_items),
        "training_memory": len(training_items),
        "failure_sample": len(failure_items),
        "reference_asset": 0,
    }

    return {
        "schemaVersion": 1,
        "kind": "local_asset_small_rag_pack",
        "status": "ready" if items else "no_matches",
        "retrievalId": f"local-rag.{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "retrievalMode": "local_lexical_small_rag",
        "query": query,
        "sourcePolicy": {
            "allowedSourceKinds": ALLOWED_SOURCE_KINDS,
            "excludedSourceKinds": EXCLUDED_SOURCE_KINDS,
            "networkAccess": "forbidden",
            "embeddingIndex": "not_used",
        },
        "scannedSources": [
            "system_asset_registry",
            "system_asset_registry:libraries/system_library/**/*.json",
            "semantic_rules",
            "semantic_rules:core/assets/semantic_rules.py",
            "training_memory",
            "training_memory:agents/**/training_memory.json",
            "failure_samples",
            "failure_samples:projects/*/runs/*failure*.json",
            "failure_samples:projects/*/runs/*learning_promotion.json",
            "failure_samples:docs/training/training-errors.md",
        ],
        "sourceSummary": source_summary,
        "encodingPreflight": encoding,
        "items": items,
        "evidenceBoundary": {
            "checked": [
                "local_system_asset_json_lookup",
                "local_semantic_rule_lookup",
                "local_training_memory_lookup",
                "local_failure_sample_lookup",
            ],
            "notChecked": [
                "real_cad_geometry",
                "created_handles_readback",
                "user_visual_acceptance",
                "external_asset_license_for_production_use",
                "model_reasoning_quality",
            ],
            "assumptions": [
                "lexical_matching_only",
                "no_embedding_rag",
                "no_network_search",
                "local_rag_pack_is_upstream_context_not_capability_proof",
            ],
        },
    }


def write_local_asset_rag_pack(pack: dict[str, Any], output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path
