from __future__ import annotations

import unittest
from pathlib import Path


def _cad_completion_task() -> object:
    from core.contracts.vnext import TaskObject

    return TaskObject(
        task_id="task-phase7-cad-completion",
        task_kind="cad_preview_with_readback",
        user_intent="Close only after deterministic CAD readback evidence.",
        target_scope={"scopeType": "fixture", "documentId": "none"},
        evidence_requirements=["real_cad_readback", "no_save_guard"],
    )


def _readback_package_without_handles() -> object:
    from core.contracts.legacy_gateway import legacy_readback_registration_evidence_package

    return legacy_readback_registration_evidence_package(
        task_id="task-phase7-cad-completion",
        readback_report={
            "status": "geometry_verified",
            "backend": "real_cad",
            "readbackStatus": "ok",
            "actual": {"created_handles": []},
        },
        registered=True,
    )


class EvidenceLedgerSkeletonTests(unittest.TestCase):
    def test_missing_ledger_record_cannot_complete(self) -> None:
        from core.contracts.evidence_ledger import InMemoryEvidenceLedger
        from core.contracts.vnext import CompletionJudge, EvidenceItem, EvidencePackage

        task = _cad_completion_task()
        evidence = EvidencePackage(
            task_id=task.task_id,
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

        decision = CompletionJudge().judge_with_ledger(
            task=task,
            evidence_packages={"pkg-real-readback": evidence},
            ledger=InMemoryEvidenceLedger(),
        )

        self.assertIn(decision.status, {"blocked", "not_verified"})
        self.assertFalse(decision.can_claim_complete)
        self.assertIn("real_cad_readback", decision.missing_evidence)

    def test_duplicate_ledger_id_is_rejected(self) -> None:
        from core.contracts.evidence_ledger import DuplicateLedgerIdError, EvidenceLedgerRecord, InMemoryEvidenceLedger

        ledger = InMemoryEvidenceLedger()
        record = EvidenceLedgerRecord(
            ledger_id="ledger-duplicate",
            task_id="task-phase7-cad-completion",
            contract_id="contract-readback",
            evidence_package_id="pkg-readback",
            evidence_type="real_cad_readback",
            producer="unit-test",
            tool_card_id="legacy.readback",
            verification_status="verified",
        )

        ledger.append(record)

        with self.assertRaises(DuplicateLedgerIdError):
            ledger.append(record)

    def test_ledger_record_pointing_to_missing_evidence_package_is_blocked(self) -> None:
        from core.contracts.evidence_ledger import EvidenceLedgerRecord, InMemoryEvidenceLedger
        from core.contracts.vnext import CompletionJudge

        ledger = InMemoryEvidenceLedger()
        ledger.append(
            EvidenceLedgerRecord(
                ledger_id="ledger-missing-package",
                task_id="task-phase7-cad-completion",
                contract_id="contract-readback",
                evidence_package_id="pkg-does-not-exist",
                evidence_type="real_cad_readback",
                producer="unit-test",
                tool_card_id="legacy.readback",
                verification_status="verified",
            )
        )

        decision = CompletionJudge().judge_with_ledger(
            task=_cad_completion_task(),
            evidence_packages={},
            ledger=ledger,
        )

        self.assertEqual(decision.status, "blocked")
        self.assertFalse(decision.can_claim_complete)
        self.assertIn("real_cad_readback", decision.missing_evidence)

    def test_model_text_evidence_cannot_be_geometry_verified_by_ledger(self) -> None:
        from core.contracts.evidence_ledger import EvidenceLedgerRecord, InMemoryEvidenceLedger
        from core.contracts.vnext import CompletionJudge, EvidencePackage

        task = _cad_completion_task()
        evidence = EvidencePackage.from_model_text(
            task_id=task.task_id,
            text="The CAD geometry is verified.",
        )
        ledger = InMemoryEvidenceLedger()
        ledger.append(
            EvidenceLedgerRecord(
                ledger_id="ledger-model-text",
                task_id=task.task_id,
                contract_id="contract-readback",
                evidence_package_id="pkg-model-text",
                evidence_type="real_cad_readback",
                producer="model",
                tool_card_id="model.text",
                verification_status="verified",
            )
        )

        decision = CompletionJudge().judge_with_ledger(
            task=task,
            evidence_packages={"pkg-model-text": evidence},
            ledger=ledger,
        )

        self.assertEqual(decision.status, "blocked")
        self.assertFalse(decision.can_claim_complete)
        self.assertIn("real_cad_readback", decision.missing_evidence)

    def test_dry_run_evidence_cannot_masquerade_as_readback(self) -> None:
        from core.contracts.evidence_ledger import EvidenceLedgerRecord, InMemoryEvidenceLedger
        from core.contracts.vnext import CompletionJudge, EvidenceItem, EvidencePackage

        task = _cad_completion_task()
        evidence = EvidencePackage(
            task_id=task.task_id,
            items=[
                EvidenceItem(kind="cad_plan_dry_run", status="pass", backend="dry_run"),
                EvidenceItem(kind="no_save_guard", status="pass", metadata={"savedCurrentDwg": False}),
            ],
        )
        ledger = InMemoryEvidenceLedger()
        ledger.append(
            EvidenceLedgerRecord(
                ledger_id="ledger-dry-run-as-readback",
                task_id=task.task_id,
                contract_id="contract-readback",
                evidence_package_id="pkg-dry-run",
                evidence_type="real_cad_readback",
                producer="legacy.dry_run",
                tool_card_id="legacy.dry_run",
                verification_status="verified",
            )
        )

        decision = CompletionJudge().judge_with_ledger(
            task=task,
            evidence_packages={"pkg-dry-run": evidence},
            ledger=ledger,
        )

        self.assertEqual(decision.status, "blocked")
        self.assertFalse(decision.can_claim_complete)
        self.assertIn("real_cad_readback", decision.missing_evidence)

    def test_preview_registered_evidence_cannot_masquerade_as_cad_write_or_readback(self) -> None:
        from core.contracts.evidence_ledger import EvidenceLedgerRecord, InMemoryEvidenceLedger
        from core.contracts.legacy_gateway import legacy_preview_registration_evidence_package
        from core.contracts.vnext import CompletionJudge

        task = _cad_completion_task()
        evidence = legacy_preview_registration_evidence_package(
            task_id=task.task_id,
            layer="CODEX_PREVIEW",
            registered=True,
        )
        ledger = InMemoryEvidenceLedger()
        ledger.append(
            EvidenceLedgerRecord(
                ledger_id="ledger-preview-as-readback",
                task_id=task.task_id,
                contract_id="contract-readback",
                evidence_package_id="pkg-preview",
                evidence_type="real_cad_readback",
                producer="legacy.preview",
                tool_card_id="legacy.preview",
                verification_status="verified",
                metadata={"claimed_effect": "cad_preview_written"},
            )
        )

        decision = CompletionJudge().judge_with_ledger(
            task=task,
            evidence_packages={"pkg-preview": evidence},
            ledger=ledger,
        )

        self.assertEqual(decision.status, "blocked")
        self.assertFalse(decision.can_claim_complete)
        self.assertFalse(evidence.satisfies("real_cad_readback"))

    def test_fixture_readback_without_created_handles_is_not_geometry_verified(self) -> None:
        from core.contracts.evidence_ledger import EvidenceLedgerRecord, InMemoryEvidenceLedger
        from core.contracts.vnext import CompletionJudge

        task = _cad_completion_task()
        evidence = _readback_package_without_handles()
        ledger = InMemoryEvidenceLedger()
        ledger.append(
            EvidenceLedgerRecord(
                ledger_id="ledger-readback-no-handles",
                task_id=task.task_id,
                contract_id="contract-readback",
                evidence_package_id="pkg-readback-no-handles",
                evidence_type="real_cad_readback",
                producer="fixture",
                tool_card_id="legacy.readback",
                verification_status="verified",
            )
        )

        decision = CompletionJudge().judge_with_ledger(
            task=task,
            evidence_packages={"pkg-readback-no-handles": evidence},
            ledger=ledger,
        )

        self.assertEqual(decision.status, "blocked")
        self.assertFalse(decision.can_claim_complete)
        self.assertFalse(evidence.satisfies("real_cad_readback"))
        self.assertEqual(evidence.real_cad_readback_items(), [])

    def test_ledger_skeleton_does_not_write_protected_evidence_paths(self) -> None:
        from core.contracts.evidence_ledger import EvidenceLedgerRecord, InMemoryEvidenceLedger

        protected_ref = Path("output/phase7-ledger-skeleton-should-not-create.json")
        self.assertFalse(protected_ref.exists())

        ledger = InMemoryEvidenceLedger()
        ledger.append(
            EvidenceLedgerRecord(
                ledger_id="ledger-protected-source-ref",
                task_id="task-phase7-cad-completion",
                contract_id="contract-readback",
                evidence_package_id="pkg-readback",
                evidence_type="real_cad_readback",
                producer="unit-test",
                tool_card_id="legacy.readback",
                verification_status="not_verified",
                source_ref=str(protected_ref),
            )
        )

        self.assertFalse(protected_ref.exists())
        self.assertEqual(ledger.records[0].source_ref, str(protected_ref))


if __name__ == "__main__":
    unittest.main()
