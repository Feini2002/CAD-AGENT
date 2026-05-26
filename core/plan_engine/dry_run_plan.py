#!/usr/bin/env python
"""Preview what a first-version CAD_PLAN would draw."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from core.plan_engine.dry_run_report import create_dry_run_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run a CAD_PLAN JSON file.")
    parser.add_argument("plan", type=Path, help="Path to CAD_PLAN JSON.")
    args = parser.parse_args()

    with args.plan.open("r", encoding="utf-8") as file:
        plan = json.load(file)

    report = create_dry_run_report(plan)
    print(report.get("human_summary", ""))
    if report.get("status") != "valid":
        for error in report.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

