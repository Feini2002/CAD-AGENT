# residential Agent

Lightweight scene agent for residential interior CAD work.

This agent only records residential vocabulary, defaults, and preferences. It must reuse core capabilities for drawing analysis, project models, object generation, layout, CAD_PLAN creation, execution, safety, and verification.

## Scope

- Residential layout preferences.
- Common room relationships.
- Typical home interior objects and feature walls.

## Core Reuse Contract

- Use core for CAD IO, drawing parsing, model building, layout solving, CAD_PLAN validation, dry-run, execution, and verification.
- Do not duplicate core schemas or execution logic in this agent.

