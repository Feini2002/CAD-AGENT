"""Batch symbol glyph CAD smoke for six archetype specs (V-PROOF-32)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from core.path_safety import find_project_root, resolve_under_project_output, resolve_under_project_root
from core.plan_engine.validate_plan import load_json
from core.verification.symbol_glyph_cad_smoke import run_symbol_glyph_cad_smoke

DEFAULT_MANIFEST = Path("examples") / "capability_proof" / "symbol_glyph_cad_matrix_manifest.json"
MATRIX_BASE_Y_STEP = 1800.0


def load_symbol_glyph_cad_matrix_manifest(path: Path) -> dict[str, Any]:
    manifest = load_json(path)
    if manifest.get("manifest_id") != "symbol_glyph_cad_matrix":
        raise ValueError("symbol_glyph_cad_matrix manifest_id must be 'symbol_glyph_cad_matrix'.")
    cases = manifest.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("symbol_glyph_cad_matrix requires a non-empty cases array.")
    return manifest


def run_symbol_glyph_cad_matrix(
    *,
    root: Path,
    output_dir: Path,
    manifest_path: Path | None = None,
    include_cad: bool = True,
    base_x: float = 56000.0,
    base_y: float = 32000.0,
    driver_factory: Callable[[], Any] | None = None,
) -> dict[str, Any]:
    manifest_path = manifest_path or (root / DEFAULT_MANIFEST)
    manifest = load_symbol_glyph_cad_matrix_manifest(manifest_path)
    output_dir = resolve_under_project_output(root, output_dir, label="output_dir")
    output_dir.mkdir(parents=True, exist_ok=True)

    case_results: list[dict[str, Any]] = []
    for index, item in enumerate(manifest["cases"]):
        case_id = str(item["case_id"])
        spec_path = resolve_under_project_root(root, Path(str(item["symbol_spec_path"])), label="symbol_spec_path")
        case_output = output_dir / case_id
        base_point = [base_x, base_y + index * MATRIX_BASE_Y_STEP, 0.0]
        smoke_report = run_symbol_glyph_cad_smoke(
            symbol_spec_path=spec_path,
            base_point=base_point,
            output_dir=case_output,
            include_cad=include_cad,
            driver_factory=driver_factory,
            project_root=root,
        )
        case_results.append(
            {
                "case_id": case_id,
                "registry_capability_id": str(item.get("registry_capability_id", "")),
                "symbol_spec_path": str(spec_path.relative_to(root)).replace("\\", "/"),
                "status": smoke_report.get("status"),
                "geometry_verified": bool(smoke_report.get("geometry_verified")),
                "report_path": str(case_output / "symbol_glyph_cad_smoke_report.json"),
                "symbol_id": smoke_report.get("symbol_id", ""),
                "created_handle_count": smoke_report.get("created_handle_count", 0),
            }
        )

    verified_count = sum(1 for row in case_results if row.get("geometry_verified"))
    all_verified = verified_count == len(case_results) and verified_count > 0
    all_deferred_no_cad = (
        not include_cad
        and all(row.get("status") == "deferred" for row in case_results)
        and len(case_results) > 0
    )
    if all_verified:
        status = "geometry_verified"
    elif all_deferred_no_cad:
        status = "deferred"
    elif any(row.get("status") == "external_blocker" for row in case_results):
        status = "external_blocker"
    else:
        status = "failed"

    report = {
        "version": "0.1",
        "suite_id": "symbol_glyph_cad_matrix",
        "status": status,
        "geometry_verified": all_verified,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "manifest_path": str(manifest_path.relative_to(root)).replace("\\", "/"),
        "output_dir": str(output_dir),
        "case_count": len(case_results),
        "verified_case_count": verified_count,
        "cases": case_results,
    }
    (output_dir / "symbol_glyph_cad_matrix_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run six-archetype symbol glyph CAD matrix.")
    parser.add_argument("--root", type=Path, default=find_project_root(Path(__file__)))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--no-cad", action="store_true")
    parser.add_argument("--base-x", type=float, default=56000.0)
    parser.add_argument("--base-y", type=float, default=32000.0)
    args = parser.parse_args()

    root = args.root.resolve()
    report = run_symbol_glyph_cad_matrix(
        root=root,
        output_dir=args.output_dir,
        manifest_path=args.manifest,
        include_cad=not args.no_cad,
        base_x=args.base_x,
        base_y=args.base_y,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] in {"geometry_verified", "deferred"}:
        return 0
    if report["status"] == "external_blocker":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
