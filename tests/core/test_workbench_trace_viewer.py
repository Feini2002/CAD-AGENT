from __future__ import annotations

import json
from pathlib import Path
import unittest

from tests.helpers import temporary_artifact_dir


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class WorkbenchTraceViewerTests(unittest.TestCase):
    def test_trace_viewer_summarizes_run_package_agents_and_gates(self) -> None:
        from core.orchestrator.workbench_trace_viewer import build_workbench_trace_viewer_data

        with temporary_artifact_dir("trace_viewer") as root:
            run_dir = root / "output" / "runs" / "run-a"
            _write_json(
                run_dir / "run_state.json",
                {"runId": "run-a", "status": "ready_for_delivery"},
            )
            _write_json(
                run_dir / "required_agents.json",
                {"requiredAgents": ["pipeline_visual_acceptance_reviewer", "pipeline_delivery"]},
            )
            _write_json(
                run_dir / "dispatch_plan.json",
                {"route": "standard_draw", "hardGates": ["validate_plan", "cad_readback"]},
            )
            _write_json(
                run_dir / "closeout_decision.json",
                {
                    "status": "ready_for_delivery",
                    "can_deliver": True,
                    "blocking_reasons": [],
                    "evidence_boundary": {
                        "checked": ["created_handles_readback", "targetLayer=CODEX_PREVIEW"],
                        "not_checked": [],
                        "notProven": ["截图只作视觉辅助"],
                    },
                },
            )
            _write_json(
                run_dir / "agent_outputs" / "pipeline_delivery.json",
                {"deliveryDecision": "ready_to_ask_user_review"},
            )
            _write_json(
                run_dir / "model_traces" / "pipeline_delivery" / "trace-review.json",
                {"agentId": "pipeline_delivery", "status": "pass"},
            )
            _write_json(
                root / "output" / "model_reviews" / "traces" / "pipeline_delivery" / "trace-review.json",
                {"agentId": "pipeline_delivery", "status": "pass"},
            )

            data = build_workbench_trace_viewer_data(root)

            self.assertEqual(data["schemaVersion"], "workbench-trace-viewer/v1")
            self.assertTrue(data["sourcePolicy"]["derivedOnly"])
            self.assertEqual(data["summary"]["runCount"], 1)
            self.assertEqual(data["summary"]["externalTraceCount"], 1)
            run = data["runs"][0]
            self.assertEqual(run["runId"], "run-a")
            self.assertIn("pipeline_delivery", run["agentsCalled"])
            self.assertIn("cad_readback", run["hardGates"])
            self.assertEqual(run["closeout"]["status"], "ready_for_delivery")

    def test_trace_viewer_declares_evidence_boundary_when_empty(self) -> None:
        from core.orchestrator.workbench_trace_viewer import build_workbench_trace_viewer_data

        with temporary_artifact_dir("trace_viewer_empty") as root:
            data = build_workbench_trace_viewer_data(root)

            self.assertEqual(data["summary"]["runCount"], 0)
            self.assertIn("does_not_prove_cad_geometry", data["sourcePolicy"]["notProofOf"])
            self.assertIn("output/runs/**", data["sourcePolicy"]["truthSources"])
