from __future__ import annotations

import unittest

from core.agents.multi_scene_p3_wave import (
    MULTI_SCENE_P3_ACCEPTANCE_DOC,
    MULTI_SCENE_P3_CHILD_ACCEPTANCE_DOCS,
    MULTI_SCENE_P3_PACKAGE_ID,
    assert_multi_scene_p3_wave_contract,
    multi_scene_p3_wave_status_summary,
)
from tests.bootstrap import PROJECT_ROOT


class RestProd04MultiSceneP3RollupTests(unittest.TestCase):
    def test_multi_scene_p3_wave_contract(self) -> None:
        assert_multi_scene_p3_wave_contract(project_root=PROJECT_ROOT)

    def test_multi_scene_p3_status_summary(self) -> None:
        summary = multi_scene_p3_wave_status_summary(project_root=PROJECT_ROOT)
        self.assertTrue(summary["docs_present"])
        self.assertEqual(summary["package_id"], MULTI_SCENE_P3_PACKAGE_ID)
        self.assertEqual(summary["scene_count"], 2)
        self.assertEqual(summary["child_package_count"], 6)
        self.assertEqual(summary["alpha_case_count"], 19)
        self.assertEqual(summary["beta_case_count"], 17)
        self.assertEqual(summary["readback_geometry_verified_count"], 0)

    def test_acceptance_doc_closes_office_and_restaurant_p3(self) -> None:
        text = (PROJECT_ROOT / MULTI_SCENE_P3_ACCEPTANCE_DOC).read_text(encoding="utf-8")
        for phrase in (
            "REST-PROD-04",
            "OFFICE-PROD-03",
            "REST-PROD-03",
            "assert_multi_scene_p3_wave_contract",
            "benchmark_pass_non_cad",
            "blocked_expected_non_cad",
            "V-PROOF-24",
            "BETA-SCENE-03",
            "geometry_verified",
            "不得声称",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_child_acceptance_docs_exist(self) -> None:
        for rel in MULTI_SCENE_P3_CHILD_ACCEPTANCE_DOCS:
            with self.subTest(doc=rel):
                self.assertTrue((PROJECT_ROOT / rel).is_file())

    def test_handoff_indexes_rest_prod_04(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(encoding="utf-8")
        self.assertIn("REST-PROD-04", handoff)
        self.assertIn("rest_prod_04_multi_scene_p3_rollup_acceptance.md", handoff)


if __name__ == "__main__":
    unittest.main()
