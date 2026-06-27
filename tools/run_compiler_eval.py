from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from evals.compiler.anti_cheat import build_report as build_anti_cheat_report
from evals.compiler.grader import Gate0CaseResult, load_cases, run_case


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic compiler evals from prebuilt SceneSpec fixtures.")
    parser.add_argument("--backend", choices=["fake", "autocad-existing"], default="fake")
    parser.add_argument("--cases", default="evals/compiler/cases.jsonl")
    parser.add_argument("--output-root", default=".cad_agent_runs/evals/compiler")
    parser.add_argument("--eval-run-id")
    parser.add_argument("--root", default=".")
    args = parser.parse_args(argv)

    eval_run_id = args.eval_run_id or datetime.now().strftime("compiler_%Y%m%d_%H%M%S")
    run_dir = Path(args.output_root) / eval_run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    cases = load_cases(args.cases)
    results = [run_case(case, backend=args.backend) for case in cases]
    anti_cheat = build_anti_cheat_report(args.root)
    summary = _summary(results, anti_cheat_status=str(anti_cheat["status"]))
    safety_report = _safety_report(results)

    _write_json(run_dir / "summary.json", summary)
    _write_jsonl(run_dir / "case_results.jsonl", [result.to_json() for result in results])
    _write_jsonl(run_dir / "failures.jsonl", [result.to_json() for result in results if result.status != "passed"])
    _write_json(run_dir / "safety_report.json", safety_report)
    _write_json(run_dir / "anti_cheat_report.json", anti_cheat)
    (run_dir / "report.md").write_text(_markdown_report(summary, results, anti_cheat), encoding="utf-8")
    return 0 if summary["status"] == "pass" else 1


def _summary(results: list[Gate0CaseResult], *, anti_cheat_status: str) -> dict[str, object]:
    passed = [result for result in results if result.status == "passed"]
    safety_violations = [result for result in results if not result.safety_pass]
    status = "pass" if len(passed) == len(results) and anti_cheat_status == "pass" else "blocked"
    return {
        "schemaVersion": "cad-agent-compiler-eval-summary/v1",
        "status": status,
        "caseCount": len(results),
        "passedCount": len(passed),
        "failedCount": len(results) - len(passed),
        "passRate": round(len(passed) / len(results), 4) if results else 0.0,
        "safetyViolationCount": len(safety_violations),
        "antiCheatStatus": anti_cheat_status,
    }


def _safety_report(results: list[Gate0CaseResult]) -> dict[str, object]:
    return {
        "schemaVersion": "cad-agent-compiler-safety-report/v1",
        "status": "pass" if all(result.safety_pass for result in results) else "blocked",
        "safetyViolationCaseIds": [result.case_id for result in results if not result.safety_pass],
    }


def _markdown_report(summary: dict[str, object], results: list[Gate0CaseResult], anti_cheat: dict[str, object]) -> str:
    lines = [
        "# Compiler Eval Report",
        "",
        f"- status: `{summary['status']}`",
        f"- cases: `{summary['caseCount']}`",
        f"- passed: `{summary['passedCount']}`",
        f"- failed: `{summary['failedCount']}`",
        f"- safety violations: `{summary['safetyViolationCount']}`",
        f"- anti-cheat: `{anti_cheat['status']}`",
        "",
        "## Failures",
        "",
    ]
    failures = [result for result in results if result.status != "passed"]
    if not failures:
        lines.append("None.")
    for result in failures:
        lines.append(f"- `{result.case_id}`: `{result.failure_category}` {result.blocking_reasons}")
    lines.append("")
    return "\n".join(lines)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
