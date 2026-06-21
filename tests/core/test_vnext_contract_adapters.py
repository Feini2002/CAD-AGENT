from __future__ import annotations

import unittest
from copy import deepcopy
from tempfile import TemporaryDirectory


def _cad_plan_fixture() -> dict[str, object]:
    return {
        "version": "0.1",
        "domain": "generic",
        "intent": "draw_object",
        "object": {
            "type": "table",
            "name": "Roundtrip Table",
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
        "cad_plan_read_only_adapter",
        "no_save_guard",
    ]
    if require_real_readback:
        evidence_requirements.append("real_cad_readback")
    return TaskObject(
        task_id="task-read-only-cad-plan-adapter",
        task_kind="vnext_contract_read_only_adapter",
        user_intent="Wrap CAD_PLAN validate and dry-run results without touching CAD.",
        inputs={
            "toolId": "cad-plan-read-only-adapter",
            "operation": "validate_dry_run",
            "permissionClass": "deterministic_verify",
            "requestedEffects": ["cad_plan_validate", "cad_plan_dry_run"],
            "cadPlan": cad_plan if cad_plan is not None else _cad_plan_fixture(),
        },
        target_scope={"scopeType": "cad_plan_fixture", "documentId": "none"},
        success_criteria=["validate and dry-run evidence can be judged without CAD execution"],
        evidence_requirements=evidence_requirements,
    )


def _tool_card_fixture() -> object:
    from core.contracts.vnext import ToolCard

    return ToolCard(
        tool_id="cad-plan-read-only-adapter",
        permission_class="deterministic_verify",
        allowed_effects=["cad_plan_validate", "cad_plan_dry_run"],
        forbidden_effects=["cad_execute", "dwg_save", "plugin_call", "table_c_mutation"],
    )


class VNextContractReadOnlyAdapterTests(unittest.TestCase):
    def test_validate_and_dry_run_wrap_into_non_cad_contract_ready(self) -> None:
        from core.contracts.vnext import run_read_only_cad_plan_adapter

        result = run_read_only_cad_plan_adapter(
            task=_task_fixture(),
            tool_card=_tool_card_fixture(),
        )

        self.assertEqual(result.status, "contract_ready_non_cad")
        self.assertEqual(result.verification_status, "not_verified")
        self.assertEqual(result.tool_contract.operation, "validate_dry_run")
        self.assertEqual(result.tool_contract.requested_effects, ["cad_plan_validate", "cad_plan_dry_run"])
        self.assertTrue(result.evidence.satisfies("cad_plan_validate"))
        self.assertTrue(result.evidence.satisfies("cad_plan_dry_run"))
        self.assertTrue(result.evidence.satisfies("cad_plan_read_only_adapter"))
        self.assertFalse(result.evidence.satisfies("real_cad_readback"))
        self.assertFalse(result.cad_geometry_verified)
        self.assertEqual(result.allowed_claims, ["contract_ready_non_cad"])
        self.assertNotIn("CAD geometry verified", result.allowed_claims)

    def test_validate_and_dry_run_pass_without_readback_is_not_geometry_verified(self) -> None:
        from core.contracts.vnext import run_read_only_cad_plan_adapter

        result = run_read_only_cad_plan_adapter(
            task=_task_fixture(require_real_readback=True),
            tool_card=_tool_card_fixture(),
        )

        self.assertEqual(result.status, "not_verified")
        self.assertEqual(result.completion.status, "not_verified")
        self.assertIn("real_cad_readback", result.missing_evidence)
        self.assertFalse(result.cad_geometry_verified)
        self.assertTrue(result.evidence.satisfies("cad_plan_validate"))
        self.assertTrue(result.evidence.satisfies("cad_plan_dry_run"))

    def test_validate_failure_blocks_completion_judge(self) -> None:
        from core.contracts.vnext import run_read_only_cad_plan_adapter

        invalid_plan = deepcopy(_cad_plan_fixture())
        invalid_plan.pop("version")

        result = run_read_only_cad_plan_adapter(
            task=_task_fixture(cad_plan=invalid_plan),
            tool_card=_tool_card_fixture(),
        )

        self.assertEqual(result.status, "blocked")
        self.assertEqual(result.completion.status, "blocked")
        self.assertIn("cad_plan_validate", result.missing_evidence)
        self.assertTrue(any("validate failed" in reason for reason in result.blocking_reasons))
        self.assertFalse(result.cad_geometry_verified)

    def test_dry_run_failure_blocks_or_not_verified_without_cad_readback(self) -> None:
        from core.contracts.vnext import run_read_only_cad_plan_adapter

        dry_run_broken_plan = deepcopy(_cad_plan_fixture())
        dry_run_broken_plan["object"] = {
            "type": "table",
            "name": "No Size Table",
        }

        result = run_read_only_cad_plan_adapter(
            task=_task_fixture(cad_plan=dry_run_broken_plan),
            tool_card=_tool_card_fixture(),
        )

        self.assertIn(result.status, {"blocked", "not_verified"})
        self.assertEqual(result.verification_status, "not_verified")
        self.assertTrue(result.evidence.satisfies("cad_plan_validate"))
        self.assertFalse(result.evidence.satisfies("cad_plan_dry_run"))
        self.assertIn("cad_plan_dry_run", result.missing_evidence)
        self.assertTrue(any("dry-run failed" in reason for reason in result.blocking_reasons))
        self.assertFalse(result.cad_geometry_verified)

    def test_model_text_cannot_override_adapter_deterministic_evidence(self) -> None:
        from core.contracts.vnext import run_read_only_cad_plan_adapter

        invalid_plan = deepcopy(_cad_plan_fixture())
        invalid_plan["drawing"] = {}

        result = run_read_only_cad_plan_adapter(
            task=_task_fixture(cad_plan=invalid_plan),
            tool_card=_tool_card_fixture(),
            model_text="The CAD plan validated, dry-run passed, and the geometry is verified.",
        )

        self.assertEqual(result.status, "blocked")
        self.assertFalse(result.evidence.satisfies("cad_plan_validate"))
        self.assertFalse(result.cad_geometry_verified)
        self.assertNotIn("contract_ready_non_cad", result.allowed_claims)
        self.assertTrue(any(item.kind == "model_text" for item in result.evidence.items))


class P11AdapterRegistryTests(unittest.TestCase):
    def test_default_registry_registers_harness_session_host_and_legacy_adapters(self) -> None:
        from core.contracts.adapter_registry import default_adapter_registry

        registry = default_adapter_registry()

        self.assertIn("harness.rehearsal-result", registry)
        self.assertIn("harness.rehearsal-closeout", registry)
        self.assertIn("cad-session-host.preview", registry)
        self.assertIn("legacy.preview", registry)
        self.assertIn("legacy.readback", registry)

        result_adapter = registry["harness.rehearsal-result"]
        self.assertEqual(result_adapter.tool_card.tool_id, "harness.rehearsal-result")
        self.assertEqual(result_adapter.tool_card.permission_class, "read_only")
        self.assertTrue(result_adapter.consumes_harness_result)
        self.assertFalse(result_adapter.executes_cad)
        self.assertFalse(result_adapter.writes_dwg)
        self.assertIn("phase10_rehearsal_result_consume", result_adapter.tool_card.allowed_effects)
        self.assertIn("dwg_save", result_adapter.tool_card.forbidden_effects)
        self.assertIn("training_source_mutation", result_adapter.tool_card.forbidden_effects)
        self.assertIn("plugin_execute", result_adapter.tool_card.forbidden_effects)

        host_adapter = registry["cad-session-host.preview"]
        self.assertEqual(host_adapter.backend, "cad-session-host")
        self.assertEqual(host_adapter.tool_card.permission_class, "cad_preview")
        self.assertTrue(host_adapter.executes_cad)
        self.assertFalse(host_adapter.saves_dwg)
        self.assertIn("cad_preview_write", host_adapter.tool_card.allowed_effects)
        self.assertIn("created_handles_readback", host_adapter.tool_card.allowed_effects)
        self.assertIn("formal_layer_write", host_adapter.tool_card.forbidden_effects)
        self.assertIn("save_current_dwg", host_adapter.tool_card.forbidden_effects)

        legacy_preview = registry["legacy.preview"]
        self.assertEqual(legacy_preview.entrypoint, "core.execution.execute_plan.execute_plan_file")
        self.assertFalse(legacy_preview.executes_cad)
        self.assertFalse(legacy_preview.writes_dwg)
        self.assertIn("legacy_preview_registered", legacy_preview.tool_card.allowed_effects)

    def test_registry_blocks_allowed_effect_escalation_before_adapter_execution(self) -> None:
        from core.contracts.adapter_registry import authorize_registered_adapter

        cases = [
            ("harness.rehearsal-result", "dwg_save"),
            ("harness.rehearsal-closeout", "phase10_rehearsal_live_preview_runs"),
            ("cad-session-host.preview", "save_current_dwg"),
            ("legacy.preview", "cad_preview_write"),
        ]
        for adapter_id, effect in cases:
            with self.subTest(adapter=adapter_id, effect=effect):
                result = authorize_registered_adapter(
                    adapter_id=adapter_id,
                    task_id="task-p11-forbidden-effect",
                    requested_effects=[effect],
                )

                self.assertEqual(result.status, "blocked")
                self.assertEqual(result.authorization.status, "blocked")
                self.assertIn(effect, " ".join(result.blocking_reasons))

    def test_registry_consumes_phase10_harness_result_without_new_cad_write(self) -> None:
        from core.contracts.adapter_registry import consume_harness_result_via_registry

        harness_result = {
            "schemaVersion": "cad-agent-harness-result/v1",
            "command": "rehearsal-result",
            "status": "ready",
            "verificationStatus": "verified",
            "backend": "phase10_rehearsal_result",
            "cadGeometryVerified": True,
            "cadWritesAttempted": False,
            "stableGeometry": True,
            "runCount": 2,
            "verifiedRunCount": 2,
            "blockingReasons": [],
            "missingEvidence": [],
            "allowedEffects": ["phase10_rehearsal_result_write"],
            "rehearsalResult": {
                "schemaVersion": "phase10-rehearsal-result/v1",
                "status": "ready",
                "verificationStatus": "verified",
                "cadGeometryVerified": True,
                "cadWritesAttempted": False,
                "stableGeometry": True,
                "runCount": 2,
                "verifiedRunCount": 2,
                "blockingReasons": [],
                "missingEvidence": [],
            },
        }

        result = consume_harness_result_via_registry(harness_result)

        self.assertEqual(result.status, "ready")
        self.assertEqual(result.verification_status, "verified")
        self.assertEqual(result.adapter.adapter_id, "harness.rehearsal-result")
        self.assertEqual(result.authorization.status, "allowed")
        self.assertFalse(result.cad_writes_attempted)
        self.assertFalse(result.source_cad_writes_attempted)
        self.assertTrue(result.cad_geometry_verified)
        self.assertTrue(result.evidence.satisfies("phase10_rehearsal_result"))
        self.assertTrue(result.evidence.satisfies("real_cad_readback"))
        self.assertIn("phase10_rehearsal_result_consumed", result.allowed_claims)
        self.assertIn("training_resume", result.not_proven)
        self.assertIn("table_c_progress", result.not_proven)
        self.assertIn("plugin_readiness", result.not_proven)

    def test_registry_blocks_rehearsal_result_consumption_that_claims_new_cad_write(self) -> None:
        from core.contracts.adapter_registry import consume_harness_result_via_registry

        result = consume_harness_result_via_registry(
            {
                "schemaVersion": "cad-agent-harness-result/v1",
                "command": "rehearsal-result",
                "status": "ready",
                "verificationStatus": "verified",
                "backend": "phase10_rehearsal_result",
                "cadGeometryVerified": True,
                "cadWritesAttempted": True,
                "stableGeometry": True,
                "runCount": 2,
                "verifiedRunCount": 2,
                "blockingReasons": [],
                "missingEvidence": [],
            }
        )

        self.assertEqual(result.status, "blocked")
        self.assertFalse(result.cad_geometry_verified)
        self.assertIn("harness_result_consumer_must_be_read_only", result.blocking_reasons)


class P12MockPluginTransactionTests(unittest.TestCase):
    def test_mock_plugin_transaction_success_commits_preview_but_never_real_cad(self) -> None:
        from core.contracts.mock_plugin_transaction import (
            execute_mock_plugin_transaction,
            mock_plugin_transaction_evidence_package,
        )

        result = execute_mock_plugin_transaction(mode="success", transaction_id="tx-p12-success")
        evidence = mock_plugin_transaction_evidence_package(result)

        self.assertEqual(result["schemaVersion"], "mock-plugin-transaction/p12/v1")
        self.assertEqual(result["transactionId"], "tx-p12-success")
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["proofStatus"], "mock_committed_preview")
        self.assertTrue(result["rollbackRequired"])
        self.assertEqual(result["rollbackStatus"], "not_required")
        self.assertTrue(result["committedPreview"])
        self.assertEqual(result["documentState"], "preview_committed")
        self.assertEqual(result["blockedReason"], "")
        self.assertFalse(result["retryable"])
        self.assertEqual(result["backend"], "mock_plugin_like")
        self.assertEqual(result["createdHandles"], ["mock-handle-001", "mock-handle-002"])
        self.assertEqual(result["createdHandlesRef"], "mock-ledger://tx-p12-success/created-handles")
        self.assertIn("tool.requested", result["ledgerRefs"])
        self.assertIn("adapter.completed", result["ledgerRefs"])
        self.assertFalse(result["cadGeometryVerified"])
        self.assertFalse(evidence.satisfies("real_cad_readback"))
        self.assertTrue(evidence.satisfies("mock_plugin_transaction"))
        self.assertIn("real_cad_readback", result["notEvidenceFor"])

    def test_mock_plugin_transaction_modes_have_explicit_rollback_and_proof_status(self) -> None:
        from core.contracts.mock_plugin_transaction import execute_mock_plugin_transaction

        cases = [
            (
                "failure",
                "blocked",
                "mock_failure_before_commit",
                "not_started",
                False,
                "unchanged",
                "mock_execution_failed_before_preview_commit",
                True,
            ),
            (
                "rollback_success",
                "blocked",
                "mock_rollback_verified",
                "rolled_back",
                False,
                "rolled_back",
                "mock_audit_failed_after_preview_batch",
                True,
            ),
            (
                "rollback_failed",
                "blocked",
                "mock_rollback_failed",
                "rollback_failed",
                False,
                "in_flight_unknown",
                "mock_rollback_failed_after_preview_batch",
                False,
            ),
            (
                "blocked",
                "blocked",
                "mock_blocked_before_transaction",
                "not_started",
                False,
                "unchanged",
                "mock_policy_blocked",
                False,
            ),
        ]

        for mode, status, proof, rollback, committed, document_state, reason, retryable in cases:
            with self.subTest(mode=mode):
                result = execute_mock_plugin_transaction(mode=mode, transaction_id=f"tx-p12-{mode}")

                self.assertEqual(result["status"], status)
                self.assertEqual(result["proofStatus"], proof)
                self.assertEqual(result["rollbackStatus"], rollback)
                self.assertEqual(result["committedPreview"], committed)
                self.assertEqual(result["documentState"], document_state)
                self.assertEqual(result["blockedReason"], reason)
                self.assertEqual(result["retryable"], retryable)
                self.assertFalse(result["cadGeometryVerified"])
                self.assertIn("rollback.applied", result["ledgerRefs"])

    def test_mock_plugin_transaction_is_registered_and_blocks_effect_escalation(self) -> None:
        from core.contracts.adapter_registry import authorize_registered_adapter, default_adapter_registry

        registry = default_adapter_registry()
        adapter = registry["mock-plugin.transaction"]

        self.assertEqual(adapter.tool_card.permission_class, "deterministic_verify")
        self.assertFalse(adapter.executes_cad)
        self.assertFalse(adapter.writes_dwg)
        self.assertFalse(adapter.calls_plugin)
        self.assertIn("mock_plugin_transaction_execute", adapter.tool_card.allowed_effects)
        self.assertIn("mock_plugin_rollback_batch", adapter.tool_card.allowed_effects)
        self.assertIn("plugin_execute", adapter.tool_card.forbidden_effects)
        self.assertIn("cad_execute", adapter.tool_card.forbidden_effects)

        allowed = authorize_registered_adapter(
            adapter_id="mock-plugin.transaction",
            task_id="task-p12-allowed",
            requested_effects=["mock_plugin_transaction_execute", "mock_plugin_rollback_batch"],
        )
        self.assertEqual(allowed.status, "allowed")

        for effect in ["plugin_execute", "cad_execute", "real_cad_readback", "dwg_save"]:
            with self.subTest(effect=effect):
                blocked = authorize_registered_adapter(
                    adapter_id="mock-plugin.transaction",
                    task_id="task-p12-forbidden",
                    requested_effects=[effect],
                )
                self.assertEqual(blocked.status, "blocked")
                self.assertIn(effect, " ".join(blocked.blocking_reasons))

    def test_harness_mock_plugin_transaction_uses_registry_and_cannot_bypass_toolcard(self) -> None:
        from core.contracts.cad_agent_harness import run_harness_command

        result = run_harness_command(
            "mock-plugin-transaction",
            backend="mock-plugin-like",
            mock_transaction_mode="success",
        )

        self.assertEqual(result["command"], "mock-plugin-transaction")
        self.assertEqual(result["adapterId"], "mock-plugin.transaction")
        self.assertEqual(result["registryAuthorization"]["status"], "allowed")
        self.assertEqual(result["transaction"]["proofStatus"], "mock_committed_preview")
        self.assertFalse(result["cadGeometryVerified"])
        self.assertIn("real_cad_readback", result["transaction"]["notEvidenceFor"])

        blocked = run_harness_command(
            "mock-plugin-transaction",
            backend="mock-plugin-like",
            requested_effects=["plugin_execute"],
            mock_transaction_mode="success",
        )

        self.assertEqual(blocked["status"], "blocked")
        self.assertEqual(blocked["adapterId"], "mock-plugin.transaction")
        self.assertEqual(blocked["registryAuthorization"]["status"], "blocked")
        self.assertIn("plugin_execute", " ".join(blocked["blockingReasons"]))
        self.assertFalse(blocked["cadWritesAttempted"])


