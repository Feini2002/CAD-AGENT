from __future__ import annotations

from pydantic import Field

from cad_agent_vnext.domain.common import StrictModel
from cad_agent_vnext.domain.patch import CadPatch


class SemanticMapping(StrictModel):
    object_to_operation: dict[str, str] = Field(default_factory=dict)
    operation_to_primitives: dict[str, list[str]] = Field(default_factory=dict)
    primitive_expected_entity_types: dict[str, str] = Field(default_factory=dict)


def build_semantic_mapping(patch: CadPatch) -> SemanticMapping:
    object_to_operation: dict[str, str] = {}
    operation_to_primitives: dict[str, list[str]] = {}
    primitive_expected_entity_types: dict[str, str] = {}
    for operation in patch.operations:
        object_to_operation[operation.semantic_object_id] = operation.op_id
        primitive_ids = [primitive.primitive_id for primitive in operation.primitives]
        operation_to_primitives[operation.op_id] = primitive_ids
        for primitive in operation.primitives:
            primitive_expected_entity_types[primitive.primitive_id] = primitive.expected_entity_type
    return SemanticMapping(
        object_to_operation=object_to_operation,
        operation_to_primitives=operation_to_primitives,
        primitive_expected_entity_types=primitive_expected_entity_types,
    )

