#!/usr/bin/env python3
"""Create or update a system-library asset sedimentation contract."""

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

from core.assets.system_asset_sedimentation import sediment_system_asset, verify_system_asset_package  # noqa: E402


def _dimensions(args: argparse.Namespace) -> dict[str, Any]:
    dimensions: dict[str, Any] = {}
    if args.width_mm is not None:
        dimensions["width_mm"] = float(args.width_mm)
    if args.depth_mm is not None:
        dimensions["depth_mm"] = float(args.depth_mm)
    if args.height_mm is not None:
        dimensions["height_mm"] = float(args.height_mm)
    return dimensions


def _source(args: argparse.Namespace) -> dict[str, Any]:
    source: dict[str, Any] = {"type": args.source_type}
    if args.source_handle:
        source["handles"] = [str(handle) for handle in args.source_handle]
    if args.active_document:
        source["activeDocument"] = args.active_document
    return source


def _expose_governance_summary(report: dict[str, Any]) -> dict[str, Any]:
    governance = report.get("libraryGovernance")
    if isinstance(governance, dict):
        report["assetGovernanceDecision"] = governance.get("decision", "")
        hardening = governance.get("polishHardeningDecision")
        if isinstance(hardening, dict):
            report["polishHardeningDecision"] = hardening
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Sediment a reusable CAD system asset contract.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--asset-id", default="")
    parser.add_argument("--name", default="")
    parser.add_argument("--category", required=True, help="Dotted category, for example furniture.seating.sofas")
    parser.add_argument("--alias", action="append", default=[])
    parser.add_argument("--use-when", action="append", default=[])
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--scenario-tag", action="append", default=[])
    parser.add_argument("--constraint", action="append", default=[])
    parser.add_argument("--evidence-ref", action="append", default=[])
    parser.add_argument("--source-handle", action="append", default=[])
    parser.add_argument("--included-handle", action="append", default=[])
    parser.add_argument("--excluded-handle", action="append", default=[])
    parser.add_argument("--source-type", default="manual_metadata")
    parser.add_argument("--source-boundary-mode", default="")
    parser.add_argument("--active-document", default="")
    parser.add_argument("--block-name", default="")
    parser.add_argument("--asset-kind", default="")
    parser.add_argument("--export-mode", default="")
    parser.add_argument("--native-library-stem", default="")
    parser.add_argument("--status", default="candidate")
    parser.add_argument("--conflict-policy", default="update_existing", choices=["update_existing", "new_variant", "reject"])
    parser.add_argument("--feedback-ref", action="append", default=[])
    parser.add_argument("--promotion-ref", action="append", default=[])
    parser.add_argument("--failure-reason", default="")
    parser.add_argument("--width-mm", type=float)
    parser.add_argument("--depth-mm", type=float)
    parser.add_argument("--height-mm", type=float)
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify the repository-side package contract; this does not write CAD or prove native geometry reuse.",
    )
    args = parser.parse_args()

    if args.verify:
        try:
            report = verify_system_asset_package(
                project_root=args.project_root,
                category=args.category,
                native_library_stem=args.native_library_stem or None,
                asset_id=args.asset_id or None,
            )
        except ValueError as exc:
            report = {"status": "fail", "reason": str(exc), "wroteCad": False, "savedDwg": False}
    else:
        if not args.asset_id or not args.name:
            parser.error("--asset-id and --name are required unless --verify is used")
        try:
            report = sediment_system_asset(
                project_root=args.project_root,
                asset_id=args.asset_id,
                name=args.name,
                category=args.category,
                aliases=args.alias,
                use_when=args.use_when,
                tags=args.tag,
                scenario_tags=args.scenario_tag,
                constraints=args.constraint,
                dimensions=_dimensions(args),
                block_name=args.block_name,
                evidence_refs=args.evidence_ref,
                source=_source(args),
                asset_kind=args.asset_kind or None,
                export_mode=args.export_mode or None,
                source_boundary_mode=args.source_boundary_mode or None,
                included_handles=args.included_handle,
                excluded_handles=args.excluded_handle,
                status=args.status,
                feedback_refs=args.feedback_ref,
                promotion_refs=args.promotion_ref,
                failure_reason=args.failure_reason,
                conflict_policy=args.conflict_policy,
                native_library_stem=args.native_library_stem or None,
            )
            report = _expose_governance_summary(report)
        except ValueError as exc:
            report = {"status": "fail", "reason": str(exc), "wroteCad": False, "savedDwg": False}
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
