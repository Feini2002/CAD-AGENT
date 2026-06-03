#!/usr/bin/env python3
"""Find and reuse a system-library asset in the current CAD drawing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.assets.system_asset_reuse import (  # noqa: E402
    apply_system_asset_reuse_workflow,
    build_system_asset_reuse_plan,
    build_system_asset_reuse_workflow,
    reuse_system_asset,
)


SUCCESS_STATUSES = {"ready", "asset_reused", "asset_reuse_workflow_completed"}


def _base_point(value: str) -> list[float] | None:
    if not value:
        return None
    parts = [part.strip() for part in value.split(",") if part.strip()]
    if len(parts) not in (2, 3):
        raise argparse.ArgumentTypeError("--base-point expects x,y or x,y,z")
    point = [float(part) for part in parts]
    if len(point) == 2:
        point.append(0.0)
    return point


def main() -> int:
    parser = argparse.ArgumentParser(description="Reuse a system-library CAD asset in the current drawing.")
    parser.add_argument("query", nargs="*", help="Natural-language request, for example: 调用线型表资产放到当前图")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--asset-id", action="append", default=[], help="Use one or more specific asset ids instead of semantic matching")
    parser.add_argument("--base-point", type=_base_point, default=None, help="Insertion base point as x,y or x,y,z")
    parser.add_argument("--target-layer", default="CODEX_PREVIEW")
    parser.add_argument("--workflow", action="store_true", help="Plan or apply a multi-asset reuse workflow")
    parser.add_argument("--plan-only", action="store_true", help="Only resolve the reusable asset; do not connect to CAD")
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON report path")
    args = parser.parse_args()

    query = " ".join(args.query).strip()
    asset_ids = [asset_id for asset_id in args.asset_id if asset_id]
    if not query and not asset_ids:
        parser.error("query text or --asset-id is required")

    if not args.workflow and len(asset_ids) > 1:
        parser.error("multiple --asset-id values require --workflow")

    if args.workflow and args.plan_only:
        report = build_system_asset_reuse_workflow(
            query,
            project_root=args.project_root,
            asset_ids=asset_ids or None,
            base_point=args.base_point,
            target_layer=args.target_layer,
        )
    elif args.workflow:
        from core.cad_io.autocad_com import AutoCADComDriver

        driver = AutoCADComDriver(connect_existing_only=True)
        workflow = build_system_asset_reuse_workflow(
            query,
            project_root=args.project_root,
            asset_ids=asset_ids or None,
            base_point=args.base_point,
            target_layer=args.target_layer,
        )
        report = apply_system_asset_reuse_workflow(workflow, driver=driver)
    elif args.plan_only:
        report: dict[str, Any] = build_system_asset_reuse_plan(
            query,
            project_root=args.project_root,
            asset_id=asset_ids[0] if asset_ids else None,
            base_point=args.base_point,
            target_layer=args.target_layer,
        )
    else:
        from core.cad_io.autocad_com import AutoCADComDriver

        driver = AutoCADComDriver(connect_existing_only=True)
        report = reuse_system_asset(
            query,
            project_root=args.project_root,
            asset_id=asset_ids[0] if asset_ids else None,
            base_point=args.base_point,
            target_layer=args.target_layer,
            driver=driver,
        )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if report.get("status") in SUCCESS_STATUSES else 1


if __name__ == "__main__":
    raise SystemExit(main())
