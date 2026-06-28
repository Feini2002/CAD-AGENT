from __future__ import annotations

from pathlib import Path

import pytest

from cad_agent.domain.scene import Dimensions2D, PlacementIntent, SceneObjectSpec
from cad_agent.planning.footprints import ResolvedPose, bbox_for_points, primitives_bbox
from cad_agent.planning.object_catalog import load_object_catalog
from cad_agent.planning.object_generators import (
    UnsupportedObjectError,
    footprint_for_object,
    generate_object_primitives,
    generator_for_catalog_entry,
)


ROOT = Path(__file__).resolve().parents[2]


def object_spec(kind: str, *, object_id: str | None = None, dimensions: Dimensions2D | None = None) -> SceneObjectSpec:
    return SceneObjectSpec(
        id=object_id or kind,
        kind=kind,
        dimensions=dimensions,
        placement=PlacementIntent(mode="absolute", base_point=(0, 0)),
    )


@pytest.mark.parametrize("kind", ["desk", "monitor", "keyboard", "mouse", "vase", "lamp"])
def test_each_gate0_generator_propagates_semantic_id_layer_and_budget(kind: str):
    catalog = load_object_catalog()
    spec = object_spec(kind, object_id=f"{kind}-01")
    pose = ResolvedPose(center=(1000, 500), rotation_deg=0)

    primitives = generate_object_primitives(spec, pose, catalog=catalog)

    assert 1 <= len(primitives) <= 6
    assert {primitive.semantic_object_id for primitive in primitives} == {f"{kind}-01"}
    assert all(primitive.primitive_id.startswith(f"{kind}-01:") for primitive in primitives)
    assert all(primitive.layer == "CODEX_PREVIEW" for primitive in primitives)
    assert all(primitive.expected_entity_type for primitive in primitives)


@pytest.mark.parametrize("kind", ["desk", "monitor", "keyboard", "mouse", "vase", "lamp"])
def test_footprint_and_primitives_bbox_match_for_default_specs(kind: str):
    catalog = load_object_catalog()
    spec = object_spec(kind)
    pose = ResolvedPose(center=(300, 200), rotation_deg=0)

    footprint = footprint_for_object(spec, pose, catalog=catalog)
    primitives = generate_object_primitives(spec, pose, catalog=catalog)

    assert primitives_bbox(primitives) == footprint.bbox


def test_rotation_is_supported_without_object_specific_coordinates():
    catalog = load_object_catalog()
    spec = object_spec("desk", dimensions=Dimensions2D(width=1000, depth=500))
    pose = ResolvedPose(center=(0, 0), rotation_deg=90)

    footprint = footprint_for_object(spec, pose, catalog=catalog)
    first_primitive = generate_object_primitives(spec, pose, catalog=catalog)[0]

    assert footprint.bbox == (-250.0, -500.0, 250.0, 500.0)
    assert bbox_for_points(first_primitive.geometry["points"]) == footprint.bbox


def test_lamp_generator_emits_base_and_shade_semantics_without_backend_access():
    catalog = load_object_catalog()
    spec = object_spec("lamp", object_id="lamp-01")
    pose = ResolvedPose(center=(700, 420), rotation_deg=0)

    primitives = generate_object_primitives(spec, pose, catalog=catalog)

    assert [primitive.primitive_id for primitive in primitives] == ["lamp-01:base", "lamp-01:shade"]
    assert [primitive.primitive_type for primitive in primitives] == ["circle", "polyline"]
    assert {primitive.expected_entity_type for primitive in primitives} == {"CIRCLE", "LWPOLYLINE"}
    assert all(primitive.layer == "CODEX_PREVIEW" for primitive in primitives)


def test_catalog_unknown_object_returns_structured_unsupported_from_generator():
    catalog = load_object_catalog()
    spec = object_spec("printer")

    with pytest.raises(UnsupportedObjectError) as exc:
        generate_object_primitives(spec, ResolvedPose(center=(0, 0), rotation_deg=0), catalog=catalog)

    assert exc.value.kind == "printer"
    assert exc.value.reason == "unsupported_object_kind"


def test_generators_are_independent_and_do_not_encode_full_scene_or_backend_access():
    source = (ROOT / "src" / "cad_agent" / "planning" / "object_generators.py").read_text(encoding="utf-8")

    forbidden = [
        "generate_computer_desk_scene",
        "computer_desk_scene",
        "desk_with_monitor_keyboard_mouse_vase",
        "backend.",
        "apply_patch",
        "user request",
    ]
    for token in forbidden:
        assert token not in source


def test_every_catalog_entry_has_registered_generator():
    catalog = load_object_catalog()

    for entry in catalog.objects.values():
        generator = generator_for_catalog_entry(entry)
        assert generator.kind == entry.kind
