from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tests.helpers import temporary_artifact_dir


def _now() -> datetime:
    return datetime(2026, 6, 6, 8, 0, 0, tzinfo=timezone.utc)


def _learning_candidate() -> dict[str, object]:
    return {
        "decision": "not_required",
        "trigger": "not_required",
        "responsibleAgentIds": [],
        "errorPattern": "",
        "correctPattern": "",
        "promptDelta": "",
        "checkerDelta": "",
        "retestOriginalTask": False,
    }


def _state_patch(label: str) -> dict[str, object]:
    return {
        "phase": label,
        "phaseLabelForUser": label,
        "completedEvidence": ["unit-test live model bridge fixture"],
        "pendingEvidence": [],
        "pendingUserAction": "",
        "blockedReason": "",
        "nextSafeAction": "continue",
    }


def _design_director_model_output() -> dict[str, object]:
    return {
        "status": "pass",
        "designStrategy": {"styleCandidatePolicy": "multiple"},
        "drawingTypeDecision": "presentation_preview",
        "expressionPurpose": "prepare one design direction before CAD_PLAN",
        "designIntent": "make a compact tea-table symbol readable in CODEX_PREVIEW later",
        "audienceAndUse": "CAD Agent downstream design-stage decision",
        "constraints": ["no CAD write", "no DWG save", "no table C claim"],
        "requiredChildAgents": ["pipeline_style_generator"],
        "openQuestions": [],
        "evidenceBoundary": {"notProofOf": ["CAD geometry", "user acceptance"]},
        "learningCandidate": _learning_candidate(),
        "statePatch": _state_patch("single_agent_live"),
        "finalResponseAllowedClaims": ["single design director JSON is schema-valid"],
        "evidenceUsed": ["worker task envelope", "request summary"],
        "evidenceMissing": ["created handles readback"],
        "toolIntent": None,
        "decision": "pass",
        "assumptions": [],
        "alternativesConsidered": [],
        "blockingReasons": [],
        "nextRequiredEvidence": [],
    }


def _style_generator_model_output() -> dict[str, object]:
    return {
        "status": "pass",
        "styleDecision": "multiple",
        "styleCandidates": [{"id": "A", "label": "清晰符号"}, {"id": "B", "label": "更轻量"}],
        "selectedStyleCandidate": "A",
        "styleParameterGrammar": {"scale": "model_units"},
        "candidateTradeoffs": [{"id": "A", "tradeoff": "readable"}],
        "needsUserChoice": False,
        "styleWaiverReason": "",
        "candidateCountPolicy": "explicit_multi_candidate",
        "requestedCandidateCount": 2,
        "candidateLabelPolicy": "abc",
        "creativityPolicy": "contextual_not_forced",
        "semanticRoutingConfidence": "high",
        "learningCandidate": _learning_candidate(),
        "statePatch": _state_patch("multi_agent_live_style"),
        "finalResponseAllowedClaims": ["style candidates are schema-valid"],
        "evidenceUsed": ["agent_outputs/pipeline_design_director.json"],
        "evidenceMissing": [],
        "toolIntent": None,
        "decision": "pass",
        "assumptions": [],
        "alternativesConsidered": [],
        "blockingReasons": [],
        "nextRequiredEvidence": [],
    }


def _design_reviewer_model_output() -> dict[str, object]:
    return {
        "status": "pass",
        "designReview": "candidate A can feed deterministic CAD intent later",
        "professionalDrawingLike": True,
        "readability": True,
        "industryHabitFit": True,
        "scaleAndProportionFit": True,
        "styleCandidateFit": True,
        "contentMatchesDesignPurpose": True,
        "needsUserChoice": False,
        "repairOrRegenerateRecommendation": {},
        "learningCandidate": _learning_candidate(),
        "statePatch": _state_patch("multi_agent_live_review"),
        "finalResponseAllowedClaims": ["review output is schema-valid"],
        "evidenceUsed": [
            "agent_outputs/pipeline_design_director.json",
            "agent_outputs/pipeline_style_generator.json",
        ],
        "evidenceMissing": ["CAD readback"],
        "toolIntent": None,
        "decision": "pass",
        "assumptions": [],
        "alternativesConsidered": [],
        "blockingReasons": [],
        "nextRequiredEvidence": [],
    }


