"""LCAD-10.3 negative CAD runner with no-handle/no-save safety evidence."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from core.path_safety import find_project_root, resolve_under_project_output
from core.safety.policy import PREVIEW_LAYER
from core.safety.write_guard import run_negative_write_guard_checks
from core.verification.cad_session_guard import (
    blocked_snapshot,
    build_session_guard_report,
    capture_active_document_snapshot,
)
from core.verification.evidence_vocabulary import (
    EVIDENCE_NEGATIVE_GUARD_VERIFIED,
    NON_CAD_GEOMETRY_ACCURACY,
    SCREENSHOT_NOT_APPLICABLE,
)
from core.verification.fake_cad_driver import FakeCadDriver
from core.verification.negative_cad_plans import run_negative_cad_plan_suite


DriverFactory = Callable[[], Any]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _entity_count(snapshot: dict[str, Any]) -> int:
    summary = snapshot.get("modelspace_summary")
    if not isinstance(summary, dict):
        return 0
    try:
        return int(summary.get("entity_count", 0))
    except (TypeError, ValueError):
        return 0


def _augment_no_write_comparison(session_guard: dict[str, Any]) -> None:
    after_connect = session_guard.get("after_connect")
    after_write = session_guard.get("after_write")
    comparison = session_guard.get("comparison")
    if not isinstance(after_connect, dict) or not isinstance(after_write, dict) or not isinstance(comparison, dict):
        return

    before_count = _entity_count(after_connect)
    after_count = _entity_count(after_write)
    modelspace_delta = after_count - before_count
    comparison["modelspace_entity_delta"] = modelspace_delta
    checks = comparison.setdefault("checks", [])
    if isinstance(checks, list):
        checks.append(
            {
                "name": "modelspace_entity_delta_zero",
                "status": "pass" if modelspace_delta == 0 else "fail",
                "message": f"before={before_count} after={after_count} delta={modelspace_delta}",
            }
        )


def _build_driver(*, use_real_cad: bool, driver_factory: DriverFactory | None) -> tuple[Any | None, dict[str, Any] | None]:
    if driver_factory is not None:
        return driver_factory(), None
    if not use_real_cad:
        return FakeCadDriver(), None

    try:
        from core.cad_io.autocad_com import AutoCADComDriver

        return AutoCADComDriver(connect_existing_only=True), None
    except Exception as exc:
        return None, {
            "status": "external_blocker",
            "error": str(exc),
            "message": "Active AutoCAD COM session is unavailable for real negative CAD guard checks.",
        }


def run_negative_cad_runner(
    *,
    root: Path,
    output_dir: Path | None = None,
    use_real_cad: bool = False,
    driver_factory: DriverFactory | None = None,
) -> dict[str, Any]:
    """Run negative CAD_PLAN validation plus CAD write guards without creating handles."""

    project_root = root.resolve()
    generated_at = _utc_now_iso()
    negative_plans = run_negative_cad_plan_suite(root=project_root)
    before_connect = blocked_snapshot(phase="before_connect", reason="negative_runner_not_connected")
    driver, connection_blocker = _build_driver(use_real_cad=use_real_cad, driver_factory=driver_factory)

    if connection_blocker is not None:
        report: dict[str, Any] = {
            "version": "0.1",
            "suite_id": "negative_cad_runner",
            "status": "external_blocker",
            "generated_at": generated_at,
            "mode": "real_cad" if use_real_cad else "fake_cad",
            "evidence_state": "deferred_cad_readback_required",
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
            "negative_cad_plans": negative_plans,
            "connection": connection_blocker,
            "created_handles": [],
            "safety": {
                "layer": PREVIEW_LAYER,
                "saved_dwg": False,
                "deleted_entities": False,
                "modified_formal_layers": False,
            },
        }
    else:
        after_connect = capture_active_document_snapshot(driver, phase="after_connect")
        write_guard = run_negative_write_guard_checks(driver, preview_layer=PREVIEW_LAYER)
        after_write = capture_active_document_snapshot(driver, phase="after_negative_checks")
        session_guard = build_session_guard_report(
            before_connect=before_connect,
            after_connect=after_connect,
            after_write=after_write,
        )
        _augment_no_write_comparison(session_guard)

        comparison = session_guard.get("comparison") if isinstance(session_guard, dict) else None
        preview_delta = int(comparison.get("preview_layer_entity_delta", -1)) if isinstance(comparison, dict) else -1
        modelspace_delta = int(comparison.get("modelspace_entity_delta", -1)) if isinstance(comparison, dict) else -1
        failed_checks = []
        for section in (write_guard, session_guard):
            checks = section.get("checks") if isinstance(section, dict) else None
            if isinstance(checks, list):
                failed_checks.extend(
                    check for check in checks if isinstance(check, dict) and check.get("status") == "fail"
                )

        status = "pass"
        if negative_plans.get("status") != "pass" or write_guard.get("status") != "pass":
            status = "fail"
        if session_guard.get("status") not in {"consistent"}:
            status = "fail"
        if preview_delta != 0 or modelspace_delta != 0 or failed_checks:
            status = "fail"

        report = {
            "version": "0.1",
            "suite_id": "negative_cad_runner",
            "status": status,
            "generated_at": generated_at,
            "mode": "real_cad" if use_real_cad else "fake_cad",
            "evidence_state": EVIDENCE_NEGATIVE_GUARD_VERIFIED if status == "pass" else "invalid_configuration",
            "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
            "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
            "negative_cad_plans": negative_plans,
            "write_guard": write_guard,
            "session_guard": session_guard,
            "created_handles": [],
            "safety": {
                "layer": PREVIEW_LAYER,
                "saved_dwg": False,
                "deleted_entities": False,
                "modified_formal_layers": False,
            },
            "limitations": [
                "negative_guard_verified proves forbidden writes were blocked without new handles; it is not geometry proof.",
                "geometry accuracy for positive drawing still requires created-handle readback.",
            ],
        }

    if output_dir is not None:
        target_dir = resolve_under_project_output(project_root, output_dir, label="output_dir")
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "negative_cad_runner_report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        report["output_path"] = str((target_dir / "negative_cad_runner_report.json").relative_to(project_root)).replace(
            "\\",
            "/",
        )
    return report


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run LCAD-10.3 negative CAD safety runner.")
    parser.add_argument("--root", type=Path, default=find_project_root(Path(__file__)))
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--real-cad", action="store_true", help="Use active AutoCAD COM session instead of fake driver.")
    args = parser.parse_args()

    report = run_negative_cad_runner(
        root=args.root,
        output_dir=args.output_dir,
        use_real_cad=args.real_cad,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] == "pass":
        return 0
    if report["status"] == "external_blocker":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
