"""Claim-level contracts for CAD capability registry rows (V-PROOF-00 / V-PROOF-03)."""

from __future__ import annotations

from typing import Any

from core.verification.evidence_vocabulary import GEOMETRY_VERIFIED_EVIDENCE_STATES


def validate_registry_claim_contracts(registry: dict[str, Any]) -> list[str]:
    """Validate claim_level-specific rules not expressible in the subset JSON Schema validator."""

    errors: list[str] = []
    capabilities = registry.get("capabilities")
    if not isinstance(capabilities, list):
        return ["capabilities must be a list."]

    seen_ids: set[str] = set()
    for index, row in enumerate(capabilities):
        if not isinstance(row, dict):
            errors.append(f"capabilities[{index}] must be an object.")
            continue
        prefix = f"capabilities[{index}]"
        capability_id = str(row.get("capability_id", ""))
        if not capability_id:
            errors.append(f"{prefix}.capability_id is required.")
            continue
        if capability_id in seen_ids:
            errors.append(f"Duplicate capability_id: {capability_id}")
        seen_ids.add(capability_id)

        claim_level = row.get("claim_level")
        evidence = row.get("evidence")
        cad_case = row.get("cad_case")
        deferred_reason = row.get("deferred_reason")

        if claim_level == "deferred" and not isinstance(deferred_reason, str):
            errors.append(f"{prefix}.deferred_reason is required when claim_level=deferred.")

        if claim_level in {"smoke", "verified", "showcase"}:
            if not isinstance(cad_case, dict):
                errors.append(f"{prefix}.cad_case is required when claim_level={claim_level}.")
            elif cad_case.get("case_kind") in {None, "", "none"}:
                errors.append(f"{prefix}.cad_case.case_kind must name an executable case when claim_level={claim_level}.")

        if claim_level in {"verified", "showcase"}:
            if not isinstance(evidence, dict):
                errors.append(f"{prefix}.evidence is required when claim_level={claim_level}.")
            else:
                evidence_state = evidence.get("evidence_state")
                if evidence_state not in GEOMETRY_VERIFIED_EVIDENCE_STATES:
                    errors.append(
                        f"{prefix}.evidence.evidence_state must be a geometry-verified state when claim_level={claim_level}."
                    )
                if not isinstance(evidence.get("report_path"), str) or not evidence.get("report_path"):
                    errors.append(f"{prefix}.evidence.report_path is required when claim_level={claim_level}.")

        if claim_level == "none" and isinstance(evidence, dict):
            evidence_state = evidence.get("evidence_state")
            if evidence_state in GEOMETRY_VERIFIED_EVIDENCE_STATES:
                errors.append(f"{prefix}.evidence must not claim geometry verification when claim_level=none.")

    return errors
