from __future__ import annotations

from pathlib import Path
import unittest


def _cad_completion_task() -> object:
    from core.contracts.vnext import TaskObject

    return TaskObject(
        task_id="task-phase8-workbench",
        task_kind="cad_preview_with_readback",
        user_intent="Expose read-only completion state for the workbench.",
        target_scope={"scopeType": "fixture", "documentId": "none"},
        evidence_requirements=["real_cad_readback", "no_save_guard"],
    )


def _real_readback_package() -> object:
    from core.contracts.vnext import EvidenceItem, EvidencePackage

    return EvidencePackage(
        task_id="task-phase8-workbench",
        items=[
            EvidenceItem(
                kind="cad_readback",
                status="pass",
                backend="real_cad",
                readback_status="ok",
                cad_geometry_verified=True,
                metadata={"created_handles": ["AB12"]},
            ),
            EvidenceItem(
                kind="no_save_guard",
                status="pass",
                metadata={"savedCurrentDwg": False},
            ),
        ],
    )


def _readback_package_without_handles() -> object:
    from core.contracts.legacy_gateway import legacy_readback_registration_evidence_package

    return legacy_readback_registration_evidence_package(
        task_id="task-phase8-workbench",
        readback_report={
            "status": "geometry_verified",
            "backend": "real_cad",
            "readbackStatus": "ok",
            "actual": {"created_handles": []},
        },
        registered=True,
    )


