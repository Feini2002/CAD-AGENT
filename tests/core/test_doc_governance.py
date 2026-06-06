from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests.helpers import PROJECT_ROOT, artifact_path

import core.maintenance.doc_governance as doc_governance

from core.maintenance.doc_governance import (
    check_active_doc_size_budgets,
    check_architecture_hardening_index,
    build_doc_governance_report,
    build_doc_registry,
    check_data_bloat_governance_manifest,
    check_doc_source_of_truth,
    check_handoff_files,
    check_handoff_document,
    check_markdown_links,
    check_root_migration_stubs,
    check_table_c_values,
    check_training_context_alignment,
)


class DocGovernanceTests(unittest.TestCase):
    def test_openspec_contract_check_flags_root_tasks_and_master_plan_claim(self) -> None:
        root = artifact_path("doc_governance", "openspec_contract_misuse")
        (root / "openspec" / "changes" / "claim-master-plan").mkdir(parents=True, exist_ok=True)
        (root / "openspec" / "changes" / "archive" / "old-claim").mkdir(parents=True, exist_ok=True)
        (root / "openspec" / "config.yaml").write_text(
            "schema: spec-driven\ncontext: CORE_RESTRUCTURE_PLAN.md remains primary.\n",
            encoding="utf-8",
        )
        (root / "openspec" / "tasks.md").write_text("- [ ] global task\n", encoding="utf-8")
        (root / "openspec" / "changes" / "claim-master-plan" / "proposal.md").write_text(
            "本文是唯一 PlanMD，承载全局 backlog。\n",
            encoding="utf-8",
        )
        (root / "openspec" / "changes" / "archive" / "old-claim" / "proposal.md").write_text(
            "历史归档里说自己是唯一 PlanMD 不应阻断当前检查。\n",
            encoding="utf-8",
        )

        report = doc_governance.check_openspec_contracts(root)

        codes = {finding["code"] for finding in report["findings"]}
        paths = {finding["path"] for finding in report["findings"]}
        self.assertIn("openspec_root_tasks_forbidden", codes)
        self.assertIn("openspec_change_claims_master_plan", codes)
        self.assertIn("openspec/tasks.md", paths)
        self.assertNotIn("openspec/changes/archive/old-claim/proposal.md", paths)

    def test_openspec_contract_check_flags_change_tasks_as_global_backlog(self) -> None:
        root = artifact_path("doc_governance", "openspec_change_tasks_backlog")
        (root / "openspec" / "changes" / "global-next").mkdir(parents=True, exist_ok=True)
        (root / "openspec" / "config.yaml").write_text(
            "schema: spec-driven\ncontext: CORE_RESTRUCTURE_PLAN.md remains primary.\n",
            encoding="utf-8",
        )
        (root / "openspec" / "changes" / "global-next" / "tasks.md").write_text(
            "这里承载全局 next 和总 backlog。\n",
            encoding="utf-8",
        )

        report = doc_governance.check_openspec_contracts(root)

        codes = {finding["code"] for finding in report["findings"]}
        paths = {finding["path"] for finding in report["findings"]}
        self.assertIn("openspec_change_tasks_claims_global_backlog", codes)
        self.assertIn("openspec/changes/global-next/tasks.md", paths)

    def test_openspec_contract_check_requires_planmd_boundary_in_config(self) -> None:
        root = artifact_path("doc_governance", "openspec_contract_config")
        (root / "openspec").mkdir(parents=True, exist_ok=True)
        (root / "openspec" / "config.yaml").write_text(
            "schema: spec-driven\ncontext: contract layer only\n",
            encoding="utf-8",
        )

        report = doc_governance.check_openspec_contracts(root)

        codes = {finding["code"] for finding in report["findings"]}
        self.assertIn("openspec_config_missing_planmd_boundary", codes)

    def test_openspec_contract_check_passes_valid_contract_layer(self) -> None:
        root = artifact_path("doc_governance", "openspec_contract_pass")
        (root / "openspec" / "changes" / "scoped-change").mkdir(parents=True, exist_ok=True)
        (root / "openspec" / "config.yaml").write_text(
            "schema: spec-driven\ncontext: CORE_RESTRUCTURE_PLAN.md remains primary.\n",
            encoding="utf-8",
        )
        (root / "openspec" / "changes" / "scoped-change" / "proposal.md").write_text(
            "This change is scoped and does not carry global next.\n",
            encoding="utf-8",
        )

        report = doc_governance.check_openspec_contracts(root)

        self.assertEqual(report["status"], "pass", report["findings"])
        self.assertEqual(report["summary"]["active_change_file_count"], 1)

    def test_build_doc_governance_report_includes_openspec_contracts(self) -> None:
        root = artifact_path("doc_governance", "openspec_contract_report")
        (root / "openspec").mkdir(parents=True, exist_ok=True)
        (root / "openspec" / "config.yaml").write_text(
            "schema: spec-driven\ncontext: CORE_RESTRUCTURE_PLAN.md remains primary.\n",
            encoding="utf-8",
        )

        report = build_doc_governance_report(root)

        self.assertIn("openspec_contracts", report)
        self.assertIn("architecture_hardening", report)
        self.assertIn("data_bloat_governance", report)

    def test_architecture_hardening_index_flags_missing_tokens(self) -> None:
        root = artifact_path("doc_governance", "architecture_hardening_missing")
        (root / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
        (root / "README.md").write_text(
            "User Request -> semantic route -> A-to-A contract\n",
            encoding="utf-8",
        )
        (root / "docs" / "architecture" / "README.md").write_text(
            "UTF-8 preflight\n",
            encoding="utf-8",
        )
        (root / "docs" / "architecture" / "current-module-boundaries.md").write_text(
            "core/orchestrator/\n",
            encoding="utf-8",
        )

        report = check_architecture_hardening_index(root)

        self.assertEqual(report["status"], "findings")
        codes = {finding["code"] for finding in report["findings"]}
        paths = {finding["path"] for finding in report["findings"]}
        self.assertIn("architecture_hardening_missing_token", codes)
        self.assertIn("README.md", paths)
        self.assertIn("docs/architecture/README.md", paths)
        self.assertIn("docs/architecture/current-module-boundaries.md", paths)

    def test_data_bloat_manifest_flags_missing_gate_and_ambiguous_workbench(self) -> None:
        root = artifact_path("doc_governance", "data_bloat_manifest_bad")
        (root / "agents" / "pipeline").mkdir(parents=True, exist_ok=True)
        (root / "AGENTS.md").write_text("data_bloat_governance\n", encoding="utf-8")
        (root / "agents" / "pipeline" / "README.md").write_text(
            "`pipeline_context_curator`\n", encoding="utf-8"
        )
        (root / "agents" / "pipeline" / "pipeline_manifest.json").write_text(
            json.dumps(
                {
                    "orchestration": {
                        "dynamic_dispatch_policy": {
                            "high_risk_task_kinds": ["training_workbench_sync"],
                            "low_risk_task_kinds": [],
                        },
                        "required_hard_gates_by_task_kind": {"training_workbench_sync": []},
                        "hard_gates": {"data_bloat_governance": {"blocks": []}},
                        "flow_variants": {"training_data_bloat_governance": ["pipeline_context_curator"]},
                    },
                    "agents": [{"agent_id": "pipeline_context_curator"}],
                    "artifacts": {},
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        report = check_data_bloat_governance_manifest(root)

        codes = {finding["code"] for finding in report["findings"]}
        self.assertIn("data_bloat_ambiguous_workbench_sync", codes)
        self.assertIn("data_bloat_missing_workbench_refresh_exemption", codes)
        self.assertIn("data_bloat_task_kind_missing_hard_gate", codes)
        self.assertIn("data_bloat_gate_missing_blocks", codes)

    def test_data_bloat_manifest_passes_valid_manifest(self) -> None:
        root = artifact_path("doc_governance", "data_bloat_manifest_pass")
        (root / "agents" / "pipeline").mkdir(parents=True, exist_ok=True)
        agent_ids = sorted(doc_governance.DATA_BLOAT_FLOW_AGENTS)
        (root / "agents" / "pipeline" / "README.md").write_text(
            "\n".join(f"`{agent_id}`" for agent_id in agent_ids),
            encoding="utf-8",
        )
        (root / "agents" / "pipeline" / "pipeline_manifest.json").write_text(
            json.dumps(
                {
                    "orchestration": {
                        "dynamic_dispatch_policy": {
                            "high_risk_task_kinds": sorted(
                                doc_governance.DATA_BLOAT_GOVERNANCE_TASK_KINDS
                            ),
                            "low_risk_task_kinds": ["workbench_snapshot_refresh"],
                        },
                        "required_hard_gates_by_task_kind": {
                            task_kind: ["data_bloat_governance"]
                            for task_kind in doc_governance.DATA_BLOAT_GOVERNANCE_TASK_KINDS
                        },
                        "hard_gates": {
                            "data_bloat_governance": {
                                "blocks": sorted(doc_governance.DATA_BLOAT_GOVERNANCE_BLOCKS)
                            }
                        },
                        "flow_variants": {"training_data_bloat_governance": agent_ids},
                    },
                    "agents": [{"agent_id": agent_id} for agent_id in agent_ids],
                    "artifacts": {
                        artifact_id: "projects/<case>/runs/report.json"
                        for artifact_id in doc_governance.DATA_BLOAT_GOVERNANCE_ARTIFACTS
                    },
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        report = check_data_bloat_governance_manifest(root)

        self.assertEqual(report["status"], "pass", report["findings"])

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
        (root / "当前状态入口.md").write_text("## 下一步计划\nnext=BAD\n", encoding="utf-8")
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
        (root / "长期规则入口.md").write_text("# Stub\n", encoding="utf-8")

        report = check_root_migration_stubs(root)

        self.assertEqual(report["status"], "findings")
        codes = {finding["code"] for finding in report["findings"]}
        self.assertIn("undocumented_root_migration_stub_deletion", codes)
        self.assertIn("broken_root_migration_target", codes)

    def test_root_migration_stub_check_allows_documented_deletion(self) -> None:
        root = artifact_path("doc_governance", "root_stubs_deleted")
        (root / "docs").mkdir(parents=True, exist_ok=True)
        for target in doc_governance.ROOT_MIGRATION_STUB_TARGETS.values():
            target_path = root / target
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text("# target\n", encoding="utf-8")
        rows = ["# Docs", "", "| 旧入口 | 目标 |", "| --- | --- |"]
        rows.extend(
            f"| `{stub}` | `{target}` |"
            for stub, target in sorted(doc_governance.ROOT_MIGRATION_STUB_TARGETS.items())
        )
        (root / "docs" / "README.md").write_text("\n".join(rows), encoding="utf-8")

        report = check_root_migration_stubs(root)

        self.assertEqual(report["status"], "pass", report["findings"])
        self.assertEqual(
            report["summary"]["documented_deleted_stub_count"],
            len(doc_governance.ROOT_MIGRATION_STUB_TARGETS),
        )

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
        (root / "docs" / "status").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "status" / "current.md").write_text(
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
        self.assertEqual(findings[0]["path"], "docs/status/current.md")

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

    def test_doc_governance_flags_table_c_as_end_to_end_claim(self) -> None:
        root = artifact_path("doc_governance", "table_c_semantic_bad")
        (root / "docs" / "status").mkdir(parents=True, exist_ok=True)
        (root / "coverage.json").write_text(
            json.dumps({"cad_strength_headline_percent": 90.99}),
            encoding="utf-8",
        )
        (root / "docs" / "status" / "current.md").write_text(
            "表 C 90.99% 证明端到端真实 CAD 能力已经具备，可以交付真实项目。\n",
            encoding="utf-8",
        )

        report = build_doc_governance_report(root, coverage_path=root / "coverage.json")

        semantic = report.get("table_c_semantic_boundary", {})
        codes = {finding["code"] for finding in semantic.get("findings", [])}
        self.assertIn("table_c_end_to_end_claim", codes)

    def test_doc_governance_accepts_table_c_three_maturity_boundary(self) -> None:
        root = artifact_path("doc_governance", "table_c_semantic_good")
        (root / "docs" / "status").mkdir(parents=True, exist_ok=True)
        (root / "coverage.json").write_text(
            json.dumps({"cad_strength_headline_percent": 90.99}),
            encoding="utf-8",
        )
        (root / "docs" / "status" / "current.md").write_text(
            "\n".join(
                [
                    "表 C 现在是 Core Proof Coverage。",
                    "它不代表 Agent Task Maturity，也不代表 Project Delivery Readiness。",
                ]
            ),
            encoding="utf-8",
        )

        report = build_doc_governance_report(root, coverage_path=root / "coverage.json")

        semantic = report.get("table_c_semantic_boundary", {})
        self.assertEqual(semantic.get("status"), "pass", semantic.get("findings"))

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
        (root / "当前状态入口.md").write_text(
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
        self.assertEqual(
            report["architecture_hardening"]["status"],
            "pass",
            report["architecture_hardening"]["findings"],
        )

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

    def test_output_reply_policy_flags_default_progress_table_regression(self) -> None:
        checker = getattr(doc_governance, "check_output_reply_policy", None)
        self.assertIsNotNone(checker)

        root = artifact_path("doc_governance", "output_reply_policy")
        root.mkdir(parents=True, exist_ok=True)
        (root / "AGENTS.md").write_text(
            "聊天交付默认用 `AGENTS.md` 的 **1 张精简进度表**，先报表 C 主指标。\n",
            encoding="utf-8",
        )
        (root / "docs" / "history").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "history" / "old.md").write_text(
            "聊天交付默认用 `AGENTS.md` 的 **1 张精简进度表**。\n",
            encoding="utf-8",
        )

        report = checker(root)

        self.assertEqual(report["status"], "findings")
        self.assertEqual(report["findings"][0]["code"], "stale_output_reply_policy")
        self.assertEqual(report["findings"][0]["path"], "AGENTS.md")

    def test_current_repository_output_reply_policy_is_opt_in(self) -> None:
        checker = getattr(doc_governance, "check_output_reply_policy", None)
        self.assertIsNotNone(checker)

        report = checker(PROJECT_ROOT)

        self.assertEqual(report["status"], "pass", report["findings"])


if __name__ == "__main__":
    unittest.main()
