from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, model_validator

from cad_agent.domain.common import Point2D, StrictModel, Units


class Dimensions2D(StrictModel):
    width: float = Field(gt=0)
    depth: float = Field(gt=0)


class PlacementIntent(StrictModel):
    mode: Literal["absolute", "free_region_center", "relative"]
    base_point: Point2D | None = None
    on: str | None = None
    anchor: str | None = None
    in_front_of: str | None = None
    behind: str | None = None
    left_of: str | None = None
    right_of: str | None = None
    align_x: str | None = None
    align_y: str | None = None
    gap: float | None = None
    rotation_deg: float = 0


class SceneObjectSpec(StrictModel):
    id: str
    kind: str
    dimensions: Dimensions2D | None = None
    placement: PlacementIntent
    parameters: dict[str, Any] = Field(default_factory=dict)


class SceneConstraint(StrictModel):
    id: str
    type: str
    members: list[str] = Field(default_factory=list)
    subject: str | None = None
    reference: str | None = None
    minimum: float | None = None


class SceneSpec(StrictModel):
    schema_version: Literal["scene-spec/v1"]
    run_id: str
    scene_id: str
    units: Units
    view: Literal["plan_2d"]
    objects: list[SceneObjectSpec]
    constraints: list[SceneConstraint] = Field(default_factory=list)
    target_layer: Literal["CODEX_PREVIEW"] = "CODEX_PREVIEW"
    assumptions: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_object_references(self) -> "SceneSpec":
        object_ids = [obj.id for obj in self.objects]
        duplicate_ids = sorted({object_id for object_id in object_ids if object_ids.count(object_id) > 1})
        if duplicate_ids:
            raise ValueError(f"duplicate object id: {', '.join(duplicate_ids)}")

        known_ids = set(object_ids)
        for obj in self.objects:
            placement = obj.placement
            for reference in (
                placement.on,
                placement.in_front_of,
                placement.behind,
                placement.left_of,
                placement.right_of,
                placement.align_x,
                placement.align_y,
            ):
                if reference and reference not in known_ids:
                    raise ValueError(f"unknown object reference: {reference}")

        for constraint in self.constraints:
            references = list(constraint.members)
            if constraint.subject:
                references.append(constraint.subject)
            if constraint.reference:
                references.append(constraint.reference)
            for reference in references:
                if reference not in known_ids:
                    raise ValueError(f"unknown object reference: {reference}")

        return self
