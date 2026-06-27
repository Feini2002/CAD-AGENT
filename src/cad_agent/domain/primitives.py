from __future__ import annotations

from typing import Any, Literal

from cad_agent.domain.common import StrictModel


class Primitive(StrictModel):
    primitive_id: str
    semantic_object_id: str
    primitive_type: Literal["line", "polyline", "rectangle", "circle", "ellipse", "arc", "text"]
    geometry: dict[str, Any]
    layer: Literal["CODEX_PREVIEW"]
    style_token: str
    expected_entity_type: str
