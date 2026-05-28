# 变聪明逻辑（Learning Loop）

最后更新：2026-05-28

## 一句话

**不是 round20 结束时一次性「灌给 Agent」；而是每一轮 fail 就记账，可复用的教训按规则晋升到全局，下一个案例/下一轮会话自动读到。**

变聪明 = **结构化记忆变厚 + 机器门槛变严 + 链路少跳步 + 常识可查可测 + 资产可检索可晋升**，不是模型神秘变强。

---

## 触发条件（什么时候算「变聪明了一次」）

| 触发事件 | 谁触发 | 立刻写什么 | 是否变「全局」 |
| --- | --- | --- | --- |
| 每轮 **你 fail** 或 Agent 自检 fail | 你 / Audit / Delivery | `feedback.md` §几何 + §根因 | 否（案例内） |
| 同类错误 **第 2 次**（本案或下一案例） | Repair / 你 | `docs/training/training-errors.md` 一行 | 待定 |
| 错误属 **链路**（审计漏项、跳过 intent、误请你验收） | Agent 判因 | `pipeline-changelog.md` | **是** |
| 错误属 **可复现反模式**（schematic 网格、clone 碎线） | Audit 发现 | Core 新探针 / `forbidden_patterns` | **是** |
| 错误属 **场景词汇**（参照≠clone、家装口径） | Intent / 你 | `agents/<scene>/rules.md` | 场景级 |
| 错误属 **本案尺寸/对象** | Intent | `audit_checklist.json` | 仅本案 |
| **你 pass，案例 done** | 你 | `feedback.md` 结论 + 可选 `rules.md` 摘要 | 场景级摘要 |

**没有触发上述写入 = 没有变聪明**，只是聊天里说过一遍（下一会话可能忘）。

---

## round1～round20 期间发生什么（以沙发案例为例）

```text
Round N fail
  ├─ feedback.md        追加一行：你判什么、不准点、证据路径
  ├─ training-errors    追加一行：现象/根因/修复/状态
  ├─ geometry_audit.json  机器可读 failures（下轮 Repair 输入）
  ├─ audit_review.md    Agent 目视：为何不能请你验收
  └─ 若链路问题 → pipeline-changelog.md

Round N+1 开始
  ├─ Orchestrator 读 feedback + 最近 audit + intent
  ├─ Intent  是否改 intent / checklist
  ├─ Execute 改 runs 或 CAD_PLAN
  ├─ Audit   同一 checklist，可能已加厚
  └─ 禁止：无视上轮 failures 重画同样错图

Round 20 你 pass
  ├─ feedback.md 标 done
  ├─ 可选：把本案教训摘要进 agents/residential/rules.md（3～5 条策略，非 20 轮流水账）
  └─ 已晋升 Core 的探针留在 core/，下案例自动生效
```

**不会做的（当前）：** 把 round1～20 的 PNG/JSON 整包「训练进模型权重」；当前交互式 Agent 靠 **读文档 + 读 artifacts** 变聪明，工具载体不绑定单一软件。

---

## 三层记忆（写在哪 = 谁能用到）

| 层级 | 文件 / 代码 | 记住什么 | 下案例能用吗 |
| --- | --- | --- | --- |
| **案例** | `feedback.md`、`runs/`、`audit_checklist.json` | 本轮几何、阈值、脚本 | 仅本案 |
| **常识 / 资产** | `libraries/objects/`、`libraries/blocks/`、`libraries/knowledge/`；后续按资产智能架构拆 `reference_library` / `system_library` / `benchmarks` | 基础对象部件、图库来源、标准表达、禁止退化、自产对象族和晋升证据 | 同类对象可用 |
| **场景** | `agents/residential/rules.md`、`preferences.json` | 白话口径、参照≠clone | 同场景案例 |
| **全局** | `core/verification/*`、`pipeline-changelog`、`agents/pipeline/*`、`precision-first.md` | 探针、禁止项、工序 | **所有案例** |

晋升方向（只允许向上）：

```text
资料 / 图库 / 外部方法论
    ↓ 编译成常识摘要，不直接变规则
reference_only
    ↓ 结构化为对象语法 / 参数 / 审计项
candidate
    ↓ 单案例 CAD 证据 + 用户反馈
case_verified
    ↓ 多变体 / 负例 / benchmark
system_verified
    ↓ 成为可检索自产资产
retrieval_pack 上游契约
```

