from __future__ import annotations

from pydantic import Field

from cad_agent.domain.common import BBox2D, StrictModel
from cad_agent.domain.patch import CadPatch
from cad_agent.planning.footprints import primitive_bbox


class PatchImpact(StrictModel):
    entity_count: int
    impact_bbox: BBox2D | None = None
    semantic_entity_counts: dict[str, int] = Field(default_factory=dict)


def estimate_patch_impact(patch: CadPatch) -> PatchImpact:
    boxes: list[BBox2D] = []
    semantic_counts: dict[str, int] = {}
    for operation in patch.operations:
        semantic_counts[operation.semantic_object_id] = len(operation.primitives)
        for primitive in operation.primitives:
            boxes.append(primitive_bbox(primitive))
    impact_bbox = None
    if boxes:
        impact_bbox = (
            min(box[0] for box in boxes),
            min(box[1] for box in boxes),
            max(box[2] for box in boxes),
            max(box[3] for box in boxes),
        )
    return PatchImpact(entity_count=sum(semantic_counts.values()), impact_bbox=impact_bbox, semantic_entity_counts=semantic_counts)

