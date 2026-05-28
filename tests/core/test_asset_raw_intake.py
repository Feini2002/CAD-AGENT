from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from core.assets import build_raw_reference_intake, write_raw_reference_intake
from core.schemas.validator import validate_value
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import ARTIFACT_ROOT


class AssetRawIntakeTests(unittest.TestCase):
    def _project_root(self) -> tempfile.TemporaryDirectory[str]:
        ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
        return tempfile.TemporaryDirectory(dir=ARTIFACT_ROOT)

    def _write_raw_file(self, root: Path, source_slug: str, rel_path: str, content: str = "stub") -> Path:
        path = root / "standard_cad_library_raw" / source_slug / "original" / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_auto_intake_infers_and_writes_reference_only_assets(self) -> None:
        with self._project_root() as temp_root:
            root = Path(temp_root)
            self._write_raw_file(root, "demo-furniture", "plan/sofa_plan.dwg")
            self._write_raw_file(root, "demo-furniture", "plan/sofa_plan.dwl")

            intake = build_raw_reference_intake(
                "demo-furniture",
                project_root=root,
                description="住宅家具图库，包含沙发平面图",
                ingest_date="2026-05-29",
            )

            self.assertEqual(intake["status"], "ready")
            self.assertEqual(intake["file_count"], 1)
            self.assertEqual(intake["skipped_files"], ["plan/sofa_plan.dwl"])
            self.assertEqual(intake["license_status"], "unknown")
            self.assertEqual(intake["usage_boundary"], "reference_only")
            self.assertEqual(intake["privacy_boundary"], "raw")

            asset = intake["assets"][0]
            self.assertIn("sofa", asset["object_tags"])
            self.assertEqual(asset["domain"], "residential")
            self.assertEqual(asset["view_type"], "plan")
            self.assertEqual(asset["source_uri_or_local_ref"], "standard_cad_library_raw/demo-furniture/original/plan/sofa_plan.dwg")
            self.assertEqual(asset["review_status"], "agent_inferred")
            self.assertIn("system_library promotion was not attempted", asset["evidence_boundary"]["not_checked"])

            schema = json.loads((PROJECT_ROOT / "core/schemas/reference_asset.schema.json").read_text(encoding="utf-8"))
            self.assertEqual(validate_value(asset, schema), [])

            written = write_raw_reference_intake(intake, project_root=root)
            self.assertTrue((root / written["raw_source_note"]).is_file())
            self.assertTrue((root / written["reference_source"]).is_file())
            self.assertTrue((root / "libraries/reference_library/manifests/demo-furniture/ref.residential.demo_furniture.0001.json").is_file())
            self.assertFalse((root / "libraries/system_library").exists())

    def test_unknown_metadata_is_allowed_without_blocking_intake(self) -> None:
        with self._project_root() as temp_root:
            root = Path(temp_root)
            self._write_raw_file(root, "misc-pack", "bundle/misc_symbol.pdf")

            intake = build_raw_reference_intake("misc-pack", project_root=root, ingest_date="2026-05-29")
            asset = intake["assets"][0]

            self.assertEqual(intake["status"], "ready")
            self.assertEqual(asset["object_tags"], ["unknown"])
            self.assertEqual(asset["domain"], "generic")
            self.assertEqual(asset["view_type"], "unknown")
            self.assertEqual(asset["part_tags"], [])
            self.assertEqual(asset["usage_boundary"], "reference_only")

    def test_source_slug_rejects_path_traversal(self) -> None:
        with self._project_root() as temp_root:
            with self.assertRaises(ValueError):
                build_raw_reference_intake("../bad", project_root=Path(temp_root))


if __name__ == "__main__":
    unittest.main()
