"""Manual DRAWING_MODEL input helpers for CAD-unavailable workflows."""

from __future__ import annotations

from typing import Any

from core.drawing_analysis.entity_summary import summarize_entities


def build_manual_drawing_model(
    *,
    drawing_id: str,
    units: str = "mm",
    spaces: list[dict[str, Any]] | None = None,
    openings: list[dict[str, Any]] | None = None,
    entities: list[dict[str, Any]] | None = None,
    uncertainties: list[str] | None = None,
) -> dict[str, Any]:
    summary = summarize_entities(entities or [])
    layers = summary["layers"] or [{"name": "CODEX_PREVIEW", "role": "preview", "entity_count": 0}]
    return {
        "version": "0.1",
        "drawing_id": drawing_id,
        "source": "manual_json",
        "units": units,
        "layers": layers,
        "entities_summary": summary["entities_summary"],
        "spaces": spaces or [],
        "openings": openings or [],
        "uncertainties": uncertainties or [],
    }
