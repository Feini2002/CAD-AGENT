from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from core.geometry_backends.registry import get_geometry_backend, list_geometry_backends


def load_plan() -> dict[str, object]:
    return json.loads((PROJECT_ROOT / "examples/plans/draw_test_cabinet.json").read_text(encoding="utf-8"))


class GeometryBackendTests(unittest.TestCase):
    def test_builtin_rect2d_backend_validates_cad_plan_geometry(self) -> None:
        backend = get_geometry_backend("cad_plan_rect2d")

        result = backend.validate_plan_geometry(load_plan(), boundary={"min": [0, 0], "max": [3000, 1800]})

        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["backend_id"], "cad_plan_rect2d")
        self.assertIn("expected_bbox", {check["name"] for check in result["checks"]})

    def test_geometry_registry_exposes_default_rect_and_orthogonal_backends(self) -> None:
        catalog = list_geometry_backends()
        by_id = {backend["backend_id"]: backend for backend in catalog}

        self.assertTrue(by_id["rect2d"]["available"])
        self.assertFalse(by_id["rect2d"]["requires_dependency"])
        self.assertIn("bbox_shell", by_id["rect2d"]["supported_models"])
        self.assertTrue(by_id["orthogonal_polygon"]["available"])
        self.assertFalse(by_id["orthogonal_polygon"]["requires_dependency"])
        self.assertIn("shell_model.boundary", by_id["orthogonal_polygon"]["supported_models"])

    def test_external_geometry_backend_slots_are_declared_without_becoming_dependencies(self) -> None:
        catalog = list_geometry_backends()
        by_id = {backend["backend_id"]: backend for backend in catalog}

        for backend_id in ["cadquery", "build123d", "ifcopenshell"]:
            self.assertIn(backend_id, by_id)
            self.assertFalse(by_id[backend_id]["available"])
            self.assertTrue(by_id[backend_id]["requires_dependency"])


if __name__ == "__main__":
    unittest.main()
