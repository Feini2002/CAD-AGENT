from __future__ import annotations

import json
import unittest

from tests.bootstrap import PROJECT_ROOT

from core.composition_engine.catalog_loader import load_composition_template_catalog
from core.composition_engine.composition_template_catalog import COMPOSITION_TEMPLATES
from core.composition_engine.drawing_policy import resolve_composition_object_drawing_flags
from core.composition_engine.templates import composition_to_cad_plans, create_composition_spec
from core.schemas.validator import validate_json


class CompositionCatalogTests(unittest.TestCase):
    def test_catalog_json_validates_against_schema(self) -> None:
        errors = validate_json(
            PROJECT_ROOT / "core" / "schemas" / "composition_template_catalog.schema.json",
            PROJECT_ROOT / "libraries" / "composition_templates" / "catalog.json",
        )
        self.assertEqual(errors, [])

    def test_loader_rejects_catalog_objects_with_preview_labels(self) -> None:
        invalid = {
            "version": "0.1",
            "catalog_id": "composition_templates",
            "templates": {
                "bedroom_bed_rug": {
                    "name": "Bedroom Bed + Rug Set",
                    "domain": "residential",
                    "objects": [
                        {
                            "instance_id": "bed-01",
                            "type": "bed",
                            "name": "Bed",
                            "role": "primary_bed",
                            "base_point": [0, 0, 0],
                            "size": {"width": 2000, "depth": 1500, "height": 600},
                            "include_label": True,
                        }
                    ],
                }
            },
        }
        path = PROJECT_ROOT / "output" / "test_artifacts" / "composition_catalog_invalid.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(invalid), encoding="utf-8")
        with self.assertRaises(ValueError):
            load_composition_template_catalog(path)

    def test_loader_matches_imported_catalog(self) -> None:
        loaded = load_composition_template_catalog()
        self.assertEqual(set(loaded), set(COMPOSITION_TEMPLATES))
        self.assertIn("bedroom_bed_rug", loaded)
        self.assertIn("office_desk_combo", loaded)

    def test_catalog_objects_default_to_no_labels_or_dimensions(self) -> None:
        for composition_id, template in COMPOSITION_TEMPLATES.items():
            for item in template["objects"]:
                with self.subTest(composition_id=composition_id, instance_id=item["instance_id"]):
                    include_label, include_dimensions = resolve_composition_object_drawing_flags(item)
                    self.assertFalse(include_label)
                    self.assertFalse(include_dimensions)

    def test_bedroom_bed_rug_plans_stay_label_free(self) -> None:
        composition = create_composition_spec("bedroom_bed_rug", persona_role="interior_designer")
        plans = composition_to_cad_plans(composition)
        for plan in plans:
            self.assertFalse(plan["drawing"]["include_label"])
            self.assertFalse(plan["drawing"]["include_dimensions"])


if __name__ == "__main__":
    unittest.main()
