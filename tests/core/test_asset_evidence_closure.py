from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import temporary_artifact_dir


def _write(path: Path, text: str = "{}") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _active_refs(value: object) -> list[str]:
    refs: list[str] = []
    list_keys = {"evidenceRefs", "refs"}
    detail_keys = {"summary", "report", "screenshot", "focusedScreenshot", "reportPath", "screenshotPath", "preview", "previewPath"}

    def looks_like_ref(item: object) -> bool:
        return isinstance(item, str) and item.startswith(("output/", "docs/", "agents/", "libraries/", "projects/"))

    def walk(item: object) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                if key in list_keys and isinstance(child, list):
                    refs.extend(str(ref) for ref in child if looks_like_ref(ref))
                if key in detail_keys and looks_like_ref(child):
                    refs.append(str(child))
                if isinstance(child, (dict, list)):
                    walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)

    walk(value)
    return refs


class AssetEvidenceClosureTests(unittest.TestCase):
    def test_missing_refs_are_archived_and_current_refs_remain_active(self) -> None:
        from core.assets.asset_evidence_closure import close_missing_asset_evidence_refs

        with temporary_artifact_dir("asset_evidence_closure") as root:
            _write(root / "docs/existing.md", "kept")
            _write(root / "output/current/current-shelf-report.json", '{"status":"pass"}')
            _write(root / "output/current/current-preview.png", "png")
            package_path = root / "libraries/system_library/drawing_standards/basic/assets.json"
            package = {
                "assets": [
                    {
                        "assetId": "interior_dimension_style_visual_standard",
                        "evidenceRefs": [
                            "output/missing-old-report.json",
                            "docs/existing.md",
                        ],
                        "native": {
                            "layoutPlan": {
                                "evidenceLinks": {
                                    "refs": ["output/missing-old-preview.png"]
                                }
                            },
                            "nativeVisiblePanelEvidence": {
                                "status": "pass",
                                "createdHandleCount": 12,
                                "report": "output/missing-old-report.json",
                                "screenshot": "output/missing-old-preview.png",
                            },
                        },
                    }
                ]
            }
            _write(package_path, json.dumps(package, ensure_ascii=False))

            report = close_missing_asset_evidence_refs(
                project_root=root,
                json_paths=[package_path],
                closure_report_path=root / "output/current/evidence-closure.json",
                report_ref="output/current/current-shelf-report.json",
                visual_ref="output/current/current-preview.png",
                extra_active_refs=[],
                reason="supersede missing historical output with current shelf evidence",
            )

            updated = json.loads(package_path.read_text(encoding="utf-8"))
            refs = _active_refs(updated)
            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["missingRefCount"], 2)
            self.assertNotIn("output/missing-old-report.json", refs)
            self.assertNotIn("output/missing-old-preview.png", refs)
            self.assertIn("docs/existing.md", refs)
            self.assertIn("output/current/current-shelf-report.json", refs)
            self.assertIn("output/current/current-preview.png", refs)
            self.assertTrue((root / "output/current/evidence-closure.json").is_file())
            closure = updated["assets"][0]["evidenceClosure"]
            self.assertEqual(closure["status"], "closed")
            self.assertEqual(len(closure["archivedMissingRefs"]), 2)


if __name__ == "__main__":
    unittest.main()
