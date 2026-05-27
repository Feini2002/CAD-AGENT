#!/usr/bin/env python3
"""Run block alpha beta suite (BETA-CAD-BLOCK-01) and write summary JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.verification.block_alpha_beta_suite import (  # noqa: E402
    default_suite_path,
    run_block_alpha_beta_suite,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run block alpha beta suite (no-CAD validate + dry-run).")
    parser.add_argument(
        "--suite",
        type=Path,
        default=None,
        help="Path to block_alpha_beta_suite.json (default: examples/plans/block_alpha_beta_suite.json)",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("output/test_artifacts/block_alpha_beta/beta_cad_block_01"),
        help="Directory for per-case artifacts and block_alpha_beta_summary.json",
    )
    parser.add_argument(
        "--connect-cad",
        action="store_true",
        help="Execute each beta case in active AutoCAD CODEX_PREVIEW and verify block_reference readback.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    suite_path = args.suite or default_suite_path(root)
    result = run_block_alpha_beta_suite(
        suite_path,
        output_root=args.output_root,
        driver_factory=_default_driver_factory if args.connect_cad else None,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("status") == "pass" else 1


def _default_driver_factory() -> object:
    from core.cad_io.autocad_com import AutoCADComDriver

    return AutoCADComDriver(connect_existing_only=True)


if __name__ == "__main__":
    sys.exit(main())
