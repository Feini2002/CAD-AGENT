from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from core.model_review.codex_cli_client import CodexCliReviewConfig
from core.orchestrator.request_context import build_request_context
from core.orchestrator.run_package_state import create_run_package
from tests.helpers import temporary_artifact_dir


def _state_patch(phase: str) -> dict[str, object]:
    return {
        "phase": phase,
        "phaseLabelForUser": phase,
        "completedEvidence": ["unit-test model output"],
        "pendingEvidence": [],
        "pendingUserAction": "",
        "blockedReason": "",
        "nextSafeAction": "continue",
    }


def _fake_output_for_schema(schema_path: str) -> dict[str, object]:
    name = Path(schema_path).name
    learning_candidate = {
        "decision": "not_required",
        "trigger": "not_required",
        "responsibleAgentIds": [],
        "errorPattern": "",
        "correctPattern": "",
        "promptDelta": "",
        "checkerDelta": "",
        "retestOriginalTask": False,
    }
    common = {
        "decision": "pass",
        "learningCandidate": learning_candidate,
        "statePatch": _state_patch(name),
        "finalResponseAllowedClaims": ["no-CAD model chain output only"],
        "evidenceUsed": ["rule_context_pack", "upstream agent outputs"],
        "evidenceMissing": [],
        "assumptions": [],
        "alternativesConsidered": [],
        "blockingReasons": [],
        "nextRequiredEvidence": [],
        "toolIntent": None,
    }
    if name == "orchestrator_dispatch_review.schema.json":
        return {
            "status": "pass",
            "route": "standard_draw",
            "taskKind": "ordinary_orchestration",
            "userIntentSummary": "设计一个展示茶几的 no-CAD 链路",
            "requiredAgents": ["pipeline_design_director", "pipeline_style_generator", "pipeline_design_reviewer"],
            "dispatchRationale": [],
            "hardGates": ["cad_plan_required", "closeout_gate"],
            "needsUserConfirmation": False,
            "blockedBeforeExecution": False,
            "blockingReasons": [],
            "additionalAgentRequests": [],
            "decision": "pass",
            "statePatch": _state_patch(name),
            "finalResponseAllowedClaims": ["orchestrator reviewed only"],
            "evidenceUsed": ["rule_context_pack"],
            "evidenceMissing": [],
            "assumptions": [],
            "alternativesConsidered": [],
            "nextRequiredEvidence": [],
            "learningCandidate": learning_candidate,
            "toolIntent": None,
        }
    if name == "design_director_review.schema.json":
        return {
            "status": "pass",
            "designStrategy": {"styleCandidatePolicy": "multiple"},
            "drawingTypeDecision": "presentation_preview",
            "expressionPurpose": "compare readable CAD expression options",
            "designIntent": "show a compact tea table symbol with Chinese labels",
            "audienceAndUse": "user review before CAD execution",
            "constraints": ["no CAD write", "CODEX_PREVIEW only after later execution"],
            "requiredChildAgents": ["pipeline_style_generator", "pipeline_design_reviewer"],
            "openQuestions": [],
            "evidenceBoundary": {"notProofOf": ["CAD geometry"]},
            **common,
        }
    if name == "style_generation_review.schema.json":
        return {
            "status": "pass",
            "styleDecision": "multiple",
            "styleCandidates": [{"id": "A"}, {"id": "B"}],
            "selectedStyleCandidate": "A",
            "styleParameterGrammar": {"scale": "model_units"},
            "candidateTradeoffs": [{"id": "A", "tradeoff": "more readable"}],
            "needsUserChoice": False,
            "styleWaiverReason": "",
            "candidateCountPolicy": "explicit_multi_candidate",
            "requestedCandidateCount": 2,
            "candidateLabelPolicy": "abc",
            "creativityPolicy": "contextual_not_forced",
            "semanticRoutingConfidence": "high",
            **common,
        }
    if name == "design_review.schema.json":
        return {
            "status": "pass",
            "designReview": "style candidates are readable enough for intent drafting",
            "professionalDrawingLike": True,
            "readability": True,
            "industryHabitFit": True,
            "scaleAndProportionFit": True,
            "styleCandidateFit": True,
            "contentMatchesDesignPurpose": True,
            "needsUserChoice": False,
            "repairOrRegenerateRecommendation": {},
            **common,
        }
    raise AssertionError(f"unexpected schema path: {schema_path}")


