#!/usr/bin/env python
"""Render or capture a preview after CAD execution."""

from __future__ import annotations

import argparse
import ctypes
import importlib.util
import json
import math
import sys
from pathlib import Path
from time import sleep
from typing import Any, Callable, Protocol


class CapturableImage(Protocol):
    def save(self, path: Path) -> None:
        ...


def module_available(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except ModuleNotFoundError:
        return False


AUTOCAD_WINDOW_TITLE_MARKERS = ("Autodesk AutoCAD", "AutoCAD", ".dwg", ".dwt")

# PrintWindow flags (winuser.h)
PW_CLIENTONLY = 0x00000001
PW_RENDERFULLCONTENT = 0x00000002
VISUAL_AID_ONLY = "visual_aid_only"


def switch_to_input_desktop() -> dict[str, object]:
    """Let sandboxed helper processes see the user's interactive Windows desktop."""

    if sys.platform != "win32":
        return {"status": "not_required", "reason": "non-Windows platform"}
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    access = 0x0001 | 0x0002 | 0x0040 | 0x0080 | 0x0100
    input_desktop = user32.OpenInputDesktop(0, False, access)
    if not input_desktop:
        return {"status": "fail", "api": "OpenInputDesktop", "lastError": int(kernel32.GetLastError())}
    ok = bool(user32.SetThreadDesktop(input_desktop))
    return {
        "status": "pass" if ok else "fail",
        "api": "SetThreadDesktop",
        "lastError": int(kernel32.GetLastError()),
    }


def _window_matches_autocad(title: str) -> bool:
    normalized = title.strip()
    if not normalized:
        return False
    return any(marker.lower() in normalized.lower() for marker in AUTOCAD_WINDOW_TITLE_MARKERS)


def _client_bbox(hwnd: int, win32gui_module: Any) -> tuple[int, int, int, int]:
    try:
        left, top, right, bottom = win32gui_module.GetClientRect(hwnd)
        screen_left, screen_top = win32gui_module.ClientToScreen(hwnd, (left, top))
        screen_right, screen_bottom = win32gui_module.ClientToScreen(hwnd, (right, bottom))
        if screen_right > screen_left and screen_bottom > screen_top:
            return (int(screen_left), int(screen_top), int(screen_right), int(screen_bottom))
    except Exception:
        pass
    left, top, right, bottom = win32gui_module.GetWindowRect(hwnd)
    return (int(left), int(top), int(right), int(bottom))


def _target_from_hwnd(hwnd: int, win32gui_module: Any) -> dict[str, object]:
    title = str(win32gui_module.GetWindowText(hwnd))
    bbox = _client_bbox(hwnd, win32gui_module)
    return {"hwnd": int(hwnd), "title": title, "bbox": list(bbox)}


def _bbox_area(bbox: list[object]) -> int:
    if len(bbox) != 4:
        return 0
    return max(0, int(bbox[2]) - int(bbox[0])) * max(0, int(bbox[3]) - int(bbox[1]))


def _usable_bbox(bbox: list[object]) -> bool:
    if len(bbox) != 4:
        return False
    width = int(bbox[2]) - int(bbox[0])
    height = int(bbox[3]) - int(bbox[1])
    return width >= 320 and height >= 240 and int(bbox[2]) > 0 and int(bbox[3]) > 0


def find_autocad_window(*, win32gui_module: Any | None = None, include_minimized: bool = False) -> dict[str, object] | None:
    """Find a visible AutoCAD window and return a screen-space client bbox."""

    if win32gui_module is None:
        try:
            import win32gui as win32gui_module
        except ImportError:
            return None

    candidates: list[dict[str, object]] = []

    def collect(hwnd: int, _: object) -> None:
        try:
            if not win32gui_module.IsWindowVisible(hwnd):
                return
            if hasattr(win32gui_module, "IsIconic") and win32gui_module.IsIconic(hwnd) and not include_minimized:
                return
            title = str(win32gui_module.GetWindowText(hwnd))
        except Exception:
            return
        if not _window_matches_autocad(title):
            return
        target = _target_from_hwnd(hwnd, win32gui_module)
        if not include_minimized and not _usable_bbox(target["bbox"]):  # type: ignore[arg-type]
            return
        candidates.append(target)

    win32gui_module.EnumWindows(collect, None)
    if not candidates:
        return None
    return max(candidates, key=lambda candidate: _bbox_area(candidate.get("bbox", [])))  # type: ignore[arg-type]


def _restore_and_focus_window(hwnd: int, win32gui_module: Any) -> None:
    if hasattr(win32gui_module, "ShowWindow"):
        win32gui_module.ShowWindow(hwnd, 9)  # SW_RESTORE
    if hasattr(win32gui_module, "BringWindowToTop"):
        try:
            win32gui_module.BringWindowToTop(hwnd)
        except Exception:
            pass
    if hasattr(win32gui_module, "SetForegroundWindow"):
        try:
            win32gui_module.SetForegroundWindow(hwnd)
        except Exception:
            pass
    sleep(0.3)


def ensure_autocad_visible(
    *,
    autocad_window_finder: Callable[[], dict[str, object] | None] | None = None,
    settle_seconds: float = 0.15,
) -> dict[str, object]:
    """Restore AutoCAD only when minimized; do not steal desktop foreground or resize."""

    if autocad_window_finder is None:
        try:
            import win32gui
        except ImportError as exc:
            raise RuntimeError("win32gui is required to locate AutoCAD.") from exc
        target = find_autocad_window(win32gui_module=win32gui, include_minimized=True)
        if target is None:
            raise RuntimeError("AutoCAD window is not visible; cannot capture.")
        hwnd = int(target["hwnd"])
        if hasattr(win32gui, "IsIconic") and win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, 9)  # SW_RESTORE only
            sleep(settle_seconds)
        return _target_from_hwnd(hwnd, win32gui)

    target = autocad_window_finder()
    if target is None:
        raise RuntimeError("AutoCAD window is not visible; cannot capture.")
    return target


