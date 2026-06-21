from __future__ import annotations

import unittest


def _task_fixture(*, require_real_readback: bool = False) -> object:
    from core.contracts.vnext import TaskObject

    evidence_requirements = [
        "no_cad_contract_roundtrip",
        "declared_contract_evidence",
        "no_save_guard",
    ]
    if require_real_readback:
        evidence_requirements.append("real_cad_readback")
    return TaskObject(
        task_id="task-no-cad-roundtrip",
        task_kind="vnext_contract_roundtrip",
        user_intent="Validate the vNext contract chain without touching CAD.",
        inputs={
            "toolId": "no-cad-contract-checker",
            "operation": "audit",
            "permissionClass": "deterministic_verify",
            "requestedEffects": ["contract_roundtrip"],
        },
        target_scope={"scopeType": "contract_fixture", "documentId": "none"},
        success_criteria=["contract can be generated, authorized, evidenced, and judged"],
        evidence_requirements=evidence_requirements,
    )


def _tool_card_fixture(*, permission_class: str = "deterministic_verify") -> object:
    from core.contracts.vnext import ToolCard

    return ToolCard(
        tool_id="no-cad-contract-checker",
        permission_class=permission_class,
        allowed_effects=["contract_roundtrip"],
        forbidden_effects=["cad_execute", "dwg_save", "plugin_call", "table_c_mutation"],
    )


def _no_cad_evidence_fixture() -> object:
    from core.contracts.vnext import EvidenceItem, EvidencePackage

    return EvidencePackage(
        task_id="task-no-cad-roundtrip",
        items=[
            EvidenceItem(kind="dry_run", status="pass", backend="dry_run"),
            EvidenceItem(kind="declared_contract_evidence", status="pass"),
            EvidenceItem(kind="no_cad_contract_roundtrip", status="pass"),
            EvidenceItem(kind="no_save_guard", status="pass", metadata={"savedCurrentDwg": False}),
        ],
    )


class VNextContractRoundtripTests(unittest.TestCase):
    def test_complete_contract_without_real_cad_readback_is_not_verified(self) -> None:
        from core.contracts.vnext import run_no_cad_contract_roundtrip

        result = run_no_cad_contract_roundtrip(
            task=_task_fixture(require_real_readback=True),
            tool_card=_tool_card_fixture(),
            evidence=_no_cad_evidence_fixture(),
        )

        self.assertEqual(result.status, "not_verified")
        self.assertEqual(result.completion.status, "not_verified")
        self.assertEqual(result.verification_status, "not_verified")
        self.assertIn("real_cad_readback", result.missing_evidence)
        self.assertFalse(result.cad_geometry_verified)
        self.assertEqual(result.allowed_claims, ["contract roundtrip ready"])
        self.assertIn("CAD geometry", " ".join(result.not_proven))

    def test_missing_evidence_package_blocks_roundtrip(self) -> None:
        from core.contracts.vnext import run_no_cad_contract_roundtrip

        result = run_no_cad_contract_roundtrip(
            task=_task_fixture(),
            tool_card=_tool_card_fixture(),
            evidence=None,
        )

        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.verification_status, "not_verified")
        self.assertIn("EvidencePackage missing", result.blocking_reasons)

    def test_tool_card_permission_shortfall_blocks_roundtrip(self) -> None:
        from core.contracts.vnext import run_no_cad_contract_roundtrip

        result = run_no_cad_contract_roundtrip(
            task=_task_fixture(),
            tool_card=_tool_card_fixture(permission_class="read_only"),
            evidence=_no_cad_evidence_fixture(),
        )

        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.verification_status, "not_verified")
        self.assertTrue(any("permission class exceeds ToolCard" in reason for reason in result.blocking_reasons))

    def test_model_completion_text_without_deterministic_evidence_blocks_roundtrip(self) -> None:
        from core.contracts.vnext import EvidencePackage, run_no_cad_contract_roundtrip

        result = run_no_cad_contract_roundtrip(
            task=_task_fixture(),
            tool_card=_tool_card_fixture(),
            evidence=EvidencePackage.from_model_text(
                task_id="task-no-cad-roundtrip",
                text="The contract roundtrip is complete and the CAD is correct.",
            ),
        )

        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.verification_status, "not_verified")
        self.assertIn("no_cad_contract_roundtrip", result.missing_evidence)
        self.assertFalse(result.cad_geometry_verified)

    def test_no_cad_contract_roundtrip_ready_does_not_claim_cad_geometry_verified(self) -> None:
        from core.contracts.vnext import run_no_cad_contract_roundtrip

        result = run_no_cad_contract_roundtrip(
            task=_task_fixture(require_real_readback=False),
            tool_card=_tool_card_fixture(),
            evidence=_no_cad_evidence_fixture(),
        )

        self.assertEqual(result.status, "ready")
        self.assertEqual(result.verification_status, "not_verified")
        self.assertEqual(result.tool_contract.tool_id, "no-cad-contract-checker")
        self.assertEqual(result.authorization.status, "allowed")
        self.assertFalse(result.evidence.satisfies("real_cad_readback"))
        self.assertFalse(result.cad_geometry_verified)
        self.assertEqual(result.allowed_claims, ["contract roundtrip ready"])
        self.assertNotIn("CAD geometry verified", result.allowed_claims)


if __name__ == "__main__":
    unittest.main()
