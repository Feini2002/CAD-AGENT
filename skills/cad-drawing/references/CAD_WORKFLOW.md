# CAD Workflow Reference

Standard order:

```text
natural language
-> CAD_PLAN
-> validate with core.plan_engine or scripts/validate_plan.py
-> dry-run with core.plan_engine or scripts/dry_run_plan.py
-> preview draw
-> inspect
-> user confirmation
```

Ask the user when location, size, target drawing, save behavior, or formal-layer changes are unclear.

When blocked, inaccurate, or unverifiable:

```text
read CAD_AGENT_BLOCKER_PLAYBOOK.md
-> run scripts/self_check.py
-> check scripts/render_preview.py --check
-> create the smallest repro
-> fix and verify before retrying broader CAD work
```
