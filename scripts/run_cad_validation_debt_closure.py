#!/usr/bin/env python
"""Build the CAD validation debt closure report from existing evidence reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.verification.cad_validation_debt_closure import run_cad_validation_debt_closure


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--evidence-audit", type=Path)
    parser.add_argument("--cad-validation", type=Path)
    parser.add_argument("--data-bloat", type=Path)
    parser.add_argument("--drawing-read", type=Path)
    parser.add_argument("--repair-gate-status", choices=["pass", "fail", "not_checked"], default="not_checked")
    parser.add_argument("--repair-gate-command", default="")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    report = run_cad_validation_debt_closure(
        coverage_path=args.coverage,
        evidence_audit_path=args.evidence_audit,
        cad_validation_path=args.cad_validation,
        data_bloat_path=args.data_bloat,
        drawing_read_path=args.drawing_read,
        repair_gate_status=args.repair_gate_status,
        repair_gate_command=args.repair_gate_command,
        output_path=args.output,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] in {"pass", "partial"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
