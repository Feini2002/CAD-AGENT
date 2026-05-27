# 能力证明体系（Capability Proof）架构说明

最后更新：2026-05-26

本文是 **Phase V / 路线 F** 的架构说明；**任务包与执行顺序**以 [`任务清单.md`](任务清单.md) §3 为准。主计划登记见 `CORE_RESTRUCTURE_PLAN.md`「路线 F」。

## 为什么要单独建体系

- 仓库 **工程完备度**（schema、runner、场景壳层）与 **CAD 几何证明覆盖率** 不是同一指标。
- 现有 RCAD / manifest 属于 **烟囱补验**；无法回答「能画多厉害的图块、展现多强能力」。
- 能力证明体系把每个可声称能力登记为一行，并绑定 **claim_level**、**cad_case**、**Ladder 等级**。

## 四层证明模型

| 层 | 名称 | 证明什么 | 主要产物 |
| --- | --- | --- | --- |
| **P0** | 契约与门禁 | validate、负向、证据词表、不误报 pass | pytest + no-CAD |
| **P1** | Capability Lab | 每个 intent/对象/符号/块有最小 CAD case 或 explicit deferred | `cad_capability_registry` + Lab 报告 |
| **P2** | Capability Ladder | 对外「多厉害」的分级展示 | `docs/verification/capability_showcase/` |
| **P3** | 项目回归集 | 多样本、趋势、稳定性 | project manifest + `evidence_trend` |

**路线 E（CAD-MCP / RCAD）** 是 P1 的**执行手段**，不是整套体系的全部。

## Capability Ladder（展示等级）

| 等级 | 名称 | 含义 |
| --- | --- | --- |
| **L0** | 结构可生成 | validate + dry-run；可无真实 CAD |
| **L1** | 几何可落图 | 真实 CAD readback；单点 smoke |
| **L2** | 符号可读 | `symbol_readable` + glyph readback |
| **L3** | 场景片段 | 微场景、多对象、净空规则 |
| **L4** | 项目切片 | 脱敏样本 + 确认流 + rollup |
| **L5** | 交付预备 | 多项目、块库策略；仍非任意施工图 |

当前诚实定位（2026-05-26）：Core 多数在 L0~L1；符号部分 L2；工装样本 L3~L4 边缘；**无 L5**。

## claim_level（登记表字段）

| 值 | 含义 |
| --- | --- |
| `none` | 仅计划，未实现 |
| `deferred` | 实现存在，明确不做真实 CAD 或 COM 未就绪 |
| `smoke` | 单次会话 smoke，未进 registry |
| `verified` | registry 行 + 可复跑 cad_case + `geometry_verified` |
| `showcase` | verified + 纳入 Ladder 展示册 |

## 四进度口径（与 AGENTS.md 对齐）

| 指标 | 回答的问题 |
| --- | --- |
| **工程完备度（表 A）** | 模块有没有、non-CAD 能不能跑 |
| **任务清单 / RCAD 烟囱（表 B）** | 任务包有没有跑完 |
| **CAD 证明覆盖率** | 登记能力中有多少 `verified` / `showcase` |
| **真实 CAD 实力（表 C）** | Ladder 加权 + L3+ 片段 + showcase 门的诚实上限 |
| **展示等级** | 当前最高已证 Ladder 到 L几 |

**禁止**用工程完备度或 RCAD 烟囱 % 代替表 C 声称「系统已能画准施工图」。表 C 机器字段见 `cad_capability_coverage.json` → `cad_strength_*`。

状态页固定表格与禁止声称：[`docs/verification/capability_proof_status_template.md`](../verification/capability_proof_status_template.md)（`CORE_STATUS.md` / `CAD_AGENT_STATUS.md` 同步）。交接扩展：[`docs/verification/capability_proof_handoff_template.md`](../verification/capability_proof_handoff_template.md)。
