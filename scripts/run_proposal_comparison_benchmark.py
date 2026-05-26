#!/usr/bin/env python3
"""Run proposal comparison benchmark suite (BETA-PROPOSAL-02)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.proposal_engine.benchmark import run_proposal_comparison_benchmark  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run proposal comparison summary benchmark.")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("output/test_artifacts/benchmarks/beta_proposal_02"),
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    result = run_proposal_comparison_benchmark(
        project_root=root,
        output_root=args.output_root.resolve(),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
