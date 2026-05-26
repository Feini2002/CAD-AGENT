from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.proposal_engine.confirmed_finalize import (
    build_default_confirmation_for_proposal,
    build_unselected_candidate_evidence,
    finalize_confirmed_cad_plans,
)
from core.schemas.validator import validate_value
from core.workflows.blank_shell_pipeline import run_blank_shell_pipeline
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class ProposalConfirmedFinalizeTests(unittest.TestCase):
    def test_beta_proposal_05_finalize_bundle_validate_and_dry_run(self) -> None:
        output_dir = artifact_path("proposal_confirmed", "retail_finalize")
        pipeline = run_blank_shell_pipeline(
            PROJECT_ROOT / "examples/workflows/blank_shell_layout_loop.json",
            output_dir=output_dir,
        )
        self.assertEqual(pipeline["status"], "ok", pipeline.get("errors"))

        proposal = json.loads((output_dir / "design_proposal.json").read_text(encoding="utf-8"))
        confirmation = build_default_confirmation_for_proposal(
            proposal,
            action="accept_with_risks",
            selected_candidate_id=str(proposal["candidates"][0]["candidate_id"]),
        )
        confirmation_path = output_dir / "confirmation.json"
        confirmation_path.write_text(json.dumps(confirmation, ensure_ascii=False, indent=2), encoding="utf-8")

        report = finalize_confirmed_cad_plans(output_dir, confirmation_path)
        self.assertEqual(report["status"], "ok", report)
        self.assertTrue(report["validation_all_valid"])
        self.assertGreaterEqual(report["unselected_candidate_count"], 1)
        self.assertGreaterEqual(report["cad_plan_count"], 5)
        self.assertEqual(report["dry_run_valid_count"], report["cad_plan_count"])

        bundle = json.loads((output_dir / "confirmed_cad_plan_bundle.json").read_text(encoding="utf-8"))
        schema = json.loads(
            (PROJECT_ROOT / "core/schemas/confirmed_cad_plan_bundle.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(validate_value(bundle, schema), [])
        self.assertEqual(bundle["controlled_cad_policy"]["layer"], "CODEX_PREVIEW")
        self.assertFalse(bundle["controlled_cad_policy"]["needs_confirmation"])
        self.assertGreaterEqual(len(bundle["unselected_candidate_evidence"]["candidates_not_selected"]), 1)

        unselected_path = output_dir / "unselected_candidate_evidence.json"
        self.assertTrue(unselected_path.is_file())

    def test_unselected_evidence_lists_rejected_candidates(self) -> None:
        proposal = {
            "proposal_id": "proposal-test",
            "candidates": [
                {"candidate_id": "c-a", "layout_candidate_id": "c-a", "score": 0.9, "summary": "a", "failed_checks": [], "ranking_reasons": []},
                {"candidate_id": "c-b", "layout_candidate_id": "c-b", "score": 0.4, "summary": "b", "failed_checks": ["x"], "ranking_reasons": []},
            ],
            "comparison_summary": "test",
        }
        confirmation = {
            "selected_candidate_id": "c-a",
            "rejected_candidates": [{"candidate_id": "c-b", "reason_code": "user_rejected"}],
        }
        evidence = build_unselected_candidate_evidence(proposal, confirmation)
        self.assertEqual(evidence["unselected_candidate_count"], 1)
        self.assertEqual(evidence["candidates_not_selected"][0]["candidate_id"], "c-b")


if __name__ == "__main__":
    unittest.main()
