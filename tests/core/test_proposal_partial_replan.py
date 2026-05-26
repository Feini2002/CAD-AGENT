from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from core.proposal_engine.partial_replan import (
    apply_placement_offsets,
    recompute_cad_plans_from_pipeline_artifacts,
)
from core.workflows.blank_shell_pipeline import _object_spec_from_placement, run_blank_shell_pipeline
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ProposalPartialReplanTests(unittest.TestCase):
    def test_beta_proposal_04_partial_replan_skips_upstream_modules(self) -> None:
        output_dir = artifact_path("proposal_partial_replan", "retail_baseline")
        baseline = run_blank_shell_pipeline(
            PROJECT_ROOT / "examples/workflows/blank_shell_layout_loop.json",
            output_dir=output_dir,
        )
        self.assertEqual(baseline["status"], "ok", baseline.get("errors"))

        shell_hash = _file_hash(Path(baseline["artifacts"]["shell_model"]))
        candidate_sets_hash = _file_hash(Path(baseline["artifacts"]["candidate_sets"]))

        placements = json.loads(Path(baseline["artifacts"]["placements"]).read_text(encoding="utf-8"))
        object_specs = [_object_spec_from_placement(item) for item in placements if isinstance(item, dict)]
        self.assertGreaterEqual(len(object_specs), 1)
        first_spec_id = str(object_specs[0]["object_id"])

        before_plans = json.loads(Path(baseline["artifacts"]["cad_plans"]).read_text(encoding="utf-8"))
        before_base = before_plans[0]["placement"]["base_point"]

        report = recompute_cad_plans_from_pipeline_artifacts(
            output_dir,
            placement_offsets={str(first_spec_id): [250, 0, 0]},
        )
        self.assertEqual(report["status"], "ok", report)
        self.assertIn("shell_model", report["modules_skipped"])
        self.assertIn("cad_plan", report["modules_recomputed"])
        self.assertIn(str(first_spec_id), report["placement_offsets_applied"])

        self.assertEqual(_file_hash(Path(baseline["artifacts"]["shell_model"])), shell_hash)
        self.assertEqual(_file_hash(Path(baseline["artifacts"]["candidate_sets"])), candidate_sets_hash)

        after_plans = json.loads((output_dir / "cad_plans.json").read_text(encoding="utf-8"))
        after_base = after_plans[0]["placement"]["base_point"]
        self.assertNotEqual(before_base[0], after_base[0])

        replan_report_path = output_dir / "partial_replan_report.json"
        self.assertTrue(replan_report_path.is_file())
        dry_run = json.loads((output_dir / "dry_run_report.json").read_text(encoding="utf-8"))
        self.assertEqual(dry_run["status"], "valid")

    def test_apply_placement_offsets_updates_base_point(self) -> None:
        placements = [{"base_point": [10, 20, 0], "status": "placed"}]
        specs = [{"object_id": "object-test-1", "type": "desk", "name": "desk", "size": {"width": 1, "depth": 1, "height": 1}}]
        updated, applied = apply_placement_offsets(
            placements,
            specs,
            {"object-test-1": [5, -3, 0]},
        )
        self.assertEqual(applied, ["object-test-1"])
        self.assertEqual(updated[0]["base_point"], [15, 17, 0])


if __name__ == "__main__":
    unittest.main()
