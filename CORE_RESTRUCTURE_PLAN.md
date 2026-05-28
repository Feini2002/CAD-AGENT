# CAD Agent Core PlanMD（唯一开发主线）

状态：完工后治理版（毛坯转精装）；活跃队列从“施工明细”收束为“后置包路由器”。
最后更新：2026-05-29

> 本文仍是唯一 `PlanMD`。用户提到 `plan.md`、`PlanMD`、主计划或主 plan 时，默认指本文。执行前先读 `AGENTS.md`、`CORE_CONTEXT_BRIEF.md`，再按本文路由打开任务清单、runbook、verification 或 history。

瘦身前全文快照已归档：`docs/history/snapshots/finished-architecture-2026-05-28/CORE_RESTRUCTURE_PLAN.md`。已完成包明细不再写回本文，统一看 `docs/planning/archive/` 与 `docs/handoffs/package-index.md`。

## 0. 当前一句话

仓库已从施工期进入 **Agent 训练期（方案 A）**：**Core 100% 收口**；默认主训 **家装**（`docs/training/residential-primary.md`），用 `projects/<case>/` + `feedback.md` 闭环。Lab 表 C / 后置 Backlog 仅在回归或扩 registry 时用，**不再**开旧 Phase 施工包。

当前最重要的边界：

- 真实 CAD 准确性只看 `CAD_PLAN` → validate → dry-run → `CODEX_PREVIEW` → created handles 回读 → `geometry_verified`。
- 训练期先走 **Visual-First**：`pipeline_visual_intent` 必须产出 `style_target`、`visual_parts` 与 `reference_match` 判定；缺失则阻断 Execute。
- **CAD 常识底座升级** 已进入训练架构：外部方法论只吸收为知识沉淀、catalog-first、可执行检查和证据边界；用户确认要随 git 迁移的标准图库原始文件放 `standard_cad_library_raw/`，但不能因为 raw 文件存在就声称学会。
- **CAD 资产智能基础设施** 已进入训练架构：参考图库只做 evidence input，自产图库才是 promoted asset；基础版已落地（目录 / schema / 自动 raw intake / `retrieval_pack` / `pipeline_asset_retriever` / intake 模板 / promotion gate），但 RAG、对象族试点、自动晋升和真实 CAD 能力证明仍未完成。
- 表 C 机器值只以 `output/validation_runs/capability-lab/cad_capability_coverage.json` 为准。
- 截图、no-CAD benchmark、RCAD 烟囱和工程百分比都不能替代真实 CAD 几何证明。

## 1. 防偏离边界

- 本仓库是通用 CAD Agent Core Lab，不变成某个家装、工装、办公、餐饮、展陈或 CAD-MCP 专用项目。
- 可复用能力放 `core/`，共享资源放 `libraries/`，项目资料放 `projects/`，场景差异放 `agents/<scenario>/`。
- 自然语言不能直接跳到真实 CAD；必须先形成 `CAD_PLAN` 或明确结构化绘图意图。
- 真实落图默认只写 `CODEX_PREVIEW`；不默认保存 DWG、不覆盖原图、不删除实体、不改正式图层。
- 场景 Agent 保持轻量，只表达偏好、词汇、对象组合语义和排序权重，不实现 Core 算法、CAD 执行或回读。

## 2. 文档主从协议

