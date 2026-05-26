from __future__ import annotations

import json
import shutil
import unittest

from core.verification.drawing_standard_beta_suite import (
    default_suite_path,
    load_drawing_standard_beta_suite,
    run_drawing_standard_beta_suite,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class DrawingStandardBetaSuiteTests(unittest.TestCase):
    def test_beta_cad_block_04_suite_has_six_cases(self) -> None:
        suite = load_drawing_standard_beta_suite(default_suite_path(PROJECT_ROOT))
        self.assertEqual(suite["suite_id"], "drawing-standard-beta-04")
        self.assertEqual(len(suite["cases"]), 6)

    def test_beta_cad_block_04_suite_passes(self) -> None:
        result = run_drawing_standard_beta_suite(
            default_suite_path(PROJECT_ROOT),
            output_root=artifact_path("drawing_standard_beta", "beta_cad_block_04"),
        )
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["summary"], {"total": 6, "passed": 6, "failed": 0})
        self.assertTrue(result["evidence_summary"].get("non_cad_only"))

        summary_path = artifact_path("drawing_standard_beta", "beta_cad_block_04") / "drawing_standard_beta_summary.json"
        self.assertTrue(summary_path.is_file())
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertEqual(summary["status"], "pass")

    def test_beta_cad_block_04_rejects_output_root_outside_project_output(self) -> None:
        output_root = PROJECT_ROOT / "tests" / "outside_drawing_standard_beta"
        try:
            with self.assertRaisesRegex(ValueError, "output_root"):
                run_drawing_standard_beta_suite(default_suite_path(PROJECT_ROOT), output_root=output_root)
        finally:
            if output_root.exists():
                shutil.rmtree(output_root, ignore_errors=True)

    def test_beta_cad_block_04_rejects_unsafe_case_id(self) -> None:
        suite_path = artifact_path("drawing_standard_beta", "unsafe_suite.json")
        suite_path.write_text(
            json.dumps(
                {
                    "suite_id": "unsafe-drawing-standard",
                    "profile_id": "codex_preview_beta",
                    "cases": [
                        {
                            "case_id": "../escape",
                            "layer_role": "preview",
                            "expected": {
                                "layer_role": "preview",
                                "semantic_layer": "CAD_AGENT_PREVIEW",
                                "resolved_layer": "CODEX_PREVIEW",
                            },
                        }
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "case_id"):
            run_drawing_standard_beta_suite(
                suite_path,
                output_root=artifact_path("drawing_standard_beta", "unsafe_suite_out"),
            )


if __name__ == "__main__":
    unittest.main()
