#!/usr/bin/env python3
"""Evaluate whether a CAD asset candidate may be promoted."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.assets import evaluate_asset_promotion  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CAD asset promotion gate.")
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument(
        "--target-status",
        choices=["candidate", "case_verified", "system_verified"],
        default=None,
    )
    parser.add_argument("--fail-on-blocked", action="store_true")
    args = parser.parse_args()

    report = evaluate_asset_promotion(
        args.candidate,
        project_root=PROJECT_ROOT,
        target_status=args.target_status,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.fail_on_blocked and report.get("status") != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
