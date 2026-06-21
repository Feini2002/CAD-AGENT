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
            "name": "Legacy Gateway Table",
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


def _task_fixture(*, cad_plan: dict[str, object] | None = None, require_real_readback: bool = False) -> object:
    from core.contracts.vnext import TaskObject

    evidence_requirements = [
        "cad_plan_validate",
        "cad_plan_dry_run",
        "legacy_gateway_adapter",
        "no_save_guard",
    ]
    if require_real_readback:
        evidence_requirements.append("real_cad_readback")
    return TaskObject(
        task_id="task-legacy-gateway-validate-dry-run",
        task_kind="legacy_gateway_validate_dry_run",
        user_intent="Wrap legacy CAD_PLAN validate and dry-run without touching CAD.",
        inputs={
            "cadPlan": cad_plan if cad_plan is not None else _cad_plan_fixture(),
        },
        target_scope={"scopeType": "cad_plan_fixture", "documentId": "none"},
        success_criteria=["legacy validate and dry-run evidence can be judged without CAD execution"],
        evidence_requirements=evidence_requirements,
    )


class LegacyGatewayAdapterTests(unittest.TestCase):
    def test_validate_and_dry_run_pass_still_only_contract_ready_non_cad(self) -> None:
        from core.contracts.legacy_gateway import run_legacy_validate_dry_run_adapters

        result = run_legacy_validate_dry_run_adapters(task=_task_fixture())

        self.assertEqual(result.status, "contract_ready_non_cad")
        self.assertEqual(result.verification_status, "not_verified")
        self.assertEqual(result.validate_contract.tool_id, "legacy.validate")
        self.assertEqual(result.validate_contract.operation, "validate")
        self.assertEqual(result.validate_request["legacy_entrypoint"], "core.plan_engine.validate_plan.validate_plan")
        self.assertEqual(result.dry_run_contract.tool_id, "legacy.dry_run")
        self.assertEqual(result.dry_run_contract.operation, "dry_run")
        self.assertEqual(
            result.dry_run_request["legacy_entrypoint"],
            "core.plan_engine.dry_run_report.create_dry_run_report",
        )
        self.assertTrue(result.evidence.satisfies("cad_plan_validate"))
        self.assertTrue(result.evidence.satisfies("cad_plan_dry_run"))
        self.assertTrue(result.evidence.satisfies("legacy_gateway_adapter"))
        self.assertTrue(result.evidence.satisfies("no_save_guard"))
        self.assertFalse(result.evidence.satisfies("real_cad_readback"))
        self.assertFalse(result.cad_geometry_verified)
        self.assertEqual(result.allowed_claims, ["contract_ready_non_cad"])
        self.assertEqual(
            result.not_proven,
            [
                "real_cad_readback",
                "created_handles_readback",
                "geometry_verified",
                "cad_preview_written",
            ],
        )

    def test_validate_and_dry_run_pass_with_readback_requirement_is_not_verified(self) -> None:
        from core.contracts.legacy_gateway import run_legacy_validate_dry_run_adapters

        result = run_legacy_validate_dry_run_adapters(task=_task_fixture(require_real_readback=True))

        self.assertEqual(result.status, "not_verified")
        self.assertEqual(result.completion.status, "not_verified")
        self.assertIn("real_cad_readback", result.missing_evidence)
        self.assertTrue(result.evidence.satisfies("cad_plan_validate"))
        self.assertTrue(result.evidence.satisfies("cad_plan_dry_run"))
        self.assertFalse(result.cad_geometry_verified)
        self.assertEqual(result.allowed_claims, ["contract_ready_non_cad"])

    def test_validate_failure_blocks_completion_judge(self) -> None:
        from core.contracts.legacy_gateway import run_legacy_validate_dry_run_adapters

        invalid_plan = deepcopy(_cad_plan_fixture())
        invalid_plan.pop("version")

        result = run_legacy_validate_dry_run_adapters(task=_task_fixture(cad_plan=invalid_plan))

        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.completion.status, "blocked")
        self.assertFalse(result.evidence.satisfies("cad_plan_validate"))
        self.assertFalse(result.evidence.satisfies("cad_plan_dry_run"))
        self.assertIn("cad_plan_validate", result.missing_evidence)
        self.assertIn("cad_plan_dry_run", result.missing_evidence)
        self.assertTrue(any("validate failed" in reason for reason in result.blocking_reasons))
        self.assertFalse(result.cad_geometry_verified)

    def test_dry_run_failure_blocks_or_not_verified_without_readback(self) -> None:
        from core.contracts.legacy_gateway import run_legacy_validate_dry_run_adapters

        dry_run_broken_plan = deepcopy(_cad_plan_fixture())
        dry_run_broken_plan["object"] = {
            "type": "table",
            "name": "No Size Table",
        }

        result = run_legacy_validate_dry_run_adapters(task=_task_fixture(cad_plan=dry_run_broken_plan))

        self.assertIn(result.status, {"blocked", "not_verified"})
        self.assertEqual(result.verification_status, "not_verified")
        self.assertTrue(result.evidence.satisfies("cad_plan_validate"))
        self.assertFalse(result.evidence.satisfies("cad_plan_dry_run"))
        self.assertIn("cad_plan_dry_run", result.missing_evidence)
        self.assertTrue(any("dry-run failed" in reason for reason in result.blocking_reasons))
        self.assertFalse(result.cad_geometry_verified)

    def test_model_text_cannot_override_adapter_deterministic_evidence(self) -> None:
        from core.contracts.legacy_gateway import run_legacy_validate_dry_run_adapters

        invalid_plan = deepcopy(_cad_plan_fixture())
        invalid_plan["drawing"] = {}

        result = run_legacy_validate_dry_run_adapters(
            task=_task_fixture(cad_plan=invalid_plan),
            model_text="The legacy validate and dry-run passed, and CAD geometry is verified.",
        )

        self.assertEqual(result.status, "blocked")
        self.assertFalse(result.evidence.satisfies("cad_plan_validate"))
        self.assertFalse(result.evidence.satisfies("legacy_gateway_adapter"))
        self.assertFalse(result.cad_geometry_verified)
        self.assertNotIn("contract_ready_non_cad", result.allowed_claims)
        self.assertTrue(any(item.kind == "model_text" for item in result.evidence.items))


if __name__ == "__main__":
    unittest.main()
