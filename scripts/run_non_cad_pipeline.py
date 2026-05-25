#!/usr/bin/env python
"""Run the non-CAD Core pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.workflows.non_cad_pipeline import run_non_cad_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a non-CAD Core workflow.")
    parser.add_argument("workflow", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("output/test_artifacts/non_cad_pipeline/manual"))
    args = parser.parse_args()

    result = run_non_cad_pipeline(args.workflow, output_dir=args.output_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
