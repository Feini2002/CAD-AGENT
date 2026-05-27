#!/usr/bin/env python3
"""Build registry writeback batch: composition CAD wave + benchmark mirror rows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.path_safety import find_project_root

ROOT = find_project_root(Path(__file__))


def _rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def _add(requests: list[dict[str, str]], capability_id: str, report_path: str, note: str) -> None:
    requests.append({"capability_id": capability_id, "report_path": report_path, "note": note})


def _from_composition_registry_report(
    requests: list[dict[str, str]],
    report_path: Path,
    manifest_path: Path,
) -> None:
    if not report_path.is_file():
        return
    report = json.loads(report_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
    mirrors_by_case = {
        str(item["benchmark_case_id"]): [str(mid) for mid in item.get("mirror_capability_ids", [])]
        for item in manifest.get("cases", [])
        if isinstance(item, dict)
    }
    for row in report.get("registry_rows", []):
        cap = row.get("registry_capability_id")
        rp = row.get("verification_report_path")
        if not cap or not row.get("geometry_verified") or not rp:
            continue
        rel_rp = _rel(ROOT / str(rp))
        case_id = str(row.get("benchmark_case_id", ""))
        _add(requests, str(cap), rel_rp, f"composition CAD {case_id}")
        for mirror_id in mirrors_by_case.get(case_id, []):
            _add(requests, mirror_id, rel_rp, f"benchmark mirror {case_id}")


OFFICE_OBJECT_BENCHMARK_CASES = {
    "office_desk_default_spec": "desk",
    "office_chair_default_spec": "chair",
    "office_cabinet_default_spec": "cabinet",
    "computer_desk_default_spec": "computer_desk",
    "storage_cabinet_front_clearance": "storage_cabinet",
    "file_cabinet_default_spec": "file_cabinet",
}


def _mirror_office_object_benchmarks(requests: list[dict[str, str]]) -> None:
    registry = json.loads(
        (ROOT / "examples/capability_proof/cad_capability_registry.json").read_text(encoding="utf-8")
    )
    by_object: dict[str, str] = {}
    for row in registry.get("capabilities", []):
        if not isinstance(row, dict):
            continue
        if row.get("claim_level") != "verified":
            continue
        object_type = row.get("object_type")
        evidence = row.get("evidence") or {}
        report = evidence.get("report_path")
        if object_type and report and row.get("capability_id", "").startswith("object."):
            if str(row["capability_id"]).endswith(".draw_object"):
                by_object[str(object_type)] = str(report)

    for case_id, object_type in OFFICE_OBJECT_BENCHMARK_CASES.items():
        report = by_object.get(object_type)
        if not report:
            continue
        cap = f"benchmark.office_alpha_benchmark.{case_id}"
        _add(requests, cap, report, f"office object_spec mirror ({object_type})")


def _static_mirrors(requests: list[dict[str, str]]) -> None:
    """Link benchmark.* rows to existing composition CAD verification reports."""
    pairs = [
        (
            "benchmark.interior_delivery_benchmark.interior_designer_bedroom_bed_rug",
            ROOT
            / "output/validation_runs/capability-lab-vproof-20260527/composition_cad_registry/composition_cad/interior_designer_bedroom_bed_rug/verification_reports/verification_report_001.json",
        ),
        (
            "benchmark.interior_delivery_benchmark.home_designer_dining_table_set",
            ROOT
            / "output/validation_runs/capability-lab-vproof-20260527/composition_cad_registry/composition_cad/home_designer_dining_table_set/verification_reports/verification_report_001.json",
        ),
        (
            "benchmark.interior_delivery_benchmark.office_planner_desk_combo",
            ROOT
            / "output/validation_runs/capability-lab-vproof-20260527/composition_cad_registry/composition_cad/office_planner_desk_combo/verification_reports/verification_report_001.json",
        ),
        (
            "benchmark.office_alpha_benchmark.single_desk_chair_pair",
            ROOT
            / "output/validation_runs/capability-lab-cad-validation-20260527/office_composition_cad/composition_cad/single_desk_chair_pair/verification_reports/verification_report_001.json",
        ),
        (
            "benchmark.office_alpha_benchmark.desk_with_back_cabinet",
            ROOT
            / "output/validation_runs/capability-lab-cad-validation-20260527/office_composition_cad/composition_cad/desk_with_back_cabinet/verification_reports/verification_report_001.json",
        ),
        (
            "benchmark.office_alpha_benchmark.two_workstations_shared_aisle",
            ROOT
            / "output/validation_runs/capability-lab-cad-validation-20260527/office_composition_cad/composition_cad/two_workstations_shared_aisle/verification_reports/verification_report_001.json",
        ),
        (
            "benchmark.office_alpha_benchmark.entry_reception_clearance",
            ROOT
            / "output/validation_runs/capability-lab-cad-validation-20260527/office_composition_cad/composition_cad/entry_reception_clearance/verification_reports/verification_report_001.json",
        ),
        (
            "block.library.controlled_test_block_001",
            ROOT
            / "output/validation_runs/capability-lab-sprint-20260527/baseline_cad_validation/block_alpha_report.json",
        ),
    ]
    for cap_id, report in pairs:
        if report.is_file():
            _add(requests, cap_id, _rel(report), "coverage expansion mirror")
    _mirror_office_object_benchmarks(requests)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wave-dir", type=Path, help="Optional wave root with composition_cad_registry_report.json")
    parser.add_argument(
        "--composition-manifest",
        type=Path,
        default=ROOT / "examples/capability_proof/fitout_composition_cad_registry_manifest.json",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--skip-static", action="store_true")
    args = parser.parse_args()

    requests: list[dict[str, str]] = []
    if args.wave_dir:
        wave = (ROOT / args.wave_dir).resolve()
        _from_composition_registry_report(
            requests,
            wave / "composition_cad_registry_report.json",
            args.composition_manifest,
        )
    if not args.skip_static:
        _static_mirrors(requests)

    seen: set[str] = set()
    deduped: list[dict[str, str]] = []
    for row in requests:
        key = row["capability_id"]
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"requests": deduped}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"request_count": len(deduped), "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
