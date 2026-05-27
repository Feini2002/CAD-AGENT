#!/usr/bin/env python3
"""Build registry writeback batch from composition_cad_registry report (office wave)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.path_safety import find_project_root

ROOT = find_project_root(Path(__file__))


def _rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    report = json.loads(args.registry_report.read_text(encoding="utf-8"))
    requests: list[dict[str, str]] = []
    for row in report.get("registry_rows", []):
        cap = row.get("registry_capability_id")
        rp = row.get("verification_report_path")
        if cap and row.get("geometry_verified") and rp:
            requests.append(
                {
                    "capability_id": str(cap),
                    "report_path": _rel(ROOT / str(rp)),
                    "note": f"V-PROOF-42 {row.get('benchmark_case_id')}",
                }
            )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"requests": requests}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"request_count": len(requests), "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