def _model_output_for_schema(schema_path: str) -> dict[str, object]:
    name = Path(schema_path).name
    if name == "design_director_review.schema.json":
        return _design_director_model_output()
    if name == "style_generation_review.schema.json":
        return _style_generator_model_output()
    if name == "design_review.schema.json":
        return _design_reviewer_model_output()
    raise AssertionError(f"unexpected schema path: {schema_path}")


def _valid_preview_cad_plan() -> dict[str, object]:
    return {
        "version": "0.1",
        "domain": "generic",
        "intent": "draw_object",
        "object": {"type": "table", "name": "茶几", "width": 1200, "depth": 600},
        "placement": {"mode": "absolute", "base_point": [0, 0, 0]},
        "drawing": {"layer": "CODEX_PREVIEW", "include_label": True, "include_dimensions": True},
        "confidence": 0.9,
        "needs_confirmation": False,
    }


class WorkerOrchestrationReadyTests(unittest.TestCase):
    def test_unknown_target_stage_is_not_silently_downgraded(self) -> None:
        from core.orchestrator.local_live_model_bridge import LocalLiveModelBridgeRuntime

        with temporary_artifact_dir("worker_unknown_stage") as root:
            runtime = LocalLiveModelBridgeRuntime(root_dir=root, now=_now)

            with self.assertRaises(ValueError):
                runtime.create_run(
                    request_summary="未知阶段不能悄悄降级成 worker-only。",
                    workspace_id="cad-agent-core-lab",
                    target_stage="made_up_live_stage",
                    agent_ids=["pipeline_design_director"],
                )

    def test_run_ids_do_not_collide_when_created_in_same_second(self) -> None:
        from core.orchestrator.local_live_model_bridge import LocalLiveModelBridgeRuntime

        with temporary_artifact_dir("worker_run_id_collision") as root:
            runtime = LocalLiveModelBridgeRuntime(root_dir=root, now=_now)

            first = runtime.create_run(
                request_summary="同一秒创建 run A。",
                workspace_id="cad-agent-core-lab",
                target_stage="worker_orchestration_ready",
                agent_ids=["pipeline_design_director"],
            )
            second = runtime.create_run(
                request_summary="同一秒创建 run B。",
                workspace_id="cad-agent-core-lab",
                target_stage="worker_orchestration_ready",
                agent_ids=["pipeline_design_director"],
            )

            self.assertNotEqual(first["runId"], second["runId"])
            self.assertTrue(Path(first["runDir"]).is_dir())
            self.assertTrue(Path(second["runDir"]).is_dir())

    def test_create_get_cancel_run_and_agent_dependencies(self) -> None:
        from core.orchestrator.local_live_model_bridge import LocalLiveModelBridgeRuntime

        with temporary_artifact_dir("worker_orchestration_ready") as root:
            runtime = LocalLiveModelBridgeRuntime(root_dir=root, now=_now)

            state = runtime.create_run(
                request_summary="设计一个茶几符号，先走 Worker 编排壳。",
                workspace_id="cad-agent-core-lab",
                target_stage="worker_orchestration_ready",
                agent_ids=[
                    "pipeline_design_director",
                    "pipeline_style_generator",
                    "pipeline_design_reviewer",
                ],
                dependencies={
                    "pipeline_style_generator": ["pipeline_design_director"],
                    "pipeline_design_reviewer": ["pipeline_style_generator"],
                },
                requested_by="codex_chat",
            )

            self.assertEqual(state["schemaVersion"], "worker_run_state/v1")
            self.assertEqual(state["state"], "queued")
            self.assertEqual(state["completionClaim"], "worker_orchestration_ready")
            self.assertTrue(state["featureGates"]["worker_orchestration_ready"]["enabled"])
            self.assertFalse(state["featureGates"]["local_bridge_connected"]["enabled"])
            self.assertFalse(state["featureGates"]["single_agent_live"]["enabled"])
            self.assertFalse(state["featureGates"]["multi_agent_live"]["enabled"])
            self.assertFalse(state["featureGates"]["cad_mcp_preview_live"]["enabled"])
            self.assertFalse(state["featureGates"]["current_dwg_save"]["enabled"])
            self.assertFalse(state["cadGeometryVerified"])
            self.assertFalse(state["modelInvoked"])
            self.assertEqual([task["agentId"] for task in state["tasks"]], [
                "pipeline_design_director",
                "pipeline_style_generator",
                "pipeline_design_reviewer",
            ])
            self.assertEqual(state["tasks"][1]["dependsOn"], ["task_pipeline_design_director_001"])
            self.assertEqual(state["tasks"][2]["dependsOn"], ["task_pipeline_style_generator_001"])
            self.assertEqual(state["circuitBreakers"]["local_bridge"]["state"], "closed")
            self.assertEqual(state["circuitBreakers"]["codex_cli_model_review"]["state"], "closed")

            resumed = runtime.get_run(state["runId"])
            self.assertEqual(resumed["runId"], state["runId"])

            cancelled = runtime.cancel_run(state["runId"], reason="user cancelled duplicate run")
            self.assertEqual(cancelled["state"], "cancelled")
            self.assertEqual(cancelled["blockedReasons"], ["user cancelled duplicate run"])
            self.assertEqual(cancelled["auditEvents"][-1]["eventType"], "run_cancelled")

    def test_target_stage_enables_only_required_feature_gates(self) -> None:
        from core.orchestrator.local_live_model_bridge import LocalLiveModelBridgeRuntime

        with temporary_artifact_dir("worker_feature_gates") as root:
            runtime = LocalLiveModelBridgeRuntime(root_dir=root, now=_now)

            state = runtime.create_run(
                request_summary="显式请求多 Agent live，但不授权 CAD 或保存。",
                workspace_id="cad-agent-core-lab",
                target_stage="multi_agent_live",
                agent_ids=[
                    "pipeline_design_director",
                    "pipeline_style_generator",
                    "pipeline_design_reviewer",
                ],
            )

            gates = state["featureGates"]
            self.assertTrue(gates["worker_orchestration_ready"]["enabled"])
            self.assertTrue(gates["local_bridge_connected"]["enabled"])
            self.assertTrue(gates["single_agent_live"]["enabled"])
            self.assertTrue(gates["multi_agent_live"]["enabled"])
            self.assertFalse(gates["cad_mcp_preview_live"]["enabled"])
            self.assertFalse(gates["current_dwg_save"]["enabled"])
            self.assertEqual(gates["multi_agent_live"]["enabledBy"], "target_stage:multi_agent_live")
            self.assertEqual(gates["current_dwg_save"]["nextAction"], "requires_explicit_save_authorization")

    def test_timeout_retry_security_block_and_idempotency_are_recorded(self) -> None:
        from core.orchestrator.local_live_model_bridge import LocalLiveModelBridgeRuntime

        clock = _now()

        def now() -> datetime:
            return clock

        with temporary_artifact_dir("worker_orchestration_guards") as root:
            runtime = LocalLiveModelBridgeRuntime(root_dir=root, now=now)
            state = runtime.create_run(
                request_summary="验证 Worker timeout / security / idempotency guard。",
                workspace_id="cad-agent-core-lab",
                target_stage="worker_orchestration_ready",
                task_specs=[
                    {
                        "taskId": "task_timeout_001",
                        "agentId": "pipeline_design_director",
                        "allowedTools": ["codex_cli_model_review"],
                        "timeoutSeconds": 5,
                        "maxAttempts": 2,
                    },
                    {
                        "taskId": "task_security_001",
                        "agentId": "pipeline_style_generator",
                        "dependsOn": ["task_timeout_001"],
                        "allowedTools": ["shell_arbitrary"],
                        "timeoutSeconds": 5,
                    },
                    {
                        "taskId": "task_after_security_001",
                        "agentId": "pipeline_design_reviewer",
                        "dependsOn": ["task_security_001"],
                        "allowedTools": ["codex_cli_model_review"],
                        "timeoutSeconds": 5,
                    },
                ],
            )

            leased = runtime.lease_task(
                bridge_id="fake_bridge_fixture",
                capabilities=["codex_cli_model_review"],
                heartbeat_token="hb-1",
            )
            self.assertEqual(leased["taskId"], "task_timeout_001")

            clock = _now() + timedelta(seconds=6)
            expired = runtime.expire_timed_out_tasks()
            self.assertEqual(expired["tasks"][0]["state"], "retry_scheduled")
            self.assertEqual(expired["tasks"][0]["retryCount"], 1)
            self.assertEqual(expired["tasks"][0]["attempt"], 1)
            self.assertEqual(expired["retryCount"], 1)

            retried = runtime.lease_task(
                bridge_id="fake_bridge_fixture",
                capabilities=["codex_cli_model_review"],
                heartbeat_token="hb-2",
            )
            self.assertEqual(retried["taskId"], "task_timeout_001")

            first_submit = runtime.submit_result(
                state["runId"],
                "task_timeout_001",
                result={
                    "schemaVersion": "agent_output/v1",
                    "status": "completed",
                    "decision": "continue",
                    "modelInvoked": False,
                    "modelUnavailable": False,
                    "schemaValid": True,
                    "summary": "fixture worker task complete",
                },
                idempotency_key="result-timeout-1",
                bridge_id="fake_bridge_fixture",
                heartbeat_token="hb-2",
            )
            duplicate_submit = runtime.submit_result(
                state["runId"],
                "task_timeout_001",
                result={
                    "schemaVersion": "agent_output/v1",
                    "status": "completed",
                    "decision": "continue",
                    "modelInvoked": False,
                    "modelUnavailable": False,
                    "schemaValid": True,
                    "summary": "duplicate should not advance twice",
                },
                idempotency_key="result-timeout-1",
                bridge_id="fake_bridge_fixture",
                heartbeat_token="hb-2",
            )
            self.assertEqual(first_submit["status"], "accepted")
            self.assertEqual(duplicate_submit["status"], "duplicate")

            blocked = runtime.get_run(state["runId"])
            security_task = next(task for task in blocked["tasks"] if task["taskId"] == "task_security_001")
            downstream_task = next(task for task in blocked["tasks"] if task["taskId"] == "task_after_security_001")
            self.assertEqual(security_task["state"], "blocked")
            self.assertEqual(security_task["blockedReason"], "security_blocked")
            self.assertEqual(security_task["retryCount"], 0)
            self.assertEqual(downstream_task["state"], "blocked")
            self.assertIn("upstream task_security_001 blocked", downstream_task["blockedReason"])
            self.assertIn("security_blocked", blocked["securityBlocks"])
            self.assertEqual(blocked["state"], "blocked")


