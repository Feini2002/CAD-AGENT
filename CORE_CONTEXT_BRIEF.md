# Core Context Brief

最后更新：2026-05-26

本文是后续 Codex 开发本仓库时的短上下文入口。它只保留当前事实、硬边界和展开索引；旧完成记录已降权到 `docs/history/root-md-full-snapshot-2026-05-26/`。

默认读取顺序：

1. `AGENTS.md`
2. 本文
3. 按当前任务展开下方“按需展开”表

只有执行具体 phase、完整复盘、排查失败、修改规则/计划/状态/变更/问题记录时，才展开对应详细文件。

## 当前结论

- 本仓库是通用 CAD Agent Core Lab，不绑定某张 DWG、某套家装图纸或某台电脑。
- 唯一 `PlanMD` / 主计划是 `CORE_RESTRUCTURE_PLAN.md`；根目录没有独立 `plan.md`。
- 当前主线优先级：**能力证明体系（路线 F）** 与 **LCAD 硬化尾项** 并行；能力证明 next=`V-PROOF-00-REGISTRY-SCHEMA`；代码轨 next=`LCAD-10.1-NEG-FIXTURES`（全队列见 `docs/planning/任务清单.md`）。
- **三进度口径**（禁止混用）：工程完备度（Core≈96%）≠ CAD 证明覆盖率（待首算，定性<10%）≠ 展示等级 Ladder（当前最高约 L3~L4 边缘）。
- `commercial_fitout` 为 **Scene Product Alpha**（C-CFIT-01..07）；office / residential / restaurant 仍为 Scene Alpha/Beta。
- Core 底座已有较厚 Alpha 原型：schema、workflow、`CAD_PLAN`、dry-run、验证、benchmark、读图、对象、受控 block、有限真实 CAD 回读都已有入口。
- office / residential / restaurant 目前主要是 Scene Alpha 壳层和 Scene Beta non-CAD 能力包；不能说具体场景产品已完成。
- `agents/demand_side/` 已建立需求侧角色 Agent 数据层，覆盖 6 个现有场景并通过 non-CAD demand benchmark；它是开发期需求压力测试脚手架，不是 Scene Product，后续能力沉淀后可清理角色表。
- `object_detail_spec` 已把部分需求沉淀为 Core 能力：table / bed / chair / sofa / desk 可展开为组件级安全预览 `CAD_PLAN`；其中 demand-side 10 个 case 已补跑真实 CAD readback。
- 最新已知 CAD regression 证据包括 complex CAD smoke 和 full strict matrix，但结论只覆盖受控测试会话、`CODEX_PREVIEW`、created handles 回读范围内的实体。
- `CORE_RESTRUCTURE_PLAN.md` 已新增系统优化路线拆分：A CAD 安全与证据链，B `Core Orchestrator` + `Scene Router`，C `commercial_fitout` Scene Product Alpha，D `SYMBOL-CORE` CAD 符号语法；默认建议顺序 A -> B -> C，D 可在对象 / 家具图库需求明确时优先。
- `docs/planning/任务清单.md`：§3 **V-PROOF** 能力证明、§4 代码轨、§5 **RCAD**。触发：「能力证明」→ §3；「一键推进」→ §4；「CAD 补验」→ §5。架构见 `docs/planning/capability-proof-architecture.md`。
- 面向用户生产的 CAD 输出默认不落中文 / 英文文字标注，也不默认落尺寸标注；文字和尺寸能力保留，只有明确需求或能力测试时启用。

## 当前可信证据

| 证据 | 当前摘要 |
| --- | --- |
| complex CAD smoke | `output\validation_runs\complex-cad-smoke-real-final`，`status=geometry_verified`，`created_handle_count=23`，覆盖 line / polyline / circle / arc / text / dimension |
| full strict CAD matrix | `output\validation_runs\complex-cad-regression-strict-final`，`selected_case_count=4`，`geometry_verified_case_count=7`，`created_handle_count=113` |
| LCAD manifest / runner | `LCAD-01`~`09` 已完成；默认 manifest 7 case；用户会话 strict 7/7 几何 verified |
| user CAD full verify | `output\validation_runs\user-cad-full-verify-20260526\user_cad_full_verify_summary.json` |
| composition CAD | `composition_cad` 3/3 `geometry_verified`；40 handles（manifest strict 子目录） |
| project sample rollup | `sample_blank_shell` 20 + `commercial_fitout_sample` 12 handles |
| symbol glyph real CAD | `user-cad-full-verify-20260526\symbol-glyph-smoke` desk glyph verified |
| demand-side agent benchmark | `examples\benchmarks\demand_side_agent_benchmark.json`，10 个需求 case 覆盖 6 场景，non-CAD pass |
| demand-side real CAD check | `output\validation_runs\demand-side-agent-cad-real-20260526\demand_side_agent_cad_check_report.json`，10/10 `geometry_verified`，`created_handle_count=100` |
| object detail spec | 精细餐桌 5 个组件 CAD_PLAN、办公椅 6 个组件 CAD_PLAN，已包含在 demand-side real CAD check 中 |
| no-CAD validation | no-CAD 报告只能证明 deferred / gate 正确，不能证明真实 CAD 几何准确 |
| Scene Alpha / Beta | 三场景 preferences、解释模板和 non-CAD benchmark 可用，但不是 Scene Product |

## 不能声称的事

