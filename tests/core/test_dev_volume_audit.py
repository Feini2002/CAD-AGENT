from __future__ import annotations

import json
import subprocess
import sys
import unittest
import uuid

from tests.helpers import PROJECT_ROOT, artifact_path

from core.maintenance.dev_volume_audit import (
    DevVolumeThresholds,
    build_dev_volume_report,
    classify_path,
    parse_numstat,
    parse_porcelain_status,
)


class DevVolumeAuditTests(unittest.TestCase):
    def test_classifies_paths_for_current_cad_agent_layout(self) -> None:
        self.assertEqual(classify_path("core/cad_io/autocad_com.py"), "core_code")
        self.assertEqual(classify_path("tests/core/test_x.py"), "tests")
        self.assertEqual(classify_path("docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md"), "handoff_docs")
        self.assertEqual(classify_path("output/validation_runs/x/report.json"), "evidence_output")
        self.assertEqual(
            classify_path("docs/verification/capability_showcase/showcase_index.json"),
            "docs",
        )

    def test_parses_git_status_and_numstat(self) -> None:
        status_rows = parse_porcelain_status(" M core/a.py\n?? docs/new.md\nA  scripts/tool.py\n")
        self.assertEqual([row["status"] for row in status_rows], ["M", "??", "A"])
        self.assertEqual(status_rows[1]["area"], "docs")

        numstat_rows = parse_numstat("10\t2\tcore/a.py\n-\t-\tassets/binary.bin\n")
        self.assertEqual(numstat_rows[0]["additions"], 10)
        self.assertEqual(numstat_rows[1]["deletions"], 0)

    def test_builds_report_and_flags_large_batches(self) -> None:
        report = build_dev_volume_report(
            PROJECT_ROOT,
            thresholds=DevVolumeThresholds(
                max_changed_files=2,
                max_insertions=5,
                max_untracked_files=0,
                max_single_file_insertions=6,
            ),
            status_text=" M core/a.py\n?? docs/new.md\n M tests/test_a.py\n",
            numstat_text="7\t1\tcore/a.py\n2\t0\ttests/test_a.py\n",
        )

        self.assertEqual(report["summary"]["changed_file_count"], 3)
        self.assertEqual(report["summary"]["untracked_file_count"], 1)
        codes = {finding["code"] for finding in report["findings"]}
        self.assertIn("large_changed_file_count", codes)
        self.assertIn("large_untracked_file_count", codes)
        self.assertIn("large_insertion_count", codes)
        self.assertIn("large_single_file_delta", codes)

    def test_cli_emits_json_report(self) -> None:
        root = artifact_path("dev_volume_audit", f"cli_case_{uuid.uuid4().hex}")
        root.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
        (root / "tracked.txt").write_text("old\n", encoding="utf-8")
        subprocess.run(["git", "add", "tracked.txt"], cwd=root, check=True, capture_output=True)
        (root / "new.txt").write_text("new\n", encoding="utf-8")

        completed = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "run_dev_volume_audit.py"),
                "--root",
                str(root),
            ],
            cwd=PROJECT_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["summary"]["changed_file_count"], 2)
        self.assertEqual(report["summary"]["untracked_file_count"], 1)


if __name__ == "__main__":
    unittest.main()
