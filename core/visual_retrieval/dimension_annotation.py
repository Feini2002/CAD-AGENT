"""Dimension annotation planning for visually retrieved CAD blocks."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from core.safety.policy import PREVIEW_LAYER
from core.visual_retrieval.cad_block_retrieval import BlockCandidate


@dataclass(frozen=True)
class DimensionOperation:
    axis: str
    start_point: list[float]
    end_point: list[float]
    text_position: list[float]
    expected_value: float
    text_override: str


@dataclass(frozen=True)
class DimensionAnnotationPlan:
    intent: str
    target_handle: str
    target_block_name: str
    target_layer: str
    target_bbox: dict[str, list[float]]
    target_size: list[float]
    output_layer: str
    text_height: float
    dimension_offset: float
    dimensions: list[DimensionOperation]
    view_bbox: dict[str, list[float]]
    evidence_source: str = "active_dwg_block_bbox"
    safety: dict[str, bool] = field(
        default_factory=lambda: {
            "preview_layer_only": True,
            "modify_target_block": False,
            "save_dwg": False,
            "delete_entities": False,
            "modify_formal_layers": False,
        }
    )
    evidence_boundary: dict[str, str] = field(
        default_factory=lambda: {
            "visual": "visual and semantic retrieval selects the target block",
            "cad": "dimension values are derived from the active DWG block bbox readback",
            "not_claimed": "screenshot pixels are not used as true CAD dimensions",
        }
    )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["dimensions"] = [asdict(item) for item in self.dimensions]
        return payload


def build_bbox_dimension_plan(
    candidate: BlockCandidate,
    *,
    output_layer: str = PREVIEW_LAYER,
    dimension_offset: float | None = None,
    text_height: float | None = None,
) -> DimensionAnnotationPlan:
    bbox = candidate.bbox
    if not bbox:
        raise ValueError("Cannot annotate dimensions without candidate bbox.")
    minimum = bbox.get("min")
    maximum = bbox.get("max")
    if not (
        isinstance(minimum, list)
        and isinstance(maximum, list)
        and len(minimum) >= 2
        and len(maximum) >= 2
    ):
        raise ValueError("Candidate bbox must contain min/max xy coordinates.")

    min_x = float(min(minimum[0], maximum[0]))
    min_y = float(min(minimum[1], maximum[1]))
    max_x = float(max(minimum[0], maximum[0]))
    max_y = float(max(minimum[1], maximum[1]))
    width = max_x - min_x
    depth = max_y - min_y
    if width <= 0 or depth <= 0:
        raise ValueError("Candidate bbox has non-positive width/depth.")

    offset = float(dimension_offset if dimension_offset is not None else max(180.0, min(width, depth) * 0.24))
    height = float(text_height if text_height is not None else max(70.0, min(130.0, min(width, depth) * 0.1)))
    z = 0.0
    mid_x = (min_x + max_x) / 2.0
    mid_y = (min_y + max_y) / 2.0

    dimensions = [
        DimensionOperation(
            axis="width",
            start_point=[min_x, min_y, z],
            end_point=[max_x, min_y, z],
            text_position=[mid_x, min_y - offset, z],
            expected_value=width,
            text_override=_format_measure(width),
        ),
        DimensionOperation(
            axis="depth",
            start_point=[min_x, min_y, z],
            end_point=[min_x, max_y, z],
            text_position=[min_x - offset, mid_y, z],
            expected_value=depth,
            text_override=_format_measure(depth),
        ),
    ]

    return DimensionAnnotationPlan(
        intent="annotate_retrieved_block_dimensions",
        target_handle=candidate.handle,
        target_block_name=candidate.block_name,
        target_layer=candidate.layer,
        target_bbox={"min": [min_x, min_y], "max": [max_x, max_y]},
        target_size=[width, depth],
        output_layer=output_layer,
        text_height=height,
        dimension_offset=offset,
        dimensions=dimensions,
        view_bbox={
            "min": [min_x - offset * 2.0, min_y - offset * 2.0],
            "max": [max_x + offset * 0.75, max_y + offset * 0.75],
        },
    )


def execute_dimension_annotation_plan(driver: Any, plan: DimensionAnnotationPlan) -> dict[str, Any]:
    created_handles: list[str] = []
    operations: list[dict[str, Any]] = []
    for dimension in plan.dimensions:
        result = driver.add_dimension(
            start_point=dimension.start_point,
            end_point=dimension.end_point,
            text_position=dimension.text_position,
            layer=plan.output_layer,
            color="cyan",
            textheight=plan.text_height,
            text_override=dimension.text_override,
        )
        handles = _collect_handles(result)
        created_handles.extend(handles)
        operations.append(
            {
                "axis": dimension.axis,
                "expected_value": dimension.expected_value,
                "text_override": dimension.text_override,
                "created_handles": handles,
            }
        )

    readback = []
    if hasattr(driver, "snapshot_handles"):
        readback = driver.snapshot_handles(handles=created_handles, layer=plan.output_layer)
    dimension_readback = [entity for entity in readback if entity.get("type") == "dimension"]

    refresh = None
    if hasattr(driver, "refresh_view"):
        refresh = driver.refresh_view()

    return {
        "status": "pass" if len(dimension_readback) == len(plan.dimensions) else "needs_review",
        "created_handles": created_handles,
        "created_handle_count": len(created_handles),
        "operations": operations,
        "readback_entities": readback,
        "dimension_readback_count": len(dimension_readback),
        "layer": plan.output_layer,
        "refresh": refresh,
        "safety": {
            "wrote_cad": bool(created_handles),
            "wrote_layer": plan.output_layer,
            "saved_dwg": False,
            "deleted_entities": False,
            "modified_target_block": False,
            "modified_formal_layers": False,
        },
    }


def _format_measure(value: float) -> str:
    rounded = round(value)
    if abs(value - rounded) < 1e-6:
        return str(int(rounded))
    return f"{value:.3f}".rstrip("0").rstrip(".")


def _collect_handles(result: object) -> list[str]:
    if result is None:
        return []
    if isinstance(result, str):
        return [result]
    if isinstance(result, dict):
        if "handles" in result and isinstance(result["handles"], list):
            return [str(handle) for handle in result["handles"]]
        if "handle" in result:
            return [str(result["handle"])]
    if isinstance(result, list):
        return [str(item) for item in result]
    return []
