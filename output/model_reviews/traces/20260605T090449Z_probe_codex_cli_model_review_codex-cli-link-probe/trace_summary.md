# Model Review Trace Summary

- Agent: probe_codex_cli_model_review
- Task: synthetic_connectivity_probe
- Trace: codex-cli-link-probe
- 状态: blocked

## 本次复盘
- trace 可复盘性：可用
- 模型调用可用性：不可用
- 输入充分性：可用
- 模型输出可信度：unavailable
- 错误分类：provider_unavailable
- gate 结论：blocked
- 导出边界清单：export_manifest.json
- 上下文泄漏审计：context_leak_audit.json
- 阻断原因：modelUnavailable is true；schemaValid is not true；gate decision is blocked；codex cli review returned non-zero exit；model report status is unavailable

## 下一步
- 检查模型开关、Codex CLI 可执行文件、登录态、额度或 provider 权限。
- 检查 schema required 字段和模型 last message JSON。
- 按 gate_decision.json 的阻断原因修复，再重新调用模型 reviewer。

## 边界
- 本摘要只用于调试模型型 Agent 调用，不替代 schema 校验、CAD readback、A-to-A hard gate 或用户验收。
