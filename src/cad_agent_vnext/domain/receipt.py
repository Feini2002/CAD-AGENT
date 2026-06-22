from __future__ import annotations

from typing import Literal

from pydantic import Field

from cad_agent_vnext.domain.common import BBox2D, StrictModel


class EntityReadback(StrictModel):
    handle: str
    entity_type: str
    layer: str
    bbox: BBox2D | None


class ExecutionReceipt(StrictModel):
    schema_version: Literal["execution-receipt/v1"]
    run_id: str
    transaction_id: str
    backend: str
    status: Literal["succeeded", "blocked", "failed"]
    semantic_to_handles: dict[str, list[str]] = Field(default_factory=dict)
    entities: list[EntityReadback] = Field(default_factory=list)
    created_handles: list[str] = Field(default_factory=list)
    updated_handles: list[str] = Field(default_factory=list)
    deleted_handles: list[str] = Field(default_factory=list)
    saved_current_dwg: Literal[False] = False
    rollback_token: str | None = None
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
