from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.verification.evidence_vocabulary import (
    EVIDENCE_CAD_CAPABILITY_VERIFIED,
    EVIDENCE_NEGATIVE_GUARD_VERIFIED,
)
from core.verification.guard_cad_registry import (
    GUARD_FULL_STRICT_CAPABILITY_ID,
    VPROOF_52_BOUNDARY_DOC,
    assert_vproof_52_guard_cad_contract,
    build_guard_cad_registry_rows,
    merge_guard_cad_registry_rows,
    run_vproof_52_guard_cad_sync,
    validate_guard_full_strict_report,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


def _sample_real_guard_report() -> dict:
    return {
        "version": "0.1",
        "suite_id": "guard_full_cad_runner",
        "status": "pass",
        "mode": "real_cad",
        "strict": True,
        "strict_gate": {"status": "pass", "failures": []},
        "subreports": {
            "write_guard": {"status": "pass"},
            "negative_cad": {
                "status": "pass",
                "evidence_state": EVIDENCE_NEGATIVE_GUARD_VERIFIED,
            },
            "capability_probe": {
                "status": "cad_capability_verified",
                "session_guard_status": "consistent",
            },
        },
        "subreport_paths": {
            "write_guard": "subreports/write_guard/write_guard_cad_runner_report.json",
            "negative_cad": "subreports/negative_cad/negative_cad_runner_report.json",
            "capability_probe": "subreports/capability_probe/cad_capability_probe.json",
        },
    }


class Vproof52GuardCadTests(unittest.TestCase):
    def test_build_four_registry_rows(self) -> None:
        rows = build_guard_cad_registry_rows()
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["capability_id"], GUARD_FULL_STRICT_CAPABILITY_ID)

    def test_validate_real_strict_report(self) -> None:
        self.assertEqual(validate_guard_full_strict_report(_sample_real_guard_report(), require_real_cad=True), [])

    def test_boundary_doc_exists(self) -> None:
        text = (PROJECT_ROOT / VPROOF_52_BOUNDARY_DOC).read_text(encoding="utf-8")
        for phrase in (
            "V-PROOF-52",
            "guard.cad.full_chain.strict",
            "strict_gate",
            "RCAD-21",
            "不得声称",
            "geometry_verified",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_sync_dry_run_with_fixture(self) -> None:
        output_dir = artifact_path("vproof_52", "sync_fixture")
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / "guard_full_cad_report.json"
        report_path.write_text(json.dumps(_sample_real_guard_report(), indent=2), encoding="utf-8")
        for name in (
            "subreports/write_guard/write_guard_cad_runner_report.json",
            "subreports/negative_cad/negative_cad_runner_report.json",
            "subreports/capability_probe/cad_capability_probe.json",
        ):
            sub = output_dir / name
            sub.parent.mkdir(parents=True, exist_ok=True)
            sub.write_text(json.dumps({"status": "pass"}), encoding="utf-8")

        summary = run_vproof_52_guard_cad_sync(
            project_root=PROJECT_ROOT,
            output_dir=output_dir,
            report_path=report_path,
            dry_run=True,
        )
        self.assertGreaterEqual(summary["writeback_applied_count"], 1)
        self.assertEqual(summary["strict_gate_status"], "pass")

    def test_merge_rows_validate_registry(self) -> None:
        registry = json.loads(
            (PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json").read_text(encoding="utf-8")
        )
        merge_guard_cad_registry_rows(registry, build_guard_cad_registry_rows())
        from core.verification.capability_registry import validate_capability_registry

        self.assertEqual(validate_capability_registry(registry), [])

    def test_live_contract_when_present(self) -> None:
        registry = json.loads(
            (PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json").read_text(encoding="utf-8")
        )
        if not any(
            item.get("capability_id") == GUARD_FULL_STRICT_CAPABILITY_ID
            for item in registry.get("capabilities", [])
        ):
            self.skipTest("guard registry rows not merged yet")
        assert_vproof_52_guard_cad_contract(project_root=PROJECT_ROOT)


if __name__ == "__main__":
    unittest.main()
