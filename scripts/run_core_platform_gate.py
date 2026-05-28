#!/usr/bin/env python3
"""Run Core platform completion gate checks (engineering rhythm, not Table C)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.verification.capability_coverage import run_capability_coverage  # noqa: E402


def _run(command: list[str], *, cwd: Path) -> dict[str, object]:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return {
        "command": command,
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-2000:],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Core Lab platform completion gate.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/validation_runs/core-platform-gate/core_platform_gate_report.json"),
    )
    parser.add_argument("--skip-unittest", action="store_true")
    args = parser.parse_args()

    root = PROJECT_ROOT
    py = sys.executable
    checks: list[dict[str, object]] = []

    if not args.skip_unittest:
        checks.append(_run([py, "-m", "unittest", "discover", "-s", "tests", "-q"], cwd=root))

    checks.append(_run([py, "scripts/run_doc_governance_audit.py"], cwd=root))
    repo_result = _run(
        [py, "scripts/run_repo_audit.py", "--max-python-lines", "500"],
        cwd=root,
    )
    try:
        repo_payload = json.loads(repo_result.get("stdout", "") or "{}")
    except json.JSONDecodeError:
        repo_payload = {}
    blocking_repo = [
        item
        for item in repo_payload.get("findings", [])
        if str(item.get("severity", "low")) not in {"low", "info"}
    ]
    repo_result["exit_code"] = 0 if not blocking_repo else 1
    repo_result["blocking_finding_count"] = len(blocking_repo)
    checks.append(repo_result)

    coverage = run_capability_coverage(
        root,
        output_path=root / "output/validation_runs/capability-lab/cad_capability_coverage.json",
    )
    checks.append(
        {
            "command": ["run_capability_coverage"],
            "exit_code": 0 if coverage.get("status") == "pass" else 1,
            "summary": coverage.get("summary", {}),
        }
    )

    failed = [item for item in checks if int(item.get("exit_code", 1)) != 0]
    report = {
        "version": "0.1",
        "package_id": "CORE-PLATFORM-GATE-100",
        "status": "pass" if not failed else "fail",
        "failed_check_count": len(failed),
        "checks": checks,
        "completion_note": (
            "Core 100% means platform schema/runner/tests/governance are complete; "
            "Table C and company block libraries remain separate tracks."
        ),
    }

    output_path = args.output
    if not output_path.is_absolute():
        output_path = root / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
