"""Readback and deterministic verification boundary for vNext."""
from cad_agent_vnext.verification.repair_planner import RepairPlanResult, plan_scene_repair
from cad_agent_vnext.verification.scene_verifier import verify_scene_execution

__all__ = ["RepairPlanResult", "plan_scene_repair", "verify_scene_execution"]
