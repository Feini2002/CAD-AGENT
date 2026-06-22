from __future__ import annotations

from pathlib import Path

from cad_agent_vnext.app.run_workspace import DEFAULT_OUTPUT_ROOT, RunWorkspace
from cad_agent_vnext.domain.brief import UserBrief
from cad_agent_vnext.tools.envelopes import ToolEnvelope


def begin_run(
    raw_text: str,
    *,
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
    run_id: str | None = None,
) -> ToolEnvelope:
    workspace = RunWorkspace.create(output_root=output_root, run_id=run_id)
    brief = UserBrief(
        schema_version="user-brief/v1",
        run_id=workspace.run_id,
        raw_text=raw_text,
        request_kind="unknown",
    )
    artifact_ref = workspace.write_json_artifact("user_brief.json", brief.model_dump(mode="json"))
    return ToolEnvelope(
        status="ok",
        run_id=workspace.run_id,
        artifact_refs=[artifact_ref],
        next_actions=["inspect"],
        summary="Run workspace initialized; CAD has not been inspected or modified.",
    )
