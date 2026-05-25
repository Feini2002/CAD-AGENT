# Multi-Agent Contribution Contract

状态：Phase R 协作协议已建立  
最后同步：2026-05-26

> 本文用于多个 Codex / sub-agent 并行参与 CAD Agent Core Lab 时保持边界清楚。它不是替代 `AGENTS.md` 的规则，也不是独立 PlanMD；冲突时以用户最新指令、仓库规则和 `CORE_RESTRUCTURE_PLAN.md` 的当前主线为准。

## 角色与可写边界

| 角色 | 可写边界 | 交付物 |
| --- | --- | --- |
| Phase 负责人 | 当前目标 `docs/planning/phase-*.md`、状态文档同步；调整优先级时必须同步 `CORE_RESTRUCTURE_PLAN.md` | Phase 总表、任务状态、同步清单 |
| CAD 能力契约 agent | Phase W / Phase R 相关计划、验证文档；代码实现需另开任务 | 实体契约、证据门禁、deferred verification |
| 图块 / 制图标准 agent | `libraries/` 与 block/style 设计文档；代码实现需 disjoint write set | BLOCK_LIBRARY 字段、受控测试块、drawing standard profile |
| 办公场景 agent | `agents/office` 偏好、examples / benchmark 计划 | 办公对象集、微场景、失败样本 |
| Benchmark agent | `examples/benchmarks`、verification 计划、runner 断言设计 | 三层 benchmark、证据状态命名、报告字段 |
| 文档同步 agent | `CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md` | 短结论、能力状态、历史流水 |
| Reviewer agent | 只读，除非明确分配修复任务 | 发现列表、边界风险、测试缺口 |

## 不可越界

- 场景 Agent 不得实现碰撞检测、通道生成、多边形 / 净空算法、CAD_PLAN 校验、执行、截图或回读。
- 真实块库路径、块名映射、属性规则不得写入 `agents/<scenario>`。
- CAD 执行、readback 和 verification 不得写入 benchmark summary 或 screenshot 工具里。
- 不得把 `benchmark_pass_non_cad`、dry-run 或截图说成几何准确。
- 不得默认保存、覆盖、删除 DWG 或修改正式图层。

## 审查门禁

修改前先判断归属：

| 内容 | 应去哪里 |
| --- | --- |
| 通用算法、schema、CAD_PLAN、执行、验证 | `core/` |
| 跨场景资源、对象、块、样式、尺寸、图层标准 | `libraries/` |
| 场景词汇、偏好、解释模板、排序权重 | `agents/<scenario>/` |
| 可提交样例和 benchmark | `examples/` |
| 真实或样例项目资料 | `projects/` |
| 计划、架构、治理、review | `docs/` |
| 历史流水 | `CAD_AGENT_CHANGELOG.md` |
| 失败、风险、教训 | `CAD_AGENT_ISSUES.md` |

几何准确声明必须满足：

1. 有预期对象、尺寸、基点、图层、文字、标注和允许误差。
2. `validate_plan.py` 和 `dry_run_plan.py` 通过。
3. 真实 CAD 写入到 `CODEX_PREVIEW`。
4. 真实 CAD readback 按 created handles 定向回读。
5. 报告为 `readback_geometry_verified`，关键 checks 全部通过。

## 冲突处理

优先级：

```text
用户最新明确指令
> AGENTS.md / 仓库规则
> CORE_RESTRUCTURE_PLAN.md
> 当前 Phase 文档
> agent 建议
> 个人判断
```

如果仍有冲突：

- 不静默覆盖别的 agent 或用户已有改动。
- 先把冲突登记为 Decision Gate。
- 对可继续的无冲突任务先推进。
- 需要真实 CAD、真实块库、正式图层或新依赖时停止并请求确认。

## 场景发现升级为 Core 能力

| 步骤 | 要求 |
| --- | --- |
| 1. 记录场景发现 | 写清场景、对象、约束、失败模式 |
| 2. 判断是否跨场景复用 | 两个以上场景会用，进入 Core / libraries 设计 |
| 3. 定义最小 schema 或 metadata | 先 metadata / benchmark，后实现 |
| 4. 增加非 CAD benchmark | 先证明输入、输出、失败原因可复验 |
| 5. 真实 CAD 补验 | 需要落图准确时再进入 Phase W / CAD validation |
| 6. 同步状态 | 更新主计划、短入口、能力矩阵和 changelog |

## 每轮收尾

- 运行适合本轮的验证；文档轮至少跑引用、占位词和边界扫描。
- 同步 `CORE_CONTEXT_BRIEF.md`、唯一 PlanMD `CORE_RESTRUCTURE_PLAN.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md`。
- 若出现失败、回归或环境教训，更新 `CAD_AGENT_ISSUES.md`。
- 最终回复说明改了什么、验证了什么、没有验证什么。
