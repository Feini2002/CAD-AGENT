from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.agents.commercial_fitout_sample_confirmation import (
    assert_pre_confirmation_gate,
    build_assumptions_risks,
    build_confirmation_for_sample_proposal,
    run_fitout_sample_confirmation_loop,
    run_fitout_sample_pre_confirmation,
)
from core.schemas.validator import validate_value
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class CommercialFitoutSampleConfirmationTests(unittest.TestCase):
    def test_pre_confirmation_blocks_cad_plan_artifacts(self) -> None:
        output_dir = artifact_path("commercial_fitout_sample", "pre_confirmation")
        result = run_fitout_sample_pre_confirmation(output_dir=output_dir, project_root=PROJECT_ROOT)
        self.assertEqual(result["status"], "confirmation_pending", result.get("errors"))
        self.assertEqual(assert_pre_confirmation_gate(result), [])
        self.assertTrue((output_dir / "design_proposal.json").is_file())
        self.assertFalse((output_dir / "cad_plans.json").exists())

    def test_confirmation_loop_records_assumptions_and_risks(self) -> None:
        output_dir = artifact_path("commercial_fitout_sample", "full_loop")
        report = run_fitout_sample_confirmation_loop(output_dir, project_root=PROJECT_ROOT)
        self.assertEqual(report["status"], "ok", report)

        bundle_path = output_dir / "commercial_fitout_sample_confirmation_bundle.json"
        self.assertTrue(bundle_path.is_file())
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        schema = json.loads(
            (
                PROJECT_ROOT / "core/schemas/commercial_fitout_sample_confirmation_bundle.schema.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(validate_value(bundle, schema), [])
        self.assertFalse(bundle["geometry_verified"])
        record = bundle["assumptions_risks"]
        self.assertGreaterEqual(len(record["assumptions"]), 1)
        self.assertGreaterEqual(len(record["risks"]), 1)
        self.assertEqual(bundle["controlled_cad_policy"]["layer"], "CODEX_PREVIEW")
        self.assertFalse(bundle["controlled_cad_policy"]["needs_confirmation"])

        confirmed = bundle["confirmed_cad_plan_bundle"]
        self.assertGreaterEqual(len(confirmed["confirmed_cad_plans"]), 1)
        for plan in confirmed["confirmed_cad_plans"]:
            self.assertFalse(plan.get("needs_confirmation", True))

    def test_build_assumptions_risks_splits_notes(self) -> None:
        brief = {"brief_id": "brief-test", "assumptions": ["from brief"]}
        confirmation = {
            "confirmation_id": "confirm-test",
            "local_preferences": {
                "notes": ["Risk: column positions unverified", "Assumption: preview only"],
            },
        }
        record = build_assumptions_risks(brief=brief, confirmation=confirmation)
        self.assertIn("from brief", record["assumptions"])
        self.assertTrue(any("column" in item.lower() for item in record["risks"]))

    def test_build_confirmation_matches_proposal_candidates(self) -> None:
        output_dir = artifact_path("commercial_fitout_sample", "confirmation_builder")
        pre = run_fitout_sample_pre_confirmation(output_dir=output_dir, project_root=PROJECT_ROOT)
        self.assertEqual(pre["status"], "confirmation_pending")
        proposal = json.loads((output_dir / "design_proposal.json").read_text(encoding="utf-8"))
        confirmation = build_confirmation_for_sample_proposal(proposal)
        self.assertEqual(confirmation["proposal_id"], proposal["proposal_id"])
        self.assertTrue(confirmation["selected_candidate_id"])


if __name__ == "__main__":
    unittest.main()
