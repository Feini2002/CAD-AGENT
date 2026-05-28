from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.verification.capability_registry import validate_capability_registry
from core.verification.object_detail_registry import (
    COMPONENT_DETAIL_SUITE_CAPABILITY_ID,
    VPROOF_23_BOUNDARY_DOC,
    VPROOF_23_PACKAGE_ID,
    assert_object_detail_registry_contract,
    build_object_detail_registry_rows,
    capability_id_for_component_detail,
    expected_object_types,
    load_object_detail_component_manifest,
    merge_object_detail_registry_rows,
    run_object_detail_component_suite,
    run_vproof_23_object_detail_sync,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class Vproof23ObjectDetailRowsTests(unittest.TestCase):
    def test_manifest_lists_five_object_types(self) -> None:
        manifest = load_object_detail_component_manifest(
            PROJECT_ROOT / "examples/capability_proof/object_detail_component_manifest.json",
        )
        types = expected_object_types(manifest=manifest)
        self.assertEqual(types, ["table", "desk", "chair", "bed", "sofa"])

    def test_build_rows_include_suite_and_objects(self) -> None:
        manifest = load_object_detail_component_manifest(
            PROJECT_ROOT / "examples/capability_proof/object_detail_component_manifest.json",
        )
        rows = build_object_detail_registry_rows(manifest=manifest, output_root="output/test")
        self.assertEqual(len(rows), 6)
        self.assertEqual(rows[0]["capability_id"], COMPONENT_DETAIL_SUITE_CAPABILITY_ID)
        ids = {row["capability_id"] for row in rows[1:]}
        self.assertEqual(
            ids,
            {capability_id_for_component_detail(t) for t in expected_object_types(manifest=manifest)},
        )

    def test_component_suite_passes(self) -> None:
        output_dir = artifact_path("vproof_23", "suite")
        manifest = load_object_detail_component_manifest(
            PROJECT_ROOT / "examples/capability_proof/object_detail_component_manifest.json",
        )
        report = run_object_detail_component_suite(
            project_root=PROJECT_ROOT,
            output_dir=output_dir,
            manifest=manifest,
        )
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["pass_count"], 5)

    def test_boundary_doc_states_claim_limits(self) -> None:
        text = (PROJECT_ROOT / VPROOF_23_BOUNDARY_DOC).read_text(encoding="utf-8")
        for phrase in (
            "V-PROOF-23",
            "component_detail",
            "benchmark_pass_non_cad",
            "claim_level",
            "smoke",
            "不得声称",
            "geometry_verified",
            "OBJ-DETAIL",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_merge_and_sync_dry_run(self) -> None:
        output_dir = artifact_path("vproof_23", "sync_dry_run")
        summary = run_vproof_23_object_detail_sync(
            project_root=PROJECT_ROOT,
            output_dir=output_dir,
            dry_run=True,
        )
        self.assertEqual(summary["package_id"], VPROOF_23_PACKAGE_ID)
        self.assertEqual(summary["object_type_count"], 5)
        self.assertEqual(summary["registry_row_count"], 6)
        self.assertEqual(summary["writeback_rejected_count"], 0)

    def test_registry_contract_after_merge_in_temp_registry(self) -> None:
        registry_path = PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        manifest = load_object_detail_component_manifest(
            PROJECT_ROOT / "examples/capability_proof/object_detail_component_manifest.json",
        )
        rows = build_object_detail_registry_rows(manifest=manifest, output_root="output/test")
        merge_object_detail_registry_rows(registry, rows)
        errors = validate_capability_registry(registry)
        self.assertEqual(errors, [])
        for object_type in expected_object_types(manifest=manifest):
            capability_id = capability_id_for_component_detail(object_type)
            row = next(item for item in registry["capabilities"] if item["capability_id"] == capability_id)
            self.assertEqual(row["claim_level"], "smoke")

    def test_live_registry_contract_when_rows_present(self) -> None:
        registry_path = PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        if COMPONENT_DETAIL_SUITE_CAPABILITY_ID not in {
            str(item.get("capability_id", "")) for item in registry.get("capabilities", [])
        }:
            self.skipTest("component_detail rows not merged; run run_vproof_23_object_detail_sync.py")
        assert_object_detail_registry_contract(project_root=PROJECT_ROOT)


if __name__ == "__main__":
    unittest.main()
