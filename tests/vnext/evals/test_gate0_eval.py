from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from evals.gate0.anti_cheat import build_report as build_anti_cheat_report
from evals.gate0.grader import classify_failure, load_cases, run_case
from scripts.vnext.run_gate0_eval import main as run_gate0_eval


ROOT = Path(__file__).resolve().parents[3]
CASES = ROOT / "evals" / "gate0" / "cases.jsonl"


def test_cases_file_has_required_public_groups():
    cases = load_cases(CASES)
    main_cases = [case for case in cases if case.group == "A.main"]

    assert len(main_cases) >= 10
    assert all({"desk", "monitor", "keyboard", "mouse"}.issubset(set(case.expected_objects)) for case in main_cases)
    assert all(case.backend == "fake" for case in cases)


def test_grader_passes_standard_fake_case():
    case = load_cases(CASES)[0]

    result = run_case(case, backend="fake")

    assert result.status == "passed"
    assert result.object_completeness == 1.0
    assert result.relation_satisfaction == 1.0
    assert result.safety_pass is True
    assert result.failure_category is None


def test_failure_classifier_uses_gate0_categories():
    assert classify_failure(["readback_missing:monitor"]) == "readback_failure"
    assert classify_failure(["outside_surface:mouse:desk"]) == "relation_solver_failure"
    assert classify_failure(["saved_current_dwg_true"]) == "safety_block_expected"
    assert classify_failure(["compile_result_missing_patch"]) == "compiler_failure"


def test_run_gate0_eval_writes_reports(tmp_path):
    exit_code = run_gate0_eval(["--backend", "fake", "--cases", str(CASES), "--output-root", str(tmp_path), "--eval-run-id", "eval-test"])

    assert exit_code == 0
    run_dir = tmp_path / "eval-test"
    assert (run_dir / "summary.json").exists()
    assert (run_dir / "case_results.jsonl").exists()
    assert (run_dir / "failures.jsonl").exists()
    assert (run_dir / "safety_report.json").exists()
    assert (run_dir / "anti_cheat_report.json").exists()
    assert (run_dir / "report.md").exists()

    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["schemaVersion"] == "cad-agent-vnext-gate0-eval-summary/v1"
    assert summary["status"] == "pass"
    assert summary["caseCount"] >= 10
    assert "coverage" not in json.dumps(summary).lower()


def test_run_gate0_eval_script_path_is_executable(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "vnext" / "run_gate0_eval.py"),
            "--backend",
            "fake",
            "--cases",
            str(CASES),
            "--output-root",
            str(tmp_path),
            "--eval-run-id",
            "eval-script-test",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert (tmp_path / "eval-script-test" / "summary.json").exists()


def test_anti_cheat_passes_current_tree_and_flags_prompt_leak(tmp_path):
    clean = build_anti_cheat_report(ROOT)

    assert clean["status"] == "pass"

    leaked_root = tmp_path / "leaked"
    (leaked_root / "src" / "cad_agent_vnext").mkdir(parents=True)
    (leaked_root / "evals" / "gate0").mkdir(parents=True)
    (leaked_root / ".agents" / "skills" / "cad-scene-authoring").mkdir(parents=True)
    (leaked_root / "evals" / "gate0" / "cases.jsonl").write_text(
        '{"caseId":"gate0-leak","prompt":"draw exact leaked prompt","backend":"fake","expectedObjects":[],"expectedRelations":[],"safety":{"targetLayer":"CODEX_PREVIEW","savedCurrentDwg":false}}\n',
        encoding="utf-8",
    )
    (leaked_root / "src" / "cad_agent_vnext" / "router.py").write_text(
        'PROMPT = "draw exact leaked prompt"\n',
        encoding="utf-8",
    )
    (leaked_root / ".agents" / "skills" / "cad-scene-authoring" / "SKILL.md").write_text(
        "hidden prompt fixture should not be here\\n",
        encoding="utf-8",
    )
    (leaked_root / "evals" / "gate0" / "hidden_cases.example.jsonl").write_text(
        '{"caseId":"hidden-001","prompt":"hidden prompt fixture"}\n',
        encoding="utf-8",
    )

    leaked = build_anti_cheat_report(leaked_root)

    assert leaked["status"] == "blocked"
    assert {finding["code"] for finding in leaked["findings"]} >= {"public_prompt_leaked_to_source", "hidden_prompt_leaked_to_skill"}
