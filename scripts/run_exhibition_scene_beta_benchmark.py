#!/usr/bin/env python3
"""Run exhibition scene beta benchmark (BETA-SCENE-04)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.agents.exhibition_scene_beta import run_exhibition_scene_beta_benchmark  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run BETA-SCENE-04 exhibition scene beta benchmark.")
    parser.add_argument(
        "--output",
        "--output-root",
        dest="output",
        type=Path,
        default=Path("output/test_artifacts/benchmarks/beta_scene_04_exhibition"),
    )
    parser.add_argument("--suite", type=Path, default=None)
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    try:
        result = run_exhibition_scene_beta_benchmark(
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
