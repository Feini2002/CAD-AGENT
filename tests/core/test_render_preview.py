from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch


from tests.bootstrap import PROJECT_ROOT



from core.verification.render_preview import (
    bring_autocad_to_foreground,
    capture_autocad_window,
    capture_screen,
    ensure_autocad_visible,
    get_preview_capabilities,
    prepare_autocad_for_capture,
)
from tests.helpers import artifact_path


class FakeImage:
    def save(self, path: Path) -> None:
        path.write_bytes(b"fake preview image")


class RecordingGrabber:
    def __init__(self) -> None:
        self.bbox: tuple[int, int, int, int] | None = None

    def __call__(self, *, bbox: tuple[int, int, int, int] | None = None) -> FakeImage:
        self.bbox = bbox
        return FakeImage()


class RenderPreviewTests(unittest.TestCase):
    def test_reports_screenshot_capabilities_without_capturing(self) -> None:
        output = artifact_path("render_preview", "capabilities.png")

        capabilities = get_preview_capabilities(output)

        self.assertEqual(capabilities["output"], str(output))
        self.assertTrue(capabilities["output_dir_exists"])
        self.assertIn("pillow_imagegrab", capabilities["dependencies"])
        self.assertIn("win32gui", capabilities["dependencies"])
        if capabilities["dependencies"]["pillow_imagegrab"]:
            self.assertIn("screen", capabilities["capture_modes"])
        else:
            self.assertNotIn("screen", capabilities["capture_modes"])
            self.assertEqual(capabilities["status"], "unavailable")

    def test_check_does_not_report_autocad_window_ready_without_window(self) -> None:
        output = artifact_path("render_preview", "no_window.png")

        capabilities = get_preview_capabilities(
            output,
            module_checker=lambda name: True,
            autocad_window_finder=lambda: None,
        )

        self.assertIn("screen", capabilities["capture_modes"])
        self.assertNotIn("autocad_window", capabilities["capture_modes"])
        self.assertEqual(capabilities["autocad_window"]["status"], "unavailable")

    def test_check_reports_autocad_window_mode_when_window_is_found(self) -> None:
        output = artifact_path("render_preview", "window_ready.png")

        capabilities = get_preview_capabilities(
            output,
            module_checker=lambda name: True,
            autocad_window_finder=lambda: {
                "hwnd": 42,
                "title": "Autodesk AutoCAD 2026 - [Drawing1.dwg]",
                "bbox": [10, 20, 1010, 820],
            },
        )

        self.assertIn("autocad_window", capabilities["capture_modes"])
        self.assertEqual(capabilities["autocad_window"]["status"], "ready")
        self.assertEqual(capabilities["autocad_window"]["title"], "Autodesk AutoCAD 2026 - [Drawing1.dwg]")

    def test_capture_screen_writes_output_with_injected_grabber(self) -> None:
        output = artifact_path("render_preview", "nested", "preview.png")

        result = capture_screen(output, grabber=lambda: FakeImage())

        self.assertEqual(result["status"], "captured")
        self.assertEqual(result["output"], str(output))
        self.assertTrue(output.exists())

    def test_capture_autocad_window_uses_client_bbox(self) -> None:
        output = artifact_path("render_preview", "window", "preview.png")
        grabber = RecordingGrabber()

        result = capture_autocad_window(
            output,
            autocad_window_finder=lambda: {
                "hwnd": 42,
                "title": "Autodesk AutoCAD 2026 - [Drawing1.dwg]",
                "bbox": [10, 20, 1010, 820],
            },
            grabber=grabber,
            foreground_first=False,
            use_screen_grab=True,
        )

        self.assertEqual(result["status"], "captured")
        self.assertEqual(result["mode"], "autocad_window_screen_grab")
        self.assertEqual(result["window_title"], "Autodesk AutoCAD 2026 - [Drawing1.dwg]")
        self.assertEqual(grabber.bbox, (10, 20, 1010, 820))
        self.assertTrue(output.exists())

    @patch("core.verification.render_preview.capture_autocad_window")
    def test_prepare_autocad_for_capture_preserve_layout_zoom_then_capture(self, mock_capture: Any) -> None:
        output = artifact_path("render_preview", "prepared", "preview.png")
        focus_calls: list[str] = []

        class FakeDriver:
            def zoom_to_handles_extents(self, *, handles: list[str], padding_ratio: float = 0.12) -> dict[str, object]:
                focus_calls.append(",".join(handles))
                return {"status": "zoomed_to_bbox", "handle_count": len(handles), "method": "com_geometric_extents"}

        mock_capture.return_value = {
            "status": "captured",
            "output": str(output),
            "mode": "autocad_window_printwindow",
        }

        summary = artifact_path("render_preview", "prepared", "execution_summary.json")
        summary.write_text('{"created_handles":["REF","P1"]}', encoding="utf-8")

        prepared = prepare_autocad_for_capture(
            output,
            execution_summary=summary,
            autocad_window_finder=lambda: {
                "hwnd": 99,
                "title": "Autodesk AutoCAD 2026 - [Drawing1.dwg]",
                "bbox": [10, 20, 1010, 820],
            },
            driver_factory=lambda: FakeDriver(),
            preserve_layout=True,
        )
        self.assertEqual(prepared["status"], "captured")
        self.assertTrue(prepared.get("prepared"))
        self.assertTrue(prepared.get("preserve_layout"))
        self.assertEqual(focus_calls, ["REF,P1"])
        mock_capture.assert_called_once()
        self.assertIs(mock_capture.call_args.kwargs.get("foreground_first"), False)

    def test_ensure_autocad_visible_uses_injected_window_without_foreground(self) -> None:
        target = ensure_autocad_visible(
            autocad_window_finder=lambda: {
                "hwnd": 7,
                "title": "Autodesk AutoCAD 2026 - [Drawing2.dwg]",
                "bbox": [0, 0, 800, 600],
            },
            settle_seconds=0.0,
        )
        self.assertEqual(target["hwnd"], 7)

    def test_bring_autocad_to_foreground_uses_injected_window(self) -> None:
        target = bring_autocad_to_foreground(
            autocad_window_finder=lambda: {
                "hwnd": 7,
                "title": "Autodesk AutoCAD 2026 - [Drawing2.dwg]",
                "bbox": [0, 0, 800, 600],
            },
            settle_seconds=0.0,
        )
        self.assertEqual(target["hwnd"], 7)

    def test_capture_autocad_window_reports_missing_window(self) -> None:
        output = artifact_path("render_preview", "window", "missing.png")

        with self.assertRaisesRegex(RuntimeError, "AutoCAD window"):
            capture_autocad_window(
                output,
                autocad_window_finder=lambda: None,
                grabber=lambda **_: FakeImage(),
            )


if __name__ == "__main__":
    unittest.main()
