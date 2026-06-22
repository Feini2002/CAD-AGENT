from __future__ import annotations

from typing import Literal

from pydantic import Field

from cad_agent_vnext.domain.common import StrictModel


class ToolEnvelope(StrictModel):
    schema_version: Literal["tool-envelope/v1"] = "tool-envelope/v1"
    status: Literal["ok", "blocked", "failed"]
    run_id: str
    artifact_refs: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    summary: str
