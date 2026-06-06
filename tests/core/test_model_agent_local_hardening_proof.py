from __future__ import annotations

import json
import unittest
from contextlib import redirect_stdout
from io import StringIO

from tests.helpers import temporary_artifact_dir


class ModelAgentLocalHardeningProofTests(unittest.TestCase):
    def test_local_hardening_proof_runs_without_codex_cli_or_autocad(self) -> None:
        from scripts.run_model_agent_local_hardening_proof import main

        with temporary_artifact_dir("model_agent_local_hardening_proof") as root:
            stdout = StringIO()
            with redirect_stdout(stdout):
                rc = main(["--run-id", "unit-local-hardening", "--output-root", str(root / "runs")])

            payload = json.loads(stdout.getvalue())
            report_path = root / "runs" / "unit-local-hardening" / "model_agent_local_hardening_proof.json"

            self.assertEqual(rc, 0)
            self.assertTrue(report_path.is_file())
            self.assertEqual(payload["schemaVersion"], "model-agent-local-hardening-proof/v1")
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["exportManifestGate"], "pass")
            self.assertTrue(payload["repoExternalCwd"])
            self.assertFalse(payload["unexpectedProjectContextLoaded"])
            self.assertEqual(payload["decisionChainFields"], "pass")
            self.assertEqual(payload["handoffPackets"], "pass")
            self.assertEqual(payload["toolIntentFixtures"], "pass")
            self.assertEqual(payload["closeoutStateMachine"], "pass")
            self.assertEqual(payload["errorTaxonomy"], "pass")
            self.assertIn("real OpenAI provider availability", payload["notProven"])
            self.assertIn("real AutoCAD geometry", payload["notProven"])

    def test_local_hardening_proof_report_matches_saved_payload(self) -> None:
        from scripts.run_model_agent_local_hardening_proof import main

        with temporary_artifact_dir("model_agent_local_hardening_proof_saved") as root:
            stdout = StringIO()
            with redirect_stdout(stdout):
                main(["--run-id", "unit-local-hardening-saved", "--output-root", str(root / "runs")])

            printed = json.loads(stdout.getvalue())
            saved = json.loads(
                (root / "runs" / "unit-local-hardening-saved" / "model_agent_local_hardening_proof.json").read_text(
                    encoding="utf-8"
                )
            )

            self.assertEqual(saved, printed)


if __name__ == "__main__":
    unittest.main()
