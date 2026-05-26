from __future__ import annotations

import json
import unittest

from core.orchestrator.scene_registry import (
    DEFAULT_SCENE_ID,
    load_scene_registry,
    match_trigger_terms,
    scene_is_registered,
    scenes_by_maturity,
    validate_scene_registry,
)
from core.schemas.validator import validate_json
from tests.bootstrap import PROJECT_ROOT


class SceneRegistryTests(unittest.TestCase):
    def test_example_registry_validates_against_schema(self) -> None:
        path = PROJECT_ROOT / "examples/orchestrator/scene_registry.json"
        errors = validate_json(PROJECT_ROOT / "core/schemas/scene_registry.schema.json", path)
        self.assertEqual(errors, [])

    def test_load_scene_registry_includes_required_scenes(self) -> None:
        registry = load_scene_registry()
        scene_ids = {scene["scene_id"] for scene in registry["scenes"]}
        self.assertEqual(registry["default_scene_id"], DEFAULT_SCENE_ID)
        self.assertTrue({"no_scene", "office", "residential", "restaurant", "commercial_fitout"}.issubset(scene_ids))
        self.assertEqual(validate_scene_registry(registry), [])

    def test_no_scene_is_core_only_without_triggers(self) -> None:
        registry = load_scene_registry()
        no_scene = next(scene for scene in registry["scenes"] if scene["scene_id"] == "no_scene")
        self.assertEqual(no_scene["maturity"], "core_only")
        self.assertEqual(no_scene["trigger_terms"], [])
        self.assertFalse(no_scene["may_bypass_core"])

    def test_commercial_fitout_is_scaffold_with_workflows(self) -> None:
        registry = load_scene_registry()
        fitout = next(scene for scene in registry["scenes"] if scene["scene_id"] == "commercial_fitout")
        self.assertEqual(fitout["maturity"], "scaffold")
        self.assertIn("blank_store_to_layout", fitout["workflows"])
        self.assertTrue(scene_is_registered(registry, "commercial_fitout"))

    def test_match_trigger_terms_finds_office_and_fitout(self) -> None:
        registry = load_scene_registry()
        matches = match_trigger_terms(registry, "需要办公室和工装门店布局")
        matched_ids = {scene["scene_id"] for scene in matches}
        self.assertIn("office", matched_ids)
        self.assertIn("commercial_fitout", matched_ids)
        self.assertNotIn("no_scene", matched_ids)

    def test_scenes_by_maturity_filters_beta(self) -> None:
        registry = load_scene_registry()
        beta = scenes_by_maturity(registry, "scene_beta")
        self.assertEqual({scene["scene_id"] for scene in beta}, {"office", "residential", "restaurant"})

    def test_invalid_registry_rejects_bypass_core(self) -> None:
        registry = json.loads(
            (PROJECT_ROOT / "examples/orchestrator/scene_registry.json").read_text(encoding="utf-8")
        )
        registry["scenes"][0]["may_bypass_core"] = True
        errors = validate_scene_registry(registry)
        self.assertTrue(any("may_bypass_core" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
