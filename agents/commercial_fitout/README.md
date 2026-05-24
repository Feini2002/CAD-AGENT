# commercial_fitout Agent

Lightweight scene agent for commercial fitout and retail store work.

This agent only records scene differences, default preferences, and workflow names. It must reuse core capabilities for drawing analysis, project models, object generation, layout, CAD_PLAN creation, execution, safety, and verification.

## Scope

- Existing retail or commercial plan to elevation intent.
- Blank store layout intent.
- Storefront, display, cashier, circulation, and feature-wall priorities.

## Core Reuse Contract

- Use core for all CAD IO, drawing parsing, model building, layout solving, CAD_PLAN validation, dry-run, execution, and verification.
- Do not duplicate core schemas or execution logic in this agent.
- Keep scene-specific rules small and explicit.

## Workflows

- `existing_plan_to_elevation`
- `blank_store_to_layout`