class LocalBridgeConnectedTests(unittest.TestCase):
    def test_live_stage_rejects_unregistered_or_incapable_bridge(self) -> None:
        from core.orchestrator.local_live_model_bridge import LocalLiveModelBridgeRuntime

        with temporary_artifact_dir("local_bridge_registration_gate") as root:
            runtime = LocalLiveModelBridgeRuntime(root_dir=root, now=_now)
            state = runtime.create_run(
                request_summary="live bridge 必须先登记能力。",
                workspace_id="cad-agent-core-lab",
                target_stage="single_agent_live",
                agent_ids=["pipeline_design_director"],
            )

            unregistered = runtime.lease_task(
                bridge_id="unknown_bridge",
                capabilities=["codex_cli_model_review"],
                heartbeat_token="lease-token-unknown",
                run_id=state["runId"],
            )
            self.assertEqual(unregistered["status"], "bridge_unregistered")
            waiting = runtime.get_run(state["runId"])
            self.assertEqual(waiting["state"], "waiting_for_bridge")
            self.assertIn("bridge_unregistered", waiting["blockedReasons"])

            runtime.register_bridge(
                bridge_id="bridge_user_pc_001",
                capabilities=["cad_mcp_preview"],
                version="local-test",
            )
            incapable = runtime.lease_task(
                bridge_id="bridge_user_pc_001",
                capabilities=["codex_cli_model_review"],
                heartbeat_token="lease-token-incapable",
                run_id=state["runId"],
            )
            self.assertEqual(incapable["status"], "capability_mismatch")

    def test_registered_bridge_leases_heartbeats_and_submits_completed_result(self) -> None:
        from core.orchestrator.local_live_model_bridge import LocalLiveModelBridgeRuntime

        with temporary_artifact_dir("local_bridge_connected") as root:
            runtime = LocalLiveModelBridgeRuntime(root_dir=root, now=_now)
            bridge = runtime.register_bridge(
                bridge_id="bridge_user_pc_001",
                capabilities=["codex_cli_model_review"],
                version="local-test",
            )
            self.assertEqual(bridge["state"], "online")

            state = runtime.create_run(
                request_summary="本地 bridge 领取一个只读模型复审任务。",
                workspace_id="cad-agent-core-lab",
                target_stage="local_bridge_connected",
                agent_ids=["pipeline_design_director"],
            )

            envelope = runtime.lease_task(
                bridge_id="bridge_user_pc_001",
                capabilities=["codex_cli_model_review"],
                heartbeat_token="lease-token-1",
                run_id=state["runId"],
            )
            self.assertEqual(envelope["schemaVersion"], "worker_task_envelope/v1")
            self.assertEqual(envelope["taskId"], "task_pipeline_design_director_001")

            heartbeat = runtime.heartbeat_task(
                state["runId"],
                envelope["taskId"],
                bridge_id="bridge_user_pc_001",
                heartbeat_token="lease-token-1",
                bridge_status="running",
            )
            self.assertEqual(heartbeat["status"], "accepted")
            self.assertEqual(heartbeat["taskState"], "running")

            accepted = runtime.submit_result(
                state["runId"],
                envelope["taskId"],
                result={
                    "schemaVersion": "agent_output/v1",
                    "status": "completed",
                    "decision": "continue",
                    "modelInvoked": False,
                    "modelUnavailable": False,
                    "schemaValid": True,
                    "summary": "bridge roundtrip fixture completed",
                },
                idempotency_key="bridge-result-1",
                bridge_id="bridge_user_pc_001",
                heartbeat_token="lease-token-1",
            )
            self.assertEqual(accepted["status"], "accepted")
            completed = runtime.get_run(state["runId"])
            self.assertEqual(completed["state"], "completed")
            self.assertFalse(completed["modelInvoked"])
            self.assertEqual(completed["tasks"][0]["state"], "completed")

    def test_bridge_offline_schema_invalid_and_duplicate_submit_have_explicit_states(self) -> None:
        from core.orchestrator.local_live_model_bridge import LocalLiveModelBridgeRuntime

        with temporary_artifact_dir("local_bridge_failure_states") as root:
            runtime = LocalLiveModelBridgeRuntime(root_dir=root, now=_now)
            runtime.register_bridge(
                bridge_id="bridge_user_pc_001",
                capabilities=["codex_cli_model_review"],
                version="local-test",
            )
            state = runtime.create_run(
                request_summary="bridge 离线和 schema invalid 都不能伪造成模型完成。",
                workspace_id="cad-agent-core-lab",
                target_stage="local_bridge_connected",
                agent_ids=["pipeline_design_director"],
            )

            offline = runtime.mark_bridge_offline("bridge_user_pc_001", reason="manual health check failed")
            self.assertEqual(offline["state"], "offline")

            no_lease = runtime.lease_task(
                bridge_id="bridge_user_pc_001",
                capabilities=["codex_cli_model_review"],
                heartbeat_token="lease-token-offline",
                run_id=state["runId"],
            )
            self.assertEqual(no_lease["status"], "bridge_unavailable")
            waiting = runtime.get_run(state["runId"])
            self.assertEqual(waiting["state"], "waiting_for_bridge")
            self.assertFalse(waiting["modelInvoked"])

            runtime.register_bridge(
                bridge_id="bridge_user_pc_001",
                capabilities=["codex_cli_model_review"],
                version="local-test",
            )
            envelope = runtime.lease_task(
                bridge_id="bridge_user_pc_001",
                capabilities=["codex_cli_model_review"],
                heartbeat_token="lease-token-2",
                run_id=state["runId"],
            )
            invalid = runtime.submit_result(
                state["runId"],
                envelope["taskId"],
                result={
                    "schemaVersion": "agent_output/v1",
                    "status": "completed",
                    "decision": "continue",
                    "modelInvoked": True,
                    "modelUnavailable": False,
                    "schemaValid": False,
                    "summary": "invalid JSON shape",
                },
                idempotency_key="invalid-result-1",
                bridge_id="bridge_user_pc_001",
                heartbeat_token="lease-token-2",
            )
            duplicate = runtime.submit_result(
                state["runId"],
                envelope["taskId"],
                result={
                    "schemaVersion": "agent_output/v1",
                    "status": "completed",
                    "decision": "continue",
                    "modelInvoked": True,
                    "modelUnavailable": False,
                    "schemaValid": False,
                    "summary": "duplicate invalid JSON shape",
                },
                idempotency_key="invalid-result-1",
            )

            self.assertEqual(invalid["status"], "accepted")
            self.assertEqual(duplicate["status"], "duplicate")
            blocked = runtime.get_run(state["runId"])
            self.assertEqual(blocked["state"], "blocked")
            self.assertEqual(blocked["tasks"][0]["state"], "blocked")
            self.assertEqual(blocked["tasks"][0]["blockedReason"], "schema_validation_failed")
            self.assertEqual(blocked["circuitBreakers"]["codex_cli_model_review"]["state"], "open")
            self.assertFalse(blocked["cadGeometryVerified"])


if __name__ == "__main__":
    unittest.main()
