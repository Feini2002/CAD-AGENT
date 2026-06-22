from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from pydantic import Field

from cad_agent_vnext.domain.common import BBox2D, Point2D, StrictModel
from cad_agent_vnext.domain.drawing import DrawingEntitySnapshot
from cad_agent_vnext.domain.scene import Dimensions2D, SceneObjectSpec, SceneSpec
from cad_agent_vnext.planning.anchors import anchor_point
from cad_agent_vnext.planning.footprints import Footprint, ResolvedPose, boxes_overlap
from cad_agent_vnext.planning.object_catalog import ObjectCatalog, ObjectCatalogError, load_object_catalog
from cad_agent_vnext.planning.object_generators import footprint_for_object
from cad_agent_vnext.planning.relation_graph import build_relation_graph


DEFAULT_MARGIN = 40.0


class RelationSolveResult(StrictModel):
    status: str
    poses: dict[str, ResolvedPose] = Field(default_factory=dict)
    footprints: dict[str, Footprint] = Field(default_factory=dict)
    local_centers: dict[str, Point2D] = Field(default_factory=dict)
    local_bboxes: dict[str, BBox2D] = Field(default_factory=dict)
    unsatisfied_constraints: list[str] = Field(default_factory=list)


@dataclass(frozen=True)
class _Layout:
    spec: SceneObjectSpec
    dimensions: Dimensions2D
    pose: ResolvedPose
    footprint: Footprint
    local_center: Point2D
    local_bbox: BBox2D
    surface_id: str | None
    origin_world: Point2D
    rotation_deg: float


def solve_scene_relations(
    scene: SceneSpec,
    *,
    catalog: ObjectCatalog | None = None,
    nearby_entities: Sequence[DrawingEntitySnapshot] | None = None,
) -> RelationSolveResult:
    resolved_catalog = catalog or load_object_catalog()
    graph = build_relation_graph(list(scene.objects))
    if graph.status != "ok":
        return RelationSolveResult(status="blocked", unsatisfied_constraints=graph.errors)

    by_id = {item.id: item for item in scene.objects}
    layouts: dict[str, _Layout] = {}
    failures: list[str] = []

    for object_id in graph.order:
        spec = by_id[object_id]
        try:
            dimensions = resolved_catalog.resolve_dimensions(spec.kind, spec.dimensions)
        except ObjectCatalogError as exc:
            failures.append(str(exc))
            break

        layout = _layout_object(spec, dimensions=dimensions, layouts=layouts)
        if isinstance(layout, str):
            failures.append(layout)
            break
        failures.extend(_layout_failures(layout, layouts=layouts, nearby_entities=nearby_entities or []))
        layouts[object_id] = layout
        if failures:
            break

    if failures:
        return RelationSolveResult(status="blocked", unsatisfied_constraints=_unique(failures))

    return RelationSolveResult(
        status="succeeded",
        poses={item.id: layouts[item.id].pose for item in scene.objects},
        footprints={item.id: layouts[item.id].footprint for item in scene.objects},
        local_centers={item.id: layouts[item.id].local_center for item in scene.objects},
        local_bboxes={item.id: layouts[item.id].local_bbox for item in scene.objects},
        unsatisfied_constraints=[],
    )


def _layout_object(
    spec: SceneObjectSpec,
    *,
    dimensions: Dimensions2D,
    layouts: dict[str, _Layout],
) -> _Layout | str:
    placement = spec.placement
    if placement.mode == "absolute":
        origin = placement.base_point or (0.0, 0.0)
        rotation = float(placement.rotation_deg)
        local_center = (dimensions.width / 2, dimensions.depth / 2)
        world_center = _local_to_world(origin, local_center, rotation)
        pose = ResolvedPose(center=world_center, rotation_deg=rotation)
        footprint = footprint_for_object(spec, pose, catalog=load_object_catalog())
        return _Layout(
            spec=spec,
            dimensions=dimensions,
            pose=pose,
            footprint=footprint,
            local_center=local_center,
            local_bbox=(0.0, 0.0, dimensions.width, dimensions.depth),
            surface_id=None,
            origin_world=origin,
            rotation_deg=rotation,
        )

    if not placement.on:
        return f"missing_surface:{spec.id}"
    surface = layouts.get(placement.on)
    if surface is None:
        return f"missing_surface:{spec.id}:{placement.on}"

    local_center = _relative_local_center(spec, dimensions=dimensions, layouts=layouts, surface=surface)
    local_bbox = _bbox_around_center(local_center, dimensions)
    world_center = _local_to_world(surface.origin_world, local_center, surface.rotation_deg)
    pose = ResolvedPose(center=world_center, rotation_deg=surface.rotation_deg + float(placement.rotation_deg))
    footprint = footprint_for_object(spec, pose, catalog=load_object_catalog())
    return _Layout(
        spec=spec,
        dimensions=dimensions,
        pose=pose,
        footprint=footprint,
        local_center=local_center,
        local_bbox=local_bbox,
        surface_id=surface.spec.id,
        origin_world=surface.origin_world,
        rotation_deg=surface.rotation_deg,
    )


