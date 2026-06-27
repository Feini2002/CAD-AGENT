from __future__ import annotations

import json
import sys
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProjectIdentityTests(unittest.TestCase):
    def test_pyproject_declares_cleanroom_python_package(self):
        pyproject_path = ROOT / "pyproject.toml"
        self.assertTrue(pyproject_path.exists(), "pyproject.toml must define the cleanroom Python project identity")

        pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

        self.assertEqual(pyproject["build-system"]["build-backend"], "hatchling.build")
        self.assertEqual(pyproject["project"]["name"], "cad-agent")
        self.assertEqual(pyproject["project"]["version"], "0.1.0")
        self.assertEqual(pyproject["project"]["requires-python"], ">=3.11")
        self.assertEqual(pyproject["project"]["scripts"]["cad-agent"], "cad_agent.cli:main")
        self.assertEqual(
            pyproject["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"],
            ["src/cad_agent"],
        )
        self.assertEqual(pyproject["tool"]["pytest"]["ini_options"]["testpaths"], ["tests"])

        dependencies = set(pyproject["project"]["dependencies"])
        self.assertIn("pydantic>=2,<3", dependencies)
        self.assertIn("shapely>=2,<3", dependencies)
        self.assertIn("jsonschema>=4,<5", dependencies)
        self.assertFalse((ROOT / "requirements.txt").exists(), "Do not add requirements.txt as a second dependency authority")

    def test_package_exports_version_without_old_system_imports(self):
        src_path = str(ROOT / "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        import cad_agent

        self.assertEqual(cad_agent.__version__, "0.1.0")
        package_source = (ROOT / "src" / "cad_agent" / "__init__.py").read_text(encoding="utf-8")
        forbidden_terms = ("core.orchestrator", "training", "workbench", "agents.pipeline")
        for term in forbidden_terms:
            self.assertNotIn(term, package_source)

    def test_root_control_plane_points_to_cleanroom_gate0(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn("docs/ARCHITECTURE.md", readme)
        self.assertIn("docs/STATUS.md", readme)
        self.assertIn("Gate 0", readme)
        self.assertIn("docs/SAFETY.md", agents)
        self.assertIn("Current Active Scope", agents)
        self.assertIn("savedCurrentDwg=false", agents)

    def test_old_system_roots_are_not_present(self):
        forbidden = ["core", "agents", "libraries", "projects", "output", "scripts", "config/vnext", "docs/vnext"]
        existing = [item for item in forbidden if (ROOT / item).exists()]

        self.assertEqual(existing, [])


if __name__ == "__main__":
    unittest.main()
