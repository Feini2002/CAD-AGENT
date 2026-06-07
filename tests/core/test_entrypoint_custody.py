from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import PROJECT_ROOT, temporary_artifact_dir


class EntrypointCustodyManifestTests(unittest.TestCase):
    def test_manifest_entries_are_schema_valid_and_workflow_routes_are_registered(self) -> None:
        from core.entrypoint_custody.manifest import load_entrypoint_manifest, validate_manifest_entry
        from core.entrypoint_custody.audit import build_entrypoint_custody_audit

        manifest = load_entrypoint_manifest(PROJECT_ROOT / "config" / "entrypoint_custody_manifest.json")
        entries = manifest["entrypointMap"]
        self.assertIn("scripts/run_cad_foundation_remaining_training.py", entries)
        self.assertIn("core.execution.execute_plan:execute_plan_file", entries)

        blocked = []
        for entry in entries.values():
            blocked.extend(finding for finding in validate_manifest_entry(entry) if finding["severity"] == "blocked")
        self.assertEqual(blocked, [])

        audit = build_entrypoint_custody_audit(PROJECT_ROOT)
        blocked_codes = [finding["code"] for finding in audit["findings"] if finding["severity"] == "blocked"]
        self.assertNotIn("workflow_route_entrypoint_unregistered", blocked_codes)
        self.assertNotIn("cad_workflow_route_not_lease_controlled", blocked_codes)


