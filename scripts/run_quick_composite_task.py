#!/usr/bin/env python3
"""Run generic current-DWG quick composite CAD tasks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.cad_io.autocad_com import AutoCADComDriver  # noqa: E402
from core.quick_tasks import run_find_and_annotate_bbox_dimensions  # noqa: E402


DEFAULT_CACHE = PROJECT_ROOT / "output" / "cache" / "current_dwg_block_cache.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "output" / "validation_runs" / "quick-composite" / "quick_composite_report.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a generic lightweight current-DWG composite CAD task.")
    parser.add_argument(
        "--task",
        default="find_and_annotate_bbox_dimensions",
        choices=["find_and_annotate_bbox_dimensions"],
    )
    parser.add_argument("--query", required=True)
    parser.add_argument("--visual-hint", default="")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--cache-path", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--refresh-cache", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Plan and report without writing CAD entities.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    try:
        driver = AutoCADComDriver(connect_existing_only=True)
        if args.task == "find_and_annotate_bbox_dimensions":
            report = run_find_and_annotate_bbox_dimensions(
                driver,
                query=args.query,
                visual_hint=args.visual_hint or None,
                cache_path=args.cache_path,
                refresh_cache=args.refresh_cache,
                top_k=args.top_k,
                execute=not args.dry_run,
            )
        else:  # pragma: no cover - argparse choices prevent this.
            raise ValueError(f"Unsupported quick composite task: {args.task}")
        report["mode"] = "dry_run" if args.dry_run else "execute"
        report["cache_path"] = str(args.cache_path)
        _write_report(args.output, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report.get("status") == "pass" else 1
    except Exception as exc:
        payload = {
            "status": "blocked",
            "failure_category": "quick_composite_task_failed",
            "message": str(exc),
            "output": str(args.output),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1


def _write_report(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
