#!/usr/bin/env python3
"""Capture and review AutoCAD visual evidence for table C writeback gating."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.verification.visual_cad_review import run_visual_cad_review  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run table C visual CAD review.")
    parser.add_argument("--output-dir", type=Path, default=Path("output/validation_runs/table-c-evidence-gate"))
    parser.add_argument("--execution-summary", type=Path, required=True)
    parser.add_argument("--readback-report", type=Path, required=True)
    parser.add_argument("--screenshot", "--screenshot-path", dest="screenshot_path", type=Path)
    parser.add_argument("--capture", action="store_true", help="Capture AutoCAD window before reviewing.")
    args = parser.parse_args()

    report = run_visual_cad_review(
        PROJECT_ROOT,
        output_dir=args.output_dir,
        execution_summary_path=args.execution_summary,
        readback_report_path=args.readback_report,
        screenshot_path=args.screenshot_path,
        capture=args.capture,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
