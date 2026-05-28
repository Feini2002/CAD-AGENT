#!/usr/bin/env python3
"""Run the aggregate table C evidence gate before registry writeback."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.verification.capability_registry import DEFAULT_REGISTRY_PATH  # noqa: E402
from core.verification.table_c_evidence_gate import run_table_c_evidence_gate  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run hard evidence + visual gates for table C writeback.")
    parser.add_argument("--registry-path", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument(
        "--output",
        "--output-path",
        dest="output_path",
        type=Path,
        default=Path("output/validation_runs/table-c-evidence-gate/table_c_evidence_gate_report.json"),
    )
    parser.add_argument("--evidence-audit-report", type=Path)
    parser.add_argument("--visual-review-report", type=Path)
    parser.add_argument("--coverage-output", type=Path)
    parser.add_argument(
        "--allow-missing-visual",
        action="store_true",
        help="Do not require visual_review_report.status=pass. Use only for audit-only diagnostics.",
    )
    args = parser.parse_args()

    report = run_table_c_evidence_gate(
        PROJECT_ROOT,
        registry_path=args.registry_path,
        output_path=args.output_path,
        evidence_audit_report_path=args.evidence_audit_report,
        visual_review_report_path=args.visual_review_report,
        coverage_output_path=args.coverage_output,
        require_visual_pass=not args.allow_missing_visual,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
