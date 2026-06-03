#!/usr/bin/env python3
"""Promote accepted training reports into agent learning memory and prompt addenda."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path
except ModuleNotFoundError:  # Imported as scripts.promote_training_acceptance.
    from scripts._bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.training.learning_promotion import promote_training_acceptance  # noqa: E402
from scripts import build_capability_map_data  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Promote accepted CAD training reports into agent learning files.")
    parser.add_argument(
        "--report",
        action="append",
        type=Path,
        dest="reports",
        help="Accepted training report path. Can be repeated. Defaults to known report paths.",
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        default=build_capability_map_data.TRAINING_LEARNING_LEDGER_PATH,
        help="Output learning ledger path.",
    )
    args = parser.parse_args()

    reports = args.reports or build_capability_map_data.TRAINING_ACCEPTANCE_REPORT_PATHS
    report = promote_training_acceptance(
        root=PROJECT_ROOT,
        report_paths=reports,
        programs=build_capability_map_data.training_programs(),
        ledger_path=args.ledger,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] in {"promoted", "no_promotable_acceptance"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