def get_preview_capabilities(
    output: Path,
    *,
    module_checker: Callable[[str], bool] = module_available,
    autocad_window_finder: Callable[[], dict[str, object] | None] = find_autocad_window,
) -> dict[str, object]:
    """Report screenshot dependencies without touching the screen."""

    dependencies = {
        "pillow_imagegrab": module_checker("PIL.ImageGrab"),
        "win32gui": module_checker("win32gui"),
        "win32ui": module_checker("win32ui"),
    }
    capture_modes: list[str] = []
    if dependencies["pillow_imagegrab"]:
        capture_modes.append("screen")

    autocad_window: dict[str, object] = {"status": "unavailable"}
    autocad_viewport_or_client: dict[str, object] = {"status": "unavailable"}
    if dependencies["pillow_imagegrab"] and dependencies["win32gui"] and dependencies["win32ui"]:
        try:
            target = autocad_window_finder()
        except Exception as exc:
            target = None
            autocad_window["detail"] = str(exc)
        if target:
            capture_modes.append("autocad_window")
            capture_modes.append("autocad_viewport_or_client")
            autocad_window = {
                "status": "ready",
                "hwnd": target.get("hwnd"),
                "title": target.get("title", ""),
                "bbox": target.get("bbox", []),
            }
            autocad_viewport_or_client = {
                "status": "ready_with_execution_summary",
                "basis": "AutoCAD window plus optional created_handles bbox focus",
            }

    return {
        "status": "ready" if capture_modes else "unavailable",
        "output": str(output),
        "output_dir": str(output.parent),
        "output_dir_exists": output.parent.exists(),
        "dependencies": dependencies,
        "capture_modes": capture_modes,
        "autocad_window": autocad_window,
        "autocad_viewport_or_client": autocad_viewport_or_client,
        "note": (
            "AutoCAD capture uses PrintWindow on the client area so IDE overlays are not baked in. "
            "Screenshot geometry remains visual aid only; CAD accuracy requires created-handle readback."
        ),
    }


