from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.symbol_engine.block_first_boundary import (
    SYMBOL_09_BOUNDARY_DOC,
    SYMBOL_09_PACKAGE_ID,
    SYMBOL_09_SUITE_CAPABILITY_ID,
    assert_block_first_tier_boundary_contract,
    block_first_boundary_status_summary,
    build_block_first_registry_rows,
    capability_id_for_block_first_case,
    sync_block_first_registry_from_smoke,
)
from core.symbol_engine.block_first_tier import (
    default_manifest_path,
    run_block_first_tier_smoke,
)
from core.symbol_engine.symbol_fallback_boundary import assert_symbol_glyph_fallback_boundary_contract
from core.drawing_standard.drawing_standard_registry import SmokeEvidenceWritebackRequest, apply_smoke_registry_evidence_writeback
from core.verification.evidence_vocabulary import EVIDENCE_DRY_RUN_VALID_PLAN_ONLY
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class Symbol09BlockFirstTierTests(unittest.TestCase):
    def test_symbol_09_boundary_contract(self) -> None:
        assert_symbol_glyph_fallback_boundary_contract(project_root=PROJECT_ROOT)
        assert_block_first_tier_boundary_contract(project_root=PROJECT_ROOT)

    def test_registry_row_count(self) -> None:
        rows = build_block_first_registry_rows(project_root=PROJECT_ROOT)
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["capability_id"], SYMBOL_09_SUITE_CAPABILITY_ID)

    def test_boundary_doc_states_claim_limits(self) -> None:
        text = (PROJECT_ROOT / SYMBOL_09_BOUNDARY_DOC).read_text(encoding="utf-8")
        for phrase in (
            "SYMBOL-09",
            "insert_block_alpha",
            "cad_insertion_verified",
            "metadata_only",
            "silent_degradation",
            "V-PROOF-34",
            "RCAD-25",
            "geometry_verified",
            "不得声称",
            "symbol-block-first-tier-01",
            "assert_block_first_tier_boundary_contract",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_no_cad_smoke_three_cases(self) -> None:
        output_root = artifact_path("symbol_09", "smoke")
        result = run_block_first_tier_smoke(
            default_manifest_path(PROJECT_ROOT),
            output_root=output_root,
        )
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["summary"], {"total": 3, "passed": 3, "failed": 0})
        paths = {case["selected_render_path"] for case in result["cases"]}
        self.assertIn("block", paths)
        self.assertIn("symbol_glyph", paths)

    def test_smoke_writeback_and_sync_dry_run(self) -> None:
        output_root = artifact_path("symbol_09", "writeback")
        result = run_block_first_tier_smoke(
            default_manifest_path(PROJECT_ROOT),
            output_root=output_root,
        )
        registry = json.loads(
            (
                PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json"
            ).read_text(encoding="utf-8")
        )
        sync_results = sync_block_first_registry_from_smoke(
            registry,
            result,
            output_root=output_root,
            project_root=PROJECT_ROOT,
            dry_run=True,
        )
        self.assertEqual(len(sync_results), 4)
        self.assertTrue(all(item.status == "applied" for item in sync_results))

        report_path = output_root / "controlled-block-wins" / "case_result.json"
        rel = str(report_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
        row = {
            "capability_id": capability_id_for_block_first_case("controlled-block-wins"),
            "display_name": "test",
            "category": "symbol",
            "claim_level": "smoke",
            "ladder_level": "L1",
            "domain": "generic",
            "source_refs": [{"source_kind": "documentation", "source_path": "x", "source_key": "y"}],
            "cad_case": {
                "case_kind": "script",
                "requires_real_cad": False,
                "entrypoint": "scripts/run_block_first_tier_smoke.py",
                "output_path": rel,
                "safety": {
                    "layer": "CODEX_PREVIEW",
                    "saved_dwg": False,
                    "deleted_entities": False,
                    "modified_formal_layers": False,
                },
            },
        }
        mini_registry = {"version": "0.1", "registry_id": "t", "capabilities": [row]}
        wb = apply_smoke_registry_evidence_writeback(
            mini_registry,
            SmokeEvidenceWritebackRequest(
                capability_id=row["capability_id"],
                report_path=rel,
            ),
            project_root=PROJECT_ROOT,
            dry_run=False,
        )
        self.assertEqual(wb.status, "applied")
        self.assertEqual(
            mini_registry["capabilities"][0]["evidence"]["evidence_state"],
            EVIDENCE_DRY_RUN_VALID_PLAN_ONLY,
        )

    def test_status_summary(self) -> None:
        summary = block_first_boundary_status_summary(project_root=PROJECT_ROOT)
        self.assertEqual(summary["package_id"], SYMBOL_09_PACKAGE_ID)
        self.assertEqual(summary["case_count"], 3)
        self.assertEqual(summary["block_cad_intent"], "insert_block_alpha")

    def test_handoff_indexes_symbol_09(self) -> None:
        handoff = (PROJECT_ROOT / "docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md").read_text(encoding="utf-8")
        self.assertIn("SYMBOL-09", handoff)
        self.assertIn("symbol_09_block_first_tier_boundary.md", handoff)


if __name__ == "__main__":
    unittest.main()
