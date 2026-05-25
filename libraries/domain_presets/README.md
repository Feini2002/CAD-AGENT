# libraries/domain_presets

This directory stores cross-scenario domain presets: common spaces, common
objects, and default layer roles that more than one scene agent can reuse.

These files are not scene agents. Scene-specific preferences and workflows stay
under `agents/<scenario>/`, while reusable defaults stay here.

`libraries/domains/` is retained only as a legacy compatibility location during
the second-round migration. New presets should be added here.