class P13NativeThinBackendTests(unittest.TestCase):
    def test_native_thin_backend_skeleton_exposes_transaction_no_save_and_rollback_fields(self) -> None:
        from core.contracts.native_thin_backend import (
            execute_native_thin_backend_skeleton,
            native_thin_backend_evidence_package,
        )

        result = execute_native_thin_backend_skeleton(
            transaction_id="tx-p13-skeleton",
            mode="contract_ready",
        )
        evidence = native_thin_backend_evidence_package(result)

        self.assertEqual(result["schemaVersion"], "native-thin-backend/p13/v1")
        self.assertEqual(result["transactionId"], "tx-p13-skeleton")
        self.assertEqual(result["adapterId"], "native-thin.backend")
        self.assertEqual(result["backend"], "native_thin_skeleton")
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["verificationStatus"], "not_verified")
        self.assertEqual(result["proofStatus"], "native_skeleton_contract_ready")
        self.assertTrue(result["rollbackRequired"])
        self.assertEqual(result["rollbackStatus"], "not_started")
        self.assertFalse(result["committedPreview"])
        self.assertEqual(result["createdHandles"], [])
        self.assertEqual(result["createdHandlesRef"], "native-ledger://tx-p13-skeleton/created-handles")
        self.assertFalse(result["retryable"])
        self.assertEqual(result["documentState"], "not_connected")
        self.assertFalse(result["cadGeometryVerified"])
        self.assertFalse(result["cadWritesAttempted"])
        self.assertFalse(result["nativePluginInvoked"])
        self.assertFalse(result["noSaveAudit"]["saveAttempted"])
        self.assertFalse(result["noSaveAudit"]["saveAllowed"])
        self.assertEqual(result["noSaveAudit"]["status"], "not_run_no_cad")
        self.assertEqual(result["rollbackProof"]["status"], "not_run_no_transaction")
        self.assertIn("rollback.applied", result["ledgerRefs"])
        self.assertTrue(evidence.satisfies("native_thin_backend_contract"))
        self.assertTrue(evidence.satisfies("no_save_guard"))
        self.assertFalse(evidence.satisfies("real_cad_readback"))
        self.assertIn("real_cad_readback", result["notEvidenceFor"])
        self.assertIn("native_plugin_execution", result["notEvidenceFor"])

    def test_native_thin_backend_blocked_mode_has_explicit_retryable_and_document_state(self) -> None:
        from core.contracts.native_thin_backend import execute_native_thin_backend_skeleton

        result = execute_native_thin_backend_skeleton(
            transaction_id="tx-p13-blocked",
            mode="blocked",
        )

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["proofStatus"], "native_skeleton_blocked_before_backend")
        self.assertEqual(result["blockedReason"], "native_backend_scope_not_confirmed")
        self.assertFalse(result["retryable"])
        self.assertEqual(result["documentState"], "not_connected")
        self.assertEqual(result["rollbackStatus"], "not_started")
        self.assertEqual(result["rollbackProof"]["status"], "not_run_no_transaction")
        self.assertFalse(result["cadGeometryVerified"])
        self.assertFalse(result["nativePluginInvoked"])

    def test_native_thin_backend_is_registered_and_blocks_effect_escalation(self) -> None:
        from core.contracts.adapter_registry import authorize_registered_adapter, default_adapter_registry

        registry = default_adapter_registry()
        adapter = registry["native-thin.backend"]

        self.assertEqual(adapter.tool_card.permission_class, "deterministic_verify")
        self.assertEqual(adapter.command, "native-thin-backend")
        self.assertEqual(adapter.backend, "native-thin-skeleton")
        self.assertFalse(adapter.executes_cad)
        self.assertFalse(adapter.writes_dwg)
        self.assertFalse(adapter.calls_plugin)
        self.assertIn("native_thin_contract_prepare", adapter.tool_card.allowed_effects)
        self.assertIn("native_thin_no_save_audit", adapter.tool_card.allowed_effects)
        self.assertIn("native_thin_rollback_proof_record", adapter.tool_card.allowed_effects)
        self.assertIn("native_plugin_execute", adapter.tool_card.forbidden_effects)
        self.assertIn("plugin_execute", adapter.tool_card.forbidden_effects)
        self.assertIn("cad_execute", adapter.tool_card.forbidden_effects)
        self.assertIn("dwg_save", adapter.tool_card.forbidden_effects)

        allowed = authorize_registered_adapter(
            adapter_id="native-thin.backend",
            task_id="task-p13-allowed",
            requested_effects=[
                "native_thin_contract_prepare",
                "native_thin_no_save_audit",
                "native_thin_rollback_proof_record",
            ],
        )
        self.assertEqual(allowed.status, "allowed")

        for effect in ["native_plugin_execute", "plugin_execute", "cad_execute", "real_cad_readback", "dwg_save"]:
            with self.subTest(effect=effect):
                blocked = authorize_registered_adapter(
                    adapter_id="native-thin.backend",
                    task_id="task-p13-forbidden",
                    requested_effects=[effect],
                )
                self.assertEqual(blocked.status, "blocked")
                self.assertIn(effect, " ".join(blocked.blocking_reasons))

    def test_harness_native_thin_backend_uses_registry_and_cannot_bypass_toolcard(self) -> None:
        from core.contracts.cad_agent_harness import run_harness_command

        result = run_harness_command(
            "native-thin-backend",
            backend="native-thin-skeleton",
            native_backend_mode="contract_ready",
        )

        self.assertEqual(result["command"], "native-thin-backend")
        self.assertEqual(result["adapterId"], "native-thin.backend")
        self.assertEqual(result["registryAuthorization"]["status"], "allowed")
        self.assertEqual(result["nativeThinBackend"]["proofStatus"], "native_skeleton_contract_ready")
        self.assertFalse(result["cadGeometryVerified"])
        self.assertFalse(result["nativeThinBackend"]["nativePluginInvoked"])
        self.assertIn("real_cad_readback", result["nativeThinBackend"]["notEvidenceFor"])

        blocked = run_harness_command(
            "native-thin-backend",
            backend="native-thin-skeleton",
            requested_effects=["native_plugin_execute"],
            native_backend_mode="contract_ready",
        )

        self.assertEqual(blocked["status"], "blocked")
        self.assertEqual(blocked["adapterId"], "native-thin.backend")
        self.assertEqual(blocked["registryAuthorization"]["status"], "blocked")
        self.assertIn("native_plugin_execute", " ".join(blocked["blockingReasons"]))
        self.assertFalse(blocked["cadWritesAttempted"])


