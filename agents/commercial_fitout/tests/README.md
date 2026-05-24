# commercial_fitout Tests

Agent tests should verify only scene selection and defaults.

Suggested future checks:

- `existing_plan_to_elevation` selects display wall, cashier back wall, or storefront candidates from a core PROJECT_MODEL.
- `blank_store_to_layout` applies entrance display and aisle width preferences before calling core layout.
- The agent never bypasses core validation, dry-run, preview execution, or verification.

