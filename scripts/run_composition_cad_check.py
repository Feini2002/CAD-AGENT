#!/usr/bin/env python
"""Execute interior delivery composition CAD_PLAN artifacts in AutoCAD."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from _bootstrap import PROJECT_ROOT
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT

from core.execution.batch_plan_runner import execute_plan_batch
from core.path_safety import resolve_under_project_output


DEFAULT_CASE_OFFSETS = {
    "interior_designer_bedroom_bed_rug": [12000, 0, 0],
    "home_designer_dining_table_set": [16200, 0, 0],
    "office_planner_desk_combo": [20400, 0, 0],
}

CASE_ORDER = [
    "interior_designer_bedroom_bed_rug",
    "home_designer_dining_table_set",
    "office_planner_desk_combo",
]


def build_case_offsets(
    *,
    start_x: float | int = 12000,
    start_y: float | int = 0,
    spacing_x: float | int = 4200,
) -> dict[str, list[float | int]]:
    return {
        case_id: [start_x + index * spacing_x, start_y, 0]
        for index, case_id in enumerate(CASE_ORDER)
    }


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _case_plan_paths(case_dir: Path) -> list[Path]:
    plan_dir = case_dir / "cad_plan_items"
    if not plan_dir.exists():
        raise ValueError(f"Missing cad_plan_items directory: {plan_dir}")
    plans = sorted(plan_dir.glob("cad_plan_*.json"))
    if not plans:
        raise ValueError(f"No cad_plan_*.json files found in {plan_dir}")
    return plans


def run_composition_cad_check(
    *,
    benchmark_output_root: Path,
    output_dir: Path,
    case_offsets: dict[str, list[float | int]] | None = None,
) -> dict[str, Any]:
    benchmark_output_root = resolve_under_project_output(
        PROJECT_ROOT,
        benchmark_output_root,
        label="benchmark_output_root",
    )
    output_dir = resolve_under_project_output(PROJECT_ROOT, output_dir, label="output_dir")

    from core.cad_io.autocad_com import AutoCADComDriver

    driver = AutoCADComDriver(connect_existing_only=True)
    case_results: list[dict[str, Any]] = []
    offsets = case_offsets or DEFAULT_CASE_OFFSETS
    for case_id in CASE_ORDER:
        offset = offsets[case_id]
        case_dir = benchmark_output_root / case_id
        if not case_dir.exists():
            raise ValueError(f"Missing benchmark case output directory: {case_dir}")
        result = execute_plan_batch(
            _case_plan_paths(case_dir),
            output_dir=output_dir / case_id,
            driver=driver,
            offset=offset,
        )
        case_results.append({"case_id": case_id, "offset": offset, **result})

    failed = [case for case in case_results if case["status"] != "geometry_verified"]
    report = {
        "version": "0.1",
        "status": "geometry_verified" if not failed else "failed",
        "benchmark_output_root": str(benchmark_output_root),
        "output_dir": str(output_dir),
        "case_count": len(case_results),
        "verified_case_count": len(case_results) - len(failed),
        "failed_case_ids": [case["case_id"] for case in failed],
        "created_handle_count": sum(int(case.get("created_handle_count", 0)) for case in case_results),
        "cases": case_results,
        "safety": {
            "layer": "CODEX_PREVIEW",
            "saved_dwg": False,
            "deleted_entities": False,
            "modified_formal_layers": False,
        },
    }
    _write_json(output_dir / "composition_cad_check_report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute composition benchmark CAD plans in AutoCAD.")
    parser.add_argument(
        "--benchmark-output-root",
        type=Path,
        default=PROJECT_ROOT / "output" / "test_artifacts" / "benchmarks" / "interior_delivery_manual",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "output" / "validation_runs" / "interior-composition-cad",
    )
    parser.add_argument(
        "--start-x",
        type=float,
        default=12000,
        help="World X coordinate for the first composition case. Use a new value to avoid old preview entities.",
    )
    parser.add_argument(
        "--spacing-x",
        type=float,
        default=4200,
        help="Horizontal spacing between composition cases.",
    )
    parser.add_argument(
        "--start-y",
        type=float,
        default=0,
        help="World Y coordinate for all composition cases. Use a high value to avoid existing DWG geometry.",
    )
    args = parser.parse_args()

    report = run_composition_cad_check(
        benchmark_output_root=args.benchmark_output_root,
        output_dir=args.output_dir,
        case_offsets=build_case_offsets(start_x=args.start_x, start_y=args.start_y, spacing_x=args.spacing_x),
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "geometry_verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
