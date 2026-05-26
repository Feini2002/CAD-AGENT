# commercial_fitout Scene Product Alpha 边界（C 路线汇总）

最后更新：2026-05-26（C-CFIT-07 收口）

> 机器入口：`agents/commercial_fitout/capabilities/product_alpha_boundary.json`  
> 校验：`core/agents/commercial_fitout_product_boundary.py` · `tests/agents/test_commercial_fitout_product_boundary.py`

## 成熟度（状态页口径）

| 字段 | 值 |
| --- | --- |
| 层级 | **Scene Product Alpha**（`scene_product_alpha`） |
| **不是** | Scene Product 产品化完成 |
| `product_alpha_status` | `product_boundary` |
| C 路线 | `C-CFIT-01` .. `C-CFIT-07` 已收口 |

`CORE_STATUS.md` / `CAD_AGENT_STATUS.md` 仅按上表与下方证据上调表述，**不得**写成「工装 Agent 已产品化」或「任意项目 geometry_verified」。

## 可声明能力（有证据）

| ID | 摘要 | 证据类型 | geometry_verified |
| --- | --- | --- | --- |
| subscene_scope | 开放办公 / 会议室 / 前台三子场景 + SCOPE | non-CAD fixture | 否 |
| object_catalog_semantics | 14 项 catalog → OBJECT_SPEC | unit test | 否 |
| controlled_block_mapping | FITOUT_* 受控块 + fallback | unit test | 否 |
| micro_scene_benchmark | 8 微场景（4 pass + 4 blocked） | benchmark | 否 |
| sample_confirmation_loop | 脱敏样本确认门禁 + assumptions/risks | non-CAD pipeline | 否 |
| sample_cad_smoke_readback | 确认后 3× `draw_object` + readback | unit test (FakeCad) | **是（仅 `commercial_fitout_sample`）** |

## 不可声明

- 完整工装 Scene Product / 任意真实项目几何准确。
- 完整施工图、机电、结构、消防报审包。
- 本机未跑通的真实 AutoCAD 会话几何结论（C-CFIT-06 CLI deferred）。
- 任意公司块库 / 零售门店 layout（见 `deferred_legacy_workflows`）。

## 下一阶段差距（→ Scene Product）

1. 真实 AutoCAD 下 `run_commercial_fitout_cad_smoke.py` 报告。
2. 第二组脱敏样本 + 块库策略。
3. 会议室 / 前台独立真实 CAD 代表 case。
4. 真实项目上用户确认 + partial replan 复验。
5. 解释模板与业务规则产品化验收。

## 子包索引

| 包 | 要点 |
| --- | --- |
| C-CFIT-01 | `SCOPE.md` + `subscenes.json` |
| C-CFIT-02 | `object_catalog.json`（14 项） |
| C-CFIT-03 | `block_mapping` + `FITOUT_*` 块库 |
| C-CFIT-04 | micro-scene benchmark 8 cases |
| C-CFIT-05 | `commercial_fitout_sample` 确认闭环 |
| C-CFIT-06 | `run_commercial_fitout_cad_smoke.py` |
| C-CFIT-07 | 本文 + `product_alpha_boundary.json` |

## 子校验

```powershell
python -m unittest tests.agents.test_commercial_fitout_product_boundary tests.agents.test_commercial_fitout_scope -v
```
