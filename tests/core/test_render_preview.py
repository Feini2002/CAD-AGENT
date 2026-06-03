from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch


from tests.bootstrap import PROJECT_ROOT



from core.verification.render_preview import (
    build_screenshot_decision,
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
    def test_screenshot_decision_requires_local_repair_focus(self) -> None:
        decision = build_screenshot_decision(
            task_kind="local_repair",
            repair_plan={"target_handles": ["FIX1"], "target_bbox": {"min": [0, 0], "max": [10, 10]}},
            execution_summary={"created_handles": ["BATCH1", "BATCH2"]},
            agent_role="pipeline_repair",
        )

        self.assertTrue(decision["shouldCapture"])
        self.assertTrue(decision["required"])
        self.assertTrue(decision["visualAidOnly"])
        self.assertEqual(decision["focusSource"], "repair_plan.target_handles")
        self.assertEqual(decision["recommendedCall"]["target_handles"], ["FIX1"])
        self.assertNotIn("whole_modelspace", decision["allowedFallbacks"])

    def test_screenshot_decision_allows_quick_trial_skip_when_readback_is_enough(self) -> None:
        decision = build_screenshot_decision(
            task_kind="quick_trial",
            key_readback_passed=True,
            visual_issue=False,
            formal_acceptance=False,
        )

        self.assertFalse(decision["shouldCapture"])
        self.assertFalse(decision["required"])
        self.assertEqual(decision["reason"], "quick_trial_key_readback_enough")
        self.assertTrue(decision["visualAidOnly"])

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

    @patch("core.verification.render_preview.capture_autocad_window")
    def test_prepare_prefers_local_target_handles_over_whole_execution_summary(self, mock_capture: Any) -> None:
        output = artifact_path("render_preview", "local_target", "preview.png")
        focus_calls: list[list[str]] = []

        class FakeDriver:
            def zoom_to_handles_extents(self, *, handles: list[str], padding_ratio: float = 0.12) -> dict[str, object]:
                focus_calls.append(list(handles))
                return {"status": "zoomed_to_bbox", "handle_count": len(handles), "method": "com_geometric_extents"}

        mock_capture.return_value = {
            "status": "captured",
            "output": str(output),
            "mode": "autocad_window_printwindow",
        }
        summary = artifact_path("render_preview", "local_target", "execution_summary.json")
        summary.write_text('{"created_handles":["BATCH1","BATCH2","BATCH3"]}', encoding="utf-8")

        prepared = prepare_autocad_for_capture(
            output,
            execution_summary=summary,
            target_handles=["FIXED1"],
            autocad_window_finder=lambda: {
                "hwnd": 99,
                "title": "Autodesk AutoCAD 2026 - [Drawing1.dwg]",
                "bbox": [10, 20, 1010, 820],
            },
            driver_factory=lambda: FakeDriver(),
        )

        self.assertEqual(focus_calls, [["FIXED1"]])
        self.assertEqual(prepared["focus"]["source"], "target_handles")
        self.assertEqual(prepared["focus"]["handle_count"], 1)

    @patch("core.verification.render_preview.capture_autocad_window")
    def test_prepare_uses_repair_plan_bbox_when_local_handles_are_missing(self, mock_capture: Any) -> None:
        output = artifact_path("render_preview", "repair_bbox", "preview.png")
        zoomed_bboxes: list[dict[str, list[float]]] = []

        class FakeDriver:
            def zoom_to_bbox(self, bbox: dict[str, list[float]], *, padding_ratio: float = 0.12) -> dict[str, object]:
                zoomed_bboxes.append(bbox)
                return {"status": "zoomed_to_bbox", "bbox": bbox}

        mock_capture.return_value = {
            "status": "captured",
            "output": str(output),
            "mode": "autocad_window_printwindow",
        }

        prepared = prepare_autocad_for_capture(
            output,
            repair_plan={"target_bbox": {"min": [100.0, 200.0], "max": [300.0, 450.0]}},
            autocad_window_finder=lambda: {
                "hwnd": 99,
                "title": "Autodesk AutoCAD 2026 - [Drawing1.dwg]",
                "bbox": [10, 20, 1010, 820],
            },
            driver_factory=lambda: FakeDriver(),
        )

        self.assertEqual(zoomed_bboxes, [{"min": [100.0, 200.0], "max": [300.0, 450.0]}])
        self.assertEqual(prepared["focus"]["source"], "repair_plan.target_bbox")
        self.assertEqual(prepared["focus"]["target_bbox"], {"min": [100.0, 200.0], "max": [300.0, 450.0]})

    @patch("core.verification.render_preview.capture_autocad_window")
    def test_prepare_forwards_layer_to_handle_focus_when_extents_api_is_absent(self, mock_capture: Any) -> None:
        output = artifact_path("render_preview", "layer_forwarding", "preview.png")
        layer_calls: list[str | None] = []

        class FakeDriver:
            def zoom_to_handles(
                self,
                *,
                handles: list[str],
                layer: str | None = None,
                padding_ratio: float = 0.12,
            ) -> dict[str, object]:
                layer_calls.append(layer)
                return {"status": "zoomed_to_handles", "handle_count": len(handles)}

        mock_capture.return_value = {
            "status": "captured",
            "output": str(output),
            "mode": "autocad_window_printwindow",
        }
        summary = artifact_path("render_preview", "layer_forwarding", "execution_summary.json")
        summary.write_text('{"created_handles":["H1"]}', encoding="utf-8")

        prepared = prepare_autocad_for_capture(
            output,
            execution_summary=summary,
            layer="CODEX_PREVIEW",
            autocad_window_finder=lambda: {
                "hwnd": 99,
                "title": "Autodesk AutoCAD 2026 - [Drawing1.dwg]",
                "bbox": [10, 20, 1010, 820],
            },
            driver_factory=lambda: FakeDriver(),
        )

        self.assertEqual(layer_calls, ["CODEX_PREVIEW"])
        self.assertEqual(prepared["focus"]["source"], "execution_summary.created_handles")

    @patch("core.verification.render_preview.capture_autocad_window")
    def test_prepare_reports_focus_target_unavailable_instead_of_zoom_extents(self, mock_capture: Any) -> None:
        output = artifact_path("render_preview", "no_zoom_extents", "preview.png")

        class FakeDriver:
            def zoom_to_handles_extents(self, *, handles: list[str], padding_ratio: float = 0.12) -> dict[str, object]:
                return {
                    "status": "zoom_extents",
                    "reason": "handle extents unavailable",
                    "handle_count": len(handles),
                    "resolved_count": 0,
                }

        mock_capture.return_value = {
            "status": "captured",
            "output": str(output),
            "mode": "autocad_window_printwindow",
        }
        summary = artifact_path("render_preview", "no_zoom_extents", "execution_summary.json")
        summary.write_text('{"created_handles":["MISSING"]}', encoding="utf-8")

        prepared = prepare_autocad_for_capture(
            output,
            execution_summary=summary,
            autocad_window_finder=lambda: {
                "hwnd": 99,
                "title": "Autodesk AutoCAD 2026 - [Drawing1.dwg]",
                "bbox": [10, 20, 1010, 820],
            },
            driver_factory=lambda: FakeDriver(),
        )

        self.assertEqual(prepared["focus"]["status"], "focus_target_unavailable")
        self.assertEqual(prepared["focus"]["source"], "execution_summary.created_handles")

    @patch("core.verification.render_preview.capture_autocad_window")
    def test_prepare_includes_screenshot_decision_payload(self, mock_capture: Any) -> None:
        output = artifact_path("render_preview", "decision_payload", "preview.png")

        class FakeDriver:
            def zoom_to_handles_extents(self, *, handles: list[str], padding_ratio: float = 0.12) -> dict[str, object]:
                return {"status": "zoomed_to_bbox", "handle_count": len(handles), "method": "com_geometric_extents"}

        mock_capture.return_value = {
            "status": "captured",
            "output": str(output),
            "mode": "autocad_window_printwindow",
            "occlusion_safe": True,
        }

        prepared = prepare_autocad_for_capture(
            output,
            target_handles=["LOCAL1"],
            autocad_window_finder=lambda: {
                "hwnd": 99,
                "title": "Autodesk AutoCAD 2026 - [Drawing1.dwg]",
                "bbox": [10, 20, 1010, 820],
            },
            driver_factory=lambda: FakeDriver(),
        )

        self.assertEqual(prepared["screenshotDecision"]["focusSource"], "target_handles")
        self.assertTrue(prepared["screenshotDecision"]["shouldCapture"])
        self.assertTrue(prepared["visualPreview"]["screenshotDecision"]["visualAidOnly"])

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
