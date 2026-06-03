#!/usr/bin/env python3
"""Find a sofa block visually, then annotate its bbox dimensions in CODEX_PREVIEW."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.cad_io.autocad_com import AutoCADComDriver  # noqa: E402
from core.visual_retrieval import (  # noqa: E402
    build_bbox_dimension_plan,
    execute_dimension_annotation_plan,
    retrieve_visual_blocks_from_driver,
)


DEFAULT_OUTPUT = (
    PROJECT_ROOT
    / "output"
    / "validation_runs"
    / "visual-cad-asset-retrieval"
    / "sofa_dimension_annotation_report.json"
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Annotate the visually retrieved sofa block dimensions.")
    parser.add_argument("--query", default="根据截图找到三人沙发并进行尺寸标注")
    parser.add_argument("--visual-hint", default="三人沙发 俯视 平面 三坐垫 圆角扶手")
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true", help="Build the dimension plan without writing CAD entities.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        driver = AutoCADComDriver(connect_existing_only=True)
        retrieval = retrieve_visual_blocks_from_driver(
            driver,
            query=args.query,
            visual_hint=args.visual_hint or None,
            top_k=args.top_k,
        )
        if retrieval.best_match is None:
            payload = {
                "status": "not_found",
                "message": "No sofa-like block candidate was found in the active DWG.",
                "retrieval": retrieval.to_dict(),
            }
            _write_report(args.output, payload)
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 1

        dimension_plan = build_bbox_dimension_plan(retrieval.best_match.candidate)
        payload: dict[str, object] = {
            "status": "dry_run_pass" if args.dry_run else "planned",
            "mode": "dry_run" if args.dry_run else "execute",
            "retrieval": retrieval.to_dict(),
            "structured_intent": dimension_plan.to_dict(),
            "dry_run": {
                "status": "pass",
                "dimension_count": len(dimension_plan.dimensions),
                "target_handle": dimension_plan.target_handle,
                "target_block_name": dimension_plan.target_block_name,
                "target_size": dimension_plan.target_size,
                "output_layer": dimension_plan.output_layer,
            },
        }

        if not args.dry_run:
            execution = execute_dimension_annotation_plan(driver, dimension_plan)
            zoom = None
            if hasattr(driver, "zoom_to_bbox"):
                zoom = driver.zoom_to_bbox(dimension_plan.view_bbox, padding_ratio=0.03)
            payload["status"] = "pass" if execution.get("status") == "pass" else "needs_review"
            payload["execution"] = execution
            payload["zoom"] = zoom
            payload["evidence_boundary"] = {
                "visual": "the screenshot-like sofa request selects the candidate",
                "cad": "dimension values come from the active DWG bbox readback",
                "not_claimed": "the source screenshot itself is not treated as a true size measurement",
            }

        _write_report(args.output, payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if str(payload.get("status")) in {"dry_run_pass", "pass"} else 1
    except Exception as exc:
        payload = {
            "status": "blocked",
            "failure_category": "sofa_dimension_annotation_failed",
            "message": str(exc),
            "output": str(args.output),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1


def _write_report(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
