from __future__ import annotations

import json
from pathlib import Path

from tools.check_gate0_acceptance import evaluate_acceptance, main


def fake_summary(status: str = "pass", pass_rate: float = 1.0) -> dict[str, object]:
    return {
        "schemaVersion": "cad-agent-compiler-eval-summary/v1",
        "status": status,
        "caseCount": 12,
        "passedCount": 12 if status == "pass" else 8,
        "failedCount": 0 if status == "pass" else 4,
        "passRate": pass_rate,
        "safetyViolationCount": 0,
        "antiCheatStatus": "pass",
    }


def anti_cheat(status: str = "pass") -> dict[str, object]:
    return {"schemaVersion": "cad-agent-compiler-anti-cheat/v1", "status": status, "findings": []}


def real_smoke(status: str = "succeeded") -> dict[str, object]:
    return {
        "schemaVersion": "cad-agent-real-cad-smoke/v1",
        "status": status,
        "runId": "real-smoke",
        "reportPath": ".cad_agent_runs/real-smoke/vn06_real_cad_backend_smoke.json",
        "blockingReasons": [] if status == "succeeded" else ["backend_unavailable:AutoCAD not active"],
        "savedCurrentDwg": False,
    }


def test_acceptance_blocks_when_real_smoke_has_not_passed():
    report = evaluate_acceptance(
        compiler_eval_summary=fake_summary(),
        anti_cheat_report=anti_cheat(),
        real_smoke_report=real_smoke("blocked"),
        worktree_clean=True,
    )

    assert report["status"] == "environment_blocked"
    assert report["gate0"]["devStatus"] == "foundation_ready_acceptance_pending"
    assert "real_backend_smoke_not_passed" in report["blockingReasons"]
    assert "Do not declare natural-language Gate 0." in report["decision"]


def test_acceptance_blocks_until_natural_language_gate0_is_proven():
    report = evaluate_acceptance(
        compiler_eval_summary=fake_summary(),
        anti_cheat_report=anti_cheat(),
        real_smoke_report=real_smoke(),
        worktree_clean=True,
    )

    assert report["status"] == "failed"
    assert report["gate0"]["devStatus"] == "foundation_ready_acceptance_pending"
    assert "natural_language_gate0_not_passed" in report["blockingReasons"]


def test_acceptance_passes_when_all_preconditions_are_met():
    report = evaluate_acceptance(
        compiler_eval_summary=fake_summary(),
        anti_cheat_report=anti_cheat(),
        real_smoke_report=real_smoke(),
        gate0_attempt_summary={"status": "passed"},
        worktree_clean=True,
    )

    assert report["status"] == "passed"
    assert report["gate0"]["devStatus"] == "passed"
    assert report["blockingReasons"] == []


def test_acceptance_script_writes_report(tmp_path):
    fake_path = write_json(tmp_path / "summary.json", fake_summary())
    anti_path = write_json(tmp_path / "anti.json", anti_cheat())
    smoke_path = write_json(tmp_path / "smoke.json", real_smoke("blocked"))
    output_path = tmp_path / "acceptance.json"

    exit_code = main(
        [
            "--compiler-eval-summary",
            str(fake_path),
            "--anti-cheat-report",
            str(anti_path),
            "--real-smoke-report",
            str(smoke_path),
            "--output",
            str(output_path),
            "--skip-worktree-check",
        ]
    )

    assert exit_code == 2
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["status"] == "environment_blocked"


def write_json(path: Path, payload: dict[str, object]) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path
