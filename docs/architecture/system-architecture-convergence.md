# CAD Agent 架构归并画布

最后更新：2026-06-07

本文是仓库级架构归并说明。它只回答“系统各部分属于哪一层、如何流转、不能越过什么边界”；不替代唯一 PlanMD：`CORE_RESTRUCTURE_PLAN.md`，也不承载执行台账。具体 next 仍看 `CORE_RESTRUCTURE_PLAN.md` 与 `docs/planning/任务清单.md`。

## 1. 归并目标

当前仓库已经有 `CAD_PLAN`、validate / dry-run、真实 CAD readback、A-to-A、资产库、训练地图、模型型 Agent、Worker / bridge、截图和证据治理。问题不是材料不够，而是材料曾按探索顺序分片生长，旧表 A/B/C、能力证明、RCAD、训练、资产、模型桥和工作台容易并列成多张画布。

本轮归并的目标是把它们收束到同一个任务生命周期里：

```text
系统入口 -> 任务对象 -> 决策编排 -> 能力与证据
  -> 执行工具 -> 审计修复 -> 沉淀成长
```

每个新增模块、脚本、状态页和训练入口，都必须能说明自己属于哪一层、输入是什么、输出给谁、不能替代哪一层。

本轮架构整理新增一个跨层判断：**主 Agent 认知证明**不是第八层，而是贯穿系统入口、决策编排、能力与证据、审计修复和沉淀成长的质量门。任何“主 Agent 变聪明”的声明，都必须说明历史经验如何改变了后续真实任务里的 route、dispatch、tool choice、blocking、requiredAgents、learningCandidate 或 replay 结果；否则只能称为机制建设，不能称为认知提升。

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
| 主 Agent 认知证明 | 决策编排 + 能力与证据 + 审计修复 + 沉淀成长 | 用 before / after 证明历史经验改变判断；不是表 C、不是 CAD 几何证据、不是“规则写多了”的自我安慰 |
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
6. 若训练目标涉及“让主 Agent 更聪明”，先完成可观察的 before / after 认知证明，而不是只写 memory、Prompt 或学习记录。

满足这些条件后，再恢复对象训练和案例训练；训练结果仍必须靠真实 CAD readback、审计、局部修复闭环、用户反馈和可复用资产 replay 逐步建立。

## 7. 给非架构读者的读法

可以把当前系统理解成一条有闸门的流水线，而不是一堆并列功能：

```text
想做什么
  -> 变成一个可追踪任务
  -> 决定谁负责、要过哪些门
  -> 查已有能力和风险
  -> 只让确定性工具执行
  -> 审计结果，不准就修
  -> 稳定后才沉淀为训练、资产或规则
```

这条线里最容易混淆的是三件事：

- **架构干净**：每个模块知道自己属于哪一层，不能替代别的层。
- **测试链可跑**：可以选一条小链路，用现有 gate、测试、审计和 artifact 验证它是否闭合。
- **正式训练 / 项目交付可恢复**：不仅能跑链路，还要有真实 CAD readback、用户反馈、修复闭环和沉淀规则。

所以，“架构归并完成”只表示系统的路标和闸门已经摆正；它不自动表示 CAD Designer Agent 已经成熟，也不表示可以直接进入真实项目交付。

## 8. 测试性链准入判断

当前架构已经可以进入**测试性链环节**，但建议从最小闭环开始，不要直接恢复整批正式训练。

测试性链的准入条件如下：

| 检查项 | 当前要求 | 不满足时的处理 |
| --- | --- | --- |
| 工作区状态 | Git 工作区干净，当前分支明确 | 先停止测试，清理或提交基线 |
| 主计划 | `CORE_RESTRUCTURE_PLAN.md` 仍是唯一 PlanMD | 先修文档治理，避免第二套 next |
| 变更契约 | OpenSpec 作为 change contract，不能当主 backlog | 先更新 OpenSpec / PlanMD 边界 |
| 任务链 | 测试任务能归入七层生命周期 | 先补任务对象和责任分发 |
| A-to-A | 高风险链路有 required agents 和 hard gates | 缺 gate 时只能 blocked |
| 执行证据 | CAD 链路必须有 validate / dry-run / readback 边界 | 只能跑 no-CAD 或 blocked 预检 |
| 沉淀边界 | quick / test output 不写训练事实源 | 只保留为 derived / diagnostic |

