"""Shared registry claim-level expectations for V-PROOF baselines vs TABLE-C upgrades."""

from __future__ import annotations

from typing import Any

CAD_PROOF_CLAIM_LEVELS = frozenset({"verified", "showcase"})


def is_cad_proof_claim_level(claim_level: str | None) -> bool:
    return str(claim_level or "") in CAD_PROOF_CLAIM_LEVELS


def assert_smoke_or_cad_proof_claim(
    row: dict[str, Any],
    capability_id: str,
    *,
    context: str,
) -> None:
    """V-PROOF rows start as smoke; TABLE-C may promote to showcase/verified with evidence."""

    claim_level = str(row.get("claim_level", ""))
    if claim_level == "smoke":
        return
    if claim_level in CAD_PROOF_CLAIM_LEVELS:
        evidence = row.get("evidence")
        if isinstance(evidence, dict) and str(evidence.get("report_path", "")).strip():
            return
        raise AssertionError(f"{capability_id} has claim_level={claim_level} but missing evidence.report_path")
    raise AssertionError(f"{capability_id} must remain smoke or cad-proof ({context}); got {claim_level!r}")


def assert_no_geometry_claim_without_cad_evidence(
    row: dict[str, Any],
    capability_id: str,
) -> None:
    """Block fresh verified/showcase rows that still carry non-CAD geometry accuracy."""

    if row.get("claim_level") not in CAD_PROOF_CLAIM_LEVELS:
        return
    evidence = row.get("evidence")
    if not isinstance(evidence, dict):
        raise AssertionError(f"{capability_id} must not claim geometry proof without evidence object")
    geometry_accuracy = str(evidence.get("geometry_accuracy", ""))
    if geometry_accuracy == "not_verified_without_cad_readback":
        raise AssertionError(f"{capability_id} must not claim geometry proof without CAD readback")
