#!/usr/bin/env python3
"""Run BETA-SCENE-04 exhibition + healthcare scene beta benchmarks and write rollup evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.agents.exhibition_scene_beta import run_exhibition_scene_beta_benchmark  # noqa: E402
from core.agents.healthcare_scene_beta import run_healthcare_scene_beta_benchmark  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run BETA-SCENE-04 exhibition + healthcare benchmarks.")
    parser.add_argument(
        "--output",
        "--output-root",
        dest="output",
        type=Path,
        default=Path("output/validation_runs/beta-scene-04-20260528"),
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    output_root = args.output.resolve()
    exhibition_dir = output_root / "exhibition"
    healthcare_dir = output_root / "healthcare"

    exhibition = run_exhibition_scene_beta_benchmark(project_root=project_root, output_root=exhibition_dir)
    healthcare = run_healthcare_scene_beta_benchmark(project_root=project_root, output_root=healthcare_dir)

    rollup = {
        "package_id": "BETA-SCENE-04",
        "status": "pass"
        if exhibition.get("status") == "pass" and healthcare.get("status") == "pass"
        else "fail",
        "exhibition": {
            "status": exhibition.get("status"),
            "summary": exhibition.get("summary"),
            "evidence_summary": exhibition.get("evidence_summary"),
        },
        "healthcare": {
            "status": healthcare.get("status"),
            "summary": healthcare.get("summary"),
            "evidence_summary": healthcare.get("evidence_summary"),
        },
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "beta_scene_04_rollup.json").write_text(
        json.dumps(rollup, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (exhibition_dir / "exhibition_scene_beta_report.json").write_text(
        json.dumps(exhibition, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (healthcare_dir / "healthcare_scene_beta_report.json").write_text(
        json.dumps(healthcare, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(rollup, ensure_ascii=False, indent=2))
    return 0 if rollup["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
