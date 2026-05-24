# commercial_fitout Workflows

## existing_plan_to_elevation

Intent:

```text
Existing commercial plan
-> core drawing_analysis creates DRAWING_MODEL
-> core project_model creates PROJECT_MODEL
-> commercial_fitout selects priority walls and store-specific elevation targets
-> core proposal_engine creates DESIGN_PROPOSAL
-> core plan_engine creates CAD_PLAN
-> core execution draws to CODEX_PREVIEW
-> core verification checks result
```

Scene-specific focus:

- Display wall elevation.
- Cashier back wall elevation.
- Storefront or entrance-facing elevation.

## blank_store_to_layout

Intent:

```text
Blank store boundary and user brief
-> core project_model creates PROJECT_MODEL
-> commercial_fitout applies store layout preferences
-> core layout_engine creates candidate LAYOUT_PROPOSAL
-> core proposal_engine explains assumptions and questions
-> core plan_engine creates CAD_PLAN after approval
-> core execution draws to CODEX_PREVIEW
-> core verification checks result
```

Scene-specific focus:

- Entrance display priority.
- Cashier near exit without blocking flow.
- Shelf and display grouping.
- Main and secondary aisle preferences.

