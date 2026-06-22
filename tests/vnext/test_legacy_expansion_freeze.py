from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "vnext" / "check_legacy_expansion.py"


def load_checker():
    assert SCRIPT_PATH.exists(), f"missing checker script: {SCRIPT_PATH}"
    spec = importlib.util.spec_from_file_location("check_legacy_expansion", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def finding_codes(findings):
    return {finding["code"] for finding in findings}


class LegacyExpansionFreezeTests(unittest.TestCase):
    def test_blocks_new_pipeline_agent_json(self):
        checker = load_checker()

        findings = checker.find_legacy_expansions(
            ["agents/pipeline/new_role/agent.json"],
            baseline_ref="legacy-baseline-2026-06-22",
        )

        self.assertIn("legacy_pipeline_agent_added", finding_codes(findings))

    def test_blocks_new_root_architecture_md_and_run_script(self):
        checker = load_checker()

        findings = checker.find_legacy_expansions(
            ["NEW_ARCHITECTURE_PLAN.md", "scripts/run_new_legacy_flow.py"],
            baseline_ref="legacy-baseline-2026-06-22",
        )

        self.assertEqual(
            finding_codes(findings),
            {"root_architecture_doc_added", "legacy_run_script_added"},
        )

    def test_blocks_new_training_curriculum_item(self):
        checker = load_checker()

        findings = checker.find_legacy_expansions(
            ["docs/training/curriculum/new_lesson.md"],
            baseline_ref="legacy-baseline-2026-06-22",
        )

        self.assertIn("training_curriculum_item_added", finding_codes(findings))

    def test_allows_vnext_migration_files(self):
        checker = load_checker()

        findings = checker.find_legacy_expansions(
            [
                "docs/vnext/baseline.md",
                "docs/vnext/MIGRATION_STATE.json",
                "scripts/vnext/check_legacy_expansion.py",
                "tests/vnext/test_legacy_expansion_freeze.py",
                "src/cad_agent_vnext/__init__.py",
                ".agents/skills/cad-scene-authoring/SKILL.md",
                "config/vnext/object_catalog.json",
                "evals/gate0/cases.jsonl",
                "schemas/vnext/generated/scene-spec.schema.json",
                "output/vnext/runs/example/report.json",
                "pyproject.toml",
            ],
            baseline_ref="legacy-baseline-2026-06-22",
        )

        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
