"""Read-only Reviewer Host runtime for delivery closeout."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from core.model_review.codex_cli_client import CodexCliReviewConfig, Runner
from core.model_review.prompt_library import run_prompt_pack_review
from core.orchestrator.closeout_gate import CLOSEOUT_DECISION_FILE, run_closeout_gate


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DELIVERY_REVIEW_FILE = "agent_outputs/pipeline_delivery.json"
DELIVERY_MODEL_REVIEW_FILE = "agent_outputs/pipeline_delivery.model_review.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _request_text(run_dir: Path) -> str:
    user_request = _read_json(run_dir / "user_request.json").get("userRequest", "")
    if isinstance(user_request, dict):
        for key in ("text", "user_request", "request", "prompt"):
            if user_request.get(key):
                return str(user_request[key])
    return str(user_request)


def _input_refs(run_dir: Path) -> list[str]:
    refs = [
        "user_request.json",
        "dispatch_plan.json",
        "task_contract.json",
        CLOSEOUT_DECISION_FILE,
    ]
    for rel in (
        "cad_reports/validation_report.json",
        "cad_reports/dry_run_report.json",
        "cad_reports/readback_summary.json",
        "agent_outputs/visual_acceptance_output.json",
        "agent_outputs/pipeline_visual_acceptance_reviewer.json",
        "cad_reports/neighbor_protection.json",
        "cad_reports/delete_scope_gate.json",
        "cad_reports/asset_source_boundary.json",
    ):
        if (run_dir / rel).is_file():
            refs.append(rel)
    screenshot_dir = run_dir / "screenshots"
    if screenshot_dir.is_dir():
        refs.extend(
            sorted(str(path.relative_to(run_dir)).replace("\\", "/") for path in screenshot_dir.iterdir() if path.is_file())
        )
    return refs


def _evidence_missing(closeout: dict[str, Any]) -> list[str]:
    boundary = closeout.get("evidence_boundary", {})
    not_checked = boundary.get("not_checked", []) if isinstance(boundary, dict) else []
    missing = [str(item) for item in not_checked if str(item)]
    for reason in closeout.get("blocking_reasons", []):
        text = str(reason)
        if "created_handles_readback" in text and "created_handles_readback" not in missing:
            missing.append("created_handles_readback")
    return missing


def _delivery_review_from_closeout(closeout: dict[str, Any]) -> dict[str, Any]:
    can_deliver = bool(closeout.get("can_deliver"))
    blocking_reasons = [str(item) for item in closeout.get("blocking_reasons", []) if str(item)]
    checked = closeout.get("evidence_boundary", {}).get("checked", [])
    checked_text = [str(item) for item in checked if str(item)]
    missing = _evidence_missing(closeout)
    screenshots = closeout.get("evidence_boundary", {}).get("screenshots", {})
    screenshot_count = screenshots.get("count", 0) if isinstance(screenshots, dict) else 0
    allowed_claims = [str(item) for item in closeout.get("final_response_allowed_claims", []) if str(item)]

    if can_deliver:
        status = "pass"
        decision = "ready_to_ask_user_review"
        opening = "可验收"
        pending = ["用户目视验收"]
        next_action = "ask_user_review"
    else:
        status = "fail"
        decision = "not_verified"
        opening = "暂不交付"
        pending = missing or blocking_reasons
        next_action = "fix_missing_evidence"
        allowed_claims = []

    evidence_does_not_prove = [
        "截图只作视觉辅助",
        "模型 pass 不等于 CAD 几何证明",
        "closeout pass 不等于用户已验收",
    ]
    return {
        "schemaVersion": "reviewer-host-delivery-review/v1",
        "status": status,
        "deliveryDecision": decision,
        "openingLine": opening,
        "whatChanged": ["Reviewer Host 已读取 run package 证据并生成交付口径"],
        "evidenceProves": checked_text if checked_text else ["当前没有足够证据证明可交付"],
        "evidenceDoesNotProve": evidence_does_not_prove,
        "lookHereFirst": ["主要对象位置", "中文文字是否可读", "遮挡 / 裁剪 / 贴边", "本轮 created handles 范围"],
        "usefulUserFeedback": "请直接指出不对的对象、位置或文字；如果只是局部错误，我会按 handles / bbox 原位修。",
        "blockingReasons": blocking_reasons,
        "statePatch": {
            "phase": "ready_for_delivery" if can_deliver else "blocked",
            "phaseLabelForUser": "交付复审通过" if can_deliver else "交付复审未通过",
            "completedEvidence": checked_text,
            "pendingEvidence": pending,
            "pendingUserAction": "请你打开 CAD 后目视验收" if can_deliver else "",
            "blockedReason": "; ".join(blocking_reasons),
            "nextSafeAction": next_action,
        },
        "finalResponseAllowedClaims": allowed_claims,
        "evidenceUsed": [str(item) for item in closeout.get("input_files", [])],
        "evidenceMissing": missing,
        "screenshotEvidence": {"role": "visual_aid_only", "count": screenshot_count},
        "modelProviderStatus": {
            "modelInvoked": False,
            "route": "deterministic_reviewer_host",
            "schemaValid": True,
            "blocking": not can_deliver,
        },
    }


def _write_final_report(run_dir: Path, review: dict[str, Any], closeout: dict[str, Any]) -> None:
    lines = [
        f"# Reviewer Host Closeout {run_dir.name}",
        "",
        f"- status: `{review['deliveryDecision']}`",
        f"- openingLine: `{review['openingLine']}`",
        f"- generatedAt: `{_utc_now()}`",
        "",
        "## Evidence Proves",
        "",
    ]
    for item in review["evidenceProves"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Evidence Does Not Prove", ""])
    for item in review["evidenceDoesNotProve"]:
        lines.append(f"- {item}")
    if review["blockingReasons"]:
        lines.extend(["", "## Blocking Reasons", ""])
        for item in review["blockingReasons"]:
            lines.append(f"- {item}")
    lines.extend(["", "## Allowed Claims", ""])
    if review["finalResponseAllowedClaims"]:
        for item in review["finalResponseAllowedClaims"]:
            lines.append(f"- {item}")
    else:
        lines.append("- 暂无；当前不得声称 CAD 几何已完成或可交付。")
    lines.extend(["", "## Boundary", "", "- 截图只作视觉辅助，不能替代 created handles readback、closeout gate 或用户验收。"])
    lines.append(f"- closeoutDecision: `{closeout.get('status')}`")
    (run_dir / "final_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _model_payload(run_dir: Path, closeout: dict[str, Any], review: dict[str, Any]) -> dict[str, Any]:
    return {
        "userRequest": _request_text(run_dir),
        "taskContext": {
            "taskKind": "reviewer_host_closeout",
            "route": _read_json(run_dir / "dispatch_plan.json").get("route", ""),
            "closeoutStatus": closeout.get("status"),
            "deliveryDecision": review.get("deliveryDecision"),
        },
        "evidenceRefs": _input_refs(run_dir),
        "statePatchRequest": {
            "phase": review["statePatch"]["phase"],
            "phaseLabelForUser": review["statePatch"]["phaseLabelForUser"],
        },
        "agentSpecific": {"closeoutDecision": closeout, "deterministicDeliveryReview": review},
    }


def _maybe_run_model_delivery_review(
    *,
    run_dir: Path,
    closeout: dict[str, Any],
    review: dict[str, Any],
    config: CodexCliReviewConfig | None,
    runner: Runner | None,
    cwd: str | Path | None,
) -> dict[str, Any]:
    cfg = config or CodexCliReviewConfig.from_environment()
    if not cfg.enabled:
        return {
            "status": "skipped",
            "modelInvoked": False,
            "reason": "reviewer host model review disabled",
            "promptPackId": "pipeline_delivery",
        }
    return run_prompt_pack_review(
        agent_id="pipeline_delivery",
        payload=_model_payload(run_dir, closeout, review),
        run_dir=run_dir,
        output_path=run_dir / DELIVERY_MODEL_REVIEW_FILE,
        config=cfg,
        runner=runner,
        cwd=cwd or PROJECT_ROOT,
        trace_id="delivery-closeout",
    )


def run_reviewer_host_closeout_runtime(
    run_dir: str | Path,
    *,
    config: CodexCliReviewConfig | None = None,
    runner: Runner | None = None,
    cwd: str | Path | None = None,
) -> dict[str, Any]:
    """Run deterministic closeout and write Reviewer Host delivery artifacts."""

    run_root = Path(run_dir)
    closeout = run_closeout_gate(run_root)
    review = _delivery_review_from_closeout(closeout)
    _write_json(run_root / DELIVERY_REVIEW_FILE, review)
    model_review = _maybe_run_model_delivery_review(
        run_dir=run_root,
        closeout=closeout,
        review=review,
        config=config,
        runner=runner,
        cwd=cwd,
    )
    _write_final_report(run_root, review, closeout)
    return {
        "schemaVersion": "reviewer-host-runtime-result/v1",
        "runId": run_root.name,
        "writtenAt": _utc_now(),
        "closeoutDecision": closeout,
        "deliveryReview": review,
        "modelReview": model_review,
        "outputFiles": [CLOSEOUT_DECISION_FILE, DELIVERY_REVIEW_FILE, "final_report.md"],
        "inputRefs": _input_refs(run_root),
    }