- 不能把 **工程完备度约 96%** 写成「CAD 已全面验证」或「能画任意复杂图块」；须看 CAD 证明覆盖率与 Ladder。
- 不能把截图、`render_preview.py --check` 或 no-CAD benchmark 当成几何准确证据。
- 不能把 `geometry_verified` 的受控 baseline、复杂 smoke、受控 block alpha 或 3 个组合样例扩大为任意真实 DWG、公司块库、属性块、hatch 或任意 `CAD_PLAN` 全部准确。
- 不能把 Scene Alpha / Beta 的 preferences、rules、benchmark pass 写成工装、办公、住宅或餐饮 Agent 已产品化。
- 不能把 demand-side role agents 或 demand benchmark 写成真实用户代理、自动设计闭环或真实 CAD verified。
- 没有明确场景或项目 manifest 指定时，默认必须是 `no_scene` + 通用 Core。
- 未经用户明确批准，不保存当前 DWG、不覆盖原始 DWG、不删除实体、不修改正式图层。

## PlanMD 主从规则

- `CORE_RESTRUCTURE_PLAN.md` 决定当前活跃工作队列、Phase 顺序、优先级、Decision Gate 和退出标准。
- `docs/planning/phase-*.md` 只是执行剧本，可以写步骤和命令，不能成为第二套主计划。
- `CORE_STATUS.md`、`CAD_AGENT_STATUS.md` 只写能力、证据、风险和当前状态，不写独立下一步。
- `CAD_AGENT_CHANGELOG.md`、`CAD_AGENT_ISSUES.md` 现在只保留高频摘要；完整旧流水见 `docs/history/root-md-full-snapshot-2026-05-26/`。

## 交付进度格式

每次 CAD Agent 相关交付最终回复都附带（详见 `AGENTS.md`）：

**表 A — 工程节奏**：总进度约 86%、Core 约 96%、Agent 约 52%。

**表 B — 任务清单三指令执行进度**（见 `docs/planning/任务清单.md` §0）：能力证明约 5%（0/43）、一键推进约 18%（9/49）、CAD 补验约 48%（14/29）。

**表 C（可选）**：CAD 证明覆盖率待 `V-PROOF-02`；Ladder 约 L3~L4 边缘。

工程节奏与三指令执行进度均不替代 `geometry_verified` 或 registry `verified` 比例。

## 按需展开

| 目标 | 先读 | 说明 |
| --- | --- | --- |
| 当前主计划 / 下一包 | `CORE_RESTRUCTURE_PLAN.md` | 唯一 PlanMD；下一包 `LCAD-10.1` |
| 任务清单 / 能力证明 | `docs/planning/任务清单.md`、`capability-proof-architecture.md` | §3 V-PROOF + §4 代码 + §5 RCAD |
| 真实 CAD 补验 | `CORE_RESTRUCTURE_PLAN.md` 路线 E | RCAD 执行后回写 registry |
| 系统优化路线 | `CORE_RESTRUCTURE_PLAN.md` | 看“系统优化路线拆分”，A/B/C/D 均已进入主计划 |
| 能力成熟度 | `CORE_STATUS.md` | 能力矩阵、进度口径、关键风险 |
| 当前交付状态 | `CAD_AGENT_STATUS.md` | 最近验证、当前缺口、恢复开发问法 |
| CAD 卡壳 / 画不准 | `CAD_AGENT_BLOCKER_PLAYBOOK.md`、`CAD_AGENT_ISSUES.md` | 按 blocker 流程跑自查和截图辅助 |
| 真实 CAD 验证 | `CAD_AGENT_AUTONOMOUS_VALIDATION.md`、`docs/planning/phase-w-cad-validation-plan.md` | `CODEX_PREVIEW`、created handles、readback |
| 场景边界 | `docs/architecture/core-scene-agent-boundaries.md`、`agents/SCENE_AGENT_RULES.md` | 防止把 Scene Alpha / Beta 误写成 Scene Product |
| 文档治理 | `docs/planning/phase-z-doc-governance-plan.md`、`docs/history/README.md` | 根 MD 压缩、历史归档、索引维护 |
| 完整旧记录 | `docs/history/root-md-full-snapshot-2026-05-26/` | 压缩前根文档完整快照 |

## 固定边界

- 通用能力进入 `core/`。
- 场景差异进入 `agents/<scenario>/`。
- 跨场景资源进入 `libraries/`。
- 真实或样例项目资料进入 `projects/`。
- 旧命令兼容包装器保留在 `scripts/` 和 `drivers/`。
- 生成证据进入 `output/` 或 `docs/verification/`，不默认提交。

## 常用验证

优先使用 CAD-MCP 虚拟环境 Python：

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
```

非 CAD 基线：

```powershell
& $py -m unittest discover -s tests
& $py scripts\self_check.py
& $py scripts\render_preview.py --check
& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\manual-no-cad
```

真实 CAD 验证：

```powershell
& $py scripts\run_local_cad_regression.py --strict --output-dir output\validation_runs\manual-local-cad-regression
& $py scripts\run_cad_validation.py --output-dir output\validation_runs\manual-cad-check
```

## 缓存友好约定

- 本文只写短摘要，不写长历史。
- 长流水进 `CAD_AGENT_CHANGELOG.md` 的高频摘要；完整旧流水进 `docs/history/`。
- 失败教训进 `CAD_AGENT_ISSUES.md` 的活跃摘要；完整旧问题库进 `docs/history/`。
- 当前主线只在 `CORE_RESTRUCTURE_PLAN.md` 维护。
- 能力成熟度只在 `CORE_STATUS.md` 维护。