class EntrypointRuntimeGuardTests(unittest.TestCase):
    def test_runtime_guard_allows_valid_lease_and_blocks_missing_lease(self) -> None:
        from core.entrypoint_custody.guard import evaluate_entrypoint_custody, issue_custody_lease

        argv = ["scripts/run_cad_foundation_remaining_training.py", "--only", "cad-hatch-boundary", "--replay-mode", "growth_replay"]
        lease = issue_custody_lease(
            entrypoint="scripts/run_cad_foundation_remaining_training.py",
            argv=argv,
            run_id="run-1",
            task_id="task-1",
            permission_class="cad_preview_write",
            allowed_write_scope=["CODEX_PREVIEW", "output/training_queues"],
            may_write_cad=True,
            required_gates_satisfied=[
                "utf8_preflight",
                "training_scope_gate",
                "adaptive_training_route",
                "promotion_gate",
                "data_bloat_governance",
            ],
            generated_at="2026-06-07T00:00:00Z",
        )

        allowed = evaluate_entrypoint_custody(
            entrypoint="scripts/run_cad_foundation_remaining_training.py",
            argv=argv,
            requested_write_scope=["CODEX_PREVIEW"],
            requested_permission_class="cad_preview_write",
            custody_lease=lease,
            run_id="run-1",
            task_id="task-1",
            target_layer="CODEX_PREVIEW",
            now="2026-06-07T00:01:00Z",
        )
        self.assertEqual(allowed["custodyDecision"], "allowed", allowed)
        self.assertTrue(allowed["leaseValidated"])

        missing = evaluate_entrypoint_custody(
            entrypoint="scripts/run_cad_foundation_remaining_training.py",
            argv=argv,
            requested_write_scope=["CODEX_PREVIEW"],
            requested_permission_class="cad_preview_write",
            run_id="run-1",
            task_id="task-1",
        )
        self.assertEqual(missing["reasonCode"], "blocked_missing_custody_lease")

    def test_runtime_guard_blocks_argv_scope_save_layer_kill_switch_and_denylist(self) -> None:
        from core.entrypoint_custody.guard import evaluate_entrypoint_custody, issue_custody_lease

        argv = ["scripts/execute_plan.py", "plan.json", "--preview-only"]
        lease = issue_custody_lease(
            entrypoint="scripts/execute_plan.py",
            argv=argv,
            run_id="run-2",
            task_id="task-2",
            permission_class="cad_preview_write",
            allowed_write_scope=["CODEX_PREVIEW"],
            may_write_cad=True,
            required_gates_satisfied=["utf8_preflight", "validate_plan", "dry_run_plan"],
            generated_at="2026-06-07T00:00:00Z",
        )

        mismatch = evaluate_entrypoint_custody(
            entrypoint="scripts/execute_plan.py",
            argv=argv + ["--extra"],
            requested_write_scope=["CODEX_PREVIEW"],
            requested_permission_class="cad_preview_write",
            custody_lease=lease,
            now="2026-06-07T00:01:00Z",
        )
        self.assertEqual(mismatch["reasonCode"], "blocked_lease_argv_hash_mismatch")

        scope = evaluate_entrypoint_custody(
            entrypoint="scripts/execute_plan.py",
            argv=argv,
            requested_write_scope=["FORMAL_LAYER"],
            requested_permission_class="cad_preview_write",
            custody_lease=lease,
            now="2026-06-07T00:01:00Z",
        )
        self.assertEqual(scope["reasonCode"], "blocked_write_scope_exceeds_manifest")

        save = evaluate_entrypoint_custody(
            entrypoint="scripts/execute_plan.py",
            argv=argv,
            requested_write_scope=["CODEX_PREVIEW"],
            requested_permission_class="cad_preview_write",
            custody_lease=lease,
            may_save_current_dwg_requested=True,
            now="2026-06-07T00:01:00Z",
        )
        self.assertEqual(save["reasonCode"], "blocked_current_dwg_save")

        layer = evaluate_entrypoint_custody(
            entrypoint="scripts/execute_plan.py",
            argv=argv,
            requested_write_scope=["CODEX_PREVIEW"],
            requested_permission_class="cad_preview_write",
            custody_lease=lease,
            target_layer="WALL",
            now="2026-06-07T00:01:00Z",
        )
        self.assertEqual(layer["reasonCode"], "blocked_non_preview_target_layer")

        kill = evaluate_entrypoint_custody(
            entrypoint="scripts/execute_plan.py",
            argv=argv,
            requested_write_scope=["CODEX_PREVIEW"],
            requested_permission_class="cad_preview_write",
            custody_lease=lease,
            kill_switch={
                "globalEntrypointExecutionDisabled": True,
                "disabledEntrypoints": [],
                "disabledReason": "maintenance",
            },
            now="2026-06-07T00:01:00Z",
        )
        self.assertEqual(kill["reasonCode"], "blocked_global_kill_switch")

        deny = evaluate_entrypoint_custody(
            entrypoint="scripts/run_cad_foundation_remaining_training.py",
            argv=[
                "scripts/run_cad_foundation_remaining_training.py",
                "--all-31",
                "--replay-mode",
                "smoke_replay",
            ],
            denylist={
                "denyPatterns": [
                    {
                        "entrypoint": "scripts/run_cad_foundation_remaining_training.py",
                        "requiredArgs": ["--all-31"],
                        "deniedArgs": ["smoke_replay"],
                        "reasonCode": "blocked_all_31_smoke_replay_without_explicit_smoke",
                    }
                ]
            },
        )
        self.assertEqual(deny["reasonCode"], "blocked_all_31_smoke_replay_without_explicit_smoke")

    def test_runtime_guard_enforces_lease_permission_flags(self) -> None:
        from core.entrypoint_custody.guard import evaluate_entrypoint_custody, issue_custody_lease

        argv = ["scripts/execute_plan.py", "plan.json", "--preview-only"]
        cad_denied_lease = issue_custody_lease(
            entrypoint="scripts/execute_plan.py",
            argv=argv,
            run_id="run-3",
            task_id="task-3",
            permission_class="diagnostic_only",
            allowed_write_scope=["CODEX_PREVIEW"],
            may_write_cad=False,
            required_gates_satisfied=["utf8_preflight", "validate_plan", "dry_run_plan"],
            generated_at="2026-06-07T00:00:00Z",
        )

        cad = evaluate_entrypoint_custody(
            entrypoint="scripts/execute_plan.py",
            argv=argv,
            requested_write_scope=["CODEX_PREVIEW"],
            requested_permission_class="cad_preview_write",
            custody_lease=cad_denied_lease,
            now="2026-06-07T00:01:00Z",
        )
        self.assertEqual(cad["reasonCode"], "blocked_lease_permission_class_mismatch")

        argv_training = [
            "scripts/run_cad_foundation_remaining_training.py",
            "--only",
            "cad-layer-lineweight-standard",
            "--explicit-smoke",
        ]
        training_denied_lease = issue_custody_lease(
            entrypoint="scripts/run_cad_foundation_remaining_training.py",
            argv=argv_training,
            run_id="run-4",
            task_id="task-4",
            permission_class="cad_preview_write",
            allowed_write_scope=["CODEX_PREVIEW", "output/training_queues"],
            may_write_cad=True,
            may_write_training_fact_source=False,
            required_gates_satisfied=[
                "utf8_preflight",
                "training_scope_gate",
                "adaptive_training_route",
                "promotion_gate",
                "data_bloat_governance",
            ],
            generated_at="2026-06-07T00:00:00Z",
        )
        training = evaluate_entrypoint_custody(
            entrypoint="scripts/run_cad_foundation_remaining_training.py",
            argv=argv_training,
            requested_write_scope=["output/training_queues"],
            requested_permission_class="cad_preview_write",
            custody_lease=training_denied_lease,
            may_write_training_fact_source_requested=True,
            now="2026-06-07T00:01:00Z",
        )
        self.assertEqual(training["reasonCode"], "blocked_lease_training_fact_write_not_granted")

        registry_denied_lease = issue_custody_lease(
            entrypoint="scripts/sediment_system_asset.py",
            argv=["scripts/sediment_system_asset.py", "--verify"],
            run_id="run-5",
            task_id="task-5",
            permission_class="asset_registry_write",
            allowed_write_scope=["libraries/system_library"],
            may_write_cad=False,
            may_write_registry=False,
            required_gates_satisfied=[
                "encoding_preflight",
                "source_spec_precise",
                "asset_governor",
                "native_visible_evidence_or_candidate_boundary",
            ],
            generated_at="2026-06-07T00:00:00Z",
        )
        registry = evaluate_entrypoint_custody(
            entrypoint="scripts/sediment_system_asset.py",
            argv=["scripts/sediment_system_asset.py", "--verify"],
            requested_write_scope=["libraries/system_library"],
            requested_permission_class="asset_registry_write",
            custody_lease=registry_denied_lease,
            may_write_registry_requested=True,
            now="2026-06-07T00:01:00Z",
        )
        self.assertEqual(registry["reasonCode"], "blocked_lease_registry_write_not_granted")


