#!/usr/bin/env python3
"""Run REST-PROD-02 restaurant beta boundary contract (no CAD)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT
except ImportError:
    from scripts._bootstrap import PROJECT_ROOT

ROOT = PROJECT_ROOT

from core.agents.restaurant_beta_boundary import (  # noqa: E402
    assert_restaurant_beta_boundary_contract,
    restaurant_beta_boundary_status_summary,
    run_restaurant_beta_boundary_smoke,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="REST-PROD-02 restaurant beta boundary contract")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "output" / "validation_runs" / "rest-prod-02-boundary-no-cad",
    )
    parser.add_argument(
        "--run-benchmark",
        action="store_true",
        help="Also run restaurant scene beta benchmark and write summary",
    )
    args = parser.parse_args()

    assert_restaurant_beta_boundary_contract(project_root=ROOT)
    summary = restaurant_beta_boundary_status_summary(project_root=ROOT)
    summary["status"] = "pass"

    if args.run_benchmark:
        bench = run_restaurant_beta_boundary_smoke(project_root=ROOT, output_root=args.output)
        summary["benchmark_status"] = bench.get("status")
        summary["benchmark_summary"] = bench.get("summary")
        summary["evidence_summary"] = bench.get("evidence_summary")

    args.output.mkdir(parents=True, exist_ok=True)
    out_path = args.output / "restaurant_beta_boundary_summary.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out_path)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
