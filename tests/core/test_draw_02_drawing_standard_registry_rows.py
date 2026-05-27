from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.drawing_standard.drawing_standard_boundary import assert_drawing_standard_boundary_contract
from core.drawing_standard.drawing_standard_registry import (
    DRAW_02_BOUNDARY_DOC,
    DRAW_02_PACKAGE_ID,
    DRAWING_STANDARD_SUITE_CAPABILITY_ID,
    apply_smoke_registry_evidence_writeback,
    assert_drawing_standard_registry_contract,
    build_drawing_standard_registry_rows,
    build_smoke_writeback_requests_from_suite_output,
    capability_id_for_drawing_standard_beta_case,
    run_drawing_standard_registry_no_cad_sync,
    sync_drawing_standard_registry_from_suite,
    SmokeEvidenceWritebackRequest,
)
from core.verification.capability_registry import load_capability_registry, validate_capability_registry
from core.verification.drawing_standard_beta_suite import (
    default_suite_path,
    run_drawing_standard_beta_suite,
)
from core.verification.evidence_vocabulary import EVIDENCE_DRY_RUN_VALID_PLAN_ONLY
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class Draw02DrawingStandardRegistryRowsTests(unittest.TestCase):
    def test_draw_02_registry_contract(self) -> None:
        assert_drawing_standard_boundary_contract(project_root=PROJECT_ROOT)
        assert_drawing_standard_registry_contract(project_root=PROJECT_ROOT)

    def test_build_rows_match_suite_case_count(self) -> None:
        rows = build_drawing_standard_registry_rows(project_root=PROJECT_ROOT)
        self.assertEqual(len(rows), 7)
        self.assertEqual(rows[0]["capability_id"], DRAWING_STANDARD_SUITE_CAPABILITY_ID)

    def test_boundary_doc_states_claim_limits(self) -> None:
        text = (PROJECT_ROOT / DRAW_02_BOUNDARY_DOC).read_text(encoding="utf-8")
        for phrase in (
            "DRAW-02",
            "dry_run_valid_plan_only",
            "apply_smoke_registry_evidence_writeback",
            "V-PROOF-44",
            "RCAD-23",
            "geometry_verified",
            "不得声称",
            "drawing_standard.beta.drawing_standard_beta_04",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_smoke_writeback_updates_evidence_on_pass_report(self) -> None:
        registry = {
            "version": "0.1",
            "registry_id": "test",
            "capabilities": build_drawing_standard_registry_rows(project_root=PROJECT_ROOT)[:1],
        }
        report_path = artifact_path("draw_02", "smoke_case_pass.json")
        report_path.write_text(
            json.dumps({"status": "pass", "case_id": "role_furniture_preview_layer"}),
            encoding="utf-8",
        )
        rel = str(report_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
        result = apply_smoke_registry_evidence_writeback(
            registry,
            SmokeEvidenceWritebackRequest(
                capability_id=DRAWING_STANDARD_SUITE_CAPABILITY_ID,
                report_path=rel,
            ),
            project_root=PROJECT_ROOT,
            dry_run=False,
        )
        self.assertEqual(result.status, "applied")
        row = registry["capabilities"][0]
        self.assertEqual(row["evidence"]["evidence_state"], EVIDENCE_DRY_RUN_VALID_PLAN_ONLY)
        self.assertEqual(row["evidence"]["report_path"], rel)
        self.assertEqual(validate_capability_registry(registry), [])

    def test_smoke_writeback_rejects_non_pass_report(self) -> None:
        registry = {
            "version": "0.1",
            "registry_id": "test",
            "capabilities": build_drawing_standard_registry_rows(project_root=PROJECT_ROOT)[:1],
        }
        report_path = artifact_path("draw_02", "smoke_case_fail.json")
        report_path.write_text(json.dumps({"status": "fail"}), encoding="utf-8")
        rel = str(report_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
        result = apply_smoke_registry_evidence_writeback(
            registry,
            SmokeEvidenceWritebackRequest(
                capability_id=DRAWING_STANDARD_SUITE_CAPABILITY_ID,
                report_path=rel,
            ),
            project_root=PROJECT_ROOT,
            dry_run=True,
        )
        self.assertEqual(result.status, "rejected")

    def test_sync_from_suite_output_writes_smoke_paths_without_downgrading_verified_rows(self) -> None:
        output_root = artifact_path("draw_02", "suite_sync")
        suite_result = run_drawing_standard_beta_suite(
            default_suite_path(PROJECT_ROOT),
            output_root=output_root,
        )
        self.assertEqual(suite_result["status"], "pass")

        registry = json.loads(
            (
                PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json"
            ).read_text(encoding="utf-8")
        )
        results = sync_drawing_standard_registry_from_suite(
            registry,
            suite_result,
            output_root=output_root,
            project_root=PROJECT_ROOT,
            dry_run=True,
        )
        self.assertEqual(len(results), 7)
        applied = [item for item in results if item.status == "applied"]
        rejected = [item for item in results if item.status == "rejected"]
        self.assertEqual(len(applied), 5)
        self.assertEqual(len(rejected), 2)
        self.assertTrue(all("claim_level=smoke" in item.message for item in rejected))

        requests = build_smoke_writeback_requests_from_suite_output(
            suite_result,
            output_root=output_root,
            project_root=PROJECT_ROOT,
        )
        self.assertEqual(len(requests), 7)
        self.assertEqual(
            requests[1].capability_id,
            capability_id_for_drawing_standard_beta_case("role_furniture_preview_layer"),
        )

    def test_no_cad_registry_sync_helper(self) -> None:
        output_root = artifact_path("draw_02", "no_cad_sync")
        summary = run_drawing_standard_registry_no_cad_sync(
            project_root=PROJECT_ROOT,
            output_dir=output_root,
            dry_run=True,
        )
        self.assertEqual(summary["package_id"], DRAW_02_PACKAGE_ID)
        self.assertEqual(summary["suite_status"], "pass")
        self.assertEqual(summary["writeback_applied_count"], 5)
        self.assertEqual(summary["writeback_rejected_count"], 2)

    def test_handoff_indexes_draw_02(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(encoding="utf-8")
        self.assertIn("DRAW-02", handoff)
        self.assertIn("draw_02_drawing_standard_registry_rows.md", handoff)


if __name__ == "__main__":
    unittest.main()
