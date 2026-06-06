from __future__ import annotations

import json
import unittest

from tests.bootstrap import PROJECT_ROOT
from tests.helpers import temporary_artifact_dir

from core.schemas.validator import validate_value


def _base_intent() -> dict[str, object]:
    return {
        "schemaVersion": "tool-intent/v1",
        "toolIntentId": "intent-read-1",
        "requestedByAgentId": "pipeline_design_reviewer",
        "toolName": "read_run_package",
        "purpose": "read run package context for downstream review",
        "inputs": {"runId": "run-1"},
        "targetScope": {"scopeType": "run_package", "scopeRef": "output/runs/run-1"},
        "riskLevel": "low",
        "permissionClass": "read_only",
        "expectedEvidence": ["run package summary"],
        "forbiddenEffects": ["cad_write", "dwg_save", "delete_entities"],
    }


def _valid_cad_plan(*, layer: str = "CODEX_PREVIEW") -> dict[str, object]:
    return {
        "version": "0.1",
        "domain": "generic",
        "intent": "draw_object",
        "object": {"type": "table", "name": "茶几", "width": 1200, "depth": 600},
        "placement": {"mode": "absolute", "base_point": [0, 0, 0]},
        "drawing": {"layer": layer, "include_label": True, "include_dimensions": True},
        "confidence": 0.9,
        "needs_confirmation": False,
    }


def _verification_intent(tool_name: str, *, target_path: str = "candidate_outputs/cad_plan.candidate.json") -> dict[str, object]:
    intent = _base_intent()
    intent.update(
        {
            "toolIntentId": f"intent-{tool_name}",
            "toolName": tool_name,
            "purpose": f"run deterministic {tool_name} gate",
            "inputs": {"planPath": target_path},
            "targetScope": {"scopeType": "run_artifact", "targetPath": target_path},
            "riskLevel": "low",
            "permissionClass": "deterministic_verify",
            "expectedEvidence": ["deterministic verification report"],
            "forbiddenEffects": ["cad_write", "dwg_save", "delete_entities", "registry_mutation", "training_source_mutation"],
        }
    )
    return intent


def _cad_preview_intent(*, driver_mode: str = "fake_driver_preflight") -> dict[str, object]:
    intent = _base_intent()
    intent.update(
        {
            "toolIntentId": "intent-preview-cad-execute",
            "toolName": "preview_cad_execute",
            "purpose": "execute a validated CAD_PLAN through the controlled preview CAD executor",
            "inputs": {
                "planPath": "candidate_outputs/cad_plan.candidate.json",
                "driverMode": driver_mode,
            },
            "targetScope": {
                "scopeType": "run_artifact",
                "targetPath": "candidate_outputs/cad_plan.candidate.json",
                "targetLayer": "CODEX_PREVIEW",
                "previewOnly": True,
                "savedCurrentDwg": False,
            },
            "riskLevel": "high",
            "permissionClass": "cad_preview",
            "expectedEvidence": [
                "execution summary",
                "created handles",
                "readback summary",
                "savedCurrentDwg=false",
            ],
            "requestedEffects": ["cad_preview_write"],
            "forbiddenEffects": ["dwg_save", "delete_entities", "cad_write_formal_layer"],
        }
    )
    return intent


