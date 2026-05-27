#!/usr/bin/env python3
"""Run REST-PROD-03 restaurant P3 wave parent rollup (no CAD)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT
except ImportError:
    from scripts._bootstrap import PROJECT_ROOT

ROOT = PROJECT_ROOT

from core.agents.restaurant_beta_boundary import run_restaurant_beta_boundary_smoke  # noqa: E402
from core.agents.restaurant_p3_wave import (  # noqa: E402
    assert_restaurant_p3_wave_contract,
    restaurant_p3_wave_status_summary,
)
from core.benchmarks.runner import run_benchmark_suite  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="REST-PROD-03 restaurant P3 wave parent rollup")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "output" / "validation_runs" / "rest-prod-03-p3-rollup-no-cad",
    )
    parser.add_argument(
        "--run-benchmarks",
        action="store_true",
        help="Also run restaurant alpha and beta no-CAD benchmarks and write summaries",
    )
    args = parser.parse_args()

    assert_restaurant_p3_wave_contract(project_root=ROOT)
    summary = restaurant_p3_wave_status_summary(project_root=ROOT)
    summary["status"] = "pass"

    if args.run_benchmarks:
        alpha_dir = args.output / "alpha"
        beta_dir = args.output / "beta"
        alpha = run_benchmark_suite(ROOT / "examples/benchmarks/scene_alpha_benchmark.json", output_root=alpha_dir)
        beta = run_restaurant_beta_boundary_smoke(project_root=ROOT, output_root=beta_dir)
        summary["alpha_status"] = alpha.get("status")
        summary["alpha_summary"] = alpha.get("summary")
        summary["beta_status"] = beta.get("status")
        summary["beta_summary"] = beta.get("summary")
        summary["beta_evidence_summary"] = beta.get("evidence_summary")

    args.output.mkdir(parents=True, exist_ok=True)
    out_path = args.output / "restaurant_p3_wave_summary.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out_path)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
