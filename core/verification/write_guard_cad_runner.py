"""LCAD-10.2: combine negative CAD_PLAN validation with preview write-guard negative checks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.path_safety import find_project_root, resolve_under_project_output
from core.safety.write_guard import run_negative_write_guard_checks
from core.verification.fake_cad_driver import FakeCadDriver
from core.verification.negative_cad_plans import run_negative_cad_plan_suite


def run_write_guard_cad_runner(
    *,
    root: Path,
    output_dir: Path | None = None,
    include_fake_cad_guard: bool = True,
    include_real_cad_guard: bool = False,
) -> dict[str, Any]:
    negative_plans = run_negative_cad_plan_suite(root=root)
    fake_guard: dict[str, Any] | None = None
    real_guard: dict[str, Any] | None = None

    if include_fake_cad_guard:
        fake_guard = run_negative_write_guard_checks(FakeCadDriver())

    if include_real_cad_guard:
        try:
            from core.cad_io.autocad_com import AutoCADComDriver

            real_guard = run_negative_write_guard_checks(AutoCADComDriver(connect_existing_only=True))
        except Exception as exc:
            real_guard = {
                "status": "external_blocker",
                "error": str(exc),
                "checks": [],
            }

    sections = [negative_plans.get("status"), fake_guard.get("status") if fake_guard else "pass"]
    if real_guard is not None:
        sections.append(real_guard.get("status"))
    top_status = "pass" if all(status == "pass" for status in sections) else "fail"
    if real_guard and real_guard.get("status") == "external_blocker" and top_status != "pass":
        top_status = "external_blocker"

    report: dict[str, Any] = {
        "version": "0.1",
        "suite_id": "write_guard_cad_runner",
        "status": top_status,
        "negative_cad_plans": negative_plans,
        "fake_write_guard": fake_guard,
        "real_write_guard": real_guard,
    }
    if output_dir is not None:
        output_dir = resolve_under_project_output(root, output_dir, label="output_dir")
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "write_guard_cad_runner_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return report


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Negative CAD_PLAN + write-guard checks (LCAD-10.2).")
    parser.add_argument("--root", type=Path, default=find_project_root(Path(__file__)))
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--real-cad", action="store_true", help="Also run write-guard negatives on active AutoCAD.")
    args = parser.parse_args()

    root = args.root.resolve()
    report = run_write_guard_cad_runner(
        root=root,
        output_dir=args.output_dir,
        include_real_cad_guard=args.real_cad,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] == "pass":
        return 0
    if report["status"] == "external_blocker":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
