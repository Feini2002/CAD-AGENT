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
        self.assertEqual(classify_path("agents/pipeline/asset_librarian.py"), "agents")
        self.assertEqual(classify_path("openspec/changes/asset-flow/tasks.md"), "openspec")
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
        self.assertEqual(report["summary"]["severity_counts"]["low"], 2)
        self.assertEqual(report["summary"]["severity_counts"]["medium"], 2)
        self.assertEqual(report["summary"]["blocking_severity"], "medium")
        self.assertEqual(report["summary"]["blocking_finding_count"], 2)

    def test_groups_untracked_files_by_area_and_directory(self) -> None:
        report = build_dev_volume_report(
            PROJECT_ROOT,
            status_text=(
                "?? agents/pipeline/asset_librarian.py\n"
                "?? agents/pipeline/asset_reuse_auditor.py\n"
                "?? openspec/changes/asset-flow/tasks.md\n"
                "?? tests/core/test_asset_flow.py\n"
                "?? scripts/new_tool.py\n"
            ),
            numstat_text="",
        )

        self.assertEqual(report["untracked_by_area"]["agents"], 2)
        self.assertEqual(report["untracked_by_area"]["openspec"], 1)
        self.assertEqual(report["untracked_by_area"]["tests"], 1)
        self.assertEqual(report["untracked_by_area"]["scripts"], 1)
        self.assertEqual(report["untracked_groups"]["agents/pipeline"], 2)
        self.assertEqual(report["untracked_groups"]["openspec/changes"], 1)
        self.assertEqual(report["untracked_groups"]["tests/core"], 1)
        self.assertEqual(report["untracked_groups"]["scripts/new_tool.py"], 1)

    def test_groups_tracked_and_all_changed_files_by_directory(self) -> None:
        report = build_dev_volume_report(
            PROJECT_ROOT,
            status_text=(
                " M core/training/a.py\n"
                " M core/training/b.py\n"
                " M scripts/tool.py\n"
                "?? core/training/new.py\n"
                "?? docs/training/new.md\n"
            ),
            numstat_text=(
                "10\t1\tcore/training/a.py\n"
                "5\t0\tcore/training/b.py\n"
                "2\t1\tscripts/tool.py\n"
            ),
        )

        self.assertEqual(report["tracked_by_area"]["core_code"], 2)
        self.assertEqual(report["tracked_by_area"]["scripts"], 1)
        self.assertEqual(report["tracked_groups"]["core/training"], 2)
        self.assertEqual(report["tracked_groups"]["scripts/tool.py"], 1)
        self.assertEqual(report["changed_groups"]["core/training"], 3)
        self.assertEqual(report["changed_groups"]["docs/training"], 1)
        self.assertEqual(report["by_group_line_delta"]["core/training"]["additions"], 15)
        self.assertEqual(report["by_group_line_delta"]["core/training"]["deletions"], 1)
        self.assertEqual(report["by_group_line_delta"]["scripts/tool.py"]["additions"], 2)
        self.assertEqual(report["by_group_line_delta"]["scripts/tool.py"]["deletions"], 1)

    def test_reports_top_groups_for_package_scoping(self) -> None:
        report = build_dev_volume_report(
            PROJECT_ROOT,
            status_text=(
                " M core/training/a.py\n"
                " M core/training/b.py\n"
                "?? core/training/new.py\n"
                " M tests/core/test_a.py\n"
                "?? scripts/new_tool.py\n"
            ),
            numstat_text=(
                "10\t1\tcore/training/a.py\n"
                "5\t0\tcore/training/b.py\n"
                "20\t3\ttests/core/test_a.py\n"
            ),
        )

        self.assertEqual(report["top_changed_groups"][0]["group"], "core/training")
        self.assertEqual(report["top_changed_groups"][0]["changed_files"], 3)
        self.assertEqual(report["top_changed_groups"][0]["tracked_files"], 2)
        self.assertEqual(report["top_changed_groups"][0]["untracked_files"], 1)
        self.assertEqual(report["top_changed_groups"][0]["additions"], 15)
        self.assertEqual(report["top_changed_groups"][0]["deletions"], 1)
        self.assertEqual(report["top_untracked_groups"][0]["group"], "core/training")
        self.assertEqual(report["top_tracked_groups"][0]["group"], "core/training")

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

    def test_cli_fail_on_severity_allows_low_findings(self) -> None:
        root = artifact_path("dev_volume_audit", f"cli_low_severity_{uuid.uuid4().hex}")
        root.mkdir(parents=True, exist_ok=True)
        tracked = root / "tracked.txt"
        tracked.write_text("old\n", encoding="utf-8")
        subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
        subprocess.run(["git", "add", "tracked.txt"], cwd=root, check=True, capture_output=True)
        tracked.write_text("old\nnew\n", encoding="utf-8")

        completed = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "run_dev_volume_audit.py"),
                "--root",
                str(root),
                "--max-insertions",
                "0",
                "--fail-on-severity",
                "medium",
            ],
            cwd=PROJECT_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["summary"]["finding_count"], 1)
        self.assertEqual(report["summary"]["blocking_finding_count"], 0)

    def test_cli_fail_on_severity_blocks_medium_findings(self) -> None:
        root = artifact_path("dev_volume_audit", f"cli_medium_severity_{uuid.uuid4().hex}")
        root.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
        (root / "new.txt").write_text("new\n", encoding="utf-8")

        completed = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "run_dev_volume_audit.py"),
                "--root",
                str(root),
                "--max-untracked-files",
                "0",
                "--fail-on-severity",
                "medium",
            ],
            cwd=PROJECT_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )

        self.assertEqual(completed.returncode, 1)
        report = json.loads(completed.stdout)
        self.assertEqual(report["summary"]["blocking_finding_count"], 1)

    def test_cli_summary_only_emits_compact_report(self) -> None:
        root = artifact_path("dev_volume_audit", f"cli_summary_only_{uuid.uuid4().hex}")
        root.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
        package_dir = root / "core" / "training"
        package_dir.mkdir(parents=True)
        tracked = package_dir / "tracked.py"
        tracked.write_text("old\n", encoding="utf-8")
        subprocess.run(["git", "add", "core/training/tracked.py"], cwd=root, check=True, capture_output=True)
        tracked.write_text("old\nnew\n", encoding="utf-8")
        (package_dir / "new.py").write_text("new\n", encoding="utf-8")

        completed = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "run_dev_volume_audit.py"),
                "--root",
                str(root),
                "--summary-only",
                "--top-groups",
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
        self.assertIn("summary", report)
        self.assertIn("top_changed_groups", report)
        self.assertEqual(len(report["top_changed_groups"]), 1)
        self.assertEqual(report["top_changed_groups"][0]["group"], "core/training")
        self.assertNotIn("changed_groups", report)
        self.assertNotIn("by_group_line_delta", report)


if __name__ == "__main__":
    unittest.main()
