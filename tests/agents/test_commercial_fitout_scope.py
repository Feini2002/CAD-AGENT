from __future__ import annotations

import unittest
from pathlib import Path

from core.agents.commercial_fitout_scope import (
    PRIMARY_SUBSCENE_IDS,
    assert_scope_contract,
    load_commercial_fitout_scope,
    validate_commercial_fitout_scope,
)
from core.agents.scene_boundary_scan import scan_agent_tree
from core.schemas.validator import validate_json
from tests.bootstrap import PROJECT_ROOT


class CommercialFitoutScopeTests(unittest.TestCase):
    def test_subscenes_fixture_validates_against_schema(self) -> None:
        scope_path = PROJECT_ROOT / "agents" / "commercial_fitout" / "subscenes.json"
        errors = validate_json(
            PROJECT_ROOT / "core" / "schemas" / "commercial_fitout_scope.schema.json",
            scope_path,
        )
        self.assertEqual(errors, [])

    def test_scope_contract_primary_subscenes_and_not_claimable(self) -> None:
        scope = load_commercial_fitout_scope()
        self.assertEqual(set(scope["primary_subscenes"]), PRIMARY_SUBSCENE_IDS)
        self.assertIn("full_construction_documents", scope["delivery_commitments"]["explicitly_not"])
        assert_scope_contract(scope)

    def test_scope_markdown_documents_three_subscenes(self) -> None:
        text = (PROJECT_ROOT / "agents" / "commercial_fitout" / "SCOPE.md").read_text(encoding="utf-8")
        self.assertIn("开放办公", text)
        self.assertIn("会议室", text)
        self.assertIn("前台", text)
        self.assertIn("完整施工图", text)
        self.assertIn("subscenes.json", text)

    def test_commercial_fitout_tree_passes_boundary_scan(self) -> None:
        agent_root = PROJECT_ROOT / "agents" / "commercial_fitout"
        violations = scan_agent_tree(agent_root)
        self.assertEqual(violations, [], violations)

    def test_validate_rejects_wrong_primary_subscene_count(self) -> None:
        scope = load_commercial_fitout_scope()
        broken = {**scope, "primary_subscenes": ["open_office", "meeting_room"]}
        errors = validate_commercial_fitout_scope(broken)
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
