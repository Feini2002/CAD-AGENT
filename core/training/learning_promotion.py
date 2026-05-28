"""Learning-promotion and round-gate helpers for training cases."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROUND_GATE_STAGES = {"visual_contract", "delivery"}


def _round_prefix(round_id: str | int) -> str:
    text = str(round_id)
    return text if text.startswith("round") else f"round{text}"


def _failure_text(failure: dict[str, Any]) -> str:
    fields = [
        "summary",
        "phenomenon",
        "root_cause",
        "fix",
        "failure_type",
        "category",
    ]
    return " ".join(str(failure.get(field, "")) for field in fields).lower()


def classify_learning_failure(
    failure: dict[str, Any],
    *,
    case_id: str,
    scene: str,
) -> dict[str, Any]:
    """Classify a training failure into the narrowest safe promotion target."""

    text = _failure_text(failure)
    if any(token in text for token in ("链路", "pipeline", "delivery", "跳过", "误请", "reference_match")):
        category = "pipeline"
        target = "docs/training/pipeline-changelog.md"
        scope = "global_pipeline"
    elif any(
        token in text
        for token in ("方法论", "反模式", "forbidden", "closed_outer_shell", "missing_required_parts", "probe")
    ):
        category = "core_probe_candidate"
        target = "core/verification/training_geometry_audit.py"
        scope = "global_core"
    elif any(token in text for token in ("场景", "家装", "scene", "vocabulary", "词汇", "product family")):
        category = "scene_rule"
        target = f"agents/{scene}/rules.md"
        scope = "scene"
    elif any(token in text for token in ("几何", "geometry", "尺寸", "断线", "style", "visual")):
        category = "case_geometry"
        target = f"projects/{case_id}/expected/audit_checklist.json"
        scope = "case"
    else:
        category = "case_memory"
        target = f"projects/{case_id}/feedback.md"
        scope = "case"

    return {
        "category": category,
        "scope": scope,
        "promotion_target": target,
        "requires_human_review": category != "case_memory",
    }


def write_learning_promotion_report(
    case_dir: Path,
    round_id: str | int,
    failure: dict[str, Any],
    *,
    scene: str,
) -> Path:
    case_dir = Path(case_dir)
    round_name = _round_prefix(round_id)
    case_id = case_dir.name
    decision = classify_learning_failure(failure, case_id=case_id, scene=scene)
    report = {
        "case_id": case_id,
        "round": round_name,
        "scene": scene,
        "failure": failure,
        "decision": decision,
        "mutated_targets": [],
        "notes": [
            "This report records promotion intent only.",
            "Apply target edits in a separate reviewed package.",
        ],
    }
    output_path = case_dir / "runs" / f"{round_name}_learning_promotion.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def _read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, f"{path.name}: invalid JSON ({exc.msg})"
    if not isinstance(data, dict):
        return None, f"{path.name}: JSON root must be an object"
    return data, None


def _case_relative_file(case_dir: Path, rel_path: str) -> Path | None:
    candidate = (case_dir / rel_path).resolve()
    try:
        candidate.relative_to(case_dir.resolve())
    except ValueError:
        return None
    return candidate


def _style_compare_is_pending(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    return "pending execution" in text or "- [ ]" in text or "not yet executed" in text


def _check_style_target_contract(
    case_dir: Path,
    visual_parts: dict[str, Any],
    blocking: list[str],
) -> None:
    style_target = visual_parts.get("style_target")
    if not isinstance(style_target, str) or not style_target.strip():
        blocking.append("style_target_missing")
        return

    target_path = _case_relative_file(case_dir, style_target)
    if target_path is None:
        blocking.append("style_target_outside_case")
    elif not target_path.is_file():
        blocking.append(f"style_target_file_missing:{style_target}")

    source = visual_parts.get("style_target_source")
    if source not in {"reference_crop", "user_reference", "reference_screenshot"}:
        blocking.append("style_target_source_not_reference_derived")

    evidence = visual_parts.get("style_target_evidence")
    if not isinstance(evidence, dict):
        blocking.append("style_target_evidence_missing")
        return

    if evidence.get("generated") is True:
        blocking.append("generated_style_target_forbidden")
    if evidence.get("derived_from_real_cad_screenshot") is not True:
        blocking.append("style_target_not_real_cad_screenshot")

    source_image = evidence.get("source_image")
    if not isinstance(source_image, str) or not source_image.strip():
        blocking.append("style_target_source_image_missing")
    else:
        source_path = _case_relative_file(case_dir, source_image)
        if source_path is None:
            blocking.append("style_target_source_image_outside_case")
        elif not source_path.is_file():
            blocking.append(f"style_target_source_image_file_missing:{source_image}")


def _required_artifacts(round_name: str, stage: str) -> list[tuple[str, Path]]:
    if stage == "visual_contract":
        return [
            ("feedback", Path("feedback.md")),
            ("visual_parts", Path("runs") / f"{round_name}_visual_parts.json"),
            ("style_compare", Path("runs") / f"{round_name}_style_compare.md"),
            ("agent_review", Path("runs") / f"{round_name}_agent_review.json"),
        ]
    return [
        ("feedback", Path("feedback.md")),
        ("execution_summary", Path("runs") / f"{round_name}_execution_summary.json"),
        ("geometry_audit", Path("runs") / f"{round_name}_geometry_audit.json"),
        ("style_compare", Path("runs") / f"{round_name}_style_compare.md"),
        ("agent_review", Path("runs") / f"{round_name}_agent_review.json"),
        ("preview", Path("runs") / f"{round_name}_preview.png"),
    ]


def run_training_round_gate(
    case_dir: Path,
    round_id: str | int,
    *,
    stage: str = "visual_contract",
) -> dict[str, Any]:
    if stage not in ROUND_GATE_STAGES:
        raise ValueError(f"Unsupported stage: {stage}")

    case_dir = Path(case_dir)
    round_name = _round_prefix(round_id)
    missing: list[str] = []
    blocking: list[str] = []
    parse_errors: list[str] = []

    for _, rel_path in _required_artifacts(round_name, stage):
        path = case_dir / rel_path
        if not path.is_file():
            missing.append(rel_path.name)

    if not missing and stage == "visual_contract":
        visual_parts_path = case_dir / "runs" / f"{round_name}_visual_parts.json"
        visual_parts, error = _read_json(visual_parts_path)
        if error:
            parse_errors.append(error)
        elif not visual_parts or not visual_parts.get("object") or not visual_parts.get("parts"):
            blocking.append("visual_parts_incomplete")
        else:
            _check_style_target_contract(case_dir, visual_parts, blocking)

    if not missing and stage == "delivery":
        audit_path = case_dir / "runs" / f"{round_name}_geometry_audit.json"
        audit, error = _read_json(audit_path)
        if error:
            parse_errors.append(error)
        elif not audit or audit.get("audit_pass") is not True:
            blocking.append("audit_not_passed")

        review_path = case_dir / "runs" / f"{round_name}_agent_review.json"
        review, error = _read_json(review_path)
        if error:
            parse_errors.append(error)
        elif not review or review.get("delivery_allowed") is not True:
            blocking.append("delivery_not_allowed")

        style_compare_path = case_dir / "runs" / f"{round_name}_style_compare.md"
        if _style_compare_is_pending(style_compare_path):
            blocking.append("style_compare_pending")

    status = "pass" if not missing and not blocking and not parse_errors else "fail"
    return {
        "status": status,
        "case_id": case_dir.name,
        "round": round_name,
        "stage": stage,
        "missing_artifacts": missing,
        "blocking_reasons": blocking,
        "parse_errors": parse_errors,
    }
