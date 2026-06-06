# CAD Agent 架构归并画布

最后更新：2026-06-06

本文是仓库级架构归并说明。它只回答“系统各部分属于哪一层、如何流转、不能越过什么边界”；不替代唯一 PlanMD：`CORE_RESTRUCTURE_PLAN.md`，也不承载执行台账。具体 next 仍看 `CORE_RESTRUCTURE_PLAN.md` 与 `docs/planning/任务清单.md`。

## 1. 归并目标

当前仓库已经有 `CAD_PLAN`、validate / dry-run、真实 CAD readback、A-to-A、资产库、训练地图、模型型 Agent、Worker / bridge、截图和证据治理。问题不是材料不够，而是材料曾按探索顺序分片生长，旧表 A/B/C、能力证明、RCAD、训练、资产、模型桥和工作台容易并列成多张画布。

本轮归并的目标是把它们收束到同一个任务生命周期里：

```text
系统入口 -> 任务对象 -> 决策编排 -> 能力与证据
  -> 执行工具 -> 审计修复 -> 沉淀成长
```

每个新增模块、脚本、状态页和训练入口，都必须能说明自己属于哪一层、输入是什么、输出给谁、不能替代哪一层。

## 2. 七层生命周期

| 层 | 责任 | 典型对象 | 禁止越权 |
| --- | --- | --- | --- |
| 1. 系统入口 | 接收用户意图和外部上下文 | 白话、DWG、截图、反馈、训练口令、资产口令 | 不直接落 CAD，不直接写训练事实源 |
| 2. 任务对象 | 把请求变成可追踪对象 | run package、task envelope、case、training item、asset / repair request | 不把同一句口令同时当训练、资产和交付完成 |
| 3. 决策编排 | 分流、派发、状态机、模型触发 | semantic route、Orchestrator Host、A-to-A contract、Worker、bridge、GPT-5.5 | 不替代 CAD evidence，不替代用户授权 |
| 4. 能力与证据 | 查询历史 proof、事实源和风险边界 | registry、表 A/B/C 历史口径、training sources、asset evidence、coverage JSON | 不把覆盖率数字当真实任务成熟度 |
| 5. 执行工具 | 确定性执行、校验和回读 | `CAD_PLAN`、validate、dry-run、Tool Contract、`CODEX_PREVIEW`、readback、screenshot | 不接受模型直接执行、保存、删除或改正式图层 |
| 6. 审计修复 | 判断结果是否可交付、是否需局部修 | geometry audit、visual review、local repair、closeout gate、neighbor protection | 不用截图替代 handles / readback |
| 7. 沉淀成长 | 把稳定经验写回规则、训练、资产或历史 | learning promotion、Agent memory、rule delta、system asset、workbench、changelog | 不把 quick trial 或一次性截图沉淀成 verified |

## 3. 旧模块归位

| 旧模块 / 概念 | 新归属 | 新含义 |
| --- | --- | --- |
| 表 A 工程节奏 | 能力与证据层 | 历史工程节奏快照，只在完整状态审计中引用 |
| 表 B 任务台账 | 能力与证据层 + 沉淀成长层 | 历史施工包完成索引，不代表当前训练能力 |
| 表 C / 旧称“真实 CAD 实力” | 能力与证据层 | 改为 `Core Proof Coverage`，即底座证据覆盖 |
| `cad_capability_registry` | 能力与证据层 | 原子能力和历史证据数据库 |
| CAD Designer Agent | 系统入口 + 决策编排 + 沉淀成长 | 未来主训练主体和任务人格，不是外挂训练文档 |
| V2 训练地图 | 任务对象 + 沉淀成长 | 训练任务生成器，不是能力成绩单 |
| `CAD_PLAN` / validate / dry-run | 执行工具层 | 所有 CAD 写入的执行脊柱 |
| A-to-A / Orchestrator | 决策编排层 | 分发责任和 hard gate，不替代执行证据 |
| GPT-5.5 / 模型桥 | 决策编排层 | 只读判断、复审、建议和工具请求 |
| Worker 编排 | 决策编排层 | 远程触发、状态机、队列、heartbeat 和结果回传 |
| 系统资产库 | 沉淀成长 + 能力与证据 | 可复用成果库；verified 必须有 sourceSpec / native evidence / reuse replay |
| 截图 | 执行工具 + 审计修复 | `visual_aid_only`，不能证明几何准确 |
| 工作台 HTML | 沉淀成长 | 派生显示器，不是事实源 |

## 4. 三个成熟度口径

旧指标的最大问题不是数字，而是语义位置错误。后续状态查询和训练恢复必须分开三层：

| 口径 | 说明 | 当前判断 |
| --- | --- | --- |
| `Core Proof Coverage` | 底座原子能力、registry、showcase 和历史 evidence 覆盖；来自 coverage JSON | 较高，只证明底层零件不是空的 |
| `Agent Task Maturity` | CAD Designer Agent 端到端任务成熟度：理解、执行、审计、修复、反馈闭环 | 早期，需要靠案例训练和用户 feedback 建立 |
| `Project Delivery Readiness` | 真实项目 / 完整施工图交付准备度 | 更早期，不能由表 C、RCAD、截图、dry-run 或 no-CAD benchmark 推导 |

`Core Proof Coverage` 可以继续机器计算并保留旧 JSON 字段；用户可见文案必须明确它只是能力与证据层指标，不代表 `Agent Task Maturity` 或 `Project Delivery Readiness`。

## 5. 当前执行边界

架构归并完成前，默认暂缓：

- 新一轮正式对象训练。
- 整批训练和表 C 推进。
- 系统资产大沉淀或仓库级清理。
- 把旧“真实 CAD 实力 90%”继续当真实能力宣传。

允许执行：

- 文档、规则、状态、OpenSpec 契约和 PlanMD 同步。
- 小范围脚本审计和 label / gate 兼容改造。
- 只读或派生型验证：OpenSpec validate、doc governance、PlanMD governance、工作台 Agent check。
- 必要的最小测试，阻止旧口径回流。

用户明确覆盖暂停时，仍可按原 quick / focused / formal 边界执行，但必须保留 `CAD_PLAN`、validate / dry-run、`CODEX_PREVIEW`、created handles readback、sourceSpec、no-save 和 evidence boundary。

## 6. 恢复训练条件

恢复正式训练前，至少确认：

1. `CORE_RESTRUCTURE_PLAN.md` 仍是唯一 PlanMD，OpenSpec 只做变更契约。
2. 训练入口、状态页、规则、工作台和关键脚本都使用 `Core Proof Coverage` / `Agent Task Maturity` / `Project Delivery Readiness` 三口径。
3. coverage JSON 字段保持机器兼容，但 UI / 文档不再把旧表 C 说成端到端能力。
4. A-to-A 和仓库级治理任务具备 `system_architecture_canvas` 或等价 hard gate。
5. 工作台仍是派生显示器，不是训练事实源。

满足这些条件后，再恢复对象训练和案例训练；训练结果仍必须靠真实 CAD readback、审计、局部修复闭环、用户反馈和可复用资产 replay 逐步建立。
