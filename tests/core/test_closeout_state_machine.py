from __future__ import annotations

import unittest


class CloseoutStateMachineTests(unittest.TestCase):
    def test_missing_readback_blocks_cad_preview_verified(self) -> None:
        from core.orchestrator.closeout_state_machine import evaluate_closeout_state

        result = evaluate_closeout_state(model_ok=True, validation_ok=True, dry_run_ok=True, readback_ok=False)

        self.assertEqual(result["state"], "cad_evidence_missing")
        self.assertIn("created_handles_readback=ok", result["missingEvidence"])

    def test_fake_driver_never_proves_geometry(self) -> None:
        from core.orchestrator.closeout_state_machine import evaluate_closeout_state

        result = evaluate_closeout_state(driver_mode="fake_driver_preflight", cadGeometryVerified=False)

        self.assertEqual(result["state"], "cad_evidence_missing")
        self.assertIn("real CAD geometry verified", result["missingEvidence"])

    def test_visual_missing_blocks_delivery_claim(self) -> None:
        from core.orchestrator.closeout_state_machine import evaluate_closeout_state

        result = evaluate_closeout_state(readback_ok=True, visual_acceptance_ok=False)

        self.assertEqual(result["state"], "visual_evidence_missing")
        self.assertIn("visual_acceptance_review=pass", result["missingEvidence"])

    def test_all_required_evidence_ready_for_user_review(self) -> None:
        from core.orchestrator.closeout_state_machine import evaluate_closeout_state

        result = evaluate_closeout_state(
            model_ok=True,
            validation_ok=True,
            dry_run_ok=True,
            readback_ok=True,
            target_layer="CODEX_PREVIEW",
            saved_current_dwg=False,
            visual_acceptance_ok=True,
            neighbor_protection_ok=True,
        )

        self.assertEqual(result["state"], "ready_for_user_review")
        self.assertEqual(result["missingEvidence"], [])


if __name__ == "__main__":
    unittest.main()
