#!/usr/bin/env python3
"""Run SCENE-PROD-06 multi-scene regression gate (no CAD)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT
except ImportError:
    from scripts._bootstrap import PROJECT_ROOT

from core.agents.scene_regression_gate import (  # noqa: E402
    SCENE_PROD_06_DEFAULT_OUTPUT_ROOT,
    run_scene_prod_06_regression_gate,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="SCENE-PROD-06 multi-scene regression gate")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / SCENE_PROD_06_DEFAULT_OUTPUT_ROOT,
    )
    args = parser.parse_args()

    summary = run_scene_prod_06_regression_gate(
        project_root=PROJECT_ROOT,
        output_root=args.output,
    )
    args.output.mkdir(parents=True, exist_ok=True)
    out_path = args.output / "scene_regression_gate_summary.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out_path)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
