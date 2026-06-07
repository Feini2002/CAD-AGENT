"""Readonly claim audit for training replay reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _finding(code: str, path: str, message: str, *, severity: str = "blocked", **extra: Any) -> dict[str, Any]:
    return {"code": code, "severity": severity, "path": path, "message": message, **extra}


def _candidate_reports(root: Path, report_roots: list[Path]) -> list[Path]:
    paths: list[Path] = []
    for report_root in report_roots:
        resolved = report_root if report_root.is_absolute() else root / report_root
        if resolved.is_file():
            paths.append(resolved)
        elif resolved.is_dir():
            paths.extend(sorted(resolved.rglob("*.json")))
    return sorted(set(paths))


def audit_training_report_claims(root: Path, report_roots: list[Path]) -> dict[str, Any]:
    """Find reports whose fields would support misleading growth/training claims."""

    findings: list[dict[str, Any]] = []
    scanned = 0
    for path in _candidate_reports(root, report_roots):
        payload = _read_json(path)
        if not payload:
            continue
        if not any(key in payload for key in ("replayMode", "adaptiveReplay", "capabilityProfile", "passType")):
            continue
        scanned += 1
        rel = _display_path(path, root)
        status = str(payload.get("status", ""))
        replay_mode = str(payload.get("replayMode", ""))
        pass_type = str(payload.get("passType", ""))
        adaptive_route = payload.get("adaptiveTrainingRoute", {})
        capability_profile = payload.get("capabilityProfile", {})
        memory_write_mode = str(payload.get("memoryWriteMode", ""))

        if status == "pass" and replay_mode == "smoke_replay":
            if pass_type != "smoke_only":
                findings.append(
                    _finding(
                        "missing_smoke_only_pass_type",
                        rel,
                        "smoke replay pass must carry passType=smoke_only.",
                        passType=pass_type,
                    )
                )
            if isinstance(adaptive_route, dict) and adaptive_route.get("route") not in {
                None,
                "",
                "quick_trial",
                "legacy_remaining_21_smoke",
            }:
                findings.append(
                    _finding(
                        "smoke_replay_upgraded_to_growth_claim",
                        rel,
                        "smoke replay report is routed like growth/formal training.",
                        adaptiveTrainingRoute=adaptive_route,
                    )
                )
        if replay_mode in {"growth_replay", "standard_replay"}:
            profile_source = capability_profile.get("profileSource", {}) if isinstance(capability_profile, dict) else {}
            if str(profile_source.get("status", "")) != "pass":
                findings.append(
                    _finding(
                        "growth_replay_missing_profile_source",
                        rel,
                        "growth/standard replay must use an explicit repo-local profile source.",
                        profileSource=profile_source,
                    )
                )
            default_profiles = [
                str(profile.get("capabilityId", ""))
                for profile in capability_profile.get("profiles", [])
                if isinstance(profile, dict) and profile.get("status") == "default"
            ] if isinstance(capability_profile, dict) else []
            if default_profiles:
                findings.append(
                    _finding(
                        "profile_default_used",
                        rel,
                        "growth/standard replay cannot pass with generated default profiles.",
                        defaultProfileCapabilityIds=default_profiles,
                    )
                )
            if status == "pass":
                renderer_decision = payload.get("rendererDecision", {})
                renderer_status = ""
                renderer_id = ""
                accepted_low_expression = False
                if isinstance(renderer_decision, dict):
                    renderer_status = str(renderer_decision.get("status", ""))
                    renderer_id = str(
                        renderer_decision.get("rendererId")
                        or renderer_decision.get("drawProgramVariant")
                        or renderer_decision.get("renderer")
                        or ""
                    )
                    accepted_low_expression = bool(renderer_decision.get("acceptedLowExpression"))
                if renderer_status not in {"pass", "not_applicable"}:
                    findings.append(
                        _finding(
                            "renderer_decision_missing",
                            rel,
                            "growth/standard replay pass must record a rendererDecision pass or explicit not_applicable boundary.",
                            rendererDecision=renderer_decision,
                        )
                    )
                if renderer_id in {"smoke_panel", "static_foundation_panel"} and not accepted_low_expression:
                    findings.append(
                        _finding(
                            "low_expression_renderer_not_accepted",
                            rel,
                            "growth/standard replay cannot pass through a smoke/static panel renderer unless acceptedLowExpression is explicit.",
                            rendererId=renderer_id,
                        )
                    )
                if payload.get("requiredFeaturesConsumed") is False:
                    findings.append(
                        _finding(
                            "required_features_not_consumed",
                            rel,
                            "growth/standard replay pass must consume required features instead of only changing report fields.",
                        )
                    )
                live_reasoning = payload.get("liveReasoning", {})
                live_required = True
                live_status = ""
                if isinstance(live_reasoning, dict):
                    live_required = bool(live_reasoning.get("required", True))
                    live_status = str(live_reasoning.get("status", ""))
                if live_required and live_status != "pass":
                    findings.append(
                        _finding(
                            "live_reasoning_missing_or_not_pass",
                            rel,
                            "growth/standard replay pass must either consume live reasoning or explicitly block/not verify when it is unavailable.",
                            liveReasoning=live_reasoning,
                        )
                    )
                memory_no_downgrade = payload.get("memoryNoDowngrade", {})
                memory_no_downgrade_status = (
                    str(memory_no_downgrade.get("status", "")) if isinstance(memory_no_downgrade, dict) else ""
                )
                if memory_write_mode == "overwrite" or (
                    memory_write_mode != "no_write" and memory_no_downgrade_status != "pass"
                ):
                    findings.append(
                        _finding(
                            "memory_no_downgrade_missing",
                            rel,
                            "growth/standard replay pass must prove memory merge/no-downgrade or explicitly perform no_write.",
                            memoryWriteMode=memory_write_mode,
                            memoryNoDowngrade=memory_no_downgrade,
                        )
                    )
                template_lock = payload.get("templateLock", {})
                template_lock_status = str(template_lock.get("status", "")) if isinstance(template_lock, dict) else ""
                if template_lock_status not in {"checked", "pass", "not_applicable"}:
                    findings.append(
                        _finding(
                            "template_lock_not_checked",
                            rel,
                            "growth/standard replay pass must check template lock or mark it not_applicable with a boundary.",
                            templateLock=template_lock,
                        )
                    )
                model_suggestion = payload.get("modelSuggestion", {})
                if isinstance(model_suggestion, dict) and model_suggestion:
                    disposition = str(model_suggestion.get("disposition", ""))
                    if disposition not in {"accepted", "rejected", "rewritten", "blocked"}:
                        findings.append(
                            _finding(
                                "model_suggestion_missing_disposition",
                                rel,
                                "model suggestions must be accepted/rejected/rewritten/blocked before a growth/standard replay can pass.",
                                modelSuggestion=model_suggestion,
                            )
                        )
                    elif disposition in {"accepted", "rewritten"} and not any(
                        key in model_suggestion
                        for key in ("cadPlanDiff", "rendererContract", "repairPlan", "checkerDelta", "testDelta")
                    ):
                        findings.append(
                            _finding(
                                "model_suggestion_not_consumed",
                                rel,
                                "accepted/rewritten model suggestions must feed CAD_PLAN diff, renderer contract, repair plan, checker, or tests.",
                                modelSuggestion=model_suggestion,
                            )
                        )
                candidate_policy = payload.get("candidatePolicy", {})
                if isinstance(candidate_policy, dict) and candidate_policy.get("policy") == "bounded_multi_candidate":
                    candidates = candidate_policy.get("candidates", [])
                    if not isinstance(candidates, list) or len(candidates) < 2:
                        findings.append(
                            _finding(
                                "bounded_autonomy_missing_candidates",
                                rel,
                                "bounded multi-candidate policy must produce at least two candidates.",
                                candidatePolicy=candidate_policy,
                            )
                        )
                    if str(candidate_policy.get("selectedCandidateDisposition", "")) not in {
                        "accepted",
                        "rewritten",
                        "rejected",
                        "blocked",
                    }:
                        findings.append(
                            _finding(
                                "candidate_policy_missing_disposition",
                                rel,
                                "bounded autonomy must record selected candidate disposition before pass.",
                                candidatePolicy=candidate_policy,
                            )
                        )
        if status == "pass" and replay_mode == "smoke_replay" and memory_write_mode == "overwrite":
            findings.append(
                _finding(
                    "memory_downgrade_risk",
                    rel,
                    "smoke replay must not overwrite training memory.",
                    memoryWriteMode=memory_write_mode,
                )
            )

    blocked = [finding for finding in findings if finding.get("severity") == "blocked"]
    return {
        "schemaVersion": "training-report-claim-audit/v1",
        "status": "blocked" if blocked else "pass",
        "summary": {
            "reportRoots": [_display_path(path if path.is_absolute() else root / path, root) for path in report_roots],
            "reportsScanned": scanned,
            "blockedCount": len(blocked),
        },
        "findings": findings,
        "operatorAction": "fix blocked report claim fields before using reports as growth/formal training evidence."
        if blocked
        else "no claim blockers found.",
    }
