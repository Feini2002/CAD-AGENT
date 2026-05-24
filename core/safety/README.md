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
- `cad_agent/SAFETY_RULES.md`

当前状态：scaffold。规则已有文档来源，尚未抽象成可测试策略。

边界：

- 安全门优先于场景 Agent 的业务效率。
- 所有执行、验证、截图和回读流程都必须尊重本模块。
- 若无法证明安全状态，应停止正式动作并进入自检。
