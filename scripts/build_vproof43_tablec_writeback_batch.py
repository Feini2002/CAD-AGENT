#!/usr/bin/env python3
"""Build V-PROOF-43 table C writeback batch (interior refresh + office composition showcase)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT

ROOT = PROJECT_ROOT


def _rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def _requests_from_report(report_path: Path, *, claim_level: str, note_prefix: str) -> list[dict[str, str]]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    requests: list[dict[str, str]] = []
    for row in report.get("registry_rows", []):
        cap = row.get("registry_capability_id")
        rp = row.get("verification_report_path")
        if cap and row.get("geometry_verified") and rp:
            requests.append(
                {
                    "capability_id": str(cap),
                    "report_path": _rel(ROOT / str(rp)),
                    "claim_level": claim_level,
                    "note": f"{note_prefix} {row.get('benchmark_case_id')}",
                }
            )
    return requests


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    requests: list[dict[str, str]] = []
    requests.extend(
        _requests_from_report(
            ROOT
            / "output/validation_runs/vproof-43-composition-rerun-20260528-cad/composition_cad_registry_report.json",
            claim_level="showcase",
            note_prefix="V-PROOF-43",
        )
    )
    requests.extend(
        _requests_from_report(
            ROOT
            / "output/validation_runs/vproof-tablec-office-composition-20260528-cad/composition_cad_registry_report.json",
            claim_level="showcase",
            note_prefix="V-PROOF-43-office-showcase",
        )
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"requests": requests}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"request_count": len(requests), "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
