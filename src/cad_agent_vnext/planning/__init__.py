"""Pure planning and geometry-solving boundary for vNext."""

from cad_agent_vnext.planning.footprints import Footprint, ResolvedPose
from cad_agent_vnext.planning.object_catalog import ObjectCatalog, load_object_catalog
from cad_agent_vnext.planning.object_generators import generate_object_primitives
from cad_agent_vnext.planning.relation_solver import RelationSolveResult, solve_scene_relations
from cad_agent_vnext.planning.scene_compiler import CompileSceneResult, compile_scene

__all__ = [
    "CompileSceneResult",
    "Footprint",
    "ObjectCatalog",
    "RelationSolveResult",
    "ResolvedPose",
    "generate_object_primitives",
    "load_object_catalog",
    "compile_scene",
    "solve_scene_relations",
]
