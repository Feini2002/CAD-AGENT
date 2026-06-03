#!/usr/bin/env python3
"""Plan or archive stale training screenshot artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.training.artifact_retention import run_training_artifact_retention  # noqa: E402


DEFAULT_OUTPUT = PROJECT_ROOT / "output" / "validation_runs" / "training-artifact-retention" / "retention_report.json"


def default_scan_roots(root: Path) -> list[Path]:
    return [
        root / "output" / "previews",
        root / "output" / "training_queues",
    ]


def default_reference_roots(root: Path) -> list[Path]:
    return [
        root / "docs" / "training",
        root / "agents",
        root / "output" / "training_queues",
        root / "output" / "training_learning",
        root / "output" / "validation_runs" / "training-workbench-sync",
        root / "docs" / "status",
        root / "capability-map-data.js",
    ]


def run_default_training_artifact_retention(
    *,
    project_root: Path = PROJECT_ROOT,
    write: bool = False,
    output_path: Path | None = DEFAULT_OUTPUT,
) -> dict[str, Any]:
    root = project_root.resolve()
    return run_training_artifact_retention(
        project_root=root,
        scan_roots=default_scan_roots(root),
        reference_roots=default_reference_roots(root),
        write=write,
        output_path=output_path,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan or archive stale training screenshot artifacts.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--scan-root", action="append", type=Path, dest="scan_roots")
    parser.add_argument("--reference-root", action="append", type=Path, dest="reference_roots")
    parser.add_argument("--archive-root", type=Path)
    parser.add_argument("--keep-latest-per-dir", type=int, default=1)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true", help="Move unreferenced old screenshots into the archive.")
    args = parser.parse_args()

    root = args.project_root.resolve()
    report = run_training_artifact_retention(
        project_root=root,
        scan_roots=args.scan_roots or default_scan_roots(root),
        reference_roots=args.reference_roots or default_reference_roots(root),
        archive_root=args.archive_root,
        keep_latest_per_dir=args.keep_latest_per_dir,
        write=args.write,
        output_path=args.output,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