class P13BNativeThinPreflightTests(unittest.TestCase):
    def test_native_thin_scope_receipt_blocks_missing_scope_cad_plan_and_safety_plans(self) -> None:
        from core.contracts.native_thin_backend import build_native_thin_backend_scope_receipt

        result = build_native_thin_backend_scope_receipt(
            cad_plan=None,
            scope_confirmed=False,
            backend_identity="",
            readback_plan=None,
            rollback_plan=None,
            no_save_guard=None,
        )

        self.assertEqual(result["schemaVersion"], "native-thin-preflight/p13b/v1")
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["cadWritesAttempted"])
        self.assertFalse(result["nativePluginInvoked"])
        blockers = " ".join(result["blockingReasons"])
        self.assertIn("native_scope_not_confirmed", blockers)
        self.assertIn("cad_plan_required", blockers)
        self.assertIn("readback_plan_required", blockers)
        self.assertIn("rollback_plan_required", blockers)
        self.assertIn("no_save_guard_required", blockers)
        self.assertIn("backend_identity_required", blockers)

        non_preview_plan = deepcopy(_cad_plan_fixture())
        non_preview_plan["drawing"] = {"layer": "A-WALL"}
        blocked_layer = build_native_thin_backend_scope_receipt(
            cad_plan=non_preview_plan,
            scope_confirmed=True,
            confirmation_statement="confirmed P13B scope for preview only",
            backend_identity="native-thin-skeleton",
            readback_plan={"required": True, "strategy": "created_handles_bbox_props"},
            rollback_plan={"required": True, "strategy": "rollback_batch"},
            no_save_guard={"required": True, "saveAllowed": False},
        )
        self.assertEqual(blocked_layer["status"], "blocked")
        self.assertIn("target_layer_must_be_CODEX_PREVIEW", blocked_layer["blockingReasons"])

    def test_native_thin_scope_receipt_ready_records_required_plans_without_execution(self) -> None:
        from core.contracts.native_thin_backend import build_native_thin_backend_scope_receipt

        with TemporaryDirectory() as tmp:
            result = build_native_thin_backend_scope_receipt(
                cad_plan=_cad_plan_fixture(),
                output_dir=tmp,
                scope_confirmed=True,
                confirmation_statement="confirmed P13B native thin scoped preflight only",
                backend_identity="native-thin-skeleton",
                readback_plan={"required": True, "strategy": "created_handles_bbox_props"},
                rollback_plan={"required": True, "strategy": "rollback_batch"},
                no_save_guard={"required": True, "saveAllowed": False},
            )

        self.assertEqual(result["status"], "ready")
        self.assertTrue(result["scopeConfirmed"])
        self.assertEqual(result["targetLayer"], "CODEX_PREVIEW")
        self.assertEqual(result["backendIdentity"]["backend"], "native-thin-skeleton")
        self.assertTrue(result["readbackPlan"]["required"])
        self.assertTrue(result["rollbackPlan"]["required"])
        self.assertFalse(result["noSaveGuard"]["saveAllowed"])
        self.assertFalse(result["cadWritesAttempted"])
        self.assertFalse(result["nativePluginInvoked"])
        self.assertIn("native_thin_scope_receipt_write", result["allowedEffects"])
        self.assertIn("native_thin_preflight_packet_write", result["nextAllowedEffects"])
        self.assertIn("real_cad_readback", result["notEvidenceFor"])
        self.assertIn("native_plugin_execution", result["notEvidenceFor"])
        self.assertTrue(result["artifacts"]["nativeThinScopeReceipt"])

    def test_native_thin_launch_packet_ready_from_receipt_without_live_execution(self) -> None:
        from core.contracts.native_thin_backend import (
            build_native_thin_backend_launch_packet,
            build_native_thin_backend_scope_receipt,
        )

        with TemporaryDirectory() as tmp:
            receipt = build_native_thin_backend_scope_receipt(
                cad_plan=_cad_plan_fixture(),
                output_dir=tmp,
                scope_confirmed=True,
                confirmation_statement="confirmed P13B native thin scoped preflight only",
                backend_identity="native-thin-skeleton",
                readback_plan={"required": True, "strategy": "created_handles_bbox_props"},
                rollback_plan={"required": True, "strategy": "rollback_batch"},
                no_save_guard={"required": True, "saveAllowed": False},
            )
            packet = build_native_thin_backend_launch_packet(
                scope_receipt_path=receipt["artifacts"]["nativeThinScopeReceipt"],
                output_dir=tmp,
            )

        self.assertEqual(packet["status"], "ready")
        self.assertTrue(packet["launchPacketReady"])
        self.assertFalse(packet["liveExecutionAuthorized"])
        self.assertFalse(packet["cadWritesAttempted"])
        self.assertFalse(packet["nativePluginInvoked"])
        self.assertFalse(packet["cadGeometryVerified"])
        self.assertEqual(packet["backendIdentity"]["backend"], "native-thin-skeleton")
        self.assertEqual(packet["targetLayer"], "CODEX_PREVIEW")
        self.assertTrue(packet["readbackPlan"]["required"])
        self.assertTrue(packet["rollbackPlan"]["required"])
        self.assertFalse(packet["noSaveGuard"]["saveAllowed"])
        self.assertIn("request_user_authorization_for_native_live_spike", packet["nextStep"])
        self.assertIn("real_cad_readback", packet["notEvidenceFor"])
        self.assertIn("native_plugin_execution", packet["notEvidenceFor"])

    def test_native_thin_launch_packet_blocks_missing_or_blocked_receipt(self) -> None:
        from core.contracts.native_thin_backend import (
            build_native_thin_backend_launch_packet,
            build_native_thin_backend_scope_receipt,
        )

        missing = build_native_thin_backend_launch_packet(scope_receipt_path=None)
        self.assertEqual(missing["status"], "blocked")
        self.assertIn("native_scope_receipt_required", missing["blockingReasons"])

        blocked_receipt = build_native_thin_backend_scope_receipt(
            cad_plan=_cad_plan_fixture(),
            scope_confirmed=False,
            backend_identity="native-thin-skeleton",
            readback_plan={"required": True},
            rollback_plan={"required": True},
            no_save_guard={"required": True, "saveAllowed": False},
        )
        blocked = build_native_thin_backend_launch_packet(scope_receipt=blocked_receipt)
        self.assertEqual(blocked["status"], "blocked")
        self.assertIn("native_scope_receipt_not_ready", blocked["blockingReasons"])
        self.assertFalse(blocked["cadWritesAttempted"])
        self.assertFalse(blocked["nativePluginInvoked"])

    def test_native_thin_backend_registry_allows_p13b_packet_writes_and_blocks_live_effects(self) -> None:
        from core.contracts.adapter_registry import authorize_registered_adapter, default_adapter_registry

        adapter = default_adapter_registry()["native-thin.backend"]
        self.assertIn("native_thin_scope_receipt_write", adapter.tool_card.allowed_effects)
        self.assertIn("native_thin_preflight_packet_write", adapter.tool_card.allowed_effects)
        self.assertIn("native_thin_launch_packet_write", adapter.tool_card.allowed_effects)

        allowed = authorize_registered_adapter(
            adapter_id="native-thin.backend",
            task_id="task-p13b-preflight",
            requested_effects=[
                "native_thin_scope_receipt_write",
                "native_thin_preflight_packet_write",
                "native_thin_launch_packet_write",
            ],
        )
        self.assertEqual(allowed.status, "allowed")

        for effect in ["native_plugin_execute", "real_cad_readback", "dwg_save", "formal_layer_write"]:
            with self.subTest(effect=effect):
                blocked = authorize_registered_adapter(
                    adapter_id="native-thin.backend",
                    task_id="task-p13b-live-effect",
                    requested_effects=[effect],
                )
                self.assertEqual(blocked.status, "blocked")
                self.assertIn(effect, " ".join(blocked.blocking_reasons))

    def test_harness_native_thin_preflight_uses_registry_and_cannot_bypass_toolcard(self) -> None:
        from core.contracts.cad_agent_harness import run_harness_command

        with TemporaryDirectory() as tmp:
            receipt_result = run_harness_command(
                "native-thin-backend",
                cad_plan=_cad_plan_fixture(),
                output_dir=tmp,
                backend="native-thin-skeleton",
                native_backend_mode="scope_receipt",
                native_scope_confirmed=True,
                confirmation_statement="confirmed P13B native thin scoped preflight only",
            )
            packet_result = run_harness_command(
                "native-thin-backend",
                output_dir=tmp,
                scope_receipt_path=receipt_result["artifacts"]["nativeThinScopeReceipt"],
                backend="native-thin-skeleton",
                native_backend_mode="preflight",
            )

        self.assertEqual(receipt_result["status"], "ready")
        self.assertEqual(receipt_result["adapterId"], "native-thin.backend")
        self.assertEqual(receipt_result["registryAuthorization"]["status"], "allowed")
        self.assertFalse(receipt_result["nativePluginInvoked"])

        self.assertEqual(packet_result["status"], "ready")
        self.assertEqual(packet_result["adapterId"], "native-thin.backend")
        self.assertEqual(packet_result["registryAuthorization"]["status"], "allowed")
        self.assertFalse(packet_result["cadWritesAttempted"])
        self.assertFalse(packet_result["nativePluginInvoked"])
        self.assertIn("real_cad_readback", packet_result["notEvidenceFor"])

        blocked = run_harness_command(
            "native-thin-backend",
            backend="native-thin-skeleton",
            requested_effects=["native_plugin_execute"],
            native_backend_mode="preflight",
        )

        self.assertEqual(blocked["status"], "blocked")
        self.assertEqual(blocked["adapterId"], "native-thin.backend")
        self.assertEqual(blocked["registryAuthorization"]["status"], "blocked")
        self.assertIn("native_plugin_execute", " ".join(blocked["blockingReasons"]))
        self.assertFalse(blocked["cadWritesAttempted"])


