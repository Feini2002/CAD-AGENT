#!/usr/bin/env python
"""Emit block alpha validation evidence for no-CAD or CAD readback runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.verification.block_alpha_validation import (
    build_block_alpha_no_cad_report,
    build_block_alpha_readback_report,
    default_block_alpha_plan_path,
    write_block_alpha_report,
)
from core.path_safety import resolve_under_project_output, resolve_under_project_root
from core.verification.inspect_dwg import load_execution_summary, snapshot_entities_by_handles


def main() -> int:
    parser = argparse.ArgumentParser(description="Build block alpha validation evidence report.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--no-cad", action="store_true", help="Emit deferred no-CAD evidence only.")
    parser.add_argument("--plan", type=Path, help="insert_block_alpha CAD_PLAN path.")
    parser.add_argument("--execution-summary", type=Path, help="execute_plan JSON with created_handles.")
    parser.add_argument("--connect-cad", action="store_true", help="Read block_reference via active AutoCAD.")
    parser.add_argument("--layer", default="CODEX_PREVIEW")
    args = parser.parse_args()

    root = args.root.resolve()
    output_dir = resolve_under_project_output(root, args.output_dir, label="output_dir")
    plan_path = resolve_under_project_root(root, args.plan or default_block_alpha_plan_path(root), label="plan")
    report_path = output_dir / "block_alpha_report.json"

    if args.no_cad:
        report = build_block_alpha_no_cad_report(plan_path=plan_path)
        write_block_alpha_report(report_path, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    execution_summary, created_handles = load_execution_summary(args.execution_summary)
    entities: list[dict[str, object]] = []
    if args.connect_cad:
        from core.cad_io.autocad_com import AutoCADComDriver

        driver = AutoCADComDriver(connect_existing_only=True)
        if created_handles:
            entities = snapshot_entities_by_handles(driver, created_handles, layer=args.layer)
        else:
            entities = []

    screenshot = output_dir / "block-alpha-window.png"
    report = build_block_alpha_readback_report(
        plan_path=plan_path,
        entities=entities,
        created_handles=created_handles,
        screenshot_path=screenshot if screenshot.exists() else None,
    )
    write_block_alpha_report(report_path, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") in {"geometry_verified", "deferred"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
