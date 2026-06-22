from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from cad_agent_vnext.app.run_workspace import DEFAULT_OUTPUT_ROOT, RunWorkspace
from cad_agent_vnext.domain.drawing import DrawingSnapshot
from cad_agent_vnext.domain.scene import SceneSpec
from cad_agent_vnext.planning.scene_compiler import compile_scene
from cad_agent_vnext.tools.envelopes import ToolEnvelope


def validate_scene(*, run_id: str, output_root: str | Path = DEFAULT_OUTPUT_ROOT) -> ToolEnvelope:
    workspace = RunWorkspace.open(output_root=output_root, run_id=run_id)
    try:
        scene = SceneSpec.model_validate(workspace.read_json_artifact("scene_spec.json"))
    except FileNotFoundError:
        return _blocked(run_id, ["scene_spec_missing"], "scene_spec.json is required before validation.")
    except ValidationError as exc:
        workspace.write_json_artifact(
            "scene_validation.json",
            {"schemaVersion": "cad-agent-vnext-scene-validation/v1", "status": "blocked", "errors": exc.errors()},
        )
        return _blocked(run_id, ["scene_spec_invalid"], "scene_spec.json failed schema validation.")

    artifact_ref = workspace.write_json_artifact(
        "scene_validation.json",
        {
            "schemaVersion": "cad-agent-vnext-scene-validation/v1",
            "status": "ok",
            "objectIds": [item.id for item in scene.objects],
        },
    )
    return ToolEnvelope(
        status="ok",
        run_id=run_id,
        artifact_refs=[artifact_ref],
        next_actions=["compile"],
        summary="SceneSpec validated.",
    )


def compile_run(*, run_id: str, output_root: str | Path = DEFAULT_OUTPUT_ROOT) -> ToolEnvelope:
    workspace = RunWorkspace.open(output_root=output_root, run_id=run_id)
    try:
        scene = SceneSpec.model_validate(workspace.read_json_artifact("scene_spec.json"))
    except FileNotFoundError:
        return _blocked(run_id, ["scene_spec_missing"], "scene_spec.json is required before compile.")
    try:
        snapshot = DrawingSnapshot.model_validate(workspace.read_json_artifact("drawing_snapshot.json"))
    except FileNotFoundError:
        return _blocked(run_id, ["drawing_snapshot_missing"], "inspect must run before compile.")

    result = compile_scene(scene, snapshot)
    artifact_refs = [workspace.write_json_artifact("compile_result.json", result.model_dump(mode="json"))]
    if result.patch is not None:
        artifact_refs.append(workspace.write_json_artifact("cad_patch.json", result.patch.model_dump(mode="json")))
    if result.semantic_map is not None:
        artifact_refs.append(workspace.write_json_artifact("semantic_map.json", result.semantic_map.model_dump(mode="json")))
    if result.impact is not None:
        artifact_refs.append(workspace.write_json_artifact("impact_summary.json", result.impact.model_dump(mode="json")))

    if result.status != "succeeded":
        return ToolEnvelope(
            status="blocked",
            run_id=run_id,
            artifact_refs=artifact_refs,
            blocking_reasons=list(result.blocking_reasons),
            summary="Scene compile blocked.",
        )
    return ToolEnvelope(
        status="ok",
        run_id=run_id,
        artifact_refs=artifact_refs,
        next_actions=["inspect-impact", "execute-preview"],
        summary="Scene compiled into a preview-only CadPatch.",
    )


def _blocked(run_id: str, reasons: list[str], summary: str) -> ToolEnvelope:
    return ToolEnvelope(status="blocked", run_id=run_id, blocking_reasons=reasons, summary=summary)