class P13CNativeThinAuthorizationGateTests(unittest.TestCase):
    def _ready_launch_packet(self, output_dir: str) -> dict[str, object]:
        from core.contracts.native_thin_backend import (
            build_native_thin_backend_launch_packet,
            build_native_thin_backend_scope_receipt,
        )

        receipt = build_native_thin_backend_scope_receipt(
            cad_plan=_cad_plan_fixture(),
            output_dir=output_dir,
            scope_confirmed=True,
            confirmation_statement="confirmed P13B native thin scoped preflight only",
            backend_identity="native-thin-skeleton",
            readback_plan={"required": True, "strategy": "created_handles_bbox_props"},
            rollback_plan={"required": True, "strategy": "rollback_batch"},
            no_save_guard={"required": True, "saveAllowed": False},
        )
        return build_native_thin_backend_launch_packet(
            scope_receipt_path=receipt["artifacts"]["nativeThinScopeReceipt"],
            output_dir=output_dir,
        )

    def _explicit_user_authorization(self, launch_packet_hash: str) -> dict[str, object]:
        return {
            "explicit": True,
            "scopeConfirmed": True,
            "cadPlanConfirmed": True,
            "codexPreviewConfirmed": True,
            "readbackConfirmed": True,
            "rollbackConfirmed": True,
            "noSaveConfirmed": True,
            "backendIdentityConfirmed": True,
            "launchPacketHash": launch_packet_hash,
            "statement": (
                "I explicitly authorize this P13C scoped live spike for CODEX_PREVIEW "
                "with readback, rollback, no-save guard, and native-thin-skeleton backend identity."
            ),
        }

    def test_ready_launch_packet_enters_authorization_pending_without_execution(self) -> None:
        from core.contracts.native_thin_backend import build_native_thin_backend_authorization_gate

        with TemporaryDirectory() as tmp:
            packet = self._ready_launch_packet(tmp)
            gate = build_native_thin_backend_authorization_gate(
                launch_packet=packet,
                output_dir=tmp,
            )

        self.assertEqual(gate["schemaVersion"], "native-thin-authorization/p13c/v1")
        self.assertEqual(gate["kind"], "authorization_gate")
        self.assertEqual(gate["status"], "blocked")
        self.assertEqual(gate["authorizationStatus"], "authorization_pending")
        self.assertIn("native_live_user_authorization_required", gate["blockingReasons"])
        self.assertTrue(gate["launchPacketReady"])
        self.assertFalse(gate["liveExecutionAuthorized"])
        self.assertFalse(gate["cadWritesAttempted"])
        self.assertFalse(gate["nativePluginInvoked"])
        self.assertFalse(gate["cadGeometryVerified"])
        self.assertEqual(gate["targetLayer"], "CODEX_PREVIEW")
        self.assertEqual(gate["backendIdentity"]["backend"], "native-thin-skeleton")
        self.assertTrue(gate["scopeHash"])
        self.assertEqual(gate["scopeHash"], gate["launchPacketHash"])
        self.assertTrue(gate["artifacts"]["nativeThinAuthorizationGate"])
        self.assertIn("real_cad_readback", gate["notEvidenceFor"])
        self.assertIn("native_plugin_execution", gate["notEvidenceFor"])

    def test_execution_receipt_blocks_without_ready_authorization(self) -> None:
        from core.contracts.native_thin_backend import (
            build_native_thin_backend_authorization_gate,
            build_native_thin_backend_execution_receipt,
        )

        with TemporaryDirectory() as tmp:
            gate = build_native_thin_backend_authorization_gate(
                launch_packet=self._ready_launch_packet(tmp),
                output_dir=tmp,
            )
            receipt = build_native_thin_backend_execution_receipt(
                authorization_gate=gate,
                output_dir=tmp,
            )

        self.assertEqual(receipt["schemaVersion"], "native-thin-execution-receipt/p13c/v1")
        self.assertEqual(receipt["kind"], "execution_receipt")
        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("native_live_authorization_not_ready", receipt["blockingReasons"])
        self.assertFalse(receipt["liveExecutionAuthorized"])
        self.assertFalse(receipt["executionStarted"])
        self.assertFalse(receipt["cadWritesAttempted"])
        self.assertFalse(receipt["nativePluginInvoked"])
        self.assertFalse(receipt["cadGeometryVerified"])
        self.assertIn("real_cad_readback", receipt["notEvidenceFor"])

    def test_explicit_authorization_builds_scoped_receipt_but_still_does_not_execute(self) -> None:
        from core.contracts.native_thin_backend import (
            build_native_thin_backend_authorization_gate,
            build_native_thin_backend_execution_receipt,
        )

        with TemporaryDirectory() as tmp:
            packet = self._ready_launch_packet(tmp)
            pending = build_native_thin_backend_authorization_gate(launch_packet=packet)
            gate = build_native_thin_backend_authorization_gate(
                launch_packet=packet,
                output_dir=tmp,
                user_authorization=self._explicit_user_authorization(pending["launchPacketHash"]),
            )
            receipt = build_native_thin_backend_execution_receipt(
                authorization_gate=gate,
                output_dir=tmp,
            )

        self.assertEqual(gate["status"], "ready")
        self.assertEqual(gate["authorizationStatus"], "authorized")
        self.assertTrue(gate["liveExecutionAuthorized"])
        self.assertFalse(gate["cadWritesAttempted"])
        self.assertFalse(gate["nativePluginInvoked"])

        self.assertEqual(receipt["status"], "ready")
        self.assertEqual(receipt["receiptStatus"], "scoped_execution_receipt_ready")
        self.assertTrue(receipt["liveExecutionAuthorized"])
        self.assertFalse(receipt["executionStarted"])
        self.assertEqual(receipt["documentState"], "not_connected")
        self.assertFalse(receipt["cadWritesAttempted"])
        self.assertFalse(receipt["nativePluginInvoked"])
        self.assertFalse(receipt["cadGeometryVerified"])
        self.assertEqual(receipt["proofStatus"], "native_live_scoped_receipt_ready_no_execution")
        self.assertTrue(receipt["artifacts"]["nativeThinExecutionReceipt"])
        self.assertIn("geometry_verified", receipt["notEvidenceFor"])

    def test_scope_hash_drift_blocks_even_with_authorization(self) -> None:
        from core.contracts.native_thin_backend import build_native_thin_backend_authorization_gate

        with TemporaryDirectory() as tmp:
            packet = self._ready_launch_packet(tmp)
            pending = build_native_thin_backend_authorization_gate(launch_packet=packet)
            drifted = deepcopy(packet)
            drifted["cadPlan"] = deepcopy(drifted["cadPlan"])
            drifted["cadPlan"]["object"] = deepcopy(drifted["cadPlan"]["object"])
            drifted["cadPlan"]["object"]["width"] = 777
            blocked = build_native_thin_backend_authorization_gate(
                launch_packet=drifted,
                user_authorization=self._explicit_user_authorization(pending["launchPacketHash"]),
            )

        self.assertEqual(blocked["status"], "blocked")
        self.assertEqual(blocked["authorizationStatus"], "blocked")
        self.assertIn("native_scope_hash_mismatch", blocked["blockingReasons"])
        self.assertFalse(blocked["liveExecutionAuthorized"])
        self.assertFalse(blocked["cadWritesAttempted"])
        self.assertFalse(blocked["nativePluginInvoked"])

    def test_registry_and_harness_block_p13c_live_effect_bypass(self) -> None:
        from core.contracts.adapter_registry import authorize_registered_adapter, default_adapter_registry
        from core.contracts.cad_agent_harness import run_harness_command

        adapter = default_adapter_registry()["native-thin.backend"]
        self.assertIn("native_thin_live_authorization_gate_write", adapter.tool_card.allowed_effects)
        self.assertIn("native_thin_execution_receipt_write", adapter.tool_card.allowed_effects)

        allowed = authorize_registered_adapter(
            adapter_id="native-thin.backend",
            task_id="task-p13c-authorization",
            requested_effects=[
                "native_thin_live_authorization_gate_write",
                "native_thin_execution_receipt_write",
            ],
        )
        self.assertEqual(allowed.status, "allowed")

        for effect in ["native_plugin_execute", "real_cad_readback", "dwg_save", "formal_layer_write"]:
            with self.subTest(effect=effect):
                blocked = authorize_registered_adapter(
                    adapter_id="native-thin.backend",
                    task_id="task-p13c-effect-bypass",
                    requested_effects=[effect],
                )
                self.assertEqual(blocked.status, "blocked")
                self.assertIn(effect, " ".join(blocked.blocking_reasons))

        with TemporaryDirectory() as tmp:
            packet = self._ready_launch_packet(tmp)
            auth_result = run_harness_command(
                "native-thin-backend",
                output_dir=tmp,
                launch_packet_path=packet["artifacts"]["nativeThinLaunchPacket"],
                backend="native-thin-skeleton",
                native_backend_mode="authorization",
            )
            blocked = run_harness_command(
                "native-thin-backend",
                backend="native-thin-skeleton",
                requested_effects=["native_plugin_execute"],
                native_backend_mode="authorization",
            )

        self.assertEqual(auth_result["status"], "blocked")
        self.assertEqual(auth_result["registryAuthorization"]["status"], "allowed")
        self.assertEqual(auth_result["nativeThinBackend"]["authorizationStatus"], "authorization_pending")
        self.assertFalse(auth_result["cadWritesAttempted"])
        self.assertFalse(auth_result["nativePluginInvoked"])

        self.assertEqual(blocked["status"], "blocked")
        self.assertEqual(blocked["registryAuthorization"]["status"], "blocked")
        self.assertIn("native_plugin_execute", " ".join(blocked["blockingReasons"]))
        self.assertFalse(blocked["cadWritesAttempted"])


