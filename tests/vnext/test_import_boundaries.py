from __future__ import annotations

import importlib.util
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "vnext" / "check_import_boundaries.py"


def load_checker():
    assert SCRIPT_PATH.exists(), f"missing checker script: {SCRIPT_PATH}"
    spec = importlib.util.spec_from_file_location("check_import_boundaries", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_file(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def codes(findings):
    return {finding["code"] for finding in findings}


class ImportBoundaryTests(unittest.TestCase):
    def test_current_vnext_tree_has_no_import_boundary_findings(self):
        checker = load_checker()

        report = checker.build_report(ROOT)

        self.assertEqual(report["status"], "pass", report["findings"])

    def test_domain_cannot_import_legacy_or_model_runtime_modules(self):
        checker = load_checker()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_file(root, "src/cad_agent_vnext/domain/bad.py", "import openai\nfrom core.orchestrator import x\n")

            findings = checker.check_import_boundaries(root)

        self.assertIn("domain_forbidden_import", codes(findings))

    def test_only_legacy_autocad_adapter_may_import_legacy_execution_base(self):
        checker = load_checker()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_file(root, "src/cad_agent_vnext/adapters/legacy_autocad_backend.py", "from core.cad_io import autocad_com\n")
            write_file(root, "src/cad_agent_vnext/adapters/other_backend.py", "from core.cad_io import autocad_com\n")

            findings = checker.check_import_boundaries(root)

        self.assertIn("vnext_forbidden_legacy_import", codes(findings))
        self.assertEqual(len(findings), 1, findings)

    def test_planning_and_verification_are_kept_from_backend_writes(self):
        checker = load_checker()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_file(root, "src/cad_agent_vnext/planning/bad.py", "from cad_agent_vnext.adapters import legacy_autocad_backend\n")
            write_file(root, "src/cad_agent_vnext/verification/bad.py", "def f(driver):\n    driver.apply_preview_patch({})\n")

            findings = checker.check_import_boundaries(root)

        self.assertIn("planning_forbidden_adapter_import", codes(findings))
        self.assertIn("verification_forbidden_cad_write_call", codes(findings))

    def test_tools_cannot_define_business_keyword_routes(self):
        checker = load_checker()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_file(root, "src/cad_agent_vnext/tools/bad.py", "DESK_KEYWORDS = ['电脑桌', '显示器']\n")

            findings = checker.check_import_boundaries(root)

        self.assertIn("tools_business_keyword_route", codes(findings))


if __name__ == "__main__":
    unittest.main()
