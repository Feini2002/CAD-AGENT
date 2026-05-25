"""Batch execution helpers for multiple safe preview CAD_PLAN files."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from core.execution.execute_plan import CadPreviewDriver, execute_plan_file
from core.verification.inspect_dwg import snapshot_entities_by_handles
from core.verification.verification_report import build_verification_report, summarize_verification_reports


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def translate_plan(plan: dict[str, Any], *, offset: list[float | int]) -> dict[str, Any]:
    translated = copy.deepcopy(plan)
    placement = translated.get("placement", {})
    if placement.get("mode") != "absolute":
        raise ValueError("Only absolute CAD_PLAN placement can be translated.")
    base = placement.get("base_point")
    if not isinstance(base, list) or len(base) not in {2, 3}:
        raise ValueError("CAD_PLAN placement.base_point must contain 2 or 3 coordinates.")
    if len(offset) == 2:
        offset = [offset[0], offset[1], 0]
    if len(base) == 2:
        base = [base[0], base[1], 0]
    placement["base_point"] = [base[0] + offset[0], base[1] + offset[1], base[2] + offset[2]]
    return translated


def execute_plan_batch(
    plan_paths: list[Path],
    *,
    output_dir: Path,
    driver: CadPreviewDriver,
    offset: list[float | int] | None = None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    offset = offset or [0, 0, 0]
    items: list[dict[str, Any]] = []
    verification_reports: list[dict[str, Any]] = []
    all_handles: list[str] = []

    for index, plan_path in enumerate(plan_paths, start=1):
        source_plan = json.loads(plan_path.read_text(encoding="utf-8"))
        if not isinstance(source_plan, dict):
            raise ValueError(f"CAD_PLAN must be a JSON object: {plan_path}")
        translated_plan = translate_plan(source_plan, offset=offset)
        translated_plan_path = output_dir / "translated_plans" / f"cad_plan_{index:03d}.json"
        execution_summary_path = output_dir / "execution_summaries" / f"execution_summary_{index:03d}.json"
        verification_report_path = output_dir / "verification_reports" / f"verification_report_{index:03d}.json"

        _write_json(translated_plan_path, translated_plan)
        execution_summary = execute_plan_file(translated_plan_path, driver=driver)
        _write_json(execution_summary_path, execution_summary)
        created_handles = [str(handle) for handle in execution_summary.get("created_handles", [])]
        all_handles.extend(created_handles)

        entities = snapshot_entities_by_handles(driver, created_handles, layer=translated_plan["drawing"]["layer"])
        verification_report = build_verification_report(
            plan_path=translated_plan_path,
            entities=entities,
            execution_summary=execution_summary,
            created_handles=created_handles,
        )
        _write_json(verification_report_path, verification_report)
        verification_reports.append(verification_report)
        items.append(
            {
                "source_plan_path": str(plan_path),
                "translated_plan_path": str(translated_plan_path),
                "execution_summary_path": str(execution_summary_path),
                "verification_report_path": str(verification_report_path),
                "execution_summary": execution_summary,
                "verification_report": verification_report,
            }
        )

    summary = summarize_verification_reports(verification_reports)
    status = "geometry_verified" if summary["all_geometry_verified"] else "failed"
    result = {
        "version": "0.1",
        "status": status,
        "output_dir": str(output_dir),
        "plan_count": len(plan_paths),
        "created_handles": all_handles,
        "created_handle_count": len(all_handles),
        "summary": summary,
        "items": items,
    }
    _write_json(output_dir / "batch_execution_report.json", result)
    return result
