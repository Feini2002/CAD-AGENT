from __future__ import annotations

import unittest
from pathlib import Path

from core.agents.commercial_fitout_sample_confirmation import run_fitout_sample_pre_confirmation
from core.agents.fitout_sample_specs import FITOUT_SAMPLE_SPECS, resolve_fitout_sample_spec
from core.project_samples.protocol import scan_project_sample, scan_projects_root
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class Cfit10ReceptionSampleTests(unittest.TestCase):
    def test_reception_sample_protocol_scan_passes(self) -> None:
        sample_dir = PROJECT_ROOT / "projects" / "commercial_fitout_reception_sample"
        result = scan_project_sample(sample_dir, projects_root=PROJECT_ROOT / "projects")
        self.assertEqual(result["status"], "pass", result)

    def test_fitout_sample_specs_cover_three_subscenes(self) -> None:
        self.assertEqual(
            set(FITOUT_SAMPLE_SPECS),
            {
                "commercial_fitout_sample",
                "commercial_fitout_meeting_sample",
                "commercial_fitout_reception_sample",
            },
        )

    def test_reception_pre_confirmation_gate(self) -> None:
        spec = resolve_fitout_sample_spec("commercial_fitout_reception_sample")
        output_dir = artifact_path("cfit_10", "reception_pre_confirmation")
        result = run_fitout_sample_pre_confirmation(
            output_dir=output_dir,
            project_root=PROJECT_ROOT,
            workflow_path=PROJECT_ROOT / spec.workflow_rel,
        )
        self.assertEqual(result["status"], "confirmation_pending", result)
        self.assertEqual(result["sample_id"], "commercial_fitout_reception_sample")

    def test_boundary_doc_names_cfit_10_contract(self) -> None:
        text = Path("docs/verification/cfit_10_reception_project_sample_boundary.md").read_text(encoding="utf-8")
        self.assertIn("CFIT-10-RECEPTION-PROJECT-SAMPLE", text)
        self.assertIn("commercial_fitout_reception_sample", text)
        self.assertIn("RCAD-19", text)


if __name__ == "__main__":
    unittest.main()
