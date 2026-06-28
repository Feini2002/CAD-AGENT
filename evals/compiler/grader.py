from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cad_agent.adapters.fake_backend import FakeCadBackend
from cad_agent.app.transaction_gateway import CadTransactionGateway
from cad_agent.domain.drawing import DrawingSnapshot
from cad_agent.domain.scene import Dimensions2D, PlacementIntent, SceneObjectSpec, SceneSpec
from cad_agent.planning.scene_compiler import compile_scene
from cad_agent.verification.scene_verifier import verify_scene_execution


@dataclass(frozen=True)
class Gate0Case:
    case_id: str
    group: str
    prompt: str
    backend: str
    expected_objects: list[str]
    expected_relations: list[list[str]]
    safety: dict[str, Any]
    scene_spec_fixture: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Gate0CaseResult:
    case_id: str
    group: str
    status: str
    object_completeness: float
    relation_satisfaction: float
    safety_pass: bool
    failure_category: str | None
    blocking_reasons: list[str]

    def to_json(self) -> dict[str, Any]:
        return {
            "caseId": self.case_id,
            "group": self.group,
            "status": self.status,
            "objectCompleteness": self.object_completeness,
            "relationSatisfaction": self.relation_satisfaction,
            "safetyPass": self.safety_pass,
            "failureCategory": self.failure_category,
            "blockingReasons": self.blocking_reasons,
        }


def load_cases(path: str | Path) -> list[Gate0Case]:
    cases: list[Gate0Case] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        cases.append(
            Gate0Case(
                case_id=payload["caseId"],
                group=payload.get("group", "ungrouped"),
                prompt=payload["prompt"],
                backend=payload.get("backend", "fake"),
                expected_objects=list(payload.get("expectedObjects", [])),
                expected_relations=[list(item) for item in payload.get("expectedRelations", [])],
                safety=dict(payload.get("safety", {})),
                scene_spec_fixture=dict(payload.get("sceneSpecFixture", {})),
            )
        )
    return cases


def run_case(case: Gate0Case, *, backend: str) -> Gate0CaseResult:
    if backend != "fake" or case.backend != "fake":
        return Gate0CaseResult(
            case_id=case.case_id,
            group=case.group,
            status="blocked",
            object_completeness=0.0,
            relation_satisfaction=0.0,
            safety_pass=False,
            failure_category="environment_failure",
            blocking_reasons=[f"unsupported_backend:{backend}"],
        )

    scene = scene_from_case(case)
    snapshot = _snapshot(run_id=scene.run_id)
    compile_result = compile_scene(scene, snapshot)
    if compile_result.patch is None:
        reasons = list(compile_result.blocking_reasons)
        return Gate0CaseResult(
            case_id=case.case_id,
            group=case.group,
            status="failed",
            object_completeness=0.0,
            relation_satisfaction=0.0,
            safety_pass=False,
            failure_category=classify_failure(reasons),
            blocking_reasons=reasons,
        )

    fake_backend = FakeCadBackend()
    gateway = CadTransactionGateway(backend=fake_backend)
    receipt = gateway.execute(compile_result.patch)
    readback = fake_backend.readback(transaction_id=compile_result.patch.transaction_id)
    report = verify_scene_execution(scene=scene, compile_result=compile_result, receipt=receipt, readback=readback, snapshot=snapshot)
    observed_objects = set(readback.semantic_to_handles)
    object_completeness = _ratio(case.expected_objects, observed_objects)
    relation_satisfaction = 1.0 if report.overall_status == "passed" else 0.0
    safety_pass = (
        receipt.saved_current_dwg is case.safety.get("savedCurrentDwg", False)
        and compile_result.patch.target_layer == case.safety.get("targetLayer", "CODEX_PREVIEW")
        and not any(reason.startswith(("wrong_layer", "saved_current_dwg", "nearby_handle_modified")) for reason in report.blocking_reasons)
    )
    passed = report.overall_status == "passed" and object_completeness == 1.0 and relation_satisfaction == 1.0 and safety_pass
    reasons = list(report.blocking_reasons)
    return Gate0CaseResult(
        case_id=case.case_id,
        group=case.group,
        status="passed" if passed else "failed",
        object_completeness=object_completeness,
        relation_satisfaction=relation_satisfaction,
        safety_pass=safety_pass,
        failure_category=None if passed else classify_failure(reasons),
        blocking_reasons=reasons,
    )


