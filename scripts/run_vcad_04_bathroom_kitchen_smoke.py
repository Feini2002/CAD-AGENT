#!/usr/bin/env python3
"""VCAD-04: residential bathroom + kitchen visual plan smoke."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.verification.visual_room_plan_smoke import (  # noqa: E402
    resolve_room_plan_output_dir,
    run_visual_room_plan_smoke,
)

VCAD_04_SCENES = ("bathroom", "kitchen")
DEFAULT_OUTPUT_ROOT = Path("output") / "validation_runs" / "vcad-04-20260528"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run VCAD-04 bathroom and kitchen visual CAD smoke.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Evidence root; each scene writes to <output-dir>/<scene>/",
    )
    parser.add_argument("--no-cad", action="store_true", help="Emit deferred reports without AutoCAD.")
    parser.add_argument(
        "--scene",
        choices=(*VCAD_04_SCENES, "all"),
        default="all",
        help="Run one scene or both (default: all).",
    )
    args = parser.parse_args()

    scenes = list(VCAD_04_SCENES) if args.scene == "all" else [args.scene]
    root = resolve_room_plan_output_dir(args.output_dir)
    results: dict[str, dict[str, object]] = {}
    exit_code = 0

    for scene in scenes:
        scene_dir = root / scene
        report = run_visual_room_plan_smoke(
            output_dir=scene_dir,
            include_cad=not args.no_cad,
            scene=scene,
        )
        results[scene] = {
            "status": report.get("status"),
            "created_handle_count": report.get("created_handle_count"),
            "type_counts": report.get("actual", {}).get("type_counts"),
            "output_dir": str(scene_dir),
        }
        if report.get("status") not in {"visual_geometry_verified", "deferred"}:
            exit_code = 1 if report.get("status") != "external_blocker" else 2

    manifest = {
        "version": "0.1",
        "suite_id": "vcad_04_bathroom_kitchen_smoke",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "scenes": results,
        "overall_pass": exit_code == 0,
    }
    root.mkdir(parents=True, exist_ok=True)
    (root / "vcad_04_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
