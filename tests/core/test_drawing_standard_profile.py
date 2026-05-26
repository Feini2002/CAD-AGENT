from __future__ import annotations

import unittest

from core.drawing_standard.drawing_standard_profile import (
    DEFAULT_DRAWING_STANDARD_PROFILE_ID,
    UnknownDrawingStandardError,
    apply_drawing_standard_to_plan,
    load_drawing_standard_profile,
    load_layer_preset,
    resolve_layer_role,
    resolve_object_role,
    resolve_primitive_style,
    semantic_layer_name,
)
from core.plan_engine.dry_run_report import create_dry_run_report
from core.plan_engine.validate_plan import validate_plan
from core.schemas.validator import validate_json
from tests.bootstrap import PROJECT_ROOT


class DrawingStandardProfileTests(unittest.TestCase):
    def test_profile_and_layer_preset_validate_against_schema(self) -> None:
        layer_errors = validate_json(
            PROJECT_ROOT / "core/schemas/layer_preset.schema.json",
            PROJECT_ROOT / "libraries/layer_presets/codex_preview_beta.json",
        )
        profile_errors = validate_json(
            PROJECT_ROOT / "core/schemas/drawing_standard_profile.schema.json",
            PROJECT_ROOT / "libraries/drawing_standards/codex_preview_beta.json",
        )
        self.assertEqual(layer_errors, [])
        self.assertEqual(profile_errors, [])
        profile = load_drawing_standard_profile(DEFAULT_DRAWING_STANDARD_PROFILE_ID)
        self.assertEqual(profile["verification_policy"]["screenshot_role"], "not_applicable")

    def test_preview_only_resolves_cad_layer_to_codex_preview(self) -> None:
        profile = load_drawing_standard_profile(DEFAULT_DRAWING_STANDARD_PROFILE_ID)
        self.assertEqual(resolve_layer_role(profile, "furniture", for_cad_execution=True), "CODEX_PREVIEW")
        self.assertEqual(semantic_layer_name(profile, "furniture"), "A-FURN")

    def test_resolve_object_role_includes_styles(self) -> None:
        profile = load_drawing_standard_profile()
        clearance = resolve_object_role(profile, "clearance")
        self.assertEqual(clearance["resolved_layer"], "CODEX_PREVIEW")
        self.assertEqual(clearance["hatch_style_id"], "HATCH_CLEARANCE")

    def test_apply_drawing_standard_to_block_plan(self) -> None:
        plan = {
            "version": "0.1",
            "domain": "generic",
            "intent": "insert_block_alpha",
            "object": {
                "type": "block_reference",
                "name": "Controlled Test Block",
                "block_id": "controlled-test-block-001",
                "cad_identity": {"block_name": "CODEX_TEST_BLOCK_001"},
            },
            "placement": {
                "mode": "absolute",
                "base_point": [1000, 500, 0],
                "rotation": 0,
                "scale": [1, 1, 1],
            },
            "drawing": {},
            "confidence": 1.0,
            "needs_confirmation": False,
            "drawing_standard_profile_id": DEFAULT_DRAWING_STANDARD_PROFILE_ID,
        }
        apply_drawing_standard_to_plan(plan, object_role="block_insert")
        self.assertEqual(plan["drawing"]["layer"], "CODEX_PREVIEW")
        self.assertEqual(plan["drawing"]["layer_role"], "preview")
        self.assertEqual(validate_plan(plan), [])
        dry_run = create_dry_run_report(plan)
        self.assertEqual(dry_run["status"], "valid")
        self.assertEqual(dry_run["layer"], "CODEX_PREVIEW")

    def test_unknown_profile_raises(self) -> None:
        with self.assertRaises(UnknownDrawingStandardError):
            load_drawing_standard_profile("missing-profile")

    def test_unknown_layer_preset_raises(self) -> None:
        with self.assertRaises(UnknownDrawingStandardError):
            load_layer_preset("missing-preset")

    def test_primitive_dimension_style(self) -> None:
        profile = load_drawing_standard_profile()
        styles = resolve_primitive_style(profile, primitive="dimension", layer_role="dimension")
        self.assertEqual(styles["style_id"], "CAD_DIM_MM")
        self.assertEqual(styles["resolved_layer"], "CODEX_PREVIEW")


if __name__ == "__main__":
    unittest.main()
