#!/usr/bin/env python3
"""Run drawing standard beta suite (BETA-CAD-BLOCK-04)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.verification.drawing_standard_beta_suite import (  # noqa: E402
    default_suite_path,
    run_drawing_standard_beta_suite,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run drawing standard beta suite (schema + dry-run).")
    parser.add_argument("--suite", type=Path, default=None)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("output/test_artifacts/drawing_standard_beta/beta_cad_block_04"),
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    suite_path = args.suite or default_suite_path(root)
    result = run_drawing_standard_beta_suite(suite_path, output_root=args.output_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
