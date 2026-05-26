#!/usr/bin/env python3
"""Run BETA-CAD-BLOCK parent-package evidence rollup (non-CAD)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.verification.cad_beta_evidence_rollup import run_cad_beta_evidence_rollup  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Roll up BETA-CAD-BLOCK 01–05 non-CAD evidence.")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("output/test_artifacts/cad_beta_evidence/beta_cad_block_05"),
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    report = run_cad_beta_evidence_rollup(root, output_root=args.output_root.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
