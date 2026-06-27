from __future__ import annotations

import math
from typing import Sequence

from cad_agent.domain.common import BBox2D, Point2D, StrictModel
from cad_agent.domain.primitives import Primitive


class ResolvedPose(StrictModel):
    center: Point2D
    rotation_deg: float = 0


class Footprint(StrictModel):
    object_id: str
    kind: str
    points: list[tuple[float, float]]
    bbox: BBox2D


def rectangle_points(*, center: Point2D, width: float, depth: float, rotation_deg: float = 0) -> list[tuple[float, float]]:
    half_width = width / 2
    half_depth = depth / 2
    local = [
        (-half_width, -half_depth),
        (half_width, -half_depth),
        (half_width, half_depth),
        (-half_width, half_depth),
    ]
    return [_rotate_translate(point, center=center, rotation_deg=rotation_deg) for point in local]


def ellipse_points(
    *,
    center: Point2D,
    width: float,
    depth: float,
    rotation_deg: float = 0,
    segments: int = 24,
) -> list[tuple[float, float]]:
    if segments < 8:
        raise ValueError("ellipse_points requires at least 8 segments")
    radius_x = width / 2
    radius_y = depth / 2
    local = [
        (math.cos((math.tau * index) / segments) * radius_x, math.sin((math.tau * index) / segments) * radius_y)
        for index in range(segments)
    ]
    return [_rotate_translate(point, center=center, rotation_deg=rotation_deg) for point in local]


def footprint_from_points(*, object_id: str, kind: str, points: Sequence[Sequence[float]]) -> Footprint:
    normalized = [(float(point[0]), float(point[1])) for point in points]
    return Footprint(object_id=object_id, kind=kind, points=normalized, bbox=bbox_for_points(normalized))


def bbox_for_points(points: Sequence[Sequence[float]]) -> BBox2D:
    if not points:
        raise ValueError("bbox_for_points requires at least one point")
    xs = [float(point[0]) for point in points]
    ys = [float(point[1]) for point in points]
    return (_clean(min(xs)), _clean(min(ys)), _clean(max(xs)), _clean(max(ys)))


def primitive_bbox(primitive: Primitive) -> BBox2D:
    geometry = primitive.geometry
    if primitive.primitive_type in {"polyline", "rectangle"} and "points" in geometry:
        return bbox_for_points(geometry["points"])
    if primitive.primitive_type == "circle":
        center = geometry["center"]
        radius = float(geometry["radius"])
        return (
            _clean(float(center[0]) - radius),
            _clean(float(center[1]) - radius),
            _clean(float(center[0]) + radius),
            _clean(float(center[1]) + radius),
        )
    if primitive.primitive_type == "ellipse" and "points" in geometry:
        return bbox_for_points(geometry["points"])
    if primitive.primitive_type == "line":
        return bbox_for_points([geometry["start"], geometry["end"]])
    if primitive.primitive_type == "text":
        position = geometry["position"]
        return (_clean(float(position[0])), _clean(float(position[1])), _clean(float(position[0])), _clean(float(position[1])))
    raise ValueError(f"Cannot compute bbox for primitive: {primitive.primitive_id}")


def primitives_bbox(primitives: Sequence[Primitive]) -> BBox2D:
    boxes = [primitive_bbox(primitive) for primitive in primitives]
    if not boxes:
        raise ValueError("primitives_bbox requires at least one primitive")
    return (
        _clean(min(box[0] for box in boxes)),
        _clean(min(box[1] for box in boxes)),
        _clean(max(box[2] for box in boxes)),
        _clean(max(box[3] for box in boxes)),
    )


def boxes_overlap(first: BBox2D, second: BBox2D, *, min_gap: float = 0) -> bool:
    return not (
        first[2] + min_gap <= second[0]
        or second[2] + min_gap <= first[0]
        or first[3] + min_gap <= second[1]
        or second[3] + min_gap <= first[1]
    )


def overlap_area(first: BBox2D, second: BBox2D) -> float:
    width = max(0.0, min(first[2], second[2]) - max(first[0], second[0]))
    depth = max(0.0, min(first[3], second[3]) - max(first[1], second[1]))
    return width * depth


def points3(points: Sequence[Sequence[float]]) -> list[list[float]]:
    return [[float(point[0]), float(point[1]), 0.0] for point in points]


def offset_point(pose: ResolvedPose, x: float, y: float) -> tuple[float, float]:
    return _rotate_translate((x, y), center=pose.center, rotation_deg=pose.rotation_deg)


def _rotate_translate(point: tuple[float, float], *, center: Point2D, rotation_deg: float) -> tuple[float, float]:
    angle = math.radians(rotation_deg)
    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)
    x, y = point
    cx, cy = center
    return (_clean(x * cos_angle - y * sin_angle + cx), _clean(x * sin_angle + y * cos_angle + cy))


def _clean(value: float) -> float:
    rounded = round(float(value), 10)
    return 0.0 if rounded == -0.0 else rounded
