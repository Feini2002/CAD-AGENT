from __future__ import annotations

from typing import Literal

from pydantic import Field

from cad_agent_vnext.domain.common import StrictModel
from cad_agent_vnext.domain.primitives import Primitive


class PatchOperation(StrictModel):
    op_id: str
    action: Literal["create", "update", "delete"]
    semantic_object_id: str
    target_handles: list[str] = Field(default_factory=list)
    primitives: list[Primitive] = Field(default_factory=list)


class CadPatch(StrictModel):
    schema_version: Literal["cad-patch/v1"]
    run_id: str
    transaction_id: str
    target_layer: Literal["CODEX_PREVIEW"]
    operations: list[PatchOperation]
    save_current_dwg: Literal[False] = False
    forbidden_effects: list[str]
