"""Validate negative CAD_PLAN fixtures reject as expected (LCAD-10.1)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.plan_engine.validate_plan import load_json, validate_plan
from core.schemas.validator import validate_json

DEFAULT_NEGATIVE_MANIFEST = Path("examples") / "plans" / "negative" / "negative_plan_manifest.json"


def load_negative_plan_manifest(path: Path) -> dict[str, Any]:
    manifest = load_json(path)
    if manifest.get("version") != "0.1":
        raise ValueError("negative_plan_manifest version must be '0.1'.")
    if manifest.get("manifest_id") != "cad_plan_negative":
        raise ValueError("negative_plan_manifest manifest_id must be 'cad_plan_negative'.")
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list) or not fixtures:
        raise ValueError("negative_plan_manifest requires a non-empty fixtures array.")
    return manifest


def run_negative_cad_plan_suite(
    *,
    root: Path,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    manifest_path = manifest_path or (root / DEFAULT_NEGATIVE_MANIFEST)
    manifest = load_negative_plan_manifest(manifest_path)
    schema_path = root / "core" / "schemas" / "cad_plan.schema.json"
    results: list[dict[str, Any]] = []

    for fixture in manifest["fixtures"]:
        plan_path = root / str(fixture["plan_path"])
        validate_errors = validate_plan(load_json(plan_path))
        schema_errors = validate_json(schema_path, plan_path)
        expected = [str(item) for item in fixture.get("expected_validate_substrings", [])]
        missing_expected = [
            substring
            for substring in expected
            if not any(substring in error for error in validate_errors)
        ]
        status = "pass"
        if not validate_errors:
            status = "fail"
        if missing_expected:
            status = "fail"

        results.append(
            {
                "id": fixture["id"],
                "failure_category": str(fixture.get("failure_category") or fixture["id"]),
                "plan_path": str(fixture["plan_path"]),
                "status": status,
                "validate_errors": validate_errors,
                "schema_errors": schema_errors,
                "missing_expected_substrings": missing_expected,
            }
        )

    failures = [row for row in results if row["status"] != "pass"]
    return {
        "status": "pass" if not failures else "fail",
        "manifest_path": str(manifest_path.relative_to(root)).replace("\\", "/"),
        "fixture_count": len(results),
        "failures": failures,
        "fixtures": results,
    }
