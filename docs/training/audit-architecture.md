# 训练审计架构（全局规则 ← 案例沉淀）

最后更新：2026-05-28

## 原则

**所有训练都服务于让全局越来越聪明**——不是为每个案例写一套 Python 验收脚本。

| 放哪 | 放什么 | 不放什么 |
| --- | --- | --- |
| **`core/verification/training_geometry_audit.py`** | 可复用探针、反模式检测、checklist 执行引擎 | 某款沙发的 1867mm、0.821 比例 |
| **`projects/<case>/expected/audit_checklist.json`** | 本 brief 的阈值、参考 handle、启用哪些探针 | 探针实现逻辑 |
| **`projects/<case>/runs/*.py`** | 本轮落图（case_script） | 审计规则硬编码 |
| **`agents/<scenario>/rules.md`** | 场景词汇、「参照≠clone」等策略 | 数值门槛 |
| **`docs/training/pipeline-changelog.md`** | 链路级教训 | 单案例几何 bug |

## 数据流

```text
brief.md + intent.json
        ↓ 派生阈值
expected/audit_checklist.json   (schema_version: 2)
        ↓
core/verification/training_geometry_audit.py
   ├─ probe: cleanliness（微线、端点、实体上限）
   ├─ probe: reference_profile（只读参考块尺寸槽位）
   ├─ probe: preview_profile（预览层同维度特征）
   ├─ probe: reference_profile_match（容差由 checklist 提供）
   └─ probe: forbidden_patterns（全局反模式，如 schematic_equal_grid）
        ↓
roundN_geometry_audit.json
        ↓
Agent 自检（agent_review_required，任何案例必有）
        ↓
你 feedback §几何
```

## 案例 → 全局 晋升规则

训练中发现 repeatable 失败模式时：

1. **先在** 本案 `audit_checklist.json` **填阈值**或启用已有探针
2. **若** 第二个案例也需要 → **在 core 加探针**（如 `forbidden_schematic_equal_grid`）
3. **写** `pipeline-changelog.md` 一条（链路）+ `training-errors.md`（案例）
4. **禁止** 复制 `sofa_*_audit.py` 到新案例

## Checklist schema v2（摘要）

```json
{
  "schema_version": 2,
  "reference": { "handle": "4A2", "read_profile": true },
  "checks": {
    "semantic": {
      "reference_profile_match": { "seat_split_ratio_tol": 0.08 },
      "min_entity_count": 20,
      "forbidden_patterns": ["schematic_equal_grid"]
    },
    "cleanliness": {
      "preview_width_mm": { "min": 1850, "max": 1885 },
      "micro_line_count_max": 0
    }
  },
  "agent_review_required": ["visual_match_brief"]
}
```

## 机器审计 vs Agent 自检

| 层 | 谁 | 作用 |
| --- | --- | --- |
| 机器 | core engine + checklist | 必要非充分；可客观量的语义/洁净度 |
| Agent | `audit_review.md` | brief 目视、款式家族、禁止 schematic 偷懒 |
| 你 | `feedback.md` | 最终 pass/fail |

**round6 教训：** 仅 `reference_profile_match` 全绿仍可能款式 fail → `forbidden_schematic_equal_grid` 已进全局探针；目视仍由 Agent/你兜底。

**视觉 > 尺寸：** checklist 可设 `sizing_mode: visual_approx_rounded` 与 `non_blocking_when_visual_pass`（Agent 策略；机器仍报数值，但不单独阻塞 Delivery）。见 [`vision-first-style.md`](vision-first-style.md)。

## 调用方式（案例脚本）

```python
from core.verification.training_geometry_audit import (
    load_training_audit_checklist,
    run_training_geometry_audit,
)

checklist = load_training_audit_checklist(CASE_ROOT / "expected" / "audit_checklist.json")
audit = run_training_geometry_audit(
    driver,
    checklist,
    preview_bounds={"x0": px0, "x1": px1, "y0": py0, "y1": py1},
)
if not audit["audit_pass"]:
    raise SystemExit(1)
```

## 相关文件

- 引擎：`core/verification/training_geometry_audit.py`
- 模板：`projects/residential_training_template/expected/audit_checklist.template.json`
- 主链路：`docs/training/README.md`
