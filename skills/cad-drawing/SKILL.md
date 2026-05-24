---
name: cad-drawing
description: Use when the user wants Codex to draw, modify, validate, or plan CAD content through natural language for generic CAD workflows, including residential, retail, office, restaurant, exhibition, hospitality, education, healthcare, industrial, or custom floor-plan scenarios.
---

# CAD Drawing Skill

Use this workflow for CAD drawing or CAD Agent development tasks. This project skill is a portable draft inside the CAD Agent kit; it is not tied to the current DWG, current folder path, or a single design industry.

## Core Workflow

1. Read `README.md`, `CORE_STATUS.md`, `CORE_ROADMAP.md`, `CORE_RESTRUCTURE_PLAN.md`, `CAD_AGENT_STATUS.md`, and `CAD_AGENT_RULES.md` when resuming project work.
2. Convert user language into a `CAD_PLAN` before drawing.
3. Validate the plan with `core.plan_engine.validate_plan` or the compatibility wrapper `scripts/validate_plan.py`.
4. Dry-run the plan with `core.plan_engine.dry_run_plan` or the compatibility wrapper `scripts/dry_run_plan.py`.
5. Draw only to `CODEX_PREVIEW` unless the user explicitly approves formal changes.
6. After drawing, report object type, layer, size, placement, and verification status.
7. If drawing is inaccurate, blocked, or unverifiable, read `CAD_AGENT_BLOCKER_PLAYBOOK.md`, run `scripts/self_check.py`, and check screenshot capability before retrying.
8. Update status, changelog, and issues when project files or rules change.
9. Put reusable CAD Agent capabilities in `core/`; keep scene-specific Agent rules lightweight under `agents/`.

## References

Read these only when needed:

- `references/CAD_WORKFLOW.md` for the standard workflow.
- `references/CAD_PLAN_SCHEMA.md` for plan format.
- `references/SAFETY_RULES.md` for CAD safety constraints.