class P13DNativeThinReadinessTests(unittest.TestCase):
    def _ready_execution_receipt(self, output_dir: str) -> dict[str, object]:
        from core.contracts.native_thin_backend import (
            build_native_thin_backend_authorization_gate,
            build_native_thin_backend_execution_receipt,
            build_native_thin_backend_launch_packet,
            build_native_thin_backend_scope_receipt,
        )

        scope_receipt = build_native_thin_backend_scope_receipt(
            cad_plan=_cad_plan_fixture(),
            output_dir=output_dir,
            scope_confirmed=True,
            confirmation_statement="confirmed P13B native thin scoped preflight only",
            backend_identity="native-thin-skeleton",
            readback_plan={"required": True, "strategy": "created_handles_bbox_props"},
            rollback_plan={"required": True, "strategy": "rollback_batch"},
            no_save_guard={"required": True, "saveAllowed": False},
        )
        launch_packet = build_native_thin_backend_launch_packet(
            scope_receipt_path=scope_receipt["artifacts"]["nativeThinScopeReceipt"],
            output_dir=output_dir,
        )
        pending_gate = build_native_thin_backend_authorization_gate(launch_packet=launch_packet)
        ready_gate = build_native_thin_backend_authorization_gate(
            launch_packet=launch_packet,
            output_dir=output_dir,
            user_authorization={
                "explicit": True,
                "scopeConfirmed": True,
                "cadPlanConfirmed": True,
                "codexPreviewConfirmed": True,
                "readbackConfirmed": True,
                "rollbackConfirmed": True,
                "noSaveConfirmed": True,
                "backendIdentityConfirmed": True,
                "launchPacketHash": pending_gate["launchPacketHash"],
                "statement": (
                    "I explicitly authorize the P13C scoped receipt for CODEX_PREVIEW "
                    "with readback, rollback, no-save guard, and native-thin-skeleton backend identity."
                ),
            },
        )
        return build_native_thin_backend_execution_receipt(
            authorization_gate_path=ready_gate["artifacts"]["nativeThinAuthorizationGate"],
            output_dir=output_dir,
        )

    def test_p13d_readiness_packet_requests_operator_authorization_without_execution(self) -> None:
        from core.contracts.native_thin_backend import build_native_thin_backend_readiness_packet

        with TemporaryDirectory() as tmp:
            receipt = self._ready_execution_receipt(tmp)
            readiness = build_native_thin_backend_readiness_packet(
                execution_receipt_path=receipt["artifacts"]["nativeThinExecutionReceipt"],
                output_dir=tmp,
            )

        self.assertEqual(readiness["schemaVersion"], "native-thin-readiness/p13d/v1")
        self.assertEqual(readiness["kind"], "operator_authorization_request")
        self.assertEqual(readiness["status"], "ready_for_user_authorization")
        self.assertEqual(readiness["authorizationRequestStatus"], "ready_for_user_authorization")
        self.assertTrue(readiness["realLiveSpikeAuthorizationRequired"])
        self.assertFalse(readiness["operatorLiveSpikeAuthorized"])
        self.assertFalse(readiness["executionStarted"])
        self.assertFalse(readiness["cadWritesAttempted"])
        self.assertFalse(readiness["nativePluginInvoked"])
        self.assertFalse(readiness["cadGeometryVerified"])
        self.assertEqual(readiness["targetLayer"], "CODEX_PREVIEW")
        self.assertTrue(readiness["cadPlan"])
        self.assertTrue(readiness["readbackPlan"]["required"])
        self.assertTrue(readiness["rollbackPlan"]["required"])
        self.assertFalse(readiness["noSaveGuard"]["saveAllowed"])
        self.assertEqual(readiness["backendIdentity"]["backend"], "native-thin-skeleton")
        self.assertTrue(readiness["launchPacketHash"])
        self.assertTrue(readiness["authorizationReceiptHash"])
        self.assertEqual(readiness["authorizationReceiptHash"], readiness["executionReceiptHash"])
        self.assertIn("native_thin_live_readiness_packet_write", readiness["allowedEffects"])
        self.assertIn("native_thin_operator_authorization_request_write", readiness["allowedEffects"])
        self.assertTrue(readiness["operatorAuthorizationRequest"]["requiresSeparateUserAuthorization"])
        self.assertIn("real_cad_readback", readiness["notEvidenceFor"])
        self.assertIn("geometry_verified", readiness["notEvidenceFor"])
        self.assertTrue(readiness["artifacts"]["nativeThinReadinessPacket"])
        self.assertTrue(readiness["artifacts"]["nativeThinOperatorAuthorizationRequest"])

    def test_p13d_readiness_blocks_missing_or_drifted_execution_receipt(self) -> None:
        from core.contracts.native_thin_backend import build_native_thin_backend_readiness_packet

        missing = build_native_thin_backend_readiness_packet(execution_receipt_path=None)
        self.assertEqual(missing["status"], "blocked")
        self.assertIn("native_execution_receipt_required", missing["blockingReasons"])
        self.assertFalse(missing["executionStarted"])
        self.assertFalse(missing["cadWritesAttempted"])
        self.assertFalse(missing["nativePluginInvoked"])

        with TemporaryDirectory() as tmp:
            receipt = self._ready_execution_receipt(tmp)
            drifted = build_native_thin_backend_readiness_packet(
                execution_receipt=receipt,
                expected_authorization_receipt_hash="not-the-current-receipt-hash",
            )

        self.assertEqual(drifted["status"], "blocked")
        self.assertIn("native_authorization_receipt_hash_mismatch", drifted["blockingReasons"])
        self.assertFalse(drifted["executionStarted"])
        self.assertFalse(drifted["cadWritesAttempted"])
        self.assertFalse(drifted["nativePluginInvoked"])

    def test_p13d_readiness_blocks_receipt_that_claims_execution_or_real_proof(self) -> None:
        from core.contracts.native_thin_backend import build_native_thin_backend_readiness_packet

        with TemporaryDirectory() as tmp:
            receipt = self._ready_execution_receipt(tmp)
            invalid = deepcopy(receipt)
            invalid["executionStarted"] = True
            invalid["cadWritesAttempted"] = True
            invalid["nativePluginInvoked"] = True
            invalid["cadGeometryVerified"] = True
            invalid["targetLayer"] = "A-WALL"
            invalid["noSaveGuard"] = {"required": True, "saveAllowed": True}
            invalid["backendIdentity"] = {"backend": "native-real-plugin"}
            blocked = build_native_thin_backend_readiness_packet(execution_receipt=invalid)

        self.assertEqual(blocked["status"], "blocked")
        self.assertIn("native_execution_receipt_must_not_start_execution", blocked["blockingReasons"])
        self.assertIn("native_execution_receipt_must_not_attempt_cad_write", blocked["blockingReasons"])
        self.assertIn("native_execution_receipt_must_not_invoke_plugin", blocked["blockingReasons"])
        self.assertIn("native_execution_receipt_must_not_claim_geometry_verified", blocked["blockingReasons"])
        self.assertIn("target_layer_must_be_CODEX_PREVIEW", blocked["blockingReasons"])
        self.assertIn("backend_identity_must_be_native_thin_skeleton", blocked["blockingReasons"])
        self.assertIn("no_save_guard_must_block_save", blocked["blockingReasons"])
        self.assertFalse(blocked["executionStarted"])
        self.assertFalse(blocked["cadWritesAttempted"])
        self.assertFalse(blocked["nativePluginInvoked"])

    def test_registry_and_harness_block_p13d_live_effect_bypass(self) -> None:
        from core.contracts.adapter_registry import authorize_registered_adapter, default_adapter_registry
        from core.contracts.cad_agent_harness import run_harness_command

        adapter = default_adapter_registry()["native-thin.backend"]
        self.assertIn("native_thin_live_readiness_packet_write", adapter.tool_card.allowed_effects)
        self.assertIn("native_thin_operator_authorization_request_write", adapter.tool_card.allowed_effects)

        allowed = authorize_registered_adapter(
            adapter_id="native-thin.backend",
            task_id="task-p13d-readiness",
            requested_effects=[
                "native_thin_live_readiness_packet_write",
                "native_thin_operator_authorization_request_write",
            ],
        )
        self.assertEqual(allowed.status, "allowed")

        for effect in ["native_plugin_execute", "cad_execute", "real_cad_readback", "dwg_save", "formal_layer_write"]:
            with self.subTest(effect=effect):
                blocked = authorize_registered_adapter(
                    adapter_id="native-thin.backend",
                    task_id="task-p13d-effect-bypass",
                    requested_effects=[effect],
                )
                self.assertEqual(blocked.status, "blocked")
                self.assertIn(effect, " ".join(blocked.blocking_reasons))

        with TemporaryDirectory() as tmp:
            receipt = self._ready_execution_receipt(tmp)
            readiness_result = run_harness_command(
                "native-thin-backend",
                output_dir=tmp,
                execution_receipt_path=receipt["artifacts"]["nativeThinExecutionReceipt"],
                backend="native-thin-skeleton",
                native_backend_mode="readiness",
            )
            blocked = run_harness_command(
                "native-thin-backend",
                backend="native-thin-skeleton",
                requested_effects=["native_plugin_execute"],
                native_backend_mode="readiness",
            )

        self.assertEqual(readiness_result["status"], "ready_for_user_authorization")
        self.assertEqual(readiness_result["registryAuthorization"]["status"], "allowed")
        self.assertFalse(readiness_result["executionStarted"])
        self.assertFalse(readiness_result["cadWritesAttempted"])
        self.assertFalse(readiness_result["nativePluginInvoked"])
        self.assertTrue(readiness_result["nativeThinBackend"]["authorizationReceiptHash"])

        self.assertEqual(blocked["status"], "blocked")
        self.assertEqual(blocked["registryAuthorization"]["status"], "blocked")
        self.assertIn("native_plugin_execute", " ".join(blocked["blockingReasons"]))
        self.assertFalse(blocked["cadWritesAttempted"])


