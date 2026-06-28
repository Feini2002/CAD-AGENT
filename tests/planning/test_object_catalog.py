from __future__ import annotations

from pathlib import Path

import pytest

from cad_agent.domain.scene import Dimensions2D
from cad_agent.planning.object_catalog import (
    DEFAULT_OBJECT_CATALOG_PATH,
    ObjectCatalogError,
    load_object_catalog,
)


ROOT = Path(__file__).resolve().parents[2]


def test_object_catalog_loads_gate0_atomic_objects():
    catalog = load_object_catalog()

    assert DEFAULT_OBJECT_CATALOG_PATH == ROOT / "src" / "cad_agent" / "resources" / "object_catalog.json"
    assert catalog.schema_version == "object-catalog/v1"
    assert set(catalog.objects) == {"desk", "monitor", "keyboard", "mouse", "vase", "lamp"}
    assert catalog.objects["desk"].default_dimensions == Dimensions2D(width=1400, depth=700)
    assert catalog.objects["desk"].min_dimensions == Dimensions2D(width=900, depth=500)
    assert catalog.objects["desk"].max_dimensions == Dimensions2D(width=2400, depth=1200)
    assert catalog.objects["mouse"].generator == "mouse_plan_2d_v1"
    assert catalog.objects["lamp"].default_dimensions == Dimensions2D(width=180, depth=180)
    assert catalog.objects["lamp"].generator == "lamp_plan_2d_v1"


def test_catalog_resolves_default_and_explicit_dimensions_with_min_max():
    catalog = load_object_catalog()

    assert catalog.resolve_dimensions("desk") == Dimensions2D(width=1400, depth=700)
    assert catalog.resolve_dimensions("desk", Dimensions2D(width=1200, depth=600)) == Dimensions2D(width=1200, depth=600)

    with pytest.raises(ObjectCatalogError, match="dimension_below_min"):
        catalog.resolve_dimensions("desk", Dimensions2D(width=800, depth=600))

    with pytest.raises(ObjectCatalogError, match="dimension_above_max"):
        catalog.resolve_dimensions("desk", Dimensions2D(width=2500, depth=600))


def test_catalog_unknown_object_returns_structured_unsupported():
    catalog = load_object_catalog()

    result = catalog.lookup("printer")

    assert result.status == "unsupported"
    assert result.kind == "printer"
    assert result.reason == "unsupported_object_kind"
    assert result.entry is None


def test_catalog_file_is_not_a_computer_desk_scene_template():
    source = DEFAULT_OBJECT_CATALOG_PATH.read_text(encoding="utf-8")

    assert "computer_desk_scene" not in source
    assert "desk_with_monitor_keyboard_mouse_vase" not in source
    assert "generate_computer_desk_scene" not in source
