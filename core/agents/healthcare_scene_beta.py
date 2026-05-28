"""Healthcare scene beta benchmark runner (BETA-SCENE-04)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.agents.scene_beta import (
    default_healthcare_scene_beta_benchmark_path,
    load_scene_beta_healthcare_preferences,
    validate_scene_beta_healthcare_preferences,
)
from core.benchmarks.runner import run_benchmark_suite, summarize_benchmark_evidence


def validate_healthcare_scene_beta_suite(suite: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    tiers = {str(case.get("case_tier", "")) for case in suite.get("cases", []) if isinstance(case, dict)}
    for required in ("object", "clinical", "waiting", "blank_shell", "failure"):
        if required not in tiers:
            errors.append(f"missing case_tier: {required}")
    scene_beta = suite.get("scene_beta", {})
    if not isinstance(scene_beta, dict) or scene_beta.get("scenario") != "healthcare":
        errors.append("suite.scene_beta.scenario must be healthcare")
    return errors


def run_healthcare_scene_beta_benchmark(
    *,
    project_root: Path,
    output_root: Path,
    suite_path: Path | None = None,
) -> dict[str, Any]:
    preferences = load_scene_beta_healthcare_preferences(root=project_root)
    preference_errors = validate_scene_beta_healthcare_preferences(preferences)
    if preference_errors:
        return {
            "status": "fail",
            "suite_id": "healthcare-scene-beta-benchmark",
            "preference_errors": preference_errors,
            "summary": {"total": 0, "passed": 0, "failed": 0},
            "cases": [],
        }

    suite_file = suite_path or default_healthcare_scene_beta_benchmark_path(project_root)
    suite = json.loads(suite_file.read_text(encoding="utf-8"))
    suite_errors = validate_healthcare_scene_beta_suite(suite)
    if suite_errors:
        return {
            "status": "fail",
            "suite_id": suite.get("suite_id", "healthcare-scene-beta-benchmark"),
            "suite_errors": suite_errors,
            "summary": {"total": 0, "passed": 0, "failed": 0},
            "cases": [],
        }

    result = run_benchmark_suite(suite_file, output_root=output_root)
    evidence_summary = summarize_benchmark_evidence(result.get("cases", []))
    expected_summary = suite.get("expected_evidence_summary", {})
    summary_errors = [
        f"expected_evidence_summary.{key}: expected {expected_value}, got {evidence_summary.get(key)}"
        for key, expected_value in expected_summary.items()
        if evidence_summary.get(key) != expected_value
    ]
    if summary_errors:
        result["status"] = "fail"
        result["expected_evidence_summary_errors"] = summary_errors
    result["evidence_summary"] = evidence_summary
    result["preference_validation"] = "pass"
    return result
