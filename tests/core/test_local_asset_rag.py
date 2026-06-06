from __future__ import annotations

import json
import unittest

from tests.helpers import temporary_artifact_dir


class LocalAssetRagTests(unittest.TestCase):
    def test_small_rag_pack_reads_only_allowed_local_sources(self) -> None:
        from core.assets.local_rag import build_local_asset_rag_pack

        with temporary_artifact_dir("local_asset_rag") as root:
            registry_path = root / "libraries" / "system_library" / "registry.json"
            registry_path.parent.mkdir(parents=True)
            registry_path.write_text(
                json.dumps(
                    {
                        "assets": [
                            {
                                "assetId": "sofa_clean_block",
                                "name": "可复用沙发块",
                                "category": "furniture.seating.sofas",
                                "aliases": ["沙发", "sofa"],
                                "tags": ["靠背", "坐垫"],
                                "useWhen": ["需要复用 clean sofa source"],
                                "assetKind": "object_block",
                                "verificationStatus": "systemized",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            reference_path = root / "libraries" / "reference_library" / "manifests" / "sofa_ref.json"
            reference_path.parent.mkdir(parents=True)
            reference_path.write_text(
                json.dumps({"id": "reference_sofa", "aliases": ["沙发"], "notes": "reference only"}, ensure_ascii=False),
                encoding="utf-8",
            )

            memory_path = root / "agents" / "cad_designer" / "training_memory.json"
            memory_path.parent.mkdir(parents=True)
            memory_path.write_text(
                json.dumps(
                    {
                        "agentId": "cad_designer",
                        "lessons": [
                            {
                                "capabilityId": "sofa-symbol",
                                "summary": "沙发绘制必须区分靠背、坐垫和扶手，不能只画外框。",
                                "promptGuidance": ["沙发对象先拆 visual_parts，再进入 CAD_PLAN。"],
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            failure_path = root / "projects" / "case_sofa" / "runs" / "round1_failure_notes.json"
            failure_path.parent.mkdir(parents=True)
            failure_path.write_text(
                json.dumps(
                    {
                        "case_id": "case_sofa",
                        "verdict": "fail",
                        "root_cause": "沙发靠背与坐垫重叠，复用前没有检查干净来源。",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            pack = build_local_asset_rag_pack("复用沙发时检查靠背和坐垫", project_root=root)

        self.assertEqual(pack["kind"], "local_asset_small_rag_pack")
        self.assertEqual(pack["retrievalMode"], "local_lexical_small_rag")
        self.assertEqual(pack["sourcePolicy"]["allowedSourceKinds"], ["system_asset", "semantic_rule", "training_memory", "failure_sample"])
        self.assertIn("reference_asset", pack["sourcePolicy"]["excludedSourceKinds"])
        self.assertEqual(pack["sourceSummary"]["reference_asset"], 0)

        source_kinds = {item["sourceKind"] for item in pack["items"]}
        self.assertIn("system_asset", source_kinds)
        self.assertIn("semantic_rule", source_kinds)
        self.assertIn("training_memory", source_kinds)
        self.assertIn("failure_sample", source_kinds)
        self.assertNotIn("reference_asset", source_kinds)
        self.assertIn("real_cad_geometry", pack["evidenceBoundary"]["notChecked"])

    def test_small_rag_pack_is_upstream_context_not_capability_proof(self) -> None:
        from core.assets.local_rag import build_local_asset_rag_pack

        with temporary_artifact_dir("local_asset_rag_boundary") as root:
            pack = build_local_asset_rag_pack("随便画一个沙发", project_root=root)

        self.assertEqual(pack["status"], "no_matches")
        self.assertIn("no_embedding_rag", pack["evidenceBoundary"]["assumptions"])
        self.assertIn("local_rag_pack_is_upstream_context_not_capability_proof", pack["evidenceBoundary"]["assumptions"])
        self.assertIn("system_asset_registry", pack["scannedSources"])
        self.assertNotIn("libraries/reference_library", " ".join(pack["scannedSources"]))


if __name__ == "__main__":
    unittest.main()
