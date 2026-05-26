#!/usr/bin/env python3
"""Run project sample benchmark suite (BETA-PROJECT-SAMPLE-04)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.project_samples.benchmark import run_project_sample_benchmark  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run project sample benchmark (pass + blocked).")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("output/test_artifacts/benchmarks/beta_project_sample_04"),
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    result = run_project_sample_benchmark(project_root=root, output_root=args.output_root.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
