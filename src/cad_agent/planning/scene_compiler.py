from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import Field

from cad_agent.domain.common import BBox2D, StrictModel
from cad_agent.domain.drawing import DrawingSnapshot
from cad_agent.domain.patch import CadPatch, PatchOperation
from cad_agent.domain.scene import Dimensions2D, PlacementIntent, SceneObjectSpec, SceneSpec
from cad_agent.planning.impact_estimator import PatchImpact, estimate_patch_impact
from cad_agent.planning.object_catalog import ObjectCatalog, ObjectCatalogError, load_object_catalog
from cad_agent.planning.object_generators import UnsupportedObjectError, generate_object_primitives
from cad_agent.planning.relation_solver import RelationSolveResult, solve_scene_relations
from cad_agent.planning.semantic_mapping import SemanticMapping, build_semantic_mapping


PREVIEW_PARKING_REGION: BBox2D = (0.0, 0.0, 2400.0, 1600.0)


class CompileSceneResult(StrictModel):
    status: Literal["succeeded", "blocked"]
    patch: CadPatch | None = None
    semantic_map: SemanticMapping | None = None
    impact: PatchImpact | None = None
    relation_result: RelationSolveResult
    target_region: BBox2D | None = None
    stable_hash: str
    blocking_reasons: list[str] = Field(default_factory=list)


def compile_scene(
    scene: SceneSpec,
    snapshot: DrawingSnapshot,
    *,
    catalog: ObjectCatalog | None = None,
    allow_preview_parking_region: bool = True,
    max_entity_budget: int = 100,
) -> CompileSceneResult:
    resolved_catalog = catalog or load_object_catalog()
    target_region = _choose_target_region(scene, snapshot, allow_preview_parking_region=allow_preview_parking_region)
    if target_region is None:
        relation_result = RelationSolveResult(status="blocked", unsatisfied_constraints=["target_region_unavailable"])
        return _blocked(scene, relation_result=relation_result, target_region=None, reasons=["target_region_unavailable"])

    normalized_scene = _scene_with_target_region(scene, target_region, resolved_catalog)
    relation_result = solve_scene_relations(
        normalized_scene,
        catalog=resolved_catalog,
        nearby_entities=snapshot.nearby_entities,
    )
    if relation_result.status != "succeeded":
        return _blocked(
            normalized_scene,
            relation_result=relation_result,
            target_region=target_region,
            reasons=relation_result.unsatisfied_constraints,
        )

    try:
        patch = _build_patch(normalized_scene, relation_result, catalog=resolved_catalog)
    except (ObjectCatalogError, UnsupportedObjectError, ValueError) as exc:
        return _blocked(
            normalized_scene,
            relation_result=relation_result,
            target_region=target_region,
            reasons=[str(exc)],
        )

    impact = estimate_patch_impact(patch)
    if impact.entity_count > max_entity_budget:
        return _blocked(
            normalized_scene,
            relation_result=relation_result,
            target_region=target_region,
            reasons=["max_entity_budget_exceeded"],
        )

    stable_hash = _stable_hash_for_patch(patch)
    patch = patch.model_copy(update={"transaction_id": stable_hash})
    semantic_map = build_semantic_mapping(patch)
    return CompileSceneResult(
        status="succeeded",
        patch=patch,
        semantic_map=semantic_map,
        impact=impact,
        relation_result=relation_result,
        target_region=target_region,
        stable_hash=stable_hash,
        blocking_reasons=[],
    )


def _build_patch(scene: SceneSpec, relation_result: RelationSolveResult, *, catalog: ObjectCatalog) -> CadPatch:
    operations: list[PatchOperation] = []
    for item in scene.objects:
        pose = relation_result.poses[item.id]
        primitives = generate_object_primitives(item, pose, catalog=catalog)
        operations.append(
            PatchOperation(
                op_id=f"create:{item.id}",
                action="create",
                semantic_object_id=item.id,
                primitives=primitives,
            )
        )
    return CadPatch(
        schema_version="cad-patch/v1",
        run_id=scene.run_id,
        transaction_id="pending",
        target_layer="CODEX_PREVIEW",
        operations=operations,
        save_current_dwg=False,
        forbidden_effects=["dwg_save", "formal_layer_write"],
    )


def _choose_target_region(
    scene: SceneSpec,
    snapshot: DrawingSnapshot,
    *,
    allow_preview_parking_region: bool,
) -> BBox2D | None:
    if any(item.placement.mode == "absolute" and item.placement.base_point is not None for item in scene.objects):
        return snapshot.target_region or PREVIEW_PARKING_REGION
    if snapshot.target_region is not None:
        return snapshot.target_region
    if allow_preview_parking_region:
        return PREVIEW_PARKING_REGION
    return None


def _scene_with_target_region(scene: SceneSpec, target_region: BBox2D, catalog: ObjectCatalog) -> SceneSpec:
    objects: list[SceneObjectSpec] = []
    for item in scene.objects:
        if item.placement.mode != "free_region_center":
            objects.append(item)
            continue
        dimensions = catalog.resolve_dimensions(item.kind, item.dimensions)
        center_x = (target_region[0] + target_region[2]) / 2
        center_y = (target_region[1] + target_region[3]) / 2
        base_point = (center_x - dimensions.width / 2, center_y - dimensions.depth / 2)
        objects.append(
            item.model_copy(
                update={
                    "placement": PlacementIntent(
                        mode="absolute",
                        base_point=base_point,
                        rotation_deg=item.placement.rotation_deg,
                    )
                }
            )
        )
    return scene.model_copy(update={"objects": objects})


def _blocked(
    scene: SceneSpec,
    *,
    relation_result: RelationSolveResult,
    target_region: BBox2D | None,
    reasons: list[str],
) -> CompileSceneResult:
    stable_hash = _stable_hash({"scene": scene.model_dump(mode="json"), "reasons": reasons})
    return CompileSceneResult(
        status="blocked",
        patch=None,
        semantic_map=None,
        impact=None,
        relation_result=relation_result,
        target_region=target_region,
        stable_hash=stable_hash,
        blocking_reasons=list(reasons),
    )


def _stable_hash_for_patch(patch: CadPatch) -> str:
    payload = patch.model_copy(update={"transaction_id": "stable"}).model_dump(mode="json")
    return _stable_hash(payload)


def _stable_hash(payload: object) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"txn-{hashlib.sha256(encoded).hexdigest()[:24]}"

