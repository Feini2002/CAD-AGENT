#!/usr/bin/env python3
"""Interior delivery composition CAD + registry mapping (V-PROOF-43)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.path_safety import resolve_under_project_output
from core.verification.composition_cad_registry import run_composition_cad_registry


def main() -> int:
    parser = argparse.ArgumentParser(description="Composition CAD registry wave.")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--start-x", type=float, default=110000)
    parser.add_argument("--start-y", type=float, default=65000)
    parser.add_argument("--spacing-x", type=float, default=4200)
    parser.add_argument("--skip-benchmark", action="store_true")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=PROJECT_ROOT / "examples" / "capability_proof" / "composition_cad_registry_manifest.json",
        help="Composition CAD registry manifest (benchmark suite + case list).",
    )
    args = parser.parse_args()

    output_dir = resolve_under_project_output(PROJECT_ROOT, args.output_dir, label="output_dir")
    report = run_composition_cad_registry(
        root=PROJECT_ROOT,
        output_dir=output_dir,
        manifest_path=args.manifest,
        start_x=args.start_x,
        start_y=args.start_y,
        spacing_x=args.spacing_x,
        skip_benchmark=args.skip_benchmark,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("geometry_verified") else 1


if __name__ == "__main__":
    raise SystemExit(main())