class WorkflowDispatchCustodyTests(unittest.TestCase):
    def test_dispatch_includes_registered_custody_summary_and_blocks_unregistered_route(self) -> None:
        from core.orchestrator.request_context import build_request_context
        from core.orchestrator.workflow_dispatch import DISPATCH_BLOCKED, orchestrate_request, resolve_workflow_route

        context = build_request_context(
            context_id="req-custody-route",
            request_kind="draw",
            user_request="执行计划",
            available_inputs=["cad_plan"],
            input_paths={"cad_plan": "examples/plans/insert_block_alpha_test.json"},
            allow_cad=True,
        )
        dispatch = resolve_workflow_route(context)
        custody = dispatch["entrypointCustody"]
        self.assertTrue(custody["registered"])
        self.assertTrue(custody["requiresLease"])

        routes_table = {
            "routes": [
                {
                    "workflow_id": "bad-route",
                    "request_kinds": ["draw"],
                    "required_any_inputs": ["cad_plan"],
                    "entrypoint": "scripts/not_registered.py",
                    "requires_cad": False,
                    "priority": 1,
                }
            ]
        }
        report = orchestrate_request(context, routes_table=routes_table)
        self.assertEqual(report["workflow_dispatch"]["status"], DISPATCH_BLOCKED)
        self.assertIn("entrypoint custody blocked", report["workflow_dispatch"]["reason"])


class TrainingReplayCustodyTests(unittest.TestCase):
    def test_cli_replay_auto_blocks_all_31_without_profile_or_explicit_smoke(self) -> None:
        from scripts.run_cad_foundation_remaining_training import resolve_cli_replay_mode

        blocked = resolve_cli_replay_mode(
            batch_preset="all-31",
            requested_replay_mode="auto",
            profile_source=None,
        )
        self.assertEqual(blocked["status"], "blocked")
        self.assertEqual(blocked["reasonCode"], "all_31_auto_requires_profile_source_or_explicit_smoke")

        smoke = resolve_cli_replay_mode(
            batch_preset="all-31",
            requested_replay_mode="auto",
            profile_source=None,
            explicit_smoke=True,
        )
        self.assertEqual(smoke["status"], "pass")
        self.assertEqual(smoke["replayMode"], "smoke_replay")

        direct_smoke = resolve_cli_replay_mode(
            batch_preset="all-31",
            requested_replay_mode="smoke_replay",
            profile_source=None,
            explicit_smoke=False,
        )
        self.assertEqual(direct_smoke["reasonCode"], "all_31_cannot_use_smoke_replay_without_explicit_smoke_flag")

    def test_growth_replay_without_profile_source_blocks_before_cad_write(self) -> None:
        from core.training.foundation_batch_training import run_foundation_remaining_training_batch
        from core.verification.fake_cad_driver import FakeCadDriver
        from scripts import build_capability_map_data

        driver = FakeCadDriver()
        with temporary_artifact_dir("growth_replay_profile_required") as root:
            report = run_foundation_remaining_training_batch(
                programs=build_capability_map_data.build_data()["trainingPrograms"],
                driver=driver,
                output_dir=root,
                generated_at="2026-06-07T00:00:00Z",
                capture_preview=False,
                selected_capability_ids=["cad-layer-lineweight-standard"],
                replay_mode="growth_replay",
                project_root=root,
            )
        self.assertEqual(report["status"], "blocked")
        self.assertEqual(report["blockedReason"], "profile_source_required_for_growth_or_standard_replay")
        self.assertEqual(report["created_handle_count"], 0)
        self.assertEqual(driver.snapshot_modelspace(layer="CODEX_PREVIEW"), [])

    def test_training_report_claim_audit_catches_smoke_and_default_profile_claims(self) -> None:
        from core.training.report_claim_audit import audit_training_report_claims

        with temporary_artifact_dir("training_claim_audit") as root:
            smoke = root / "smoke.json"
            smoke.write_text(
                json.dumps({"status": "pass", "replayMode": "smoke_replay", "passType": "growth_replay"}, ensure_ascii=False),
                encoding="utf-8",
            )
            growth = root / "growth.json"
            growth.write_text(
                json.dumps(
                    {
                        "status": "pass",
                        "replayMode": "growth_replay",
                        "passType": "growth_replay",
                        "capabilityProfile": {
                            "profileSource": {"status": "pass"},
                            "profiles": [{"capabilityId": "cad-layer-lineweight-standard", "status": "default"}],
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            audit = audit_training_report_claims(root, [root])
        codes = {finding["code"] for finding in audit["findings"]}
        self.assertIn("missing_smoke_only_pass_type", codes)
        self.assertIn("profile_default_used", codes)
        self.assertEqual(audit["status"], "blocked")


if __name__ == "__main__":
    unittest.main()
