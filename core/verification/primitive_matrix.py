"""Primitive capability matrix wrapper around the CAD capability probe."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from core.verification.cad_capability_probe import EXPECTED_TYPE_COUNTS, run_cad_capability_probe
from core.verification.preview_only_audit import build_preview_only_audit


PRIMITIVE_TYPES = tuple(sorted(EXPECTED_TYPE_COUNTS.keys()))


def run_primitive_matrix(
    *,
    output_dir: Path | None = None,
    no_cad: bool = False,
    driver_factory: Callable[[], Any] | None = None,
) -> dict[str, Any]:
    if no_cad:
        from core.verification.fake_cad_driver import FakeCadDriver

        probe = run_cad_capability_probe(driver_factory=FakeCadDriver, output_dir=output_dir)
        geometry_verified = False
    else:
        probe = run_cad_capability_probe(driver_factory=driver_factory, output_dir=output_dir)
        geometry_verified = probe.get("status") == "cad_capability_verified"

    type_counts = probe.get("actual", {}).get("type_counts", {})
    type_ok = type_counts == EXPECTED_TYPE_COUNTS
    report = {
        "version": "0.1",
        "suite_id": "primitive_matrix",
        "status": "pass" if probe.get("status") in {"cad_capability_verified"} or (no_cad and probe.get("status") != "failed") else "fail",
        "no_cad": no_cad,
        "geometry_verified": geometry_verified,
        "primitive_types": list(PRIMITIVE_TYPES),
        "expected_type_counts": EXPECTED_TYPE_COUNTS,
        "actual_type_counts": type_counts,
        "type_counts_match": type_ok,
        "probe_status": probe.get("status"),
        "created_handle_count": len(probe.get("created_handles", [])),
        "safety": build_preview_only_audit(),
        "probe": probe,
    }
    if no_cad:
        report["status"] = "pass" if type_ok and probe.get("status") != "failed" else "fail"
    else:
        report["status"] = "pass" if geometry_verified and type_ok else "fail"

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "primitive_matrix_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return report
