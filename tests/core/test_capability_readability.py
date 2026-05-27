from __future__ import annotations

import json
import unittest

from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path

from core.verification.capability_readability import run_capability_readability_report
from core.verification.capability_registry_contract import validate_registry_claim_contracts
from core.verification.negative_cad_runner import run_negative_cad_runner
from core.symbol_engine.readability import READABILITY_STATUSES
from core.schemas.registry import get_schema_path
from core.schemas.validator import validate_value


class CapabilityReadabilityTests(unittest.TestCase):
    def test_readability_report_groups_geometry_guard_and_unverified_rows(self) -> None:
        guard_dir = artifact_path("capability_readability", "negative_guard")
        guard_report = run_negative_cad_runner(
            root=PROJECT_ROOT,
            output_dir=guard_dir,
            use_real_cad=False,
        )
        output_dir = artifact_path("capability_readability", "report")

        report = run_capability_readability_report(
            PROJECT_ROOT,
            output_dir=output_dir,
            guard_report_paths=[PROJECT_ROOT / guard_report["output_path"]],
            generated_at="2026-05-27T00:00:02Z",
        )

        self.assertEqual(report["status"], "pass")
        summary = report["summary"]
        self.assertGreater(summary["verified_geometry_count"], 0)
        self.assertEqual(summary["verified_guard_count"], 1)
        self.assertGreater(summary["deferred_cad_count"], 0)
        self.assertGreater(summary["none_count"], 0)
        self.assertIn("what_can_be_claimed_as_geometry", report["readable_sections"])
        self.assertIn("what_is_guard_only", report["readable_sections"])
        self.assertTrue(report["recommended_next_capability_ids"])

        saved = output_dir / "capability_readability_report.json"
        self.assertTrue(saved.is_file())
        on_disk = json.loads(saved.read_text(encoding="utf-8"))
        self.assertEqual(on_disk["summary"]["verified_guard_count"], 1)

    def test_readability_status_rows_are_bound_in_capability_registry(self) -> None:
        registry_path = PROJECT_ROOT / "examples" / "capability_proof" / "cad_capability_registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        rows = {
            row.get("readability_status"): row
            for row in registry.get("capabilities", [])
            if str(row.get("capability_id", "")).startswith("symbol.readability_status.")
        }

        self.assertEqual(set(rows), set(READABILITY_STATUSES))
        for status, row in rows.items():
            with self.subTest(status=status):
                self.assertEqual(row["category"], "symbol")
                self.assertEqual(row["readability_status"], status)
                self.assertEqual(row["evidence"]["evidence_state"], "benchmark_pass_non_cad")
                self.assertEqual(row["evidence"]["geometry_accuracy"], "not_verified_without_cad_readback")

        schema = json.loads(get_schema_path("cad_capability_registry").read_text(encoding="utf-8"))
        self.assertEqual(validate_value(registry, schema), [])
        self.assertEqual(validate_registry_claim_contracts(registry), [])


if __name__ == "__main__":
    unittest.main()
