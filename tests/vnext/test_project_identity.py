from __future__ import annotations

import json
import sys
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ProjectIdentityTests(unittest.TestCase):
    def test_pyproject_declares_vnext_python_package(self):
        pyproject_path = ROOT / "pyproject.toml"
        self.assertTrue(pyproject_path.exists(), "pyproject.toml must define the vNext Python project identity")

        pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

        self.assertEqual(pyproject["build-system"]["build-backend"], "hatchling.build")
        self.assertEqual(pyproject["project"]["name"], "cad-agent-vnext")
        self.assertEqual(pyproject["project"]["version"], "0.1.0")
        self.assertEqual(pyproject["project"]["requires-python"], ">=3.11")
        self.assertEqual(pyproject["project"]["scripts"]["cad-agent-vnext"], "cad_agent_vnext.cli:main")
        self.assertEqual(
            pyproject["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"],
            ["src/cad_agent_vnext"],
        )
        self.assertEqual(pyproject["tool"]["pytest"]["ini_options"]["testpaths"], ["tests/vnext"])

        dependencies = set(pyproject["project"]["dependencies"])
        self.assertIn("pydantic>=2,<3", dependencies)
        self.assertIn("shapely>=2,<3", dependencies)
        self.assertIn("jsonschema>=4,<5", dependencies)
        self.assertFalse((ROOT / "requirements.txt").exists(), "VN-01 must not add requirements.txt as a second dependency authority")

    def test_vnext_package_exports_version_without_legacy_imports(self):
        src_path = str(ROOT / "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        import cad_agent_vnext

        self.assertEqual(cad_agent_vnext.__version__, "0.1.0")
        package_source = (ROOT / "src" / "cad_agent_vnext" / "__init__.py").read_text(encoding="utf-8")
        forbidden_terms = ("core.orchestrator", "training", "workbench", "agents.pipeline")
        for term in forbidden_terms:
            self.assertNotIn(term, package_source)

    def test_root_control_plane_points_to_vnext_gate0(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

        self.assertIn("docs/vnext/ARCHITECTURE_DECISION.md", readme)
        self.assertIn("docs/vnext/IMPLEMENTATION_MASTER_PLAN.md", readme)
        self.assertIn("vNext Gate 0", readme)
        self.assertIn("docs/vnext/IMPLEMENTATION_MASTER_PLAN.md", agents)
        self.assertIn("active Work Package", agents)
        self.assertIn("savedCurrentDwg=false", agents)

    def test_package_json_marks_worker_as_optional_infrastructure(self):
        package_json = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))

        self.assertTrue(package_json["private"])
        self.assertIn("worker:check", package_json["scripts"])
        self.assertEqual(package_json["cadAgentVNext"]["coreLanguage"], "python")
        self.assertEqual(package_json["cadAgentVNext"]["workerRole"], "optional-infrastructure")
        self.assertEqual(package_json["cadAgentVNext"]["authorityDocs"], ["docs/vnext/ARCHITECTURE_DECISION.md", "docs/vnext/IMPLEMENTATION_MASTER_PLAN.md"])


if __name__ == "__main__":
    unittest.main()
