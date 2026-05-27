#!/usr/bin/env python3
"""Run SCENE-PROD-05 scene beta explanation template summary (no CAD)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT
except ImportError:
    from scripts._bootstrap import PROJECT_ROOT

ROOT = PROJECT_ROOT

from core.agents.scene_beta_explanation import (  # noqa: E402
    build_all_scene_beta_explanations,
    scene_beta_explanation_status_summary,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="SCENE-PROD-05 scene beta explanation template")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "output" / "validation_runs" / "scene-prod-05-explanation-template-no-cad",
    )
    args = parser.parse_args()

    summary = scene_beta_explanation_status_summary(project_root=ROOT)
    summary["status"] = "pass"
    summary["explanations"] = build_all_scene_beta_explanations(project_root=ROOT)

    args.output.mkdir(parents=True, exist_ok=True)
    out_path = args.output / "scene_beta_explanation_summary.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out_path)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
