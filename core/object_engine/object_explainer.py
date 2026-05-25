"""Explain OBJECT_SPEC decisions and provenance in Core-native terms."""

from __future__ import annotations

from typing import Any


def _size_sources(object_spec: dict[str, Any]) -> list[dict[str, str]]:
    size = object_spec.get("size", {})
    sources = object_spec.get("size_sources", {}) if isinstance(object_spec.get("size_sources"), dict) else {}
    result: list[dict[str, str]] = []
    if isinstance(size, dict):
        for field in ["width", "depth", "height"]:
            if field in size:
                result.append(
                    {
                        "field": field,
                        "value": str(size[field]),
                        "source": str(sources.get(field, "object_spec.size")),
                    }
                )
    return result


def _component_rationale(object_spec: dict[str, Any]) -> list[dict[str, str]]:
    components = object_spec.get("components", [])
    if not isinstance(components, list):
        return []
    rationale: list[dict[str, str]] = []
    for component in components:
        if not isinstance(component, dict):
            continue
        role = str(component.get("role", "component"))
        component_id = str(component.get("component_id", role))
        rationale.append(
            {
                "component_id": component_id,
                "role": role,
                "reason": f"{role} is part of the {object_spec.get('type', 'object')} construction model.",
            }
        )
    return rationale


def explain_object_spec(
    object_spec: dict[str, Any],
    *,
    style_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    style_profile = style_profile or {}
    style_profile_id = str(
        object_spec.get("style_profile_id")
        or style_profile.get("style_profile_id")
        or style_profile.get("profile_id")
        or ""
    )
    size_sources = _size_sources(object_spec)
    component_rationale = _component_rationale(object_spec)
    object_id = str(object_spec.get("object_id", ""))
    return {
        "status": "ok" if object_id else "invalid",
        "object_id": object_id,
        "summary": (
            f"{object_spec.get('name', 'Object')} is represented as a "
            f"{object_spec.get('type', 'generic')} for {object_spec.get('drawing_intent', 'drawing')}."
        ),
        "size_sources": size_sources,
        "component_rationale": component_rationale,
        "evidence": {
            "object_spec_id": object_id,
            "style_profile_id": style_profile_id,
            "drawing_intent": str(object_spec.get("drawing_intent", "")),
        },
        "warnings": [] if object_id else ["object_id is required for stable provenance."],
    }
