"""CAD_PLAN intent inventory and minimal-plan coverage (V-PROOF-10 / V-PROOF-11)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.plan_engine.validate_plan import ALLOWED_INTENTS, load_json, validate_plan

DEFAULT_INTENT_LAB_MANIFEST = Path("examples") / "capability_proof" / "intent_lab_manifest.json"


def load_intent_lab_manifest(path: Path) -> dict[str, Any]:
    manifest = load_json(path)
    if manifest.get("version") != "0.1":
        raise ValueError("intent_lab_manifest version must be '0.1'.")
    if manifest.get("manifest_id") != "intent_lab":
        raise ValueError("intent_lab_manifest manifest_id must be 'intent_lab'.")
    intents = manifest.get("intents")
    if not isinstance(intents, list) or not intents:
        raise ValueError("intent_lab_manifest requires a non-empty intents array.")
    for index, item in enumerate(intents):
        if not isinstance(item, dict):
            raise ValueError(f"intents[{index}] must be an object.")
        for key in ("intent", "plan_path", "registry_capability_id"):
            if key not in item:
                raise ValueError(f"intents[{index}] missing required field: {key}")
    return manifest


def inventory_from_manifest(manifest: dict[str, Any]) -> list[str]:
    return sorted({str(item["intent"]) for item in manifest["intents"]})


def validate_intent_inventory_complete(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    manifest_intents = inventory_from_manifest(manifest)
    missing = sorted(ALLOWED_INTENTS - set(manifest_intents))
    extra = sorted(set(manifest_intents) - ALLOWED_INTENTS)
    if missing:
        errors.append(f"intent_lab_manifest missing intents: {', '.join(missing)}")
    if extra:
        errors.append(f"intent_lab_manifest has unknown intents: {', '.join(extra)}")
    if len(manifest_intents) != len(ALLOWED_INTENTS):
        errors.append("intent_lab_manifest must contain exactly one row per allowed intent.")
    return errors


def run_intent_lab_inventory(
    *,
    root: Path,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    manifest_path = manifest_path or (root / DEFAULT_INTENT_LAB_MANIFEST)
    manifest = load_intent_lab_manifest(manifest_path)
    inventory_errors = validate_intent_inventory_complete(manifest)
    plan_results: list[dict[str, Any]] = []
    for item in manifest["intents"]:
        plan_path = root / str(item["plan_path"])
        plan_errors = validate_plan(load_json(plan_path)) if plan_path.exists() else ["plan file not found"]
        plan_results.append(
            {
                "intent": item["intent"],
                "plan_path": str(item["plan_path"]),
                "registry_capability_id": item.get("registry_capability_id"),
                "cad_execution": item.get("cad_execution", False),
                "deferred_reason": item.get("deferred_reason"),
                "validate_status": "pass" if not plan_errors else "fail",
                "validate_errors": plan_errors,
            }
        )

    plan_failures = [row for row in plan_results if row["validate_status"] != "pass"]
    status = "pass"
    if inventory_errors or plan_failures:
        status = "fail"

    return {
        "status": status,
        "manifest_path": str(manifest_path.relative_to(root)).replace("\\", "/"),
        "allowed_intents": sorted(ALLOWED_INTENTS),
        "manifest_intents": inventory_from_manifest(manifest),
        "inventory_errors": inventory_errors,
        "intents": plan_results,
    }
