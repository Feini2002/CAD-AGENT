#!/usr/bin/env python3
"""Build registry writeback batch from a coverage CAD wave output directory."""

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


def _add(requests: list[dict[str, str]], capability_id: str, report_path: str, note: str) -> None:
    requests.append(
        {
            "capability_id": capability_id,
            "report_path": report_path,
            "note": note,
        }
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wave-dir", type=Path, required=True, help="capability-lab-coverage-wave-*/")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    wave = (PROJECT_ROOT / args.wave_dir).resolve()
    requests: list[dict[str, str]] = []

    object_report = wave / "object_cad_smoke" / "object_cad_smoke_report.json"
    if object_report.is_file():
        payload = json.loads(object_report.read_text(encoding="utf-8"))
        for row in payload.get("objects", []):
            cap = row.get("registry_capability_id")
            report_path = row.get("verification_report_path")
            if cap and row.get("geometry_verified") and report_path:
                rp = Path(str(report_path))
                if rp.is_absolute():
                    rp = rp.relative_to(PROJECT_ROOT.resolve())
                _add(requests, str(cap), str(rp).replace("\\", "/"), f"object smoke {row.get('object_type')}")

    domain_report = wave / "domain_draw_object" / "domain_draw_object_cad_smoke_report.json"
    if domain_report.is_file():
        payload = json.loads(domain_report.read_text(encoding="utf-8"))
        for row in payload.get("domains", []):
            cap = row.get("registry_capability_id")
            report_path = row.get("verification_report_path")
            if cap and row.get("geometry_verified") and report_path:
                rp = Path(str(report_path))
                if rp.is_absolute():
                    rp = rp.relative_to(PROJECT_ROOT.resolve())
                _add(requests, str(cap), str(rp).replace("\\", "/"), f"domain smoke {row.get('domain')}")

    sofa_report = wave / "symbol_sofa" / "symbol_glyph_cad_smoke_report.json"
    if sofa_report.is_file():
        payload = json.loads(sofa_report.read_text(encoding="utf-8"))
        if payload.get("geometry_verified"):
            rel = str(sofa_report.relative_to(PROJECT_ROOT.resolve())).replace("\\", "/")
            _add(requests, "object.sofa.glyph", rel, "RCAD-15 sofa glyph")

    glyph_aliases: dict[str, str] = {
        "object.computer_desk.glyph": "output/validation_runs/capability-lab-coverage-20260527/symbol-workstation/symbol_glyph_cad_smoke_report.json",
        "object.display_unit.glyph": "output/validation_runs/capability-lab-coverage-20260527/symbol-shelf/symbol_glyph_cad_smoke_report.json",
        "object.file_cabinet.glyph": "output/validation_runs/capability-lab-coverage-20260527/symbol-cabinet/symbol_glyph_cad_smoke_report.json",
        "object.storage_cabinet.glyph": "output/validation_runs/capability-lab-coverage-20260527/symbol-cabinet/symbol_glyph_cad_smoke_report.json",
    }
    if object_report.is_file():
        payload = json.loads(object_report.read_text(encoding="utf-8"))
        for row in payload.get("objects", []):
            if row.get("object_type") == "counter" and row.get("verification_report_path"):
                rp = Path(str(row["verification_report_path"]))
                if rp.is_absolute():
                    rp = rp.relative_to(PROJECT_ROOT.resolve())
                glyph_aliases["object.counter.glyph"] = str(rp).replace("\\", "/")
    for capability_id, report_path in glyph_aliases.items():
        if (PROJECT_ROOT / report_path).is_file():
            _add(requests, capability_id, report_path, "glyph alias linked smoke")

    block_report = "output/validation_runs/capability-lab-sprint-20260527/baseline_cad_validation/block_alpha_report.json"
    if (PROJECT_ROOT / block_report).is_file():
        for cap in (
            "block.insert_block_alpha.anchor",
            "block.insert_block_alpha.rotation",
            "block.insert_block_alpha.scale",
            "block.insert_block_alpha.attributes",
        ):
            _add(requests, cap, block_report, "baseline block_alpha readback")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"requests": requests}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"request_count": len(requests), "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
