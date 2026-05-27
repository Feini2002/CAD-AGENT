from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path

from core.verification.symbol_glyph_cad_matrix import run_symbol_glyph_cad_matrix


class SymbolGlyphCadMatrixTests(unittest.TestCase):
    def test_no_cad_matrix_emits_deferred_suite(self) -> None:
        output_dir = artifact_path("symbol_glyph_cad_matrix", "no_cad")
        report = run_symbol_glyph_cad_matrix(
            root=PROJECT_ROOT,
            output_dir=output_dir,
            include_cad=False,
        )
        self.assertEqual(report["case_count"], 6)
        self.assertEqual(report["status"], "deferred")
        self.assertFalse(report["geometry_verified"])
        matrix_report = output_dir / "symbol_glyph_cad_matrix_report.json"
        self.assertTrue(matrix_report.is_file())
        payload = json.loads(matrix_report.read_text(encoding="utf-8"))
        self.assertEqual(payload["verified_case_count"], 0)


if __name__ == "__main__":
    unittest.main()
