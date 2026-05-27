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

from core.maintenance.doc_governance import build_doc_governance_report


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CAD Agent Markdown governance audit.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--coverage",
        type=Path,
        default=PROJECT_ROOT / "output" / "validation_runs" / "capability-lab" / "cad_capability_coverage.json",
    )
    parser.add_argument("--fail-on-findings", action="store_true")
    args = parser.parse_args()

    report = build_doc_governance_report(args.root, coverage_path=args.coverage)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.fail_on_findings and report["status"] == "findings":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
