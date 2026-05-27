#!/usr/bin/env python3
"""Build registry writeback batch from symbol_glyph_cad_matrix report."""

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
    parser.add_argument("--matrix-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    report = json.loads(args.matrix_report.read_text(encoding="utf-8"))
    requests: list[dict[str, str]] = []
    for row in report.get("cases", []):
        cap = row.get("registry_capability_id")
        if not cap or not row.get("geometry_verified"):
            continue
        rp = row.get("report_path")
        if not rp:
            continue
        requests.append(
            {
                "capability_id": str(cap),
                "report_path": _rel(ROOT / str(rp)),
                "note": f"V-PROOF-32 {row.get('case_id')}",
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"requests": requests}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"request_count": len(requests), "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
