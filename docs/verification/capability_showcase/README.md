# Capability Showcase（能力展示册）

最后更新：2026-05-27（`V-PROOF-63` L4 双工装样本 + 扩面；共 **12** 条 showcase；最高已证 **L4**）

本目录索引 **可浏览** 的真实 CAD 证据，供表 C「展示就绪度」与 `claim_level=showcase` 登记行使用。展示册 **不能** 替代 created-handle readback 或 `geometry_verified` 报告；仅汇总已有证据路径。

## 层级

| Ladder | 目录 | 说明 |
| --- | --- | --- |
| L2 | `showcase/L2/` | 单对象 / symbol glyph 画廊（待 `V-PROOF-61`） |
| L3 | `showcase/L3/` | 工装 / 办公微场景平面片段（非 primitive 矩形 smoke） |
| L4 | `showcase/L4/` | 脱敏项目样本切片（待 `V-PROOF-63`） |

## 机器索引

- `showcase_index.json`：登记 `capability_id`、证据报告、基准 case、安全约束摘要。

## 禁止声称

- 有 showcase 行 **不等于** L5 施工图或全库 `geometry_verified`。
- 主指标 `cad_strength_headline_percent` 仍为 min(实力指数, L3+ 片段, showcase 就绪度)；须与 `run_capability_coverage.py` 一致汇报。
