"""Capability growth profile helpers for adaptive foundation replay."""

from __future__ import annotations

import json
import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


VALID_REPLAY_MODES = {"smoke_replay", "growth_replay", "standard_replay"}
DERIVED_PROFILE_SOURCE_NAMES = {
    "capability-map-data.js",
    "capability-map.html",
    "training_workbench_sync_report.json",
    "training_workbench_sync_report.md",
    "retention_report.json",
}


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _repo_rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _hash_file(path: Path) -> str:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return ""


def classify_profile_source_role(
    path: Path,
    *,
    project_root: Path,
    active_fact_source_paths: list[Path] | None = None,
) -> dict[str, Any]:
    root = Path(project_root)
    source = Path(path)
    rel = _repo_rel(source, root)
    exists = source.is_file()
    active_paths = {
        _repo_rel(Path(active_path), root)
        for active_path in (active_fact_source_paths or [])
    }
    if rel in active_paths and exists:
        role = "fact_source"
        hard_baseline_allowed = True
    elif not exists:
        role = "missing_or_stale"
        hard_baseline_allowed = False
    elif rel.startswith("output/debug/"):
        role = "diagnostic"
        hard_baseline_allowed = False
    elif source.name in DERIVED_PROFILE_SOURCE_NAMES or rel.startswith("output/validation_runs/training-workbench-sync/"):
        role = "derived"
        hard_baseline_allowed = False
    elif rel.startswith("archive/") or "/archive/" in rel or rel.startswith("docs/handoffs/archive/"):
        role = "archived_index"
        hard_baseline_allowed = False
    elif rel.startswith("output/training_queues/") or rel.startswith("output/training_learning/"):
        role = "candidate"
        hard_baseline_allowed = False
    else:
        role = "candidate"
        hard_baseline_allowed = False
    return {
        "path": rel,
        "exists": exists,
        "role": role,
        "status": "pass" if exists else "missing",
        "hardBaselineAllowed": hard_baseline_allowed,
        "hash": _hash_file(source) if exists else "",
        "dataBloatRole": "protected" if role == "fact_source" else ("derived" if role == "derived" else "diagnostic"),
    }


def validate_profile_source(profile_source: Path | None, *, project_root: Path) -> dict[str, Any]:
    if profile_source is None:
        return {
            "status": "not_provided",
            "role": "none",
            "path": "",
            "reason": "profile_source_not_provided",
            "readAttempted": False,
        }
    source = Path(profile_source)
    if not _is_relative_to(source, Path(project_root)):
        return {
            "status": "blocked",
            "role": "local_file",
            "path": str(source),
            "reason": "profile_source_outside_workspace",
            "readAttempted": False,
        }
    if not source.is_file():
        return {
            "status": "blocked",
            "role": "local_file",
            "path": str(source),
            "reason": "profile_source_missing",
            "readAttempted": True,
        }
    return {
        "status": "pass",
        "role": "local_file",
        "path": str(source),
        "reason": "",
        "readAttempted": True,
    }