class P13ENativeThinLiveSpikeGateTests(unittest.TestCase):
    def _ready_execution_receipt(self, output_dir: str) -> dict[str, object]:
        from core.contracts.native_thin_backend import (
            build_native_thin_backend_authorization_gate,
            build_native_thin_backend_execution_receipt,
            build_native_thin_backend_launch_packet,
            build_native_thin_backend_scope_receipt,
        )

        scope_receipt = build_native_thin_backend_scope_receipt(
            cad_plan=_cad_plan_fixture(),
            output_dir=output_dir,
            scope_confirmed=True,
            confirmation_statement="confirmed P13B native thin scoped preflight only",
            backend_identity="native-thin-skeleton",
            readback_plan={"required": True, "strategy": "created_handles_bbox_props"},
            rollback_plan={"required": True, "strategy": "rollback_batch"},
            no_save_guard={"required": True, "saveAllowed": False},
        )
        launch_packet = build_native_thin_backend_launch_packet(
            scope_receipt_path=scope_receipt["artifacts"]["nativeThinScopeReceipt"],
            output_dir=output_dir,
        )
        pending_gate = build_native_thin_backend_authorization_gate(launch_packet=launch_packet)
        ready_gate = build_native_thin_backend_authorization_gate(
            launch_packet=launch_packet,
            output_dir=output_dir,
            user_authorization={
                "explicit": True,
                "scopeConfirmed": True,
                "cadPlanConfirmed": True,
                "codexPreviewConfirmed": True,
                "readbackConfirmed": True,
                "rollbackConfirmed": True,
                "noSaveConfirmed": True,
                "backendIdentityConfirmed": True,
                "launchPacketHash": pending_gate["launchPacketHash"],
                "statement": (
                    "I explicitly authorize the P13C scoped receipt for CODEX_PREVIEW "
                    "with readback, rollback, no-save guard, and native-thin-skeleton backend identity."
                ),
            },
        )
        return build_native_thin_backend_execution_receipt(
            authorization_gate_path=ready_gate["artifacts"]["nativeThinAuthorizationGate"],
            output_dir=output_dir,
        )

    def _ready_readiness_packet(self, output_dir: str) -> dict[str, object]:
        from core.contracts.native_thin_backend import build_native_thin_backend_readiness_packet

        receipt = self._ready_execution_receipt(output_dir)
        return build_native_thin_backend_readiness_packet(
            execution_receipt_path=receipt["artifacts"]["nativeThinExecutionReceipt"],
            output_dir=output_dir,
        )

    def _operator_authorization(self, readiness: dict[str, object]) -> dict[str, object]:
        return {
            "explicit": True,
            "scopeConfirmed": True,
            "cadPlanConfirmed": True,
            "codexPreviewConfirmed": True,
            "readbackConfirmed": True,
            "rollbackConfirmed": True,
            "noSaveConfirmed": True,
            "backendIdentityConfirmed": True,
            "launchPacketHash": readiness["launchPacketHash"],
            "authorizationReceiptHash": readiness["authorizationReceiptHash"],
            "statement": (
                "I separately authorize the P13E minimal native live spike for CODEX_PREVIEW "
                "with readback, rollback, no-save guard, backend identity, launch packet hash, "
                "and authorization receipt hash confirmed."
            ),
        }

    def test_p13e_blocks_missing_operator_authorization_without_touching_cad(self) -> None:
        from core.contracts.native_thin_backend import build_native_thin_backend_live_spike_execution_gate

        with TemporaryDirectory() as tmp:
            readiness = self._ready_readiness_packet(tmp)
            gate = build_native_thin_backend_live_spike_execution_gate(
                readiness_packet_path=readiness["artifacts"]["nativeThinReadinessPacket"],
                output_dir=tmp,
            )

        self.assertEqual(gate["schemaVersion"], "native-thin-live-spike-gate/p13e/v1")
        self.assertEqual(gate["kind"], "minimal_live_spike_execution_gate")
        self.assertEqual(gate["status"], "blocked")
        self.assertEqual(gate["closeoutStatus"], "missing_authorization")
        self.assertIn("native_live_spike_operator_authorization_required", gate["blockingReasons"])
        self.assertFalse(gate["executionStarted"])
        self.assertFalse(gate["cadWritesAttempted"])
        self.assertFalse(gate["nativePluginInvoked"])
        self.assertFalse(gate["cadGeometryVerified"])
        self.assertFalse(gate["savedCurrentDwg"])
        self.assertEqual(gate["noSaveAudit"]["status"], "not_run_no_cad")
        self.assertEqual(gate["rollbackProof"]["status"], "not_run_no_transaction")
        self.assertEqual(gate["bboxLayerEntityAudit"]["status"], "not_run_no_execution")
        self.assertTrue(gate["artifacts"]["nativeThinLiveSpikeExecutionGate"])
        self.assertIn("real_cad_readback", gate["notEvidenceFor"])
        self.assertIn("geometry_verified", gate["notEvidenceFor"])

    def test_p13e_blocks_operator_authorization_hash_drift_before_backend(self) -> None:
        from core.contracts.native_thin_backend import build_native_thin_backend_live_spike_execution_gate

        with TemporaryDirectory() as tmp:
            readiness = self._ready_readiness_packet(tmp)
            auth = self._operator_authorization(readiness)
            auth["authorizationReceiptHash"] = "drifted-authorization-receipt-hash"
            gate = build_native_thin_backend_live_spike_execution_gate(
                readiness_packet=readiness,
                operator_authorization=auth,
            )

        self.assertEqual(gate["status"], "blocked")
        self.assertEqual(gate["closeoutStatus"], "missing_authorization")
        self.assertIn("native_live_spike_authorization_receipt_hash_mismatch", gate["blockingReasons"])
        self.assertFalse(gate["executionStarted"])
        self.assertFalse(gate["cadWritesAttempted"])
        self.assertFalse(gate["nativePluginInvoked"])

    def test_p13e_authorized_but_missing_environment_returns_external_blocker(self) -> None:
        from core.contracts.native_thin_backend import build_native_thin_backend_live_spike_execution_gate

        with TemporaryDirectory() as tmp:
            readiness = self._ready_readiness_packet(tmp)
            gate = build_native_thin_backend_live_spike_execution_gate(
                readiness_packet=readiness,
                operator_authorization=self._operator_authorization(readiness),
                environment={},
            )

        self.assertEqual(gate["status"], "external_blocker")
        self.assertEqual(gate["closeoutStatus"], "external_blocker")
        self.assertIn("native_live_backend_environment_required", gate["blockingReasons"])
        self.assertEqual(gate["proofStatus"], "native_live_spike_external_blocker_no_execution")
        self.assertFalse(gate["executionStarted"])
        self.assertFalse(gate["cadWritesAttempted"])
        self.assertFalse(gate["nativePluginInvoked"])
        self.assertFalse(gate["cadGeometryVerified"])

    def test_registry_and_harness_block_p13e_live_execution_bypass(self) -> None:
        from core.contracts.adapter_registry import authorize_registered_adapter, default_adapter_registry
        from core.contracts.cad_agent_harness import run_harness_command

        adapter = default_adapter_registry()["native-thin.backend"]
        self.assertIn("native_thin_live_spike_execution_gate_write", adapter.tool_card.allowed_effects)
        self.assertIn("native_thin_external_blocker_closeout_write", adapter.tool_card.allowed_effects)

        allowed = authorize_registered_adapter(
            adapter_id="native-thin.backend",
            task_id="task-p13e-live-spike-gate",
            requested_effects=[
                "native_thin_live_spike_execution_gate_write",
                "native_thin_external_blocker_closeout_write",
            ],
        )
        self.assertEqual(allowed.status, "allowed")

        for effect in ["native_plugin_execute", "cad_execute", "real_cad_readback", "dwg_save", "formal_layer_write"]:
            with self.subTest(effect=effect):
                blocked = authorize_registered_adapter(
                    adapter_id="native-thin.backend",
                    task_id="task-p13e-effect-bypass",
                    requested_effects=[effect],
                )
                self.assertEqual(blocked.status, "blocked")
                self.assertIn(effect, " ".join(blocked.blocking_reasons))

        with TemporaryDirectory() as tmp:
            readiness = self._ready_readiness_packet(tmp)
            gate_result = run_harness_command(
                "native-thin-backend",
                output_dir=tmp,
                backend="native-thin-skeleton",
                readiness_packet_path=readiness["artifacts"]["nativeThinReadinessPacket"],
                native_backend_mode="live_spike_gate",
            )
            blocked = run_harness_command(
                "native-thin-backend",
                backend="native-thin-skeleton",
                requested_effects=["native_plugin_execute"],
                native_backend_mode="live_spike_gate",
            )

        self.assertEqual(gate_result["status"], "blocked")
        self.assertEqual(gate_result["closeoutStatus"], "missing_authorization")
        self.assertEqual(gate_result["registryAuthorization"]["status"], "allowed")
        self.assertFalse(gate_result["executionStarted"])
        self.assertFalse(gate_result["cadWritesAttempted"])
        self.assertFalse(gate_result["nativePluginInvoked"])
        self.assertTrue(gate_result["nativeThinBackend"]["readinessPacketHash"])

        self.assertEqual(blocked["status"], "blocked")
        self.assertEqual(blocked["registryAuthorization"]["status"], "blocked")
        self.assertIn("native_plugin_execute", " ".join(blocked["blockingReasons"]))
        self.assertFalse(blocked["cadWritesAttempted"])


