from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / ".agents" / "skills" / "cad-scene-authoring"


def test_cad_scene_authoring_skill_frontmatter_and_scope():
    skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

    assert "name: cad-scene-authoring" in skill
    assert "create, arrange, modify, inspect, or verify CAD scene content" in skill
    assert "Do not use for repository architecture work or status reporting." in skill
    assert "CODEX_PREVIEW" in skill
    assert "savedCurrentDwg=false" in skill


def test_skill_references_describe_scene_spec_and_tool_loop():
    scene_spec = (SKILL_ROOT / "references" / "scene-spec.md").read_text(encoding="utf-8")
    tool_loop = (SKILL_ROOT / "references" / "tool-loop.md").read_text(encoding="utf-8")
    checklist = (SKILL_ROOT / "references" / "gate0-checklist.md").read_text(encoding="utf-8")

    assert "SceneSpec" in scene_spec
    assert "cad-agent compile" in tool_loop
    assert "cad-agent verify" in tool_loop
    assert "deterministic verify fail" in checklist
    assert "Do not save the current DWG" in checklist


def test_skill_forbids_legacy_shortcuts_and_exact_routes():
    text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

    forbidden_guidance = [
        "Do not call old drawing scripts",
        "Do not execute arbitrary AutoLISP",
        "Do not skip inspect",
        "Do not write formal layers",
        "Do not add exact phrase routes",
    ]
    for guidance in forbidden_guidance:
        assert guidance in text
