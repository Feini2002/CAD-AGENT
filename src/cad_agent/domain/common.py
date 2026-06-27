from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


Point2D = tuple[float, float]
BBox2D = tuple[float, float, float, float]
Units = Literal["mm"]
