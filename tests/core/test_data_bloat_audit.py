from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any

from tests.helpers import PROJECT_ROOT, temporary_artifact_dir


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def write_workbench_snapshot(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"window.CAD_CAPABILITY_MAP_DATA = {json.dumps(payload, ensure_ascii=False)};\n",
        encoding="utf-8",
    )


class DataBloatAuditTests(unittest.TestCase):
    def test_audit_blocks_missing_fact_sources_and_missing_coverage_evidence_without_cleanup(self) -> None:
        from core.maintenance.data_bloat_audit import run_data_bloat_audit

        with temporary_artifact_dir("data_bloat_audit_blocked") as root:
            write_json(root / "reports" / "final_report.json", {"status": "pass"})
            write_json(
                root / "docs" / "training" / "training-sources.json",
                {
                    "schemaVersion": 1,
                    "sources": [
                        {
                            "id": "final-report",
                            "kind": "training_acceptance_report",
                            "role": "fact_source",
                            "path": "reports/final_report.json",
                            "status": "active",
                        },
                        {
                            "id": "missing-report",
                            "kind": "training_acceptance_report",
                            "role": "fact_source",
                            "path": "reports/missing_report.json",
                            "status": "active",
                        },
                        {
                            "id": "workbench-snapshot",
                            "kind": "workbench_snapshot",
                            "role": "derived",
                            "path": "capability-map-data.js",
                            "status": "active",
                        },
                    ],
                },
            )
            write_json(
                root / "output" / "validation_runs" / "capability-lab" / "cad_capability_coverage.json",
                {
                    "evidence_path_audit": {
                        "report_path_missing": 2,
                        "missing_report_paths": ["reports/missing_a.json", "reports/missing_b.json"],
                    }
                },
            )
            write_workbench_snapshot(
                root / "capability-map-data.js",
                {
                    "schemaVersion": 2,
                    "trainingPrograms": [{"id": "program-a"}],
                    "agentProfiles": [],
                    "trainingStageColumns": [],
                    "tableCBoundary": {},
                    "capabilities": [{"id": "program-a"}],
                    "agents": [],
                    "stages": [],
                    "coverageSnapshot": {},
                },
            )
            (root / "output" / "debug").mkdir(parents=True)
            (root / "output" / "debug" / "retry.json").write_text("{}", encoding="utf-8")
            (root / "output" / "test_artifacts").mkdir(parents=True)
            (root / "output" / "test_artifacts" / "tmp.txt").write_text("tmp", encoding="utf-8")

            report = run_data_bloat_audit(
                project_root=root,
                size_warning_bytes=10,
                line_warning_count=1,
            )

            self.assertEqual(report["status"], "blocked")
            self.assertFalse(report["write"])
            blocked_codes = {item["code"] for item in report["blocked"]}
            self.assertIn("active_fact_source_missing", blocked_codes)
            self.assertIn("coverage_report_path_missing", blocked_codes)
            protected_paths = {item["path"] for item in report["protected"]}
            self.assertIn("reports/final_report.json", protected_paths)
            derived_paths = {item["path"] for item in report["derived"]}
            self.assertIn("capability-map-data.js", derived_paths)
            candidate_paths = {item["path"] for item in report["candidate"]}
            self.assertIn("output/debug/retry.json", candidate_paths)
            self.assertIn("output/test_artifacts/tmp.txt", candidate_paths)
            snapshot = report["ratchet"]["capabilityMapData"]
            self.assertGreater(snapshot["bytes"], 10)
            self.assertIn("legacy_alias_present", {warning["code"] for warning in snapshot["warnings"]})

    def test_cli_returns_warning_success_for_size_ratchet_without_blockers(self) -> None:
        with temporary_artifact_dir("data_bloat_audit_cli_warning") as root:
            write_json(root / "reports" / "final_report.json", {"status": "pass"})
            write_json(
                root / "docs" / "training" / "training-sources.json",
                {
                    "schemaVersion": 1,
                    "sources": [
                        {
                            "id": "final-report",
                            "kind": "training_acceptance_report",
                            "role": "fact_source",
                            "path": "reports/final_report.json",
                            "status": "active",
                        }
                    ],
                },
            )
            write_json(
                root / "output" / "validation_runs" / "capability-lab" / "cad_capability_coverage.json",
                {"evidence_path_audit": {"report_path_missing": 0}},
            )
            write_workbench_snapshot(
                root / "capability-map-data.js",
                {"schemaVersion": 2, "trainingPrograms": [{"id": "program-a"}]},
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_ROOT / "scripts" / "run_data_bloat_audit.py"),
                    "--project-root",
                    str(root),
                    "--summary-only",
                    "--size-warning-bytes",
                    "10",
                    "--line-warning-count",
                    "1",
                ],
                cwd=PROJECT_ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(completed.stdout)
            self.assertEqual(report["status"], "warning")
            self.assertEqual(report["blocked"], [])
            self.assertEqual(report["outputPath"], None)

    def test_derived_workbench_snapshot_registered_as_fact_source_is_blocked(self) -> None:
        from core.maintenance.data_bloat_audit import run_data_bloat_audit

        with temporary_artifact_dir("data_bloat_audit_derived_fact") as root:
            write_json(
                root / "docs" / "training" / "training-sources.json",
                {
                    "schemaVersion": 1,
                    "sources": [
                        {
                            "id": "bad-workbench-source",
                            "kind": "workbench_snapshot",
                            "role": "fact_source",
                            "path": "capability-map-data.js",
                            "status": "active",
                        }
                    ],
                },
            )
            write_json(
                root / "output" / "validation_runs" / "capability-lab" / "cad_capability_coverage.json",
                {"evidence_path_audit": {"report_path_missing": 0}},
            )
            write_workbench_snapshot(root / "capability-map-data.js", {"schemaVersion": 2})

            report = run_data_bloat_audit(project_root=root)

            self.assertEqual(report["status"], "blocked")
            self.assertIn("derived_artifact_registered_as_fact_source", {item["code"] for item in report["blocked"]})

    def test_derived_audit_report_is_not_promoted_to_fact_source(self) -> None:
        from core.maintenance.data_bloat_audit import run_data_bloat_audit

        with temporary_artifact_dir("data_bloat_audit_derived_report") as root:
            write_json(root / "reports" / "final_report.json", {"status": "pass"})
            write_json(root / "output" / "validation_runs" / "data-bloat" / "retention_report.json", {"status": "pass"})
            write_json(
                root / "docs" / "training" / "training-sources.json",
                {
                    "schemaVersion": 1,
                    "sources": [
                        {
                            "id": "final-report",
                            "kind": "training_acceptance_report",
                            "role": "fact_source",
                            "path": "reports/final_report.json",
                            "status": "active",
                        },
                        {
                            "id": "retention-report",
                            "kind": "retention_report",
                            "role": "derived",
                            "path": "output/validation_runs/data-bloat/retention_report.json",
                            "status": "active",
                        },
                    ],
                },
            )
            write_json(
                root / "output" / "validation_runs" / "capability-lab" / "cad_capability_coverage.json",
                {"evidence_path_audit": {"report_path_missing": 0}},
            )
            write_workbench_snapshot(root / "capability-map-data.js", {"schemaVersion": 2})

            report = run_data_bloat_audit(project_root=root)

            self.assertEqual(report["status"], "pass")
            protected_paths = {item["path"] for item in report["protected"]}
            derived_paths = {item["path"] for item in report["derived"]}
            self.assertIn("reports/final_report.json", protected_paths)
            self.assertIn("output/validation_runs/data-bloat/retention_report.json", derived_paths)
            self.assertNotIn("output/validation_runs/data-bloat/retention_report.json", protected_paths)


if __name__ == "__main__":
    unittest.main()
