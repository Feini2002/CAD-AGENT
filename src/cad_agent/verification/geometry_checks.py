from __future__ import annotations

from collections.abc import Iterable

from cad_agent.domain.common import BBox2D, Point2D


def bbox_area(box: BBox2D | None) -> float:
    if box is None:
        return 0.0
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def bbox_center(box: BBox2D) -> Point2D:
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def bbox_inside(inner: BBox2D, outer: BBox2D, *, tolerance: float = 1e-6) -> bool:
    return (
        inner[0] >= outer[0] - tolerance
        and inner[1] >= outer[1] - tolerance
        and inner[2] <= outer[2] + tolerance
        and inner[3] <= outer[3] + tolerance
    )


def union_bboxes(boxes: Iterable[BBox2D]) -> BBox2D | None:
    normalized = list(boxes)
    if not normalized:
        return None
    return (
        min(box[0] for box in normalized),
        min(box[1] for box in normalized),
        max(box[2] for box in normalized),
        max(box[3] for box in normalized),
    )


def overlap_area(first: BBox2D, second: BBox2D) -> float:
    width = max(0.0, min(first[2], second[2]) - max(first[0], second[0]))
    depth = max(0.0, min(first[3], second[3]) - max(first[1], second[1]))
    return width * depth


def overlap_ratio(first: BBox2D, second: BBox2D) -> float:
    denominator = min(bbox_area(first), bbox_area(second))
    if denominator <= 0:
        return 0.0
    return overlap_area(first, second) / denominator


def bboxes_close(first: BBox2D, second: BBox2D, *, tolerance: float = 1.0) -> bool:
    return all(abs(left - right) <= tolerance for left, right in zip(first, second, strict=True))
