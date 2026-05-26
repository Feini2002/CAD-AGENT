"""Minimal drawing_standard_profile: role → preview layer / semantic style mapping (BETA-CAD-BLOCK-04)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from core.safety.policy import PREVIEW_LAYER


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRAWING_STANDARDS_DIR = PROJECT_ROOT / "libraries" / "drawing_standards"
LAYER_PRESETS_DIR = PROJECT_ROOT / "libraries" / "layer_presets"
DEFAULT_DRAWING_STANDARD_PROFILE_ID = "codex_preview_beta"


class UnknownDrawingStandardError(ValueError):
    """Raised when a drawing standard profile or layer preset is missing."""


def load_layer_preset(preset_id: str, *, library: Path = LAYER_PRESETS_DIR) -> dict[str, Any]:
    path = library / f"{preset_id}.json"
    if not path.exists():
        available = sorted(item.stem for item in library.glob("*.json"))
        raise UnknownDrawingStandardError(
            f"Unknown layer preset '{preset_id}'. Available: {available}"
        )
    with path.open("r", encoding="utf-8") as file:
        preset = json.load(file)
    if not isinstance(preset, dict):
        raise ValueError(f"Layer preset must be a JSON object: {path}")
    layers = preset.get("layers")
    if not isinstance(layers, dict) or not layers:
        raise ValueError(f"Layer preset must define layers: {path}")
    return preset


def load_drawing_standard_profile(
    profile_id: str = DEFAULT_DRAWING_STANDARD_PROFILE_ID,
    *,
    library: Path = DRAWING_STANDARDS_DIR,
) -> dict[str, Any]:
    path = library / f"{profile_id}.json"
    if not path.exists():
        available = sorted(item.stem for item in library.glob("*.json"))
        raise UnknownDrawingStandardError(
            f"Unknown drawing standard profile '{profile_id}'. Available: {available}"
        )
    with path.open("r", encoding="utf-8") as file:
        profile = json.load(file)
    if not isinstance(profile, dict):
        raise ValueError(f"Drawing standard profile must be a JSON object: {path}")
    return profile


@lru_cache(maxsize=4)
def _cached_layer_preset(preset_id: str) -> dict[str, Any]:
    return load_layer_preset(preset_id)


def semantic_layer_name(profile: dict[str, Any], layer_role: str) -> str:
    preset_id = str(profile.get("layer_preset_id", ""))
    preset = _cached_layer_preset(preset_id)
    layers = preset["layers"]
    if layer_role in layers:
        return str(layers[layer_role])
    if "preview" in layers:
        return str(layers["preview"])
    raise UnknownDrawingStandardError(f"layer_role {layer_role!r} not in preset {preset_id!r}")


def resolve_layer_role(
    profile: dict[str, Any],
    layer_role: str,
    *,
    for_cad_execution: bool = True,
) -> str:
    """Resolve a layer role to a CAD layer name.

    Under preview_only policy, CAD execution always targets CODEX_PREVIEW.
    Semantic (formal) layer names are still available via for_cad_execution=False.
    """

    policy = profile.get("block_layer_policy", {})
    if (
        for_cad_execution
        and str(policy.get("cad_execution_mode", "")) == "preview_only"
    ):
        return str(policy.get("preview_layer", PREVIEW_LAYER))
    return semantic_layer_name(profile, layer_role)


def resolve_object_role(profile: dict[str, Any], object_role: str) -> dict[str, Any]:
    bindings = profile.get("object_role_bindings", {})
    if not isinstance(bindings, dict):
        raise ValueError("object_role_bindings must be an object")
    binding = bindings.get(object_role)
    if not isinstance(binding, dict):
        raise UnknownDrawingStandardError(
            f"object_role {object_role!r} not defined in profile {profile.get('profile_id')!r}"
        )
    layer_role = str(binding.get("layer_role", "preview"))
    return {
        "object_role": object_role,
        "layer_role": layer_role,
        "semantic_layer": semantic_layer_name(profile, layer_role),
        "resolved_layer": resolve_layer_role(profile, layer_role, for_cad_execution=True),
        "text_style_id": binding.get("text_style_id"),
        "dim_style_id": binding.get("dim_style_id"),
        "hatch_style_id": binding.get("hatch_style_id"),
    }


def _style_id_for_primitive(
    profile: dict[str, Any],
    *,
    primitive: str,
    layer_role: str,
) -> tuple[str, dict[str, Any]]:
    style_id = ""
    catalog: dict[str, Any] = {}
    bindings = profile.get("object_role_bindings", {})
    if isinstance(bindings, dict):
        for binding in bindings.values():
            if not isinstance(binding, dict):
                continue
            if str(binding.get("layer_role", "")) != layer_role:
                continue
            if primitive == "text" and binding.get("text_style_id"):
                style_id = str(binding["text_style_id"])
                catalog = profile.get("text_styles", {})
                break
            if primitive == "dimension" and binding.get("dim_style_id"):
                style_id = str(binding["dim_style_id"])
                catalog = profile.get("dim_styles", {})
                break
            if primitive == "hatch" and binding.get("hatch_style_id"):
                style_id = str(binding["hatch_style_id"])
                catalog = profile.get("hatch_styles", {})
                break

    if not style_id:
        defaults = {
            "text": ("CAD_LABEL", profile.get("text_styles", {})),
            "dimension": ("CAD_DIM_MM", profile.get("dim_styles", {})),
            "hatch": ("HATCH_CLEARANCE", profile.get("hatch_styles", {})),
        }
        if primitive in defaults:
            style_id, catalog = defaults[primitive]  # type: ignore[assignment]
            style_id = str(style_id)
            catalog = catalog if isinstance(catalog, dict) else {}
    return style_id, catalog


def resolve_primitive_style(
    profile: dict[str, Any],
    *,
    primitive: str,
    layer_role: str = "preview",
) -> dict[str, Any]:
    """Resolve text/dim/hatch style dicts for a primitive + layer role."""

    styles: dict[str, Any] = {"primitive": primitive, "layer_role": layer_role}
    styles["resolved_layer"] = resolve_layer_role(profile, layer_role, for_cad_execution=True)
    styles["semantic_layer"] = semantic_layer_name(profile, layer_role)

    style_id, catalog = _style_id_for_primitive(profile, primitive=primitive, layer_role=layer_role)
    if style_id and isinstance(catalog, dict) and style_id in catalog:
        styles["style_id"] = style_id
        styles["style"] = dict(catalog[style_id])
    return styles


def apply_drawing_standard_to_plan(
    plan: dict[str, Any],
    *,
    profile: dict[str, Any] | None = None,
    object_role: str | None = None,
) -> dict[str, Any]:
    """Apply profile resolution to plan.drawing (layer_role → layer for CAD execution)."""

    profile = profile or load_drawing_standard_profile(
        str(plan.get("drawing_standard_profile_id", DEFAULT_DRAWING_STANDARD_PROFILE_ID))
    )
    drawing = plan.setdefault("drawing", {})
    if not isinstance(drawing, dict):
        raise ValueError("plan.drawing must be an object")

    layer_role = str(
        drawing.get("layer_role")
        or plan.get("layer_role")
        or profile.get("block_layer_policy", {}).get("insert_layer_role_default", "preview")
    )
    if object_role:
        role_info = resolve_object_role(profile, object_role)
        layer_role = str(role_info["layer_role"])
        plan["object_role"] = object_role
        plan["drawing_standard_resolution"] = role_info
    else:
        plan["drawing_standard_resolution"] = {
            "layer_role": layer_role,
            "semantic_layer": semantic_layer_name(profile, layer_role),
            "resolved_layer": resolve_layer_role(profile, layer_role, for_cad_execution=True),
        }

    drawing["layer_role"] = layer_role
    drawing["layer"] = resolve_layer_role(profile, layer_role, for_cad_execution=True)
    drawing["semantic_layer"] = semantic_layer_name(profile, layer_role)
    plan["drawing_standard_profile_id"] = str(profile.get("profile_id", DEFAULT_DRAWING_STANDARD_PROFILE_ID))
    return plan


def layer_mapping_resolution(
    *,
    profile: dict[str, Any] | None = None,
    layer_role: str,
    readback_layer: str,
) -> dict[str, str]:
    """Structured layer mapping result for verification probes."""

    profile = profile or load_drawing_standard_profile()
    expected = resolve_layer_role(profile, layer_role, for_cad_execution=True)
    semantic = semantic_layer_name(profile, layer_role)
    if readback_layer == expected:
        return {
            "status": "pass",
            "message": f"layer_role={layer_role} → {expected} (semantic={semantic})",
        }
    if not readback_layer and str(profile.get("block_layer_policy", {}).get("cad_execution_mode")) == "preview_only":
        return {
            "status": "deferred",
            "message": f"layer_role={layer_role} targets {expected}; readback not available",
        }
    return {
        "status": "fail",
        "message": f"expected {expected!r}, readback {readback_layer!r} (semantic={semantic})",
        "failure_category": "layer_mismatch",
    }
