# CAD Agent 变更记录

这个文件记录 CAD Agent 测试工作区的结构、规则、Schema、脚本和重要决策变化。

## 2026-05-24

### 通用化调整

- 将 `README.md` 定位从当前测试目录调整为“通用 CAD Agent 开发包”。
- 明确本文件夹不绑定当前家装图纸、不绑定当前电脑。
- 明确完整能力由“本文件夹 + 运行环境 + 项目图纸”共同组成。
- 将 `CAD_AGENT_STATUS.md` 当前阶段更新为“阶段 3：CAD_PLAN 校验和 dry-run 已跑通，下一步进入预览绘制”。
- 在 `CAD_AGENT_RULES.md` 增加“通用开发包定位”。
- 扩展 domain 枚举，支持 `exhibition`、`hotel`、`education`、`healthcare`、`industrial`、`custom`。
- 增加办公、餐饮、展厅、酒店、教育、医疗、工业、通用自定义行业包占位。
- 统一 `README.md` 的恢复入口说明：先看 README，再看 4 个项目管理文件。

### 通用化原因

- 用户确认最终目标是可迁移的通用 CAD Agent 开发包。
- 该文件夹未来应能复制到其他电脑和其他 CAD 项目中复用。
- 具体家装图纸只是第一套测试现场，不应污染通用规则。

### 新增

- 创建 `CAD测试相关文件/README.md`，作为测试工作区入口。
- 创建 `CAD_AGENT_STATUS.md`，记录当前开发阶段。
- 创建 `CAD_AGENT_RULES.md`，记录长期规则。
- 创建 `CAD_AGENT_CHANGELOG.md`，记录变更历史。
- 创建 `CAD_AGENT_ISSUES.md`，记录错误和修复。
- 创建 `CAD_AGENT_DECISIONS.md`，记录关键决策和原因。
- 创建第一版目录框架：`cad_agent/`、`skills/`、`schemas/`、`examples/`、`scripts/`、`drivers/`、`libraries/`、`tests/`、`output/`。
- 创建第一版 `CAD_PLAN` Schema 和测试柜示例。
- 创建 `cad-drawing` Skill 骨架。
- 创建 `scripts/validate_plan.py`，用于校验第一版 CAD_PLAN。
- 创建 `scripts/dry_run_plan.py`，用于预演 CAD_PLAN。

### 调整

- 将旧的 `CAD_AGENT_BUILD_GUIDE.md`、`CODEX_CAD_DEV_LOG.md`、`CODEX_CAD_RULES.md` 移动到 `docs/archive/`。

### 决策

- 当前先不创建根目录 `AGENTS.md`，避免过早影响所有 Codex 行为。
- 当前先不引入 SQL。
- 当前先不做完整自动设计。
- 当前先以 `CAD_PLAN` 作为白话和 CAD 绘制之间的中间层。

### 原因

- 用户希望隔几天回来仍能知道开发进度。
- 用户希望规则能随着需求、测试、错误不断迭代。
- 用户希望整个根目录作为 CAD 测试方向，但 CAD 相关资料不要散落在根目录。

### 验证

- 使用 CAD-MCP 虚拟环境 Python 成功运行 `validate_plan.py`。
- 使用 CAD-MCP 虚拟环境 Python 成功运行 `dry_run_plan.py`。
- 发现全局 `python` 命令不可用，已记录到 `CAD_AGENT_ISSUES.md`。
- 发现中文终端输出需要显式 UTF-8，已记录到 `CAD_AGENT_ISSUES.md`。
