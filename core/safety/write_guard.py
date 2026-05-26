"""Runtime guards blocking save, delete, and formal-layer writes during preview CAD sessions."""

from __future__ import annotations

from typing import Any

from core.safety.policy import PREVIEW_LAYER


class CadWriteGuardViolation(RuntimeError):
    """Raised when a preview-only CAD session attempts a forbidden write."""


class CadWriteGuard:
    def __init__(
        self,
        *,
        enabled: bool = True,
        preview_layer: str = PREVIEW_LAYER,
        allow_formal_layer: bool = False,
        allow_save: bool = False,
        allow_delete: bool = False,
        allow_overwrite: bool = False,
    ) -> None:
        self.enabled = enabled
        self.preview_layer = preview_layer
        self.allow_formal_layer = allow_formal_layer
        self.allow_save = allow_save
        self.allow_delete = allow_delete
        self.allow_overwrite = allow_overwrite
        self.blocked_attempts: list[dict[str, str]] = []

    def _record_block(self, operation: str, message: str) -> None:
        self.blocked_attempts.append({"operation": operation, "message": message})

    def assert_preview_layer_write(self, layer: str | None) -> None:
        if not self.enabled or layer is None:
            return
        if layer == self.preview_layer:
            return
        if self.allow_formal_layer:
            return
        message = f"Formal layer write blocked: {layer!r} (preview-only session allows {self.preview_layer!r})"
        self._record_block("write_formal_layer", message)
        raise CadWriteGuardViolation(message)

    def assert_save_allowed(self) -> None:
        if not self.enabled or self.allow_save:
            return
        message = "DWG save blocked in preview-only CAD session"
        self._record_block("save", message)
        raise CadWriteGuardViolation(message)

    def assert_overwrite_allowed(self) -> None:
        if not self.enabled or self.allow_overwrite:
            return
        message = "DWG overwrite blocked in preview-only CAD session"
        self._record_block("overwrite", message)
        raise CadWriteGuardViolation(message)

    def assert_delete_allowed(self) -> None:
        if not self.enabled or self.allow_delete:
            return
        message = "Entity delete blocked in preview-only CAD session"
        self._record_block("delete", message)
        raise CadWriteGuardViolation(message)


def _check(name: str, status: str, message: str) -> dict[str, str]:
    return {"name": name, "status": status, "message": message}


def _non_preview_entity_count(driver: Any, *, preview_layer: str) -> int:
    if not hasattr(driver, "snapshot_modelspace"):
        return 0
    entities = driver.snapshot_modelspace()
    return sum(1 for entity in entities if isinstance(entity, dict) and entity.get("layer") not in {None, "", preview_layer})


def run_negative_write_guard_checks(driver: Any, *, preview_layer: str = PREVIEW_LAYER) -> dict[str, Any]:
    """Attempt forbidden save/delete/formal-layer writes; all must be blocked without new formal entities."""

    guard = getattr(driver, "write_guard", None)
    if not isinstance(guard, CadWriteGuard):
        guard = CadWriteGuard(enabled=True, preview_layer=preview_layer)

    checks: list[dict[str, str]] = []
    formal_before = _non_preview_entity_count(driver, preview_layer=preview_layer)

    def expect_blocked(operation: str, callback: Any) -> None:
        try:
            callback()
        except CadWriteGuardViolation as exc:
            checks.append(_check(f"block_{operation}", "pass", str(exc)))
        except Exception as exc:
            checks.append(_check(f"block_{operation}", "fail", f"unexpected error: {exc}"))
        else:
            checks.append(_check(f"block_{operation}", "fail", f"{operation} was not blocked"))

    expect_blocked(
        "formal_layer_write",
        lambda: driver.draw_line(
            start_point=[0, 0, 0],
            end_point=[10, 0, 0],
            layer="WALL",
        ),
    )
    if hasattr(driver, "save_document"):
        expect_blocked("save", driver.save_document)
    if hasattr(driver, "overwrite_document"):
        expect_blocked("overwrite", driver.overwrite_document)
    if hasattr(driver, "delete_entity_by_handle"):
        expect_blocked("delete", lambda: driver.delete_entity_by_handle("H999"))

    formal_after = _non_preview_entity_count(driver, preview_layer=preview_layer)
    no_new_formal = formal_after == formal_before
    checks.append(
        _check(
            "no_new_formal_entities",
            "pass" if no_new_formal else "fail",
            f"formal entities before={formal_before} after={formal_after}",
        )
    )

    failed = [check for check in checks if check["status"] != "pass"]
    return {
        "status": "pass" if not failed else "fail",
        "preview_layer": preview_layer,
        "blocked_attempt_count": len(guard.blocked_attempts),
        "blocked_attempts": list(guard.blocked_attempts),
        "checks": checks,
    }
