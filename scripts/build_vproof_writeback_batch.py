#!/usr/bin/env python3
"""Build registry writeback batch from V-PROOF capability-lab wave."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.path_safety import find_project_root

PROJECT_ROOT = find_project_root(Path(__file__))


def _rel(path: Path) -> str:
    resolved = path.resolve()
    if resolved.is_absolute():
        return str(resolved.relative_to(PROJECT_ROOT.resolve())).replace("\\", "/")
    return str(path).replace("\\", "/")


def _add(requests: list[dict[str, str]], capability_id: str, report_path: str, note: str) -> None:
    requests.append({"capability_id": capability_id, "report_path": report_path, "note": note})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wave-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    wave = (PROJECT_ROOT / args.wave_dir).resolve()
    requests: list[dict[str, str]] = []

    demand_report = wave / "demand_case_cad" / "demand_case_cad_smoke_report.json"
    if demand_report.is_file():
        for row in json.loads(demand_report.read_text(encoding="utf-8")).get("cases", []):
            cap = row.get("registry_capability_id")
            rp = row.get("verification_report_path")
            if cap and row.get("geometry_verified") and rp:
                _add(requests, str(cap), _rel(Path(str(rp))), f"demand CAD {row.get('case_id')}")

    composition_report = wave / "composition_cad_registry" / "composition_cad_registry_report.json"
    if composition_report.is_file():
        for row in json.loads(composition_report.read_text(encoding="utf-8")).get("registry_rows", []):
            cap = row.get("registry_capability_id")
            rp = row.get("verification_report_path")
            if cap and row.get("geometry_verified") and rp:
                _add(requests, str(cap), _rel(Path(str(rp))), f"composition {row.get('benchmark_case_id')}")

    for glyph_dir, cap_id in (
        ("symbol_monitor", "object.monitor.glyph"),
        ("symbol_rug", "object.rug.glyph"),
    ):
        report = wave / glyph_dir / "symbol_glyph_cad_smoke_report.json"
        if report.is_file():
            payload = json.loads(report.read_text(encoding="utf-8"))
            if payload.get("geometry_verified"):
                _add(requests, cap_id, _rel(report), "V-PROOF-31 glyph")
                spec_cap = cap_id.replace("object.", "symbol.spec.").replace(".glyph", "_plan")
                spec_cap = spec_cap.replace("monitor", "symbol_monitor").replace("rug", "symbol_rug")
                if spec_cap.startswith("symbol.spec."):
                    spec_id = {
                        "object.monitor.glyph": "symbol.spec.surface_monitor_plan",
                        "object.rug.glyph": "symbol.spec.surface_rug_plan",
                    }.get(cap_id)
                    if spec_id:
                        _add(requests, spec_id, _rel(report), "V-PROOF-31 spec row")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"requests": requests}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"request_count": len(requests), "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
