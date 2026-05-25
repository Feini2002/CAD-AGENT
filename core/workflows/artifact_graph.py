"""Workflow artifact dependency graph utilities.

This module turns workflow artifact lists into an explicit dependency graph so
Core can reason about artifact order, path existence, and invalid cycles before
running CAD or pipeline actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from core.schemas.validator import load_json


@dataclass
class ArtifactNode:
    artifact_id: str
    model_type: str
    path: str = ""
    role: str = "derived"
    depends_on: list[str] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)


class ArtifactGraph:
    """Small topological graph for workflow artifacts."""

    def __init__(self) -> None:
        self.nodes: dict[str, ArtifactNode] = {}

    def add_artifact(
        self,
        artifact_id: str,
        *,
        model_type: str,
        path: str | None = None,
        role: str = "derived",
        depends_on: list[str] | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        self.nodes[artifact_id] = ArtifactNode(
            artifact_id=artifact_id,
            model_type=model_type,
            path=path or "",
            role=role,
            depends_on=list(depends_on or []),
            data=dict(data or {}),
        )

    def dependency_order(self) -> list[str]:
        ordered: list[str] = []
        temporary: set[str] = set()
        permanent: set[str] = set()

        def visit(artifact_id: str) -> None:
            if artifact_id in permanent:
                return
            if artifact_id in temporary:
                raise ValueError(f"Artifact dependency cycle includes {artifact_id}.")
            if artifact_id not in self.nodes:
                raise ValueError(f"Unknown artifact dependency: {artifact_id}.")
            temporary.add(artifact_id)
            for dependency in self.nodes[artifact_id].depends_on:
                visit(dependency)
            temporary.remove(artifact_id)
            permanent.add(artifact_id)
            ordered.append(artifact_id)

        for artifact_id in self.nodes:
            visit(artifact_id)
        return ordered

    def validate_paths(self, root: Path) -> dict[str, Any]:
        missing: list[str] = []
        for node in self.nodes.values():
            if node.path and not (root / node.path).exists():
                missing.append(node.path)
        return {
            "status": "ok" if not missing else "missing_paths",
            "missing": missing,
            "checked": sum(1 for node in self.nodes.values() if node.path),
        }

    def to_index(self) -> dict[str, Any]:
        return {
            artifact_id: {
                "model_type": node.model_type,
                "path": node.path,
                "role": node.role,
                "depends_on": list(node.depends_on),
            }
            for artifact_id, node in self.nodes.items()
        }


_DEFAULT_DEPENDENCIES = {
    "design_brief": [],
    "drawing_model": [],
    "style_profile": [],
    "project_model": ["design_brief", "drawing_model"],
    "object_spec": ["design_brief", "style_profile"],
    "layout_proposal": ["project_model", "object_spec"],
    "design_proposal": ["design_brief", "project_model", "object_spec", "layout_proposal"],
    "cad_plan": ["design_proposal", "object_spec", "layout_proposal"],
    "verification_report": ["cad_plan"],
}


def _artifact_id_for(model_type: str, counts: dict[str, int]) -> str:
    counts[model_type] = counts.get(model_type, 0) + 1
    return model_type if counts[model_type] == 1 else f"{model_type}:{counts[model_type]}"


def _existing_dependencies(model_type: str, known_model_types: set[str]) -> list[str]:
    return [dependency for dependency in _DEFAULT_DEPENDENCIES.get(model_type, []) if dependency in known_model_types]


def build_artifact_graph_from_workflow(workflow_path: Path) -> ArtifactGraph:
    workflow = load_json(workflow_path)
    if not isinstance(workflow, dict):
        raise ValueError("Workflow must be a JSON object.")
    artifacts = workflow.get("artifacts", [])
    if not isinstance(artifacts, list):
        raise ValueError("Workflow artifacts must be a list.")

    graph = ArtifactGraph()
    counts: dict[str, int] = {}
    known_model_types = {
        artifact.get("model_type")
        for artifact in artifacts
        if isinstance(artifact, dict) and isinstance(artifact.get("model_type"), str)
    }
    for artifact in artifacts:
        if not isinstance(artifact, dict) or not isinstance(artifact.get("model_type"), str):
            raise ValueError("Each workflow artifact must include model_type.")
        model_type = artifact["model_type"]
        artifact_id = str(artifact.get("artifact_id") or _artifact_id_for(model_type, counts))
        raw_dependencies = artifact.get("depends_on")
        if raw_dependencies is None:
            depends_on = _existing_dependencies(model_type, known_model_types)
        elif isinstance(raw_dependencies, list) and all(isinstance(item, str) for item in raw_dependencies):
            depends_on = list(raw_dependencies)
        else:
            raise ValueError(f"{artifact_id}.depends_on must be a list of artifact ids.")
        graph.add_artifact(
            artifact_id,
            model_type=model_type,
            path=str(artifact.get("path", "")),
            role=str(artifact.get("role", "derived")),
            depends_on=depends_on,
            data=artifact,
        )
    graph.dependency_order()
    return graph
