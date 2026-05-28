#!/usr/bin/env python
"""Run Capability Lab tier steps (V-PROOF-72 nightly / CI entry)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT

from core.verification.capability_lab import (
    VPROOF_72_DEFAULT_OUTPUT,
    run_capability_lab,
    validate_capability_lab_report,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Capability Lab tier orchestrator.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--tier",
        choices=["L0", "L1"],
        default="L1",
        help="Lab tier (default L1 nightly no-CAD stack).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / VPROOF_72_DEFAULT_OUTPUT.replace("/", "\\"),
    )
    parser.add_argument("--manifest", type=Path, help="Override nightly_lab_tier_manifest.json")
    parser.add_argument("--dry-run", action="store_true", help="Print planned commands without executing.")
    args = parser.parse_args()

    root = args.root.resolve()
    output_dir = args.output_dir.resolve()
    if args.tier == "L1" and output_dir == (root / VPROOF_72_DEFAULT_OUTPUT).resolve():
        pass
    elif args.tier == "L0":
        output_dir = output_dir / "tier-l0" if "tier-l" not in str(output_dir) else output_dir

    try:
        report = run_capability_lab(
            project_root=root,
            tier=args.tier,
            output_dir=output_dir,
            manifest_path=args.manifest,
            dry_run=args.dry_run,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    schema_errors = validate_capability_lab_report(report, project_root=root)
    if schema_errors:
        report["schema_errors"] = schema_errors

    report_path = output_dir / "capability_lab_report.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if schema_errors:
        return 2
    if report.get("status") != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
