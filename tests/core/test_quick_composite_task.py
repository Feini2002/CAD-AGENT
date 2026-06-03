from __future__ import annotations

import unittest

from core.quick_tasks.find_and_annotate import run_find_and_annotate_bbox_dimensions
from core.verification.fake_cad_driver import FakeCadDriver
from core.visual_retrieval.current_dwg_cache import build_block_cache_manifest


def _block(handle: str, name: str, layer: str, bbox: dict[str, list[float]]) -> dict[str, object]:
    return {
        "handle": handle,
        "type": "block_reference",
        "block_name": name,
        "layer": layer,
        "bbox": bbox,
    }


class SnapshotCountingDriver(FakeCadDriver):
    def __init__(self) -> None:
        super().__init__()
        self.snapshot_calls = 0

    def snapshot_modelspace(self, *, layer: str | None = None) -> list[dict[str, object]]:
        self.snapshot_calls += 1
        return super().snapshot_modelspace(layer=layer)


class FakeBlockReference:
    Handle = "B1"
    ObjectName = "AcDbBlockReference"
    Layer = "source"
    block_name = "TABLE_BLOCK"

    def GetBoundingBox(self) -> tuple[list[float], list[float]]:
        return [0, 0, 0], [1600, 800, 0]


class QuickCompositeTaskTests(unittest.TestCase):
    def test_uses_valid_cache_to_annotate_generic_block_without_live_snapshot(self) -> None:
        driver = SnapshotCountingDriver()
        manifest = build_block_cache_manifest(
            entities=[
                _block("B1", "BED_QUEEN", "source", {"min": [0, 0], "max": [2000, 1700]}),
            ],
            document={"name": "sample-active.dwg", "full_name": r"C:\sample-active.dwg"},
            source="test_cache",
        )

        report = run_find_and_annotate_bbox_dimensions(
            driver,
            query="找到床并标注尺寸",
            visual_hint="bed plan view wide furniture",
            cache_manifest=manifest,
        )

        self.assertEqual(report["status"], "pass")
        self.assertEqual(driver.snapshot_calls, 0)
        self.assertEqual(report["candidate_source"], "cache")
        self.assertEqual(report["target"]["block_name"], "BED_QUEEN")
        self.assertEqual(report["execution"]["created_handle_count"], 2)
        self.assertEqual([item["text"] for item in report["execution"]["readback_entities"]], ["2000", "1700"])
        self.assertFalse(report["execution"]["safety"]["modified_target_block"])

    def test_falls_back_to_live_snapshot_when_cache_document_mismatches(self) -> None:
        driver = SnapshotCountingDriver()
        driver.entities["B1"] = FakeBlockReference()
        manifest = build_block_cache_manifest(
            entities=[_block("OLD", "OLD_BLOCK", "source", {"min": [0, 0], "max": [300, 300]})],
            document={"name": "old.dwg", "full_name": r"C:\old.dwg"},
            source="stale_cache",
        )

        report = run_find_and_annotate_bbox_dimensions(
            driver,
            query="find table and annotate dimensions",
            visual_hint="table plan view furniture",
            cache_manifest=manifest,
        )

        self.assertEqual(report["status"], "pass")
        self.assertEqual(driver.snapshot_calls, 1)
        self.assertEqual(report["candidate_source"], "live_snapshot")
        self.assertEqual(report["target"]["block_name"], "TABLE_BLOCK")


if __name__ == "__main__":
    unittest.main()
