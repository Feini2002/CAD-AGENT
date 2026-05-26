"""Symbol readability gate reports for SYMBOL_SPEC and object mapping results."""

from __future__ import annotations

from typing import Any

from core.symbol_engine.archetypes import validate_archetype_grammar
from core.symbol_engine.symbol_spec import validate_symbol_spec


READABILITY_STATUSES = (
    "symbol_readable",
    "visual_review_required",
    "fallback_component_preview",
    "fallback_bbox_placeholder",
    "deferred_unsupported_symbol",
)

FALLBACK_TO_READABILITY = {
    "symbol_readable": "symbol_readable",
    "block_preferred": "visual_review_required",
    "visual_review_required": "visual_review_required",
    "fallback_component_preview": "fallback_component_preview",
    "fallback_bbox_placeholder": "fallback_bbox_placeholder",
    "deferred_unsupported_symbol": "deferred_unsupported_symbol",
}

MIN_READABLE_FOOTPRINT_MM = 200.0
_BBOX_ONLY_KINDS = frozenset({"outline"})


def _part_kinds(spec: dict[str, Any]) -> set[str]:
    kinds: set[str] = set()
    for part in spec.get("parts", []):
        if isinstance(part, dict) and isinstance(part.get("kind"), str):
            kinds.add(part["kind"])
    return kinds


def _check(name: str, status: str, message: str) -> dict[str, str]:
    return {"name": name, "status": status, "message": message}


def _run_readability_checks(spec: dict[str, Any]) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    kinds = _part_kinds(spec)
    footprint = spec.get("footprint", {})
    width = float(footprint.get("width_mm", 0))
    depth = float(footprint.get("depth_mm", 0))
    readability = spec.get("readability_constraints", {})

    if kinds.issubset(_BBOX_ONLY_KINDS):
        checks.append(_check("not_single_bbox", "fail", "symbol parts are outline-only bbox placeholder"))
    else:
        checks.append(_check("not_single_bbox", "pass", "symbol includes non-bbox readability parts"))

    grammar_errors = validate_archetype_grammar(spec)
    if grammar_errors:
        checks.append(
            _check(
                "archetype_grammar",
                "fail",
                "; ".join(grammar_errors[:3]) + (" ..." if len(grammar_errors) > 3 else ""),
            )
        )
    else:
        checks.append(_check("archetype_grammar", "pass", "archetype required parts and placement rules satisfied"))

    min_parts = 2
    if isinstance(readability, dict) and isinstance(readability.get("min_part_count"), int):
        min_parts = max(1, int(readability["min_part_count"]))
    if len(spec.get("parts", [])) >= min_parts:
        checks.append(_check("min_part_count", "pass", f"symbol has at least {min_parts} parts"))
    else:
        checks.append(_check("min_part_count", "fail", f"symbol has fewer than {min_parts} parts"))

    if width >= MIN_READABLE_FOOTPRINT_MM and depth >= MIN_READABLE_FOOTPRINT_MM:
        checks.append(_check("min_footprint", "pass", "footprint meets minimum readable size"))
    else:
        checks.append(
            _check(
                "min_footprint",
                "fail",
                f"footprint {width}x{depth} mm is below minimum {MIN_READABLE_FOOTPRINT_MM} mm",
            )
        )

    orientation = spec.get("orientation", {})
    facing = str(orientation.get("facing", "unspecified")) if isinstance(orientation, dict) else "unspecified"
    if "orientation_marker" in kinds or facing != "unspecified":
        checks.append(_check("orientation_cue", "pass", "facing or orientation_marker is present"))
    else:
        checks.append(_check("orientation_cue", "fail", "cannot infer viewing or seating orientation"))

    allows_text = bool(readability.get("allows_text_labels")) if isinstance(readability, dict) else False
    allows_dim = bool(readability.get("allows_dimensions")) if isinstance(readability, dict) else False
    if not allows_text and not allows_dim:
        checks.append(_check("no_text_or_dimension_labels", "pass", "readability does not rely on text or dimensions"))
    else:
        checks.append(_check("no_text_or_dimension_labels", "fail", "text or dimension labels are enabled"))

    schema_errors = validate_symbol_spec(spec)
    if schema_errors:
        checks.append(_check("symbol_spec_valid", "fail", "; ".join(schema_errors[:2])))
    else:
        checks.append(_check("symbol_spec_valid", "pass", "SYMBOL_SPEC schema and semantic guards pass"))

    return checks


def resolve_readability_status(spec: dict[str, Any], checks: list[dict[str, str]]) -> str:
    fallback_mode = str(spec.get("fallback_policy", {}).get("mode", ""))
    if fallback_mode != "symbol_readable":
        return FALLBACK_TO_READABILITY.get(fallback_mode, "visual_review_required")

    failed = [item for item in checks if item["status"] == "fail"]
    if not failed:
        return "symbol_readable"

    critical = {item["name"] for item in failed}
    if critical == {"not_single_bbox"} or "symbol_spec_valid" in critical:
        return "fallback_bbox_placeholder"
    return "visual_review_required"


def build_symbol_readability_report(
    spec: dict[str, Any],
    *,
    report_id: str | None = None,
    source_object_id: str | None = None,
) -> dict[str, Any]:
    """Build a machine-readable readability report for a SYMBOL_SPEC."""

    checks = _run_readability_checks(spec)
    readability_status = resolve_readability_status(spec, checks)
    kinds = _part_kinds(spec)
    object_id = source_object_id
    evidence = spec.get("evidence")
    if object_id is None and isinstance(evidence, dict):
        object_id = evidence.get("source_object_id")

    return {
        "version": "0.1",
        "report_id": report_id or f"symbol-readability-{spec.get('symbol_id', 'unknown')}",
        "symbol_id": spec.get("symbol_id"),
        "archetype": spec.get("archetype"),
        "object_type": spec.get("object_type"),
        "source_object_id": object_id,
        "readability_status": readability_status,
        "fallback_policy_mode": spec.get("fallback_policy", {}).get("mode"),
        "part_kinds": sorted(kinds),
        "part_count": len(spec.get("parts", [])),
        "checks": checks,
        "failed_check_count": sum(1 for item in checks if item["status"] == "fail"),
        "geometry_verified": False,
        "evidence_state": "non_cad_readability_only",
        "limitations": [
            "readability_status does not imply geometry_verified",
            "visual review may still be required for aesthetic clarity",
        ],
    }


def evaluate_object_spec_readability(spec: dict[str, Any]) -> dict[str, Any]:
    """Map OBJECT_SPEC to SYMBOL_SPEC and return a combined readability report."""

    from core.symbol_engine.object_to_symbol import object_spec_to_symbol_spec

    mapping = object_spec_to_symbol_spec(spec)
    report = build_symbol_readability_report(
        mapping.symbol_spec,
        source_object_id=spec.get("object_id"),
    )
    report["mapping_status"] = mapping.mapping_status
    report["mapping_reason"] = mapping.mapping_reason
    return report
