# Gate 0 Acceptance Cases

These cases are not compiler fixtures. A valid Gate 0 run must start from the
raw `prompt` only, then produce a SceneSpec through Codex/tool use before CAD
execution.

Forbidden in these cases:

- prefilled SceneSpec
- object dimensions
- placement-side answers such as `mouseSide`
- complete scene templates

