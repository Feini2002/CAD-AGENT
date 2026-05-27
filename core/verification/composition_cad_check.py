"""Execute interior delivery composition CAD_PLAN artifacts in AutoCAD."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.execution.batch_plan_runner import execute_plan_batch
from core.path_safety import find_project_root, resolve_under_project_output

DEFAULT_CASE_ORDER = [
    "interior_designer_bedroom_bed_rug",
    "home_designer_dining_table_set",
    "office_planner_desk_combo",
]

# Backward-compatible alias for existing imports.
CASE_ORDER = DEFAULT_CASE_ORDER


def build_case_offsets(
    case_ids: list[str] | None = None,
    *,
    start_x: float | int = 12000,
    start_y: float | int = 0,
    spacing_x: float | int = 4200,
) -> dict[str, list[float | int]]:
    ordered = case_ids or list(DEFAULT_CASE_ORDER)
    if not ordered:
        raise ValueError("case_ids must be a non-empty list when provided.")
    return {
        case_id: [start_x + index * spacing_x, start_y, 0]
        for index, case_id in enumerate(ordered)
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
    case_ids: list[str] | None = None,
    case_offsets: dict[str, list[float | int]] | None = None,
    project_root: Path | None = None,
    driver: Any | None = None,
) -> dict[str, Any]:
    root = project_root or find_project_root(Path(__file__))
    benchmark_output_root = resolve_under_project_output(
        root,
        benchmark_output_root,
        label="benchmark_output_root",
    )
    output_dir = resolve_under_project_output(root, output_dir, label="output_dir")

    if driver is None:
        from core.cad_io.autocad_com import AutoCADComDriver

        driver = AutoCADComDriver(connect_existing_only=True)

    case_results: list[dict[str, Any]] = []
    ordered_case_ids = case_ids or list(DEFAULT_CASE_ORDER)
    offsets = case_offsets or build_case_offsets(ordered_case_ids)
    for case_id in ordered_case_ids:
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
