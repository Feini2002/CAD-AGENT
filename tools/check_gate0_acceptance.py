from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


SCHEMA_VERSION = "cad-agent-gate0-real-acceptance/v1"


def evaluate_acceptance(
    *,
    compiler_eval_summary: dict[str, Any],
    anti_cheat_report: dict[str, Any],
    real_smoke_report: dict[str, Any] | None,
    worktree_clean: bool,
    gate0_attempt_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    blocking_reasons: list[str] = []
    compiler_pass_rate = float(compiler_eval_summary.get("passRate", 0.0) or 0.0)
    if compiler_eval_summary.get("status") != "pass" or compiler_pass_rate < 0.95:
        blocking_reasons.append("compiler_eval_below_threshold")
    if int(compiler_eval_summary.get("safetyViolationCount", 0) or 0) != 0:
        blocking_reasons.append("safety_violations_present")
    if anti_cheat_report.get("status") != "pass":
        blocking_reasons.append("anti_cheat_not_passed")
    if real_smoke_report is None or real_smoke_report.get("status") != "succeeded":
        blocking_reasons.append("real_backend_smoke_not_passed")
    if real_smoke_report is not None and real_smoke_report.get("savedCurrentDwg") is not False:
        blocking_reasons.append("saved_current_dwg_not_false")
    if gate0_attempt_summary is None or gate0_attempt_summary.get("status") != "passed":
        blocking_reasons.append("natural_language_gate0_not_passed")
    if not worktree_clean:
        blocking_reasons.append("working_tree_not_clean")

    if not blocking_reasons:
        status = "passed"
        decision = "Gate 0 natural-language acceptance passed from provided evidence."
        dev_status = "passed"
    elif "real_backend_smoke_not_passed" in blocking_reasons:
        status = "environment_blocked"
        decision = "Environment blocked. Compiler eval may continue. Do not declare natural-language Gate 0."
        dev_status = "foundation_ready_acceptance_pending"
    else:
        status = "failed"
        decision = "Natural-language Gate 0 has not been proven. Fix the specific root-cause layer and rerun the full gate."
        dev_status = "foundation_ready_acceptance_pending"

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
            "compilerEvalStatus": compiler_eval_summary.get("status"),
            "compilerPassRate": compiler_pass_rate,
            "antiCheatStatus": anti_cheat_report.get("status"),
            "realSmokeStatus": real_smoke_report.get("status") if real_smoke_report else "missing",
            "gate0AttemptStatus": gate0_attempt_summary.get("status") if gate0_attempt_summary else "missing",
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
    parser.add_argument("--compiler-eval-summary", required=True)
    parser.add_argument("--anti-cheat-report", required=True)
    parser.add_argument("--real-smoke-report", required=True)
    parser.add_argument("--gate0-attempt-summary")
    parser.add_argument("--output", required=True)
    parser.add_argument("--skip-worktree-check", action="store_true")
    args = parser.parse_args(argv)

    compiler_eval_summary = _read_json(args.compiler_eval_summary)
    anti_cheat_report = _read_json(args.anti_cheat_report)
    real_smoke_report = _read_json(args.real_smoke_report)
    gate0_attempt_summary = _read_json(args.gate0_attempt_summary) if args.gate0_attempt_summary else None
    worktree_clean = True if args.skip_worktree_check else _worktree_clean(ROOT)
    report = evaluate_acceptance(
        compiler_eval_summary=compiler_eval_summary,
        anti_cheat_report=anti_cheat_report,
        real_smoke_report=real_smoke_report,
        gate0_attempt_summary=gate0_attempt_summary,
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