规则继续向上晋升：

```text
对象常识候选
    ↓ 有第二个案例或 benchmark 需要
可执行审计 / benchmark
    ↓ 机器可证明
案例 checklist 阈值
    ↓ 第二个案例也需要
Core 探针（training_geometry_audit）
    ↓ 影响所有 Agent 工序
pipeline 禁止项 / Agent must_not
    ↓ 案例 done 后摘要
agents/<scene>/rules.md（策略，不是数值）
```

**禁止向下污染：** 不把 `1867mm`、`0.821` 写进 Core；不把 COM 写进 `agents/`。

**禁止假学习：** 不把图库、PDF、网页或截图直接丢进根目录就声称系统学会；必须形成 `source_note → knowledge_summary → object_or_rule_candidate → executable_check → evidence_boundary`，详见 `cad-common-sense-upgrade.md`。外部参考还必须和自产资产分层，详见 `docs/architecture/cad-asset-intelligence-architecture.md`。

---

## 各 Agent「变聪明」具体指什么

| Agent | 变聪明 = | 输入从哪来 |
| --- | --- | --- |
| **Intent** | 更少 open_questions；checklist 一次写对 | 你白话、`rules.md`、上轮 §理解 fail |
| **Asset Retriever / Context** | 更少凭空画；能说明 strong / weak / none 命中和证据边界 | `libraries/`、`knowledge`、`benchmarks`、case 历史 |
| **Execute** | 少犯已记录几何错误 | `training-errors.md`、case runs、intent |
| **Audit** | 少漏检、少误绿 | Core 探针增多、checklist 加厚、对象常识测试 |
| **Repair** | 对症而非补丁 | `audit_failures`、feedback §根因 |
| **Delivery** | 少请你验收错图；汇报能让用户判断下一步 | `precision-first`、audit_review 模板、低噪声反馈模板 |
| **Orchestrator** | 少跳步 | `pipeline-changelog`、manifest、常识来源状态 |

**不是：** 每个 Agent 单独训练一个大模型。

---

## round20 验收时会不会「整体交给 Agent」？

**会，但是结构化交付，不是原始 dump。**

案例 done 时应有一份 **晋升摘要**（Agent 写，你可审）：

| 条目 | 内容 |
| --- | --- |
| 本案轮次 | 20 轮；pass 于 round20 |
| 全局已晋升 | 如 `forbidden_schematic_equal_grid`、全局 audit 引擎、preserve_layout 截图 |
| 场景已晋升 | 如 `rules.md`：「产品块改座数 → 语义重绘，禁止 clone 碎线」 |
| 仅本案保留 | 如 `semantic_draw_helpers.py`、具体 checklist 数值 |
| 未解决 / 下案例待测 | 如「款式目视仍部分靠 Agent 自检」 |

**不会：** 把 20 张截图塞进一个 prompt 说「你学会了吗」——读不懂、不可回归、不可审计。

---

## 你怎么参与（口令）

| 你说 | 系统应变聪明的方式 |
| --- | --- |
| **记反馈** | 强制写 feedback + training-errors；链路则 changelog |
| **优化聪明度** / **校准 Agent** | 不只重画；必须找根因，判断是 Prompt / visual_parts / checklist / Core 探针 / scene rules 哪一层缺失，并把可复用教训写入相应层级 |
| **fail + 原因** | §根因 必填；Repair 下轮对症 |
| **pass / done** | 案例关闭；触发 rules 摘要（可选） |
| 第二个家装案例同类 fail | Agent 应提议 **Core 探针晋升**，不是再写 `sofa_*_audit.py` |

---

## 当前缺口（诚实）

| 已有 | 还没有 |
| --- | --- |
| 每轮 feedback / training-errors 约定 | 自动 `runs/state.json` 编排（Phase C） |
| 全局 audit 引擎 + 晋升规则文档 | 案例 done 时 **自动生成晋升摘要** 的脚本 |
| 6 Agent manifest | 各 Agent 独立 Skill 自动读 artifacts（Phase B） |

**变聪明逻辑已定义；自动化程度仍在 Phase A→B。**

---

## 相关文件

- 精度宪章：`precision-first.md`
- 审计晋升：`audit-architecture.md`
- 多 Agent：`global-agent-pipeline.md`
- 错因台账：`docs/training/training-errors.md`
