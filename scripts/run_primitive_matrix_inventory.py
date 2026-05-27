#!/usr/bin/env python3
"""Print primitive_matrix_cad manifest inventory (V-PROOF-12)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.verification.primitive_matrix_cad_manifest import (
    DEFAULT_PRIMITIVE_MATRIX_CAD_MANIFEST,
    load_primitive_matrix_cad_manifest,
    primitive_inventory_from_manifest,
    validate_primitive_matrix_cad_manifest,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and list primitive_matrix_cad manifest rows.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_PRIMITIVE_MATRIX_CAD_MANIFEST,
        help="Path to primitive_matrix_cad_manifest.json",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable summary JSON.")
    args = parser.parse_args()
    root = PROJECT_ROOT
    manifest_path = args.manifest if args.manifest.is_absolute() else root / args.manifest
    manifest = load_primitive_matrix_cad_manifest(manifest_path)
    errors = validate_primitive_matrix_cad_manifest(manifest)
    if errors:
        for message in errors:
            print(message, file=sys.stderr)
        return 1

    inventory = primitive_inventory_from_manifest(manifest)
    if args.json:
        payload = {
            "manifest_path": str(manifest_path),
            "primitive_count": len(inventory),
            "primitives": inventory,
            "regression_case": manifest.get("regression_case", {}),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(f"manifest: {manifest_path}")
    print(f"primitives ({len(inventory)}): {', '.join(inventory)}")
    regression = manifest.get("regression_case", {})
    print(f"regression_case.id: {regression.get('id', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
