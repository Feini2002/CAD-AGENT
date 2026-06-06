from __future__ import annotations

import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from core.orchestrator.request_context import build_request_context
from core.orchestrator.run_package_state import create_run_package
from tests.helpers import temporary_artifact_dir


class ModelAgentLiveCollabCliTests(unittest.TestCase):
    def test_cli_fixture_model_proves_agent_chain_without_network_or_autocad(self) -> None:
        from scripts.run_model_agent_live_collab_proof import main

        with temporary_artifact_dir("model_agent_live_collab_cli_fixture") as root:
            context = build_request_context(
                context_id="unit-live-cli-fixture",
                request_kind="draw",
                user_request="本地 fixture 模型协作设计一个茶几符号，并做 fake CAD 预检。",
                available_inputs=["cad_plan"],
                allow_cad=False,
            )
            state = create_run_package(
                "unit-live-cli-fixture",
                user_request={"text": context["user_request"], "requestKind": "draw"},
                context_pack={
                    "schemaVersion": "run-package-context-pack/v1",
                    "runId": "unit-live-cli-fixture",
                    "requestContext": context,
                },
                root_dir=root,
            )
            run_dir = Path(state["runDir"])
            stdout = StringIO()

            with redirect_stdout(stdout):
                rc = main(
                    [
                        "--run-dir",
                        str(run_dir),
                        "--driver-mode",
                        "fake_driver_preflight",
                        "--fixture-model",
                    ]
                )

            payload = json.loads(stdout.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(payload["modelChainStatus"], "ready")
            self.assertEqual(payload["conflictHandling"]["status"], "pass")
            self.assertEqual(payload["localFixtureModel"]["status"], "used")
            self.assertTrue(payload["localAgentChainProof"]["agentChainReady"])
            self.assertFalse(payload["cadProof"]["cadGeometryVerified"])
            self.assertEqual(payload["cadProof"]["driverMode"], "fake_driver_preflight")
            self.assertTrue((run_dir / "agent_outputs" / "pipeline_design_director.handoff.json").is_file())
            self.assertTrue((run_dir / "cad_reports" / "cad_preview_tool_report.json").is_file())


if __name__ == "__main__":
    unittest.main()
