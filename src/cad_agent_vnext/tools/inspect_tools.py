from __future__ import annotations

from pathlib import Path
from typing import Literal

from cad_agent_vnext.adapters.fake_backend import FakeCadBackend
from cad_agent_vnext.adapters.legacy_autocad_backend import LegacyAutoCadBackend
from cad_agent_vnext.app.run_workspace import DEFAULT_OUTPUT_ROOT, RunWorkspace
from cad_agent_vnext.tools.envelopes import ToolEnvelope


BackendName = Literal["fake", "autocad-existing"]


def inspect_run(
    *,
    run_id: str,
    output_root: str | Path = DEFAULT_OUTPUT_ROOT,
    backend: BackendName = "fake",
) -> ToolEnvelope:
    workspace = RunWorkspace.open(output_root=output_root, run_id=run_id)
    try:
        if backend == "fake":
            snapshot = FakeCadBackend().inspect_document(run_id=run_id)
        elif backend == "autocad-existing":
            snapshot = LegacyAutoCadBackend.from_existing_autocad().inspect_document(run_id=run_id)
        else:
            return _blocked(run_id, [f"unsupported_backend:{backend}"], "Unsupported inspect backend.")
    except Exception as exc:
        return _blocked(run_id, [f"inspect_failed:{type(exc).__name__}"], str(exc))

    artifact_ref = workspace.write_json_artifact("drawing_snapshot.json", snapshot.model_dump(mode="json"))
    return ToolEnvelope(
        status="ok",
        run_id=run_id,
        artifact_refs=[artifact_ref],
        next_actions=["create-scene-spec", "validate-scene"],
        summary=f"Inspection completed with {backend}; CAD preview has not been modified.",
    )


def _blocked(run_id: str, reasons: list[str], summary: str) -> ToolEnvelope:
    return ToolEnvelope(status="blocked", run_id=run_id, blocking_reasons=reasons, summary=summary)
