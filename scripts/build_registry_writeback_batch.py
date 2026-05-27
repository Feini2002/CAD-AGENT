#!/usr/bin/env python3
"""Build capability registry writeback batch from fitout catalog smoke + glyph links."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fitout-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    fitout = json.loads(args.fitout_report.read_text(encoding="utf-8"))
    requests: list[dict[str, str]] = []
    for row in fitout.get("catalog_objects", []):
        if row.get("geometry_verified") and row.get("verification_report_path"):
            requests.append(
                {
                    "capability_id": str(row["registry_capability_id"]),
                    "report_path": str(row["verification_report_path"]),
                    "note": f"fitout catalog CAD {row['catalog_object_id']}",
                }
            )

    glyph_map = {
        "object.desk.glyph": "output/validation_runs/capability-lab-sprint-20260527-extra/rcad-12-desk/symbol_glyph_cad_smoke_report.json",
        "object.chair.glyph": "output/validation_runs/capability-lab-sprint-20260527-extra/rcad-13-chair/symbol_glyph_cad_smoke_report.json",
        "object.cabinet.glyph": "output/validation_runs/capability-lab-coverage-20260527/symbol-cabinet/symbol_glyph_cad_smoke_report.json",
        "object.shelf.glyph": "output/validation_runs/capability-lab-coverage-20260527/symbol-shelf/symbol_glyph_cad_smoke_report.json",
        "object.bed.glyph": "output/validation_runs/capability-lab-coverage-20260527/symbol-bed/symbol_glyph_cad_smoke_report.json",
        "object.table.glyph": "output/validation_runs/capability-lab-round2-20260527/rcad-14-table/symbol_glyph_cad_smoke_report.json",
    }
    for capability_id, report_path in glyph_map.items():
        requests.append(
            {
                "capability_id": capability_id,
                "report_path": report_path,
                "note": "glyph fallback linked to symbol spec smoke",
            }
        )

    requests.extend(
        [
            {
                "capability_id": "regression.baseline_cad_validation",
                "report_path": "output/validation_runs/cad-validation-wave-20260527/baseline_cad_validation/report.json",
                "note": "cad-validation-wave geometry gate",
            },
            {
                "capability_id": "regression.composition_cad_check",
                "report_path": "output/validation_runs/cad-validation-wave-20260527/composition_cad_retry/composition_cad_check_report.json",
                "note": "composition retry wave",
            },
        ]
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"requests": requests}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"request_count": len(requests), "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