def _valid_cad_plan_candidate() -> dict[str, object]:
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


class ModelAgentChainRuntimeTests(unittest.TestCase):
    def test_no_cad_chain_writes_outputs_and_downstream_prompts_reference_upstream_json(self) -> None:
        from core.orchestrator.model_agent_chain_runtime import run_no_cad_model_agent_chain

        with temporary_artifact_dir("model_agent_chain_runtime") as root:
            context = build_request_context(
                context_id="model-chain-case",
                request_kind="draw",
                user_request="先像专业设计师一样构思一个茶几符号，再给 no-CAD 参数化候选。",
                available_inputs=["cad_plan"],
                allow_cad=False,
            )
            state = create_run_package(
                "model-chain-case",
                user_request={"text": context["user_request"], "requestKind": "draw"},
                context_pack={
                    "schemaVersion": "run-package-context-pack/v1",
                    "runId": "model-chain-case",
                    "requestContext": context,
                },
                root_dir=root,
            )
            run_dir = Path(state["runDir"])

            def fake_runner(
                command: list[str],
                *,
                input: str,
                cwd: Path,
                text: bool,
                encoding: str,
                errors: str,
                capture_output: bool,
                timeout: int,
                check: bool,
            ) -> subprocess.CompletedProcess[str]:
                schema_path = command[command.index("--output-schema") + 1]
                output_path = Path(command[command.index("--output-last-message") + 1])
                output_path.write_text(json.dumps(_fake_output_for_schema(schema_path), ensure_ascii=False), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            result = run_no_cad_model_agent_chain(
                run_dir,
                config=CodexCliReviewConfig(enabled=True, model="gpt-5.5"),
                runner=fake_runner,
                cwd=root,
            )

            self.assertEqual(result["status"], "ready")
            self.assertFalse(result["cadExecutionAuthorized"])
            for agent_id in ("pipeline_design_director", "pipeline_style_generator", "pipeline_design_reviewer"):
                self.assertTrue((run_dir / "agent_outputs" / f"{agent_id}.json").is_file(), agent_id)
                self.assertTrue((run_dir / "agent_outputs" / f"{agent_id}.handoff.json").is_file(), agent_id)

            style_prompt = (
                run_dir
                / "model_traces"
                / "pipeline_style_generator"
                / "pipeline-style-generator"
                / "prompt.md"
            ).read_text(encoding="utf-8")
            review_prompt = (
                run_dir
                / "model_traces"
                / "pipeline_design_reviewer"
                / "pipeline-design-reviewer"
                / "prompt.md"
            ).read_text(encoding="utf-8")
            self.assertIn("agent_outputs/pipeline_design_director.json", style_prompt)
            self.assertIn("agent_outputs/pipeline_design_director.handoff.json", style_prompt)
            self.assertIn("agent_outputs/pipeline_style_generator.json", review_prompt)
            self.assertIn("agent_outputs/pipeline_style_generator.handoff.json", review_prompt)
            self.assertIn("ruleContextPack", style_prompt)
            upstream = result["upstreamOutputs"]
            self.assertTrue(any(item.get("handoffPath") == "agent_outputs/pipeline_design_director.handoff.json" for item in upstream))
            self.assertTrue(any(item.get("handoffSha256") for item in upstream if item.get("agentId") == "pipeline_design_director"))
            self.assertTrue((run_dir / "agent_outputs" / "pipeline_intent.json").is_file())
            self.assertTrue((run_dir / "agent_outputs" / "pipeline_audit.json").is_file())
            self.assertTrue((run_dir / "agent_outputs" / "pipeline_delivery.chain.json").is_file())

    def test_model_unavailable_output_gets_learning_candidate_sidecar(self) -> None:
        from core.orchestrator.model_agent_chain_runtime import run_no_cad_model_agent_chain

        with temporary_artifact_dir("model_agent_chain_learning") as root:
            context = build_request_context(
                context_id="model-chain-learning-case",
                request_kind="draw",
                user_request="设计一个茶几符号，生成两个候选。",
                available_inputs=["cad_plan"],
                allow_cad=False,
            )
            state = create_run_package(
                "model-chain-learning-case",
                user_request={"text": context["user_request"], "requestKind": "draw"},
                context_pack={
                    "schemaVersion": "run-package-context-pack/v1",
                    "runId": "model-chain-learning-case",
                    "requestContext": context,
                },
                root_dir=root,
            )
            run_dir = Path(state["runDir"])

            def fake_runner(
                command: list[str],
                *,
                input: str,
                cwd: Path,
                text: bool,
                encoding: str,
                errors: str,
                capture_output: bool,
                timeout: int,
                check: bool,
            ) -> subprocess.CompletedProcess[str]:
                schema_path = command[command.index("--output-schema") + 1]
                if schema_path.endswith("style_generation_review.schema.json"):
                    return subprocess.CompletedProcess(command, 1, stdout="", stderr="模型服务不可用")
                output_path = Path(command[command.index("--output-last-message") + 1])
                output_path.write_text(json.dumps(_fake_output_for_schema(schema_path), ensure_ascii=False), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            result = run_no_cad_model_agent_chain(
                run_dir,
                config=CodexCliReviewConfig(enabled=True, model="gpt-5.5"),
                runner=fake_runner,
                cwd=root,
            )

            self.assertEqual(result["status"], "blocked")
            style_output = json.loads(
                (run_dir / "agent_outputs" / "pipeline_style_generator.json").read_text(encoding="utf-8")
            )
            self.assertEqual(style_output["learningCandidate"]["decision"], "review_required")
            self.assertIn("model_fail_or_schema_invalid", style_output["learningCandidate"]["trigger"])

    def test_chain_executes_read_only_tool_intent_and_passes_trace_downstream(self) -> None:
        from core.orchestrator.model_agent_chain_runtime import run_no_cad_model_agent_chain

        with temporary_artifact_dir("model_agent_chain_tool_intent") as root:
            context = build_request_context(
                context_id="model-chain-tool-intent",
                request_kind="draw",
                user_request="先做 no-CAD 设计链路，并读取 run package 上下文。",
                available_inputs=["cad_plan"],
                allow_cad=False,
            )
            state = create_run_package(
                "model-chain-tool-intent",
                user_request={"text": context["user_request"], "requestKind": "draw"},
                context_pack={
                    "schemaVersion": "run-package-context-pack/v1",
                    "runId": "model-chain-tool-intent",
                    "requestContext": context,
                },
                root_dir=root,
            )
            run_dir = Path(state["runDir"])

            def fake_runner(
                command: list[str],
                *,
                input: str,
                cwd: Path,
                text: bool,
                encoding: str,
                errors: str,
                capture_output: bool,
                timeout: int,
                check: bool,
            ) -> subprocess.CompletedProcess[str]:
                schema_path = command[command.index("--output-schema") + 1]
                output_path = Path(command[command.index("--output-last-message") + 1])
                payload = _fake_output_for_schema(schema_path)
                if schema_path.endswith("design_director_review.schema.json"):
                    payload["toolIntent"] = {
                        "schemaVersion": "tool-intent/v1",
                        "toolIntentId": "intent-read-run-package",
                        "requestedByAgentId": "pipeline_design_director",
                        "toolName": "read_run_package",
                        "purpose": "read run package context",
                        "inputs": {"runId": "model-chain-tool-intent"},
                        "targetScope": {
                            "scopeType": "run_package",
                            "scopeRef": "output/runs/model-chain-tool-intent",
                        },
                        "riskLevel": "low",
                        "permissionClass": "read_only",
                        "expectedEvidence": ["run package context"],
                        "forbiddenEffects": ["cad_write", "dwg_save", "delete_entities"],
                    }
                output_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            result = run_no_cad_model_agent_chain(
                run_dir,
                config=CodexCliReviewConfig(enabled=True, model="gpt-5.5"),
                runner=fake_runner,
                cwd=root,
            )

            trace_path = run_dir / "tool_traces" / "pipeline_design_director.intent-read-run-package.json"
            self.assertEqual(result["status"], "ready")
            self.assertTrue(trace_path.is_file())
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
            self.assertEqual(trace["orchestratorDecision"], "allowed")
            self.assertEqual(trace["executionStatus"], "executed")
            self.assertEqual(trace["result"]["toolStage"], "stage1_read_only")
            style_prompt = (
                run_dir
                / "model_traces"
                / "pipeline_style_generator"
                / "pipeline-style-generator"
                / "prompt.md"
            ).read_text(encoding="utf-8")
            self.assertIn("tool_traces/pipeline_design_director.intent-read-run-package.json", style_prompt)

    def test_chain_executes_safe_generation_tool_intent_only_in_candidate_zone(self) -> None:
        from core.orchestrator.model_agent_chain_runtime import run_no_cad_model_agent_chain

        with temporary_artifact_dir("model_agent_chain_safe_generation") as root:
            context = build_request_context(
                context_id="model-chain-safe-generation",
                request_kind="draw",
                user_request="做 no-CAD 设计链路，并生成候选 intent。",
                available_inputs=["cad_plan"],
                allow_cad=False,
            )
            state = create_run_package(
                "model-chain-safe-generation",
                user_request={"text": context["user_request"], "requestKind": "draw"},
                context_pack={
                    "schemaVersion": "run-package-context-pack/v1",
                    "runId": "model-chain-safe-generation",
                    "requestContext": context,
                },
                root_dir=root,
            )
            run_dir = Path(state["runDir"])

            def fake_runner(
                command: list[str],
                *,
                input: str,
                cwd: Path,
                text: bool,
                encoding: str,
                errors: str,
                capture_output: bool,
                timeout: int,
                check: bool,
            ) -> subprocess.CompletedProcess[str]:
                schema_path = command[command.index("--output-schema") + 1]
                output_path = Path(command[command.index("--output-last-message") + 1])
                payload = _fake_output_for_schema(schema_path)
                if schema_path.endswith("style_generation_review.schema.json"):
                    payload["toolIntent"] = {
                        "schemaVersion": "tool-intent/v1",
                        "toolIntentId": "intent-write-draft-intent",
                        "requestedByAgentId": "pipeline_style_generator",
                        "toolName": "write_draft_intent_candidate",
                        "purpose": "write candidate intent for downstream review",
                        "inputs": {
                            "payload": {
                                "schemaVersion": "candidate-intent/v1",
                                "status": "candidate",
                                "cadExecutionAuthorized": False,
                            }
                        },
                        "targetScope": {
                            "scopeType": "run_candidate",
                            "targetPath": "candidate_outputs/pipeline_intent.draft.json",
                        },
                        "riskLevel": "low",
                        "permissionClass": "safe_generate",
                        "expectedEvidence": ["candidate intent json"],
                        "forbiddenEffects": ["cad_write", "dwg_save", "registry_mutation", "training_source_mutation"],
                    }
                output_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            result = run_no_cad_model_agent_chain(
                run_dir,
                config=CodexCliReviewConfig(enabled=True, model="gpt-5.5"),
                runner=fake_runner,
                cwd=root,
            )

            candidate_path = run_dir / "candidate_outputs" / "pipeline_intent.draft.json"
            trace_path = run_dir / "tool_traces" / "pipeline_style_generator.intent-write-draft-intent.json"
            self.assertEqual(result["status"], "ready")
            self.assertTrue(candidate_path.is_file())
            self.assertFalse((run_dir / "agent_outputs" / "pipeline_intent.draft.json").exists())
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
            self.assertEqual(trace["executionStatus"], "executed")
            self.assertEqual(trace["result"]["toolStage"], "stage2_safe_generation")

    def test_chain_executes_deterministic_validate_plan_and_feeds_report_downstream(self) -> None:
        from core.orchestrator.model_agent_chain_runtime import run_no_cad_model_agent_chain

        with temporary_artifact_dir("model_agent_chain_stage3_validate") as root:
            context = build_request_context(
                context_id="model-chain-stage3-validate",
                request_kind="draw",
                user_request="生成 no-CAD 茶几 CAD_PLAN candidate，并请求确定性 validate_plan。",
                available_inputs=["cad_plan"],
                allow_cad=False,
            )
            state = create_run_package(
                "model-chain-stage3-validate",
                user_request={"text": context["user_request"], "requestKind": "draw"},
                context_pack={
                    "schemaVersion": "run-package-context-pack/v1",
                    "runId": "model-chain-stage3-validate",
                    "requestContext": context,
                },
                root_dir=root,
            )
            run_dir = Path(state["runDir"])

            def fake_runner(
                command: list[str],
                *,
                input: str,
                cwd: Path,
                text: bool,
                encoding: str,
                errors: str,
                capture_output: bool,
                timeout: int,
                check: bool,
            ) -> subprocess.CompletedProcess[str]:
                schema_path = command[command.index("--output-schema") + 1]
                output_path = Path(command[command.index("--output-last-message") + 1])
                payload = _fake_output_for_schema(schema_path)
                if schema_path.endswith("style_generation_review.schema.json"):
                    payload["toolIntent"] = {
                        "schemaVersion": "tool-intent/v1",
                        "toolIntentId": "intent-write-cad-plan-candidate",
                        "requestedByAgentId": "pipeline_style_generator",
                        "toolName": "write_cad_plan_candidate",
                        "purpose": "write candidate CAD_PLAN for deterministic validation",
                        "inputs": {"payload": _valid_cad_plan_candidate()},
                        "targetScope": {
                            "scopeType": "run_candidate",
                            "targetPath": "candidate_outputs/cad_plan.candidate.json",
                        },
                        "riskLevel": "low",
                        "permissionClass": "safe_generate",
                        "expectedEvidence": ["candidate CAD_PLAN"],
                        "forbiddenEffects": ["cad_write", "dwg_save", "delete_entities"],
                    }
                if schema_path.endswith("design_review.schema.json"):
                    payload["toolIntent"] = {
                        "schemaVersion": "tool-intent/v1",
                        "toolIntentId": "intent-validate-cad-plan",
                        "requestedByAgentId": "pipeline_design_reviewer",
                        "toolName": "validate_plan",
                        "purpose": "request deterministic validation of candidate CAD_PLAN",
                        "inputs": {"planPath": "candidate_outputs/cad_plan.candidate.json"},
                        "targetScope": {
                            "scopeType": "run_artifact",
                            "targetPath": "candidate_outputs/cad_plan.candidate.json",
                        },
                        "riskLevel": "low",
                        "permissionClass": "deterministic_verify",
                        "expectedEvidence": ["cad_reports/validation_report.json"],
                        "forbiddenEffects": ["cad_write", "dwg_save", "delete_entities"],
                    }
                output_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            result = run_no_cad_model_agent_chain(
                run_dir,
                config=CodexCliReviewConfig(enabled=True, model="gpt-5.5"),
                runner=fake_runner,
                cwd=root,
            )

            trace_path = run_dir / "tool_traces" / "pipeline_design_reviewer.intent-validate-cad-plan.json"
            report_path = run_dir / "cad_reports" / "validation_report.json"
            audit_output = json.loads((run_dir / "agent_outputs" / "pipeline_audit.json").read_text(encoding="utf-8"))

            self.assertEqual(result["status"], "ready")
            self.assertTrue(report_path.is_file())
            trace = json.loads(trace_path.read_text(encoding="utf-8"))
            self.assertEqual(trace["executionStatus"], "executed")
            self.assertEqual(trace["result"]["toolStage"], "stage3_deterministic_verify")
            self.assertEqual(trace["result"]["reportPath"], "cad_reports/validation_report.json")
            upstream = audit_output["evidenceBundle"]["upstreamOutputs"]
            self.assertTrue(any(item.get("reportPath") == "cad_reports/validation_report.json" for item in upstream))

    def test_provider_unavailable_does_not_fabricate_tool_trace_or_candidate_output(self) -> None:
        from core.orchestrator.model_agent_chain_runtime import run_no_cad_model_agent_chain

        with temporary_artifact_dir("model_agent_chain_unavailable_no_tool") as root:
            context = build_request_context(
                context_id="model-chain-unavailable-no-tool",
                request_kind="draw",
                user_request="设计一个茶几符号，生成两个候选。",
                available_inputs=["cad_plan"],
                allow_cad=False,
            )
            state = create_run_package(
                "model-chain-unavailable-no-tool",
                user_request={"text": context["user_request"], "requestKind": "draw"},
                context_pack={
                    "schemaVersion": "run-package-context-pack/v1",
                    "runId": "model-chain-unavailable-no-tool",
                    "requestContext": context,
                },
                root_dir=root,
            )
            run_dir = Path(state["runDir"])

            def fake_runner(
                command: list[str],
                *,
                input: str,
                cwd: Path,
                text: bool,
                encoding: str,
                errors: str,
                capture_output: bool,
                timeout: int,
                check: bool,
            ) -> subprocess.CompletedProcess[str]:
                return subprocess.CompletedProcess(command, 1, stdout="", stderr="模型服务不可用")

            result = run_no_cad_model_agent_chain(
                run_dir,
                config=CodexCliReviewConfig(enabled=True, model="gpt-5.5"),
                runner=fake_runner,
                cwd=root,
            )

            self.assertEqual(result["status"], "blocked")
            self.assertFalse((run_dir / "tool_traces").exists())
            self.assertFalse((run_dir / "candidate_outputs").exists())

    def test_live_collab_proof_writes_downstream_outputs_and_fake_cad_stays_not_verified(self) -> None:
        from core.orchestrator.model_agent_chain_runtime import run_model_agent_live_collab_proof

        with temporary_artifact_dir("model_agent_live_collab_proof") as root:
            context = build_request_context(
                context_id="model-agent-live-collab-proof",
                request_kind="draw",
                user_request="让模型型 Agent 协作设计一个茶几符号，并做 preview-only CAD 校验。",
                available_inputs=["cad_plan"],
                allow_cad=False,
            )
            state = create_run_package(
                "model-agent-live-collab-proof",
                user_request={"text": context["user_request"], "requestKind": "draw"},
                context_pack={
                    "schemaVersion": "run-package-context-pack/v1",
                    "runId": "model-agent-live-collab-proof",
                    "requestContext": context,
                },
                root_dir=root,
            )
            run_dir = Path(state["runDir"])

            def fake_runner(
                command: list[str],
                *,
                input: str,
                cwd: Path,
                text: bool,
                encoding: str,
                errors: str,
                capture_output: bool,
                timeout: int,
                check: bool,
            ) -> subprocess.CompletedProcess[str]:
                schema_path = command[command.index("--output-schema") + 1]
                output_path = Path(command[command.index("--output-last-message") + 1])
                output_path.write_text(json.dumps(_fake_output_for_schema(schema_path), ensure_ascii=False), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            result = run_model_agent_live_collab_proof(
                run_dir,
                config=CodexCliReviewConfig(enabled=True, model="gpt-5.5"),
                runner=fake_runner,
                cwd=root,
                driver_mode="fake_driver_preflight",
            )

            self.assertEqual(result["status"], "not_verified")
            self.assertEqual(result["cadProof"]["driverMode"], "fake_driver_preflight")
            self.assertFalse(result["cadProof"]["cadGeometryVerified"])
            for rel_path in (
                "agent_outputs/pipeline_design_director.json",
                "agent_outputs/pipeline_style_generator.json",
                "agent_outputs/pipeline_visual_intent.json",
                "agent_outputs/pipeline_intent.json",
                "agent_outputs/pipeline_audit.json",
                "agent_outputs/pipeline_delivery.json",
                "candidate_outputs/cad_plan.candidate.json",
                "cad_reports/validation_report.json",
                "cad_reports/dry_run_report.json",
                "cad_reports/cad_preview_tool_report.json",
                "cad_reports/readback_summary.json",
                "closeout_decision.json",
                "model_agent_live_collab_completion_audit.json",
            ):
                self.assertTrue((run_dir / rel_path).is_file(), rel_path)

            visual_intent = json.loads((run_dir / "agent_outputs" / "pipeline_visual_intent.json").read_text(encoding="utf-8"))
            self.assertIn("agent_outputs/pipeline_design_director.json", visual_intent["sourceAgentOutputs"])
            self.assertIn("agent_outputs/pipeline_style_generator.json", visual_intent["sourceAgentOutputs"])

            audit = json.loads((run_dir / "agent_outputs" / "pipeline_audit.json").read_text(encoding="utf-8"))
            self.assertTrue(
                any(
                    item.get("path") == "tool_traces/pipeline_intent.intent-preview-cad-execute.json"
                    for item in audit["evidenceBundle"]["upstreamOutputs"]
                )
            )
            self.assertIn("created_handles_readback not ok", result["closeoutEvidence"]["blockingReasons"])
            completion_audit = json.loads(
                (run_dir / "model_agent_live_collab_completion_audit.json").read_text(encoding="utf-8")
            )
            self.assertEqual(completion_audit["status"], "not_complete")
            self.assertEqual(completion_audit["requirements"]["realCadPreviewValidation"]["status"], "blocked")
            self.assertEqual(completion_audit["requirements"]["liveModelAgentInvocation"]["status"], "achieved")

    def test_live_collab_proof_can_run_cad_preflight_when_model_chain_is_blocked_if_explicitly_allowed(self) -> None:
        from core.orchestrator.model_agent_chain_runtime import run_model_agent_live_collab_proof

        with temporary_artifact_dir("model_agent_live_collab_blocked_cad_preflight") as root:
            context = build_request_context(
                context_id="model-agent-live-collab-blocked-cad",
                request_kind="draw",
                user_request="模型桥不可用时，也只验证受控 CAD preview 工具。",
                available_inputs=["cad_plan"],
                allow_cad=False,
            )
            state = create_run_package(
                "model-agent-live-collab-blocked-cad",
                user_request={"text": context["user_request"], "requestKind": "draw"},
                context_pack={
                    "schemaVersion": "run-package-context-pack/v1",
                    "runId": "model-agent-live-collab-blocked-cad",
                    "requestContext": context,
                },
                root_dir=root,
            )
            run_dir = Path(state["runDir"])

            def unavailable_runner(
                command: list[str],
                *,
                input: str,
                cwd: Path,
                text: bool,
                encoding: str,
                errors: str,
                capture_output: bool,
                timeout: int,
                check: bool,
            ) -> subprocess.CompletedProcess[str]:
                return subprocess.CompletedProcess(command, 1, stdout="", stderr="模型服务不可用")

            result = run_model_agent_live_collab_proof(
                run_dir,
                config=CodexCliReviewConfig(enabled=True, model="gpt-5.5"),
                runner=unavailable_runner,
                cwd=root,
                driver_mode="fake_driver_preflight",
                continue_cad_on_model_blocked=True,
            )

            self.assertEqual(result["modelChainStatus"], "blocked")
            self.assertEqual(result["conflictHandling"]["status"], "fail")
            self.assertEqual(result["cadContinuationPolicy"]["mode"], "explicit_continue_after_model_block")
            self.assertGreater(result["cadProof"]["createdHandleCount"], 0)
            self.assertFalse(result["cadProof"]["cadGeometryVerified"])
            self.assertTrue((run_dir / "cad_reports" / "validation_report.json").is_file())
            self.assertTrue((run_dir / "cad_reports" / "dry_run_report.json").is_file())
            self.assertTrue((run_dir / "cad_reports" / "cad_preview_tool_report.json").is_file())


if __name__ == "__main__":
    unittest.main()
