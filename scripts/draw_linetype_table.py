#!/usr/bin/env python3
"""Draw the Chinese linetype summary table through the reusable UTF-8 demo path."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path
except ModuleNotFoundError:  # Imported as scripts.draw_linetype_table.
    from scripts._bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.training.linetype_table_demo import draw_linetype_table  # noqa: E402
from core.training.streaming_demo import SleepFn, StreamingCadDemoConfig  # noqa: E402

DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output" / "validation_runs" / "linetype-table"


def _driver(fake_cad: bool) -> Any:
    if fake_cad:
        from core.verification.fake_cad_driver import FakeCadDriver

        return FakeCadDriver()
    from core.cad_io.autocad_com import AutoCADComDriver

    return AutoCADComDriver(connect_existing_only=True)


def run_linetype_table_demo(
    *,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    fake_cad: bool = False,
    stream_demo: bool = True,
    stream_item_delay_seconds: float = 0.12,
    stream_operation_delay_seconds: float = 0.05,
    stream_operation_budget: int = 2,
    stream_zoom_each_item: bool = True,
    capture_preview: bool = False,
    sleep_fn: SleepFn | None = None,
) -> dict[str, Any]:
    streaming_config = (
        StreamingCadDemoConfig.hybrid(
            item_delay_seconds=stream_item_delay_seconds,
            operation_delay_seconds=stream_operation_delay_seconds,
            operation_budget_per_item=stream_operation_budget,
            zoom_each_item=stream_zoom_each_item,
        )
        if stream_demo
        else StreamingCadDemoConfig.disabled()
    )
    report = draw_linetype_table(
        driver=_driver(fake_cad),
        output_dir=Path(output_dir),
        streaming_config=streaming_config,
        sleep_fn=sleep_fn,
    )
    report["capturePreview"] = {
        "status": "not_requested" if not capture_preview else "deferred",
        "reason": "This entry draws and readbacks the table; screenshots remain an explicit render_preview step.",
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Draw the Chinese linetype summary table in CODEX_PREVIEW.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--fake-cad", action="store_true", help="Use the in-memory fake CAD driver.")
    parser.add_argument("--no-stream-demo", action="store_true", help="Disable row-by-row streaming demo pacing.")
    parser.add_argument("--stream-item-delay", type=float, default=0.12)
    parser.add_argument("--stream-operation-delay", type=float, default=0.05)
    parser.add_argument("--stream-operation-budget", type=int, default=2)
    parser.add_argument("--stream-no-zoom", action="store_true", help="Disable per-row zoom events while streaming.")
    parser.add_argument("--capture-preview", action="store_true", help="Record screenshot request metadata only.")
    args = parser.parse_args()

    report = run_linetype_table_demo(
        output_dir=args.output_dir,
        fake_cad=args.fake_cad,
        stream_demo=not args.no_stream_demo,
        stream_item_delay_seconds=args.stream_item_delay,
        stream_operation_delay_seconds=args.stream_operation_delay,
        stream_operation_budget=args.stream_operation_budget,
        stream_zoom_each_item=not args.stream_no_zoom,
        capture_preview=args.capture_preview,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if report.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
