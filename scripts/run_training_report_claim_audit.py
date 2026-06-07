from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT

from core.training.report_claim_audit import audit_training_report_claims


def main() -> int:
    parser = argparse.ArgumentParser(description="Run readonly training report claim audit.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--reports",
        type=Path,
        nargs="+",
        default=[
            PROJECT_ROOT / "output" / "training_queues",
            PROJECT_ROOT / "output" / "validation_runs",
        ],
        help="Report files or directories to scan.",
    )
    parser.add_argument("--fail-on-blocked", action="store_true")
    args = parser.parse_args()

    report = audit_training_report_claims(args.root, args.reports)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.fail_on_blocked and report.get("status") == "blocked":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
