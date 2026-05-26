# CAD Agent Core Lab

## 系统简介

CAD Agent Core Lab 是一个可迁移的通用 CAD Agent 开发包，用结构化 `CAD_PLAN` 连接自然语言需求、设计模型、CAD 执行和可验证结果。它不绑定某一张 DWG、某一套家装图纸或某一台电脑，也不把工装、家装、办公等场景写成彼此割裂的独立系统。

核心方向是：

- `core/` 沉淀通用能力：读图、模型、对象、风格、布局、计划、执行、验证和安全边界。
- `agents/<scenario>/` 只保留轻量场景差异，复用 Core，不复制 Core 算法。
- `libraries/` 存放跨场景资源，例如对象默认值、块库、风格、材料、尺寸和图层标准。
- `projects/` 存放真实或样例项目资料。
- `docs/` 存放架构、计划、治理、交接、验证、决策和历史记录；Cursor 按包交付见 [`docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md`](docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md)。

仓库的绘图原则是先把白话需求转成 `CAD_PLAN` 或更高层结构化意图，再做校验、dry-run、执行和回读验证。真实 CAD 输出默认只落到 `CODEX_PREVIEW`，不默认保存 DWG，不覆盖原始文件，不删除已有实体，不修改正式图层；面向用户生产的图形默认不加中文 / 英文文字标注，也默认不加尺寸标注，相关能力保留到用户明确要求时再启用。

## 开发状况

当前仓库是 **通用 CAD Agent Core Lab**（Core Alpha 原型 + 场景 Alpha/Beta 验证层）。日常执行台账见 [`docs/planning/任务清单.md`](docs/planning/任务清单.md)（§3 能力证明 / §4 代码轨 / §5 CAD 补验）；架构说明见 [`docs/planning/capability-proof-architecture.md`](docs/planning/capability-proof-architecture.md)。

主链路已经跑通：

```text
SHELL_MODEL
-> PROJECT_MODEL
-> CIRCULATION_MODEL
-> FUNCTION_ZONE
-> placements
-> LAYOUT_PROPOSAL
-> DESIGN_PROPOSAL
-> CAD_PLAN
-> dry-run
-> VERIFICATION_REPORT
```

最新稳定结论：

- 当前唯一 `PlanMD` / 开发主线是 `CORE_RESTRUCTURE_PLAN.md`。
- `CORE_CONTEXT_BRIEF.md` 是日常恢复上下文的短入口。
- `docs/planning/phase-*.md` 是 Phase 执行剧本，不是第二套主计划；后置 Backlog 和未来小包只看 `CORE_RESTRUCTURE_PLAN.md`。
- 最新真实 CAD strict 矩阵的 baseline 子流程内全量回归为 `466 tests OK`，repo audit 0 findings；blank-shell、office alpha、interior delivery、project sample、proposal confirmed、CAD beta rollup 和 scene beta benchmark 均已有可重复运行证据。
- `core.plan_engine`、benchmark runner、composition engine、CAD validation runner、本地 CAD regression runner 已进入可运行原型状态。
- `LCAD-01-REGRESSION-MANIFEST` 已完成：`scripts/run_local_cad_regression.py` 现在有默认 regression manifest，能汇总 baseline CAD validation、project sample CAD check 和 interior composition CAD check，并输出 manifest metadata、deferred / strict gate 证据；no-CAD 矩阵不等于真实 CAD 几何通过。
- `LCAD-02-STRICT-MATRIX-RUNNER` 已完成：runner 支持 `--case` selected case、默认 all case、`--strict` 严格别名和统一 rollup；selected no-CAD 证据见 `output\validation_runs\lcad-02-selected-project-sample-no-cad`。
- 在当前测试 CAD 文件下，`LCAD-02` 真实 CAD strict all run 已通过：`output\validation_runs\lcad-02-strict-all-cad` 顶层 `status=pass`，`geometry_verified_case_count=6`，`created_handle_count=90`。
- 复杂 CAD smoke 已前置加固并纳入默认 regression manifest：`output\validation_runs\complex-cad-regression-strict-final` 顶层 `status=pass`，`selected_case_count=4`，`step_count=5`，`geometry_verified_case_count=7`，`created_handle_count=113`；其中 `complex_cad_smoke` 单项绘制并回读 23 个混合实体，类型覆盖 line / polyline / circle / arc / text / dimension，bbox 为 `3600 x 2200`。
- 真实 CAD 验证已覆盖 baseline、基础图元能力探针、受控 block alpha 和 3 个简单 interior composition cases，并取得有限 `geometry_verified` 证据。
- 场景相关工作目前应分为四级：`Core 底座`、`Scene Alpha 壳层`、`Scene Beta 能力包`、`Scene Product 场景产品`。当前已有的是轻量场景壳层和若干 non-CAD beta benchmark，不等于工装、办公、住宅或餐饮场景 Agent 已产品化完成；边界说明见 `docs/architecture/core-scene-agent-boundaries.md`。
- **路线 A~D** 已收口或进入 LCAD 尾项；**路线 E**（RCAD 真实 CAD）与 **路线 F**（能力证明体系）并行推进。
- `LCAD-01`~`09` 已 done；`commercial_fitout` 为 **Scene Product Alpha**（C-CFIT-01..07）；`SYMBOL-CORE`（D-SYMBOL-01..07）、`Core Orchestrator`（B-ORCH-01..05）已收口。
- 用户会话 CAD 补验证据：`output/validation_runs/user-cad-full-verify-20260526/`、`rcad补验-20260526/`。

