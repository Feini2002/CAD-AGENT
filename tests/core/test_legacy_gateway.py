from __future__ import annotations

import unittest


class LegacyGatewaySkeletonTests(unittest.TestCase):
    def test_legacy_gateway_registers_four_adapter_cards(self) -> None:
        from core.contracts.legacy_gateway import legacy_gateway_adapter_cards
        from core.contracts.vnext import ToolCard

        cards = legacy_gateway_adapter_cards()

        self.assertEqual(
            sorted(cards),
            [
                "legacy.dry_run",
                "legacy.preview",
                "legacy.readback",
                "legacy.validate",
            ],
        )
        self.assertEqual(cards["legacy.validate"].tool_card.permission_class, "deterministic_verify")
        self.assertEqual(cards["legacy.dry_run"].tool_card.permission_class, "deterministic_verify")
        self.assertEqual(cards["legacy.preview"].tool_card.permission_class, "cad_preview")
        self.assertEqual(cards["legacy.readback"].tool_card.permission_class, "read_only")
        for adapter in cards.values():
            self.assertIsInstance(adapter.tool_card, ToolCard)
            self.assertFalse(adapter.executes_cad)
            self.assertFalse(adapter.writes_dwg)
            self.assertFalse(adapter.saves_dwg)
            self.assertFalse(adapter.mutates_registry)
            self.assertFalse(adapter.advances_table_c)

    def test_preview_adapter_without_explicit_authorization_cannot_write_cad(self) -> None:
        from core.contracts.legacy_gateway import legacy_gateway_adapter_cards
        from core.contracts.vnext import ToolContract

        preview = legacy_gateway_adapter_cards()["legacy.preview"]
        contract = ToolContract(
            tool_call_id="preview-write-attempt",
            task_id="task-legacy-preview",
            tool_id=preview.tool_card.tool_id,
            operation="preview",
            permission_class="cad_preview",
            requested_effects=["cad_preview_write"],
            evidence_required=["legacy_preview_registered", "no_save_guard"],
        )

        decision = preview.tool_card.authorize(contract)

        self.assertEqual(decision.status, "blocked")
        self.assertIn("cad_preview_write", " ".join(decision.reasons))
        self.assertIn("cad_execute", preview.tool_card.forbidden_effects)
        self.assertIn("dwg_save", preview.tool_card.forbidden_effects)

    def test_readback_without_created_handles_is_not_geometry_verified(self) -> None:
        from core.contracts.legacy_gateway import legacy_readback_evidence_package
        from core.contracts.vnext import CompletionJudge, TaskObject

        task = TaskObject(
            task_id="task-readback-no-handles",
            task_kind="legacy_gateway_readback",
            user_intent="Normalize readback evidence without reading a DWG.",
            evidence_requirements=["real_cad_readback"],
        )
        evidence = legacy_readback_evidence_package(
            task_id=task.task_id,
            readback_report={
                "status": "geometry_verified",
                "backend": "real_cad",
                "readbackStatus": "ok",
                "actual": {"created_handles": []},
            },
        )

        decision = CompletionJudge().judge(task=task, evidence=evidence)

        self.assertFalse(evidence.satisfies("real_cad_readback"))
        self.assertEqual(evidence.real_cad_readback_items(), [])
        self.assertEqual(decision.status, "blocked")
        self.assertEqual(decision.verification_status, "not_verified")
        self.assertIn("real_cad_readback", decision.missing_evidence)

    def test_dry_run_screenshot_and_model_text_do_not_masquerade_as_readback(self) -> None:
        from core.contracts.legacy_gateway import legacy_non_readback_evidence_package

        evidence = legacy_non_readback_evidence_package(
            task_id="task-non-readback",
            include_model_text="The preview and dry-run passed, so CAD geometry is verified.",
        )

        self.assertFalse(evidence.satisfies("real_cad_readback"))
        self.assertEqual(evidence.real_cad_readback_items(), [])

    def test_gateway_forbids_dwg_save_registry_and_table_c_mutation(self) -> None:
        from core.contracts.legacy_gateway import legacy_gateway_adapter_cards
        from core.contracts.vnext import ToolContract, protected_evidence_write_decision

        forbidden_effects = ["dwg_save", "save_current_dwg", "registry_mutation", "table_c_mutation"]
        for adapter in legacy_gateway_adapter_cards().values():
            for effect in forbidden_effects:
                with self.subTest(adapter=adapter.adapter_id, effect=effect):
                    contract = ToolContract(
                        tool_call_id=f"{adapter.adapter_id}.{effect}",
                        task_id="task-forbidden-effect",
                        tool_id=adapter.tool_card.tool_id,
                        operation=adapter.operation,
                        permission_class=adapter.tool_card.permission_class,
                        requested_effects=[effect],
                        evidence_required=list(adapter.allowed_evidence),
                    )
                    decision = adapter.tool_card.authorize(contract)
                    self.assertEqual(decision.status, "blocked")

        protected_paths = [
            "libraries/system_library/registry.json",
            "docs/training/training-sources.json",
            "output/validation_runs/legacy-gateway/report.json",
            "openspec/changes/example/tasks.md",
        ]
        for path in protected_paths:
            with self.subTest(path=path):
                self.assertEqual(protected_evidence_write_decision(path).status, "blocked")


if __name__ == "__main__":
    unittest.main()
