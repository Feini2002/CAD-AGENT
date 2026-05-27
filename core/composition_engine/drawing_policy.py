"""Preview drawing flags for composition-backed CAD plans."""

from __future__ import annotations

from typing import Any

# Composition benchmarks and interior-delivery previews default to geometry-only output.
DEFAULT_COMPOSITION_INCLUDE_LABEL = False
DEFAULT_COMPOSITION_INCLUDE_DIMENSIONS = False


def resolve_composition_object_drawing_flags(item: dict[str, Any]) -> tuple[bool, bool]:
    """Resolve text label and dimension flags for one composition object instance.

    Composition-backed previews are globally geometry-only. Object-level flags are
    ignored so catalog/runtime payloads cannot reintroduce annotation clutter.
    """
    return (
        DEFAULT_COMPOSITION_INCLUDE_LABEL,
        DEFAULT_COMPOSITION_INCLUDE_DIMENSIONS,
    )
