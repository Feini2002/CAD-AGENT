"""Phase 14 Engineering Kernel / BIM contract layer.

This module projects a CAD_PLAN and existing backend evidence into shared
task / geometry / semantic / version / evidence graphs, then compares backend
candidate profiles in a DiffPackage. It is intentionally no-CAD: it never
connects to AutoCAD, executes a plugin, saves a DWG, writes a formal layer, or
claims new real CAD readback.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from core.contracts.vnext import EvidenceItem, EvidencePackage
from core.geometry_backends.registry import list_geometry_backends
from core.safety.policy import PREVIEW_LAYER


ENGINEERING_KERNEL_GRAPHS_SCHEMA = "engineering-kernel-graphs/p14/v1"
ENGINEERING_KERNEL_DIFF_PACKAGE_SCHEMA = "engineering-kernel-diff-package/p14/v1"
ENGINEERING_KERNEL_BACKEND = "engineering_kernel"

P14_ENGINEERING_KERNEL_ALLOWED_EFFECTS = (
    "engineering_kernel_graph_build",
    "engineering_kernel_diff_package_write",
    "backend_candidate_profile_write",
)

P14_ENGINEERING_KERNEL_FORBIDDEN_EFFECTS = (
    "cad_execute",
    "native_plugin_execute",
    "plugin_execute",
    "real_cad_readback",
    "cad_preview_write",
    "created_handles_readback",
    "dwg_save",
    "save_current_dwg",
    "formal_layer_write",
    "training_source_mutation",
    "table_c_mutation",
)

DEFAULT_BACKEND_CANDIDATES = (
    "cad_session_host",
    "native_thin_live_backend",
    "dxf_file",
    "geometry_kernel",
    "ifc_bim",
)


def build_engineering_kernel_graphs(
    *,
    cad_plan: dict[str, Any] | None,
    evidence_sources: list[dict[str, Any]] | None = None,
    backend_candidates: list[str] | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Build P14 shared graph projections without CAD execution."""

    plan = dict(cad_plan or {})
    blockers = _cad_plan_blockers(plan)
    status = "blocked" if blockers else "ready"
    bbox = _cad_plan_bbox(plan)
    semantic_type = _semantic_type(plan)
    candidates = _normalised_candidates(backend_candidates)
    profiles = _source_profiles(evidence_sources or [])
    candidate_docs = _backend_candidate_docs(candidates=candidates, profiles=profiles)
    source_hashes = {"cadPlan": _stable_hash(plan)}
    for backend, profile in profiles.items():
        source_hashes[backend] = str(profile["sourceHash"])

    graphs = {
        "schemaVersion": ENGINEERING_KERNEL_GRAPHS_SCHEMA,
        "phase": "Phase 14",
        "packageId": "phase14.engineering-kernel-graphs",
        "taskId": "phase14.engineering-kernel.diff-package",
        "kind": "engineering_kernel_graph_projection",
        "status": status,
        "verificationStatus": "not_verified",
        "backend": ENGINEERING_KERNEL_BACKEND,
        "adapterId": "engineering-kernel.diff-package",
        "targetLayer": _plan_layer(plan),
        "cadWritesAttempted": False,
        "sourceCadWritesAttempted": any(bool(profile["cadWritesAttempted"]) for profile in profiles.values()),
        "cadGeometryVerified": False,
        "sourceCadGeometryVerified": any(bool(profile["cadGeometryVerified"]) for profile in profiles.values()),
        "nativePluginInvoked": False,
        "savedCurrentDwg": False,
        "taskGraph": {
            "nodes": [
                {
                    "id": "task.cad_plan",
                    "kind": "cad_plan",
                    "intent": str(plan.get("intent") or ""),
                    "domain": str(plan.get("domain") or ""),
                    "targetLayer": _plan_layer(plan),
                },
                {
                    "id": "task.compare_backends",
                    "kind": "backend_diff",
                    "backendCandidates": list(candidates),
                },
            ],
            "edges": [{"from": "task.cad_plan", "to": "task.compare_backends", "kind": "projects_to"}],
        },
        "geometryGraph": {
            "nodes": [
                {
                    "id": "geometry.primary_object",
                    "kind": "bbox_footprint",
                    "bbox": bbox,
                    "targetLayer": _plan_layer(plan),
                    "source": "cad_plan",
                }
            ],
            "edges": [],
        },
        "semanticGraph": {
            "nodes": [
                {
                    "id": "semantic.primary_object",
                    "kind": "semantic_object",
                    "semanticType": semantic_type,
                    "name": str(_object(plan).get("name") or ""),
                }
            ],
            "edges": [{"from": "semantic.primary_object", "to": "geometry.primary_object", "kind": "describes"}],
        },
        "versionGraph": {
            "cadPlanHash": source_hashes["cadPlan"],
            "sourceHashes": source_hashes,
            "backendEvidenceOrder": sorted(profiles),
        },
        "evidenceGraph": {
            "backendEvidence": profiles,
            "backendCandidateDocs": candidate_docs,
        },
        "blockingReasons": blockers,
        "missingEvidence": [],
        "allowedEffects": list(P14_ENGINEERING_KERNEL_ALLOWED_EFFECTS),
        "forbiddenEffects": list(P14_ENGINEERING_KERNEL_FORBIDDEN_EFFECTS),
        "completionBoundary": (
            "P14 graph projection compares CAD_PLAN and supplied backend evidence only; "
            "it is not new CAD execution, real readback, training, Table C, or BIM export proof."
        ),
        "notEvidenceFor": _p14_not_evidence_for(),
        "artifacts": {},
    }
    if output_dir is not None:
        graphs["artifacts"]["engineeringKernelGraphs"] = _write_json(
            output_dir=output_dir,
            filename="engineering_kernel_graphs.json",
            payload=graphs,
        )
    return graphs