| 层级 | 文件 | 负责什么 |
| --- | --- | --- |
| L0 规则 | `AGENTS.md` | 不变规则、交付口径、安全边界 |
| L1 短入口 | `CORE_CONTEXT_BRIEF.md` | 一句话、表 C、训练口令、按需展开表 |
| L1b 训练 | `docs/training/README.md` | 案例闭环、家装主训、不可声称 |
| L1c 常识 | `docs/training/cad-common-sense-upgrade.md` | 外部方法论吸收、常识进入系统、低噪声训练反馈 |
| L1d 资产智能 | `docs/architecture/cad-asset-intelligence-architecture.md` | 参考图库 / 自产图库边界、检索调用链、Agent 职责、训练晋升生命周期 |
| L1e 资产开发计划 | `docs/planning/cad-commonsense-asset-dev-plan-01.md` | 标准图库 raw 输入、reference 标注、knowledge 编译、自产图库晋升步骤 |
| L1f OpenSpec 契约 | `openspec/changes/<change>/` | 单个复杂变更的 proposal / design / tasks / specs；不承载总 backlog |
| L2 主线 | 本文 | Decision Gate、Lab 路由、完成判定 |
| L3 执行台账 | `docs/planning/任务清单.md` | **案例 backlog**、训练 / 表 C 口令 |
| L4 证据 | `CORE_STATUS.md`、`docs/status/current.md`、`docs/verification/`、`output/validation_runs/**` | 能力状态、风险、机器证据 |
| L5 历史 | `docs/planning/archive/`、`docs/history/`、`docs/handoffs/archive/` | done 明细、旧 Phase 剧本、交接归档 |

冲突处理顺序：用户最新明确指令 > `AGENTS.md` 安全规则 > 本文 > 任务清单 > 状态页 / handoff / 历史。其它 MD 不得保留第二套 next、优先级或退出标准。

OpenSpec 只在复杂契约变更时承接 proposal / design / tasks / specs；单文件小修、训练 round、刷新表 C 和状态记录不强制开 change。根级 `openspec/tasks.md` 禁止出现，所有任务必须归属具体 change。

## 3. 当前可选主线

**Core 平台施工已关闭**（2026-05-28）：三轨 45/52/29 收口 + `run_core_platform_gate.py`；明细见 `docs/planning/archive/core-platform-closed.md`。下表为**后续**可选主线，不是 Core 底座 backlog。

| 主线 | 触发条件 | 默认入口 | 退出门槛 |
| --- | --- | --- | --- |
| **Agent 训练（家装）** | 用户白话训 Agent、开案例 | `docs/training/README.md`、`agents/residential/`、`projects/<case>/` | `feedback.md` 三步 pass；rules 反哺 |
| 表 C 硬证据债 | 新表 C writeback 被 hard audit / visual gate 阻断 | `docs/verification/table_c_evidence_gate.md` | 缺失报告、created handles、checks 或截图复盘债被机器审计通过 |
| CAD 画面能力 | 用户说“图块太简单”“推进 CAD 画面能力” | `VCAD-*` 小包 | AutoCAD 截图 + created handles 回读 + visual-only 边界清楚 |
| 真实 CAD 能力扩展 | 需要扩充 block、hatch、symbol、drawing standard 真实回读样本 | `docs/planning/任务清单.md` §4 / §5 索引 | validate、dry-run、真实 CAD、定向 readback 均通过 |
| 项目样本闭环 | 用户给脱敏样本或要求真实项目切片 | `projects/` + verification runbook | 样本协议、benchmark、可选真实 CAD 证据闭环 |
| 多方案与确认 | 需要候选比较、人工确认、局部修改 | `core/proposal_engine` 相关 tests | 候选比较、确认 schema、确认后 CAD_PLAN 可复验 |
| 自动读图 / shell 识别 | 用户要求 DWG/PDF 只读识别 | drawing-read 后置包 | 只读 summary、shell candidates、人工确认文件，未确认不得落 CAD |
| 场景 Agent Beta | 要把更多场景差异产品化 | `agents/<scenario>/` + scene benchmark | 至少复用同一 Core pipeline，不把算法塞进场景层 |
| 文档治理 | 默认上下文又变长、入口漂移或链接断裂 | `scripts/run_doc_governance_audit.py` | 活跃入口短、archive 可追溯、链接与表 C 不漂移 |

## 4. 后置包路由

包 ID、状态和阻塞项只在 **`docs/planning/post-backlog.md`** 维护；本文只保留方向入口，避免形成第二套状态。