class P13FNativeThinLiveSpikeTests(unittest.TestCase):
    def _ready_readiness_packet(self, output_dir: str) -> dict[str, object]:
        from core.contracts.native_thin_backend import (
            build_native_thin_backend_authorization_gate,
            build_native_thin_backend_execution_receipt,
            build_native_thin_backend_launch_packet,
            build_native_thin_backend_readiness_packet,
            build_native_thin_backend_scope_receipt,
        )

        scope_receipt = build_native_thin_backend_scope_receipt(
            cad_plan=_cad_plan_fixture(),
            output_dir=output_dir,
            scope_confirmed=True,
            confirmation_statement="confirmed P13F native thin scoped live spike",
            backend_identity="native-thin-skeleton",
            readback_plan={"required": True, "strategy": "created_handles_bbox_props"},
            rollback_plan={"required": True, "strategy": "rollback_batch"},
            no_save_guard={"required": True, "saveAllowed": False},
        )
        launch_packet = build_native_thin_backend_launch_packet(
            scope_receipt_path=scope_receipt["artifacts"]["nativeThinScopeReceipt"],
            output_dir=output_dir,
        )
        pending_gate = build_native_thin_backend_authorization_gate(launch_packet=launch_packet)
        ready_gate = build_native_thin_backend_authorization_gate(
            launch_packet=launch_packet,
            output_dir=output_dir,
            user_authorization={
                "explicit": True,
                "scopeConfirmed": True,
                "cadPlanConfirmed": True,
                "codexPreviewConfirmed": True,
                "readbackConfirmed": True,
                "rollbackConfirmed": True,
                "noSaveConfirmed": True,
                "backendIdentityConfirmed": True,
                "launchPacketHash": pending_gate["launchPacketHash"],
                "statement": (
                    "I explicitly authorize the P13C scoped receipt for CODEX_PREVIEW "
                    "with readback, rollback, no-save guard, and native-thin-skeleton backend identity."
                ),
            },
        )
        execution_receipt = build_native_thin_backend_execution_receipt(
            authorization_gate_path=ready_gate["artifacts"]["nativeThinAuthorizationGate"],
            output_dir=output_dir,
        )
        return build_native_thin_backend_readiness_packet(
            execution_receipt_path=execution_receipt["artifacts"]["nativeThinExecutionReceipt"],
            output_dir=output_dir,
        )

    def _operator_authorization(self, readiness: dict[str, object]) -> dict[str, object]:
        return {
            "explicit": True,
            "scopeConfirmed": True,
            "cadPlanConfirmed": True,
            "codexPreviewConfirmed": True,
            "readbackConfirmed": True,
            "rollbackConfirmed": True,
            "noSaveConfirmed": True,
            "backendIdentityConfirmed": True,
            "launchPacketHash": readiness["launchPacketHash"],
            "authorizationReceiptHash": readiness["authorizationReceiptHash"],
            "environmentReady": True,
            "statement": (
                "I separately authorize the P13F minimal native live spike for CODEX_PREVIEW "
                "with created handles readback, rollback proof, no-save guard, backend identity, "
                "launch packet hash, authorization receipt hash, and environment readiness confirmed."
            ),
        }

    def _environment(self) -> dict[str, object]:
        return {
            "nativeThinBackendAvailable": True,
            "autocadConnectionAvailable": True,
            "readbackRunnerAvailable": True,
            "rollbackRunnerAvailable": True,
            "noSaveGuardActive": True,
            "backendIdentity": {"backend": "native-thin-skeleton"},
            "targetLayer": "CODEX_PREVIEW",
            "dwgSaveAllowed": False,
            "formalLayerWriteAllowed": False,
        }

    def _verified_runner_result(self, **kwargs: object) -> dict[str, object]:
        output_dir = str(kwargs["output_dir"])
        return {
            "schemaVersion": "native-thin-autocad-plugin-result/p13f/v1",
            "status": "geometry_verified",
            "verificationStatus": "verified",
            "backend": "autocad_plugin",
            "targetLayer": "CODEX_PREVIEW",
            "transactionId": "tx-p13f-native-live-spike-001",
            "nativePluginInvoked": True,
            "cadWritesAttempted": True,
            "savedCurrentDwg": False,
            "committedPreview": True,
            "createdHandles": ["2A1"],
            "createdHandlesReadback": {
                "status": "verified",
                "readbackStatus": "verified",
                "createdHandles": ["2A1"],
                "entities": [
                    {
                        "handle": "2A1",
                        "type": "LWPOLYLINE",
                        "layer": "CODEX_PREVIEW",
                        "bbox": {"min": [100.0, 200.0, 0.0], "max": [1300.0, 800.0, 0.0]},
                    }
                ],
            },
            "bboxLayerEntityAudit": {
                "status": "verified",
                "bboxChecked": True,
                "layerChecked": True,
                "entityAuditChecked": True,
                "targetLayer": "CODEX_PREVIEW",
            },
            "rollbackRequired": True,
            "rollbackStatus": "rolled_back",
            "rollbackProof": {
                "status": "verified",
                "rollbackRequired": True,
                "rollbackStatus": "rolled_back",
                "verified": True,
                "rolledBackHandles": ["2A1"],
            },
            "noSaveAudit": {
                "status": "verified",
                "saveAttempted": False,
                "saveAllowed": False,
                "savedCurrentDwg": False,
            },
            "documentStateBefore": "temporary_core_console_document",
            "documentState": "rolled_back_no_save",
            "documentStateAfter": "rolled_back_no_save",
            "artifacts": {"nativePluginReport": output_dir + "\\native_thin_plugin_result.json"},
        }

    def test_p13f_registers_scoped_live_spike_adapter_without_generic_plugin_effects(self) -> None:
        from core.contracts.adapter_registry import authorize_registered_adapter, default_adapter_registry

        adapter = default_adapter_registry()["native-thin.live-spike"]

        self.assertEqual(adapter.command, "native-thin-live-spike")
        self.assertEqual(adapter.backend, "native-thin-live-backend")
        self.assertEqual(adapter.tool_card.permission_class, "cad_preview")
        self.assertTrue(adapter.executes_cad)
        self.assertTrue(adapter.writes_dwg)
        self.assertTrue(adapter.reads_dwg)
        self.assertTrue(adapter.calls_plugin)
        self.assertFalse(adapter.saves_dwg)
        self.assertIn("native_thin_scoped_live_spike_execute", adapter.tool_card.allowed_effects)
        self.assertIn("native_thin_created_handles_readback", adapter.tool_card.allowed_effects)
        self.assertIn("native_plugin_execute", adapter.tool_card.forbidden_effects)
        self.assertIn("dwg_save", adapter.tool_card.forbidden_effects)
        self.assertIn("formal_layer_write", adapter.tool_card.forbidden_effects)

        allowed = authorize_registered_adapter(
            adapter_id="native-thin.live-spike",
            task_id="task-p13f-live-spike",
            requested_effects=[
                "native_thin_scoped_live_spike_execute",
                "native_thin_created_handles_readback",
                "native_thin_bbox_layer_entity_audit",
                "native_thin_rollback_created_handles",
                "native_thin_no_save_audit",
            ],
        )
        self.assertEqual(allowed.status, "allowed")

        for effect in ["native_plugin_execute", "cad_execute", "real_cad_readback", "dwg_save", "formal_layer_write"]:
            with self.subTest(effect=effect):
                blocked = authorize_registered_adapter(
                    adapter_id="native-thin.live-spike",
                    task_id="task-p13f-effect-bypass",
                    requested_effects=[effect],
                )
                self.assertEqual(blocked.status, "blocked")
                self.assertIn(effect, " ".join(blocked.blocking_reasons))

    def test_p13f_live_spike_result_requires_readback_rollback_and_no_save_proof(self) -> None:
        from core.contracts.native_thin_backend import execute_native_thin_live_spike

        with TemporaryDirectory() as tmp:
            readiness = self._ready_readiness_packet(tmp)
            result = execute_native_thin_live_spike(
                readiness_packet=readiness,
                operator_authorization=self._operator_authorization(readiness),
                environment=self._environment(),
                output_dir=tmp,
                runner=self._verified_runner_result,
            )

        self.assertEqual(result["schemaVersion"], "native-thin-live-spike/p13f/v1")
        self.assertEqual(result["adapterId"], "native-thin.live-spike")
        self.assertEqual(result["backend"], "native_thin_live_backend")
        self.assertEqual(result["backendIdentity"]["backend"], "native_thin_live_backend")
        self.assertEqual(result["backendIdentity"]["adapterId"], "native-thin.live-spike")
        self.assertEqual(result["backendIdentity"]["pluginBackend"], "autocad_plugin")
        self.assertTrue(result["backendIdentity"]["nativePluginInvoked"])
        self.assertEqual(result["backendIdentity"]["sourceReadinessBackend"]["backend"], "native-thin-skeleton")
        self.assertEqual(result["status"], "geometry_verified")
        self.assertEqual(result["verificationStatus"], "verified")
        self.assertTrue(result["cadGeometryVerified"])
        self.assertTrue(result["cadWritesAttempted"])
        self.assertTrue(result["nativePluginInvoked"])
        self.assertFalse(result["savedCurrentDwg"])
        self.assertTrue(result["committedPreview"])
        self.assertEqual(result["rollbackStatus"], "rolled_back")
        self.assertEqual(result["createdHandles"], ["2A1"])
        self.assertEqual(result["createdHandlesReadback"]["status"], "verified")
        self.assertEqual(result["bboxLayerEntityAudit"]["status"], "verified")
        self.assertEqual(result["rollbackProof"]["status"], "verified")
        self.assertEqual(result["noSaveAudit"]["savedCurrentDwg"], False)
        self.assertNotIn("real_cad_readback", result["notEvidenceFor"])
        self.assertNotIn("geometry_verified", result["notEvidenceFor"])

    def test_p13f_harness_routes_live_spike_through_registry_and_blocks_bypass(self) -> None:
        from core.contracts.cad_agent_harness import run_harness_command
        from unittest import mock

        with TemporaryDirectory() as tmp:
            readiness = self._ready_readiness_packet(tmp)
            with mock.patch(
                "core.contracts.native_thin_backend.run_native_thin_autocad_core_console_spike",
                self._verified_runner_result,
            ):
                result = run_harness_command(
                    "native-thin-live-spike",
                    backend="native-thin-live-backend",
                    readiness_packet_path=readiness["artifacts"]["nativeThinReadinessPacket"],
                    operator_authorization=self._operator_authorization(readiness),
                    native_live_environment=self._environment(),
                    output_dir=tmp,
                )
            blocked = run_harness_command(
                "native-thin-live-spike",
                backend="native-thin-live-backend",
                requested_effects=["native_plugin_execute"],
                output_dir=tmp,
            )

        self.assertEqual(result["registryAuthorization"]["status"], "allowed")
        self.assertEqual(result["registryAdapter"]["adapterId"], "native-thin.live-spike")
        self.assertEqual(result["status"], "geometry_verified")
        self.assertEqual(result["verificationStatus"], "verified")
        self.assertTrue(result["cadGeometryVerified"])
        self.assertTrue(result["cadWritesAttempted"])
        self.assertTrue(result["nativePluginInvoked"])
        self.assertFalse(result["savedCurrentDwg"])

        self.assertEqual(blocked["status"], "blocked")
        self.assertEqual(blocked["registryAuthorization"]["status"], "blocked")
        self.assertIn("native_plugin_execute", " ".join(blocked["blockingReasons"]))
        self.assertFalse(blocked["cadWritesAttempted"])
        self.assertFalse(blocked["nativePluginInvoked"])


