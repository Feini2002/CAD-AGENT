from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

import pytest

from cad_agent.app.run_service import begin_run
from cad_agent.app.run_workspace import RunWorkspace
from cad_agent.cli import main
from cad_agent.domain.scene import PlacementIntent, SceneObjectSpec, SceneSpec
from cad_agent.tools.cad_tools import execute_preview
from cad_agent.tools.inspect_tools import inspect_run
from cad_agent.tools.scene_tools import compile_run, validate_scene
from cad_agent.tools.verify_tools import closeout_run, verify_run


def standard_scene(run_id: str) -> SceneSpec:
    return SceneSpec(
        schema_version="scene-spec/v1",
        run_id=run_id,
        scene_id="tool-loop-standard",
        units="mm",
        view="plan_2d",
        objects=[
            SceneObjectSpec(id="desk", kind="desk", placement=PlacementIntent(mode="free_region_center")),
            SceneObjectSpec(id="monitor", kind="monitor", placement=PlacementIntent(mode="relative", on="desk", anchor="rear_center")),
            SceneObjectSpec(
                id="keyboard",
                kind="keyboard",
                placement=PlacementIntent(mode="relative", on="desk", in_front_of="monitor", align_x="monitor", gap=40),
            ),
            SceneObjectSpec(
                id="mouse",
                kind="mouse",
                placement=PlacementIntent(mode="relative", on="desk", right_of="keyboard", align_y="keyboard", gap=40),
            ),
            SceneObjectSpec(id="vase", kind="vase", placement=PlacementIntent(mode="relative", on="desk", anchor="rear_right")),
        ],
    )


def write_scene(output_root: Path, run_id: str) -> None:
    workspace = RunWorkspace.open(output_root=output_root, run_id=run_id)
    workspace.write_json_artifact("scene_spec.json", standard_scene(run_id).model_dump(mode="json"))


def test_tool_loop_runs_fake_backend_end_to_end(tmp_path):
    run_id = "run_20260622_120000_abcdef12"
    begin = begin_run("draw a computer desk scene", output_root=tmp_path, run_id=run_id)
    write_scene(tmp_path, run_id)

    inspect = inspect_run(run_id=run_id, output_root=tmp_path, backend="fake")
    validation = validate_scene(run_id=run_id, output_root=tmp_path)
    compile_envelope = compile_run(run_id=run_id, output_root=tmp_path)
    execution = execute_preview(run_id=run_id, output_root=tmp_path, backend="fake")
    verification = verify_run(run_id=run_id, output_root=tmp_path)
    closeout = closeout_run(run_id=run_id, output_root=tmp_path)

    assert begin.status == "ok"
    assert inspect.artifact_refs == ["drawing_snapshot.json"]
    assert validation.status == "ok"
    assert compile_envelope.status == "ok"
    assert execution.status == "ok"
    assert verification.status == "ok"
    assert closeout.status == "ok"
    assert "closeout.json" in closeout.artifact_refs

    root = tmp_path / run_id
    assert json.loads((root / "verification_report.json").read_text(encoding="utf-8"))["overall_status"] == "passed"
    assert json.loads((root / "closeout.json").read_text(encoding="utf-8"))["savedCurrentDwg"] is False


def test_execute_preview_blocks_until_scene_is_validated_and_compiled(tmp_path):
    run_id = "run_20260622_120000_abcdef12"
    begin_run("draw a desk", output_root=tmp_path, run_id=run_id)

    envelope = execute_preview(run_id=run_id, output_root=tmp_path, backend="fake")

    assert envelope.status == "blocked"
    assert "cad_patch_missing" in envelope.blocking_reasons


def test_closeout_blocks_when_verification_failed(tmp_path):
    run_id = "run_20260622_120000_abcdef12"
    begin_run("draw a desk", output_root=tmp_path, run_id=run_id)
    workspace = RunWorkspace.open(output_root=tmp_path, run_id=run_id)
    workspace.write_json_artifact(
        "verification_report.json",
        {
            "schema_version": "verification-report/v1",
            "run_id": run_id,
            "overall_status": "failed",
            "checks": [],
            "allowed_claims": [],
            "blocking_reasons": ["missing_object:desk"],
        },
    )

    envelope = closeout_run(run_id=run_id, output_root=tmp_path)

    assert envelope.status == "blocked"
    assert "verification_not_passed" in envelope.blocking_reasons


def test_run_workspace_open_blocks_path_escape(tmp_path):
    with pytest.raises(ValueError, match="run id"):
        RunWorkspace.open(output_root=tmp_path, run_id="../escape")


def test_cli_commands_print_tool_envelope_json(tmp_path):
    run_id = "run_20260622_120000_abcdef12"
    exit_code, output = run_cli(
        "begin-run",
        "--request",
        "draw a desk",
        "--run-id",
        run_id,
        "--output-root",
        str(tmp_path),
    )

    assert exit_code == 0
    payload = json.loads(output)
    assert payload["schema_version"] == "tool-envelope/v1"
    assert payload["status"] == "ok"
    assert payload["next_actions"] == ["inspect"]

    exit_code, output = run_cli("inspect", "--run", run_id, "--backend", "fake", "--output-root", str(tmp_path))

    assert exit_code == 0
    payload = json.loads(output)
    assert payload["artifact_refs"] == ["drawing_snapshot.json"]


def run_cli(*args: str) -> tuple[int, str]:
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exit_code = main(list(args))
    return exit_code, stdout.getvalue().strip()