def scene_from_case(case: Gate0Case) -> SceneSpec:
    fixture = case.scene_spec_fixture
    run_id = f"gate0-{case.case_id}"
    desk_width = float(fixture.get("deskWidth", 1400))
    mouse_side = str(fixture.get("mouseSide", "right"))
    include_vase = bool(fixture.get("includeVase", True))
    include_lamp = bool(fixture.get("includeLamp", False))
    monitor_count = int(fixture.get("monitorCount", 1))

    objects = [
        SceneObjectSpec(
            id="desk",
            kind="desk",
            dimensions=Dimensions2D(width=desk_width, depth=700),
            placement=PlacementIntent(mode="free_region_center"),
        )
    ]
    if monitor_count == 1:
        objects.append(SceneObjectSpec(id="monitor", kind="monitor", placement=PlacementIntent(mode="relative", on="desk", anchor="rear_center")))
        keyboard_reference = "monitor"
    else:
        objects.extend(
            [
                SceneObjectSpec(id="monitor-a", kind="monitor", placement=PlacementIntent(mode="relative", on="desk", anchor="rear_left")),
                SceneObjectSpec(
                    id="monitor-b",
                    kind="monitor",
                    placement=PlacementIntent(mode="relative", on="desk", right_of="monitor-a", align_y="monitor-a", gap=40),
                ),
            ]
        )
        keyboard_reference = "monitor-a"
    objects.append(
        SceneObjectSpec(
            id="keyboard",
            kind="keyboard",
            placement=PlacementIntent(mode="relative", on="desk", in_front_of=keyboard_reference, align_x=keyboard_reference, gap=40),
        )
    )
    mouse_relation = {"left_of": "keyboard"} if mouse_side == "left" else {"right_of": "keyboard"}
    objects.append(
        SceneObjectSpec(
            id="mouse",
            kind="mouse",
            placement=PlacementIntent(mode="relative", on="desk", align_y="keyboard", gap=40, **mouse_relation),
        )
    )
    if include_vase:
        objects.append(SceneObjectSpec(id="vase", kind="vase", placement=PlacementIntent(mode="relative", on="desk", anchor="rear_right")))
    if include_lamp:
        objects.append(SceneObjectSpec(id="lamp", kind="lamp", placement=PlacementIntent(mode="relative", on="desk", anchor="front_left")))
    return SceneSpec(schema_version="scene-spec/v1", run_id=run_id, scene_id=case.case_id, units="mm", view="plan_2d", objects=objects)


def classify_failure(blocking_reasons: list[str]) -> str:
    joined = " ".join(blocking_reasons)
    if not blocking_reasons:
        return "verification_false_negative"
    if "unsupported_object" in joined or "unsupported_generator" in joined:
        return "catalog_or_generator_missing"
    if "compile_result" in joined or "target_region" in joined or "max_entity_budget" in joined:
        return "compiler_failure"
    if "backend" in joined:
        return "backend_execution_failure"
    if "readback" in joined or "missing_object" in joined:
        return "readback_failure"
    if "saved_current_dwg" in joined or "wrong_layer" in joined or "nearby_handle_modified" in joined:
        return "safety_block_expected"
    if any(token in joined for token in ["outside_surface", "wrong_side", "severe_overlap", "bbox_mismatch", "vase_overlap"]):
        return "relation_solver_failure"
    return "semantic_planning_failure"


def _snapshot(*, run_id: str) -> DrawingSnapshot:
    return DrawingSnapshot(
        schema_version="drawing-snapshot/v1",
        run_id=run_id,
        document_id="gate0-fake",
        units="mm",
        current_space="model",
        active_layer="CODEX_PREVIEW",
        saved=False,
        target_region=(0, 0, 2200, 1400),
        nearby_entities=[],
        snapshot_hash="gate0:snapshot",
    )


def _ratio(expected: list[str], observed: set[str]) -> float:
    if not expected:
        return 1.0
    return len(set(expected) & observed) / len(set(expected))
