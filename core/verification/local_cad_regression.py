"""Local CAD regression matrix for CODEX_PREVIEW readback checks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.verification.local_cad_regression_manifest import (
    DEFAULT_MANIFEST_RELATIVE_PATH,
    load_regression_manifest,
)
from core.verification.local_cad_regression_matrix import run_local_cad_regression
from core.verification.local_cad_regression_runtime import default_command_runner

__all__ = [
    "DEFAULT_MANIFEST_RELATIVE_PATH",
    "load_regression_manifest",
    "run_local_cad_regression",
    "default_command_runner",
]

def main() -> int:
    parser = argparse.ArgumentParser(description="Run local CAD regression matrix for CODEX_PREVIEW checks.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output") / "validation_runs" / "local-cad-regression",
    )
    parser.add_argument("--no-cad", action="store_true", help="Run safe deferred matrix without connecting to AutoCAD.")
    parser.add_argument(
        "--require-cad-verified",
        action="store_true",
        help="Return non-zero unless real CAD checks produce geometry_verified evidence.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Alias for --require-cad-verified.",
    )
    parser.add_argument(
        "--case",
        dest="selected_case_ids",
        action="append",
        default=None,
        help="Run only a selected manifest case id. Repeat to run multiple cases. Default runs all manifest cases.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Optional local CAD regression manifest path. Relative paths are resolved under --root.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    output_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    require_cad_verified = args.require_cad_verified or args.strict
    report = run_local_cad_regression(
        root=root,
        output_dir=output_dir,
        include_cad=not args.no_cad,
        require_cad_verified=require_cad_verified,
        manifest_path=args.manifest,
        selected_case_ids=args.selected_case_ids,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] == "pass":
        return 0
    if report["status"] == "external_blocker":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
