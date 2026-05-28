#!/usr/bin/env python3
"""Run RESIDENTIAL-PROD-01 residential alpha boundary contract (no CAD)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT
except ImportError:
    from scripts._bootstrap import PROJECT_ROOT

ROOT = PROJECT_ROOT

from core.agents.residential_alpha_boundary import (  # noqa: E402
    assert_residential_alpha_boundary_contract,
    residential_alpha_boundary_status_summary,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="RESIDENTIAL-PROD-01 residential alpha boundary contract"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "output" / "validation_runs" / "res-prod-01-boundary-no-cad",
    )
    args = parser.parse_args()

    assert_residential_alpha_boundary_contract(project_root=ROOT)
    summary = residential_alpha_boundary_status_summary(project_root=ROOT)
    summary["status"] = "pass"

    args.output.mkdir(parents=True, exist_ok=True)
    out_path = args.output / "residential_alpha_boundary_summary.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out_path)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
