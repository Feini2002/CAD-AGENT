from __future__ import annotations

from pydantic import Field

from cad_agent.domain.common import StrictModel
from cad_agent.domain.scene import SceneObjectSpec


class RelationGraph(StrictModel):
    status: str
    dependencies: dict[str, list[str]] = Field(default_factory=dict)
    order: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


def build_relation_graph(objects: list[SceneObjectSpec]) -> RelationGraph:
    object_ids = [item.id for item in objects]
    known = set(object_ids)
    dependencies: dict[str, list[str]] = {item.id: [] for item in objects}
    errors: list[str] = []

    for item in objects:
        for reference in _references(item):
            if reference not in known:
                errors.append(f"unknown_object_reference:{item.id}:{reference}")
            elif reference == item.id:
                errors.append(f"relation_cycle:{item.id}")
            elif reference not in dependencies[item.id]:
                dependencies[item.id].append(reference)

    if errors:
        return RelationGraph(status="blocked", dependencies=dependencies, order=[], errors=_unique(errors))

    order = _topological_order(object_ids, dependencies)
    if order is None:
        remaining = sorted(item for item in object_ids if dependencies[item])
        return RelationGraph(
            status="blocked",
            dependencies=dependencies,
            order=[],
            errors=[f"relation_cycle:{','.join(remaining)}"],
        )
    return RelationGraph(status="ok", dependencies=dependencies, order=order, errors=[])


def _references(item: SceneObjectSpec) -> list[str]:
    placement = item.placement
    refs = [
        placement.on,
        placement.in_front_of,
        placement.behind,
        placement.left_of,
        placement.right_of,
        placement.align_x,
        placement.align_y,
    ]
    return [str(ref) for ref in refs if ref]


def _topological_order(object_ids: list[str], dependencies: dict[str, list[str]]) -> list[str] | None:
    pending = {key: set(value) for key, value in dependencies.items()}
    order: list[str] = []
    while pending:
        ready = [object_id for object_id in object_ids if object_id in pending and not pending[object_id]]
        if not ready:
            return None
        for object_id in ready:
            order.append(object_id)
            pending.pop(object_id)
            for deps in pending.values():
                deps.discard(object_id)
    return order


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result

