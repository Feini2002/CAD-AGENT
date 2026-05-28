#!/usr/bin/env python3
"""Build registry writeback batch for TABLE-C final-gap CAD wave."""

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
    parser.add_argument(
        "--wave-dir",
        type=Path,
        default=Path("output/validation_runs/tablec-final-gap-20260528-cad"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/validation_runs/tablec-final-gap-20260528-cad/writeback_batch.json"),
    )
    args = parser.parse_args()

    wave = (PROJECT_ROOT / args.wave_dir).resolve()
    intent_dir = wave / "intent-lab"
    requests: list[dict[str, str]] = []
    for intent in ("draw_annotation", "modify_object", "delete_object"):
        report = intent_dir / f"intent_{intent}_cad_report.json"
        if report.is_file():
            rel = str(report.relative_to(PROJECT_ROOT.resolve())).replace("\\", "/")
            requests.append(
                {
                    "capability_id": f"intent.{intent}",
                    "report_path": rel,
                    "claim_level": "showcase",
                    "note": f"TABLE-C-FINAL-GAP intent {intent}",
                }
            )

    cad_report = wave / "verification_no_cad_cad" / "verification_reports" / "verification_report_001.json"
    if cad_report.is_file():
        rel = str(cad_report.relative_to(PROJECT_ROOT.resolve())).replace("\\", "/")
        requests.append(
            {
                "capability_id": "core.api.verification_no_cad_report",
                "report_path": rel,
                "claim_level": "showcase",
                "note": "TABLE-C-FINAL-GAP verification.no_cad_report CAD mirror",
            }
        )

    output = PROJECT_ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {"version": "0.1", "requests": requests}
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if requests else 1


if __name__ == "__main__":
    raise SystemExit(main())
