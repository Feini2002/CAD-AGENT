#!/usr/bin/env python3
"""Run table C hard evidence audit for verified/showcase capability rows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.verification.capability_evidence_audit import audit_capability_evidence  # noqa: E402
from core.verification.capability_registry import DEFAULT_REGISTRY_PATH  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit table C verified/showcase evidence reports.")
    parser.add_argument("--registry-path", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument(
        "--output",
        "--output-path",
        dest="output_path",
        type=Path,
        default=Path("output/validation_runs/table-c-evidence-gate/evidence_audit_report.json"),
    )
    args = parser.parse_args()

    report = audit_capability_evidence(
        PROJECT_ROOT,
        registry_path=args.registry_path,
        output_path=args.output_path,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
