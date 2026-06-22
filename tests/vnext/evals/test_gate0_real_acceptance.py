from __future__ import annotations

import json
from pathlib import Path

from scripts.vnext.check_gate0_real_acceptance import evaluate_acceptance, main


def fake_summary(status: str = "pass", pass_rate: float = 1.0) -> dict[str, object]:
    return {
        "schemaVersion": "cad-agent-vnext-gate0-eval-summary/v1",
        "status": status,
        "caseCount": 12,
        "passedCount": 12 if status == "pass" else 8,
        "failedCount": 0 if status == "pass" else 4,
        "passRate": pass_rate,
        "safetyViolationCount": 0,
        "antiCheatStatus": "pass",
    }


def anti_cheat(status: str = "pass") -> dict[str, object]:
    return {"schemaVersion": "cad-agent-vnext-gate0-anti-cheat/v1", "status": status, "findings": []}


def real_smoke(status: str = "succeeded") -> dict[str, object]:
    return {
        "schemaVersion": "cad-agent-vnext-vn06-real-cad-smoke/v1",
        "status": status,
        "runId": "real-smoke",
        "reportPath": "output/vnext/runs/real-smoke/vn06_real_cad_backend_smoke.json",
        "blockingReasons": [] if status == "succeeded" else ["backend_unavailable:AutoCAD not active"],
        "savedCurrentDwg": False,
    }


def test_acceptance_blocks_when_real_smoke_has_not_passed():
    report = evaluate_acceptance(
        fake_eval_summary=fake_summary(),
        anti_cheat_report=anti_cheat(),
        real_smoke_report=real_smoke("blocked"),
        worktree_clean=True,
    )

    assert report["status"] == "environment_blocked"
    assert report["gate0"]["devStatus"] == "environment_blocked"
    assert "real_backend_smoke_not_passed" in report["blockingReasons"]
    assert "Do not declare real Gate 0." in report["decision"]


def test_acceptance_passes_when_all_preconditions_are_met():
    report = evaluate_acceptance(
        fake_eval_summary=fake_summary(),
        anti_cheat_report=anti_cheat(),
        real_smoke_report=real_smoke(),
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
            "--fake-eval-summary",
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
