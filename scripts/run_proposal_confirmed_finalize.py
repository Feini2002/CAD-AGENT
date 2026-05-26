#!/usr/bin/env python3
"""Finalize confirmed CAD_PLAN bundle from pipeline artifacts (BETA-PROPOSAL-05)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.proposal_engine.confirmed_finalize import finalize_confirmed_cad_plans  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Finalize user-confirmed CAD_PLAN bundle.")
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--confirmation", type=Path, required=True)
    args = parser.parse_args()

    report = finalize_confirmed_cad_plans(args.artifact_dir.resolve(), args.confirmation.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
