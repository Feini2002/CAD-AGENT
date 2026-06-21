from __future__ import annotations

import unittest
from copy import deepcopy


def _cad_plan_fixture() -> dict[str, object]:
    return {
        "version": "0.1",
        "domain": "generic",
        "intent": "draw_object",
        "object": {
            "type": "table",
            "name": "Preview Guard Table",
            "width": 1200,
            "depth": 600,
        },
        "placement": {
            "mode": "absolute",
            "base_point": [100, 200, 0],
        },
        "drawing": {
            "layer": "CODEX_PREVIEW",
            "include_label": True,
            "include_dimensions": True,
        },
        "confidence": 0.88,
        "needs_confirmation": False,
    }


def _preview_task(*, cad_plan: dict[str, object] | None = None) -> object:
    from core.contracts.vnext import TaskObject

    return TaskObject(
        task_id="task-legacy-preview-registration",
        task_kind="legacy_gateway_preview_registration",
        user_intent="Register a legacy preview request without executing CAD.",
        inputs={
            "cadPlan": cad_plan if cad_plan is not None else _cad_plan_fixture(),
        },
        target_scope={"scopeType": "cad_plan_fixture", "documentId": "none"},
        evidence_requirements=["legacy_preview_registered", "no_save_guard"],
    )


def _readback_task() -> object:
    from core.contracts.vnext import TaskObject

    return TaskObject(
        task_id="task-legacy-readback-registration",
        task_kind="legacy_gateway_readback_registration",
        user_intent="Register legacy readback evidence without reading a DWG.",
        target_scope={"scopeType": "readback_report_fixture", "documentId": "none"},
        evidence_requirements=["legacy_readback_registered", "real_cad_readback", "no_save_guard"],
    )


