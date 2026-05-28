#!/usr/bin/env python3
"""Compute CAD capability registry coverage (V-PROOF-02)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.verification.capability_coverage import (  # noqa: E402
    DEFAULT_OUTPUT_PATH,
    DEFAULT_REGISTRY_PATH,
    run_capability_coverage,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compute verified/total coverage from cad_capability_registry.json."
    )
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=DEFAULT_REGISTRY_PATH,
        help="Capability registry JSON (default: examples/capability_proof/cad_capability_registry.json)",
    )
    parser.add_argument(
        "--output",
        "--output-dir",
        dest="output_path",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Write coverage report JSON under project output/ (default: output/validation_runs/capability-lab/cad_capability_coverage.json)",
    )
    parser.add_argument(
        "--min-cad-proof-rate",
        type=float,
        default=None,
        help="Optional CI gate: fail when summary.cad_proof_coverage_rate is below this value (0.0-1.0).",
    )
    parser.add_argument(
        "--require-evidence-audit-pass",
        action="store_true",
        help="Fail unless verified/showcase registry evidence reports pass the table C hard audit.",
    )
    parser.add_argument(
        "--evidence-audit-output",
        type=Path,
        default=None,
        help="Optional output path for the table C evidence audit JSON.",
    )
    args = parser.parse_args()

    report = run_capability_coverage(
        PROJECT_ROOT,
        registry_path=args.registry_path,
        output_path=args.output_path,
        require_evidence_audit_pass=args.require_evidence_audit_pass,
        evidence_audit_output_path=args.evidence_audit_output,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if report.get("status") != "pass":
        return 1
    if args.min_cad_proof_rate is not None:
        rate = float(report.get("summary", {}).get("cad_proof_coverage_rate", 0.0))
        if rate < args.min_cad_proof_rate:
            print(
                f"cad_proof_coverage_rate {rate} below minimum {args.min_cad_proof_rate}",
                file=sys.stderr,
            )
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
