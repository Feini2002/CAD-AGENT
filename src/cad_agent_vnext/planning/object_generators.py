from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from cad_agent_vnext.domain.primitives import Primitive
from cad_agent_vnext.domain.scene import Dimensions2D, SceneObjectSpec
from cad_agent_vnext.planning.footprints import (
    Footprint,
    ResolvedPose,
    ellipse_points,
    footprint_from_points,
    offset_point,
    points3,
    rectangle_points,
)
from cad_agent_vnext.planning.object_catalog import CatalogEntry, ObjectCatalog, load_object_catalog


class UnsupportedObjectError(ValueError):
    def __init__(self, *, kind: str, reason: str) -> None:
        self.kind = kind
        self.reason = reason
        super().__init__(f"{reason}:{kind}")


class ObjectGenerator(Protocol):
    kind: str

    def footprint(self, spec: SceneObjectSpec, pose: ResolvedPose, dimensions: Dimensions2D) -> Footprint:
        ...

    def primitives(self, spec: SceneObjectSpec, pose: ResolvedPose, dimensions: Dimensions2D) -> list[Primitive]:
        ...


@dataclass(frozen=True)
class _Generator:
    kind: str

    def footprint(self, spec: SceneObjectSpec, pose: ResolvedPose, dimensions: Dimensions2D) -> Footprint:
        points = _outer_points(kind=self.kind, pose=pose, dimensions=dimensions)
        return footprint_from_points(object_id=spec.id, kind=spec.kind, points=points)

    def primitives(self, spec: SceneObjectSpec, pose: ResolvedPose, dimensions: Dimensions2D) -> list[Primitive]:
        if self.kind == "desk":
            return [_polyline(spec, "top", _outer_points(kind=self.kind, pose=pose, dimensions=dimensions))]
        if self.kind == "monitor":
            outer = _outer_points(kind=self.kind, pose=pose, dimensions=dimensions)
            return [
                _polyline(spec, "screen", outer),
                _line(spec, "stand", pose.center, offset_point(pose, 0, -dimensions.depth * 0.35)),
            ]
        if self.kind == "keyboard":
            outer = _outer_points(kind=self.kind, pose=pose, dimensions=dimensions)
            return [
                _polyline(spec, "body", outer),
                _line(
                    spec,
                    "split-a",
                    offset_point(pose, -dimensions.width * 0.25, -dimensions.depth * 0.35),
                    offset_point(pose, -dimensions.width * 0.25, dimensions.depth * 0.35),
                ),
                _line(
                    spec,
                    "split-b",
                    offset_point(pose, dimensions.width * 0.25, -dimensions.depth * 0.35),
                    offset_point(pose, dimensions.width * 0.25, dimensions.depth * 0.35),
                ),
            ]
        if self.kind == "mouse":
            return [_polyline(spec, "body", _outer_points(kind=self.kind, pose=pose, dimensions=dimensions))]
        if self.kind == "vase":
            radius = min(dimensions.width, dimensions.depth) / 2
            return [
                Primitive(
                    primitive_id=f"{spec.id}:body",
                    semantic_object_id=spec.id,
                    primitive_type="circle",
                    geometry={"center": [pose.center[0], pose.center[1], 0.0], "radius": radius},
                    layer="CODEX_PREVIEW",
                    style_token="preview.default",
                    expected_entity_type="CIRCLE",
                )
            ]
        raise UnsupportedObjectError(kind=self.kind, reason="unsupported_object_kind")


GENERATORS: dict[str, _Generator] = {
    "desk_plan_2d_v1": _Generator(kind="desk"),
    "monitor_plan_2d_v1": _Generator(kind="monitor"),
    "keyboard_plan_2d_v1": _Generator(kind="keyboard"),
    "mouse_plan_2d_v1": _Generator(kind="mouse"),
    "vase_plan_2d_v1": _Generator(kind="vase"),
}


def generator_for_catalog_entry(entry: CatalogEntry) -> ObjectGenerator:
    generator = GENERATORS.get(entry.generator)
    if generator is None:
        raise UnsupportedObjectError(kind=entry.kind, reason="unsupported_generator")
    return generator


def footprint_for_object(
    spec: SceneObjectSpec,
    pose: ResolvedPose,
    *,
    catalog: ObjectCatalog | None = None,
) -> Footprint:
    resolved_catalog = catalog or load_object_catalog()
    lookup = resolved_catalog.lookup(spec.kind)
    if lookup.entry is None:
        raise UnsupportedObjectError(kind=spec.kind, reason=lookup.reason or "unsupported_object_kind")
    dimensions = resolved_catalog.resolve_dimensions(spec.kind, spec.dimensions)
    return generator_for_catalog_entry(lookup.entry).footprint(spec, pose, dimensions)


def generate_object_primitives(
    spec: SceneObjectSpec,
    pose: ResolvedPose,
    *,
    catalog: ObjectCatalog | None = None,
) -> list[Primitive]:
    resolved_catalog = catalog or load_object_catalog()
    lookup = resolved_catalog.lookup(spec.kind)
    if lookup.entry is None:
        raise UnsupportedObjectError(kind=spec.kind, reason=lookup.reason or "unsupported_object_kind")
    dimensions = resolved_catalog.resolve_dimensions(spec.kind, spec.dimensions)
    return generator_for_catalog_entry(lookup.entry).primitives(spec, pose, dimensions)


def _outer_points(*, kind: str, pose: ResolvedPose, dimensions: Dimensions2D) -> list[tuple[float, float]]:
    if kind == "mouse":
        return ellipse_points(center=pose.center, width=dimensions.width, depth=dimensions.depth, rotation_deg=pose.rotation_deg)
    return rectangle_points(center=pose.center, width=dimensions.width, depth=dimensions.depth, rotation_deg=pose.rotation_deg)


def _polyline(spec: SceneObjectSpec, suffix: str, points: list[tuple[float, float]]) -> Primitive:
    return Primitive(
        primitive_id=f"{spec.id}:{suffix}",
        semantic_object_id=spec.id,
        primitive_type="polyline",
        geometry={"points": points3(points), "closed": True},
        layer="CODEX_PREVIEW",
        style_token="preview.default",
        expected_entity_type="LWPOLYLINE",
    )


def _line(spec: SceneObjectSpec, suffix: str, start: tuple[float, float], end: tuple[float, float]) -> Primitive:
    return Primitive(
        primitive_id=f"{spec.id}:{suffix}",
        semantic_object_id=spec.id,
        primitive_type="line",
        geometry={"start": [start[0], start[1], 0.0], "end": [end[0], end[1], 0.0]},
        layer="CODEX_PREVIEW",
        style_token="preview.default",
        expected_entity_type="LINE",
    )
