from __future__ import annotations

import unittest


class AgentCognitionProofTests(unittest.TestCase):
    def test_behavior_change_proof_distinguishes_growth_from_mechanism_only(self) -> None:
        from core.orchestrator.agent_cognition import build_behavior_change_proof

        unchanged = build_behavior_change_proof(
            agent_id="pipeline_learning_promoter",
            before_decision={
                "route": "standard_draw",
                "requiredAgents": ["pipeline_audit"],
                "toolChoice": ["validate_plan"],
                "blockingReasons": ["missing readback"],
            },
            after_decision={
                "route": "standard_draw",
                "requiredAgents": ["pipeline_audit"],
                "toolChoice": ["validate_plan"],
                "blockingReasons": ["missing readback"],
            },
            memory_applied_in_future_run=False,
            retested_original_task=False,
        )
        self.assertEqual(unchanged["claimStatus"], "mechanism_only")
        self.assertFalse(unchanged["changedRoute"])
        self.assertFalse(unchanged["changedToolChoice"])
        self.assertFalse(unchanged["changedBlockingReason"])
        self.assertIn("不能声称主 Agent 认知提升", unchanged["allowedClaim"])

        changed = build_behavior_change_proof(
            agent_id="pipeline_learning_promoter",
            before_decision={
                "route": "standard_draw",
                "requiredAgents": ["pipeline_audit"],
                "toolChoice": ["validate_plan"],
                "blockingReasons": [],
            },
            after_decision={
                "route": "local_repair",
                "requiredAgents": ["pipeline_repair", "pipeline_audit"],
                "toolChoice": ["validate_plan", "dry_run"],
                "blockingReasons": ["must localize repair handles first"],
            },
            memory_applied_in_future_run=True,
            retested_original_task=True,
            prediction={
                "statement": "用户会接受局部修复方案，因为它不重画整块面板。",
                "outcome": "correct",
                "reconciled": True,
            },
        )
        self.assertEqual(changed["claimStatus"], "behavior_change_evidence")
        self.assertTrue(changed["changedRoute"])
        self.assertTrue(changed["changedRequiredAgents"])
        self.assertTrue(changed["changedToolChoice"])
        self.assertTrue(changed["changedBlockingReason"])
        self.assertTrue(changed["retestedOriginalTask"])
        self.assertEqual(changed["predictionReconciliation"]["outcome"], "correct")

    def test_agent_task_maturity_metrics_are_separate_from_table_c(self) -> None:
        from core.orchestrator.agent_cognition import summarize_agent_task_maturity

        metrics = summarize_agent_task_maturity(
            behavior_proofs=[
                {"changedRoute": True, "changedToolChoice": False, "changedBlockingReason": True},
                {"changedRoute": False, "changedToolChoice": True, "changedBlockingReason": False},
            ],
            prediction_records=[
                {"reconciled": True, "outcome": "correct"},
                {"reconciled": True, "outcome": "incorrect"},
                {"reconciled": False, "outcome": "pending"},
            ],
            overclaim_blocks=3,
            repeated_corrections=1,
        )

        self.assertEqual(metrics["schemaVersion"], "agent-task-maturity-metrics/v1")
        self.assertEqual(metrics["evidenceBoundary"]["notProofOf"], ["Core Proof Coverage", "CAD geometry", "Project Delivery Readiness"])
        self.assertEqual(metrics["behaviorChangeProofCount"], 2)
        self.assertAlmostEqual(metrics["predictionAccuracy"], 0.5)
        self.assertEqual(metrics["overclaimBlockCount"], 3)
        self.assertEqual(metrics["repeatedCorrectionCount"], 1)


if __name__ == "__main__":
    unittest.main()
