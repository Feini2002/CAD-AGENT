from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable
sys.path.insert(0, str(PROJECT_ROOT))


class CoreRestructureTests(unittest.TestCase):
    def test_legacy_and_core_execute_imports_share_same_function(self) -> None:
        from core.execution.execute_plan import execute_plan_file as core_execute
        from scripts.execute_plan import execute_plan_file as legacy_execute

        self.assertIs(legacy_execute, core_execute)

    def test_legacy_and_core_render_preview_imports_share_same_function(self) -> None:
        from core.verification.render_preview import capture_screen as core_capture
        from scripts.render_preview import capture_screen as legacy_capture

        self.assertIs(legacy_capture, core_capture)

    def test_driver_legacy_import_reexports_core_driver_status(self) -> None:
        from core.cad_io.autocad_com import driver_status as core_status
        from drivers.autocad_com import driver_status as legacy_status

        self.assertIs(legacy_status, core_status)
        self.assertEqual(legacy_status(), "autocad_com driver ready")

    def test_other_legacy_driver_imports_reexport_core_status(self) -> None:
        from core.cad_io.dxf_writer import driver_status as core_dxf_status
        from core.cad_io.zwcad_com import driver_status as core_zwcad_status
        from drivers.dxf_writer import driver_status as legacy_dxf_status
        from drivers.zwcad_com import driver_status as legacy_zwcad_status

        self.assertIs(legacy_dxf_status, core_dxf_status)
        self.assertIs(legacy_zwcad_status, core_zwcad_status)
        self.assertEqual(legacy_dxf_status(), "dxf_writer driver scaffold")
        self.assertEqual(legacy_zwcad_status(), "zwcad_com driver scaffold")

    def test_schema_compatibility_copies_match_core(self) -> None:
        for name in ["cad_plan.schema.json", "cad_context.schema.json", "cad_object.schema.json"]:
            legacy = (PROJECT_ROOT / "schemas" / name).read_text(encoding="utf-8")
            core = (PROJECT_ROOT / "core" / "schemas" / name).read_text(encoding="utf-8")
            self.assertEqual(legacy, core)

    def test_self_check_identifies_project_root_from_core_module(self) -> None:
        from core.verification.self_check import run_self_check

        report = run_self_check()

        self.assertEqual(Path(str(report["root"])), PROJECT_ROOT)
        self.assertIn(report["status"], {"pass", "warn"})

    def test_legacy_cli_wrappers_still_work(self) -> None:
        commands = [
            [PYTHON, "scripts/validate_plan.py", "examples/plans/draw_test_cabinet.json"],
            [PYTHON, "scripts/dry_run_plan.py", "examples/plans/draw_test_cabinet.json"],
            [PYTHON, "scripts/render_preview.py", "--check"],
            [PYTHON, "scripts/self_check.py"],
            [PYTHON, "scripts/inspect_dwg.py"],
            [PYTHON, "scripts/execute_plan.py", "--help"],
        ]

        for command in commands:
            with self.subTest(command=command):
                result = subprocess.run(
                    command,
                    cwd=PROJECT_ROOT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    capture_output=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

    def test_core_cli_validate_entrypoint_works(self) -> None:
        result = subprocess.run(
            [PYTHON, "-m", "core.plan_engine.validate_plan", "examples/plans/draw_test_cabinet.json"],
            cwd=PROJECT_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("VALID CAD_PLAN", result.stdout)

    def test_agent_manifests_are_valid_json_and_reuse_core(self) -> None:
        agents_root = PROJECT_ROOT / "agents"
        for manifest in agents_root.glob("*/agent.json"):
            with self.subTest(manifest=manifest):
                data = json.loads(manifest.read_text(encoding="utf-8"))
                self.assertIn("name", data)
                self.assertTrue(data.get("coreReuseRequired"))
                self.assertIn("usesCore", data)
                self.assertIn("execution", data["usesCore"])


if __name__ == "__main__":
    unittest.main()