建议下一步选择**一条测试性链**，而不是同时开训练、资产、模型桥和真实 CAD：

1. **首选：仓库级无 CAD 测试链**  
   目标是验证架构 gate 是否稳：OpenSpec validate、doc governance、PlanMD governance、A-to-A gate、workbench agent check。它证明系统路标干净，不证明真实 CAD 几何。

2. **次选：模型型 Agent no-CAD 链**  
   目标是验证模型桥 / Prompt Pack / trace / closeout gate / tool intent 的证据传递。`prove-main-agent-cognition-loop` 已补 no-CAD 认知闭环：工具 trace 可回喂同一 Agent，run result 写 `cognitiveLoopSummary`，并把行为改变证明、evidence portfolio、`selfUncertainty` 和 route budget 纳入机器测试。它证明判断链和机制边界可审计，不证明 CAD 输出。

3. **再选：单项真实 CAD preview 链**  
   目标是只写 `CODEX_PREVIEW`，验证同一 `CAD_PLAN` 的 validate、dry-run、execute、created handles readback、closeout gate。它证明单项执行链，不证明整批训练或项目交付。

若下一步做家具测试，推荐把它定义为**家具 focused rehearsal**，而不是正式整批训练。默认只选一个家具族或一个点名能力，先验证主 Agent 是否正确分流、读取历史 profile、选择 quick / focused / formal、派发必要 Agent、阻断越权完成；真实 CAD 可用时再进入 `CODEX_PREVIEW` + handles readback。只有这条小链闭合，才把结果追加为训练证据或继续扩大到对象课程。

### 8.1 当前残项裁决

| 残项 | 是否阻断下一步 | 裁决 |
| --- | --- | --- |
| 真实 AutoCAD 当前未连接 | 不阻断无 CAD 仓库治理链；阻断单项真实 CAD preview 链和正式训练恢复 | 先跑 no-CAD 测试链；进入真实 CAD preview 前再重连 AutoCAD 并跑 created handles readback |
| 工作台 flightdeck 还有观察视图 follow-up | 不阻断测试性链 | 作为可视化润色 / 观察性改进排期，不当作主训练链 hard gate |
| 工作区存在未提交变化 | 阻断任何新测试链 | 先提交或清理成干净基线；只有 `git status` 干净后再开始测试 |
| 架构还想继续补满 | 默认不阻断 | 除非发现第二套 PlanMD、缺 hard gate、证据边界无法分类，否则先用测试链暴露真实缺口 |

## 9. 仍需补满的架构缺口

当前系统不是“空架构”，但还没有到“所有大链路都可正式恢复”的状态。剩余缺口主要是三类：

| 缺口 | 为什么重要 | 建议处理 |
| --- | --- | --- |
| 测试链分层记录还不够集中 | 现在证据分散在 tests、scripts、output 和状态文档里，外行很难一眼判断该跑哪条链 | 新增或整理一份 `testing-chain-readiness` 小文档 / 报告入口 |
| 主 Agent 认知证明仍需真实任务续证 | no-CAD fixture 已证明工具结果可进入同一 Agent 二轮修正，并能记录 before / after 行为改变边界；但真实用户任务里历史经验是否稳定改变 route / dispatch / blocking / replay 仍需后续案例 | 下一步若做家具测试，使用 focused rehearsal 验证真实任务 route / scope / memory 命中与阻断是否因历史经验改变 |
| 正式训练恢复门槛还需要一次实跑证明 | 文档已经说明训练暂停和恢复条件，但还缺“从测试性链到 focused training”的桥接样例 | 先跑一个 focused、单项、可回读的训练恢复 rehearsal |
| 真实 CAD project readiness 仍缺端到端案例 | 表 C、基础训练、对象 replay 都不是完整施工图交付 | 后续用一个小 DWG 案例建立端到端任务成熟度证据 |

因此当前判断是：**可以进入下一步测试性链；不建议直接进入正式整批训练或真实项目交付。**
