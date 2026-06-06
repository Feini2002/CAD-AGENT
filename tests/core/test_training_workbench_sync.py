from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests.bootstrap import PROJECT_ROOT


class TrainingWorkbenchSyncTests(unittest.TestCase):
    def artifact_root(self) -> Path:
        root = PROJECT_ROOT / "output" / "test_artifacts" / "training_workbench_sync_tests"
        root.mkdir(parents=True, exist_ok=True)
        return root

    def rewrite_training_sources_to_fixture_files(self, data_path: Path) -> None:
        from scripts.run_training_workbench_agent_check import load_workbench_data

        data = load_workbench_data(data_path)
        source_root = self.artifact_root() / "training_source_fixture"
        source_root.mkdir(parents=True, exist_ok=True)

        path_map: dict[str, str] = {}
        for index, source in enumerate(data.get("trainingSources", [])):
            old_path = str(source.get("path", ""))
            if not old_path or source.get("status", "active") != "active":
                continue
            suffix = Path(old_path).suffix or ".json"
            fixture_path = source_root / f"source_{index}{suffix}"
            if suffix.lower() in {".png", ".jpg", ".jpeg"}:
                fixture_path.write_bytes(b"fixture image placeholder")
            else:
                fixture_path.write_text(
                    json.dumps({"fixtureFor": old_path}, ensure_ascii=False),
                    encoding="utf-8",
                )
            new_path = fixture_path.relative_to(PROJECT_ROOT).as_posix()
            path_map[old_path] = new_path
            source["path"] = new_path

        for program in data.get("trainingPrograms", []):
            acceptance = program.get("trainingAcceptance", {})
            source_path = acceptance.get("source")
            if source_path in path_map:
                acceptance["source"] = path_map[source_path]

        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        data_path.write_text(f"window.CAD_CAPABILITY_MAP_DATA = {payload};\n", encoding="utf-8")

    def test_generated_prompt_source_refs_point_to_real_files(self) -> None:
        from scripts import build_capability_map_data

        data = build_capability_map_data.build_data()
        missing: list[str] = []
        for contract in data["promptContracts"]:
            for source_ref in contract.get("sourceRefs", []):
                path = source_ref.get("path", "")
                if not path or "<" in path or "*" in path:
                    continue
                if not (PROJECT_ROOT / path).is_file():
                    missing.append(path)

        self.assertEqual(missing, [])

    def test_prompt_contracts_share_common_training_rules_without_addendum_duplication(self) -> None:
        from scripts import build_capability_map_data

        data = build_capability_map_data.build_data()
        common_path = "agents/COMMON_PROMPT_CONTRACT.md"
        common_text = (PROJECT_ROOT / common_path).read_text(encoding="utf-8")
        common_rules = [
            "CAD 测试必须使用中文标注；图层名、文件名、Schema key 等技术名允许保留原文。",
            "落图前先选择不覆盖旧图形的测试画布，避免重叠用户已有图块。",
            "通过前必须回读 created handles，并说明 checked / not_checked。",
            "真实 CAD 测试默认只写 CODEX_PREVIEW，不保存 DWG，不污染正式图层。",
        ]

        self.assertTrue((PROJECT_ROOT / common_path).is_file())
        for phrase in ("截图编排", "target_handles", "repair_plan", "PrintWindow", "visual_aid_only"):
            self.assertIn(phrase, common_text)
        for contract in data["promptContracts"]:
            source_paths = {source_ref.get("path") for source_ref in contract.get("sourceRefs", [])}
            self.assertIn(common_path, source_paths, contract["agentId"])

        duplicated: list[str] = []
        for prompt_path in PROJECT_ROOT.glob("agents/**/prompt_addendum.md"):
            text = prompt_path.read_text(encoding="utf-8")
            for rule in common_rules:
                if rule in text:
                    duplicated.append(f"{prompt_path.relative_to(PROJECT_ROOT).as_posix()}::{rule}")

        self.assertEqual(duplicated, [])

    def test_workbench_data_declares_sync_boundary(self) -> None:
        from scripts import build_capability_map_data

        data = build_capability_map_data.build_data()
        sync = data.get("workbenchSync", {})

        self.assertEqual(sync.get("mode"), "static_snapshot")
        self.assertIn("scripts\\sync_training_workbench.py", sync.get("recommendedCommand", ""))
        self.assertEqual(sync.get("launcher"), "start_training_workbench.bat")
        self.assertIn("generatedAfterCoverage", sync)

    def test_workbench_data_declares_portable_training_evidence_status(self) -> None:
        from scripts import build_capability_map_data

        data = build_capability_map_data.build_data()
        summary = data.get("trainingSourceSummary", {})

        self.assertEqual(summary.get("schemaVersion"), "training-source-summary/v1")
        self.assertEqual(summary.get("localAcceptedTrainingProgramCount"), 31)
        self.assertEqual(summary.get("localFullyCompleteProgramCount"), 31)
        self.assertGreater(summary.get("archivedTrainingAcceptanceReportCount", 0), 0)
        self.assertEqual(summary.get("activeTrainingAcceptanceReportCount"), 1)
        self.assertEqual(summary.get("recommendationCode"), "local_training_evidence_available")
        self.assertIn("不是浏览器缓存", summary.get("portableEvidencePolicy", ""))
        self.assertIn("不需要重新训练", summary.get("recommendedAction", ""))
        self.assertIn("output/training_queues/**", summary.get("restorePaths", []))

    def test_workbench_v3_flightdeck_contract_declared(self) -> None:
        from scripts import build_capability_map_data

        data = build_capability_map_data.build_data()
        v3 = data.get("workbenchV3", {})
        command_center = v3.get("views", {}).get("commandCenter", {})
        source_registry = v3.get("facts", {}).get("sourceRegistry", [])
        gateboard = command_center.get("gateboard", [])
        candidates = command_center.get("nextTrainingCandidates", [])
        source_policy = v3.get("sourcePolicy", {})

        self.assertEqual(data.get("schemaVersion"), 2)
        self.assertEqual(v3.get("schemaVersion"), "workbench-data-contract/v3-draft")
        self.assertTrue(source_policy.get("derivedOnly"))
        self.assertIn("capability-map-data.js", source_policy.get("derivedArtifacts", []))
        self.assertIn("docs/training/training-sources.json", source_policy.get("truthSources", []))
        self.assertGreaterEqual(len(source_registry), 1)
        self.assertTrue(any(source.get("role") == "derived" for source in source_registry))
        self.assertTrue(any(source.get("statusClass") == "archived_only" for source in source_registry))
        self.assertGreaterEqual(len(candidates), 3)
        self.assertTrue({"id", "label", "routeMode", "reason", "responsibleAgentIds", "evidenceRequired", "blockingConditions"}.issubset(candidates[0]))
        self.assertGreaterEqual(len(gateboard), 5)
        self.assertTrue({"snapshot_freshness", "source_health", "agent_check_status", "table_c_boundary"}.issubset({item.get("id") for item in gateboard}))
        self.assertIn("表 C", command_center.get("evidenceBoundary", ""))
        self.assertIn("不是事实源", command_center.get("derivedBoundary", ""))

    def test_workbench_v3_agent_graph_and_evidence_bundles_declared(self) -> None:
        from scripts import build_capability_map_data

        data = build_capability_map_data.build_data()
        v3 = data.get("workbenchV3", {})
        agent_graph = v3.get("views", {}).get("agentGraph", {})
        evidence_center = v3.get("views", {}).get("evidenceCenter", {})

        node_ids = {node.get("id") for node in agent_graph.get("nodes", [])}
        edge_types = {edge.get("edgeType") for edge in agent_graph.get("edges", [])}
        bundles = evidence_center.get("evidenceBundles", [])

        self.assertIn("agent:cad_designer", node_ids)
        self.assertIn("agent:pipeline_execute", node_ids)
        self.assertIn("prompt-contract:cad_designer", node_ids)
        self.assertTrue(any(str(node_id).startswith("gate:") for node_id in node_ids))
        self.assertTrue(any(str(node_id).startswith("source:") for node_id in node_ids))
        self.assertIn("responsible_for", edge_types)
        self.assertIn("has_prompt_contract", edge_types)
        self.assertIn("checked_against_source", edge_types)
        self.assertGreaterEqual(len(bundles), 3)
        self.assertTrue({"programId", "capabilityId", "status", "evidenceTypes", "sourceRefs", "notProven"}.issubset(bundles[0]))
        self.assertTrue(any("derived_snapshot" in bundle.get("evidenceTypes", []) for bundle in bundles))

    def test_agent_check_validates_workbench_v3_flightdeck_contract(self) -> None:
        from scripts import build_capability_map_data
        from scripts.run_training_workbench_agent_check import run_agent_check

        data_output = self.artifact_root() / "capability-map-data-v3-check.js"
        build_capability_map_data.write_data(data_output)

        report = run_agent_check(PROJECT_ROOT, data_path=data_output, html_path=PROJECT_ROOT / "capability-map.html")
        check_by_name = {item["name"]: item for item in report["checks"]}
        required = {
            "workbench_v3_declared",
            "workbench_v3_source_policy_derived_only",
            "workbench_v3_command_center_declared",
            "workbench_v3_next_candidates_declared",
            "workbench_v3_gateboard_declared",
            "workbench_v3_agent_graph_declared",
            "workbench_v3_evidence_bundles_declared",
            "html_flightdeck_overview_present",
        }

        self.assertTrue(required.issubset(check_by_name))
        for name in required:
            self.assertEqual(check_by_name[name]["status"], "pass", name)

    def test_workbench_snapshot_is_compact_and_omits_legacy_aliases(self) -> None:
        from scripts import build_capability_map_data
        from scripts.run_training_workbench_agent_check import load_workbench_data

        output_path = self.artifact_root() / "compact" / "capability-map-data.js"

        build_capability_map_data.write_data(output_path)

        text = output_path.read_text(encoding="utf-8")
        self.assertLessEqual(text.count("\n"), 1)
        data = load_workbench_data(output_path)
        self.assertIn("trainingPrograms", data)
        self.assertIn("agentProfiles", data)
        self.assertIn("trainingStageColumns", data)
        self.assertIn("tableCBoundary", data)
        self.assertIn("workbenchV3", data)
        for legacy_key in ("capabilities", "agents", "stages", "coverageSnapshot"):
            self.assertNotIn(legacy_key, data)

    def test_workbench_html_uses_normalized_data_instead_of_snapshot_duplication(self) -> None:
        html = (PROJECT_ROOT / "capability-map.html").read_text(encoding="utf-8")

        self.assertIn("function normalizeWorkbenchData", html)
        self.assertIn("const systemData = normalizeWorkbenchData(window.CAD_CAPABILITY_MAP_DATA || {})", html)
        self.assertIn('data-tab="overview"', html)
        self.assertIn('id="view-overview"', html)
        self.assertIn("renderCommandCenter", html)
        self.assertIn("commandCenter", html)
        self.assertIn("训练飞控台", html)
        self.assertIn("trainingSourceSummary", html)
        self.assertIn("训练证据同步", html)
        self.assertNotIn("systemData.trainingPrograms || systemData.capabilities", html)
        self.assertNotIn("systemData.agentProfiles || systemData.agents", html)
        self.assertNotIn("systemData.trainingStageColumns || systemData.stages", html)
        self.assertNotIn("systemData.tableCBoundary || systemData.coverageSnapshot", html)

    def test_training_source_manifest_declares_fact_sources_and_derived_snapshots(self) -> None:
        from scripts import build_capability_map_data

        data = build_capability_map_data.build_data()
        sources = {source["id"]: source for source in data.get("trainingSources", [])}

        self.assertEqual(
            sources["cad-foundation-first-10-unsupervised-10-chinese-report"]["role"],
            "fact_source",
        )
        self.assertEqual(
            sources["cad-foundation-first-10-unsupervised-10-chinese-report"]["kind"],
            "training_acceptance_report",
        )
        self.assertEqual(sources["agent-learning-ledger"]["kind"], "training_learning_ledger")
        self.assertEqual(sources["workbench-data-snapshot"]["role"], "derived")
        self.assertIn("不是事实源", sources["workbench-data-snapshot"]["desc"])

    def test_designer_agent_growth_path_declared(self) -> None:
        from scripts import build_capability_map_data

        data = build_capability_map_data.build_data()
        designer = data.get("designerAgent", {})
        growth_stages = data.get("growthStages", [])
        foundation_courses = data.get("foundationCourses", [])
        agent_ids = {agent["id"] for agent in data.get("agentProfiles", [])}
        course_ids = {course["id"] for course in foundation_courses}
        matrix_ids = {item["id"] for item in data.get("capabilityCatalog", [])}

        self.assertEqual(designer.get("id"), "cad_designer")
        self.assertIn("cad_designer", agent_ids)
        self.assertGreaterEqual(len(growth_stages), 7)
        self.assertEqual(growth_stages[0]["id"], "foundation_operations")
        self.assertGreaterEqual(len(foundation_courses), 7)
        self.assertTrue({"cad-primitives", "cad-selection-edit", "cad-offset-trim"}.issubset(course_ids))
        self.assertTrue(course_ids.issubset(matrix_ids))
        self.assertIn("不提升表 C", designer.get("evidenceBoundary", ""))

    def test_training_plan_v2_has_large_scale_coverage(self) -> None:
        from scripts import build_capability_map_data

        data = build_capability_map_data.build_data()
        catalog = data.get("capabilityCatalog", [])
        programs = data.get("trainingPrograms", [])
        ids = [item["id"] for item in catalog]
        group_counts = data.get("designerAgent", {}).get("capabilityPassport", {}).get("groupCounts", {})

        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(programs), len(catalog))
        self.assertGreaterEqual(len(programs), 180)
        self.assertGreaterEqual(group_counts.get("CAD 基础操作", 0), 30)
        self.assertGreaterEqual(group_counts.get("基础家具", 0), 40)
        self.assertGreaterEqual(group_counts.get("储位家具", 0), 25)
        self.assertGreaterEqual(group_counts.get("厨卫对象", 0), 30)
        self.assertGreaterEqual(group_counts.get("基础绘图", 0), 35)
        self.assertGreaterEqual(group_counts.get("标注表达", 0), 25)

        required_ids = {
            "furniture-sectional-sofa",
            "furniture-extendable-dining-table",
            "storage-swing-wardrobe",
            "storage-kitchen-base-cabinet",
            "kitchen-work-triangle",
            "bathroom-clearance",
            "drawing-demolition-plan",
            "drawing-rcp-plan",
            "annotation-ffe-schedule",
            "annotation-checked-not-checked",
        }
        self.assertTrue(required_ids.issubset(set(ids)))

    def test_training_batches_and_checker_skeleton_declared(self) -> None:
        from scripts import build_capability_map_data

        data = build_capability_map_data.build_data()
        programs = {program["capabilityId"] for program in data.get("trainingPrograms", [])}
        batches = data.get("trainingBatches", [])
        checkers = data.get("validationCheckers", [])
        batch_ids = {batch["id"] for batch in batches}
        checker_ids = {checker["id"] for checker in checkers}

        self.assertGreaterEqual(len(batches), 6)
        self.assertGreaterEqual(len(checkers), 8)
        self.assertEqual(len(batch_ids), len(batches))
        self.assertEqual(len(checker_ids), len(checkers))
        self.assertIn("batch-foundation-production-hygiene", batch_ids)
        self.assertIn("batch-cross-sheet-delivery-closure", batch_ids)
        self.assertIn("checker-clearance-collision", checker_ids)
        self.assertIn("checker-cross-sheet-consistency", checker_ids)

        for batch in batches:
            self.assertNotIn("天", batch.get("label", ""))
            self.assertNotIn("周", batch.get("label", ""))
            self.assertTrue(set(batch.get("programIds", [])).issubset(programs))
            self.assertTrue(set(batch.get("dependsOn", [])).issubset(batch_ids))
            self.assertTrue(set(batch.get("checkerIds", [])).issubset(checker_ids))
            self.assertIn("evidenceRequired", batch)
            self.assertIn("passBoundary", batch)

        for checker in checkers:
            self.assertEqual(checker.get("implementationStatus"), "skeleton")
            self.assertIn("not yet a CAD proof", checker.get("evidenceBoundary", ""))

    def test_foundation_programs_do_not_require_asset_libraries(self) -> None:
        from scripts import build_capability_map_data

        data = build_capability_map_data.build_data()
        programs = [
            program
            for program in data.get("trainingPrograms", [])
            if program.get("group") == "CAD 基础操作"
        ]

        self.assertGreaterEqual(len(programs), 30)
        for program in programs:
            asset_states = program.get("assetStates", {})
            self.assertEqual(asset_states.get("raw", {}).get("state"), "not_applicable", program["capabilityId"])
            self.assertEqual(asset_states.get("raw", {}).get("label"), "不适用", program["capabilityId"])
            self.assertIn("不需要标准图块", asset_states.get("raw", {}).get("note", ""))
            self.assertEqual(asset_states.get("system", {}).get("state"), "not_applicable", program["capabilityId"])
            self.assertEqual(asset_states.get("system", {}).get("label"), "不适用", program["capabilityId"])
            self.assertIn("不沉淀为自产资产", asset_states.get("system", {}).get("note", ""))
            self.assertIn("handles", " ".join(program.get("successCriteria", [])))
            self.assertIn("bbox", " ".join(program.get("successCriteria", [])))

        html = (PROJECT_ROOT / "capability-map.html").read_text(encoding="utf-8")
        self.assertIn("not_applicable", html)
        self.assertIn("不适用", html)

    def test_workbench_html_defaults_to_collapsing_fully_completed_plans(self) -> None:
        html = (PROJECT_ROOT / "capability-map.html").read_text(encoding="utf-8")

        self.assertIn("showFullyCompletePlans: false", html)
        self.assertIn("isFullyCompleteProgram", html)
        self.assertIn("showCompletePlanToggle", html)
        self.assertIn("已折叠", html)

    def test_training_acceptance_report_marks_foundation_program_done(self) -> None:
        from scripts import build_capability_map_data

        report_path = self.artifact_root() / "accepted_foundation_report.json"
        report_path.write_text(
            json.dumps(
                {
                    "status": "pass",
                    "generated_at": "2026-06-01T00:00:00Z",
                    "queueId": "cad-foundation-first-10",
                    "mode": "unsupervised",
                    "items": [
                        {
                            "capabilityId": "cad-primitives",
                            "status": "pass",
                            "handle_count": 14,
                            "readback_count": 14,
                        }
                    ],
                    "checks": [
                        {"name": "all_10_items_generated", "status": "pass"},
                        {"name": "persistent_handle_readback", "status": "pass"},
                        {"name": "preview_layer_only", "status": "pass"},
                        {"name": "dwg_not_saved", "status": "pass"},
                        {"name": "chinese_labels", "status": "pass"},
                    ],
                    "visual_self_check": {"status": "pass"},
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        original_paths = build_capability_map_data.TRAINING_ACCEPTANCE_REPORT_PATHS
        original_ledger = build_capability_map_data.TRAINING_LEARNING_LEDGER_PATH
        try:
            build_capability_map_data.TRAINING_ACCEPTANCE_REPORT_PATHS = [report_path]
            build_capability_map_data.TRAINING_LEARNING_LEDGER_PATH = self.artifact_root() / "missing_learning_ledger.json"
            data = build_capability_map_data.build_data()
        finally:
            build_capability_map_data.TRAINING_ACCEPTANCE_REPORT_PATHS = original_paths
            build_capability_map_data.TRAINING_LEARNING_LEDGER_PATH = original_ledger

        program = next(item for item in data["trainingPrograms"] if item["capabilityId"] == "cad-primitives")
        self.assertEqual(program["stageState"]["id"], "user_feedback_pass")
        self.assertEqual(program["assetStates"]["trained"]["state"], "evidence")
        self.assertEqual(program["trainingAcceptance"]["readbackCount"], 14)
        self.assertFalse(program["isFullyComplete"])
        self.assertEqual(data["trainingPlanVisibility"]["defaultMode"], "hide_fully_completed")
        self.assertEqual(data["trainingPlanVisibility"]["fullyCompletedCount"], 0)
        self.assertIn("plainLanguageSummary", program["trainingAcceptance"])
        self.assertIn("中文", program["trainingAcceptance"]["plainLanguageSummary"])
        self.assertIn("CODEX_PREVIEW", program["trainingAcceptance"]["plainLanguageSummary"])
        visible_notes = " ".join(
            [
                program["stageState"]["note"],
                program["assetStates"]["trained"]["note"],
            ]
        )
        self.assertNotIn(".json", visible_notes)
        self.assertNotIn("output/", visible_notes)

    def test_workbench_data_links_acceptance_to_agent_learning_promotion(self) -> None:
        from scripts import build_capability_map_data

        report_path = self.artifact_root() / "accepted_foundation_with_learning.json"
        ledger_path = self.artifact_root() / "agent_learning_ledger.json"
        report_path.write_text(
            json.dumps(
                {
                    "status": "pass",
                    "generated_at": "2026-06-01T00:00:00Z",
                    "queueId": "cad-foundation-first-10",
                    "mode": "unsupervised",
                    "items": [
                        {
                            "capabilityId": "cad-primitives",
                            "status": "pass",
                            "handle_count": 14,
                            "readback_count": 14,
                        }
                    ],
                    "checks": [
                        {"name": "all_10_items_generated", "status": "pass"},
                        {"name": "persistent_handle_readback", "status": "pass"},
                        {"name": "preview_layer_only", "status": "pass"},
                        {"name": "dwg_not_saved", "status": "pass"},
                        {"name": "chinese_labels", "status": "pass"},
                    ],
                    "visual_self_check": {"status": "pass"},
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        ledger_path.write_text(
            json.dumps(
                {
                    "status": "promoted",
                    "sourceReportPaths": [str(report_path.relative_to(PROJECT_ROOT)).replace("\\", "/")],
                    "acceptedItemCount": 1,
                    "promotedAgentCount": 1,
                    "agentUpdates": [
                        {
                            "agentId": "cad_designer",
                            "learningState": "prompt_updated",
                            "acceptedCapabilities": ["cad-primitives"],
                            "sourceRefs": ["agents/cad_designer/agent.json", "agents/cad_designer/rules.md"],
                            "promptUpdateSummary": ["CAD 测试必须使用中文标注。"],
                        }
                    ],
                    "promotionGate": {
                        "schemaVersion": 1,
                        "promotionLevel": "systemized",
                        "decisions": {
                            "updateTrainingSource": {"required": True, "status": "ready"},
                            "updateWorkbench": {"required": True, "status": "required"},
                            "updateBaseRules": {"required": False, "status": "not_required"},
                            "updateTaskRules": {"required": False, "status": "not_required"},
                            "updateAgentCalibration": {"required": True, "status": "ready"},
                            "updateChecker": {"required": False, "status": "not_required"},
                            "retestOriginalTask": {"required": False, "status": "not_required"},
                        },
                    },
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        original_paths = build_capability_map_data.TRAINING_ACCEPTANCE_REPORT_PATHS
        original_ledger = build_capability_map_data.TRAINING_LEARNING_LEDGER_PATH
        try:
            build_capability_map_data.TRAINING_ACCEPTANCE_REPORT_PATHS = [report_path]
            build_capability_map_data.TRAINING_LEARNING_LEDGER_PATH = ledger_path
            data = build_capability_map_data.build_data()
        finally:
            build_capability_map_data.TRAINING_ACCEPTANCE_REPORT_PATHS = original_paths
            build_capability_map_data.TRAINING_LEARNING_LEDGER_PATH = original_ledger

        program = next(item for item in data["trainingPrograms"] if item["capabilityId"] == "cad-primitives")
        contract = next(item for item in data["promptContracts"] if item["agentId"] == "cad_designer")

        self.assertEqual(data["trainingLearning"]["status"], "promoted")
        self.assertEqual(program["stageState"]["id"], "systemized")
        self.assertEqual(program["stageState"]["rank"], 4)
        self.assertEqual(program["stageState"]["label"], "已沉淀")
        self.assertTrue(program["isFullyComplete"])
        self.assertEqual(data["trainingPlanVisibility"]["fullyCompletedCount"], 1)
        self.assertIn("learningPromotion.status=promoted", data["trainingPlanVisibility"]["completionRule"])
        self.assertEqual(program["learningPromotion"]["status"], "promoted")
        self.assertEqual(program["learningPromotion"]["promotionGate"]["promotionLevel"], "systemized")
        self.assertEqual(program["learningPromotion"]["promotedAgentCount"], 1)
        self.assertIn("plainLanguageSummary", program["learningPromotion"])
        self.assertIn("责任智能体", program["learningPromotion"]["plainLanguageSummary"])
        self.assertEqual(program["assetStates"]["knowledge"]["state"], "evidence")
        self.assertIn("常识", program["assetStates"]["knowledge"]["note"])
        self.assertTrue(any(ref["path"] == "agents/cad_designer/rules.md" for ref in contract["sourceRefs"]))

    def test_agent_check_rejects_systemized_training_without_promotion_gate(self) -> None:
        from scripts import build_capability_map_data
        from scripts.run_training_workbench_agent_check import run_agent_check

        report_path = self.artifact_root() / "accepted_without_gate.json"
        ledger_path = self.artifact_root() / "agent_learning_ledger_without_gate.json"
        report_path.write_text(
            json.dumps(
                {
                    "status": "pass",
                    "generated_at": "2026-06-01T00:00:00Z",
                    "queueId": "cad-foundation-first-10",
                    "mode": "unsupervised",
                    "items": [{"capabilityId": "cad-primitives", "status": "pass", "handle_count": 1, "readback_count": 1}],
                    "checks": [
                        {"name": "all_items_generated", "status": "pass"},
                        {"name": "persistent_handle_readback", "status": "pass"},
                        {"name": "preview_layer_only", "status": "pass"},
                        {"name": "dwg_not_saved", "status": "pass"},
                        {"name": "chinese_labels", "status": "pass"},
                    ],
                    "visual_self_check": {"status": "pass"},
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        ledger_path.write_text(
            json.dumps(
                {
                    "status": "promoted",
                    "sourceReportPaths": [str(report_path.relative_to(PROJECT_ROOT)).replace("\\", "/")],
                    "acceptedItemCount": 1,
                    "promotedAgentCount": 1,
                    "agentUpdates": [
                        {
                            "agentId": "cad_designer",
                            "learningState": "prompt_updated",
                            "acceptedCapabilities": ["cad-primitives"],
                            "sourceRefs": ["agents/cad_designer/agent.json"],
                            "promptUpdateSummary": [],
                        }
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        data_output = self.artifact_root() / "capability-map-data-missing-gate.js"
        original_paths = build_capability_map_data.TRAINING_ACCEPTANCE_REPORT_PATHS
        original_ledger = build_capability_map_data.TRAINING_LEARNING_LEDGER_PATH
        try:
            build_capability_map_data.TRAINING_ACCEPTANCE_REPORT_PATHS = [report_path]
            build_capability_map_data.TRAINING_LEARNING_LEDGER_PATH = ledger_path
            build_capability_map_data.write_data(data_output)
        finally:
            build_capability_map_data.TRAINING_ACCEPTANCE_REPORT_PATHS = original_paths
            build_capability_map_data.TRAINING_LEARNING_LEDGER_PATH = original_ledger

        report = run_agent_check(PROJECT_ROOT, data_path=data_output, html_path=PROJECT_ROOT / "capability-map.html")
        check_by_name = {item["name"]: item for item in report["checks"]}

        self.assertEqual(check_by_name["systemized_training_has_promotion_gate"]["status"], "fail")
        self.assertIn("cad-primitives", check_by_name["systemized_training_has_promotion_gate"]["detail"])

    def test_agent_check_cli_blocks_missing_training_sources_in_generated_snapshot(self) -> None:
        from scripts import build_capability_map_data

        data_output = self.artifact_root() / "capability-map-data-agent-check-missing-sources.js"
        output = self.artifact_root() / "agent_check_missing_sources.json"
        build_capability_map_data.write_data(data_output)
        missing_path = "output/test_artifacts/training_workbench_sync_tests/missing_fact_source.json"
        snapshot = data_output.read_text(encoding="utf-8")
        payload = snapshot.removeprefix("window.CAD_CAPABILITY_MAP_DATA = ").rstrip(";\n")
        data = json.loads(payload)
        data.setdefault("trainingSources", []).append(
            {
                "id": "fixture-missing-fact-source",
                "kind": "training_learning_ledger",
                "role": "fact_source",
                "path": missing_path,
                "status": "active",
                "owner": "test",
                "desc": "Fixture-only missing source.",
            }
        )
        data_output.write_text(
            f"window.CAD_CAPABILITY_MAP_DATA = {json.dumps(data, ensure_ascii=False, separators=(',', ':'))};\n",
            encoding="utf-8",
        )
        completed = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "run_training_workbench_agent_check.py"),
                "--data",
                str(data_output),
                "--output",
                str(output),
            ],
            cwd=PROJECT_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )

        self.assertEqual(completed.returncode, 1)
        report = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "fail")
        check_by_name = {item["name"]: item for item in report["checks"]}
        self.assertEqual(check_by_name["training_source_paths_exist"]["status"], "fail")
        self.assertIn(
            missing_path,
            check_by_name["training_source_paths_exist"]["detail"],
        )

    def test_agent_check_cli_passes_when_training_source_paths_exist(self) -> None:
        from scripts import build_capability_map_data

        data_output = self.artifact_root() / "capability-map-data-agent-check.js"
        output = self.artifact_root() / "agent_check.json"
        build_capability_map_data.write_data(data_output)
        self.rewrite_training_sources_to_fixture_files(data_output)
        completed = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "run_training_workbench_agent_check.py"),
                "--data",
                str(data_output),
                "--output",
                str(output),
            ],
            cwd=PROJECT_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["summary"]["failed_check_count"], 0)
        check_names = {item["name"] for item in report["checks"]}
        self.assertIn("designer_agent_declared", check_names)
        self.assertIn("foundation_courses_declared", check_names)
        self.assertIn("training_batches_declared", check_names)
        self.assertIn("validation_checkers_declared", check_names)
        self.assertIn("common_prompt_contract_referenced", check_names)
        self.assertIn("screenshot_orchestration_rules_in_common_contract", check_names)
        self.assertIn("prompt_addenda_do_not_duplicate_common_rules", check_names)
        self.assertIn("training_source_summary_declared", check_names)
        self.assertIn("training_source_summary_portable_policy_declared", check_names)
        self.assertIn("html_training_source_sync_present", check_names)
        self.assertIn("systemized_training_has_promotion_gate", check_names)
        self.assertIn("promotion_gate_decisions_complete", check_names)

    def test_sync_cli_refreshes_data_when_training_sources_are_closed(self) -> None:
        temp_path = self.artifact_root() / "sync_cli"
        temp_path.mkdir(parents=True, exist_ok=True)
        data_output = temp_path / "capability-map-data.js"
        output_dir = temp_path / "sync"
        completed = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "sync_training_workbench.py"),
                "--skip-coverage",
                "--data-output",
                str(data_output),
                "--output-dir",
                str(output_dir),
            ],
            cwd=PROJECT_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(data_output.is_file())
        report = json.loads((output_dir / "training_workbench_sync_report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["agent_check"]["status"], "pass")
        common_text = (PROJECT_ROOT / "agents" / "COMMON_PROMPT_CONTRACT.md").read_text(encoding="utf-8")
        self.assertIn("modelAssistedDecision", common_text)
        self.assertIn("modelBackedVisualAcceptance", common_text)
        self.assertIn("modelProviderStatus", common_text)
        self.assertIn("modelBackedRepairPlan", common_text)
        self.assertIn("proposal_only", common_text)
        check_by_name = {item["name"]: item for item in report["agent_check"]["checks"]}
        self.assertEqual(check_by_name["training_source_paths_exist"]["status"], "pass")
        self.assertIn("promotionGate", report["learning_promotion"])

    def test_launcher_bat_runs_sync_before_serving_page(self) -> None:
        launcher = PROJECT_ROOT / "start_training_workbench.bat"
        self.assertTrue(launcher.is_file())
        text = launcher.read_text(encoding="utf-8")
        self.assertIn("scripts\\sync_training_workbench.py", text)
        self.assertIn("http.server", text)
        self.assertIn("capability-map.html", text)


if __name__ == "__main__":
    unittest.main()
