"""LCAD-14: strict rollup for LCAD-03 guard chain (write guard, negative CAD, capability probe)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from core.path_safety import find_project_root, resolve_under_project_output
from core.verification.cad_capability_probe import run_cad_capability_probe
from core.verification.evidence_contract import validate_capability_probe_evidence
from core.verification.evidence_vocabulary import NON_CAD_GEOMETRY_ACCURACY, SCREENSHOT_NOT_APPLICABLE
from core.verification.fake_cad_driver import FakeCadDriver
from core.verification.negative_cad_runner import run_negative_cad_runner
from core.verification.write_guard_cad_runner import run_write_guard_cad_runner

DriverFactory = Callable[[], Any]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _subreport_summary(report: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {"status": report.get("status")}
    for key in ("evidence_state", "mode", "suite_id"):
        if key in report:
            summary[key] = report[key]
    session_guard = report.get("session_guard")
    if isinstance(session_guard, dict):
        summary["session_guard_status"] = session_guard.get("status")
    return summary


def evaluate_guard_full_strict_gate(
    *,
    write_guard: dict[str, Any],
    negative_cad: dict[str, Any],
    capability_probe: dict[str, Any],
) -> dict[str, Any]:
    """Return strict gate status for the LCAD-03 guard chain sub-reports."""

    failures: list[str] = []

    if write_guard.get("status") != "pass":
        failures.append(f"write_guard.status={write_guard.get('status')!r}; expected 'pass'")

    negative_status = negative_cad.get("status")
    if negative_status != "pass":
        failures.append(f"negative_cad.status={negative_status!r}; expected 'pass'")
    elif negative_cad.get("evidence_state") != "negative_guard_verified":
        failures.append(
            "negative_cad.evidence_state="
            f"{negative_cad.get('evidence_state')!r}; expected 'negative_guard_verified'"
        )

    probe_error = validate_capability_probe_evidence(capability_probe)
    if probe_error:
        failures.append(probe_error)
    if capability_probe.get("status") != "cad_capability_verified":
        failures.append(
            f"capability_probe.status={capability_probe.get('status')!r}; expected 'cad_capability_verified'"
        )

    session_guard = capability_probe.get("session_guard")
    if not isinstance(session_guard, dict) or session_guard.get("status") != "consistent":
        failures.append("capability_probe.session_guard must be consistent for strict gate")

    return {
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "guard_chain": {
            "negative_plan_validation": write_guard.get("negative_cad_plans", {}).get("status"),
            "preview_write_guard": (
                write_guard.get("fake_write_guard", {}).get("status")
                if write_guard.get("fake_write_guard")
                else write_guard.get("real_write_guard", {}).get("status")
            ),
            "negative_cad_runner": negative_cad.get("status"),
            "capability_probe": capability_probe.get("status"),
            "session_snapshot_guard": (
                session_guard.get("status") if isinstance(session_guard, dict) else None
            ),
        },
    }


def _resolve_top_status(
    *,
    strict_gate: dict[str, Any],
    write_guard: dict[str, Any],
    negative_cad: dict[str, Any],
    capability_probe: dict[str, Any],
) -> str:
    section_statuses = [
        write_guard.get("status"),
        negative_cad.get("status"),
        capability_probe.get("status"),
        strict_gate.get("status"),
    ]
    if strict_gate.get("status") == "pass" and all(status == "pass" or status == "cad_capability_verified" for status in section_statuses[:3]):
        if capability_probe.get("status") == "cad_capability_verified":
            return "pass"
    if any(status == "external_blocker" for status in section_statuses):
        return "external_blocker"
    return "fail"


def run_guard_full_cad_runner(
    *,
    root: Path,
    output_dir: Path | None = None,
    use_real_cad: bool = False,
    strict: bool = True,
    driver_factory: DriverFactory | None = None,
) -> dict[str, Any]:
    """Run write-guard, negative CAD, and capability probe sub-reports with a strict rollup."""

    project_root = root.resolve()
    target_dir = (
        resolve_under_project_output(project_root, output_dir, label="output_dir")
        if output_dir is not None
        else None
    )
    subreports_root = target_dir / "subreports" if target_dir is not None else None

    write_guard_dir = subreports_root / "write_guard" if subreports_root is not None else None
    negative_dir = subreports_root / "negative_cad" if subreports_root is not None else None
    probe_dir = subreports_root / "capability_probe" if subreports_root is not None else None

    write_guard = run_write_guard_cad_runner(
        root=project_root,
        output_dir=write_guard_dir,
        include_fake_cad_guard=not use_real_cad,
        include_real_cad_guard=use_real_cad,
    )
    negative_cad = run_negative_cad_runner(
        root=project_root,
        output_dir=negative_dir,
        use_real_cad=use_real_cad,
        driver_factory=driver_factory,
    )

    if driver_factory is not None:
        probe_factory = driver_factory
    elif use_real_cad:
        from core.cad_io.autocad_com import AutoCADComDriver

        probe_factory = lambda: AutoCADComDriver(connect_existing_only=True)
    else:
        probe_factory = FakeCadDriver

    capability_probe = run_cad_capability_probe(
        driver_factory=probe_factory,
        output_dir=probe_dir,
    )

    strict_gate = (
        evaluate_guard_full_strict_gate(
            write_guard=write_guard,
            negative_cad=negative_cad,
            capability_probe=capability_probe,
        )
        if strict
        else {"status": "not_evaluated", "failures": [], "guard_chain": {}}
    )

    top_status = _resolve_top_status(
        strict_gate=strict_gate,
        write_guard=write_guard,
        negative_cad=negative_cad,
        capability_probe=capability_probe,
    )
    if strict and strict_gate.get("status") != "pass":
        top_status = "fail" if top_status != "external_blocker" else "external_blocker"

    report: dict[str, Any] = {
        "version": "0.1",
        "suite_id": "guard_full_cad_runner",
        "package_id": "LCAD-14-GUARD-FULL-CAD",
        "status": top_status,
        "generated_at": _utc_now_iso(),
        "mode": "real_cad" if use_real_cad else "fake_cad",
        "strict": strict,
        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY if not use_real_cad else capability_probe.get("geometry_accuracy"),
        "screenshot_role": SCREENSHOT_NOT_APPLICABLE,
        "strict_gate": strict_gate,
        "subreports": {
            "write_guard": _subreport_summary(write_guard),
            "negative_cad": _subreport_summary(negative_cad),
            "capability_probe": _subreport_summary(capability_probe),
        },
        "limitations": [
            "guard_full_cad strict pass proves LCAD-03 guard chain fields are present and internally consistent.",
            "fake_cad mode does not substitute for RCAD-21 real AutoCAD session strict re-verification.",
            "capability_probe geometry in fake mode is fake-driver readback only, not project DWG proof.",
        ],
    }

    if target_dir is not None:
        target_dir.mkdir(parents=True, exist_ok=True)
        report_path = target_dir / "guard_full_cad_report.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report["output_path"] = str(report_path.relative_to(project_root)).replace("\\", "/")
        report["subreport_paths"] = {
            "write_guard": "subreports/write_guard/write_guard_cad_runner_report.json",
            "negative_cad": "subreports/negative_cad/negative_cad_runner_report.json",
            "capability_probe": "subreports/capability_probe/cad_capability_probe.json",
            "active_document_snapshot": "subreports/capability_probe/active_document_snapshot.json",
        }

    return report


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="LCAD-14 guard chain strict rollup (write guard + negative CAD + probe).")
    parser.add_argument("--root", type=Path, default=find_project_root(Path(__file__)))
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--real-cad", action="store_true", help="Use active AutoCAD COM session for all sub-reports.")
    parser.add_argument("--no-strict", action="store_true", help="Write sub-reports without evaluating the strict gate.")
    args = parser.parse_args()

    report = run_guard_full_cad_runner(
        root=args.root,
        output_dir=args.output_dir,
        use_real_cad=args.real_cad,
        strict=not args.no_strict,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["status"] == "pass":
        return 0
    if report["status"] == "external_blocker":
        return 2
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
