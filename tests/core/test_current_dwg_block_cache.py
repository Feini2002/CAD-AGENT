from __future__ import annotations

import unittest
from pathlib import Path

from core.visual_retrieval.current_dwg_cache import (
    build_block_cache_manifest,
    cache_matches_document,
    load_block_cache_manifest,
    write_block_cache_manifest,
)


def _block(handle: str, name: str, layer: str, bbox: dict[str, list[float]]) -> dict[str, object]:
    return {
        "handle": handle,
        "type": "block_reference",
        "block_name": name,
        "layer": layer,
        "bbox": bbox,
    }


class CurrentDwgBlockCacheTests(unittest.TestCase):
    def test_builds_manifest_with_lightweight_block_candidates(self) -> None:
        manifest = build_block_cache_manifest(
            entities=[
                _block("A1", "SOFA_3P", "source", {"min": [0, 0], "max": [2800, 960]}),
                {"handle": "L1", "type": "line", "layer": "source"},
            ],
            document={"name": "Drawing2.dwg", "full_name": r"D:\sample\Drawing2.dwg"},
            source="live_snapshot",
            snapshot_seconds=3.2,
        )

        self.assertEqual(manifest["document"]["name"], "Drawing2.dwg")
        self.assertEqual(manifest["candidate_count"], 1)
        self.assertEqual(manifest["candidates"][0]["handle"], "A1")
        self.assertEqual(manifest["candidates"][0]["block_name"], "SOFA_3P")
        self.assertEqual(manifest["candidates"][0]["size"], [2800.0, 960.0])
        self.assertAlmostEqual(manifest["candidates"][0]["aspect_ratio"], 2.9166666667)
        self.assertEqual(manifest["source"], "live_snapshot")

    def test_writes_loads_and_matches_document_identity(self) -> None:
        manifest = build_block_cache_manifest(
            entities=[_block("A1", "BED_QUEEN", "source", {"min": [10, 20], "max": [2010, 1720]})],
            document={"name": "Drawing2.dwg", "full_name": r"D:\sample\Drawing2.dwg"},
            source="live_snapshot",
        )

        path = Path.cwd() / "output" / "validation_runs" / "test-current-dwg-block-cache.json"
        write_block_cache_manifest(path, manifest)
        loaded = load_block_cache_manifest(path)

        self.assertTrue(cache_matches_document(loaded, {"name": "Drawing2.dwg", "full_name": r"D:\sample\Drawing2.dwg"}))
        self.assertFalse(cache_matches_document(loaded, {"name": "Other.dwg", "full_name": r"D:\sample\Other.dwg"}))


if __name__ == "__main__":
    unittest.main()
