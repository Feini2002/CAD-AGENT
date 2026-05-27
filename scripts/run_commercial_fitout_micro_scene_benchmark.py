"""Run commercial_fitout micro-scene benchmark suite (C-CFIT-04)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.benchmarks.runner import run_benchmark_suite


DEFAULT_SUITE = PROJECT_ROOT / "examples" / "benchmarks" / "commercial_fitout_micro_scene_benchmark.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "output" / "test_artifacts" / "benchmarks" / "commercial-fitout-micro-scene"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run commercial_fitout micro-scene benchmark suite.")
    parser.add_argument("--suite", type=Path, default=DEFAULT_SUITE)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    result = run_benchmark_suite(args.suite, output_root=args.output_root)
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