class ToolContractReactTests(unittest.TestCase):
    def test_tool_intent_and_trace_schemas_are_registered_and_validatable(self) -> None:
        from core.schemas.registry import MODEL_SCHEMAS, infer_model_type

        self.assertEqual(MODEL_SCHEMAS["tool_intent"], "tool_intent.schema.json")
        self.assertEqual(MODEL_SCHEMAS["tool_trace"], "tool_trace.schema.json")
        self.assertEqual(infer_model_type(_base_intent()), "tool_intent")

        intent_schema = json.loads((PROJECT_ROOT / "core/schemas/tool_intent.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(validate_value(_base_intent(), intent_schema), [])

    def test_model_agent_schemas_allow_nullable_tool_intent_for_no_tool_request(self) -> None:
        schema_root = PROJECT_ROOT / "core/model_review/schemas"
        for schema_path in schema_root.glob("*.schema.json"):
            with self.subTest(schema=schema_path.name):
                schema = json.loads(schema_path.read_text(encoding="utf-8"))
                self.assertIn("toolIntent", schema["properties"])
                self.assertIn("toolIntent", schema.get("required", []))
                tool_intent_schema = schema["properties"]["toolIntent"]
                self.assertIn({"type": "null"}, tool_intent_schema.get("anyOf", []))

    def test_read_only_tool_intent_is_allowed_but_not_executed_by_model(self) -> None:
        from core.orchestrator.tool_contract import build_tool_trace, evaluate_tool_intent

        decision = evaluate_tool_intent(_base_intent())

        self.assertEqual(decision["orchestratorDecision"], "allowed")
        self.assertIn("orchestrator-owned allowlisted execution", " ".join(decision["evidenceBoundary"]))

        trace = build_tool_trace(_base_intent(), run_id="run-1")
        trace_schema = json.loads((PROJECT_ROOT / "core/schemas/tool_trace.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(trace["executionStatus"], "allowed_not_executed")
        self.assertEqual(trace["resultStatus"], "not_verified")
        self.assertEqual(validate_value(trace, trace_schema), [])

    def test_high_risk_tool_missing_target_scope_is_blocked(self) -> None:
        from core.orchestrator.tool_contract import evaluate_tool_intent

        intent = _base_intent()
        intent.update(
            {
                "toolIntentId": "intent-high-risk-no-scope",
                "toolName": "preview_cad_write",
                "riskLevel": "high",
                "permissionClass": "cad_preview",
                "targetScope": {"scopeType": "unspecified"},
            }
        )

        decision = evaluate_tool_intent(intent)

        self.assertEqual(decision["orchestratorDecision"], "blocked")
        self.assertIn("high-risk tool intent missing precise targetScope", decision["blockingReasons"])

    def test_model_direct_save_delete_or_formal_layer_request_is_blocked(self) -> None:
        from core.orchestrator.tool_contract import evaluate_tool_intent

        for tool_name, effect in [
            ("save_current_dwg", "dwg_save"),
            ("delete_entities", "delete_entities"),
            ("modify_formal_layer", "modify_formal_layer"),
        ]:
            with self.subTest(tool_name=tool_name):
                intent = _base_intent()
                intent.update(
                    {
                        "toolIntentId": f"intent-{tool_name}",
                        "toolName": tool_name,
                        "riskLevel": "critical",
                        "permissionClass": "save_current_dwg" if tool_name.startswith("save") else "delete_or_replace",
                        "targetScope": {"scopeType": "current_dwg", "scopeRef": "active_document"},
                        "requestedEffects": [effect],
                    }
                )

                decision = evaluate_tool_intent(intent)

                self.assertEqual(decision["orchestratorDecision"], "blocked")
                self.assertTrue(any(effect in reason for reason in decision["blockingReasons"]))

    def test_write_tool_trace_creates_downstream_artifact_without_running_tool(self) -> None:
        from core.orchestrator.tool_contract import write_tool_trace

        with temporary_artifact_dir("tool_contract_react") as root:
            trace = write_tool_trace(root, _base_intent(), run_id="run-1")
            trace_path = root / trace["downstreamArtifactPath"]

            self.assertTrue(trace_path.is_file())
            written = json.loads(trace_path.read_text(encoding="utf-8"))
            self.assertEqual(written["orchestratorDecision"], "allowed")
            self.assertEqual(written["executionStatus"], "allowed_not_executed")

    def test_run_tool_intent_executes_read_only_reader_inside_run_dir(self) -> None:
        from core.orchestrator.tool_contract import run_tool_intent

        with temporary_artifact_dir("tool_contract_read_only") as root:
            (root / "user_request.json").write_text(
                json.dumps({"userRequest": {"text": "读取 run package"}}, ensure_ascii=False),
                encoding="utf-8",
            )

            trace = run_tool_intent(root, _base_intent(), run_id="run-1")

            self.assertEqual(trace["orchestratorDecision"], "allowed")
            self.assertEqual(trace["executionStatus"], "executed")
            self.assertEqual(trace["result"]["status"], "pass")
            self.assertEqual(trace["result"]["toolStage"], "stage1_read_only")
            self.assertTrue((root / trace["downstreamArtifactPath"]).is_file())

    def test_safe_generation_tool_writes_only_candidate_outputs(self) -> None:
        from core.orchestrator.tool_contract import run_tool_intent

        intent = _base_intent()
        intent.update(
            {
                "toolIntentId": "intent-candidate-output",
                "toolName": "write_agent_output_candidate",
                "permissionClass": "safe_generate",
                "targetScope": {
                    "scopeType": "run_candidate",
                    "targetPath": "candidate_outputs/agent_outputs/pipeline_design_reviewer.json",
                },
                "inputs": {
                    "agentId": "pipeline_design_reviewer",
                    "payload": {
                        "schemaVersion": "candidate-agent-output/v1",
                        "status": "candidate",
                        "evidenceBoundary": ["candidate only"],
                    },
                },
            }
        )

        with temporary_artifact_dir("tool_contract_safe_generate") as root:
            trace = run_tool_intent(root, intent, run_id="run-1")
            candidate_path = root / "candidate_outputs" / "agent_outputs" / "pipeline_design_reviewer.json"

            self.assertEqual(trace["orchestratorDecision"], "allowed")
            self.assertEqual(trace["executionStatus"], "executed")
            self.assertTrue(candidate_path.is_file())
            self.assertFalse((root / "agent_outputs" / "pipeline_design_reviewer.json").exists())
            self.assertIn("candidate_outputs", trace["result"]["writtenPath"])

    def test_safe_generation_tool_blocks_non_candidate_target(self) -> None:
        from core.orchestrator.tool_contract import evaluate_tool_intent

        intent = _base_intent()
        intent.update(
            {
                "toolIntentId": "intent-bad-candidate-output",
                "toolName": "write_agent_output_candidate",
                "permissionClass": "safe_generate",
                "targetScope": {
                    "scopeType": "run_candidate",
                    "targetPath": "agent_outputs/pipeline_delivery.json",
                },
                "inputs": {"payload": {"status": "candidate"}},
            }
        )

        decision = evaluate_tool_intent(intent)

        self.assertEqual(decision["orchestratorDecision"], "blocked")
        self.assertIn("safe generation targetPath must stay under candidate_outputs/", decision["blockingReasons"])

    def test_deterministic_validate_plan_tool_writes_closeout_readable_report(self) -> None:
        from core.orchestrator.tool_contract import run_tool_intent

        with temporary_artifact_dir("tool_contract_validate_plan") as root:
            plan_path = root / "candidate_outputs" / "cad_plan.candidate.json"
            plan_path.parent.mkdir(parents=True, exist_ok=True)
            plan_path.write_text(json.dumps(_valid_cad_plan(), ensure_ascii=False), encoding="utf-8")

            trace = run_tool_intent(root, _verification_intent("validate_plan"), run_id="run-1")
            report = json.loads((root / "cad_reports" / "validation_report.json").read_text(encoding="utf-8"))

            self.assertEqual(trace["orchestratorDecision"], "allowed")
            self.assertEqual(trace["executionStatus"], "executed")
            self.assertEqual(trace["result"]["toolStage"], "stage3_deterministic_verify")
            self.assertEqual(trace["result"]["reportPath"], "cad_reports/validation_report.json")
            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["validationErrors"], [])

    def test_deterministic_validate_plan_blocks_invalid_plan(self) -> None:
        from core.orchestrator.tool_contract import run_tool_intent

        with temporary_artifact_dir("tool_contract_validate_plan_invalid") as root:
            plan_path = root / "candidate_outputs" / "cad_plan.candidate.json"
            plan_path.parent.mkdir(parents=True, exist_ok=True)
            plan_path.write_text(json.dumps({"version": "0.1"}, ensure_ascii=False), encoding="utf-8")

            trace = run_tool_intent(root, _verification_intent("validate_plan"), run_id="run-1")
            report = json.loads((root / "cad_reports" / "validation_report.json").read_text(encoding="utf-8"))

            self.assertEqual(trace["orchestratorDecision"], "blocked")
            self.assertEqual(trace["executionStatus"], "failed")
            self.assertEqual(trace["result"]["status"], "fail")
            self.assertTrue(report["validationErrors"])
            self.assertIn("Missing top-level field", trace["downstreamReadableSummary"])

    def test_deterministic_dry_run_tool_normalizes_valid_to_pass_for_closeout(self) -> None:
        from core.orchestrator.tool_contract import run_tool_intent

        with temporary_artifact_dir("tool_contract_dry_run") as root:
            plan_path = root / "candidate_outputs" / "cad_plan.candidate.json"
            plan_path.parent.mkdir(parents=True, exist_ok=True)
            plan_path.write_text(json.dumps(_valid_cad_plan(), ensure_ascii=False), encoding="utf-8")

            trace = run_tool_intent(root, _verification_intent("dry_run_plan"), run_id="run-1")
            report = json.loads((root / "cad_reports" / "dry_run_report.json").read_text(encoding="utf-8"))

            self.assertEqual(trace["executionStatus"], "executed")
            self.assertEqual(trace["result"]["status"], "pass")
            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["dryRunStatus"], "valid")
            self.assertGreater(report["entityCount"], 0)

    def test_controlled_cad_preview_requires_stage3_reports_before_execution(self) -> None:
        from core.orchestrator.tool_contract import run_tool_intent

        with temporary_artifact_dir("tool_contract_cad_preview_missing_stage3") as root:
            plan_path = root / "candidate_outputs" / "cad_plan.candidate.json"
            plan_path.parent.mkdir(parents=True, exist_ok=True)
            plan_path.write_text(json.dumps(_valid_cad_plan(), ensure_ascii=False), encoding="utf-8")

            trace = run_tool_intent(root, _cad_preview_intent(), run_id="run-1")
            report = json.loads((root / "cad_reports" / "cad_preview_tool_report.json").read_text(encoding="utf-8"))

            self.assertEqual(trace["orchestratorDecision"], "blocked")
            self.assertEqual(trace["executionStatus"], "failed")
            self.assertEqual(trace["result"]["status"], "fail")
            self.assertEqual(report["status"], "not_verified")
            self.assertIn("validate_plan report missing", trace["downstreamReadableSummary"])
            self.assertFalse((root / "cad_reports" / "execution_summary.json").exists())

    def test_controlled_cad_preview_fake_preflight_writes_evidence_without_claiming_real_cad(self) -> None:
        from core.orchestrator.tool_contract import run_tool_intent

        with temporary_artifact_dir("tool_contract_cad_preview_fake") as root:
            plan_path = root / "candidate_outputs" / "cad_plan.candidate.json"
            plan_path.parent.mkdir(parents=True, exist_ok=True)
            plan_path.write_text(json.dumps(_valid_cad_plan(), ensure_ascii=False), encoding="utf-8")

            run_tool_intent(root, _verification_intent("validate_plan"), run_id="run-1")
            run_tool_intent(root, _verification_intent("dry_run_plan"), run_id="run-1")
            trace = run_tool_intent(root, _cad_preview_intent(), run_id="run-1")

            report = json.loads((root / "cad_reports" / "cad_preview_tool_report.json").read_text(encoding="utf-8"))
            execution_summary = json.loads((root / "cad_reports" / "execution_summary.json").read_text(encoding="utf-8"))
            readback_summary = json.loads((root / "cad_reports" / "readback_summary.json").read_text(encoding="utf-8"))

            self.assertEqual(trace["orchestratorDecision"], "allowed")
            self.assertEqual(trace["executionStatus"], "executed")
            self.assertEqual(trace["result"]["toolStage"], "stage4_controlled_cad")
            self.assertEqual(trace["resultStatus"], "not_verified")
            self.assertEqual(trace["result"]["driverMode"], "fake_driver_preflight")
            self.assertEqual(trace["result"]["targetLayer"], "CODEX_PREVIEW")
            self.assertFalse(trace["result"]["savedCurrentDwg"])
            self.assertFalse(trace["result"]["cadGeometryVerified"])
            self.assertGreater(trace["result"]["createdHandleCount"], 0)
            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["resultStatus"], "not_verified")
            self.assertFalse(execution_summary["savedCurrentDwg"])
            self.assertEqual(readback_summary["readbackStatus"], "not_verified")
            self.assertEqual(readback_summary["rawReadbackStatus"], "ok")
            self.assertGreater(readback_summary["readbackEntityCount"], 0)
            self.assertIsNotNone(readback_summary["bbox"])

    def test_controlled_cad_preview_blocks_formal_layer_even_with_passed_stage3_reports(self) -> None:
        from core.orchestrator.tool_contract import run_tool_intent

        with temporary_artifact_dir("tool_contract_cad_preview_formal_layer") as root:
            plan_path = root / "candidate_outputs" / "cad_plan.candidate.json"
            plan_path.parent.mkdir(parents=True, exist_ok=True)
            plan_path.write_text(json.dumps(_valid_cad_plan(layer="FORMAL"), ensure_ascii=False), encoding="utf-8")
            report_dir = root / "cad_reports"
            report_dir.mkdir(parents=True, exist_ok=True)
            for name in ("validation_report.json", "dry_run_report.json"):
                (report_dir / name).write_text(
                    json.dumps(
                        {
                            "status": "pass",
                            "planPath": "candidate_outputs/cad_plan.candidate.json",
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )

            trace = run_tool_intent(root, _cad_preview_intent(), run_id="run-1")
            report = json.loads((root / "cad_reports" / "cad_preview_tool_report.json").read_text(encoding="utf-8"))

            self.assertEqual(trace["orchestratorDecision"], "blocked")
            self.assertEqual(trace["executionStatus"], "failed")
            self.assertEqual(report["status"], "not_verified")
            self.assertFalse(report["savedCurrentDwg"])
            self.assertTrue("formal layer" in report["reason"] or "CODEX_PREVIEW" in report["reason"])

    def test_preview_only_audit_tool_blocks_unsafe_execution_summary(self) -> None:
        from core.orchestrator.tool_contract import run_tool_intent

        intent = _base_intent()
        intent.update(
            {
                "toolIntentId": "intent-preview-only-audit",
                "toolName": "preview_only_audit",
                "purpose": "verify preview-only safety fields",
                "inputs": {"summaryPath": "cad_reports/execution_summary.json"},
                "targetScope": {"scopeType": "run_artifact", "targetPath": "cad_reports/execution_summary.json"},
                "riskLevel": "low",
                "permissionClass": "deterministic_verify",
                "expectedEvidence": ["preview-only audit report"],
                "forbiddenEffects": ["cad_write", "dwg_save", "delete_entities"],
            }
        )

        with temporary_artifact_dir("tool_contract_preview_audit") as root:
            summary_path = root / "cad_reports" / "execution_summary.json"
            summary_path.parent.mkdir(parents=True, exist_ok=True)
            summary_path.write_text(
                json.dumps(
                    {
                        "status": "ok",
                        "safety": {
                            "layer": "FORMAL",
                            "saved_dwg": True,
                            "deleted_entities": False,
                            "modified_formal_layers": False,
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            trace = run_tool_intent(root, intent, run_id="run-1")
            report = json.loads((root / "cad_reports" / "preview_only_audit.json").read_text(encoding="utf-8"))

            self.assertEqual(trace["orchestratorDecision"], "blocked")
            self.assertEqual(trace["executionStatus"], "failed")
            self.assertEqual(report["status"], "fail")
            self.assertIn("preview-only audit failed", trace["downstreamReadableSummary"])

    def test_closeout_gate_tool_blocks_claim_boundary_without_readback_or_visual_review(self) -> None:
        from core.orchestrator.run_package_state import create_run_package
        from core.orchestrator.tool_contract import run_tool_intent

        intent = _base_intent()
        intent.update(
            {
                "toolIntentId": "intent-closeout-gate",
                "toolName": "closeout_gate",
                "purpose": "run deterministic closeout gate",
                "inputs": {},
                "targetScope": {"scopeType": "run_package", "scopeRef": "current_run"},
                "riskLevel": "low",
                "permissionClass": "deterministic_verify",
                "expectedEvidence": ["closeout decision"],
                "forbiddenEffects": ["cad_write", "dwg_save", "delete_entities"],
            }
        )

        with temporary_artifact_dir("tool_contract_closeout_gate") as root:
            state = create_run_package("closeout-tool-run", user_request={"text": "closeout gate"}, root_dir=root)
            from pathlib import Path

            run_dir = Path(state["runDir"])

            trace = run_tool_intent(run_dir, intent, run_id=state["runId"])
            decision = json.loads((run_dir / "closeout_decision.json").read_text(encoding="utf-8"))

            self.assertEqual(trace["orchestratorDecision"], "blocked")
            self.assertEqual(trace["executionStatus"], "failed")
            self.assertEqual(trace["result"]["status"], "needs_more_evidence")
            self.assertFalse(decision["can_deliver"])
            self.assertIn("created_handles_readback missing", decision["blocking_reasons"])


if __name__ == "__main__":
    unittest.main()