class LegacyGatewayPreviewReadbackTests(unittest.TestCase):
    def test_preview_registration_only_never_writes_cad(self) -> None:
        from core.contracts.legacy_gateway import run_legacy_preview_registration

        result = run_legacy_preview_registration(task=_preview_task())

        self.assertEqual(result.status, "preview_registered_non_cad")
        self.assertEqual(result.verification_status, "not_verified")
        self.assertEqual(result.tool_contract.tool_id, "legacy.preview")
        self.assertEqual(result.tool_contract.operation, "preview")
        self.assertEqual(result.authorization.status, "allowed")
        self.assertEqual(result.request["layer"], "CODEX_PREVIEW")
        self.assertFalse(result.request["executes_cad"])
        self.assertFalse(result.request["writes_dwg"])
        self.assertFalse(result.request["saves_dwg"])
        self.assertFalse(result.request["savedCurrentDwg"])
        self.assertTrue(result.evidence.satisfies("legacy_preview_registered"))
        self.assertTrue(result.evidence.satisfies("no_save_guard"))
        self.assertFalse(result.evidence.satisfies("real_cad_readback"))
        self.assertFalse(result.cad_geometry_verified)
        self.assertEqual(result.allowed_claims, ["preview_registered_non_cad"])

    def test_preview_write_effect_without_explicit_authorization_is_blocked(self) -> None:
        from core.contracts.legacy_gateway import run_legacy_preview_registration

        result = run_legacy_preview_registration(
            task=_preview_task(),
            requested_effects=["cad_preview_write"],
        )

        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.authorization.status, "blocked")
        self.assertIn("cad_preview_write", " ".join(result.blocking_reasons))
        self.assertFalse(result.evidence.satisfies("legacy_preview_registered"))
        self.assertFalse(result.cad_geometry_verified)

    def test_preview_layer_is_codex_preview_only_and_never_saves_current_dwg(self) -> None:
        from core.contracts.legacy_gateway import run_legacy_preview_registration

        formal_layer_plan = deepcopy(_cad_plan_fixture())
        formal_layer_plan["drawing"] = {
            "layer": "A-WALL",
            "include_label": True,
            "include_dimensions": True,
        }

        result = run_legacy_preview_registration(task=_preview_task(cad_plan=formal_layer_plan))

        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.request["layer"], "A-WALL")
        self.assertFalse(result.request["savedCurrentDwg"])
        self.assertFalse(result.evidence.satisfies("legacy_preview_registered"))
        self.assertTrue(result.evidence.satisfies("no_save_guard"))
        self.assertTrue(any("CODEX_PREVIEW" in reason for reason in result.blocking_reasons))

    def test_readback_registration_without_created_handles_is_not_geometry_verified(self) -> None:
        from core.contracts.legacy_gateway import run_legacy_readback_registration

        result = run_legacy_readback_registration(
            task=_readback_task(),
            readback_report={
                "status": "geometry_verified",
                "backend": "real_cad",
                "readbackStatus": "ok",
                "actual": {"created_handles": []},
            },
        )

        self.assertIn(result.status, {"blocked", "not_verified"})
        self.assertEqual(result.verification_status, "not_verified")
        self.assertTrue(result.evidence.satisfies("legacy_readback_registered"))
        self.assertTrue(result.evidence.satisfies("no_save_guard"))
        self.assertFalse(result.evidence.satisfies("real_cad_readback"))
        self.assertEqual(result.evidence.real_cad_readback_items(), [])
        self.assertFalse(result.cad_geometry_verified)
        self.assertIn("real_cad_readback", result.missing_evidence)

    def test_screenshot_dry_run_and_model_text_cannot_masquerade_as_readback(self) -> None:
        from core.contracts.legacy_gateway import run_legacy_readback_registration

        result = run_legacy_readback_registration(
            task=_readback_task(),
            readback_report={
                "status": "ok",
                "backend": "dry_run",
                "readbackStatus": "not_run",
                "screenshot": "visual-aid.png",
                "dryRunStatus": "valid",
            },
            model_text="The screenshot and dry-run prove CAD geometry is verified.",
        )

        self.assertFalse(result.evidence.satisfies("real_cad_readback"))
        self.assertEqual(result.evidence.real_cad_readback_items(), [])
        self.assertFalse(result.cad_geometry_verified)
        self.assertTrue(any(item.kind == "model_text" for item in result.evidence.items))
        self.assertTrue(any("created handles" in reason for reason in result.blocking_reasons))

    def test_preview_and_readback_forbid_dwg_save_formal_layer_registry_and_table_c_mutation(self) -> None:
        from core.contracts.legacy_gateway import legacy_gateway_adapter_cards
        from core.contracts.vnext import ToolContract

        forbidden_effects = [
            "dwg_save",
            "save_current_dwg",
            "formal_layer_write",
            "registry_mutation",
            "table_c_mutation",
        ]
        for adapter_id in ("legacy.preview", "legacy.readback"):
            adapter = legacy_gateway_adapter_cards()[adapter_id]
            for effect in forbidden_effects:
                with self.subTest(adapter=adapter_id, effect=effect):
                    contract = ToolContract(
                        tool_call_id=f"{adapter_id}.{effect}",
                        task_id="task-forbidden-preview-readback-effect",
                        tool_id=adapter.tool_card.tool_id,
                        operation=adapter.operation,
                        permission_class=adapter.tool_card.permission_class,
                        requested_effects=[effect],
                        evidence_required=list(adapter.allowed_evidence),
                    )

                    decision = adapter.tool_card.authorize(contract)

                    self.assertEqual(decision.status, "blocked")
                    self.assertIn(effect, " ".join(decision.reasons))

    def test_phase6_closeout_summary_keeps_gateway_behind_contracts(self) -> None:
        from core.contracts.legacy_gateway import legacy_gateway_phase6_closeout_summary

        summary = legacy_gateway_phase6_closeout_summary()

        self.assertEqual(summary["status"], "phase6_closeout_ready")
        self.assertFalse(summary["bypasses_phase5_contracts"])
        self.assertFalse(summary["cad_execution_invoked"])
        self.assertFalse(summary["dwg_written_or_saved"])
        self.assertFalse(summary["protected_evidence_mutated"])
        self.assertEqual(
            sorted(summary["adapter_ids"]),
            ["legacy.dry_run", "legacy.preview", "legacy.readback", "legacy.validate"],
        )
        for adapter_id, adapter_summary in summary["adapters"].items():
            with self.subTest(adapter=adapter_id):
                self.assertEqual(adapter_summary["tool_contract_status"], "allowed")
                self.assertTrue(adapter_summary["has_tool_card"])
                self.assertTrue(adapter_summary["has_permission_class"])
                self.assertTrue(adapter_summary["has_evidence_boundary"])
                self.assertFalse(adapter_summary["executes_cad"])
                self.assertFalse(adapter_summary["writes_dwg"])
                self.assertFalse(adapter_summary["saves_dwg"])

        distinctions = summary["completion_judge_distinctions"]
        self.assertEqual(distinctions["schema_plan_valid"], "cad_plan_validate")
        self.assertEqual(distinctions["dry_run_feasible"], "cad_plan_dry_run")
        self.assertEqual(distinctions["preview_registered"], "legacy_preview_registered")
        self.assertEqual(distinctions["readback_verified"], "real_cad_readback")
        self.assertEqual(distinctions["geometry_verified"], "created_handles_real_cad_readback")
        self.assertFalse(summary["no_handles_can_geometry_verify"])
        self.assertFalse(summary["non_readback_evidence_can_masquerade"])
        self.assertEqual(summary["next_phase"], "Phase 7: Evidence Ledger")


if __name__ == "__main__":
    unittest.main()
