"""Pluggable geometry backend declarations.

The current default is a no-dependency CAD_PLAN rectangle backend. External
geometry kernels are only declared as optional slots until the project chooses
to adopt and verify them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.verification.geometry_checks import check_plan_geometry


@dataclass(frozen=True)
class GeometryBackend:
    backend_id: str
    title: str
    available: bool
    requires_dependency: bool
    requires_cad: bool
    supported_models: list[str]
    notes: str

    def to_spec(self) -> dict[str, Any]:
        return {
            "backend_id": self.backend_id,
            "title": self.title,
            "available": self.available,
            "requires_dependency": self.requires_dependency,
            "requires_cad": self.requires_cad,
            "supported_models": list(self.supported_models),
            "notes": self.notes,
        }


class CadPlanRect2DBackend(GeometryBackend):
    def validate_plan_geometry(
        self,
        plan: dict[str, Any],
        *,
        boundary: dict[str, list[float | int]] | None = None,
        other_bboxes: list[dict[str, list[float | int]]] | None = None,
    ) -> dict[str, Any]:
        checks = check_plan_geometry(plan, boundary=boundary, other_bboxes=other_bboxes)
        failed = [check for check in checks if check.get("status") == "fail"]
        return {
            "backend_id": self.backend_id,
            "status": "fail" if failed else "pass",
            "checks": checks,
            "errors": [check.get("message", check.get("name", "geometry check failed")) for check in failed],
        }


_BACKENDS: dict[str, GeometryBackend] = {
    "cad_plan_rect2d": CadPlanRect2DBackend(
        backend_id="cad_plan_rect2d",
        title="CAD_PLAN 2D rectangle checks",
        available=True,
        requires_dependency=False,
        requires_cad=False,
        supported_models=["cad_plan", "layout_bbox"],
        notes="Built-in bbox, boundary and overlap checks for non-CAD verification.",
    ),
    "cadquery": GeometryBackend(
        backend_id="cadquery",
        title="CadQuery optional solid modeling slot",
        available=False,
        requires_dependency=True,
        requires_cad=False,
        supported_models=["parametric_solid", "step"],
        notes="Declared as a future adapter slot; not imported or required by Core.",
    ),
    "build123d": GeometryBackend(
        backend_id="build123d",
        title="build123d optional solid modeling slot",
        available=False,
        requires_dependency=True,
        requires_cad=False,
        supported_models=["parametric_solid", "step"],
        notes="Declared as a future adapter slot; not imported or required by Core.",
    ),
    "ifcopenshell": GeometryBackend(
        backend_id="ifcopenshell",
        title="IfcOpenShell optional BIM geometry slot",
        available=False,
        requires_dependency=True,
        requires_cad=False,
        supported_models=["ifc", "bim_element"],
        notes="Declared as a future adapter slot for BIM exchange; not imported by Core.",
    ),
}


def list_geometry_backends() -> list[dict[str, Any]]:
    return [_BACKENDS[backend_id].to_spec() for backend_id in sorted(_BACKENDS)]


def get_geometry_backend(backend_id: str) -> GeometryBackend:
    if backend_id not in _BACKENDS:
        raise KeyError(f"Unknown geometry backend: {backend_id}")
    return _BACKENDS[backend_id]