仍需注意：工程完备度高 **不等于** CAD 已全面验证。不能把有限 `geometry_verified` 扩大为任意项目、公司块库或任意 `CAD_PLAN` 均已准确；几何结论仍以 created handles 回读与 `geometry_verified` 为准。

## 交付进度规则

每次 CAD Agent 相关交付应附带两组粗估进度（详见 `AGENTS.md`）：

**表 A — 工程节奏**

| 指标 | 当前粗估 |
| --- | --- |
| 总进度 | 约 86% |
| Core 底座开发进度 | 约 96% |
| Agent 多场景实现进度 | 约 52% |

**表 B — 任务清单三指令执行进度**（[`任务清单.md`](docs/planning/任务清单.md) §0）

| 指令 | 板块 | 执行进度 |
| --- | --- | --- |
| 能力证明 | §3 | 约 5%（0/43） |
| 一键推进（代码轨） | §4 | 约 18%（9/49） |
| CAD 补验 | §5 | 约 48%（14/29） |

默认 `总进度 = Core * 70% + Agent * 30%`。表 B 与表 A 不是同一套数；新增任务包入表时分母变大，百分比可能下降。

## 三指令（对白话）

| 你说 | 推进 |
| --- | --- |
| **能力证明** | `任务清单.md` §3 首项 `next` |
| **一键推进** | `任务清单.md` §4 代码轨首项 `next` |
| **CAD 补验** / **开 CAD 了** | `任务清单.md` §5 首项 `stale`/`pending`（须 AutoCAD + `$py`） |

## 下一步计划

1. **能力证明**：`V-PROOF-00-REGISTRY-SCHEMA` → 种子登记表与覆盖率 CLI。
2. **代码轨**：`LCAD-10.1-NEG-FIXTURES` → `10.2`~`10.5` 负向安全 → `LCAD-11.x` 趋势（与 V-PROOF-71 合并）。
3. **CAD 补验**：`RCAD-01`（stale）→ `RCAD-14`~`28` 待办（逐项见 `任务清单.md` §5.2）。
4. 主计划与 Decision Gate：`CORE_RESTRUCTURE_PLAN.md`；短上下文：`CORE_CONTEXT_BRIEF.md`。

## 常用命令

```powershell
cd "C:\Users\User\Desktop\新家改造\CAD测试相关文件"
$env:PYTHONIOENCODING='utf-8'
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest discover -s tests
& $py scripts\self_check.py
& $py scripts\render_preview.py --check
& $py scripts\run_local_cad_regression.py --strict --output-dir output\validation_runs\manual-strict
```

## 文档入口

| 目标 | 文件 |
| --- | --- |
| 主计划 PlanMD | `CORE_RESTRUCTURE_PLAN.md` |
| 任务清单（三板块） | `docs/planning/任务清单.md` |
| 短上下文 | `CORE_CONTEXT_BRIEF.md` |
| 能力与证据 | `CORE_STATUS.md`、`CAD_AGENT_STATUS.md` |
| 规则与变更 | `AGENTS.md`、`CAD_AGENT_RULES.md`、`CAD_AGENT_CHANGELOG.md` |
| Cursor 交接 | `docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` |
