from __future__ import annotations

from typing import Literal

from pydantic import Field

from cad_agent_vnext.domain.common import BBox2D, StrictModel, Units


class DrawingEntitySnapshot(StrictModel):
    handle: str
    entity_type: str
    layer: str
    bbox: BBox2D | None


class DrawingSnapshot(StrictModel):
    schema_version: Literal["drawing-snapshot/v1"]
    run_id: str
    document_id: str
    units: Units
    current_space: str
    active_layer: str
    saved: bool | None
    target_region: BBox2D | None
    nearby_entities: list[DrawingEntitySnapshot] = Field(default_factory=list)
    snapshot_hash: str
