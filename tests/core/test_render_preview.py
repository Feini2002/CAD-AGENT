from __future__ import annotations

import unittest


from tests.bootstrap import PROJECT_ROOT



from core.verification.render_preview import capture_screen, get_preview_capabilities
from tests.helpers import artifact_path


class FakeImage:
    def save(self, path: Path) -> None:
        path.write_bytes(b"fake preview image")


class RenderPreviewTests(unittest.TestCase):
    def test_reports_screenshot_capabilities_without_capturing(self) -> None:
        output = artifact_path("render_preview", "capabilities.png")

        capabilities = get_preview_capabilities(output)

        self.assertEqual(capabilities["output"], str(output))
        self.assertTrue(capabilities["output_dir_exists"])
        self.assertIn("pillow_imagegrab", capabilities["dependencies"])
        self.assertIn("win32gui", capabilities["dependencies"])
        self.assertIn("screen", capabilities["capture_modes"])

    def test_capture_screen_writes_output_with_injected_grabber(self) -> None:
        output = artifact_path("render_preview", "nested", "preview.png")

        result = capture_screen(output, grabber=lambda: FakeImage())

        self.assertEqual(result["status"], "captured")
        self.assertEqual(result["output"], str(output))
        self.assertTrue(output.exists())


if __name__ == "__main__":
    unittest.main()
