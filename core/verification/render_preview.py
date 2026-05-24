#!/usr/bin/env python
"""Render or capture a preview after CAD execution."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any, Callable, Protocol


class CapturableImage(Protocol):
    def save(self, path: Path) -> None:
        ...


def module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def get_preview_capabilities(output: Path) -> dict[str, object]:
    """Report screenshot dependencies without touching the screen."""

    dependencies = {
        "pillow_imagegrab": module_available("PIL.ImageGrab"),
        "win32gui": module_available("win32gui"),
    }
    capture_modes: list[str] = []
    if dependencies["pillow_imagegrab"]:
        capture_modes.append("screen")

    return {
        "status": "ready" if capture_modes else "unavailable",
        "output": str(output),
        "output_dir": str(output.parent),
        "output_dir_exists": output.parent.exists(),
        "dependencies": dependencies,
        "capture_modes": capture_modes,
        "note": "CAD-window cropping can be added later; current implemented mode captures the visible screen.",
    }


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a CAD preview.")
    parser.add_argument("--output", type=Path, default=Path("output/previews/preview.png"))
    parser.add_argument("--check", action="store_true", help="Report screenshot capability without capturing.")
    parser.add_argument("--capture-screen", action="store_true", help="Capture the visible screen to --output.")
    args = parser.parse_args()

    if args.check:
        print(json.dumps(get_preview_capabilities(args.output), ensure_ascii=False, indent=2))
        return 0

    if args.capture_screen:
        print(json.dumps(capture_screen(args.output), ensure_ascii=False, indent=2))
        return 0

    capabilities: dict[str, Any] = get_preview_capabilities(args.output)
    print("render_preview.py")
    print(f"- output: {args.output}")
    print(f"- status: {capabilities['status']}")
    print("- next: use --capture-screen after drawing to save a visual checkpoint.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
