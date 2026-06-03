from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest

from tests.helpers import PROJECT_ROOT, temporary_artifact_dir


class TrainingArtifactRetentionTests(unittest.TestCase):
    def test_dry_run_keeps_referenced_and_latest_preview_while_planning_unreferenced_archive(self) -> None:
        from core.training.artifact_retention import run_training_artifact_retention

        with temporary_artifact_dir("training_artifact_retention") as root:
            preview_dir = root / "output" / "previews"
            preview_dir.mkdir(parents=True)
            old_image = preview_dir / "old-preview.png"
            referenced_image = preview_dir / "referenced-preview.png"
            latest_image = preview_dir / "latest-preview.png"
            for image in (old_image, referenced_image, latest_image):
                image.write_bytes(b"png")
            for offset, image in enumerate((old_image, referenced_image, latest_image), start=1):
                os.utime(image, (1_700_000_000 + offset, 1_700_000_000 + offset))

            (root / "reports").mkdir()
            (root / "reports" / "final_report.json").write_text(
                json.dumps({"screenshot": "output/previews/referenced-preview.png"}),
                encoding="utf-8",
            )

            report = run_training_artifact_retention(
                project_root=root,
                scan_roots=[preview_dir],
                reference_roots=[root / "reports"],
                keep_latest_per_dir=1,
                write=False,
            )

            self.assertEqual(report["status"], "pass")
            self.assertFalse(report["write"])
            self.assertEqual(report["candidateCount"], 3)
            self.assertEqual(report["archivePlannedCount"], 1)
            self.assertEqual(report["archivedCount"], 0)
            self.assertTrue(old_image.is_file())
            self.assertEqual(
                {item["path"]: item["reason"] for item in report["kept"]},
                {
                    "output/previews/latest-preview.png": "latest_preview",
                    "output/previews/referenced-preview.png": "referenced",
                },
            )
            self.assertEqual(report["archivePlanned"][0]["path"], "output/previews/old-preview.png")

    def test_write_archives_only_unreferenced_old_images_without_deleting_reference_targets(self) -> None:
        from core.training.artifact_retention import run_training_artifact_retention

        with temporary_artifact_dir("training_artifact_retention_write") as root:
            preview_dir = root / "output" / "training_queues" / "queue-a"
            preview_dir.mkdir(parents=True)
            stale_image = preview_dir / "retry-preview.png"
            referenced_image = preview_dir / "accepted-preview.png"
            latest_image = preview_dir / "latest-preview.png"
            for image in (stale_image, referenced_image, latest_image):
                image.write_bytes(b"png")
            for offset, image in enumerate((stale_image, referenced_image, latest_image), start=1):
                os.utime(image, (1_700_000_000 + offset, 1_700_000_000 + offset))

            report_dir = root / "output" / "training_queues" / "queue-a"
            (report_dir / "accepted_report.json").write_text(
                json.dumps({"preview": "output/training_queues/queue-a/accepted-preview.png"}),
                encoding="utf-8",
            )

            report = run_training_artifact_retention(
                project_root=root,
                scan_roots=[preview_dir],
                reference_roots=[report_dir],
                archive_root=root / "archive",
                keep_latest_per_dir=1,
                write=True,
            )

            archived_path = root / "archive" / "output" / "training_queues" / "queue-a" / "retry-preview.png"
            self.assertEqual(report["status"], "pass")
            self.assertTrue(report["write"])
            self.assertFalse(stale_image.exists())
            self.assertTrue(archived_path.is_file())
            self.assertTrue(referenced_image.is_file())
            self.assertTrue(latest_image.is_file())
            self.assertEqual(report["archivedCount"], 1)
            self.assertEqual(report["archived"][0]["archivePath"], "archive/output/training_queues/queue-a/retry-preview.png")

    def test_cli_writes_dry_run_retention_report(self) -> None:
        with temporary_artifact_dir("training_artifact_retention_cli") as root:
            preview_dir = root / "output" / "previews"
            preview_dir.mkdir(parents=True)
            (preview_dir / "old.png").write_bytes(b"png")
            (preview_dir / "latest.png").write_bytes(b"png")
            output_path = root / "retention_report.json"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_ROOT / "scripts" / "run_training_artifact_retention.py"),
                    "--project-root",
                    str(root),
                    "--scan-root",
                    str(preview_dir),
                    "--reference-root",
                    str(root),
                    "--output",
                    str(output_path),
                ],
                cwd=PROJECT_ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(completed.stdout)
            self.assertFalse(report["write"])
            self.assertEqual(report["archivePlannedCount"], 1)
            self.assertTrue(output_path.is_file())


if __name__ == "__main__":
    unittest.main()
