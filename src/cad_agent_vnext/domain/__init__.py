"""Pure domain contracts for vNext."""

from cad_agent_vnext.domain.brief import UserBrief
from cad_agent_vnext.domain.drawing import DrawingEntitySnapshot, DrawingSnapshot
from cad_agent_vnext.domain.patch import CadPatch, PatchOperation
from cad_agent_vnext.domain.primitives import Primitive
from cad_agent_vnext.domain.receipt import EntityReadback, ExecutionReceipt
from cad_agent_vnext.domain.scene import Dimensions2D, PlacementIntent, SceneConstraint, SceneObjectSpec, SceneSpec
from cad_agent_vnext.domain.verification import VerificationCheck, VerificationReport

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
