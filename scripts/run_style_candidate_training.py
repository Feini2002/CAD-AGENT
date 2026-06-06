#!/usr/bin/env python3
"""Run the focused A/B/C style-candidate training case."""

from __future__ import annotations

import argparse
import ctypes
import json
import sys
from pathlib import Path
from typing import Any

try:
    from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path
except ModuleNotFoundError:
    from scripts._bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.training.style_candidate_training import TRAINING_ID, run_style_candidate_training  # noqa: E402


DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output" / "training_queues" / TRAINING_ID


def _switch_to_input_desktop() -> dict[str, Any]:
    if sys.platform != "win32":
        return {"status": "not_required", "reason": "non-Windows platform"}

    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    access = 0x0001 | 0x0002 | 0x0040 | 0x0080 | 0x0100
    input_desktop = user32.OpenInputDesktop(0, False, access)
    if not input_desktop:
        return {"status": "fail", "api": "OpenInputDesktop", "lastError": int(kernel32.GetLastError())}
    ok = bool(user32.SetThreadDesktop(input_desktop))
    return {
        "status": "pass" if ok else "fail",
        "api": "SetThreadDesktop",
        "lastError": int(kernel32.GetLastError()),
        "reason": "AutoCAD COM runs on the interactive Default desktop.",
    }


def _driver(fake_cad: bool) -> Any:
    if fake_cad:
        from core.verification.fake_cad_driver import FakeCadDriver

        return FakeCadDriver()
    from core.cad_io.autocad_com import AutoCADComDriver

    return AutoCADComDriver(connect_existing_only=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run focused A/B/C style-candidate training.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--fake-cad", action="store_true", help="Use the in-memory fake CAD driver.")
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args(argv)

    desktop_switch = {"status": "skipped", "reason": "fake CAD driver"} if args.fake_cad else _switch_to_input_desktop()
    if desktop_switch.get("status") == "fail":
        payload = {
            "status": "external_blocker",
            "failure_category": "desktop_switch_failed",
            "desktopSwitch": desktop_switch,
            "outputDir": str(args.output_dir),
            "savedCurrentDwg": False,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2

    try:
        driver = _driver(args.fake_cad)
    except Exception as exc:
        payload = {
            "status": "external_blocker",
            "failure_category": "cad_connection_failed",
            "error": str(exc),
            "desktopSwitch": desktop_switch,
            "outputDir": str(args.output_dir),
            "savedCurrentDwg": False,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 2

    report = run_style_candidate_training(driver=driver, output_dir=args.output_dir, desktop_switch=desktop_switch)
    if args.summary_only:
        report = {
            "status": report.get("status"),
            "outputDir": str(args.output_dir),
            "desktopSwitch": desktop_switch,
            "styleCandidateIds": report.get("styleCandidateIds"),
            "executionStatus": report.get("execution", {}).get("status"),
            "readbackStatus": report.get("readback", {}).get("status"),
            "designReviewStatus": report.get("designReview", {}).get("status"),
            "askUserToChoose": report.get("askUserToChoose"),
            "savedCurrentDwg": report.get("safety", {}).get("savedCurrentDwg"),
        }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") == "needs_user_choice" else 1


if __name__ == "__main__":
    raise SystemExit(main())
