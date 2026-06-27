from __future__ import annotations

import pytest
from pydantic import ValidationError

from cad_agent.domain.brief import UserBrief
from cad_agent.domain.drawing import DrawingEntitySnapshot, DrawingSnapshot
from cad_agent.domain.patch import CadPatch, PatchOperation
from cad_agent.domain.primitives import Primitive
from cad_agent.domain.receipt import EntityReadback, ExecutionReceipt
from cad_agent.domain.scene import (
    Dimensions2D,
    PlacementIntent,
    SceneConstraint,
    SceneObjectSpec,
    SceneSpec,
)
from cad_agent.domain.verification import VerificationCheck, VerificationReport


def valid_brief() -> UserBrief:
    return UserBrief(
        schema_version="user-brief/v1",
        run_id="run_001",
        raw_text="draw a desk",
        request_kind="create_scene",
    )


def valid_snapshot() -> DrawingSnapshot:
    return DrawingSnapshot(
        schema_version="drawing-snapshot/v1",
        run_id="run_001",
        document_id="doc-001",
        units="mm",
        current_space="model",
        active_layer="0",
        saved=None,
        target_region=(0, 0, 2000, 1200),
        nearby_entities=[
            DrawingEntitySnapshot(handle="A1", entity_type="LWPOLYLINE", layer="0", bbox=(0, 0, 10, 10))
        ],
        snapshot_hash="sha256:abc",
    )


def valid_scene() -> SceneSpec:
    return SceneSpec(
        schema_version="scene-spec/v1",
        run_id="run_001",
        scene_id="scene-001",
        units="mm",
        view="plan_2d",
        objects=[
            SceneObjectSpec(
                id="desk",
                kind="desk",
                dimensions=Dimensions2D(width=1400, depth=700),
                placement=PlacementIntent(mode="free_region_center"),
            ),
            SceneObjectSpec(
                id="monitor",
                kind="monitor",
                placement=PlacementIntent(mode="relative", on="desk", anchor="rear_center"),
            ),
        ],
        constraints=[SceneConstraint(id="c1", type="inside_surface", members=["monitor"], reference="desk")],
    )


def valid_primitive() -> Primitive:
    return Primitive(
        primitive_id="prim-001",
        semantic_object_id="desk",
        primitive_type="rectangle",
        geometry={"origin": [0, 0], "width": 1400, "depth": 700},
        layer="CODEX_PREVIEW",
        style_token="preview.default",
        expected_entity_type="LWPOLYLINE",
    )


def valid_patch() -> CadPatch:
    return CadPatch(
        schema_version="cad-patch/v1",
        run_id="run_001",
        transaction_id="txn-001",
        target_layer="CODEX_PREVIEW",
        operations=[
            PatchOperation(
                op_id="op-001",
                action="create",
                semantic_object_id="desk",
                primitives=[valid_primitive()],
            )
        ],
        forbidden_effects=["dwg_save", "formal_layer_write"],
    )


def valid_receipt() -> ExecutionReceipt:
    return ExecutionReceipt(
        schema_version="execution-receipt/v1",
        run_id="run_001",
        transaction_id="txn-001",
        backend="fake",
        status="succeeded",
        semantic_to_handles={"desk": ["A1"]},
        entities=[EntityReadback(handle="A1", entity_type="LWPOLYLINE", layer="CODEX_PREVIEW", bbox=(0, 0, 10, 10))],
        created_handles=["A1"],
        updated_handles=[],
        deleted_handles=[],
        saved_current_dwg=False,
        rollback_token="rollback-001",
        errors=[],
        warnings=[],
    )


def valid_report() -> VerificationReport:
    return VerificationReport(
        schema_version="verification-report/v1",
        run_id="run_001",
        overall_status="passed",
        checks=[
            VerificationCheck(
                check_id="layer-check",
                status="passed",
                severity="blocking",
                subject_ids=["desk"],
                expected={"layer": "CODEX_PREVIEW"},
                observed={"layer": "CODEX_PREVIEW"},
                evidence_refs=["execution_receipt.json"],
                repair_hint=None,
            )
        ],
        allowed_claims=["preview geometry verified"],
        blocking_reasons=[],
    )


