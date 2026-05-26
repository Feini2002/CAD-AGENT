from __future__ import annotations

import unittest
from typing import Any


from tests.bootstrap import PROJECT_ROOT



from core.verification.render_preview import capture_autocad_window, capture_screen, get_preview_capabilities
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
        self.assertIn("screen", capabilities["capture_modes"])

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
        )

        self.assertEqual(result["status"], "captured")
        self.assertEqual(result["mode"], "autocad_window")
        self.assertEqual(result["window_title"], "Autodesk AutoCAD 2026 - [Drawing1.dwg]")
        self.assertEqual(grabber.bbox, (10, 20, 1010, 820))
        self.assertTrue(output.exists())

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
