#!/usr/bin/env python3
"""Validate commercial_fitout catalog manifest (V-PROOF-20)."""

from __future__ import annotations

import argparse
import json
import sys

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.verification.commercial_fitout_catalog_manifest import run_commercial_fitout_catalog_inventory


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate commercial_fitout catalog inventory manifest.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = run_commercial_fitout_catalog_inventory(root=PROJECT_ROOT)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"status: {report['status']}")
        print(f"catalog_entry_count: {report['catalog_entry_count']}")
        for error in report.get("errors", []):
            print(error, file=sys.stderr)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
