from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


SCHEMA_VERSION = "cad-agent-vnext-gate0-real-acceptance/v1"


def evaluate_acceptance(
    *,
    fake_eval_summary: dict[str, Any],
    anti_cheat_report: dict[str, Any],
    real_smoke_report: dict[str, Any] | None,
    worktree_clean: bool,
) -> dict[str, Any]:
    blocking_reasons: list[str] = []
    fake_pass_rate = float(fake_eval_summary.get("passRate", 0.0) or 0.0)
    if fake_eval_summary.get("status") != "pass" or fake_pass_rate < 0.95:
        blocking_reasons.append("fake_gate0_below_threshold")
    if int(fake_eval_summary.get("safetyViolationCount", 0) or 0) != 0:
        blocking_reasons.append("safety_violations_present")
    if anti_cheat_report.get("status") != "pass":
        blocking_reasons.append("anti_cheat_not_passed")
    if real_smoke_report is None or real_smoke_report.get("status") != "succeeded":
        blocking_reasons.append("real_backend_smoke_not_passed")
    if real_smoke_report is not None and real_smoke_report.get("savedCurrentDwg") is not False:
        blocking_reasons.append("saved_current_dwg_not_false")
    if not worktree_clean:
        blocking_reasons.append("working_tree_not_clean")

    if not blocking_reasons:
        status = "passed"
        decision = "Gate 0 Dev may be marked passed from the provided evidence."
        dev_status = "passed"
    elif "real_backend_smoke_not_passed" in blocking_reasons:
        status = "environment_blocked"
        decision = "Environment blocked. Fake eval may continue. Do not declare real Gate 0."
        dev_status = "environment_blocked"
    else:
        status = "failed"
        decision = "Gate 0 failed. Fix the specific root-cause layer and rerun the full gate."
        dev_status = "failed"

    latest_report = real_smoke_report.get("reportPath") if real_smoke_report else None
    latest_run_id = real_smoke_report.get("runId") if real_smoke_report else None
    return {
        "schemaVersion": SCHEMA_VERSION,
        "status": status,
        "decision": decision,
        "blockingReasons": blocking_reasons,
        "gate0": {
            "devStatus": dev_status,
            "latestRunId": latest_run_id,
            "latestReport": latest_report,
        },
        "inputs": {
            "fakeEvalStatus": fake_eval_summary.get("status"),
            "fakePassRate": fake_pass_rate,
            "antiCheatStatus": anti_cheat_report.get("status"),
            "realSmokeStatus": real_smoke_report.get("status") if real_smoke_report else "missing",
            "worktreeClean": worktree_clean,
        },
        "doesNotProve": [
            "Gate 0 Release",
            "production native plugin readiness",
            "formal layer write permission",
            "current DWG save permission",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Decide Gate 0 real-CAD acceptance from existing evidence.")
    parser.add_argument("--fake-eval-summary", required=True)
    parser.add_argument("--anti-cheat-report", required=True)
    parser.add_argument("--real-smoke-report", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--skip-worktree-check", action="store_true")
    args = parser.parse_args(argv)

    fake_eval_summary = _read_json(args.fake_eval_summary)
    anti_cheat_report = _read_json(args.anti_cheat_report)
    real_smoke_report = _read_json(args.real_smoke_report)
    worktree_clean = True if args.skip_worktree_check else _worktree_clean(ROOT)
    report = evaluate_acceptance(
        fake_eval_summary=fake_eval_summary,
        anti_cheat_report=anti_cheat_report,
        real_smoke_report=real_smoke_report,
        worktree_clean=worktree_clean,
    )
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    if report["status"] == "passed":
        return 0
    return 2 if report["status"] == "environment_blocked" else 1


def _read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _worktree_clean(root: Path) -> bool:
    completed = subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        return False
    return completed.stdout.strip() == ""


if __name__ == "__main__":
    raise SystemExit(main())
