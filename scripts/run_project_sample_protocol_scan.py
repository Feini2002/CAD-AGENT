#!/usr/bin/env python3
"""Scan projects/ for de-identified sample protocol compliance (BETA-PROJECT-SAMPLE-01)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.project_samples.protocol import scan_projects_root  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan projects/ sample protocol compliance.")
    parser.add_argument(
        "--projects-root",
        type=Path,
        default=None,
        help="Path to projects/ (default: <repo>/projects)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/test_artifacts/project_samples/beta_project_sample_01/protocol_scan.json"),
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    projects_root = (args.projects_root or root / "projects").resolve()
    report = scan_projects_root(projects_root)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
