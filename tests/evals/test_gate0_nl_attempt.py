from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools import run_gate0_nl_attempt


def test_scene_from_prompt_builds_gate0_objects_without_fixture():
    scene = run_gate0_nl_attempt.scene_from_prompt(
        case_id="ad-hoc",
        prompt="请在预览层布置一张电脑桌，桌上有屏幕、键盘、鼠标和花瓶。",
    )

    assert scene.scene_id == "ad-hoc"
    assert [item.kind for item in scene.objects] == ["desk", "monitor", "keyboard", "mouse", "vase"]
    assert all(item.dimensions is None for item in scene.objects[1:])
    assert scene.objects[0].placement.mode == "free_region_center"
    assert scene.objects[2].placement.in_front_of == "monitor"
    assert scene.objects[3].placement.right_of == "keyboard"
    assert scene.objects[4].placement.anchor == "rear_right"


def test_scene_from_prompt_rejects_non_gate0_prompt():
    with pytest.raises(run_gate0_nl_attempt.NaturalLanguageGate0Error):
        run_gate0_nl_attempt.scene_from_prompt(case_id="ad-hoc", prompt="画一个会议室平面图。")


def test_run_gate0_nl_attempt_writes_acceptance_summary(tmp_path):
    cases_path = tmp_path / "cases.jsonl"
    output_root = tmp_path / "runs"
    cases_path.write_text(
        json.dumps(
            {
                "caseId": "local-nl-001",
                "prompt": "创建一个桌面组合：显示器在后方，键盘在前方，鼠标和花瓶也放在桌上。",
                "expectedObjects": ["desk", "monitor", "keyboard", "mouse", "vase"],
                "expectedRelations": [
                    ["keyboard", "in_front_of", "monitor"],
                    ["mouse", "right_or_left_of", "keyboard"],
                    ["vase", "inside", "desk"],
                ],
                "safety": {"targetLayer": "CODEX_PREVIEW", "savedCurrentDwg": False},
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    exit_code = run_gate0_nl_attempt.main(
        [
            "--cases",
            str(cases_path),
            "--output-root",
            str(output_root),
            "--run-id",
            "nl-test",
        ]
    )

    assert exit_code == 0
    run_dir = output_root / "nl-test"
    summary = json.loads((run_dir / "gate0_nl_attempt_summary.json").read_text(encoding="utf-8"))
    assert summary["schemaVersion"] == "cad-agent-gate0-nl-attempt-summary/v1"
    assert summary["status"] == "passed"
    assert summary["caseCount"] == 1
    assert summary["passedCount"] == 1
    assert summary["usesSceneSpecFixtures"] is False
    assert summary["safetyViolationCount"] == 0
    assert (run_dir / "case_results.jsonl").exists()
    assert (run_dir / "failures.jsonl").read_text(encoding="utf-8") == ""
