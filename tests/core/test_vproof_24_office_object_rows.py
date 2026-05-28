from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.verification.capability_registry import validate_capability_registry
from core.verification.office_object_registry import (
    OFFICE_OBJECT_SUITE_CAPABILITY_ID,
    VPROOF_24_BOUNDARY_DOC,
    VPROOF_24_PACKAGE_ID,
    assert_office_object_registry_contract,
    build_office_object_registry_rows,
    capability_id_for_office_object_case,
    expected_office_object_case_ids,
    load_office_alpha_object_manifest,
    merge_office_object_registry_rows,
    run_office_object_benchmark_subset,
    run_vproof_24_office_object_sync,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class Vproof24OfficeObjectRowsTests(unittest.TestCase):
    def test_manifest_lists_six_object_cases(self) -> None:
        manifest = load_office_alpha_object_manifest(
            PROJECT_ROOT / "examples/capability_proof/office_alpha_object_manifest.json",
        )
        cases = expected_office_object_case_ids(manifest=manifest)
        self.assertEqual(len(cases), 6)
        self.assertIn("office_desk_default_spec", cases)

    def test_build_rows_include_suite_and_cases(self) -> None:
        manifest = load_office_alpha_object_manifest(
            PROJECT_ROOT / "examples/capability_proof/office_alpha_object_manifest.json",
        )
        rows = build_office_object_registry_rows(manifest=manifest, output_root="output/test")
        self.assertEqual(len(rows), 7)
        self.assertEqual(rows[0]["capability_id"], OFFICE_OBJECT_SUITE_CAPABILITY_ID)
        ids = {row["capability_id"] for row in rows[1:]}
        self.assertEqual(
            ids,
            {capability_id_for_office_object_case(c) for c in expected_office_object_case_ids(manifest=manifest)},
        )
        for row in rows:
            self.assertEqual(row["claim_level"], "smoke")
            self.assertEqual(row["domain"], "office")

    def test_office_object_subset_passes(self) -> None:
        output_dir = artifact_path("vproof_24", "subset")
        manifest = load_office_alpha_object_manifest(
            PROJECT_ROOT / "examples/capability_proof/office_alpha_object_manifest.json",
        )
        report = run_office_object_benchmark_subset(
            project_root=PROJECT_ROOT,
            output_dir=output_dir,
            manifest=manifest,
        )
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["pass_count"], 6)

    def test_boundary_doc_states_claim_limits(self) -> None:
        text = (PROJECT_ROOT / VPROOF_24_BOUNDARY_DOC).read_text(encoding="utf-8")
        for phrase in (
            "V-PROOF-24",
            "office_alpha",
            "object_spec",
            "benchmark_pass_non_cad",
            "claim_level",
            "smoke",
            "不得声称",
            "geometry_verified",
            "no-CAD",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_merge_and_sync_dry_run(self) -> None:
        output_dir = artifact_path("vproof_24", "sync_dry_run")
        summary = run_vproof_24_office_object_sync(
            project_root=PROJECT_ROOT,
            output_dir=output_dir,
            dry_run=True,
        )
        self.assertEqual(summary["package_id"], VPROOF_24_PACKAGE_ID)
        self.assertEqual(summary["object_case_count"], 6)
        self.assertEqual(summary["registry_row_count"], 7)
        self.assertEqual(summary["writeback_rejected_count"], 0)

    def test_merge_downgrades_office_object_rows_to_smoke(self) -> None:
        registry_path = PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        manifest = load_office_alpha_object_manifest(
            PROJECT_ROOT / "examples/capability_proof/office_alpha_object_manifest.json",
        )
        rows = build_office_object_registry_rows(manifest=manifest, output_root="output/test")
        merge_office_object_registry_rows(registry, rows)
        errors = validate_capability_registry(registry)
        self.assertEqual(errors, [])
        case_id = "office_desk_default_spec"
        capability_id = capability_id_for_office_object_case(case_id)
        row = next(item for item in registry["capabilities"] if item["capability_id"] == capability_id)
        self.assertEqual(row["claim_level"], "smoke")
        self.assertEqual(row["cad_case"]["benchmark_case_id"], case_id)

    def test_live_registry_contract_when_rows_present(self) -> None:
        registry_path = PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        if OFFICE_OBJECT_SUITE_CAPABILITY_ID not in {
            str(item.get("capability_id", "")) for item in registry.get("capabilities", [])
        }:
            self.skipTest("office object suite row not merged; run run_vproof_24_office_object_sync.py")
        assert_office_object_registry_contract(project_root=PROJECT_ROOT)


if __name__ == "__main__":
    unittest.main()
