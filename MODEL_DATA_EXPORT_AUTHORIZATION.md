# Model Data Export Authorization

最后更新：2026-06-05

本文记录用户对本仓库模型桥的长期授权口径，供新电脑克隆、环境迁移和后续 Agent 接手时读取。本文不是密钥文件，不保存 OpenAI / Codex / Cloudflare token，也不替代本机登录、系统审批、沙箱审批或工具权限。

## 核心授权

用户已明确预授权：在 `C:\Users\User\Desktop\CAD-AGENT` / 本仓库工作区内，为打通模型型 Agent 的 5.5 只读复审链路，可以通过本机 `codex.cmd exec` 或等价 Codex CLI 桥调用 `gpt-5.5`，并将经过边界控制的 prompt、schema、任务摘要、CAD readback 摘要、必要截图或报告片段发送给 OpenAI 模型服务。

授权目的仅限：

- 让 `core/model_review`、Prompt Pack、Reviewer Host、Orchestrator Host 或模型桥 Agent 产生真实 `modelInvoked=true` 的 schema 化 JSON 输出。
- 复审设计意图、视觉质量、语义拆分、资产来源、修复建议、交付声明、训练沉淀候选和场景常识。
- 写入可审计 trace、`modelProviderStatus`、stdout / stderr、schema 校验、normalized output、`trace_review.json`、`trace_summary.md` 和 run package 证据。

## 默认允许的数据

在不再单独追问用户的情况下，允许发送以下最小必要内容：

- 当前任务的自然语言指令、结构化任务摘要和 Prompt Pack。
- 与当前模型复审直接相关的 JSON schema、boundary rules、required fields 和输出格式要求。
- 当前 run package 中已明确列入 evidence bundle 的摘要文件。
- `CAD_PLAN`、validate / dry-run 摘要、created handles readback 摘要、bbox / layer / entity type 审计摘要。
- 为视觉复审必要的裁剪截图或聚焦截图，前提是截图来源、用途和路径写入 trace。
- 不含密钥、不含无关全仓内容的错误日志、stdout / stderr 摘要和模型调用诊断信息。

## 默认禁止的数据和动作

以下内容不在本授权内，必须阻断或另行取得用户明确授权：

- 上传整个仓库、整个 `output/`、整个 DWG、全模型空间内容、全屏截图或无关项目资料。
- 上传 API key、token、cookie、SSH key、浏览器缓存、个人账号凭据、客户合同、报价、地址、身份证明或其它明显敏感信息。
- 读取或发送未列入当前任务 evidence bundle 的任意本地文件。
- 让模型输出或授权 AutoCAD 命令、COM 调用、保存当前业务 DWG、覆盖原图、删除实体、移动实体、修改正式图层或扩大 CAD 写入范围。
- 用模型 pass 替代 UTF-8 编码门禁、`CAD_PLAN` 校验、dry-run、created handles 回读、bbox / layer / overlap 审计、sourceSpec、reuseReplay、表 C 证据或用户验收。
- 将本授权解释为公开 API、账号共享、多人共用个人 Codex 登录态或规避服务条款的代理。

## 运行要求

每次真实模型桥调用必须满足：

- 调用入口优先使用 `core/model_review`、`codex.cmd exec` 或仓库认可的等价 SDK 桥。
- 输出必须是 strict JSON，并通过对应 schema 校验。
- 输出必须包含或归一化为 `modelProviderStatus`，至少记录 `modelInvoked`、`modelUnavailable`、`schemaValid`、`route`、`required` 和 `blocking`。
- 必须记录 sanitized command、cwd、模型、reasoning effort、输入引用、stdout / stderr、last message、normalized output、trace review 和 trace summary。
- 若模型不可用、schema invalid、字段缺失、外传范围超出本文、或工具层需要额外审批未通过，则结果必须是 `blocked` / `not_verified`，不得伪装成模型已参与。

## 换机迁移

新电脑克隆本仓库后，本文只提供策略口径，不迁移任何本机凭据或登录态。新机器首次启用模型桥前，应重新检查：

- `codex.cmd` / Codex CLI 已安装并可运行。
- 本机 Codex 已登录，且有目标模型权限和额度。
- 工作区白名单指向新机器上的本仓库路径。
- `CAD_AGENT_MODEL_REVIEW_ENABLED` 等模型桥开关按当前任务需要设置。
- AutoCAD / CAD-MCP / Python venv / COM / 截图工具在新机器上可用。
- 本文仍符合用户意愿；若用户撤销或收紧授权，以最新口头或书面指令为准。

## 推荐最小验证

新机器首次验证时，不要直接跑完整 CAD 训练。先做一个低风险只读模型复审 probe：

```powershell
codex.cmd exec --json --model gpt-5.5 --sandbox read-only "Return a strict JSON object proving this local Codex CLI model call works. Do not read files."
```

随后再用仓库脚本或 `core/model_review` 跑一个只包含脱敏摘要的 Prompt Pack probe，确认 `modelInvoked=true`、`schemaValid=true` 和 trace 写入正常。

## 撤销和收紧

用户可随时用自然语言撤销或收紧本文授权。收到撤销后，Agent 必须停止远端模型桥调用，并将相关流程退回 `local_model`、`manual_human_review`、`summary_candidate_not_sent` 或 `modelProviderStatus=unavailable`。

