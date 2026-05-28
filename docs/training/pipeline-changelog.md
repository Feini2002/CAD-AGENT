# 训练链路修订记录（持续更新）

本文件只记 **流程 / 审计 / 自检 / 产物约定** 类问题。单案例几何算法、坐标、裁切错误见 `docs/training/training-errors.md`，**不重复堆进链路**（除非暴露出审计门槛或工序缺失）。

主文档：`docs/training/README.md`「理想链路」。

| 日期 | 触发（你的 feedback / 对话） | 判因类型 | 链路缺口 | 修订动作 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 2026-05-28 | 用户要求前五项资产智能计划一起落地，但排除测试 | **链路 / 架构** | 架构包已有，但目录、检索包、Agent 资产检索、intake 模板和晋升 gate 还只是计划 | 新增资产目录、schema、`core.assets` 检索 / 晋升入口、`pipeline_asset_retriever`、训练 intake 模板和 CLI 脚本 | **基础版已落地；未写测试 / 未跑测试** |
| 2026-05-28 | 用户要求从参考图库 / 自产图库 / RAG / 训练晋升角度重构架构，并担心图库限制创造性 | **链路 / 架构** | 仅“查 catalog”不足以约束后续生成；缺 reference_library 与 system_library 边界；图库弱命中时容易在“套旧模板”和“凭空画线”之间摇摆 | 新增 `docs/architecture/cad-asset-intelligence-architecture.md`；README 和 global pipeline 增 `retrieval_pack`、route、生产 / 探索模式、Agent 资产检索职责和晋升生命周期 | **架构包已写入；落地待后续小包** |
| 2026-05-28 | 用户要求把 llm-wiki、step.parts、CADTestBench、CADCLAW 方法论吸收为 CAD 常识底座，并优化训练反馈文本 | **链路** | 基础常识散在案例和对话；资料放入仓库容易被误认为“已学会”；交付汇报只堆机器数字，用户难判断看哪里 | 新增 `cad-common-sense-upgrade.md`；README 增 Step0 查常识 / catalog；learning loop 增常识层；交付汇报改为“结论、变化、checked/not_checked、重点看点、反馈入口” | **已写入文档** |
| 2026-05-28 | 沙发 round1：少线、多轮截图一样、认为 Agent 未思考 | **链路** | 缺「截图后 Agent 自检」；审计未过仍可请你验收；审计项只有线数+底边 | 在 `README.md` 增「理想链路」；checklist 拆出审计→截图→自检；禁止审计红灯请你验收 | **已写入文档** |
| 2026-05-28 | 同上：机器审计绿灯但图仍错 | **链路** | 几何审计与 brief 语义脱节（未查中缝竖线、靠背分区） | `expected/audit_checklist.json`；全局禁止「仅总线数+底边」 | **round2 已实施** |
| 2026-05-28 | 要求整理全局理想链路、非单任务 | **链路** | 训练 SOP 散落在对话 | `README.md` 标明全局训练期；`AGENTS.md` 训练例外引用理想链路 | **已写入** |
| 2026-05-28 | feedback 后要能记录你指出的错因并优化链路 | **链路** | 无统一「用户指因 → 修复步骤 → 是否改链路」表 | 本文件 + `feedback.md` §错因与修复 + `记反馈` 口令 | **本次新增** |
| 2026-05-28 | 审计过关但靠背空、中缝无竖线（Agent 自检应发现） | **链路** | 自检未对照 brief 语义；审计门槛缺失 | 禁止仅「线数+底边」；自检必写 `agent_review` | **round2 已修** |
| 2026-05-28 | 用户：训练应沉淀全局规则；能否加全局多 Agent | **链路** | 三角角色未注册；审计/落图混在同 Agent | `training_geometry_audit` + `agents/pipeline/*` + `global-agent-pipeline.md` | **Phase A 已注册** |
| 2026-05-28 | 沙发 round12：衔接仍错；参考有弧线且更丝滑，生成全靠圆角矩形且有重叠/间隙 | **链路** | Visual-First 契约只声明部件存在，未约束弧线丰富度、装配拓扑、gap/overlap；审计读取 reference profile 但缺少 `reference_profile_match` 阻断项；Agent 自检未对照用户标注区域 | round13 前补 reference profile、部件衔接和形态丰富度硬门槛；生成从独立圆角矩形改为带装配节点的语义重绘 | **待修复** |
| 2026-05-28 | 沙发 round13：用户认可部件衔接靠在一起，但指出中间白线与沙发方向语义反了 | **链路** | 视觉契约没有 `visual_semantics`，Agent 不知道低 Y 是硬靠背、中间是软靠垫、高 Y 是坐垫；执行层重复输出共享边导致亮线/白线；旧 reference split ratio 带着反向语义假设 | Visual Intent 必填沙发 `layer_order_back_to_front`；Audit 新增 `sofa_direction_semantics_inverted`，语义层接管时不再用旧 split ratio 阻断；Execute 去重完全重复线段；Repair 优先处理常识方向错误 | **已写入并重画 round14** |

## 判因类型（Agent 必填）

| 类型 | 含义 | 写哪里 |
| --- | --- | --- |
| **链路** | 工序顺序、审计项、自检、截图、产物、口令 | 本文件 + `docs/training/README.md`（必要时） |
| **几何/算法** | 裁切、坐标、块解析、座数逻辑 | `docs/training/training-errors.md` + `agents/<scene>/rules.md` + case `runs/` |
| **环境** | CAD 未开、截图被挡、COM 失败 | `docs/training/training-errors.md` + `blocker-playbook.md` |
| **需求** | brief 不清、理解偏了 | 案例 `feedback.md` §理解 + 澄清 brief |

**规则：** 只有判为 **链路** 时才改 `README` / 本 changelog；几何类 **不要** 为了凑数改理想链路图。

## 下一轮链路待办（ backlog ）

- [x] 模板 `intent.template.json` + `audit_checklist.template.json` + `audit_review.template.md`
- [ ] `scripts/` 或 runs 内统一 `write_round_agent_review.py`（可选，非必须）
