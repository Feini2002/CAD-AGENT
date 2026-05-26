from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.execution.execute_plan import execute_plan_file
from core.execution.symbol_glyph_execute import expected_readback_type_counts
from core.verification.evidence_contract import (
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    NON_CAD_GEOMETRY_ACCURACY,
)
from core.verification.fake_cad_driver import FakeCadDriver
from core.verification.symbol_glyph_cad_smoke import (
    BASE_POINT,
    build_desk_glyph_plan,
    default_symbol_spec_path,
    load_symbol_spec,
    resolve_symbol_glyph_output_dir,
    run_symbol_glyph_cad_smoke,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class SymbolGlyphCadSmokeTests(unittest.TestCase):
    def test_desk_glyph_plan_expected_readback_counts(self) -> None:
        spec = load_symbol_spec(default_symbol_spec_path(project_root=PROJECT_ROOT))
        plan = build_desk_glyph_plan(spec, base_point=BASE_POINT)
        expected = expected_readback_type_counts(plan["object"]["glyph_primitives"])
        self.assertEqual(expected, {"circle": 1, "line": 9})

    def test_execute_plan_draw_symbol_glyph_writes_preview_handles(self) -> None:
        spec = load_symbol_spec(default_symbol_spec_path(project_root=PROJECT_ROOT))
        plan = build_desk_glyph_plan(spec, base_point=BASE_POINT)
        plan_path = artifact_path("execute_plan", "symbol_glyph_desk.json")
        plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")

        driver = FakeCadDriver()
        result = execute_plan_file(plan_path, driver=driver)

        self.assertEqual(result["intent"], "draw_symbol_glyph")
        self.assertEqual(result["layer"], "CODEX_PREVIEW")
        self.assertEqual(result["expected_readback_type_counts"], {"circle": 1, "line": 9})
        self.assertEqual(len(result["created_handles"]), 10)

    def test_symbol_glyph_smoke_verifies_created_handles(self) -> None:
        output_dir = artifact_path("symbol_glyph_cad_smoke", "pass")
        report = run_symbol_glyph_cad_smoke(driver_factory=FakeCadDriver, output_dir=output_dir)

        self.assertEqual(report["status"], "geometry_verified")
        self.assertTrue(report["geometry_verified"])
        self.assertEqual(report["evidence_state"], EVIDENCE_READBACK_GEOMETRY_VERIFIED)
        self.assertEqual(report["geometry_accuracy"], GEOMETRY_VERIFIED_BY_READBACK)
        self.assertEqual(report["symbol_readability_status"], "symbol_readable")
        self.assertEqual(report["expected"]["type_counts"], {"circle": 1, "line": 9})
        self.assertEqual(report["actual"]["type_counts"], {"circle": 1, "line": 9})
        self.assertTrue(all(check["status"] == "pass" for check in report["checks"]))
        self.assertTrue((output_dir / "symbol_glyph_cad_smoke_report.json").is_file())
        self.assertTrue((output_dir / "symbol_glyph_execution_summary.json").is_file())

    def test_symbol_glyph_smoke_no_cad_is_deferred(self) -> None:
        report = run_symbol_glyph_cad_smoke(
            output_dir=artifact_path("symbol_glyph_cad_smoke", "no_cad"),
            include_cad=False,
        )
        self.assertEqual(report["status"], "deferred")
        self.assertFalse(report["geometry_verified"])
        self.assertEqual(report["evidence_state"], EVIDENCE_DEFERRED_CAD_READBACK)
        self.assertEqual(report["geometry_accuracy"], NON_CAD_GEOMETRY_ACCURACY)

    def test_symbol_glyph_smoke_output_must_stay_under_project_output(self) -> None:
        output_dir = resolve_symbol_glyph_output_dir(
            Path("output/validation_runs/symbol-glyph-safe-output"),
            project_root=PROJECT_ROOT,
        )
        self.assertTrue(output_dir.is_relative_to((PROJECT_ROOT / "output").resolve()))

        with self.assertRaisesRegex(ValueError, "output_dir must stay under project output directory"):
            resolve_symbol_glyph_output_dir(PROJECT_ROOT.parent / "outside-symbol-glyph", project_root=PROJECT_ROOT)


if __name__ == "__main__":
    unittest.main()
