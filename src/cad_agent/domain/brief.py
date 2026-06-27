from __future__ import annotations

from typing import Literal

from pydantic import Field

from cad_agent.domain.common import StrictModel, Units


class UserBrief(StrictModel):
    schema_version: Literal["user-brief/v1"]
    run_id: str
    raw_text: str
    request_kind: Literal["create_scene", "modify_scene", "inspect", "unknown"]
    units: Units = "mm"
    target_view: Literal["plan_2d"] = "plan_2d"
    explicit_constraints: list[str] = Field(default_factory=list)
    assumptions_allowed: bool = True
    cad_write_authorized: bool = False
    save_current_dwg_authorized: bool = False
