# CAD Agent Rules

This directory is a portable CAD Agent development kit. It is not tied to one DWG, one home renovation drawing, or one computer.

## Always Restore Context First

Before CAD Agent development, drawing, debugging, or status reporting, read:

1. `README.md`
2. `CORE_STATUS.md`
3. `CORE_ROADMAP.md`
4. `CORE_RESTRUCTURE_PLAN.md`
5. `CAD_AGENT_STATUS.md`
6. `CAD_AGENT_RULES.md`
7. `CAD_AGENT_BLOCKER_PLAYBOOK.md`
8. `CAD_AGENT_CHANGELOG.md`
9. `CAD_AGENT_ISSUES.md`

## Core First

This repository is a generic CAD Agent Core Lab. Put reusable capabilities in `core/`, shared resources in `libraries/`, project-specific data in `projects/`, and only scene-specific differences in `agents/<scenario>/`.

Do not turn the repository into a commercial fitout-only, residential-only, or CAD-MCP-only project. Scenario agents must stay lightweight and reuse Core.

## No Direct White-Language-To-CAD Jump

Natural language must become a `CAD_PLAN` or an explicit structured drawing intent before CAD execution, except for clearly temporary low-risk tests. Validate and dry-run before real CAD drawing.

## Mandatory Drawing Accuracy Gate

Before telling the user a CAD drawing is done or accurate, Codex must verify it against evidence:

- expected object, dimensions, base point, layer, text, annotations, and allowed tolerance
- `scripts/validate_plan.py` result
- `scripts/dry_run_plan.py` result
- equivalent `core.plan_engine` entrypoints when using the new architecture
- actual CAD output on `CODEX_PREVIEW`
- screenshot from `scripts/render_preview.py --capture-screen` or CAD entity readback from the inspection path
- comparison of actual output against the expected CAD_PLAN or structured intent

If actual output differs from expected output, Codex must not hand the bad result to the user as finished. It must diagnose the mismatch, make the smallest safe fix, redraw or re-run, and verify again.

## Blocked Or Inaccurate Drawing Flow

When the user says “画不准”, “画不出来”, “不对”, “继续修”, or when Codex cannot prove the drawing is accurate, follow `CAD_AGENT_BLOCKER_PLAYBOOK.md`.

Minimum required probes:

```powershell
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' 'scripts\self_check.py'
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' 'scripts\render_preview.py' --check
```

If visual evidence is needed and the user has not forbidden screenshots, capture a checkpoint:

```powershell
& 'C:\Users\User\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe' 'scripts\render_preview.py' --capture-screen --output 'output\previews\manual-check.png'
```

If screenshot or readback is unavailable, say that accuracy cannot yet be proven and prioritize the missing verification mechanism before claiming success.

## Protect The User's DWG

- Default to `CODEX_PREVIEW`.
- Do not save the active DWG by default.
- Do not overwrite original DWG files.
- Do not modify formal layers, delete entities, or commit irreversible CAD actions without explicit user approval.

## Keep Records Updated

When CAD Agent rules, scripts, tests, workflow docs, or status change, update:

- `CAD_AGENT_STATUS.md`
- `CAD_AGENT_CHANGELOG.md`
- `CAD_AGENT_ISSUES.md` when the change is caused by a failure, risk, or debugging lesson
