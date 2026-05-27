#!/usr/bin/env python
"""Run CAD_PLAN intent lab inventory (V-PROOF-10 / V-PROOF-11)."""

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

from core.verification.intent_lab import run_intent_lab_inventory


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate intent lab manifest and minimal plans.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=PROJECT_ROOT / "examples" / "capability_proof" / "intent_lab_manifest.json",
    )
    parser.add_argument("--output", type=Path, help="Optional JSON report path.")
    args = parser.parse_args()

    root = args.root.resolve()
    report = run_intent_lab_inventory(root=root, manifest_path=args.manifest.resolve())
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output_path = args.output if args.output.is_absolute() else root / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