class MutationTrapLedger:
    def __init__(self, records: list[object] | None = None) -> None:
        self._records = tuple(records or [])

    def records_for_task(self, task_id: str) -> tuple[object, ...]:
        return tuple(record for record in self._records if getattr(record, "task_id", "") == task_id)

    def append(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("projection must not append ledger records")

    def overwrite(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("projection must not overwrite ledger records")

    def delete(self, *_args: object, **_kwargs: object) -> None:
        raise AssertionError("projection must not delete ledger records")


class WorkbenchProjectionTests(unittest.TestCase):
    def test_projection_summarizes_ready_decision_ledger_records_and_package_refs(self) -> None:
        from core.contracts.evidence_ledger import EvidenceLedgerRecord, evidence_package_content_hash
        from core.contracts.workbench_projection import build_workbench_projection

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
                    source_ref="output/phase8-fixture/readback.json",
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
                    source_ref="output/phase8-fixture/no-save.json",
                    content_hash=content_hash,
                ),
            ]
        )

        projection = build_workbench_projection(
            task=task,
            evidence_packages={"pkg-real-readback": package},
            ledger=ledger,
        )

        self.assertEqual(projection.task_id, task.task_id)
        self.assertEqual(projection.task_kind, "cad_preview_with_readback")
        self.assertEqual(projection.required_evidence, ["real_cad_readback", "no_save_guard"])
        self.assertEqual(projection.checked_evidence, ["real_cad_readback", "no_save_guard"])
        self.assertEqual(projection.missing_evidence, [])
        self.assertEqual(projection.completion_status, "ready")
        self.assertEqual(projection.verification_status, "verified")
        self.assertTrue(projection.can_claim_complete)
        self.assertTrue(projection.cad_geometry_verified)
        self.assertEqual(len(projection.ledger_records_summary), 2)
        self.assertEqual(projection.ledger_records_summary[0]["producer"], "unit-test")
        self.assertEqual(projection.ledger_records_summary[0]["tool_card_id"], "legacy.readback")
        self.assertEqual(projection.ledger_records_summary[0]["source_ref"], "output/phase8-fixture/readback.json")
        self.assertEqual(projection.evidence_package_refs[0]["evidence_package_id"], "pkg-real-readback")
        self.assertEqual(projection.evidence_package_refs[0]["content_hash"], content_hash)
        self.assertEqual(projection.blocked_reason, "")
        self.assertEqual(projection.not_verified_reason, "")

    def test_missing_ledger_record_projects_missing_evidence_as_blocked(self) -> None:
        from core.contracts.workbench_projection import build_workbench_projection

        task = _cad_completion_task()
        projection = build_workbench_projection(
            task=task,
            evidence_packages={"pkg-real-readback": _real_readback_package()},
            ledger=MutationTrapLedger(),
        )

        self.assertEqual(projection.completion_status, "blocked")
        self.assertFalse(projection.can_claim_complete)
        self.assertFalse(projection.cad_geometry_verified)
        self.assertIn("real_cad_readback", projection.missing_evidence)
        self.assertIn("missing ledger record", projection.blocked_reason)

    def test_missing_package_and_hash_mismatch_project_blocked_reasons(self) -> None:
        from core.contracts.evidence_ledger import EvidenceLedgerRecord
        from core.contracts.workbench_projection import build_workbench_projection

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

        self.assertEqual(projection.completion_status, "blocked")
        self.assertIn("points to missing EvidencePackage", projection.blocked_reason)
        self.assertIn("content_hash does not match package", projection.blocked_reason)
        self.assertEqual(projection.ledger_records_summary[0]["package_status"], "missing")
        self.assertEqual(projection.ledger_records_summary[1]["hash_matches"], False)

    def test_non_cad_evidence_projects_not_verified_without_geometry_verified(self) -> None:
        from core.contracts.evidence_ledger import EvidenceLedgerRecord
        from core.contracts.legacy_gateway import legacy_validate_dry_run_evidence_package
        from core.contracts.workbench_projection import build_workbench_projection

        task = _cad_completion_task()
        package = legacy_validate_dry_run_evidence_package(
            task_id=task.task_id,
            validation_errors=[],
            dry_run_result={"status": "valid"},
            model_text="The preview looks ready.",
        )
        ledger = MutationTrapLedger(
            [
                EvidenceLedgerRecord(
                    ledger_id="ledger-non-cad-ready",
                    task_id=task.task_id,
                    contract_id="contract-dry-run",
                    evidence_package_id="pkg-non-cad",
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
            evidence_packages={"pkg-non-cad": package},
            ledger=ledger,
        )

        self.assertEqual(projection.completion_status, "not_verified")
        self.assertEqual(projection.verification_status, "not_verified")
        self.assertFalse(projection.can_claim_complete)
        self.assertFalse(projection.cad_geometry_verified)
        self.assertIn("real_cad_readback", projection.missing_evidence)
        self.assertIn("dry-run has no created handles readback", projection.not_verified_reason)

    def test_projection_does_not_treat_fixture_readback_without_handles_as_geometry_verified(self) -> None:
        from core.contracts.evidence_ledger import EvidenceLedgerRecord
        from core.contracts.workbench_projection import build_workbench_projection

        task = _cad_completion_task()
        package = _readback_package_without_handles()
        ledger = MutationTrapLedger(
            [
                EvidenceLedgerRecord(
                    ledger_id="ledger-readback-no-handles",
                    task_id=task.task_id,
                    contract_id="contract-readback",
                    evidence_package_id="pkg-readback-no-handles",
                    evidence_type="real_cad_readback",
                    producer="fixture",
                    tool_card_id="legacy.readback",
                    verification_status="verified",
                    blocked_reason="created handles missing",
                )
            ]
        )

        projection = build_workbench_projection(
            task=task,
            evidence_packages={"pkg-readback-no-handles": package},
            ledger=ledger,
        )

        self.assertEqual(projection.completion_status, "blocked")
        self.assertFalse(projection.cad_geometry_verified)
        self.assertIn("created handles missing", projection.blocked_reason)
        self.assertIn("does not match EvidencePackage evidence_type", projection.blocked_reason)

    def test_projection_is_read_only_and_does_not_write_protected_evidence_path(self) -> None:
        from core.contracts.evidence_ledger import EvidenceLedgerRecord
        from core.contracts.workbench_projection import build_workbench_projection

        protected_ref = Path("output/phase8-workbench-should-not-create.json")
        self.assertFalse(protected_ref.exists())
        task = _cad_completion_task()
        ledger = MutationTrapLedger(
            [
                EvidenceLedgerRecord(
                    ledger_id="ledger-protected-ref",
                    task_id=task.task_id,
                    contract_id="contract-readback",
                    evidence_package_id="pkg-real-readback",
                    evidence_type="real_cad_readback",
                    producer="unit-test",
                    tool_card_id="legacy.readback",
                    verification_status="not_verified",
                    source_ref=str(protected_ref),
                    not_verified_reason="source path is display-only",
                )
            ]
        )

        projection = build_workbench_projection(
            task=task,
            evidence_packages={"pkg-real-readback": _real_readback_package()},
            ledger=ledger,
        )

        self.assertFalse(protected_ref.exists())
        self.assertFalse(projection.can_claim_complete)
        self.assertEqual(projection.source_refs, [str(protected_ref)])


if __name__ == "__main__":
    unittest.main()
