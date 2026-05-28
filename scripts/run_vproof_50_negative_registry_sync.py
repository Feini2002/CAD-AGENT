#!/usr/bin/env python
"""V-PROOF-50: sync negative failure_category rows into cad_capability_registry."""

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

from core.verification.negative_plan_registry import run_vproof_50_negative_registry_sync


def main() -> int:
    parser = argparse.ArgumentParser(description="V-PROOF-50 negative plan registry sync.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "output" / "validation_runs" / "vproof-50-negative-registry-no-cad",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    summary = run_vproof_50_negative_registry_sync(
        project_root=args.root.resolve(),
        output_dir=args.output_dir.resolve(),
        dry_run=args.dry_run,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if summary.get("writeback_rejected_count", 0) > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
