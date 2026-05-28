from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import PROJECT_ROOT, artifact_path

from core.maintenance.doc_governance import (
    check_active_doc_size_budgets,
    build_doc_governance_report,
    build_doc_registry,
    check_doc_source_of_truth,
    check_handoff_files,
    check_handoff_document,
    check_markdown_links,
    check_root_migration_stubs,
    check_table_c_values,
    check_training_context_alignment,
)


class DocGovernanceTests(unittest.TestCase):
    def test_registry_ignores_output_markdown_by_default(self) -> None:
        root = artifact_path("doc_governance", "registry")
        (root / "docs").mkdir(parents=True, exist_ok=True)
        (root / "output" / "validation_runs" / "case").mkdir(parents=True, exist_ok=True)
        (root / "README.md").write_text("# Root\n", encoding="utf-8")
        (root / "docs" / "README.md").write_text("# Docs\n", encoding="utf-8")
        (root / "output" / "validation_runs" / "case" / "report.md").write_text(
            "# Generated\n", encoding="utf-8"
        )

        report = build_doc_registry(root)

        paths = {row["path"] for row in report["documents"]}
        self.assertIn("README.md", paths)
        self.assertIn("docs/README.md", paths)
        self.assertNotIn("output/validation_runs/case/report.md", paths)
        self.assertEqual(report["summary"]["document_count"], 2)

    def test_source_of_truth_check_flags_extra_planmd_and_status_next(self) -> None:
        root = artifact_path("doc_governance", "source_of_truth")
        root.mkdir(parents=True, exist_ok=True)
        (root / "CORE_RESTRUCTURE_PLAN.md").write_text("# Main PlanMD\n", encoding="utf-8")
        (root / "CAD_AGENT_STATUS.md").write_text("## 下一步计划\nnext=BAD\n", encoding="utf-8")
        (root / "docs" / "planning").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "planning" / "phase-extra.md").write_text(
            "# Extra PlanMD\n后置 Backlog\n", encoding="utf-8"
        )

        report = check_doc_source_of_truth(root)

        codes = {finding["code"] for finding in report["findings"]}
        self.assertIn("status_carries_next", codes)
        self.assertIn("planning_doc_carries_backlog", codes)

    def test_handoff_check_requires_fixed_sections_and_extension_items(self) -> None:
        handoff_text = """# Handoff

## V-PROOF-01：能力包

### 1. 包名
### 2. 改动范围
### 3. 验证命令
### 4. 证据路径
### 5. 风险边界
### 6. 真实 CAD
### 7. 输出
### 8. 结论分类
### 9. 后续接手
"""

        report = check_handoff_document(handoff_text, path="docs/handoffs/current.md")

        codes = {finding["code"] for finding in report["findings"]}
        self.assertIn("handoff_missing_capability_extension", codes)

    def test_handoff_check_validates_package_index_locations(self) -> None:
        root = artifact_path("doc_governance", "handoff_index")
        (root / "docs" / "handoffs").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "handoffs" / "current.md").write_text("# Current\n", encoding="utf-8")
        (root / "docs" / "handoffs" / "package-index.md").write_text(
            "\n".join(
                [
                    "# Index",
                    "",
                    "| 序号 | 开发包 | 位置 |",
                    "| --- | --- | --- |",
                    "| 1 | STRUCT-AUDIT-01 | `current.md` |",
                    "| 2 | OLD-PACKAGE | `archive/missing.md` |",
                ]
            ),
            encoding="utf-8",
        )

        report = check_handoff_files(root)

        codes = {finding["code"] for finding in report["findings"]}
        self.assertIn("handoff_index_missing_target", codes)

    def test_handoff_index_current_rows_must_exist_in_current_window(self) -> None:
        root = artifact_path("doc_governance", "handoff_index_current_window")
        (root / "docs" / "handoffs").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "handoffs" / "current.md").write_text(
            "# Current\n\n## CAD-EVIDENCE-01-HARD-AUDIT\n\n1. 包名\n",
            encoding="utf-8",
        )
        (root / "docs" / "handoffs" / "package-index.md").write_text(
            "\n".join(
                [
                    "# Index",
                    "",
                    "| 序号 | 开发包 | 位置 |",
                    "| --- | --- | --- |",
                    "| 1 | CAD-EVIDENCE-01：HARD-AUDIT | `current.md` |",
                    "| 2 | STRUCT-AUDIT-01：历史包 | `current.md` |",
                ]
            ),
            encoding="utf-8",
        )

        report = check_handoff_files(root)

        codes = {finding["code"] for finding in report["findings"]}
        self.assertIn("handoff_index_current_missing_package_section", codes)

    def test_markdown_link_check_flags_missing_relative_files(self) -> None:
        root = artifact_path("doc_governance", "links")
        (root / "docs").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "README.md").write_text(
            "[Missing](missing.md)\n[Existing](existing.md)\n", encoding="utf-8"
        )
        (root / "docs" / "existing.md").write_text("# Existing\n", encoding="utf-8")

        report = check_markdown_links(root)

        self.assertEqual(report["status"], "findings")
        self.assertEqual(report["findings"][0]["code"], "missing_markdown_link_target")

    def test_markdown_link_check_ignores_history_snapshots(self) -> None:
        root = artifact_path("doc_governance", "history_links")
        (root / "docs" / "history" / "snapshots" / "case").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "history" / "snapshots" / "case" / "old.md").write_text(
            "[Old relative link](../../CORE_STATUS.md)\n",
            encoding="utf-8",
        )

        report = check_markdown_links(root)

        self.assertEqual(report["status"], "pass", report["findings"])

    def test_table_c_check_ignores_changelog_history_stream(self) -> None:
        root = artifact_path("doc_governance", "table_c_changelog")
        (root / "docs" / "status").mkdir(parents=True, exist_ok=True)
        coverage = {"cad_strength_headline_percent": 9.6, "highest_proven_ladder_level": "L4"}
        (root / "coverage.json").write_text(json.dumps(coverage), encoding="utf-8")
        (root / "docs" / "status" / "changelog.md").write_text(
            "真实 CAD 实力主指标 **8.87%** 的历史流水\n", encoding="utf-8"
        )
        (root / "README.md").write_text("真实 CAD 实力 | 约 9.6%，最高 L4\n", encoding="utf-8")

        report = check_table_c_values(root, coverage_path=root / "coverage.json")

        self.assertEqual(report["status"], "pass", report["findings"])

    def test_table_c_check_skips_historical_lines_in_active_docs(self) -> None:
        root = artifact_path("doc_governance", "table_c_historical_line")
        (root / "docs" / "status").mkdir(parents=True, exist_ok=True)
        coverage = {"cad_strength_headline_percent": 9.6, "highest_proven_ladder_level": "L4"}
        (root / "coverage.json").write_text(json.dumps(coverage), encoding="utf-8")
        current = root / "docs" / "status" / "current.md"
        current.write_text(
            "\n".join(
                [
                    "历史快照：真实 CAD 实力主指标 **8.87%**",
                    "真实 CAD 实力（主指标） | **9.6%**",
                ]
            ),
            encoding="utf-8",
        )

        report = check_table_c_values(root, coverage_path=root / "coverage.json")

        self.assertEqual(report["status"], "pass", report["findings"])

    def test_root_migration_stub_check_flags_missing_target(self) -> None:
        root = artifact_path("doc_governance", "root_stubs")
        root.mkdir(parents=True, exist_ok=True)
        (root / "CAD_AGENT_RULES.md").write_text("# Stub\n", encoding="utf-8")

        report = check_root_migration_stubs(root)

        self.assertEqual(report["status"], "findings")
        codes = {finding["code"] for finding in report["findings"]}
        self.assertIn("missing_root_migration_stub", codes)
        self.assertIn("broken_root_migration_target", codes)

    def test_active_doc_size_budget_flags_overgrown_control_file(self) -> None:
        root = artifact_path("doc_governance", "active_doc_budget")
        root.mkdir(parents=True, exist_ok=True)
        (root / "CORE_RESTRUCTURE_PLAN.md").write_text(
            "\n".join(["# Plan"] + ["line"] * 141),
            encoding="utf-8",
        )

        report = check_active_doc_size_budgets(root)

        self.assertEqual(report["status"], "findings")
        self.assertEqual(report["findings"][0]["code"], "active_doc_over_budget")
        self.assertEqual(report["findings"][0]["path"], "CORE_RESTRUCTURE_PLAN.md")

    def test_current_repository_active_docs_fit_finished_architecture_budget(self) -> None:
        report = check_active_doc_size_budgets(PROJECT_ROOT)

        self.assertEqual(report["status"], "pass", report["findings"])

    def test_table_c_check_compares_active_docs_and_ignores_history(self) -> None:
        root = artifact_path("doc_governance", "table_c")
        (root / "docs" / "history").mkdir(parents=True, exist_ok=True)
        coverage = {
            "cad_strength_headline_percent": 8.87,
            "cad_proof_coverage_percent": 48.58,
            "highest_proven_ladder_level": "L4",
        }
        (root / "coverage.json").write_text(json.dumps(coverage), encoding="utf-8")
        (root / "CAD_AGENT_STATUS.md").write_text(
            "真实 CAD 实力 | 约 4.35%，最高 L3\n", encoding="utf-8"
        )
        (root / "docs" / "history" / "old.md").write_text(
            "历史快照：真实 CAD 实力 | 约 4.35%，最高 L3；当前以 JSON 为准\n",
            encoding="utf-8",
        )

        report = check_table_c_values(root, coverage_path=root / "coverage.json")

        findings = report["findings"]
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["code"], "stale_table_c_headline")
        self.assertEqual(findings[0]["path"], "CAD_AGENT_STATUS.md")

    def test_table_c_check_ignores_templates_and_unrelated_percentages(self) -> None:
        root = artifact_path("doc_governance", "table_c_template")
        root.mkdir(parents=True, exist_ok=True)
        coverage = {
            "cad_strength_headline_percent": 8.87,
            "cad_proof_coverage_percent": 48.58,
            "highest_proven_ladder_level": "L4",
        }
        (root / "coverage.json").write_text(json.dumps(coverage), encoding="utf-8")
        (root / "AGENTS.md").write_text(
            "\n".join(
                [
                    "| 真实 CAD 实力 | 约 xx%，最高 Lx | 表 C 主指标 |",
                    "表 A 默认 Core 70% + Agent 30%。",
                    "机器值字段包括 cad_strength_headline_percent。",
                ]
            ),
            encoding="utf-8",
        )

        report = check_table_c_values(root, coverage_path=root / "coverage.json")

        self.assertEqual(report["status"], "pass", report["findings"])

    def test_table_c_check_accepts_zero_headline_value(self) -> None:
        root = artifact_path("doc_governance", "table_c_zero")
        root.mkdir(parents=True, exist_ok=True)
        coverage = {
            "summary": {
                "cad_strength_headline_percent": 0.0,
                "cad_proof_coverage_percent": 0.0,
            },
            "cad_strength": {"highest_proven_ladder_level": ""},
        }
        (root / "coverage.json").write_text(json.dumps(coverage), encoding="utf-8")
        (root / "CAD_AGENT_STATUS.md").write_text(
            "真实 CAD 实力 | 0%，最高 L0\n", encoding="utf-8"
        )

        report = check_table_c_values(root, coverage_path=root / "coverage.json")

        self.assertEqual(report["status"], "pass", report["findings"])

    def test_cli_emits_aggregate_report(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "run_doc_governance_audit.py"),
                "--root",
                str(PROJECT_ROOT),
            ],
            cwd=PROJECT_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertIn("doc_registry", report)
        self.assertIn("source_of_truth", report)
        self.assertIn("table_c", report)
        self.assertIn("handoff", report)
        self.assertIn("root_stubs", report)
        self.assertIn("training_context", report)

    def test_current_repository_keeps_required_doc_architecture(self) -> None:
        report = build_doc_governance_report(PROJECT_ROOT)

        self.assertIn(report["status"], {"pass", "findings"})
        registry_paths = {row["path"] for row in report["doc_registry"]["documents"]}
        self.assertIn("CORE_RESTRUCTURE_PLAN.md", registry_paths)
        self.assertIn("CORE_CONTEXT_BRIEF.md", registry_paths)
        self.assertNotIn("output/validation_runs/struct-audit-01/struct_audit_fragments.md", registry_paths)

    def test_training_context_alignment_flags_missing_visual_first_contract(self) -> None:
        root = artifact_path("doc_governance", "training_context_missing")
        (root / "docs" / "training").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "planning").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "history").mkdir(parents=True, exist_ok=True)
        (root / "CORE_CONTEXT_BRIEF.md").write_text("# Brief\nAgent training.\n", encoding="utf-8")
        (root / "CORE_RESTRUCTURE_PLAN.md").write_text("# Plan\nAgent training.\n", encoding="utf-8")
        (root / "docs" / "training" / "README.md").write_text("# Training\nCAD_PLAN only.\n", encoding="utf-8")
        (root / "docs" / "planning" / "任务清单.md").write_text("# Tasks\ncase backlog.\n", encoding="utf-8")
        (root / "docs" / "history" / "README.md").write_text("# History\nOld docs.\n", encoding="utf-8")

        report = check_training_context_alignment(root)

        codes = {finding["code"] for finding in report["findings"]}
        self.assertIn("training_context_missing_token", codes)
        self.assertIn("history_readme_missing_history_only_marker", codes)

    def test_training_context_alignment_checks_pipeline_manifest_gate(self) -> None:
        root = artifact_path("doc_governance", "training_context_manifest")
        (root / "docs" / "training").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "planning").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "history").mkdir(parents=True, exist_ok=True)
        (root / "agents" / "pipeline").mkdir(parents=True, exist_ok=True)
        (root / "CORE_CONTEXT_BRIEF.md").write_text("Visual-First visual_parts\n", encoding="utf-8")
        (root / "CORE_RESTRUCTURE_PLAN.md").write_text("Visual-First visual_parts\n", encoding="utf-8")
        (root / "docs" / "training" / "README.md").write_text(
            "pipeline_visual_intent visual_parts reference_match\n",
            encoding="utf-8",
        )
        (root / "docs" / "planning" / "任务清单.md").write_text(
            "Visual-First visual_parts\n",
            encoding="utf-8",
        )
        (root / "docs" / "history" / "README.md").write_text("HISTORY-ONLY\n", encoding="utf-8")
        (root / "agents" / "pipeline" / "pipeline_manifest.json").write_text(
            json.dumps(
                {
                    "orchestration": {
                        "default_flow": ["pipeline_intent", "pipeline_execute"],
                        "hard_gates": {
                            "reference_match": {
                                "requires": ["style_target"],
                                "blocks": [],
                            }
                        },
                    }
                }
            ),
            encoding="utf-8",
        )

        report = check_training_context_alignment(root)

        codes = {finding["code"] for finding in report["findings"]}
        self.assertIn("pipeline_visual_intent_not_in_default_flow", codes)
        self.assertIn("reference_match_gate_incomplete", codes)

    def test_current_repository_training_context_is_visual_first_aligned(self) -> None:
        report = check_training_context_alignment(PROJECT_ROOT)

        self.assertEqual(report["status"], "pass", report["findings"])


if __name__ == "__main__":
    unittest.main()
