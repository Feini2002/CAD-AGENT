"""Per-subscene representative catalog draw_object CAD smoke (CFIT-12 / V-PROOF-25)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.plan_engine.validate_plan import load_json
from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)
from core.verification.fitout_catalog_cad_smoke import run_fitout_catalog_cad_smoke
from core.verification.preview_only_audit import build_preview_only_audit

DEFAULT_MANIFEST = Path("examples") / "capability_proof" / "fitout_subscene_object_cad_smoke_manifest.json"
SUBSCENE_SPACING_Y = 12000


def load_fitout_subscene_object_cad_smoke_manifest(path: Path) -> dict[str, Any]:
    manifest = load_json(path)
    if manifest.get("version") != "0.1":
        raise ValueError("fitout_subscene_object_cad_smoke_manifest version must be '0.1'.")
    if manifest.get("manifest_id") != "fitout_subscene_object_cad_smoke":
        raise ValueError("manifest_id must be 'fitout_subscene_object_cad_smoke'.")
    subscenes = manifest.get("subscenes")
    if not isinstance(subscenes, list) or not subscenes:
        raise ValueError("fitout_subscene_object_cad_smoke_manifest requires a non-empty subscenes array.")
    return manifest


def _catalog_ids_for_subscene(subscene_entry: dict[str, Any]) -> list[str]:
    objects = subscene_entry.get("representative_objects")
    if not isinstance(objects, list) or not objects:
        raise ValueError(f"subscene {subscene_entry.get('subscene_id')!r} has no representative_objects")
    return [str(item["catalog_object_id"]) for item in objects if isinstance(item, dict)]


def run_fitout_subscene_object_cad_smoke(
    *,
    root: Path,
    manifest_path: Path | None = None,
    output_dir: Path | None = None,
    no_cad: bool = False,
    driver: Any | None = None,
    base_offset: list[float] | None = None,
    subscene_ids: list[str] | None = None,
) -> dict[str, Any]:
    manifest_path = manifest_path or (root / DEFAULT_MANIFEST)
    manifest = load_fitout_subscene_object_cad_smoke_manifest(manifest_path)

    catalog_manifest_path = root / str(manifest.get("catalog_manifest_path", ""))
    catalog_path = root / str(manifest.get("catalog_path", ""))

    selected = manifest["subscenes"]
    if subscene_ids is not None:
        wanted = set(subscene_ids)
        selected = [row for row in selected if isinstance(row, dict) and str(row.get("subscene_id")) in wanted]
        if len(selected) != len(wanted):
            missing = wanted - {str(row.get("subscene_id")) for row in selected}
            raise ValueError(f"unknown subscene_id(s): {sorted(missing)!r}")

    subscene_results: list[dict[str, Any]] = []
    offset = list(base_offset or [96000, 60000, 0])

    for index, subscene_entry in enumerate(selected):
        subscene_id = str(subscene_entry["subscene_id"])
        catalog_object_ids = _catalog_ids_for_subscene(subscene_entry)
        sub_offset = list(offset)
        sub_offset[1] = float(sub_offset[1]) + index * SUBSCENE_SPACING_Y

        sub_output = (output_dir / subscene_id) if output_dir is not None else None
        catalog_report = run_fitout_catalog_cad_smoke(
            root=root,
            manifest_path=catalog_manifest_path,
            catalog_path=catalog_path,
            output_dir=sub_output,
            no_cad=no_cad,
            driver=driver,
            base_offset=sub_offset,
            catalog_object_ids=catalog_object_ids,
        )

        verified_count = int(catalog_report.get("geometry_verified_catalog_object_count", 0))
        subscene_results.append(
            {
                "subscene_id": subscene_id,
                "sample_id": str(subscene_entry.get("sample_id", "")),
                "rcad_followup": str(subscene_entry.get("rcad_followup", "")),
                "catalog_object_ids": catalog_object_ids,
                "status": catalog_report.get("status", "fail"),
                "geometry_verified": verified_count == len(catalog_object_ids) and verified_count > 0,
                "geometry_verified_object_count": verified_count,
                "representative_object_count": len(catalog_object_ids),
                "catalog_objects": catalog_report.get("catalog_objects", []),
                "report_path": str((sub_output / "fitout_catalog_cad_smoke_report.json")) if sub_output else "",
            }
        )

    total_objects = sum(item["representative_object_count"] for item in subscene_results)
    verified_total = sum(item["geometry_verified_object_count"] for item in subscene_results)
    subscenes_verified = sum(1 for item in subscene_results if item.get("geometry_verified"))

    if no_cad:
        status = "deferred"
        evidence_state = EVIDENCE_DEFERRED_CAD_READBACK
        geometry_accuracy = NON_CAD_GEOMETRY_ACCURACY
    elif verified_total == total_objects and total_objects > 0:
        status = "geometry_verified"
        evidence_state = EVIDENCE_READBACK_GEOMETRY_VERIFIED
        geometry_accuracy = GEOMETRY_VERIFIED_BY_READBACK
    else:
        status = "fail"
        evidence_state = EVIDENCE_DEFERRED_CAD_READBACK
        geometry_accuracy = NON_CAD_GEOMETRY_ACCURACY

    report: dict[str, Any] = {
        "version": "0.1",
        "suite_id": "fitout_subscene_object_cad_smoke",
        "package_id": "CFIT-12-FITOUT-SUBSCENE-OBJECT-CAD-SMOKE",
        "status": status,
        "no_cad": no_cad,
        "subscene_count": len(subscene_results),
        "geometry_verified_subscene_count": subscenes_verified,
        "representative_object_count": total_objects,
        "geometry_verified_object_count": verified_total,
        "geometry_verified": status == "geometry_verified",
        "evidence_state": evidence_state,
        "geometry_accuracy": geometry_accuracy,
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
        "safety": build_preview_only_audit(),
        "subscenes": subscene_results,
    }

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / "fitout_subscene_object_cad_smoke_report.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report["report_path"] = str(report_path)

    return report


def assert_fitout_subscene_object_manifest_contract(manifest: dict[str, Any]) -> None:
    """Raise when manifest does not cover meeting_room + reception with registry ids."""

    subscene_ids = {
        str(row.get("subscene_id"))
        for row in manifest.get("subscenes", [])
        if isinstance(row, dict)
    }
    if subscene_ids != {"meeting_room", "reception"}:
        raise AssertionError(f"expected meeting_room + reception, got {sorted(subscene_ids)!r}")

    for row in manifest.get("subscenes", []):
        if not isinstance(row, dict):
            continue
        for obj in row.get("representative_objects", []):
            if not isinstance(obj, dict):
                raise AssertionError("representative_objects entries must be objects")
            if not obj.get("registry_capability_id"):
                raise AssertionError(f"missing registry_capability_id for {obj.get('catalog_object_id')!r}")
