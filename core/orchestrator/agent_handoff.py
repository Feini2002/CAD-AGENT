"""Explicit handoff packets between model-backed pipeline Agents."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "handoff_packet/v1"
PASS_STATUSES = {"pass", "ready", "ok", "complete", "complete_for_current_scope"}


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return ""


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _strings(value: Any) -> list[str]:
    result: list[str] = []
    for item in _list(value):
        text = str(item).strip()
        if text and text not in result:
            result.append(text)
    return result


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _packet_status(output: dict[str, Any]) -> str:
    provider = _dict(output.get("modelProviderStatus"))
    status = str(output.get("status") or output.get("decision") or "").casefold()
    if provider.get("modelUnavailable") is True or provider.get("schemaValid") is False or provider.get("blocking") is True:
        return "blocked"
    if status in {"needs_more_evidence", "needs-more-evidence"}:
        return "needs_more_evidence"
    if status in PASS_STATUSES:
        return "ready"
    return "blocked"


def _decision_summary(output: dict[str, Any]) -> str:
    parts = [
        str(output.get("decision") or ""),
        str(output.get("status") or ""),
        str(output.get("drawingTypeDecision") or ""),
        str(output.get("styleDecision") or ""),
        str(output.get("designReview") or ""),
    ]
    return " ".join(part for part in parts if part).strip()


def build_handoff_packet(
    agent_output: dict[str, Any],
    *,
    from_agent_id: str,
    to_agent_ids: list[str],
    source_path: str | Path,
) -> dict[str, Any]:
    """Build a downstream-readable packet without adding new evidence claims."""

    status = _packet_status(agent_output)
    blocking = _strings(agent_output.get("blockingReasons"))
    missing = _strings(agent_output.get("evidenceMissing"))
    next_required = _strings(agent_output.get("nextRequiredEvidence"))
    return {
        "schemaVersion": SCHEMA_VERSION,
        "fromAgentId": str(from_agent_id),
        "toAgentIds": [str(item) for item in to_agent_ids],
        "status": status,
        "decisionSummary": _decision_summary(agent_output),
        "statePatch": _dict(agent_output.get("statePatch")),
        "evidenceRefs": _strings(agent_output.get("evidenceRefs")) or _strings(agent_output.get("evidenceUsed")),
        "evidenceMissing": missing,
        "openQuestions": _strings(agent_output.get("openQuestions")),
        "downstreamInstructions": [*blocking, *next_required],
        "allowedClaims": _strings(agent_output.get("finalResponseAllowedClaims")),
        "forbiddenClaims": [
            "must not invent evidence",
            "must not claim CAD geometry without created handles/readback",
            "must not claim user acceptance",
            "must not authorize CAD writes, deletes, saves, registry mutation, or table C claims",
        ],
        "sha256OfSourceOutput": _sha256(Path(source_path)),
    }


def validate_handoff_packet(packet: dict[str, Any]) -> dict[str, Any]:
    required = [
        "schemaVersion",
        "fromAgentId",
        "toAgentIds",
        "status",
        "decisionSummary",
        "statePatch",
        "evidenceRefs",
        "evidenceMissing",
        "openQuestions",
        "downstreamInstructions",
        "allowedClaims",
        "forbiddenClaims",
        "sha256OfSourceOutput",
    ]
    missing = [field for field in required if field not in packet]
    issues: list[str] = []
    if packet.get("schemaVersion") != SCHEMA_VERSION:
        issues.append("schemaVersion must be handoff_packet/v1")
    if str(packet.get("status") or "") not in {"ready", "blocked", "needs_more_evidence"}:
        issues.append("status must be ready, blocked, or needs_more_evidence")
    for field in (
        "toAgentIds",
        "evidenceRefs",
        "evidenceMissing",
        "openQuestions",
        "downstreamInstructions",
        "allowedClaims",
        "forbiddenClaims",
    ):
        if field in packet and not isinstance(packet.get(field), list):
            issues.append(f"{field} must be a list")
    if "statePatch" in packet and not isinstance(packet.get("statePatch"), dict):
        issues.append("statePatch must be an object")
    return {
        "status": "pass" if not missing and not issues else "fail",
        "missingFields": missing,
        "issues": issues,
    }