@pytest.mark.parametrize(
    "factory",
    [valid_brief, valid_snapshot, valid_scene, valid_primitive, valid_patch, valid_receipt, valid_report],
)
def test_contracts_round_trip(factory):
    model = factory()

    payload = model.model_dump(mode="json")
    restored = type(model).model_validate(payload)

    assert restored == model


@pytest.mark.parametrize(
    "model_cls,payload,missing_field",
    [
        (UserBrief, lambda: valid_brief().model_dump(mode="json"), "run_id"),
        (DrawingSnapshot, lambda: valid_snapshot().model_dump(mode="json"), "document_id"),
        (SceneSpec, lambda: valid_scene().model_dump(mode="json"), "scene_id"),
        (Primitive, lambda: valid_primitive().model_dump(mode="json"), "primitive_id"),
        (CadPatch, lambda: valid_patch().model_dump(mode="json"), "transaction_id"),
        (ExecutionReceipt, lambda: valid_receipt().model_dump(mode="json"), "backend"),
        (VerificationReport, lambda: valid_report().model_dump(mode="json"), "overall_status"),
    ],
)
def test_contracts_reject_missing_required_field(model_cls, payload, missing_field):
    data = payload()
    data.pop(missing_field)

    with pytest.raises(ValidationError):
        model_cls.model_validate(data)


@pytest.mark.parametrize(
    "model_cls,payload",
    [
        (UserBrief, lambda: valid_brief().model_dump(mode="json")),
        (DrawingSnapshot, lambda: valid_snapshot().model_dump(mode="json")),
        (SceneSpec, lambda: valid_scene().model_dump(mode="json")),
        (Primitive, lambda: valid_primitive().model_dump(mode="json")),
        (CadPatch, lambda: valid_patch().model_dump(mode="json")),
        (ExecutionReceipt, lambda: valid_receipt().model_dump(mode="json")),
        (VerificationReport, lambda: valid_report().model_dump(mode="json")),
    ],
)
def test_contracts_reject_extra_fields(model_cls, payload):
    data = payload()
    data["unexpected"] = True

    with pytest.raises(ValidationError):
        model_cls.model_validate(data)


@pytest.mark.parametrize(
    "model_cls,payload",
    [
        (UserBrief, lambda: valid_brief().model_dump(mode="json")),
        (DrawingSnapshot, lambda: valid_snapshot().model_dump(mode="json")),
        (SceneSpec, lambda: valid_scene().model_dump(mode="json")),
    ],
)
def test_contracts_reject_invalid_units(model_cls, payload):
    data = payload()
    data["units"] = "inch"

    with pytest.raises(ValidationError):
        model_cls.model_validate(data)


def test_scene_rejects_duplicate_object_ids():
    data = valid_scene().model_dump(mode="json")
    data["objects"].append(data["objects"][0])

    with pytest.raises(ValidationError, match="duplicate object id"):
        SceneSpec.model_validate(data)


def test_scene_rejects_missing_relation_reference():
    data = valid_scene().model_dump(mode="json")
    data["constraints"][0]["reference"] = "missing-desk"

    with pytest.raises(ValidationError, match="unknown object reference"):
        SceneSpec.model_validate(data)


def test_scene_rejects_non_preview_target_layer():
    data = valid_scene().model_dump(mode="json")
    data["target_layer"] = "A-WALL"

    with pytest.raises(ValidationError):
        SceneSpec.model_validate(data)


def test_patch_rejects_save_current_dwg_true():
    data = valid_patch().model_dump(mode="json")
    data["save_current_dwg"] = True

    with pytest.raises(ValidationError):
        CadPatch.model_validate(data)
