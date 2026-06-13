# 训练链路修订记录（持续更新）

本文件只记 **流程 / 审计 / 自检 / 产物约定** 类问题。单案例几何算法、坐标、裁切错误见 `docs/training/training-errors.md`，**不重复堆进链路**（除非暴露出审计门槛或工序缺失）。

主文档：`docs/training/README.md`「理想链路」。

| 日期 | 触发（你的 feedback / 对话） | 判因类型 | 链路缺口 | 修订动作 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 2026-06-09 | 用户指出当前基础训练测试速度极慢，并进一步纠正：训练和正式落图不应分成快 / 慢两条链路，提速应来自统一链路内的不合理调用粒度优化 | **链路 / 性能 / 调用粒度** | 先前把开发提速理解成跳过 post-sync、capture preview、artifact retention 等链路，这是错误方向；真正根因是 0-31 这类矩阵可能被拆成标题、外框、样线、文字逐图元 MCP/COM 调用，导致质量链路被“碎调用”拖慢 | 撤销 `dev_fast` 跳过链路口径，改为 `unified_optimized`：训练与正式共用一条质量链路，保留结构化计划、校验、CAD 写入、handles 回读和收尾证据；新增 item/batch 级提交粒度，`toolCallGranularity.minimumExternalSubmitUnit=foundation_item`、`preferredExternalSubmitUnit=foundation_batch`、`primitiveExternalCallsAllowed=false`；基础训练面板改为先 queue 操作再一次 item 级 batch 提交 | **已写入代码与规则；相关单测通过** |
| 2026-06-08 | 用户指出 0-31 基础训练矩阵空框、重叠；要求删除错误框后，Agent 误删大量原有内容；用户手动 `Ctrl+Z` 可恢复而 Agent 快捷键恢复不可靠 | **链路 / CAD 安全 / 修复策略** | 现有“原位局部修复优先”只说按 handles / bbox 限制，但没有禁止在无本轮 handles 时用大窗口删除 `CODEX_PREVIEW`；训练矩阵也缺少“每格必须有内容 + 不重叠视觉检查”；恢复链路误把 SendKeys `Ctrl+Z` 当作可依赖安全网 | 新增 CAD 基础测试矩阵安全规则：先做布局预案和一屏视觉检查；每格必须有图元内容；批量绘制不能用并行调用造成半成品；删除只能按本轮 created handles / 唯一 run layer / 用户确认范围，禁止用大窗口删除共享 `CODEX_PREVIEW`；Agent 发送 `Ctrl+Z` / `_OOPS` 只能作为一次性尝试，不能替代删除前证据 | **已写入规则链路** |
| 2026-06-02 | 用户指出回测校验可以发现问号乱码等局部错误，但不应每次在旁边重新画完整测试内容；已开放删除编辑命令，要求错哪修哪 | **链路 / 修复策略 / 安全边界** | 旧流程强调不盲画和停放区，但没有明确“局部错误优先原位编辑 / 删除替换”，导致 Agent 容易用旁边整套重画绕开局部修复；删除权限也缺少 handles / bbox 范围限制 | 新增“原位局部修复优先”：反馈 fail 后先读 `execution_summary` / created handles / CAD readback，生成 `repair_plan`，只对 `target_handles` / `target_bbox` 执行 `update`、`delete_replace` 或 `add_missing`；删除默认仅限 `CODEX_PREVIEW` 中被证据锁定的错误对象；handles 失效或全局布局根因时才允许整块重画 | **已写入规则链路** |
| 2026-06-02 | 用户指出线宽线型颜色是 CAD 基础且高频，家具图块和完整家装方案需要多层线条语义，不应只有三条测试线 | **链路 / 契约 / 审计** | 线宽线型复训只证明样板线属性回读，没有把墙体、家具外轮廓、家具内部细节、中心线、隐藏线、标注线等语义进入 `CAD_PLAN` 和 profile；也未区分属性验证、视觉可读和 plot 验证 | 新增 `cad-style-semantics` OpenSpec；`drawing_standard_profile` 增 style token，`CAD_PLAN.drawing` 增 `style_token/style_resolution`，dry-run / execution summary 增 `style_evidence`，glyph primitive 支持局部 style override；默认 `plot_verified=false` 并写明 CTB/STB、plot 和视口比例未检查 | **底座契约已落地；未做 plot 验证** |
| 2026-06-01 | 用户指出“画个正方体 + 填充”这类小动作理论上几秒即可，但实际被套入大量训练工序，要求增加全量化执行约定 | **链路 / 口令 / 节流** | 缺少轻量动作与正式训练验收之间的量化路由，Agent 容易把 quick CAD 试画、focused 复训和 formal acceptance 混成同一条重链路 | 新增 `quick_trial` / `focused_retraining` / `formal_acceptance` 三档：≤2 分钟快试、≤8 分钟 focused 复训、完整验收链路；明确触发词、必跑证据、可跳过项、升级条件和“快试未沉淀”汇报口径 | **已写入规则链路** |
| 2026-06-01 | 用户指出未来会临场组合已有能力，例如截图沙发 + 尺寸标注，但不希望把所有组合写进训练计划 | **链路 / 规则** | 训练地图列原子能力，但缺少未列入计划的复合任务路由；截图推断、比例估算、DWG / handles 回读的证据边界也未集中声明 | 新增复合任务动态编排规则：拆能力节点、声明 `evidence_source`、走 `CAD_PLAN` / validate / dry-run / readback / audit；单次组合不污染 V2 训练地图，重复失败或可机器检查时才晋升训练项 / 检查器 | **已写入规则链路** |
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