| 方向 | 入口 | 说明 |
| --- | --- | --- |
| 真实 CAD 能力扩展 / CAD 画面 | `docs/planning/post-backlog.md`、`docs/verification/` | 只按台账当前状态开包 |
| 真实项目样本闭环 | `projects/sample_intake_template/`、`docs/runbooks/project-sample-intake.md` | 用户样本先走 intake |
| 多方案设计与交互确认 | `core/proposal_engine` tests | 用户确认后才能落 CAD_PLAN |
| 自动读图 / 空壳识别 | `docs/runbooks/drawing-read-user-gate.md` | 未确认不得落 CAD |
| 场景 Agent Beta | `agents/`、`docs/training/README.md` | 复用 Core pipeline |

历史 done 包的测试数、退出门槛和证据路径不在本文重复维护；查 `docs/planning/archive/README.md`。

## 5. Decision Gates

| Gate | 默认选择 | 需要用户确认的触发条件 |
| --- | --- | --- |
| G1 几何库 | 暂不引入成熟几何库 | clearance / 多边形算法明显变重 |
| G2 自动读图 | 先人工 JSON shell 闭环 | 用户要求真实 DWG/PDF 自动识别 |
| G3 首个真实业务场景 | 默认 office / commercial fitout 小切片 | 用户指定家装、餐饮、展陈等真实验收 |
| G4 真实块库 | 先受控测试块 | 用户提供公司块库且允许接入 |
| G5 proposal 自动转 CAD_PLAN | 默认需要用户确认 | 用户明确允许低风险自动落图 |
| G6 正式图层 / 保存 / 删除 | 默认禁止 | 用户逐项明确批准并有回滚方案 |

## 6. 执行入口

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_doc_governance_audit.py
& $py scripts\run_capability_coverage.py --output output\validation_runs\capability-lab\cad_capability_coverage.json
```

- 训练与案例 backlog：`docs/training/README.md`、`docs/planning/任务清单.md` §0。
- CAD 常识底座升级：`docs/training/cad-common-sense-upgrade.md`。
- CAD 资产智能架构包：`docs/architecture/cad-asset-intelligence-architecture.md`。
- CAD 常识资产开发计划：`docs/planning/cad-commonsense-asset-dev-plan-01.md`。
- 历史 Phase 剧本（勿当 next）：`docs/planning/HISTORY-ONLY.md`。
- CAD 卡壳 / 画不准：`docs/runbooks/blocker-playbook.md`。
- 真实 CAD 验证：`docs/runbooks/cad-validation.md`。
- 当前能力状态：`CORE_STATUS.md`。
- 近期流水：`docs/status/current.md` 与 `docs/status/changelog.md`。
- 交接包：`docs/handoffs/current.md`、`docs/handoffs/package-index.md`。

## 7. 完成判定

可以说某个小包完成，必须同时满足：

1. 目标测试 / benchmark / validator 已按本轮实际范围跑过。
2. 涉及真实 CAD 时有 `CODEX_PREVIEW`、created handles、readback、实体类型和几何检查。
3. 涉及表 C 时先过 evidence audit、visual review、table C gate，再 registry writeback 和 coverage 复跑。
4. 状态、changelog、必要 handoff 已同步；失败教训写入 `docs/status/issues.md`。
5. 最终汇报默认不用进度表；只在用户点名开发状态查询、进度、表 A/B/C、表 C 或真实 CAD 实力时展开表格，并先报表 C 主指标。

## 8. 历史与证据

| 需要 | 入口 |
| --- | --- |
| PlanMD 瘦身前全文 | `docs/history/snapshots/finished-architecture-2026-05-28/CORE_RESTRUCTURE_PLAN.md` |
| 任务清单瘦身前全文 | `docs/history/snapshots/finished-architecture-2026-05-28/docs__planning__任务清单.md` |
| V-PROOF / 代码轨 / RCAD done 索引 | `docs/planning/archive/` |
| 包交接全文 | `docs/handoffs/archive/2026-05.md`、`docs/handoffs/current.md` |
| 机器证据本体 | `output/validation_runs/**` |

历史文档可以保留旧百分比、旧 Phase 语义和旧路径，但当前表 C 只认 coverage JSON，当前 next 只认本文与任务清单。
