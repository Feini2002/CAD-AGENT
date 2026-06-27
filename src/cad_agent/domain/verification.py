from __future__ import annotations

from typing import Any, Literal

from pydantic import Field

from cad_agent.domain.common import StrictModel


class VerificationCheck(StrictModel):
    check_id: str
    status: Literal["passed", "blocked", "failed"]
    severity: Literal["info", "warning", "blocking"]
    subject_ids: list[str] = Field(default_factory=list)
    expected: dict[str, Any] = Field(default_factory=dict)
    observed: dict[str, Any] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)
    repair_hint: str | None = None


class VerificationReport(StrictModel):
    schema_version: Literal["verification-report/v1"]
    run_id: str
    overall_status: Literal["passed", "blocked", "failed"]
    checks: list[VerificationCheck] = Field(default_factory=list)
    allowed_claims: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
