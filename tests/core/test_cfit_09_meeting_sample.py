from __future__ import annotations

import unittest
from pathlib import Path

from core.agents.commercial_fitout_sample_confirmation import run_fitout_sample_pre_confirmation
from core.agents.fitout_sample_specs import resolve_fitout_sample_spec
from core.project_samples.protocol import scan_project_sample, scan_projects_root
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class Cfit09MeetingSampleTests(unittest.TestCase):
    def test_meeting_sample_protocol_scan_passes(self) -> None:
        sample_dir = PROJECT_ROOT / "projects" / "commercial_fitout_meeting_sample"
        result = scan_project_sample(sample_dir, projects_root=PROJECT_ROOT / "projects")
        self.assertEqual(result["status"], "pass", result)

    def test_projects_root_includes_meeting_sample(self) -> None:
        report = scan_projects_root(PROJECT_ROOT / "projects")
        sample_ids = {item["sample_id"] for item in report["samples"]}
        self.assertEqual(report["status"], "pass")
        self.assertIn("commercial_fitout_meeting_sample", sample_ids)

    def test_meeting_sample_pre_confirmation_gate(self) -> None:
        spec = resolve_fitout_sample_spec("commercial_fitout_meeting_sample")
        output_dir = artifact_path("cfit_09", "meeting_pre_confirmation")
        workflow = PROJECT_ROOT / spec.workflow_rel
        result = run_fitout_sample_pre_confirmation(
            output_dir=output_dir,
            project_root=PROJECT_ROOT,
            workflow_path=workflow,
        )
        self.assertEqual(result["status"], "confirmation_pending", result)
        self.assertEqual(result["sample_id"], "commercial_fitout_meeting_sample")

    def test_boundary_doc_names_cfit_09_contract(self) -> None:
        text = Path("docs/verification/cfit_09_second_project_sample_boundary.md").read_text(encoding="utf-8")
        self.assertIn("CFIT-09-SECOND-PROJECT-SAMPLE", text)
        self.assertIn("commercial_fitout_meeting_sample", text)
        self.assertIn("RCAD-10", text)


if __name__ == "__main__":
    unittest.main()