def _relative_local_center(
    spec: SceneObjectSpec,
    *,
    dimensions: Dimensions2D,
    layouts: dict[str, _Layout],
    surface: _Layout,
) -> Point2D:
    placement = spec.placement
    gap = float(placement.gap if placement.gap is not None else DEFAULT_MARGIN)
    center = _anchor_center(surface.local_bbox, dimensions, placement.anchor or "center", margin=DEFAULT_MARGIN)

    if placement.in_front_of:
        reference = layouts[placement.in_front_of]
        center = (center[0], reference.local_center[1] - reference.dimensions.depth / 2 - gap - dimensions.depth / 2)
    if placement.behind:
        reference = layouts[placement.behind]
        center = (center[0], reference.local_center[1] + reference.dimensions.depth / 2 + gap + dimensions.depth / 2)
    if placement.left_of:
        reference = layouts[placement.left_of]
        center = (reference.local_center[0] - reference.dimensions.width / 2 - gap - dimensions.width / 2, center[1])
    if placement.right_of:
        reference = layouts[placement.right_of]
        center = (reference.local_center[0] + reference.dimensions.width / 2 + gap + dimensions.width / 2, center[1])
    if placement.align_x:
        center = (layouts[placement.align_x].local_center[0], center[1])
    if placement.align_y:
        center = (center[0], layouts[placement.align_y].local_center[1])
    return (_clean(center[0]), _clean(center[1]))


def _anchor_center(surface_bbox: BBox2D, dimensions: Dimensions2D, anchor: str, *, margin: float) -> Point2D:
    x, y = anchor_point(surface_bbox, anchor, margin=margin)
    min_x, min_y, max_x, max_y = surface_bbox
    half_width = dimensions.width / 2
    half_depth = dimensions.depth / 2
    if anchor.startswith("front"):
        y = min_y + margin + half_depth
    elif anchor.startswith("rear"):
        y = max_y - margin - half_depth
    if anchor.endswith("left"):
        x = min_x + half_width
    elif anchor.endswith("right"):
        x = max_x - half_width
    return (
        _clean(min(max(x, min_x + half_width), max_x - half_width)),
        _clean(min(max(y, min_y + half_depth), max_y - half_depth)),
    )


def _layout_failures(
    layout: _Layout,
    *,
    layouts: dict[str, _Layout],
    nearby_entities: Sequence[DrawingEntitySnapshot],
) -> list[str]:
    failures: list[str] = []
    if layout.surface_id:
        surface = layouts[layout.surface_id]
        if not _inside(layout.local_bbox, surface.local_bbox):
            failures.append(f"outside_surface:{layout.spec.id}")
        for other in layouts.values():
            if other.surface_id == layout.surface_id and boxes_overlap(layout.local_bbox, other.local_bbox):
                failures.append(f"overlap:{layout.spec.id}:{other.spec.id}")
    if layout.surface_id:
        for entity in nearby_entities:
            if entity.bbox is not None and boxes_overlap(layout.footprint.bbox, entity.bbox):
                failures.append(f"nearby_collision:{layout.spec.id}:{entity.handle}")
    return failures


def _inside(inner: BBox2D, outer: BBox2D) -> bool:
    return inner[0] >= outer[0] and inner[1] >= outer[1] and inner[2] <= outer[2] and inner[3] <= outer[3]


def _bbox_around_center(center: Point2D, dimensions: Dimensions2D) -> BBox2D:
    return (
        _clean(center[0] - dimensions.width / 2),
        _clean(center[1] - dimensions.depth / 2),
        _clean(center[0] + dimensions.width / 2),
        _clean(center[1] + dimensions.depth / 2),
    )


def _local_to_world(origin: Point2D, point: Point2D, rotation_deg: float) -> Point2D:
    angle = math.radians(rotation_deg)
    x, y = point
    ox, oy = origin
    return (_clean(x * math.cos(angle) - y * math.sin(angle) + ox), _clean(x * math.sin(angle) + y * math.cos(angle) + oy))


def _clean(value: float) -> float:
    rounded = round(float(value), 10)
    return 0.0 if rounded == -0.0 else rounded


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
