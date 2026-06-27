"""Pure domain contracts for cleanroom."""

from cad_agent.domain.brief import UserBrief
from cad_agent.domain.drawing import DrawingEntitySnapshot, DrawingSnapshot
from cad_agent.domain.patch import CadPatch, PatchOperation
from cad_agent.domain.primitives import Primitive
from cad_agent.domain.receipt import EntityReadback, ExecutionReceipt
from cad_agent.domain.scene import Dimensions2D, PlacementIntent, SceneConstraint, SceneObjectSpec, SceneSpec
from cad_agent.domain.verification import VerificationCheck, VerificationReport

__all__ = [
    "CadPatch",
    "Dimensions2D",
    "DrawingEntitySnapshot",
    "DrawingSnapshot",
    "EntityReadback",
    "ExecutionReceipt",
    "PatchOperation",
    "PlacementIntent",
    "Primitive",
    "SceneConstraint",
    "SceneObjectSpec",
    "SceneSpec",
    "UserBrief",
    "VerificationCheck",
    "VerificationReport",
]
