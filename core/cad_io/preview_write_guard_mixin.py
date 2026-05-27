"""Shared preview-only write guard for CAD drivers (real COM and fake)."""

from __future__ import annotations

from typing import Any

from core.safety.policy import PREVIEW_LAYER
from core.safety.write_guard import CadWriteGuard, CadWriteGuardViolation


class PreviewWriteGuardMixin:
    """Mixin: block formal-layer writes and destructive DWG operations in preview sessions."""

    write_guard: CadWriteGuard

    def _init_preview_write_guard(self, *, preview_layer: str = PREVIEW_LAYER) -> None:
        self.write_guard = CadWriteGuard(enabled=True, preview_layer=preview_layer)

    def _guard_preview_layer_write(self, layer: str | None) -> None:
        if layer is not None:
            self.write_guard.assert_preview_layer_write(layer)

    def save_document(self) -> None:
        self.write_guard.assert_save_allowed()
        raise CadWriteGuardViolation("DWG save blocked in preview-only CAD session")

    def overwrite_document(self) -> None:
        self.write_guard.assert_overwrite_allowed()
        raise CadWriteGuardViolation("DWG overwrite blocked in preview-only CAD session")

    def delete_entity_by_handle(self, handle: str) -> None:
        self.write_guard.assert_delete_allowed()
        raise CadWriteGuardViolation("Entity delete blocked in preview-only CAD session")
