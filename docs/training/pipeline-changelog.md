# 训练链路修订记录（持续更新）

本文件只记 **流程 / 审计 / 自检 / 产物约定** 类问题。单案例几何算法、坐标、裁切错误见根目录 `TRAINING_ERRORS.md`，**不重复堆进链路**（除非暴露出审计门槛或工序缺失）。

主文档：`docs/training/README.md`「理想链路」。

| 日期 | 触发（你的 feedback / 对话） | 判因类型 | 链路缺口 | 修订动作 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 2026-05-28 | 沙发 round1：少线、多轮截图一样、认为 Agent 未思考 | **链路** | 缺「截图后 Agent 自检」；审计未过仍可请你验收；审计项只有线数+底边 | 在 `README.md` 增「理想链路」；checklist 拆出审计→截图→自检；禁止审计红灯请你验收 | **已写入文档** |
| 2026-05-28 | 同上：机器审计绿灯但图仍错 | **链路** | 几何审计与 brief 语义脱节（未查中缝竖线、靠背分区） | `expected/audit_checklist.json`；全局禁止「仅总线数+底边」 | **round2 已实施** |
| 2026-05-28 | 要求整理全局理想链路、非单任务 | **链路** | 训练 SOP 散落在对话 | `README.md` 标明全局训练期；`AGENTS.md` 训练例外引用理想链路 | **已写入** |
| 2026-05-28 | feedback 后要能记录你指出的错因并优化链路 | **链路** | 无统一「用户指因 → 修复步骤 → 是否改链路」表 | 本文件 + `feedback.md` §错因与修复 + `记反馈` 口令 | **本次新增** |
| 2026-05-28 | 审计过关但靠背空、中缝无竖线（Agent 自检应发现） | **链路** | 自检未对照 brief 语义；审计门槛缺失 | 禁止仅「线数+底边」；自检必写 `agent_review` | **round2 已修** |
| 2026-05-28 | 用户：训练应沉淀全局规则；能否加全局多 Agent | **链路** | 三角角色未注册；审计/落图混在同 Agent | `training_geometry_audit` + `agents/pipeline/*` + `global-agent-pipeline.md` | **Phase A 已注册** |

## 判因类型（Agent 必填）

| 类型 | 含义 | 写哪里 |
| --- | --- | --- |
| **链路** | 工序顺序、审计项、自检、截图、产物、口令 | 本文件 + `docs/training/README.md`（必要时） |
| **几何/算法** | 裁切、坐标、块解析、座数逻辑 | `TRAINING_ERRORS.md` + `agents/<scene>/rules.md` + case `runs/` |
| **环境** | CAD 未开、截图被挡、COM 失败 | `TRAINING_ERRORS.md` + `blocker-playbook.md` |
| **需求** | brief 不清、理解偏了 | 案例 `feedback.md` §理解 + 澄清 brief |

**规则：** 只有判为 **链路** 时才改 `README` / 本 changelog；几何类 **不要** 为了凑数改理想链路图。

## 下一轮链路待办（ backlog ）

- [x] 模板 `intent.template.json` + `audit_checklist.template.json` + `audit_review.template.md`
- [ ] `scripts/` 或 runs 内统一 `write_round_agent_review.py`（可选，非必须）
