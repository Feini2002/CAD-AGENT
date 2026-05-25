# core/safety

职责：统一 CAD Agent 的安全规则，保护原图，并定义所有 Core 与场景 Agent 必须遵守的绘图门槛。

核心规则：

- 默认写入 `CODEX_PREVIEW`。
- 不默认保存 DWG。
- 不覆盖原始 DWG 文件。
- 不默认修改正式图层。
- 不删除正式实体。
- 大批量生成、正式落图、保存、覆盖和删除必须获得明确批准。

当前迁移来源：

- `CAD_AGENT_RULES.md`
- `AGENTS.md`
- legacy `cad_agent/SAFETY_RULES.md`

当前状态：prototype。文档规则已收束到 Core 入口，后续会继续抽象为可测试策略。

## 状态表达规则

- `executed_only`：已经请求执行，但没有截图或实体回读证据。
- `screenshot_captured`：已经有视觉证据，但还没有几何实体回读。
- `geometry_verified`：已有实体回读，并且图层、数量、尺寸、文字或标注检查通过。
- `unverified`：没有足够证据。
- `failed`：验证证据显示与预期不一致。

Codex 不得把 `executed_only` 或 `screenshot_captured` 描述成“图纸已经准确”。

边界：

- 安全门优先于场景 Agent 的业务效率。
- 所有执行、验证、截图和回读流程都必须尊重本模块。
- 若无法证明安全状态，应停止正式动作并进入自检。
