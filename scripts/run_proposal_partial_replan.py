#!/usr/bin/env python3
"""Recompute CAD_PLAN after local placement edits (BETA-PROPOSAL-04)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.proposal_engine.partial_replan import recompute_cad_plans_from_pipeline_artifacts  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Partially replan CAD_PLAN from pipeline artifacts.")
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        required=True,
        help="Directory with placements.json, layout_proposal.json, design_proposal.json, etc.",
    )
    parser.add_argument("--confirmation", type=Path, default=None)
    parser.add_argument(
        "--offset-json",
        type=Path,
        default=None,
        help='JSON object mapping object_spec_id to [dx, dy] or [dx, dy, dz], e.g. {"object-desk-001":[200,0]}',
    )
    args = parser.parse_args()

    offsets = None
    if args.offset_json:
        offsets = json.loads(args.offset_json.read_text(encoding="utf-8"))

    report = recompute_cad_plans_from_pipeline_artifacts(
        args.artifact_dir,
        placement_offsets=offsets,
        confirmation_path=args.confirmation,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
