from __future__ import annotations

from pathlib import Path

from core.verification.entity_level_evidence import minimal_verified_entity_evidence
from core.verification.evidence_contract import (
    EVIDENCE_CAD_CAPABILITY_VERIFIED,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE,
    GEOMETRY_VERIFIED_BY_READBACK,
    SCREENSHOT_NOT_APPLICABLE,
    SCREENSHOT_VISUAL_AID_ONLY,
)


def block_alpha_geometry_verified_payload() -> dict[str, object]:
    return {
        "status": "geometry_verified",
        "evidence_state": EVIDENCE_READBACK_GEOMETRY_VERIFIED,
        "geometry_accuracy": GEOMETRY_VERIFIED_BY_READBACK,
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
        "checks": [
            {"name": "created_handles_scope", "status": "pass"},
            {"name": "block_name", "status": "pass"},
            {"name": "insertion_point", "status": "pass"},
            {"name": "rotation", "status": "pass"},
            {"name": "scale", "status": "pass"},
            {"name": "layer", "status": "pass"},
            {"name": "bbox", "status": "pass"},
        ],
        "created_handles": ["BR1"],
        "entity": {
            "handle": "BR1",
            "type": "block_reference",
            "block_name": "CODEX_TEST_BLOCK_001",
            "insertion_point": [1200.0, 800.0, 0.0],
            "rotation": 0.0,
            "scale": [1.0, 1.0, 1.0],
            "layer": "CODEX_PREVIEW",
            "bbox": {"min": [1200.0, 800.0], "max": [2100.0, 1250.0]},
        },
    }


def cad_capability_verified_probe_payload(**extra: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "status": "cad_capability_verified",
        "contract_version": "phase-r-cad-v1",
        "evidence_state": EVIDENCE_CAD_CAPABILITY_VERIFIED,
        "geometry_accuracy": GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE,
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
        "contract": {"version": "phase-r-cad-v1", "entities": {}, "deferred_verification": []},
        "deferred_verification": [],
        "limitations": [],
        "entity_evidence": minimal_verified_entity_evidence(),
        "checks": [
            {"name": "handle_readback_count", "status": "pass"},
            {"name": "readback_type_counts", "status": "pass"},
        ],
    }
    payload.update(extra)
    return payload


def readback_geometry_verified_payload(
    *,
    handle: str = "H1",
    screenshot: Path | None = None,
) -> dict[str, object]:
    screenshot_value = str(screenshot) if screenshot is not None else ""
    return {
        "status": "geometry_verified",
        "evidence_state": EVIDENCE_READBACK_GEOMETRY_VERIFIED,
        "geometry_accuracy": GEOMETRY_VERIFIED_BY_READBACK,
        "screenshot_role": SCREENSHOT_VISUAL_AID_ONLY if screenshot_value else SCREENSHOT_NOT_APPLICABLE,
        "evidence": {
            "execution_summary": {"created_handles": [handle]},
            "screenshot": screenshot_value,
        },
        "actual": {
            "entities": [{"handle": handle, "type": "line", "layer": "CODEX_PREVIEW"}],
            "created_handles": [handle],
        },
        "checks": [
            {"name": "readback_scope", "status": "pass"},
            {"name": "created_handles_scope", "status": "pass"},
        ],
    }