def build_engineering_kernel_diff_package(
    *,
    cad_plan: dict[str, Any] | None,
    evidence_sources: list[dict[str, Any]] | None = None,
    backend_candidates: list[str] | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Build a no-CAD P14 DiffPackage across backend evidence candidates."""

    candidates = _normalised_candidates(backend_candidates)
    graphs = build_engineering_kernel_graphs(
        cad_plan=cad_plan,
        evidence_sources=evidence_sources,
        backend_candidates=candidates,
        output_dir=output_dir,
    )
    profiles = dict(graphs["evidenceGraph"]["backendEvidence"])
    candidate_docs = dict(graphs["evidenceGraph"]["backendCandidateDocs"])
    verified_backends = [
        backend for backend in candidates if backend in profiles and _profile_is_verified(profiles[backend])
    ]
    not_run_backends = [backend for backend in candidates if backend not in profiles]
    status = "blocked" if graphs["status"] == "blocked" else "ready"
    diff_package = {
        "schemaVersion": ENGINEERING_KERNEL_DIFF_PACKAGE_SCHEMA,
        "phase": "Phase 14",
        "packageId": "phase14.engineering-kernel-diff-package",
        "taskId": "phase14.engineering-kernel.diff-package",
        "kind": "engineering_kernel_diff_package",
        "status": status,
        "verificationStatus": "not_verified",
        "comparisonStatus": "blocked" if status == "blocked" else "complete",
        "evidenceCompleteness": "complete" if not not_run_backends and verified_backends else "partial",
        "backend": ENGINEERING_KERNEL_BACKEND,
        "adapterId": "engineering-kernel.diff-package",
        "targetLayer": _plan_layer(dict(cad_plan or {})),
        "cadWritesAttempted": False,
        "sourceCadWritesAttempted": bool(graphs["sourceCadWritesAttempted"]),
        "cadGeometryVerified": False,
        "sourceCadGeometryVerified": bool(graphs["sourceCadGeometryVerified"]),
        "nativePluginInvoked": False,
        "savedCurrentDwg": False,
        "backendCandidates": list(candidates),
        "verifiedBackends": verified_backends,
        "notRunBackends": not_run_backends,
        "backendCandidateDocs": candidate_docs,
        "geometryDelta": _geometry_delta([profiles[backend] for backend in verified_backends]),
        "styleDelta": _style_delta([profiles[backend] for backend in verified_backends]),
        "semanticDelta": _semantic_delta(cad_plan=dict(cad_plan or {}), profiles=[profiles[b] for b in verified_backends]),
        "graphs": {
            "taskGraph": graphs["taskGraph"],
            "geometryGraph": graphs["geometryGraph"],
            "semanticGraph": graphs["semanticGraph"],
            "versionGraph": graphs["versionGraph"],
            "evidenceGraph": graphs["evidenceGraph"],
        },
        "blockingReasons": list(graphs["blockingReasons"]),
        "missingEvidence": [],
        "allowedEffects": list(P14_ENGINEERING_KERNEL_ALLOWED_EFFECTS),
        "forbiddenEffects": list(P14_ENGINEERING_KERNEL_FORBIDDEN_EFFECTS),
        "completionBoundary": (
            "P14 DiffPackage is a comparison artifact over existing proof and candidate docs. "
            "It cannot claim real_cad_readback or geometry_verified by itself."
        ),
        "notEvidenceFor": _p14_not_evidence_for(),
        "artifacts": dict(graphs.get("artifacts") or {}),
    }
    if output_dir is not None:
        diff_package["artifacts"]["engineeringKernelDiffPackage"] = _write_json(
            output_dir=output_dir,
            filename="engineering_kernel_diff_package.json",
            payload=diff_package,
        )
    return diff_package


def execute_engineering_kernel_diff(
    *,
    cad_plan: dict[str, Any] | None,
    evidence_sources: list[dict[str, Any]] | None = None,
    backend_candidates: list[str] | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Harness-facing alias for the P14 no-CAD DiffPackage builder."""

    return build_engineering_kernel_diff_package(
        cad_plan=cad_plan,
        evidence_sources=evidence_sources,
        backend_candidates=backend_candidates,
        output_dir=output_dir,
    )


def engineering_kernel_evidence_package(diff_package: dict[str, Any]) -> EvidencePackage:
    payload = dict(diff_package)
    status_ready = payload.get("status") == "ready"
    artifacts = dict(payload.get("artifacts") or {})
    return EvidencePackage(
        task_id=str(payload.get("taskId") or "phase14.engineering-kernel.diff-package"),
        items=[
            EvidenceItem(
                kind="engineering_kernel_graphs",
                status="pass" if artifacts.get("engineeringKernelGraphs") or payload.get("graphs") else "fail",
                backend=ENGINEERING_KERNEL_BACKEND,
                metadata={
                    "cadWritesAttempted": False,
                    "savedCurrentDwg": False,
                    "boundary": "graph projection only",
                },
            ),
            EvidenceItem(
                kind="engineering_kernel_diff_package",
                status="pass" if payload.get("schemaVersion") == ENGINEERING_KERNEL_DIFF_PACKAGE_SCHEMA and status_ready else "fail",
                backend=ENGINEERING_KERNEL_BACKEND,
                metadata={
                    "comparisonStatus": str(payload.get("comparisonStatus") or ""),
                    "evidenceCompleteness": str(payload.get("evidenceCompleteness") or ""),
                    "verifiedBackends": list(payload.get("verifiedBackends") or []),
                },
            ),
            EvidenceItem(
                kind="backend_candidate_profile",
                status="pass" if payload.get("backendCandidateDocs") else "fail",
                backend=ENGINEERING_KERNEL_BACKEND,
                metadata={"backendCandidates": list(payload.get("backendCandidates") or [])},
            ),
            EvidenceItem(
                kind="no_save_guard",
                status="pass" if payload.get("savedCurrentDwg") is False else "fail",
                backend=ENGINEERING_KERNEL_BACKEND,
                metadata={"savedCurrentDwg": payload.get("savedCurrentDwg")},
            ),
        ],
    )


def _cad_plan_blockers(plan: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not plan:
        blockers.append("cad_plan_missing")
    if str(_plan_layer(plan)) != PREVIEW_LAYER:
        blockers.append("cad_plan_must_target_CODEX_PREVIEW")
    if not isinstance(_object(plan).get("width"), (int, float)) or not isinstance(_object(plan).get("depth"), (int, float)):
        blockers.append("cad_plan_object_width_depth_required")
    return blockers


def _cad_plan_bbox(plan: dict[str, Any]) -> dict[str, list[Any]]:
    placement = plan.get("placement") if isinstance(plan.get("placement"), dict) else {}
    base = placement.get("base_point") if isinstance(placement.get("base_point"), list) else [0, 0, 0]
    base = list(base[:3]) + [0] * max(0, 3 - len(base))
    obj = _object(plan)
    width = obj.get("width", 0)
    depth = obj.get("depth", 0)
    return {
        "min": [base[0], base[1], base[2]],
        "max": [_add_number(base[0], width), _add_number(base[1], depth), base[2]],
    }


def _source_profiles(evidence_sources: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    profiles: dict[str, dict[str, Any]] = {}
    for source in evidence_sources:
        if not isinstance(source, dict):
            continue
        profile = _source_profile(source)
        backend = str(profile["backend"])
        profiles[backend] = profile
    return dict(sorted(profiles.items()))


def _source_profile(source: dict[str, Any]) -> dict[str, Any]:
    backend = _normalise_backend(_source_backend(source))
    entities = _source_entities(source)
    bbox = _first_entity_bbox(entities)
    profile = {
        "backend": backend,
        "status": str(source.get("status") or ""),
        "verificationStatus": str(source.get("verificationStatus") or ""),
        "cadGeometryVerified": source.get("cadGeometryVerified") is True,
        "cadWritesAttempted": source.get("cadWritesAttempted") is True,
        "savedCurrentDwg": source.get("savedCurrentDwg") is True,
        "nativePluginInvoked": source.get("nativePluginInvoked") is True,
        "targetLayer": str(source.get("targetLayer") or _entity_layer(entities) or ""),
        "createdHandles": [str(item) for item in source.get("createdHandles", [])],
        "entityTypes": sorted({str(item.get("type") or "") for item in entities if isinstance(item, dict)}),
        "layers": sorted({str(item.get("layer") or "") for item in entities if isinstance(item, dict)}),
        "bbox": bbox,
        "bboxSignature": _stable_hash(bbox) if bbox else "",
        "rollbackStatus": str(source.get("rollbackStatus") or ""),
        "entityCount": len(entities),
        "sourceHash": _stable_hash(source),
        "proofBoundary": "existing_backend_evidence_profile_only",
    }
    if not profile["createdHandles"]:
        profile["createdHandles"] = [str(item.get("handle") or "") for item in entities if isinstance(item, dict)]
    return profile


def _backend_candidate_docs(
    *,
    candidates: tuple[str, ...],
    profiles: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    geometry_slots = list_geometry_backends()
    docs: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        profile = profiles.get(candidate)
        docs[candidate] = {
            "backend": candidate,
            "status": "evidence_profiled" if profile else "candidate_not_run",
            "hasEvidence": profile is not None,
            "requiresCad": candidate in {"cad_session_host", "native_thin_live_backend"},
            "requiresNativePlugin": candidate == "native_thin_live_backend",
            "proofBoundary": _candidate_boundary(candidate),
        }
        if profile:
            docs[candidate]["profileHash"] = str(profile["sourceHash"])
            docs[candidate]["verificationStatus"] = str(profile["verificationStatus"])
        if candidate == "geometry_kernel":
            docs[candidate]["declaredGeometryBackends"] = geometry_slots
        if candidate == "ifc_bim":
            docs[candidate]["declaredBimBackends"] = [
                item for item in geometry_slots if item.get("backend_id") == "ifcopenshell"
            ]
        if candidate == "dxf_file":
            docs[candidate]["candidateArtifact"] = "future_dxf_diff_export"
    return docs


def _geometry_delta(profiles: list[dict[str, Any]]) -> dict[str, Any]:
    signatures = _unique([str(profile.get("bboxSignature") or "") for profile in profiles if profile.get("bboxSignature")])
    return {
        "bboxDeltaCount": 0 if len(signatures) <= 1 else len(signatures) - 1,
        "comparedBackends": [str(profile.get("backend") or "") for profile in profiles if profile.get("bboxSignature")],
        "bboxSignatures": signatures,
    }


def _style_delta(profiles: list[dict[str, Any]]) -> dict[str, Any]:
    layer_signatures = _unique(["|".join(profile.get("layers") or []) for profile in profiles if profile.get("layers")])
    return {
        "layerDeltaCount": 0 if len(layer_signatures) <= 1 else len(layer_signatures) - 1,
        "layerSignatures": layer_signatures,
    }


def _semantic_delta(*, cad_plan: dict[str, Any], profiles: list[dict[str, Any]]) -> dict[str, Any]:
    semantic = _semantic_type(cad_plan)
    compared = [str(profile.get("backend") or "") for profile in profiles]
    return {
        "semanticTypeDeltaCount": 0,
        "cadPlanSemanticType": semantic,
        "comparedBackends": compared,
    }


def _profile_is_verified(profile: dict[str, Any]) -> bool:
    return (
        profile.get("status") == "geometry_verified"
        and profile.get("verificationStatus") == "verified"
        and profile.get("cadGeometryVerified") is True
        and profile.get("savedCurrentDwg") is False
        and profile.get("targetLayer") == PREVIEW_LAYER
    )


def _source_backend(source: dict[str, Any]) -> str:
    adapter_id = str(source.get("adapterId") or "")
    if adapter_id == "native-thin.live-spike":
        return "native_thin_live_backend"
    backend_identity = source.get("backendIdentity") if isinstance(source.get("backendIdentity"), dict) else {}
    if str(backend_identity.get("backend") or "") == "native_thin_live_backend":
        return "native_thin_live_backend"
    return str(source.get("backend") or "")


def _source_entities(source: dict[str, Any]) -> list[dict[str, Any]]:
    readback = source.get("createdHandlesReadback") if isinstance(source.get("createdHandlesReadback"), dict) else {}
    plugin = source.get("pluginResult") if isinstance(source.get("pluginResult"), dict) else {}
    plugin_readback = plugin.get("createdHandlesReadback") if isinstance(plugin.get("createdHandlesReadback"), dict) else {}
    candidates = [
        source.get("readbackEntities"),
        readback.get("entities"),
        plugin_readback.get("entities"),
    ]
    for value in candidates:
        if isinstance(value, list):
            return [dict(item) for item in value if isinstance(item, dict)]
    return []


def _first_entity_bbox(entities: list[dict[str, Any]]) -> dict[str, Any]:
    for entity in entities:
        bbox = entity.get("bbox")
        if isinstance(bbox, dict):
            return dict(bbox)
    return {}


def _entity_layer(entities: list[dict[str, Any]]) -> str:
    for entity in entities:
        if isinstance(entity, dict) and entity.get("layer"):
            return str(entity.get("layer"))
    return ""


def _normalised_candidates(candidates: list[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    values = candidates or DEFAULT_BACKEND_CANDIDATES
    return tuple(_unique([_normalise_backend(str(item)) for item in values if str(item)]))


def _normalise_backend(value: str) -> str:
    text = str(value or "").strip().replace("-", "_")
    aliases = {
        "cad_session_host": "cad_session_host",
        "cad_session": "cad_session_host",
        "autocad_com_existing": "cad_session_host",
        "com": "cad_session_host",
        "native_thin_live_backend": "native_thin_live_backend",
        "native_thin_live": "native_thin_live_backend",
        "autocad_plugin": "native_thin_live_backend",
        "dxf": "dxf_file",
        "dxf_file": "dxf_file",
        "geometry_kernel": "geometry_kernel",
        "kernel": "geometry_kernel",
        "cad_plan_rect2d": "geometry_kernel",
        "ifc": "ifc_bim",
        "ifc_bim": "ifc_bim",
        "ifcopenshell": "ifc_bim",
    }
    return aliases.get(text, text)


def _candidate_boundary(candidate: str) -> str:
    if candidate == "cad_session_host":
        return "existing cad-session-host preview/readback evidence profile; no new CAD execution by P14"
    if candidate == "native_thin_live_backend":
        return "existing scoped native thin live spike evidence profile; no new plugin execution by P14"
    if candidate == "dxf_file":
        return "declared future DXF artifact comparison slot; not run in P14A"
    if candidate == "geometry_kernel":
        return "declared no-CAD geometry kernel candidate slots; no dependency import required"
    if candidate == "ifc_bim":
        return "declared future IFC/BIM backend slot; not a production BIM export"
    return "declared backend candidate; not run unless an evidence source is supplied"


def _plan_layer(plan: dict[str, Any]) -> str:
    drawing = plan.get("drawing") if isinstance(plan.get("drawing"), dict) else {}
    return str(drawing.get("layer") or PREVIEW_LAYER)


def _object(plan: dict[str, Any]) -> dict[str, Any]:
    value = plan.get("object") if isinstance(plan.get("object"), dict) else {}
    return dict(value)


def _semantic_type(plan: dict[str, Any]) -> str:
    obj = _object(plan)
    return str(obj.get("type") or "unknown")


def _add_number(left: Any, right: Any) -> Any:
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left + right
    return right


def _stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _write_json(*, output_dir: str | Path, filename: str, payload: dict[str, Any]) -> str:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    path = root / filename
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


def _p14_not_evidence_for() -> list[str]:
    return [
        "real_cad_readback",
        "geometry_verified",
        "cad_geometry_verified",
        "new_cad_execution",
        "native_plugin_execution",
        "current_dwg_save",
        "formal_layer_write",
        "training_resume",
        "table_c_progress",
        "production_bim_export",
    ]


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            result.append(value)
    return result
