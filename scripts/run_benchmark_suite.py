"""Compatibility wrapper for running Core benchmark suites."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


try:
    from _bootstrap import PROJECT_ROOT
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT

from core.benchmarks.runner import run_benchmark_suite


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a non-CAD Core benchmark suite.")
    parser.add_argument("suite", type=Path)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=PROJECT_ROOT / "output" / "test_artifacts" / "benchmarks" / "manual",
    )
    args = parser.parse_args()

    suite_path = args.suite if args.suite.is_absolute() else PROJECT_ROOT / args.suite
    output_root = args.output_root if args.output_root.is_absolute() else PROJECT_ROOT / args.output_root
    result = run_benchmark_suite(suite_path, output_root=output_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