def capture_hwnd_client_printwindow(hwnd: int) -> CapturableImage:
    """Capture a window client area via PrintWindow (not occluded by other apps on screen)."""

    try:
        import win32gui
        import win32ui
        from ctypes import windll
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("win32gui, win32ui, and Pillow are required for PrintWindow capture.") from exc

    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    width = int(right - left)
    height = int(bottom - top)
    if width < 1 or height < 1:
        raise RuntimeError(f"AutoCAD client rect is empty: {(left, top, right, bottom)}")

    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(bitmap)

    flags = PW_CLIENTONLY | PW_RENDERFULLCONTENT
    ok = bool(windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), flags))
    if not ok:
        ok = bool(windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), PW_CLIENTONLY))
    if not ok:
        win32gui.DeleteObject(bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)
        raise RuntimeError("PrintWindow failed for AutoCAD hwnd.")

    bmpinfo = bitmap.GetInfo()
    bmpstr = bitmap.GetBitmapBits(True)
    image = Image.frombuffer(
        "RGB",
        (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
        bmpstr,
        "raw",
        "BGRX",
        0,
        1,
    )

    win32gui.DeleteObject(bitmap.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)
    return image


def capture_screen(
    output: Path,
    *,
    grabber: Callable[[], CapturableImage] | None = None,
) -> dict[str, object]:
    """Capture the visible screen to a PNG-like path.

    The grabber is injectable so tests can verify file writing without reading
    the user's actual display.
    """

    if grabber is None:
        try:
            from PIL import ImageGrab
        except ImportError as exc:
            raise RuntimeError("Pillow ImageGrab is required for screenshot capture.") from exc
        grabber = ImageGrab.grab

    output.parent.mkdir(parents=True, exist_ok=True)
    image = grabber()
    image.save(output)
    return {
        "status": "captured",
        "output": str(output),
        "mode": "screen",
    }


def bring_autocad_to_foreground(
    *,
    autocad_window_finder: Callable[[], dict[str, object] | None] | None = None,
    settle_seconds: float = 0.35,
) -> dict[str, object]:
    """Restore AutoCAD and bring it to the desktop foreground before capture or zoom."""

    if autocad_window_finder is None:
        try:
            import win32gui
        except ImportError as exc:
            raise RuntimeError("win32gui is required to focus AutoCAD.") from exc
        target = find_autocad_window(win32gui_module=win32gui, include_minimized=True)
        if target is None:
            raise RuntimeError("AutoCAD window is not visible; cannot bring to foreground.")
        hwnd = int(target["hwnd"])
        _restore_and_focus_window(hwnd, win32gui)
        sleep(settle_seconds)
        return _target_from_hwnd(hwnd, win32gui)

    target = autocad_window_finder()
    if target is None:
        raise RuntimeError("AutoCAD window is not visible; cannot bring to foreground.")
    return target


def capture_autocad_window(
    output: Path,
    *,
    autocad_window_finder: Callable[[], dict[str, object] | None] | None = None,
    grabber: Callable[..., CapturableImage] | None = None,
    hwnd_capturer: Callable[[int], CapturableImage] | None = None,
    foreground_first: bool = True,
    settle_seconds: float = 0.2,
    use_screen_grab: bool = False,
) -> dict[str, object]:
    """Capture AutoCAD client area.

    Default: PrintWindow on hwnd (immune to other windows drawn on top in screen space).
    Legacy: ``use_screen_grab=True`` or inject ``grabber`` for desktop bbox capture (can include IDE overlay).
    """

    if foreground_first:
        target = bring_autocad_to_foreground(
            autocad_window_finder=autocad_window_finder,
            settle_seconds=settle_seconds,
        )
    elif autocad_window_finder is None:
        try:
            import win32gui
        except ImportError as exc:
            raise RuntimeError("win32gui is required for AutoCAD window capture.") from exc
        target = find_autocad_window(win32gui_module=win32gui, include_minimized=True)
    else:
        target = autocad_window_finder()
    if target is None:
        raise RuntimeError("AutoCAD window is not visible; cannot capture AutoCAD window.")

    raw_bbox = target.get("bbox")
    if not isinstance(raw_bbox, list) or len(raw_bbox) != 4:
        raise RuntimeError("AutoCAD window bbox is unavailable; cannot capture AutoCAD window.")
    bbox = tuple(int(value) for value in raw_bbox)
    if bbox[2] <= bbox[0] or bbox[3] <= bbox[1]:
        raise RuntimeError(f"AutoCAD window bbox is invalid: {bbox}")

    output.parent.mkdir(parents=True, exist_ok=True)
    hwnd = int(target["hwnd"])
    capture_mode = "autocad_window_printwindow"

    if grabber is not None or use_screen_grab:
        if grabber is None:
            try:
                from PIL import ImageGrab
            except ImportError as exc:
                raise RuntimeError("Pillow ImageGrab is required for screen-grab capture.") from exc
            grabber = ImageGrab.grab
        image = grabber(bbox=bbox)
        capture_mode = "autocad_window_screen_grab"
    else:
        capturer = hwnd_capturer or capture_hwnd_client_printwindow
        image = capturer(hwnd)

    image.save(output)
    return {
        "status": "captured",
        "output": str(output),
        "mode": capture_mode,
        "window_title": str(target.get("title", "")),
        "bbox": list(bbox),
        "hwnd": hwnd,
        "foreground_first": foreground_first,
        "occlusion_safe": capture_mode == "autocad_window_printwindow",
    }


def _load_json_object(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _normalize_handles(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(handle).strip() for handle in value if str(handle).strip()]


def _normalize_bbox(value: object) -> dict[str, list[float]] | None:
    if isinstance(value, (list, tuple)) and len(value) == 4:
        try:
            min_x, min_y, max_x, max_y = [float(item) for item in value]
        except (TypeError, ValueError):
            return None
    elif isinstance(value, dict):
        minimum = value.get("min")
        maximum = value.get("max")
        if not isinstance(minimum, list) or not isinstance(maximum, list) or len(minimum) < 2 or len(maximum) < 2:
            return None
        try:
            min_x, min_y = float(minimum[0]), float(minimum[1])
            max_x, max_y = float(maximum[0]), float(maximum[1])
        except (TypeError, ValueError):
            return None
    else:
        return None
    if not all(math.isfinite(value) for value in (min_x, min_y, max_x, max_y)):
        return None
    if max_x <= min_x or max_y <= min_y:
        return None
    return {"min": [min_x, min_y], "max": [max_x, max_y]}


def _load_created_handles(execution_summary: Path) -> list[str]:
    return _normalize_handles(_load_json_object(execution_summary).get("created_handles"))


def _repair_plan_payload(repair_plan: dict[str, object] | Path | None) -> dict[str, object]:
    if isinstance(repair_plan, Path):
        return _load_json_object(repair_plan)
    return repair_plan if isinstance(repair_plan, dict) else {}


def _execution_summary_payload(execution_summary: Path | dict[str, object] | None) -> dict[str, object]:
    if isinstance(execution_summary, Path):
        return _load_json_object(execution_summary)
    return execution_summary if isinstance(execution_summary, dict) else {}


def _focus_target(
    *,
    execution_summary: Path | dict[str, object] | None = None,
    target_handles: list[str] | None = None,
    target_bbox: dict[str, list[float]] | list[float] | None = None,
    repair_plan: dict[str, object] | Path | None = None,
) -> dict[str, object]:
    local_handles = _normalize_handles(target_handles or [])
    if local_handles:
        return {"kind": "handles", "source": "target_handles", "handles": local_handles}

    repair = _repair_plan_payload(repair_plan)
    repair_handles = _normalize_handles(repair.get("target_handles"))
    if repair_handles:
        return {"kind": "handles", "source": "repair_plan.target_handles", "handles": repair_handles}
    repair_bbox = _normalize_bbox(repair.get("target_bbox"))
    if repair_bbox:
        return {"kind": "bbox", "source": "repair_plan.target_bbox", "bbox": repair_bbox}

    explicit_bbox = _normalize_bbox(target_bbox)
    if explicit_bbox:
        return {"kind": "bbox", "source": "explicit_bbox", "bbox": explicit_bbox}

    summary = _execution_summary_payload(execution_summary)
    summary_handles = _normalize_handles(summary.get("created_handles"))
    if summary_handles:
        return {
            "kind": "handles",
            "source": "execution_summary.created_handles",
            "handles": summary_handles,
        }
    for key in ("target_bbox", "created_bbox", "batch_bbox"):
        summary_bbox = _normalize_bbox(summary.get(key))
        if summary_bbox:
            return {"kind": "bbox", "source": f"execution_summary.{key}", "bbox": summary_bbox}
    return {"kind": "none", "source": "none"}


def build_screenshot_decision(
    *,
    task_kind: str = "",
    evidence_stage: str = "",
    execution_summary: Path | dict[str, object] | None = None,
    target_handles: list[str] | None = None,
    target_bbox: dict[str, list[float]] | list[float] | None = None,
    repair_plan: dict[str, object] | Path | None = None,
    capture_requested: bool | None = None,
    key_readback_passed: bool = False,
    visual_issue: bool = False,
    formal_acceptance: bool = False,
    agent_role: str = "",
) -> dict[str, object]:
    """Decide whether a CAD task needs a task-scoped screenshot and how to focus it."""

    target = _focus_target(
        execution_summary=execution_summary,
        target_handles=target_handles,
        target_bbox=target_bbox,
        repair_plan=repair_plan,
    )
    focus_source = str(target.get("source", "none"))
    focus_kind = str(target.get("kind", "none"))
    local_sources = {"target_handles", "repair_plan.target_handles", "repair_plan.target_bbox", "explicit_bbox"}
    local_target = focus_source in local_sources
    stage = str(evidence_stage or task_kind or "")
    formal_stage = formal_acceptance or stage in {
        "formal_acceptance",
        "focused_retraining",
        "visual_review",
        "local_repair",
        "training_batch",
    }

    if (
        task_kind == "quick_trial"
        and key_readback_passed
        and not visual_issue
        and not formal_acceptance
        and capture_requested is not True
    ):
        should_capture = False
        required = False
        reason = "quick_trial_key_readback_enough"
    else:
        required = bool(local_target or visual_issue or formal_stage)
        should_capture = bool(capture_requested) if capture_requested is not None else bool(required or focus_kind != "none")
        reason = (
            "local_repair_focus_required"
            if local_target
            else "formal_or_visual_review_required"
            if required
            else "task_scoped_focus_available"
            if should_capture
            else "not_required"
        )

    recommended_call: dict[str, object] = {
        "capture": "prepare_autocad_for_capture" if should_capture else "not_required",
        "preserve_layout": True,
        "capture_mode": "autocad_window_printwindow",
        "focusSource": focus_source,
    }
    if focus_kind == "handles":
        recommended_call["target_handles"] = _normalize_handles(target.get("handles"))
    if focus_kind == "bbox":
        bbox = _normalize_bbox(target.get("bbox"))
        if bbox:
            recommended_call["target_bbox"] = bbox
    if isinstance(execution_summary, Path):
        recommended_call["execution_summary"] = str(execution_summary)
    if repair_plan is not None:
        recommended_call["repair_plan"] = str(repair_plan) if isinstance(repair_plan, Path) else "inline"

    return {
        "schemaVersion": 1,
        "taskKind": task_kind,
        "evidenceStage": evidence_stage,
        "agentRole": agent_role,
        "shouldCapture": should_capture,
        "required": required,
        "reason": reason,
        "focusSource": focus_source,
        "focusKind": focus_kind,
        "visualAidOnly": True,
        "allowedFallbacks": ["execution_summary.created_handles", "execution_summary.target_bbox", "explicit_bbox"],
        "recommendedCall": recommended_call,
    }


def _normalize_focus_result(result: dict[str, object], *, target: dict[str, object]) -> dict[str, object]:
    normalized = dict(result)
    source = str(target.get("source", "unknown"))
    normalized["source"] = source
    if target.get("kind") == "handles":
        handles = _normalize_handles(target.get("handles"))
        normalized["handles"] = handles
        normalized["handle_count"] = len(handles)
    elif target.get("kind") == "bbox":
        bbox = _normalize_bbox(target.get("bbox"))
        if bbox:
            normalized["target_bbox"] = bbox
    if normalized.get("status") == "zoom_extents":
        normalized["status"] = "focus_target_unavailable"
        normalized["full_extents_fallback_blocked"] = True
    return normalized


def focus_autocad_view(
    *,
    execution_summary: Path | None = None,
    target_handles: list[str] | None = None,
    target_bbox: dict[str, list[float]] | list[float] | None = None,
    repair_plan: dict[str, object] | Path | None = None,
    layer: str | None = None,
    padding_ratio: float = 0.12,
    driver_factory: Callable[[], Any] | None = None,
) -> dict[str, object]:
    """Zoom AutoCAD to the most precise task-scoped focus target available."""

    target = _focus_target(
        execution_summary=execution_summary,
        target_handles=target_handles,
        target_bbox=target_bbox,
        repair_plan=repair_plan,
    )
    if target.get("kind") == "none":
        return {"status": "not_run", "reason": "no task-scoped focus target", "source": "none"}

    if driver_factory is None:
        from core.cad_io.autocad_com import AutoCADComDriver

        driver_factory = lambda: AutoCADComDriver(connect_existing_only=True)
    driver = driver_factory()
    if target.get("kind") == "bbox":
        if not hasattr(driver, "zoom_to_bbox"):
            return {"status": "focus_target_unavailable", "reason": "driver does not support zoom_to_bbox", "source": target["source"]}
        result = driver.zoom_to_bbox(target["bbox"], padding_ratio=padding_ratio)
        return _normalize_focus_result(result, target=target)

    handles = _normalize_handles(target.get("handles"))
    if not handles:
        return {"status": "focus_target_unavailable", "reason": "empty handle target", "source": target["source"]}
    if hasattr(driver, "zoom_to_handles_extents"):
        result = driver.zoom_to_handles_extents(handles=handles, padding_ratio=padding_ratio)
    elif hasattr(driver, "zoom_to_handles"):
        result = driver.zoom_to_handles(handles=handles, layer=layer, padding_ratio=padding_ratio)
    else:
        return {"status": "focus_target_unavailable", "reason": "driver does not support handle focus", "source": target["source"]}
    return _normalize_focus_result(result, target=target)


def focus_autocad_view_from_execution_summary(
    execution_summary: Path,
    *,
    layer: str | None = None,
    padding_ratio: float = 0.12,
    driver_factory: Callable[[], Any] | None = None,
) -> dict[str, object]:
    """Zoom AutoCAD to handles listed in an execution summary (reference + preview allowed)."""

    return focus_autocad_view(
        execution_summary=execution_summary,
        layer=layer,
        padding_ratio=padding_ratio,
        driver_factory=driver_factory,
    )


def visual_preview_payload(capture_result: dict[str, object]) -> dict[str, object]:
    decision = capture_result.get("screenshotDecision")
    if not isinstance(decision, dict):
        focus = capture_result.get("focus")
        focus_source = str(focus.get("source", "none")) if isinstance(focus, dict) else "none"
        decision = {
            "schemaVersion": 1,
            "shouldCapture": str(capture_result.get("status", "not_run")) == "captured",
            "required": False,
            "focusSource": focus_source,
            "focusKind": "unknown" if focus_source != "none" else "none",
            "visualAidOnly": True,
            "reason": "derived_from_capture_result",
        }
    return {
        "status": str(capture_result.get("status", "not_run")),
        "role": VISUAL_AID_ONLY,
        "output": str(capture_result.get("output", "")),
        "mode": str(capture_result.get("mode", "")),
        "occlusion_safe": bool(capture_result.get("occlusion_safe", False)),
        "foreground_first": bool(capture_result.get("foreground_first", False)),
        "foreground_fallback": bool(capture_result.get("foreground_fallback", False)),
        "focus": capture_result.get("focus", {"status": "not_run"}),
        "screenshotDecision": decision,
    }


def prepare_autocad_for_capture(
    output: Path,
    *,
    execution_summary: Path | None = None,
    target_handles: list[str] | None = None,
    target_bbox: dict[str, list[float]] | list[float] | None = None,
    repair_plan: dict[str, object] | Path | None = None,
    layer: str | None = None,
    padding_ratio: float = 0.12,
    autocad_window_finder: Callable[[], dict[str, object] | None] | None = None,
    driver_factory: Callable[[], Any] | None = None,
    preserve_layout: bool = True,
) -> dict[str, object]:
    """Re-frame CAD view and capture client area.

    Default ``preserve_layout=True``: keep user's CAD/IDE split; only restore if minimized,
    zoom via COM, capture with PrintWindow (no SetForegroundWindow). If PrintWindow fails,
    fall back to bringing AutoCAD to foreground once.
    """

    if preserve_layout:
        window = ensure_autocad_visible(autocad_window_finder=autocad_window_finder)
    else:
        window = bring_autocad_to_foreground(autocad_window_finder=autocad_window_finder)
    screenshot_decision = build_screenshot_decision(
        task_kind="capture",
        execution_summary=execution_summary,
        target_handles=target_handles,
        target_bbox=target_bbox,
        repair_plan=repair_plan,
        capture_requested=True,
    )
    focus: dict[str, object] = {"status": "not_run", "reason": "no task-scoped focus target"}
    if execution_summary is not None or target_handles or target_bbox is not None or repair_plan is not None:
        focus = focus_autocad_view(
            execution_summary=execution_summary,
            target_handles=target_handles,
            target_bbox=target_bbox,
            repair_plan=repair_plan,
            layer=layer,
            padding_ratio=padding_ratio,
            driver_factory=driver_factory,
        )
        sleep(0.25)
    try:
        capture = capture_autocad_window(
            output,
            autocad_window_finder=lambda: window,
            foreground_first=False,
            settle_seconds=0.15,
        )
    except Exception as exc:
        if not preserve_layout:
            raise
        window = bring_autocad_to_foreground(autocad_window_finder=autocad_window_finder)
        capture = capture_autocad_window(
            output,
            autocad_window_finder=lambda: window,
            foreground_first=False,
            settle_seconds=0.15,
        )
        capture["foreground_fallback"] = True
        capture["foreground_fallback_reason"] = str(exc)
    capture["window"] = {"hwnd": window.get("hwnd"), "title": window.get("title", "")}
    capture["focus"] = focus
    screenshot_decision["focusStatus"] = str(focus.get("status", "not_run"))
    capture["screenshotDecision"] = screenshot_decision
    capture["prepared"] = True
    capture["preserve_layout"] = preserve_layout
    capture["visualPreview"] = visual_preview_payload(capture)
    return capture


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a CAD preview.")
    parser.add_argument("--output", type=Path, default=Path("output/previews/preview.png"))
    parser.add_argument("--check", action="store_true", help="Report screenshot capability without capturing.")
    parser.add_argument("--capture-screen", action="store_true", help="Capture the visible screen to --output.")
    parser.add_argument("--capture-autocad-window", action="store_true", help="Capture the visible AutoCAD client area to --output.")
    parser.add_argument("--execution-summary", type=Path, help="Optional execute_plan summary used to focus CAD view before capture.")
    parser.add_argument("--target-handle", action="append", dest="target_handle", help="Task-local handle to focus. Repeat for multiple handles.")
    parser.add_argument("--target-handles", dest="target_handles_csv", help="Comma-separated task-local handles to focus.")
    parser.add_argument("--bbox", nargs=4, type=float, dest="target_bbox", metavar=("MIN_X", "MIN_Y", "MAX_X", "MAX_Y"))
    parser.add_argument("--repair-plan", type=Path, help="Optional repair plan JSON with target_handles or target_bbox.")
    parser.add_argument("--layer", default=None, help="Optional layer filter when focusing (default: all handles in summary).")
    parser.add_argument(
        "--padding-ratio",
        type=float,
        default=0.12,
        help="Padding around ZoomWindow when focusing from --execution-summary.",
    )
    parser.add_argument(
        "--no-foreground",
        action="store_true",
        help="Alias for default preserve-layout capture (no SetForegroundWindow).",
    )
    parser.add_argument(
        "--force-foreground",
        action="store_true",
        help="Bring AutoCAD to desktop foreground before capture (use only if PrintWindow fails or CAD is fully occluded).",
    )
    parser.add_argument("--fallback-screen", action="store_true", help="Use full-screen capture if AutoCAD window capture fails.")
    args = parser.parse_args()
    desktop_switch = switch_to_input_desktop()

    if args.check:
        capabilities = get_preview_capabilities(args.output)
        capabilities["desktopSwitch"] = desktop_switch
        print(json.dumps(capabilities, ensure_ascii=False, indent=2))
        return 0

    if args.capture_screen:
        print(json.dumps(capture_screen(args.output), ensure_ascii=False, indent=2))
        return 0

    if args.capture_autocad_window:
        preserve_layout = not args.force_foreground
        focus_result: dict[str, object] | None = None
        try:
            target_handles = list(args.target_handle or [])
            if args.target_handles_csv:
                target_handles.extend(handle.strip() for handle in args.target_handles_csv.split(",") if handle.strip())
            if args.execution_summary or target_handles or args.target_bbox or args.repair_plan:
                result = prepare_autocad_for_capture(
                    args.output,
                    execution_summary=args.execution_summary,
                    target_handles=target_handles or None,
                    target_bbox=args.target_bbox,
                    repair_plan=args.repair_plan,
                    layer=args.layer,
                    padding_ratio=args.padding_ratio,
                    preserve_layout=preserve_layout,
                )
                focus_result = result.get("focus") if isinstance(result.get("focus"), dict) else None
            elif preserve_layout or args.no_foreground:
                ensure_autocad_visible()
                result = capture_autocad_window(args.output, foreground_first=False)
            else:
                bring_autocad_to_foreground()
                result = capture_autocad_window(args.output, foreground_first=False)
            if focus_result is not None and "focus" not in result:
                result["focus"] = focus_result
            result["desktopSwitch"] = desktop_switch
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        except Exception as exc:
            if args.fallback_screen:
                result = capture_screen(args.output)
                result["mode"] = "screen_fallback"
                result["warning"] = f"AutoCAD window capture failed: {exc}"
                if focus_result is not None:
                    result["focus"] = focus_result
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return 0
            print(
                json.dumps(
                    {
                        "status": "failed",
                        "failure_category": "screenshot_failed",
                        "mode": "autocad_window",
                        "output": str(args.output),
                        "message": str(exc),
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 1

    capabilities: dict[str, Any] = get_preview_capabilities(args.output)
    print("render_preview.py")
    print(f"- output: {args.output}")
    print(f"- status: {capabilities['status']}")
    print("- next: use --capture-autocad-window after drawing to save a visual checkpoint.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
