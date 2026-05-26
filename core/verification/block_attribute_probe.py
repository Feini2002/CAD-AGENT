"""Controlled block attribute / tag readback probe (BETA-CAD-BLOCK-02)."""

from __future__ import annotations

from typing import Any

from core.verification.evidence_contract import EVIDENCE_DEFERRED_CAD_READBACK


FAILURE_ATTRIBUTE_UNVERIFIED = "attribute_unverified"


def plan_expects_attribute_readback(plan: dict[str, Any]) -> bool:
    obj = plan.get("object", {})
    if not isinstance(obj, dict):
        return False
    if not obj.get("attribute_readback_probe"):
        return False
    attributes = obj.get("attributes")
    return isinstance(attributes, dict) and bool(attributes)


def expected_attributes_from_plan(plan: dict[str, Any]) -> dict[str, str]:
    attributes = plan.get("object", {}).get("attributes", {})
    if not isinstance(attributes, dict):
        return {}
    normalized: dict[str, str] = {}
    for tag, value in attributes.items():
        normalized[str(tag)] = str(value)
    return normalized


def normalize_entity_attributes(entity: dict[str, Any]) -> dict[str, str]:
    raw = entity.get("attributes")
    if not isinstance(raw, dict):
        return {}
    return {str(tag): str(value) for tag, value in raw.items()}


def check_block_attribute_readback(plan: dict[str, Any], entity: dict[str, Any]) -> dict[str, Any]:
    """Assess attribute/tag readback. Plans without attribute_readback_probe do not run (no false positive)."""

    if not plan_expects_attribute_readback(plan):
        return {
            "status": "not_run",
            "blocks_geometry_verified": False,
            "evidence_state": "",
            "checks": [
                {
                    "name": "attribute_readback",
                    "status": "not_run",
                    "message": "plan has no attribute_readback_probe; attribute tags not required",
                }
            ],
        }

    expected = expected_attributes_from_plan(plan)
    actual = normalize_entity_attributes(entity)
    checks: list[dict[str, Any]] = []

    if not actual:
        checks.append(
            {
                "name": "attribute_readback",
                "status": "deferred",
                "failure_category": FAILURE_ATTRIBUTE_UNVERIFIED,
                "message": "plan requires attribute tags but readback entity has no attributes",
                "expected_tags": sorted(expected.keys()),
                "actual_tags": [],
            }
        )
        return {
            "status": "deferred",
            "blocks_geometry_verified": True,
            "evidence_state": EVIDENCE_DEFERRED_CAD_READBACK,
            "checks": checks,
        }

    missing_tags = [tag for tag in expected if tag not in actual]
    mismatched = [
        {"tag": tag, "expected": expected[tag], "actual": actual.get(tag)}
        for tag in expected
        if tag in actual and actual[tag] != expected[tag]
    ]
    if missing_tags or mismatched:
        checks.append(
            {
                "name": "attribute_readback",
                "status": "fail",
                "failure_category": FAILURE_ATTRIBUTE_UNVERIFIED,
                "message": "attribute tag readback mismatch",
                "missing_tags": missing_tags,
                "mismatched": mismatched,
                "actual_tags": sorted(actual.keys()),
            }
        )
        return {
            "status": "fail",
            "blocks_geometry_verified": True,
            "evidence_state": EVIDENCE_DEFERRED_CAD_READBACK,
            "checks": checks,
        }

    checks.append(
        {
            "name": "attribute_readback",
            "status": "pass",
            "message": f"matched tags: {sorted(expected.keys())}",
            "actual_tags": sorted(actual.keys()),
        }
    )
    return {
        "status": "pass",
        "blocks_geometry_verified": False,
        "evidence_state": "",
        "checks": checks,
    }


def merge_block_readback_checks(
    geometry_checks: list[dict[str, Any]],
    attribute_assessment: dict[str, Any],
) -> tuple[list[dict[str, Any]], bool, str]:
    """Merge geometry + attribute checks; return checks, geometry_verified, evidence_state."""

    checks = list(geometry_checks)
    attr_checks = attribute_assessment.get("checks", [])
    attr_status = str(attribute_assessment.get("status", "not_run"))
    if attr_status != "not_run" and isinstance(attr_checks, list):
        checks.extend(attr_checks)

    geometry_failed = any(
        isinstance(check, dict) and check.get("status") == "fail" for check in geometry_checks
    )
    blocks = bool(attribute_assessment.get("blocks_geometry_verified"))

    if blocks:
        return checks, False, str(attribute_assessment.get("evidence_state") or EVIDENCE_DEFERRED_CAD_READBACK)
    if geometry_failed or attr_status in {"fail", "deferred"}:
        return checks, False, EVIDENCE_DEFERRED_CAD_READBACK

    geometry_verified = bool(geometry_checks) and all(
        isinstance(check, dict) and check.get("status") == "pass" for check in geometry_checks
    )
    evidence_state = EVIDENCE_DEFERRED_CAD_READBACK if not geometry_verified else ""
    return checks, geometry_verified, evidence_state
