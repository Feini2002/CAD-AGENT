"""Interior delivery composition CAD + registry mapping (V-PROOF-43)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.benchmarks.runner import run_benchmark_suite
from core.plan_engine.validate_plan import load_json
from core.verification.composition_cad_check import build_case_offsets, run_composition_cad_check

DEFAULT_MANIFEST = Path("examples") / "capability_proof" / "composition_cad_registry_manifest.json"


def load_composition_cad_registry_manifest(path: Path) -> dict[str, Any]:
    manifest = load_json(path)
    if manifest.get("manifest_id") != "composition_cad_registry":
        raise ValueError("composition_cad_registry manifest_id must be 'composition_cad_registry'.")
    return manifest


def run_composition_cad_registry(
    *,
    root: Path,
    output_dir: Path,
    manifest_path: Path | None = None,
    start_x: float = 110000,
    start_y: float = 65000,
    spacing_x: float = 4200,
    skip_benchmark: bool = False,
) -> dict[str, Any]:
    manifest_path = manifest_path or (root / DEFAULT_MANIFEST)
    manifest = load_composition_cad_registry_manifest(manifest_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    benchmark_subdir = str(manifest.get("benchmark_output_subdir", "benchmark_artifacts"))
    benchmark_root = output_dir / benchmark_subdir

    if not skip_benchmark:
        suite_path = root / str(manifest["benchmark_suite_path"])
        benchmark_result = run_benchmark_suite(suite_path, output_root=benchmark_root)
        if benchmark_result.get("status") != "pass":
            return {
                "version": "0.1",
                "suite_id": "composition_cad_registry",
                "status": "fail",
                "failure_category": "benchmark_failed",
                "benchmark_result": benchmark_result,
            }

    manifest_cases = manifest.get("cases", [])
    case_ids = [str(item["benchmark_case_id"]) for item in manifest_cases if item.get("benchmark_case_id")]
    if not case_ids:
        raise ValueError("composition_cad_registry manifest requires at least one case with benchmark_case_id.")

    composition_dir = output_dir / "composition_cad"
    cad_report = run_composition_cad_check(
        benchmark_output_root=benchmark_root,
        output_dir=composition_dir,
        case_ids=case_ids,
        case_offsets=build_case_offsets(case_ids, start_x=start_x, start_y=start_y, spacing_x=spacing_x),
        project_root=root,
    )

    registry_rows: list[dict[str, Any]] = []
    cases_by_id = {case["case_id"]: case for case in cad_report.get("cases", []) if isinstance(case, dict)}
    for item in manifest.get("cases", []):
        benchmark_case_id = str(item["benchmark_case_id"])
        capability_id = str(item.get("registry_capability_id", ""))
        case_result = cases_by_id.get(benchmark_case_id, {})
        verified = case_result.get("status") == "geometry_verified"
        report_path = ""
        if verified:
            report_path = str(
                composition_dir
                / benchmark_case_id
                / "verification_reports"
                / "verification_report_001.json"
            )
        registry_rows.append(
            {
                "benchmark_case_id": benchmark_case_id,
                "registry_capability_id": capability_id,
                "geometry_verified": verified,
                "verification_report_path": report_path,
                "created_handle_count": case_result.get("created_handle_count", 0),
            }
        )

    verified_count = sum(1 for row in registry_rows if row.get("geometry_verified"))
    report = {
        "version": "0.1",
        "suite_id": "composition_cad_registry",
        "status": cad_report.get("status", "fail"),
        "geometry_verified": verified_count == len(registry_rows) and verified_count > 0,
        "composition_cad_check_report_path": str(composition_dir / "composition_cad_check_report.json"),
        "registry_rows": registry_rows,
        "composition_cad_check": cad_report,
    }
    (output_dir / "composition_cad_registry_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report
