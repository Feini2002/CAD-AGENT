from __future__ import annotations

import contextlib
import io
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class CliSmokeTests(unittest.TestCase):
    def run_cli(self, *args: str) -> tuple[int, str]:
        from cad_agent_vnext.cli import main

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(list(args))
        return exit_code, stdout.getvalue().strip()

    def test_version_prints_package_version(self):
        exit_code, output = self.run_cli("version")

        self.assertEqual(exit_code, 0)
        self.assertEqual(output, "cad-agent-vnext 0.1.0")

    def test_doctor_reports_without_touching_cad(self):
        exit_code, output = self.run_cli("doctor")

        self.assertEqual(exit_code, 0)
        payload = json.loads(output)
        self.assertEqual(payload["schemaVersion"], "cad-agent-vnext-doctor/v1")
        self.assertEqual(payload["package"]["name"], "cad-agent-vnext")
        self.assertEqual(payload["package"]["version"], "0.1.0")
        self.assertEqual(payload["cad"]["connected"], False)
        self.assertEqual(payload["cad"]["modified"], False)
        self.assertIn("python", payload)
        self.assertIn("pydantic", payload["dependencies"])
        self.assertIn("shapely", payload["dependencies"])
        self.assertTrue(payload["outputPath"]["writable"])


if __name__ == "__main__":
    unittest.main()
