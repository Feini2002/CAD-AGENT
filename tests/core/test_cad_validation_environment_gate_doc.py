from __future__ import annotations

import unittest

from tests.bootstrap import PROJECT_ROOT


class CadValidationEnvironmentGateDocTests(unittest.TestCase):
    def test_cad_val_02_document_exists_and_states_environment_boundary(self) -> None:
        path = PROJECT_ROOT / "docs" / "verification" / "cad_validation_environment_gate.md"

        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")

        required_phrases = [
            "CAD-VAL-02",
            "--environment-optional",
            "geometry_gate",
            "infrastructure_gate",
            "infrastructure_debt",
            "unit_tests",
            "render_preview_check",
            "python_import_pillow",
            "非几何失败",
            "不得声称",
            "geometry_verified",
            "created-handle readback",
        ]

        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
