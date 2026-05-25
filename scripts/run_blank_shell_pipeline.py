#!/usr/bin/env python
"""Run the blank-shell Core pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.workflows.blank_shell_pipeline import run_blank_shell_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a blank-shell Core workflow.")
    parser.add_argument("workflow", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("output/test_artifacts/blank_shell_pipeline/manual"))
    args = parser.parse_args()

    result = run_blank_shell_pipeline(args.workflow, output_dir=args.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
