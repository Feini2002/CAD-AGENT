"""Run commercial_fitout micro-scene benchmark suite (C-CFIT-04)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
