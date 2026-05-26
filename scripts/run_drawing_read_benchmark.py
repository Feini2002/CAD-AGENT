#!/usr/bin/env python3
"""Run drawing-read benchmark suite (BETA-DRAWING-READ-05)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.drawing_analysis.drawing_read_benchmark import (  # noqa: E402
    default_drawing_read_benchmark_path,
    run_drawing_read_benchmark,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run drawing-read benchmark suite.")
    parser.add_argument("--output", type=Path, default=Path("output/test_artifacts/benchmarks/drawing_read_05"))
    parser.add_argument("--suite", type=Path, default=None)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    try:
        result = run_drawing_read_benchmark(
            project_root=project_root,
            output_root=args.output.resolve(),
            suite_path=args.suite.resolve() if args.suite else None,
        )
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
