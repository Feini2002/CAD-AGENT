from __future__ import annotations

from pathlib import Path
import unittest

from tests.helpers import temporary_artifact_dir


def _cad_completion_task() -> object:
    from core.contracts.vnext import TaskObject

    return TaskObject(
        task_id="task-phase8-adapter",
        task_kind="cad_preview_with_readback",
        user_intent="Expose Phase 8 completion state in the workbench.",
        target_scope={"scopeType": "fixture", "documentId": "none"},
        evidence_requirements=["real_cad_readback", "no_save_guard"],
    )


def _real_readback_package() -> object:
    from core.contracts.vnext import EvidenceItem, EvidencePackage

    return EvidencePackage(
        task_id="task-phase8-adapter",
        items=[
            EvidenceItem(
                kind="cad_readback",
                status="pass",
                backend="real_cad",
                readback_status="ok",
                cad_geometry_verified=True,
                metadata={"created_handles": ["H-001"]},
            ),
            EvidenceItem(
                kind="no_save_guard",
                status="pass",
                metadata={"savedCurrentDwg": False},
            ),
        ],
    )


class MutationTrapLedger:
    def __init__(self, records: list[object] | None = None) -> None:
        self._records = tuple(records or [])

    def records_for_task(self, task_id: str) -> tuple[object, ...]:
        return tuple(record for record in self._records if getattr(record, "task_id", "") == task_id)

    def append(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("adapter must not append ledger records")

    def overwrite(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("adapter must not overwrite ledger records")

    def delete(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("adapter must not delete ledger records")


class WorkbenchReadonlyAdapterTests(unittest.TestCase):
    def test_adapter_projects_workbench_projection_into_read_only_workbench_shape(self) -> None:
        from core.contracts.evidence_ledger import EvidenceLedgerRecord, evidence_package_content_hash
        from core.contracts.workbench_projection import build_workbench_projection
        from core.contracts.workbench_readonly_adapter import build_workbench_readonly_adapter

        task = _cad_completion_task()
        package = _real_readback_package()
        content_hash = evidence_package_content_hash(package)
        ledger = MutationTrapLedger(
            [
                EvidenceLedgerRecord(
                    ledger_id="ledger-readback",
                    task_id=task.task_id,
                    contract_id="contract-readback",
                    evidence_package_id="pkg-real-readback",
                    evidence_type="real_cad_readback",
                    producer="unit-test",
                    tool_card_id="legacy.readback",
                    verification_status="verified",
                    source_ref="output/phase8-adapter/readback.json",
                    content_hash=content_hash,
                ),
                EvidenceLedgerRecord(
                    ledger_id="ledger-no-save",
                    task_id=task.task_id,
                    contract_id="contract-no-save",
                    evidence_package_id="pkg-real-readback",
                    evidence_type="no_save_guard",
                    producer="unit-test",
                    tool_card_id="legacy.readback",
                    verification_status="verified",
                    source_ref="output/phase8-adapter/no-save.json",
                    content_hash=content_hash,
                ),
            ]
        )
        projection = build_workbench_projection(
            task=task,
            evidence_packages={"pkg-real-readback": package},
            ledger=ledger,
        )

        adapter = build_workbench_readonly_adapter(
            [projection],
            generated_at="2026-06-15T00:00:00+00:00",
        )

        self.assertEqual(adapter["schemaVersion"], "workbench-readonly-adapter/v1")
        self.assertTrue(adapter["sourcePolicy"]["derivedOnly"])
        self.assertTrue(adapter["sourcePolicy"]["readOnly"])
        self.assertEqual(adapter["sourcePolicy"]["mutatedTargets"], [])
        self.assertEqual(adapter["summary"]["projectionCount"], 1)
        self.assertEqual(adapter["summary"]["ledgerRecordCount"], 2)

        row = adapter["views"]["evidenceCenter"]["contractWorkbenchProjections"][0]
        self.assertTrue(row["read_only"])
        self.assertEqual(row["mutated_targets"], [])
        self.assertEqual(row["task_id"], task.task_id)
        self.assertEqual(row["task_kind"], "cad_preview_with_readback")
        self.assertEqual(row["completion_status"], "ready")
        self.assertEqual(row["verification_status"], "verified")
        self.assertTrue(row["can_claim_complete"])
        self.assertEqual(row["checked_evidence"], ["real_cad_readback", "no_save_guard"])
        self.assertEqual(row["missing_evidence"], [])
        self.assertEqual(row["ledger_record_count"], 2)
        self.assertEqual(row["evidence_package_refs"][0]["evidence_package_id"], "pkg-real-readback")
        self.assertEqual(row["source_ref"], "output/phase8-adapter/readback.json")
        self.assertEqual(row["content_hash"], content_hash)
        self.assertEqual(row["producer"], "unit-test")
        self.assertEqual(row["tool_card_id"], "legacy.readback")

    def test_adapter_retains_blocked_not_verified_and_missing_evidence_reasons(self) -> None:
        from core.contracts.evidence_ledger import EvidenceLedgerRecord
        from core.contracts.legacy_gateway import legacy_validate_dry_run_evidence_package
        from core.contracts.workbench_projection import build_workbench_projection
        from core.contracts.workbench_readonly_adapter import build_workbench_readonly_adapter

        task = _cad_completion_task()
        package = legacy_validate_dry_run_evidence_package(
            task_id=task.task_id,
            validation_errors=[],
            dry_run_result={"status": "valid"},
            model_text="Preview registered, but no created handles were read back.",
        )
        ledger = MutationTrapLedger(
            [
                EvidenceLedgerRecord(
                    ledger_id="ledger-dry-run",
                    task_id=task.task_id,
                    contract_id="contract-dry-run",
                    evidence_package_id="pkg-dry-run",
                    evidence_type="no_save_guard",
                    producer="legacy.dry_run",
                    tool_card_id="legacy.dry_run",
                    verification_status="verified",
                    not_verified_reason="dry-run has no created handles readback",
                )
            ]
        )
        projection = build_workbench_projection(
            task=task,
            evidence_packages={"pkg-dry-run": package},
            ledger=ledger,
        )

        adapter = build_workbench_readonly_adapter([projection])
        row = adapter["views"]["evidenceCenter"]["contractWorkbenchProjections"][0]

        self.assertEqual(row["completion_status"], "not_verified")
        self.assertEqual(row["verification_status"], "not_verified")
        self.assertFalse(row["can_claim_complete"])
        self.assertFalse(row["cad_geometry_verified"])
        self.assertIn("real_cad_readback", row["missing_evidence"])
        self.assertIn("dry-run has no created handles readback", row["not_verified_reason"])
        self.assertEqual(adapter["summary"]["notVerifiedCount"], 1)
        self.assertEqual(adapter["summary"]["cadGeometryVerifiedCount"], 0)

    def test_adapter_keeps_missing_package_and_hash_mismatch_blocked(self) -> None:
        from core.contracts.evidence_ledger import EvidenceLedgerRecord
        from core.contracts.workbench_projection import build_workbench_projection
        from core.contracts.workbench_readonly_adapter import build_workbench_readonly_adapter

        task = _cad_completion_task()
        ledger = MutationTrapLedger(
            [
                EvidenceLedgerRecord(
                    ledger_id="ledger-missing-package",
                    task_id=task.task_id,
                    contract_id="contract-readback",
                    evidence_package_id="pkg-missing",
                    evidence_type="real_cad_readback",
                    producer="unit-test",
                    tool_card_id="legacy.readback",
                    verification_status="verified",
                ),
                EvidenceLedgerRecord(
                    ledger_id="ledger-hash-mismatch",
                    task_id=task.task_id,
                    contract_id="contract-no-save",
                    evidence_package_id="pkg-real-readback",
                    evidence_type="no_save_guard",
                    producer="unit-test",
                    tool_card_id="legacy.readback",
                    verification_status="verified",
                    content_hash="sha256-not-the-package",
                ),
            ]
        )
        projection = build_workbench_projection(
            task=task,
            evidence_packages={"pkg-real-readback": _real_readback_package()},
            ledger=ledger,
        )

        adapter = build_workbench_readonly_adapter([projection])
        row = adapter["views"]["evidenceCenter"]["contractWorkbenchProjections"][0]

        self.assertEqual(row["completion_status"], "blocked")
        self.assertIn("points to missing EvidencePackage", row["blocked_reason"])
        self.assertIn("content_hash does not match package", row["blocked_reason"])
        self.assertEqual(row["ledger_records_summary"][0]["package_status"], "missing")
        self.assertEqual(row["ledger_records_summary"][1]["hash_matches"], False)
        self.assertEqual(adapter["summary"]["blockedCount"], 1)

    def test_flightdeck_can_consume_adapter_output_without_promoting_it_to_truth_source(self) -> None:
        from core.contracts.workbench_projection import WorkbenchProjection
        from core.contracts.workbench_readonly_adapter import build_workbench_readonly_adapter
        from core.training_workbench.flightdeck import build_workbench_v3

        projection = WorkbenchProjection(
            schema_version="workbench-projection/v1",
            task_id="task-flightdeck",
            task_kind="cad_preview_with_readback",
            missing_evidence=["real_cad_readback"],
            completion_status="blocked",
            verification_status="not_verified",
            blocked_reason="ledger record missing",
            source_refs=["output/phase8-adapter/blocked.json"],
        )
        adapter = build_workbench_readonly_adapter([projection])
        v3 = build_workbench_v3(Path.cwd(), {"contractWorkbench": adapter})

        evidence_center = v3["views"]["evidenceCenter"]
        panel = evidence_center["contractWorkbench"]
        self.assertTrue(panel["readOnly"])
        self.assertEqual(panel["mutatedTargets"], [])
        self.assertEqual(panel["summary"]["projectionCount"], 1)
        self.assertEqual(panel["items"][0]["task_id"], "task-flightdeck")
        self.assertIn("contractWorkbench", v3["sourcePolicy"]["derivedArtifacts"])
        self.assertIn("cad_geometry", v3["sourcePolicy"]["notProofOf"])

    def test_trace_viewer_can_attach_adapter_summary_as_read_only_context(self) -> None:
        from core.contracts.workbench_projection import WorkbenchProjection
        from core.contracts.workbench_readonly_adapter import build_workbench_readonly_adapter
        from core.orchestrator.workbench_trace_viewer import build_workbench_trace_viewer_data

        projection = WorkbenchProjection(
            schema_version="workbench-projection/v1",
            task_id="task-trace-viewer",
            task_kind="cad_preview_with_readback",
            missing_evidence=["real_cad_readback"],
            completion_status="blocked",
            verification_status="not_verified",
            blocked_reason="missing package",
        )
        adapter = build_workbench_readonly_adapter([projection])

        with temporary_artifact_dir("trace_viewer_contract_workbench") as root:
            data = build_workbench_trace_viewer_data(root, contract_workbench=adapter)

        contract_context = data["contractWorkbench"]
        self.assertTrue(contract_context["readOnly"])
        self.assertEqual(contract_context["mutatedTargets"], [])
        self.assertEqual(contract_context["summary"]["projectionCount"], 1)
        self.assertEqual(contract_context["blockedTaskIds"], ["task-trace-viewer"])
        self.assertIn("does_not_prove_cad_geometry", data["sourcePolicy"]["notProofOf"])

    def test_adapter_does_not_write_display_only_protected_source_refs(self) -> None:
        from core.contracts.workbench_projection import WorkbenchProjection
        from core.contracts.workbench_readonly_adapter import build_workbench_readonly_adapter

        protected_ref = Path("output/phase8-adapter-should-not-create.json")
        self.assertFalse(protected_ref.exists())
        projection = WorkbenchProjection(
            schema_version="workbench-projection/v1",
            task_id="task-protected-ref",
            task_kind="cad_preview_with_readback",
            source_refs=[str(protected_ref)],
            content_hashes=["sha256-display-only"],
            producers=["unit-test"],
            tool_card_ids=["legacy.readback"],
            completion_status="blocked",
            verification_status="not_verified",
            blocked_reason="display only",
        )

        adapter = build_workbench_readonly_adapter([projection])

        row = adapter["views"]["evidenceCenter"]["contractWorkbenchProjections"][0]
        self.assertEqual(row["source_ref"], str(protected_ref))
        self.assertFalse(protected_ref.exists())


if __name__ == "__main__":
    unittest.main()
