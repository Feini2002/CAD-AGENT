#!/usr/bin/env python3
"""Run OFFICE-PROD-01 office alpha boundary contract (no CAD)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT
except ImportError:
    from scripts._bootstrap import PROJECT_ROOT

ROOT = PROJECT_ROOT

from core.agents.office_alpha_boundary import (
    assert_office_alpha_boundary_contract,
    office_alpha_boundary_status_summary,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="OFFICE-PROD-01 office alpha boundary contract")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "output" / "validation_runs" / "office-prod-01-boundary-no-cad",
    )
    args = parser.parse_args()

    assert_office_alpha_boundary_contract(project_root=ROOT)
    summary = office_alpha_boundary_status_summary(project_root=ROOT)
    summary["status"] = "pass"

    args.output.mkdir(parents=True, exist_ok=True)
    out_path = args.output / "office_alpha_boundary_summary.json"
    out_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out_path)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
