"""Multi-scene beta regression gate (SCENE-PROD-06 / BETA-SCENE-05)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from core.agents.multi_scene_p3_wave import multi_scene_p3_wave_status_summary
from core.agents.office_scene_beta import run_office_scene_beta_benchmark
from core.agents.residential_scene_beta import run_residential_scene_beta_benchmark
from core.agents.restaurant_scene_beta import run_restaurant_scene_beta_benchmark
from core.agents.scene_beta_explanation import scene_beta_explanation_status_summary

SCENE_PROD_06_PACKAGE_ID = "SCENE-PROD-06-MULTI-SCENE-REGRESSION-GATE"
SCENE_PROD_06_ACCEPTANCE_DOC = "docs/verification/scene_prod_06_multi_scene_regression_gate.md"
SCENE_PROD_06_DEFAULT_OUTPUT_ROOT = "output/validation_runs/scene-prod-06-regression-gate-no-cad"

SCENE_PROD_06_EVIDENCE_BOUNDARIES: tuple[str, ...] = (
    "benchmark_pass_non_cad",
    "blocked_expected_non_cad",
    "not_verified_without_cad_readback",
)

SceneBenchmarkRunner = Callable[..., dict[str, Any]]


SCENE_BETA_BENCHMARKS: tuple[tuple[str, SceneBenchmarkRunner], ...] = (
    ("office", run_office_scene_beta_benchmark),
    ("residential", run_residential_scene_beta_benchmark),
    ("restaurant", run_restaurant_scene_beta_benchmark),
)


def _evidence_count(result: dict[str, Any], key: str) -> int:
    evidence = result.get("evidence_summary", {})
    if not isinstance(evidence, dict):
        return 0
    return int(evidence.get(key, 0) or 0)


def _summary_count(result: dict[str, Any], key: str) -> int:
    summary = result.get("summary", {})
    if not isinstance(summary, dict):
        return 0
    return int(summary.get(key, 0) or 0)


def run_scene_prod_06_regression_gate(*, project_root: Path, output_root: Path) -> dict[str, Any]:
    """Run the selected no-CAD scene beta benchmarks and return a gate summary."""

    root = project_root.resolve()
    output = output_root.resolve()
    output.mkdir(parents=True, exist_ok=True)

    benchmark_results: dict[str, dict[str, Any]] = {}
    for scenario, runner in SCENE_BETA_BENCHMARKS:
        benchmark_results[scenario] = runner(
            project_root=root,
            output_root=output / scenario,
        )

    failed = {
        scenario: result
        for scenario, result in benchmark_results.items()
        if result.get("status") != "pass"
    }
    readback_count = sum(
        _evidence_count(result, "readback_geometry_verified_count")
        for result in benchmark_results.values()
    )
    total_count = sum(_summary_count(result, "total") for result in benchmark_results.values())
    passed_count = sum(_summary_count(result, "passed") for result in benchmark_results.values())
    blocked_expected_count = sum(
        _evidence_count(result, "blocked_expected_non_cad_count")
        for result in benchmark_results.values()
    )
    benchmark_pass_count = sum(
        _evidence_count(result, "benchmark_pass_non_cad_count")
        for result in benchmark_results.values()
    )

    explanation = scene_beta_explanation_status_summary(project_root=root)
    p3 = multi_scene_p3_wave_status_summary(project_root=root)
    doc_present = (root / SCENE_PROD_06_ACCEPTANCE_DOC).is_file()

    status = "pass"
    errors: list[str] = []
    if failed:
        status = "fail"
        errors.append(f"failed scene benchmark(s): {sorted(failed)}")
    if readback_count != 0:
        status = "fail"
        errors.append("scene regression gate must not report readback_geometry_verified")
    if not doc_present:
        status = "fail"
        errors.append(f"missing acceptance doc: {SCENE_PROD_06_ACCEPTANCE_DOC}")
    if explanation.get("scenario_count") != 3:
        status = "fail"
        errors.append("scene beta explanation must cover three scenarios")

    return {
        "package_id": SCENE_PROD_06_PACKAGE_ID,
        "status": status,
        "errors": errors,
        "acceptance_doc": SCENE_PROD_06_ACCEPTANCE_DOC,
        "doc_present": doc_present,
        "scenarios": sorted(benchmark_results),
        "scenario_count": len(benchmark_results),
        "benchmark_total_count": total_count,
        "benchmark_passed_count": passed_count,
        "benchmark_failed_count": total_count - passed_count,
        "benchmark_pass_non_cad_count": benchmark_pass_count,
        "blocked_expected_non_cad_count": blocked_expected_count,
        "readback_geometry_verified_count": readback_count,
        "non_cad_only": readback_count == 0,
        "evidence_boundaries": list(SCENE_PROD_06_EVIDENCE_BOUNDARIES),
        "scene_beta_explanation": explanation,
        "multi_scene_p3_rollup": p3,
        "repo_audit_required": True,
        "repo_audit_command": "scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings",
        "benchmark_results": benchmark_results,
    }


def scene_prod_06_status_summary(*, project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    explanation = scene_beta_explanation_status_summary(project_root=root)
    p3 = multi_scene_p3_wave_status_summary(project_root=root)
    return {
        "package_id": SCENE_PROD_06_PACKAGE_ID,
        "acceptance_doc": SCENE_PROD_06_ACCEPTANCE_DOC,
        "doc_present": (root / SCENE_PROD_06_ACCEPTANCE_DOC).is_file(),
        "scenarios": ["office", "residential", "restaurant"],
        "scenario_count": 3,
        "scene_beta_explanation": explanation,
        "multi_scene_p3_rollup": p3,
        "readback_geometry_verified_count": 0,
        "evidence_boundaries": list(SCENE_PROD_06_EVIDENCE_BOUNDARIES),
        "repo_audit_required": True,
    }


def assert_scene_prod_06_regression_gate_contract(*, project_root: Path) -> None:
    summary = run_scene_prod_06_regression_gate(
        project_root=project_root,
        output_root=project_root / SCENE_PROD_06_DEFAULT_OUTPUT_ROOT,
    )
    if summary["status"] != "pass":
        raise AssertionError(f"SCENE-PROD-06 regression gate failed: {summary['errors']}")
