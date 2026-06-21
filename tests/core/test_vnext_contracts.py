from __future__ import annotations

import unittest
from pathlib import Path


class VNextContractSkeletonTests(unittest.TestCase):
    def test_model_text_cannot_replace_evidence_package(self) -> None:
        from core.contracts.vnext import CompletionJudge, EvidencePackage, TaskObject

        task = TaskObject(
            task_id="task-model-text",
            task_kind="cad_preview",
            user_intent="Draw a preview table.",
            evidence_requirements=["real_cad_readback"],
        )
        evidence = EvidencePackage.from_model_text(
            task_id=task.task_id,
            text="I inspected the CAD result and it looks correct.",
        )

        decision = CompletionJudge().judge(task=task, evidence=evidence)

        self.assertFalse(evidence.satisfies("real_cad_readback"))
        self.assertEqual(decision.status, "blocked")
        self.assertEqual(decision.verification_status, "not_verified")
        self.assertIn("real_cad_readback", decision.missing_evidence)

    def test_fake_dry_run_and_screenshot_do_not_count_as_real_cad_readback(self) -> None:
        from core.contracts.vnext import EvidenceItem, EvidencePackage

        evidence = EvidencePackage(
            task_id="task-non-real-evidence",
            items=[
                EvidenceItem(kind="dry_run", status="pass"),
                EvidenceItem(kind="screenshot", status="pass", metadata={"role": "visual_aid_only"}),
                EvidenceItem(
                    kind="cad_readback",
                    status="pass",
                    backend="fake_cad",
                    readback_status="ok",
                    cad_geometry_verified=True,
                    metadata={"driverMode": "fake_driver_preflight"},
                ),
            ],
        )

        self.assertFalse(evidence.satisfies("real_cad_readback"))
        self.assertEqual(evidence.real_cad_readback_items(), [])

    def test_tool_card_cannot_authorize_beyond_permission_class(self) -> None:
        from core.contracts.vnext import ToolCard, ToolContract

        card = ToolCard(
            tool_id="preview-writer",
            permission_class="cad_preview",
            allowed_effects=["cad_preview_write"],
            forbidden_effects=["dwg_save", "formal_layer_write"],
        )
        contract = ToolContract(
            tool_call_id="tool-call-save",
            task_id="task-permission",
            tool_id="preview-writer",
            operation="save",
            permission_class="dwg_save",
            requested_effects=["dwg_save"],
            evidence_required=["real_cad_readback"],
        )

        decision = card.authorize(contract)

        self.assertEqual(decision.status, "blocked")
        self.assertIn("permission class exceeds ToolCard", decision.reasons[0])

    def test_completion_judge_blocks_when_required_evidence_is_missing(self) -> None:
        from core.contracts.vnext import CompletionJudge, EvidencePackage, TaskObject

        task = TaskObject(
            task_id="task-missing-evidence",
            task_kind="cad_preview",
            user_intent="Preview a CAD object.",
            evidence_requirements=["real_cad_readback", "no_save_guard"],
        )
        evidence = EvidencePackage(task_id=task.task_id, items=[])

        decision = CompletionJudge().judge(task=task, evidence=evidence)

        self.assertEqual(decision.status, "blocked")
        self.assertEqual(decision.verification_status, "not_verified")
        self.assertEqual(decision.missing_evidence, ["real_cad_readback", "no_save_guard"])
        self.assertFalse(decision.can_claim_complete)

    def test_phase5_skeleton_blocks_protected_evidence_writes(self) -> None:
        from core.contracts.vnext import protected_evidence_write_decision

        protected_paths = [
            Path("output/validation_runs/case/report.json"),
            Path("projects/sample/project.json"),
            Path("libraries/system_library/registry.json"),
            Path("docs/training/training-sources.json"),
            Path("openspec/changes/unify-system-architecture-canvas/tasks.md"),
        ]

        for path in protected_paths:
            with self.subTest(path=str(path)):
                decision = protected_evidence_write_decision(path)
                self.assertEqual(decision.status, "blocked")
                self.assertIn("protected evidence", " ".join(decision.reasons))

    def test_contract_layer_is_descriptive_only_in_phase5(self) -> None:
        from core.contracts.vnext import PHASE5_FORBIDDEN_EFFECTS, ToolContract

        contract = ToolContract(
            tool_call_id="tool-call-descriptive",
            task_id="task-descriptive",
            tool_id="cad-contract-placeholder",
            operation="create",
            permission_class="cad_preview",
            requested_effects=["cad_preview_write"],
            evidence_required=["real_cad_readback"],
        )

        self.assertTrue(contract.descriptive_only)
        self.assertIn("cad_execute", PHASE5_FORBIDDEN_EFFECTS)
        self.assertIn("dwg_save", PHASE5_FORBIDDEN_EFFECTS)
        self.assertIn("plugin_call", PHASE5_FORBIDDEN_EFFECTS)
        self.assertIn("table_c_mutation", PHASE5_FORBIDDEN_EFFECTS)


if __name__ == "__main__":
    unittest.main()