def _read_profile_payload(profile_source: Path | None, source_check: dict[str, Any]) -> dict[str, Any]:
    if source_check.get("status") != "pass" or profile_source is None:
        return {}
    try:
        return json.loads(Path(profile_source).read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        source_check["status"] = "blocked"
        source_check["reason"] = f"profile_source_invalid_json: {exc}"
        return {}


def _profile_entries(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw_profiles = payload.get("profiles", {})
    if isinstance(raw_profiles, dict):
        return {
            str(capability_id): profile
            for capability_id, profile in raw_profiles.items()
            if isinstance(profile, dict)
        }
    if isinstance(raw_profiles, list):
        entries: dict[str, dict[str, Any]] = {}
        for profile in raw_profiles:
            if isinstance(profile, dict) and profile.get("capabilityId"):
                entries[str(profile["capabilityId"])] = profile
        return entries
    return {}


def _normalize_lessons(raw_lessons: Any, capability_id: str) -> list[dict[str, Any]]:
    if not isinstance(raw_lessons, list):
        return []
    lessons = []
    for index, lesson in enumerate(raw_lessons, start=1):
        if not isinstance(lesson, dict):
            continue
        lesson_id = str(lesson.get("lessonId") or f"{capability_id}:lesson-{index}")
        lessons.append(
            {
                "lessonId": lesson_id,
                "originCapabilityId": str(lesson.get("originCapabilityId") or capability_id),
                "lessonType": str(lesson.get("lessonType") or "transferable_observation"),
                "summary": str(lesson.get("summary") or lesson.get("statement") or ""),
                "statement": str(lesson.get("statement") or lesson.get("summary") or ""),
                "positiveExample": str(lesson.get("positiveExample") or lesson.get("positivePattern") or ""),
                "negativeExample": str(lesson.get("negativeExample") or lesson.get("negativePattern") or ""),
                "evidenceBoundary": {
                    "checked": list(lesson.get("checked", [])) if isinstance(lesson.get("checked"), list) else [],
                    "notChecked": list(lesson.get("notChecked", []))
                    if isinstance(lesson.get("notChecked"), list)
                    else ["真实 CAD 几何仍由当前 replay readback 决定"],
                    "forbiddenClaims": list(lesson.get("forbiddenClaims", []))
                    if isinstance(lesson.get("forbiddenClaims"), list)
                    else ["不能把历史经验当作当前 CAD 通过"],
                },
                "promotionLevel": str(lesson.get("promotionLevel") or "observation"),
                "confidence": str(lesson.get("confidence") or "medium"),
            }
        )
    return lessons


def _default_minimum_expression(replay_mode: str) -> str:
    if replay_mode == "standard_replay":
        return "standard"
    if replay_mode == "growth_replay":
        return "growth"
    return "smoke"


def build_capability_growth_profile(
    *,
    programs: list[dict[str, Any]],
    capability_ids: list[str],
    replay_mode: str,
    profile_source: Path | None = None,
    project_root: Path | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    if replay_mode not in VALID_REPLAY_MODES:
        return {
            "schemaVersion": 1,
            "status": "blocked",
            "reason": "unsupported_replay_mode",
            "replayMode": replay_mode,
            "profileSource": {
                "status": "not_checked",
                "role": "none",
                "path": "",
                "readAttempted": False,
            },
            "profiles": [],
        }

    root = Path(project_root or Path.cwd())
    source_check = validate_profile_source(profile_source, project_root=root)
    source_check["evidenceRole"] = "profile_input_not_fact_source"
    source_check["sourceClosure"] = "not_registered"
    payload = _read_profile_payload(profile_source, source_check)
    if source_check.get("status") == "blocked":
        return {
            "schemaVersion": 1,
            "status": "blocked",
            "reason": source_check.get("reason", "profile_source_blocked"),
            "generatedAt": generated_at or _utc_now(),
            "replayMode": replay_mode,
            "profileSource": source_check,
            "profiles": [],
        }

    program_map = {str(program.get("capabilityId", "")): program for program in programs}
    stored_profiles = _profile_entries(payload)
    profiles = []
    for capability_id in capability_ids:
        program = program_map.get(capability_id, {})
        stored = stored_profiles.get(capability_id, {})
        lessons = _normalize_lessons(stored.get("transferableLessons", []), capability_id)
        profile_version = str(stored.get("profileVersion") or "generated-default-v1")
        minimum_expression = str(stored.get("minimumExpressionLevel") or _default_minimum_expression(replay_mode))
        source_ref_id = f"{capability_id}:profile-source"
        profiles.append(
            {
                "schemaVersion": 1,
                "profileId": f"{capability_id}:adaptive-growth",
                "capabilityId": capability_id,
                "title": str(program.get("name") or stored.get("title") or capability_id),
                "stage": str(stored.get("stage") or "foundation"),
                "category": str(stored.get("category") or "cad_foundation_operation"),
                "status": "active" if stored else "default",
                "profileVersion": profile_version,
                "sourceRefs": [
                    {
                        "id": source_ref_id,
                        "kind": "local_profile_json" if profile_source else "generated_default",
                        "path": str(profile_source or ""),
                        "status": source_check.get("status", "not_provided"),
                        "role": "profile_input",
                        "evidenceRole": "planning_context_only",
                        "sourceClosure": "not_registered",
                        "hash": str(stored.get("hash") or ""),
                        "generatedAt": generated_at or _utc_now(),
                    }
                ],
                "proofLevel": str(stored.get("proofLevel") or "planning_context_only"),
                "expressionLevel": minimum_expression,
                "minimumExpressionLevel": minimum_expression,
                "confidence": str(stored.get("confidence") or ("medium" if stored else "low")),
                "evidenceState": "profile_loaded" if stored else "profile_default",
                "evidenceBoundary": {
                    "checked": ["profile schema parsed"] if stored else ["program metadata mapped"],
                    "notChecked": [
                        "当前真实 CAD 几何",
                        "用户人工视觉验收",
                        "工作台同步",
                        "项目交付准备度",
                    ],
                    "forbiddenClaims": [
                        "不能用 profile 代替 created handles readback",
                        "不能用历史训练 pass 声称当前任务通过",
                    ],
                },
                "deterministicProofBoundaries": {
                    "cadGeometryProof": "not_checked",
                    "projectDeliveryReadiness": "not_checked",
                    "workbenchSync": "not_checked",
                    "workerDeployment": "not_required",
                },
                "lastBestEvidence": {
                    "sourceRefId": source_ref_id,
                    "mode": "profile_context",
                    "scope": "planning_only",
                    "cadReadback": "not_checked",
                    "auditSummary": "not_checked",
                },
                "defaultReplayStrategy": {
                    "quickTrial": "smoke_replay",
                    "focusedRetraining": "growth_replay",
                    "formalAcceptance": "standard_replay",
                },
                "requiredFeatureSet": list(stored.get("requiredFeatureSet", []))
                if isinstance(stored.get("requiredFeatureSet"), list)
                else [],
                "optionalFeatureSet": list(stored.get("optionalFeatureSet", []))
                if isinstance(stored.get("optionalFeatureSet"), list)
                else [],
                "forbiddenShortcuts": list(stored.get("forbiddenShortcuts", []))
                if isinstance(stored.get("forbiddenShortcuts"), list)
                else ["screenshot_only_pass", "handle_count_only_pass"],
                "relatedCapabilities": list(stored.get("relatedCapabilities", []))
                if isinstance(stored.get("relatedCapabilities"), list)
                else [],
                "prerequisites": list(stored.get("prerequisites", []))
                if isinstance(stored.get("prerequisites"), list)
                else [],
                "downstreamAffected": list(stored.get("downstreamAffected", []))
                if isinstance(stored.get("downstreamAffected"), list)
                else [],
                "transferableLessons": lessons,
                "transferableLessonIds": [lesson["lessonId"] for lesson in lessons],
                "knownFailureModeIds": list(stored.get("knownFailureModeIds", []))
                if isinstance(stored.get("knownFailureModeIds"), list)
                else [],
                "validatorIds": list(stored.get("validatorIds", []))
                if isinstance(stored.get("validatorIds"), list)
                else [],
                "promotionState": {
                    "level": str(stored.get("promotionLevel") or "observation"),
                    "lastPromotionGateRef": str(stored.get("lastPromotionGateRef") or ""),
                    "needsReviewedPackage": bool(stored.get("needsReviewedPackage", False)),
                },
                "staleness": {
                    "profileGeneratedAt": generated_at or _utc_now(),
                    "sourceStale": False,
                    "missingActiveRefs": [],
                    "rebuildReason": "",
                },
                "dataBloatRole": "profile_input_only",
            }
        )
    return {
        "schemaVersion": 1,
        "status": "pass",
        "generatedAt": generated_at or _utc_now(),
        "replayMode": replay_mode,
        "profileSource": source_check,
        "profiles": profiles,
    }


def _load_training_sources(project_root: Path) -> tuple[list[dict[str, Any]], list[Path]]:
    path = project_root / "docs" / "training" / "training-sources.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return [], []
    raw_sources = payload.get("sources") or payload.get("trainingSources") or []
    sources = [source for source in raw_sources if isinstance(source, dict)]
    active_paths = []
    for source in sources:
        if source.get("status") == "active" and source.get("path"):
            active_paths.append(project_root / str(source["path"]))
    return sources, active_paths


def build_capability_growth_inventory(
    *,
    project_root: Path,
    programs: list[dict[str, Any]],
) -> dict[str, Any]:
    root = Path(project_root)
    training_sources, active_paths = _load_training_sources(root)
    source_paths: list[Path] = []
    for source in training_sources:
        if source.get("path"):
            source_paths.append(root / str(source["path"]))
    source_paths.extend(root.glob("agents/**/training_memory.json"))
    source_paths.extend(root.glob("agents/**/prompt_addendum.md"))
    source_paths.extend(root.glob("output/training_queues/**/*.json"))
    source_paths.extend(root.glob("archive/**/*.json"))
    unique_paths = []
    seen = set()
    for path in source_paths:
        rel = _repo_rel(path, root)
        if rel not in seen:
            seen.add(rel)
            unique_paths.append(path)
    sources = [
        classify_profile_source_role(path, project_root=root, active_fact_source_paths=active_paths)
        for path in unique_paths
    ]
    role_counts = {}
    for source in sources:
        role = str(source.get("role", "unknown"))
        role_counts[role] = role_counts.get(role, 0) + 1
    return {
        "schemaVersion": "capability-growth-profile-inventory/v1",
        "status": "pass",
        "generatedAt": _utc_now(),
        "mode": "no_cad",
        "cadExecution": {"status": "not_run", "created_handle_count": 0, "savedCurrentDwg": False},
        "programCount": len(programs),
        "sources": sources,
        "sourceRoleCounts": role_counts,
        "mutatedTargets": [],
        "dataBloatRole": "diagnostic",
        "factSourceWriteAllowed": False,
        "workbenchSyncAllowed": False,
    }


def write_growth_inventory_report(inventory: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "capability_growth_profile_inventory.json"
    path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "status": "pass",
        "reportPath": str(path),
        "dataBloatRole": "diagnostic",
        "factSourceWriteAllowed": False,
    }


def build_transferable_lesson_candidate(
    *,
    lesson_id: str,
    origin_capability_id: str,
    statement: str,
    positive_pattern: str = "",
    negative_pattern: str = "",
    preconditions: list[str] | None = None,
    does_not_apply_when: list[str] | None = None,
    audit_implication: str = "",
    retest_required: bool | None = None,
    source_refs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    missing = []
    for field, value in (
        ("lessonId", lesson_id),
        ("originCapabilityId", origin_capability_id),
        ("statement", statement),
        ("positivePattern", positive_pattern),
        ("negativePattern", negative_pattern),
        ("preconditions", preconditions),
        ("doesNotApplyWhen", does_not_apply_when),
        ("auditImplication", audit_implication),
        ("retestRequired", retest_required),
    ):
        if value in ("", None, []):
            missing.append(field)
    status = "invalid" if missing else "valid"
    return {
        "schemaVersion": "transferable-lesson/v1",
        "status": status,
        "missingFields": missing,
        "lessonId": lesson_id,
        "originCapabilityId": origin_capability_id,
        "originTaskId": "",
        "originMode": "focused_retraining",
        "sourceRefs": source_refs or [],
        "lessonType": "cad_expression_boundary",
        "statement": statement,
        "positivePattern": positive_pattern,
        "negativePattern": negative_pattern,
        "preconditions": preconditions or [],
        "doesNotApplyWhen": does_not_apply_when or [],
        "appliesToCapabilities": [origin_capability_id],
        "cadPlanImplication": "planner may add required semantic features, but CAD execution remains deterministic",
        "auditImplication": audit_implication,
        "promptImplication": "candidate only; requires reviewed package before prompt/memory update",
        "checkerDelta": {"status": "needs_reviewed_package"},
        "evidenceBoundary": {
            "checked": ["candidate schema completeness"] if status == "valid" else [],
            "notChecked": ["当前真实 CAD 几何", "用户人工验收", "工作台同步"],
            "forbiddenClaims": ["不能用 candidate lesson 直接更新规则、checker、memory 或 profile fact source"],
        },
        "confidence": "medium" if status == "valid" else "low",
        "promotionLevel": "candidate",
        "ownerAgents": ["pipeline_learning_promoter", "pipeline_audit"],
        "retestRequired": bool(retest_required),
    }


def build_profile_candidate_from_sources(
    *,
    capability_id: str,
    sources: list[Path],
    project_root: Path,
    require_hard_baseline: bool = False,
) -> dict[str, Any]:
    source_refs = [
        classify_profile_source_role(source, project_root=project_root)
        for source in sources
    ]
    hard_sources = [source for source in source_refs if source.get("hardBaselineAllowed")]
    if require_hard_baseline and not hard_sources:
        return {
            "schemaVersion": "capability-profile-candidate/v1",
            "status": "blocked",
            "reason": "no_fact_source_hard_baseline",
            "capabilityId": capability_id,
            "sourceRefs": source_refs,
            "mutatedTargets": [],
        }
    return {
        "schemaVersion": "capability-profile-candidate/v1",
        "status": "candidate",
        "reason": "",
        "capabilityId": capability_id,
        "sourceRefs": source_refs,
        "hardBaselineSourceCount": len(hard_sources),
        "mutatedTargets": [],
    }