class P14EngineeringKernelBimTests(unittest.TestCase):
    def _cad_session_host_source(self) -> dict[str, object]:
        return {
            "backend": "cad_session_host",
            "status": "geometry_verified",
            "verificationStatus": "verified",
            "cadGeometryVerified": True,
            "cadWritesAttempted": True,
            "savedCurrentDwg": False,
            "targetLayer": "CODEX_PREVIEW",
            "createdHandles": ["10A"],
            "readbackEntities": [
                {
                    "handle": "10A",
                    "type": "LWPOLYLINE",
                    "layer": "CODEX_PREVIEW",
                    "bbox": {"min": [100, 200, 0], "max": [1300, 800, 0]},
                }
            ],
        }

    def _native_live_source(self) -> dict[str, object]:
        return {
            "backend": "native_thin_live_backend",
            "status": "geometry_verified",
            "verificationStatus": "verified",
            "cadGeometryVerified": True,
            "cadWritesAttempted": True,
            "nativePluginInvoked": True,
            "savedCurrentDwg": False,
            "targetLayer": "CODEX_PREVIEW",
            "createdHandles": ["2CF"],
            "readbackEntities": [
                {
                    "handle": "2CF",
                    "type": "LWPOLYLINE",
                    "layer": "CODEX_PREVIEW",
                    "bbox": {"min": [100, 200, 0], "max": [1300, 800, 0]},
                }
            ],
            "rollbackStatus": "rolled_back",
        }

    def test_p14_kernel_graphs_project_cad_plan_without_cad_execution(self) -> None:
        from core.contracts.engineering_kernel import build_engineering_kernel_graphs

        graphs = build_engineering_kernel_graphs(
            cad_plan=_cad_plan_fixture(),
            evidence_sources=[self._cad_session_host_source(), self._native_live_source()],
        )

        self.assertEqual(graphs["schemaVersion"], "engineering-kernel-graphs/p14/v1")
        self.assertEqual(graphs["status"], "ready")
        self.assertFalse(graphs["cadWritesAttempted"])
        self.assertFalse(graphs["cadGeometryVerified"])
        self.assertEqual(graphs["taskGraph"]["nodes"][0]["kind"], "cad_plan")
        self.assertEqual(graphs["geometryGraph"]["nodes"][0]["bbox"]["min"], [100, 200, 0])
        self.assertEqual(graphs["geometryGraph"]["nodes"][0]["bbox"]["max"], [1300, 800, 0])
        self.assertEqual(graphs["semanticGraph"]["nodes"][0]["semanticType"], "table")
        self.assertEqual(graphs["versionGraph"]["cadPlanHash"], graphs["versionGraph"]["sourceHashes"]["cadPlan"])
        self.assertEqual(sorted(graphs["evidenceGraph"]["backendEvidence"].keys()), [
            "cad_session_host",
            "native_thin_live_backend",
        ])
        self.assertIn("real_cad_readback", graphs["notEvidenceFor"])
        self.assertIn("geometry_verified", graphs["notEvidenceFor"])

    def test_p14_diff_package_compares_com_plugin_dxf_kernel_and_bim_candidates(self) -> None:
        from core.contracts.engineering_kernel import build_engineering_kernel_diff_package

        diff = build_engineering_kernel_diff_package(
            cad_plan=_cad_plan_fixture(),
            evidence_sources=[self._cad_session_host_source(), self._native_live_source()],
            backend_candidates=[
                "cad_session_host",
                "native_thin_live_backend",
                "dxf_file",
                "geometry_kernel",
                "ifc_bim",
            ],
        )

        self.assertEqual(diff["schemaVersion"], "engineering-kernel-diff-package/p14/v1")
        self.assertEqual(diff["status"], "ready")
        self.assertEqual(diff["comparisonStatus"], "complete")
        self.assertEqual(diff["evidenceCompleteness"], "partial")
        self.assertFalse(diff["cadWritesAttempted"])
        self.assertFalse(diff["cadGeometryVerified"])
        self.assertEqual(diff["verifiedBackends"], ["cad_session_host", "native_thin_live_backend"])
        self.assertEqual(diff["notRunBackends"], ["dxf_file", "geometry_kernel", "ifc_bim"])
        self.assertEqual(diff["geometryDelta"]["bboxDeltaCount"], 0)
        self.assertEqual(diff["styleDelta"]["layerDeltaCount"], 0)
        self.assertEqual(diff["semanticDelta"]["semanticTypeDeltaCount"], 0)
        self.assertIn("dxf_file", diff["backendCandidateDocs"])
        self.assertIn("ifc_bim", diff["backendCandidateDocs"])
        self.assertIn("real_cad_readback", diff["notEvidenceFor"])
        self.assertIn("training_resume", diff["notEvidenceFor"])

    def test_p14_registry_and_harness_route_kernel_diff_and_block_live_effects(self) -> None:
        from core.contracts.adapter_registry import authorize_registered_adapter, default_adapter_registry
        from core.contracts.cad_agent_harness import run_harness_command

        adapter = default_adapter_registry()["engineering-kernel.diff-package"]
        self.assertEqual(adapter.command, "engineering-kernel-diff")
        self.assertEqual(adapter.backend, "engineering-kernel")
        self.assertEqual(adapter.tool_card.permission_class, "deterministic_verify")
        self.assertFalse(adapter.executes_cad)
        self.assertFalse(adapter.writes_dwg)
        self.assertIn("engineering_kernel_graph_build", adapter.tool_card.allowed_effects)
        self.assertIn("engineering_kernel_diff_package_write", adapter.tool_card.allowed_effects)
        self.assertIn("cad_execute", adapter.tool_card.forbidden_effects)
        self.assertIn("native_plugin_execute", adapter.tool_card.forbidden_effects)
        self.assertIn("dwg_save", adapter.tool_card.forbidden_effects)
        self.assertIn("formal_layer_write", adapter.tool_card.forbidden_effects)

        allowed = authorize_registered_adapter(
            adapter_id="engineering-kernel.diff-package",
            task_id="task-p14-engineering-kernel",
            requested_effects=["engineering_kernel_graph_build", "engineering_kernel_diff_package_write"],
        )
        self.assertEqual(allowed.status, "allowed")

        for effect in ["cad_execute", "native_plugin_execute", "real_cad_readback", "dwg_save", "formal_layer_write"]:
            with self.subTest(effect=effect):
                blocked = authorize_registered_adapter(
                    adapter_id="engineering-kernel.diff-package",
                    task_id="task-p14-effect-bypass",
                    requested_effects=[effect],
                )
                self.assertEqual(blocked.status, "blocked")
                self.assertIn(effect, " ".join(blocked.blocking_reasons))

        with TemporaryDirectory() as tmp:
            result = run_harness_command(
                "engineering-kernel-diff",
                backend="engineering-kernel",
                cad_plan=_cad_plan_fixture(),
                output_dir=tmp,
            )
            blocked = run_harness_command(
                "engineering-kernel-diff",
                backend="engineering-kernel",
                requested_effects=["cad_execute"],
                output_dir=tmp,
            )

        self.assertEqual(result["registryAuthorization"]["status"], "allowed")
        self.assertEqual(result["registryAdapter"]["adapterId"], "engineering-kernel.diff-package")
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["verificationStatus"], "not_verified")
        self.assertFalse(result["cadWritesAttempted"])
        self.assertFalse(result["cadGeometryVerified"])
        self.assertTrue(result["artifacts"]["engineeringKernelDiffPackage"])

        self.assertEqual(blocked["status"], "blocked")
        self.assertEqual(blocked["registryAuthorization"]["status"], "blocked")
        self.assertIn("cad_execute", " ".join(blocked["blockingReasons"]))
        self.assertFalse(blocked["cadWritesAttempted"])


if __name__ == "__main__":
    unittest.main()
