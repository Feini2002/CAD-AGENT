from __future__ import annotations

import json
import subprocess
import sys
import unittest
from unittest import mock

from tests.helpers import PROJECT_ROOT, temporary_artifact_dir


def _phase9_plan(*, layer: str = "CODEX_PREVIEW") -> dict[str, object]:
    return {
        "version": "0.1",
        "domain": "generic",
        "intent": "draw_object",
        "object": {
            "type": "table",
            "name": "Phase 9 harness table",
            "width": 900,
            "depth": 450,
        },
        "placement": {
            "mode": "absolute",
            "base_point": [72000, 42000, 0],
        },
        "drawing": {
            "layer": layer,
            "include_label": False,
            "include_dimensions": False,
        },
        "confidence": 0.91,
        "needs_confirmation": False,
    }


class CadAgentHarnessTests(unittest.TestCase):
    def test_validate_result_uses_contract_schema_and_safe_defaults(self) -> None:
        from core.contracts.cad_agent_harness import run_harness_command

        result = run_harness_command("validate", cad_plan=_phase9_plan())

        self.assertEqual(result["schemaVersion"], "cad-agent-harness-result/v1")
        self.assertEqual(result["command"], "validate")
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["verificationStatus"], "not_verified")
        self.assertEqual(result["targetLayer"], "CODEX_PREVIEW")
        self.assertEqual(result["backend"], "none")
        self.assertEqual(result["createdHandles"], [])
        self.assertEqual(result["readbackEntities"], [])
        self.assertEqual(result["safety"]["saveAllowed"], False)
        self.assertEqual(result["safety"]["deleteAllowed"], False)
        self.assertEqual(result["safety"]["formalLayersAllowed"], False)
        self.assertEqual(result["safety"]["connectExistingOnly"], True)

    def test_harness_command_is_exported_from_contracts_package(self) -> None:
        from core.contracts import run_harness_command

        result = run_harness_command("validate", cad_plan=_phase9_plan())

        self.assertEqual(result["schemaVersion"], "cad-agent-harness-result/v1")
        self.assertEqual(result["command"], "validate")

    def test_preview_fake_backend_keeps_geometry_not_verified(self) -> None:
        from core.contracts.cad_agent_harness import run_harness_command

        with temporary_artifact_dir("cad_agent_harness_fake_preview") as root:
            result = run_harness_command(
                "preview",
                cad_plan=_phase9_plan(),
                output_dir=root,
                backend="fake-driver",
            )

        self.assertEqual(result["schemaVersion"], "cad-agent-harness-result/v1")
        self.assertEqual(result["command"], "preview")
        self.assertEqual(result["status"], "not_verified")
        self.assertEqual(result["verificationStatus"], "not_verified")
        self.assertEqual(result["backend"], "fake-driver")
        self.assertEqual(len(result["createdHandles"]), 4)
        self.assertEqual(len(result["readbackEntities"]), 4)
        self.assertEqual(result["savedCurrentDwg"], False)
        self.assertEqual(result["cadGeometryVerified"], False)
        self.assertIn("real_cad_readback", result["missingEvidence"])
        self.assertTrue(result["evidencePackageRef"].endswith("phase9_single_preview_evidence_package.json"))

    def test_preview_session_host_backend_uses_host_client_as_real_cad_backend(self) -> None:
        from core.contracts.cad_agent_harness import run_harness_command
        from core.verification.fake_cad_driver import FakeCadDriver

        class FakeSessionHostClient(FakeCadDriver):
            def __init__(self, *, base_url: str, token: str, timeout_seconds: float = 30.0) -> None:
                super().__init__()
                self.base_url = base_url
                self.token = token
                self.timeout_seconds = timeout_seconds

        with temporary_artifact_dir("cad_agent_harness_session_host_preview") as root:
            with mock.patch.dict(
                "os.environ",
                {
                    "CAD_SESSION_HOST_URL": "http://127.0.0.1:8765",
                    "CAD_SESSION_TOKEN": "secret",
                },
            ):
                with mock.patch("core.cad_io.cad_session_host.CadSessionHostClient", FakeSessionHostClient):
                    result = run_harness_command(
                        "preview",
                        cad_plan=_phase9_plan(),
                        output_dir=root,
                        backend="cad-session-host",
                    )

        self.assertEqual(result["backend"], "cad-session-host")
        self.assertEqual(result["status"], "geometry_verified")
        self.assertEqual(result["verificationStatus"], "verified")
        self.assertTrue(result["cadGeometryVerified"])
        self.assertGreater(len(result["createdHandles"]), 0)
        self.assertEqual(len(result["createdHandles"]), len(result["readbackEntities"]))
        self.assertEqual(result["missingEvidence"], [])

    def test_preview_default_backend_uses_session_host_as_primary_live_path(self) -> None:
        from core.contracts.cad_agent_harness import run_harness_command
        from core.verification.fake_cad_driver import FakeCadDriver

        class FakeSessionHostClient(FakeCadDriver):
            def __init__(self, *, base_url: str, token: str, timeout_seconds: float = 30.0) -> None:
                super().__init__()

        with temporary_artifact_dir("cad_agent_harness_default_session_host_preview") as root:
            with mock.patch.dict(
                "os.environ",
                {
                    "CAD_SESSION_HOST_URL": "http://127.0.0.1:8765",
                    "CAD_SESSION_TOKEN": "secret",
                },
            ):
                with mock.patch("core.cad_io.cad_session_host.CadSessionHostClient", FakeSessionHostClient):
                    result = run_harness_command(
                        "preview",
                        cad_plan=_phase9_plan(),
                        output_dir=root,
                    )

        self.assertEqual(result["backend"], "cad-session-host")
        self.assertEqual(result["status"], "geometry_verified")
        self.assertTrue(result["cadGeometryVerified"])

    def test_preview_session_host_backend_requires_explicit_host_configuration(self) -> None:
        from core.contracts.cad_agent_harness import run_harness_command

        with temporary_artifact_dir("cad_agent_harness_session_host_missing_config") as root:
            with mock.patch.dict("os.environ", {}, clear=True):
                result = run_harness_command(
                    "preview",
                    cad_plan=_phase9_plan(),
                    output_dir=root,
                    backend="cad-session-host",
                )

        self.assertEqual(result["backend"], "cad-session-host")
        self.assertEqual(result["status"], "external_blocker")
        self.assertFalse(result["cadGeometryVerified"])
        self.assertIn("real_cad_readback", result["missingEvidence"])
        self.assertTrue(any("CAD_SESSION_HOST_URL" in reason for reason in result["blockingReasons"]))

    def test_evidence_command_reads_existing_phase9_report(self) -> None:
        from core.contracts.cad_agent_harness import run_harness_command

        with temporary_artifact_dir("cad_agent_harness_evidence") as root:
            preview = run_harness_command(
                "preview",
                cad_plan=_phase9_plan(),
                output_dir=root,
                backend="fake-driver",
            )
            result = run_harness_command("evidence", run_dir=root)

        self.assertEqual(result["command"], "evidence")
        self.assertEqual(result["status"], preview["status"])
        self.assertEqual(result["verificationStatus"], "not_verified")
        self.assertEqual(result["artifacts"]["report"], str(root / "phase9_preview_report.json"))
        self.assertEqual(result["createdHandles"], preview["createdHandles"])

    def test_script_validate_outputs_json(self) -> None:
        script = PROJECT_ROOT / "scripts" / "cad_agent_harness.py"

        completed = subprocess.run(
            [sys.executable, str(script), "validate", "--json"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)

        self.assertEqual(result["schemaVersion"], "cad-agent-harness-result/v1")
        self.assertEqual(result["command"], "validate")
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["verificationStatus"], "not_verified")


if __name__ == "__main__":
    unittest.main()
