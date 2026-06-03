"""Find and reuse system-library CAD assets."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from core.assets.semantic_rules import (
    asset_registry_encoding_preflight as _semantic_asset_registry_encoding_preflight,
    semantic_rule_summary,
)
from core.assets.system_asset_sedimentation import PROJECT_ROOT, REGISTRY_REL


PREVIEW_LAYER = "CODEX_PREVIEW"
IMPLICIT_ASSET_MATCH_SCORE = 5.0
MULTI_ASSET_MATCH_SCORE = 5.0
DEFAULT_MULTI_ASSET_X_OFFSET = 12000.0
EXPLICIT_ASSET_ID_SCORE = 999999.0
REUSE_VERBS = (
    "调用",
    "使用",
    "复用",
    "放到",
    "放入",
    "插入",
    "加入",
    "应用",
    "套用",
    "拿",
    "找",
    "引用",
    "资产",
    "asset",
    "insert",
    "reuse",
    "apply",
)


@dataclass(frozen=True)
class AssetMatch:
    asset: dict[str, Any]
    score: float
    matched_terms: list[str]


def _match_summary(match: AssetMatch | None) -> dict[str, Any]:
    if match is None:
        return {}
    return {
        "assetId": str(match.asset.get("assetId", "")),
        "assetName": str(match.asset.get("name", "")),
        "category": str(match.asset.get("category", "")),
        "score": match.score,
        "matchedTerms": match.matched_terms,
    }


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _norm(text: object) -> str:
    return re.sub(r"\s+", "", str(text or "").lower())


def _tokens(text: object) -> list[str]:
    raw = str(text or "").lower()
    latin = re.findall(r"[a-z0-9_]+", raw)
    cjk = re.findall(r"[\u4e00-\u9fff]{2,}", raw)
    return [*_unique(latin), *_unique(cjk)]


def _unique(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def _flatten_match_text(asset: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for key in ("assetId", "name", "category"):
        if asset.get(key):
            values.append(str(asset[key]))
    for key in ("aliases", "useWhen", "tags"):
        raw = asset.get(key)
        if isinstance(raw, list):
            values.extend(str(item) for item in raw)
    retrieval = asset.get("retrieval")
    if isinstance(retrieval, dict):
        for key in ("aliases", "useWhen", "tags", "scenarioTags", "constraints", "matchText"):
            raw = retrieval.get(key)
            if isinstance(raw, list):
                values.extend(str(item) for item in raw)
    return _unique([value.strip() for value in values if str(value).strip()])


def load_system_assets(project_root: Path = PROJECT_ROOT) -> list[dict[str, Any]]:
    registry = _read_json_object(project_root / REGISTRY_REL)
    assets = registry.get("assets", [])
    return [asset for asset in assets if isinstance(asset, dict)]


def asset_registry_encoding_preflight(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    """Validate searchable registry text before it participates in matching."""

    return _semantic_asset_registry_encoding_preflight(load_system_assets(project_root))


def should_search_system_assets(phrase: str) -> bool:
    text = _norm(phrase)
    if not text:
        return False
    return any(_norm(verb) in text for verb in REUSE_VERBS)


def split_system_asset_reuse_queries(phrase: str) -> list[str]:
    """Split a composite user request into asset-reuse-sized clauses."""
    text = str(phrase or "").strip()
    if not text:
        return []
    normalized = re.sub(r"(?:然后|并且|以及|同时|另外|还有)", "，", text)
    normalized = re.sub(r"再(?=(?:调用|复用|插入|套用|放|加入|找|拿|画|绘制|生成|应用|使用))", "，", normalized)
    parts = re.split(r"[，,；;。\n]+", normalized)
    return _unique([part.strip() for part in parts if part.strip()])


def score_asset_for_query(asset: dict[str, Any], query: str) -> AssetMatch:
    query_text = _norm(query)
    query_tokens = _tokens(query)
    match_texts = _flatten_match_text(asset)
    matched: list[str] = []
    score = 0.0
    for value in match_texts:
        value_norm = _norm(value)
        if not value_norm:
            continue
        if value_norm and value_norm in query_text:
            score += 5.0
            matched.append(value)
            continue
        for token in query_tokens:
            if token and token in value_norm:
                score += 1.5 if len(token) > 1 else 0.2
                matched.append(value)
                break
    if matched:
        status = str(asset.get("status") or asset.get("lifecycleStatus") or "")
        if status == "verified":
            score += 0.75
        elif status == "systemized":
            score += 0.25
        native = asset.get("nativeDwgExists")
        if native is True or (isinstance(asset.get("native"), dict) and asset["native"].get("nativeDwgExists") is True):
            score += 0.75
    return AssetMatch(asset=asset, score=round(score, 3), matched_terms=_unique(matched))


def find_system_asset(
    query: str,
    *,
    project_root: Path = PROJECT_ROOT,
    asset_id: str | None = None,
    min_score: float = 1.0,
) -> AssetMatch | None:
    assets = load_system_assets(project_root)
    if asset_id:
        for asset in assets:
            if str(asset.get("assetId", "")) == asset_id:
                return AssetMatch(asset=asset, score=EXPLICIT_ASSET_ID_SCORE, matched_terms=[asset_id])
        return None
    matches = find_system_asset_matches(query, project_root=project_root, min_score=min_score, max_matches=1)
    if not matches:
        return None
    return matches[0]


def _status_rank(asset: dict[str, Any]) -> int:
    status = str(asset.get("status") or asset.get("lifecycleStatus") or "")
    return {"verified": 4, "systemized": 3, "candidate": 1, "deprecated": 0}.get(status, 0)


def _native_rank(asset: dict[str, Any]) -> int:
    native = asset.get("native") if isinstance(asset.get("native"), dict) else {}
    return 1 if asset.get("nativeDwgExists") is True or native.get("nativeDwgExists") is True else 0


def _source_rank(asset: dict[str, Any]) -> int:
    try:
        _copy_source_spec(asset)
    except ValueError:
        return 0
    return 1


def _match_sort_key(match: AssetMatch) -> tuple[float, int, int, int, str]:
    return (
        match.score,
        _status_rank(match.asset),
        _native_rank(match.asset),
        _source_rank(match.asset),
        str(match.asset.get("assetId", "")),
    )


def find_system_asset_matches(
    query: str,
    *,
    project_root: Path = PROJECT_ROOT,
    min_score: float = 1.0,
    max_matches: int = 5,
) -> list[AssetMatch]:
    matches = [score_asset_for_query(asset, query) for asset in load_system_assets(project_root)]
    matches = [match for match in matches if match.score >= min_score]
    matches.sort(key=_match_sort_key, reverse=True)
    return matches[:max(0, max_matches)]


def analyze_system_asset_search_need(
    phrase: str,
    *,
    project_root: Path = PROJECT_ROOT,
    implicit_min_score: float = IMPLICIT_ASSET_MATCH_SCORE,
) -> dict[str, Any]:
    encoding_preflight = asset_registry_encoding_preflight(project_root)
    rules = semantic_rule_summary(phrase)
    if encoding_preflight["status"] != "pass":
        return {
            "shouldSearchSystemAssets": False,
            "trigger": "asset_registry_encoding_failed",
            "reason": "system asset registry text failed encoding preflight before semantic matching",
            "implicitMinScore": implicit_min_score,
            "bestMatch": {},
            "candidateMatches": [],
            "encodingPreflight": encoding_preflight,
            "semanticRules": rules,
        }
    explicit = should_search_system_assets(phrase)
    matches = find_system_asset_matches(phrase, project_root=project_root, min_score=1.0, max_matches=3)
    best = matches[0] if matches else None
    implicit = best is not None and best.score >= implicit_min_score
    if explicit:
        trigger = "explicit_reuse_language"
        reason = "request contains asset reuse language"
    elif implicit:
        trigger = "implicit_asset_match"
        reason = "request strongly matches an existing system asset"
    else:
        trigger = "no_asset_signal"
        reason = "request has no reuse verb and no strong system asset match"
    return {
        "shouldSearchSystemAssets": explicit or implicit,
        "trigger": trigger,
        "reason": reason,
        "implicitMinScore": implicit_min_score,
        "bestMatch": _match_summary(best),
        "candidateMatches": [_match_summary(match) for match in matches],
        "encodingPreflight": encoding_preflight,
        "semanticRules": rules,
    }


def _asset_native_dwg(asset: dict[str, Any], project_root: Path) -> Path:
    native = asset.get("native")
    raw = ""
    if isinstance(native, dict):
        raw = str(native.get("dwg") or "")
    if not raw:
        raw = str(asset.get("nativeDwg") or "")
    if not raw:
        raise ValueError(f"asset {asset.get('assetId')!r} has no native DWG path")
    path = Path(raw)
    return path if path.is_absolute() else project_root / path


def _copy_source_spec(asset: dict[str, Any]) -> dict[str, Any]:
    manifest = asset.get("exportManifest") if isinstance(asset.get("exportManifest"), dict) else {}
    native = asset.get("native") if isinstance(asset.get("native"), dict) else {}
    verification = asset.get("verification") if isinstance(asset.get("verification"), dict) else {}
    evidence = verification.get("evidence") if isinstance(verification.get("evidence"), dict) else {}
    asset_kind = str(asset.get("assetKind") or manifest.get("assetKind") or "")
    export_mode = str(manifest.get("exportMode") or "")
    verification_status = str(asset.get("verificationStatus") or verification.get("status") or "")
    native_write = str(manifest.get("nativeWrite") or "")
    included = manifest.get("includedHandles", [])
    if isinstance(included, list) and included:
        return {"mode": "handles", "handles": [str(handle) for handle in included], "reason": "exportManifest.includedHandles"}
    block_name = str(native.get("blockName") or manifest.get("targetBlockName") or "")
    if asset_kind == "object_block" and export_mode == "block_export" and block_name:
        return {"mode": "block", "blockName": block_name, "reason": "object_block.blockName"}
    if (
        asset_kind == "style_standard"
        and export_mode == "style_export"
        and (verification_status == "native_style_definition_written" or native_write == "written_to_standard_assets_dwg")
    ):
        return {
            "mode": "style_definition",
            "assetId": str(asset.get("assetId", "")),
            "nativeWrite": native_write,
            "verificationStatus": verification_status,
            "reason": "style_standard.native_style_definition_written",
        }
    if asset_kind == "style_standard" and (native.get("nativeDwgExists") is True or asset.get("nativeDwgExists") is True):
        return {"mode": "layer", "layer": PREVIEW_LAYER, "reason": "style_standard.preview_layer_copy"}
    if evidence.get("textStyleCounts") or evidence.get("entityCount"):
        return {"mode": "layer", "layer": PREVIEW_LAYER, "reason": "native_visual_evidence.preview_layer_copy"}
    raise ValueError(
        f"asset {asset.get('assetId')!r} has no precise reusable native source; "
        "expected includedHandles, blockName, or verified style_standard native DWG"
    )


def build_system_asset_reuse_plan(
    query: str,
    *,
    project_root: Path = PROJECT_ROOT,
    asset_id: str | None = None,
    base_point: list[float] | None = None,
    target_layer: str = PREVIEW_LAYER,
) -> dict[str, Any]:
    encoding_preflight = asset_registry_encoding_preflight(project_root)
    if encoding_preflight["status"] != "pass":
        return {
            "status": "asset_registry_encoding_failed",
            "query": query,
            "assetId": asset_id or "",
            "shouldSearchSystemAssets": False,
            "reason": "system asset registry text failed encoding preflight before semantic matching",
            "encodingPreflight": encoding_preflight,
            "semanticRules": semantic_rule_summary(query),
            "target": {"layer": target_layer, "basePoint": base_point or [], "saveCurrentDwg": False},
        }
    should_search = should_search_system_assets(query) or bool(asset_id)
    match = find_system_asset(query, project_root=project_root, asset_id=asset_id)
    if match is None:
        return {
            "status": "needs_asset_match",
            "query": query,
            "assetId": asset_id or "",
            "shouldSearchSystemAssets": should_search,
            "reason": "no system asset matched the request",
        }
    asset = match.asset
    native_dwg = _asset_native_dwg(asset, project_root)
    try:
        source_spec = _copy_source_spec(asset)
    except ValueError as exc:
        return {
            "status": "needs_precise_native_source",
            "query": query,
            "shouldSearchSystemAssets": should_search,
            "assetId": str(asset.get("assetId", "")),
            "assetName": str(asset.get("name", "")),
            "category": str(asset.get("category", "")),
            "nativeDwg": str(native_dwg),
            "match": {
                "score": match.score,
                "matchedTerms": match.matched_terms,
            },
            "reason": str(exc),
        }
    return {
        "status": "ready",
        "query": query,
        "shouldSearchSystemAssets": should_search,
        "assetId": str(asset.get("assetId", "")),
        "assetName": str(asset.get("name", "")),
        "category": str(asset.get("category", "")),
        "assetKind": str(asset.get("assetKind", "")),
        "verificationStatus": str(asset.get("verificationStatus") or (asset.get("verification") or {}).get("status") or ""),
        "nativeDwg": str(native_dwg),
        "sourceSpec": source_spec,
        "target": {
            "layer": target_layer,
            "basePoint": base_point or [],
            "saveCurrentDwg": False,
        },
        "match": {
            "score": match.score,
            "matchedTerms": match.matched_terms,
        },
        "encodingPreflight": encoding_preflight,
        "semanticRules": semantic_rule_summary(query),
    }


def _target_base_point(base_point: list[float] | None, slot_index: int) -> list[float] | None:
    if base_point is None:
        return None
    point = [float(value) for value in base_point[:3]]
    while len(point) < 3:
        point.append(0.0)
    point[0] += DEFAULT_MULTI_ASSET_X_OFFSET * slot_index
    return point


def infer_system_asset_reuse_tasks(
    phrase: str,
    *,
    project_root: Path = PROJECT_ROOT,
    implicit_min_score: float = IMPLICIT_ASSET_MATCH_SCORE,
    multi_match_min_score: float = MULTI_ASSET_MATCH_SCORE,
    max_tasks: int = 8,
) -> dict[str, Any]:
    decision = analyze_system_asset_search_need(
        phrase,
        project_root=project_root,
        implicit_min_score=implicit_min_score,
    )
    clauses = split_system_asset_reuse_queries(phrase)
    if decision.get("trigger") == "asset_registry_encoding_failed":
        return {
            "status": "asset_registry_encoding_failed",
            "phrase": phrase,
            "decision": decision,
            "clauses": clauses,
            "tasks": [],
        }
    if not clauses:
        clauses = [phrase] if phrase else []
    tasks: list[dict[str, Any]] = []
    seen_asset_ids: set[str] = set()

    if len(clauses) <= 1:
        strong_matches = find_system_asset_matches(
            phrase,
            project_root=project_root,
            min_score=multi_match_min_score,
            max_matches=max_tasks,
        )
        if len(strong_matches) > 1:
            for index, match in enumerate(strong_matches[:max_tasks], start=1):
                asset_id = str(match.asset.get("assetId", ""))
                if asset_id in seen_asset_ids:
                    continue
                seen_asset_ids.add(asset_id)
                tasks.append(
                    {
                        "taskId": f"asset_reuse_{index}",
                        "query": phrase,
                        "status": "matched",
                        "assetId": asset_id,
                        "assetName": str(match.asset.get("name", "")),
                        "category": str(match.asset.get("category", "")),
                        "match": _match_summary(match),
                        "decision": "multi_asset_phrase_match",
                    }
                )
            return {
                "status": "tasks_inferred",
                "phrase": phrase,
                "decision": decision,
                "clauses": clauses,
                "tasks": tasks,
            }

    for clause in clauses:
        clause_decision = analyze_system_asset_search_need(
            clause,
            project_root=project_root,
            implicit_min_score=implicit_min_score,
        )
        if not clause_decision["shouldSearchSystemAssets"]:
            continue
        match = find_system_asset(clause, project_root=project_root, min_score=1.0)
        if match is None:
            tasks.append(
                {
                    "taskId": f"asset_reuse_{len(tasks) + 1}",
                    "query": clause,
                    "status": "needs_asset_match",
                    "assetId": "",
                    "match": {},
                    "decision": clause_decision["trigger"],
                    "reason": "no system asset matched this clause",
                }
            )
            continue
        asset_id = str(match.asset.get("assetId", ""))
        if asset_id in seen_asset_ids:
            continue
        seen_asset_ids.add(asset_id)
        tasks.append(
            {
                "taskId": f"asset_reuse_{len(tasks) + 1}",
                "query": clause,
                "status": "matched",
                "assetId": asset_id,
                "assetName": str(match.asset.get("name", "")),
                "category": str(match.asset.get("category", "")),
                "match": _match_summary(match),
                "decision": clause_decision["trigger"],
            }
        )

    if not tasks and decision["shouldSearchSystemAssets"]:
        match = find_system_asset(phrase, project_root=project_root, min_score=1.0)
        if match is None:
            tasks.append(
                {
                    "taskId": "asset_reuse_1",
                    "query": phrase,
                    "status": "needs_asset_match",
                    "assetId": "",
                    "match": {},
                    "decision": decision["trigger"],
                    "reason": "no system asset matched the request",
                }
            )
        else:
            tasks.append(
                {
                    "taskId": "asset_reuse_1",
                    "query": phrase,
                    "status": "matched",
                    "assetId": str(match.asset.get("assetId", "")),
                    "assetName": str(match.asset.get("name", "")),
                    "category": str(match.asset.get("category", "")),
                    "match": _match_summary(match),
                    "decision": decision["trigger"],
                }
            )

    return {
        "status": "tasks_inferred" if tasks else "not_asset_reuse_request",
        "phrase": phrase,
        "decision": decision,
        "clauses": clauses,
        "tasks": tasks[:max_tasks],
    }


def build_system_asset_reuse_workflow(
    phrase: str,
    *,
    project_root: Path = PROJECT_ROOT,
    asset_ids: list[str] | None = None,
    base_point: list[float] | None = None,
    target_layer: str = PREVIEW_LAYER,
) -> dict[str, Any]:
    inferred = infer_system_asset_reuse_tasks(phrase, project_root=project_root)
    if asset_ids:
        inferred["tasks"] = [
            {
                "taskId": f"asset_reuse_{index}",
                "query": phrase,
                "status": "matched",
                "assetId": asset_id,
                "match": {"assetId": asset_id, "score": EXPLICIT_ASSET_ID_SCORE, "matchedTerms": [asset_id]},
                "decision": "explicit_asset_id",
            }
            for index, asset_id in enumerate(asset_ids, start=1)
        ]
        inferred["status"] = "tasks_inferred"
        inferred["decision"] = {
            "shouldSearchSystemAssets": True,
            "trigger": "explicit_asset_id",
            "reason": "asset ids were provided explicitly",
            "bestMatch": {},
            "candidateMatches": [],
        }

    tasks = [task for task in inferred.get("tasks", []) if isinstance(task, dict)]
    if not tasks:
        status = str(inferred.get("status") or "not_asset_reuse_request")
        return {
            "kind": "system_asset_reuse_workflow",
            "status": status,
            "phrase": phrase,
            "understanding": {
                **inferred["decision"],
                "taskCount": 0,
                "readyTaskCount": 0,
                "blockedTaskCount": 0,
            },
            "clauses": inferred.get("clauses", []),
            "tasks": [],
            "reusePlans": [],
            "blockedTasks": [],
            "target": {"layer": target_layer, "basePoint": base_point or [], "saveCurrentDwg": False},
        }

    reuse_plans: list[dict[str, Any]] = []
    blocked_tasks: list[dict[str, Any]] = []
    task_summaries: list[dict[str, Any]] = []
    for slot_index, task in enumerate(tasks):
        if task.get("status") != "matched":
            blocked = {**task, "planStatus": task.get("status", "blocked")}
            blocked_tasks.append(blocked)
            task_summaries.append(blocked)
            continue
        plan = build_system_asset_reuse_plan(
            str(task.get("query") or phrase),
            project_root=project_root,
            asset_id=str(task.get("assetId") or "") or None,
            base_point=_target_base_point(base_point, slot_index),
            target_layer=target_layer,
        )
        summary = {
            **task,
            "planStatus": plan.get("status", ""),
            "sourceSpec": plan.get("sourceSpec", {}),
            "target": plan.get("target", {}),
            "reason": plan.get("reason", ""),
        }
        task_summaries.append(summary)
        if plan.get("status") == "ready":
            reuse_plans.append(plan)
        else:
            blocked_tasks.append(summary)

    if reuse_plans and not blocked_tasks:
        status = "ready"
    elif reuse_plans:
        status = "partial"
    else:
        first = blocked_tasks[0] if blocked_tasks else {}
        status = str(first.get("planStatus") or first.get("status") or "blocked")

    return {
        "kind": "system_asset_reuse_workflow",
        "status": status,
        "phrase": phrase,
        "understanding": {
            **inferred["decision"],
            "taskCount": len(tasks),
            "readyTaskCount": len(reuse_plans),
            "blockedTaskCount": len(blocked_tasks),
        },
        "clauses": inferred.get("clauses", []),
        "tasks": task_summaries,
        "reusePlans": reuse_plans,
        "blockedTasks": blocked_tasks,
        "target": {"layer": target_layer, "basePoint": base_point or [], "saveCurrentDwg": False},
    }


def apply_system_asset_reuse_plan(
    plan: dict[str, Any],
    *,
    driver: Any,
    copier: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if plan.get("status") != "ready":
        return {"status": "blocked", "reason": "reuse plan is not ready", "plan": plan}
    target = plan.get("target") if isinstance(plan.get("target"), dict) else {}
    source = plan.get("sourceSpec") if isinstance(plan.get("sourceSpec"), dict) else {}
    if source.get("mode") == "style_definition":
        import_fn = getattr(driver, "apply_style_standard_from_dwg", None) or getattr(driver, "import_style_standard_from_dwg", None)
        if import_fn is None:
            return {
                "status": "style_reuse_deferred_cad_required",
                "reason": "driver does not support native style definition import yet",
                "assetId": plan.get("assetId", ""),
                "assetName": plan.get("assetName", ""),
                "nativeDwg": plan.get("nativeDwg", ""),
                "sourceSpec": source,
                "target": target,
                "created_handles": [],
                "createdHandleCount": 0,
                "readbackStatus": "not_applicable_style_definition",
                "readbackError": "",
                "readbackEntityCount": 0,
                "copyResult": {},
                "savedCurrentDwg": False,
            }
        raw_style_result = import_fn(
            source_dwg=str(plan["nativeDwg"]),
            source_spec=source,
            target_layer=str(target.get("layer") or PREVIEW_LAYER),
        )
        style_result = raw_style_result if isinstance(raw_style_result, dict) else {"status": "invalid_style_import_result", "rawResult": str(raw_style_result)}
        return {
            "status": "style_reused" if style_result.get("status") in {"pass", "style_imported", "style_reused"} else str(style_result.get("status") or "style_reuse_attempted"),
            "assetId": plan.get("assetId", ""),
            "assetName": plan.get("assetName", ""),
            "nativeDwg": plan.get("nativeDwg", ""),
            "sourceSpec": source,
            "target": target,
            "created_handles": [],
            "createdHandleCount": 0,
            "readbackStatus": str(style_result.get("readbackStatus") or "style_definition_import"),
            "readbackError": str(style_result.get("readbackError") or ""),
            "readbackEntityCount": 0,
            "copyResult": style_result,
            "savedCurrentDwg": False,
        }
    copy_fn = copier or getattr(driver, "copy_entities_from_dwg", None)
    if copy_fn is None:
        return {"status": "deferred_cad_required", "reason": "driver does not support cross-DWG system asset copying", "plan": plan}
    raw_result = copy_fn(
        source_dwg=str(plan["nativeDwg"]),
        source_spec=source,
        target_layer=str(target.get("layer") or PREVIEW_LAYER),
        base_point=target.get("basePoint") or None,
    )
    result = raw_result if isinstance(raw_result, dict) else {"status": "invalid_copy_result", "rawResult": str(raw_result)}
    handles = [str(handle) for handle in result.get("created_handles", []) if str(handle)]
    entities = []
    readback_status = "not_attempted"
    readback_error = ""
    if handles and hasattr(driver, "snapshot_handles"):
        try:
            entities = driver.snapshot_handles(handles=handles, layer=str(target.get("layer") or PREVIEW_LAYER))
            readback_status = "ok" if entities else "empty"
        except Exception as exc:  # pragma: no cover - defensive around CAD COM drivers
            readback_status = "failed"
            readback_error = str(exc)
    elif handles:
        readback_status = "unavailable"
    if handles and entities:
        status = "asset_reused"
    elif handles:
        status = f"asset_reuse_readback_{readback_status}"
    else:
        status = str(result.get("status") or "asset_reuse_attempted")
    return {
        "status": status,
        "assetId": plan.get("assetId", ""),
        "assetName": plan.get("assetName", ""),
        "nativeDwg": plan.get("nativeDwg", ""),
        "sourceSpec": source,
        "target": target,
        "created_handles": handles,
        "createdHandleCount": len(handles),
        "readbackStatus": readback_status,
        "readbackError": readback_error,
        "readbackEntityCount": len(entities),
        "copyResult": result,
        "savedCurrentDwg": False,
    }


def apply_system_asset_reuse_workflow(
    workflow: dict[str, Any],
    *,
    driver: Any,
    copier: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    plans = [plan for plan in workflow.get("reusePlans", []) if isinstance(plan, dict)]
    if not plans:
        return {
            "status": "asset_reuse_workflow_blocked",
            "reason": "reuse workflow has no ready plans",
            "workflowStatus": workflow.get("status", ""),
            "workflow": workflow,
            "savedCurrentDwg": False,
        }
    reports = [apply_system_asset_reuse_plan(plan, driver=driver, copier=copier) for plan in plans]
    created_handles: list[str] = []
    for report in reports:
        created_handles.extend(str(handle) for handle in report.get("created_handles", []) if str(handle))
    successful = [report for report in reports if report.get("status") == "asset_reused"]
    blocked_tasks = workflow.get("blockedTasks", []) if isinstance(workflow.get("blockedTasks"), list) else []
    if len(successful) == len(plans) and not blocked_tasks:
        status = "asset_reuse_workflow_completed"
    else:
        status = "asset_reuse_workflow_partial"
    return {
        "status": status,
        "kind": "system_asset_reuse_workflow_result",
        "phrase": workflow.get("phrase", ""),
        "workflowStatus": workflow.get("status", ""),
        "appliedTaskCount": len(reports),
        "successfulTaskCount": len(successful),
        "blockedTaskCount": len(blocked_tasks),
        "created_handles": created_handles,
        "createdHandleCount": len(created_handles),
        "readbackEntityCount": sum(int(report.get("readbackEntityCount", 0)) for report in reports),
        "reports": reports,
        "blockedTasks": blocked_tasks,
        "savedCurrentDwg": False,
    }


def reuse_system_asset(
    query: str,
    *,
    project_root: Path = PROJECT_ROOT,
    asset_id: str | None = None,
    base_point: list[float] | None = None,
    target_layer: str = PREVIEW_LAYER,
    driver: Any | None = None,
) -> dict[str, Any]:
    plan = build_system_asset_reuse_plan(
        query,
        project_root=project_root,
        asset_id=asset_id,
        base_point=base_point,
        target_layer=target_layer,
    )
    if driver is None:
        return plan
    return apply_system_asset_reuse_plan(plan, driver=driver)
