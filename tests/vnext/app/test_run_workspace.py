from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor

import pytest

from cad_agent_vnext.app.run_service import begin_run
from cad_agent_vnext.app.run_workspace import RunWorkspace, new_run_id
from cad_agent_vnext.tools.envelopes import ToolEnvelope


RUN_ID_RE = re.compile(r"^run_\d{8}_\d{6}_[0-9a-f]{8}$")


def test_run_id_is_unique_and_not_second_only():
    first = new_run_id()
    second = new_run_id()

    assert first != second
    assert RUN_ID_RE.match(first)
    assert RUN_ID_RE.match(second)


def test_workspace_uses_configurable_output_root(tmp_path):
    output_root = tmp_path / "custom-runs"

    workspace = RunWorkspace.create(output_root=output_root, run_id="run_20260622_120000_abcdef12")

    assert workspace.root == output_root / "run_20260622_120000_abcdef12"
    assert (workspace.root / "screenshots").is_dir()
    assert (workspace.root / "debug").is_dir()
    assert (workspace.root / "events.jsonl").exists()


def test_path_escape_is_blocked(tmp_path):
    workspace = RunWorkspace.create(output_root=tmp_path, run_id="run_20260622_120000_abcdef12")

    with pytest.raises(ValueError, match="outside run root"):
        workspace.write_json_artifact("../escape.json", {"bad": True})


def test_json_artifact_is_stable_and_evented(tmp_path):
    workspace = RunWorkspace.create(output_root=tmp_path, run_id="run_20260622_120000_abcdef12")

    ref = workspace.write_json_artifact("scene_spec.json", {"z": 1, "a": {"b": 2}})

    assert ref == "scene_spec.json"
    assert (workspace.root / "scene_spec.json").read_text(encoding="utf-8") == '{\n  "a": {\n    "b": 2\n  },\n  "z": 1\n}\n'
    events = [json.loads(line) for line in (workspace.root / "events.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [event["sequence"] for event in events] == [1]
    assert events[0]["event"] == "artifact_written"
    assert events[0]["artifactRef"] == "scene_spec.json"


def test_concurrent_writes_do_not_leave_half_json(tmp_path):
    workspace = RunWorkspace.create(output_root=tmp_path, run_id="run_20260622_120000_abcdef12")

    def write(index: int) -> None:
        workspace.write_json_artifact("scene_spec.json", {"index": index, "items": list(range(index + 1))})

    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(write, range(12)))

    payload = json.loads((workspace.root / "scene_spec.json").read_text(encoding="utf-8"))
    assert isinstance(payload["index"], int)
    assert isinstance(payload["items"], list)


def test_debug_artifacts_are_not_evidence_refs(tmp_path):
    workspace = RunWorkspace.create(output_root=tmp_path, run_id="run_20260622_120000_abcdef12")

    workspace.write_json_artifact("scene_spec.json", {"ok": True})
    workspace.write_json_artifact("debug/raw_model_output.json", {"not": "evidence"})

    assert workspace.evidence_refs() == ["scene_spec.json"]


def test_begin_run_writes_user_brief_and_returns_tool_envelope(tmp_path):
    envelope = begin_run("draw a desk", output_root=tmp_path, run_id="run_20260622_120000_abcdef12")

    assert envelope.status == "ok"
    assert envelope.run_id == "run_20260622_120000_abcdef12"
    assert envelope.artifact_refs == ["user_brief.json"]
    assert envelope.next_actions == ["inspect"]
    assert (tmp_path / envelope.run_id / "user_brief.json").exists()


def test_tool_envelope_rejects_unknown_status():
    with pytest.raises(ValueError):
        ToolEnvelope(status="done", run_id="run_1", summary="bad")
