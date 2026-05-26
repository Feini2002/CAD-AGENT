# LCAD-07：Block / Attribute / Hatch 能力边界

最后更新：2026-05-26

> 机器入口：`examples/cad_regression/cad_block_attribute_hatch_boundary.json`  
> 校验：`core/verification/cad_block_attribute_hatch_boundary.py`

## 能力矩阵

| ID | 图元 | 状态 | geometry_verified | 说明 |
| --- | --- | --- | --- | --- |
| `insert_block_alpha_controlled` | block_reference | **verified** | 是（受控范围） | `CODEX_TEST_BLOCK_001` + created-handle readback |
| `block_attribute_tags_probe` | block_reference | **verified** | 是（probe 计划） | 须 `attribute_readback_probe`；标签匹配才 verified |
| `hatch_write_readback` | hatch | **deferred** | 否 | COM 写入/回读未实现；probe 仅占位 |

## 可声称（有证据）

- 受控 `insert_block_alpha` 在 `CODEX_PREVIEW` 上可执行并通过 block_reference 几何回读（见 `block_alpha_cad_evidence.md`）。
- 带 `attribute_readback_probe` 的计划可验证属性 tag 匹配（`tests.core.test_block_attribute_probe`）。
- Hatch 在 capability probe 中有 **structured deferred** 槽位，failure_category=`hatch_unverified`。

## 不可声称

- 任意块名 / 公司块库 / 全部 `insert_block_alpha` 计划均已几何准确。
- 无 probe 标志的属性块自动 verified。
- Hatch 已 geometry_verified 或可用于生产填充验收。

## 子校验

```powershell
python -m unittest tests.core.test_block_attribute_probe tests.core.test_cad_block_attribute_hatch_boundary -v
```

真实 CAD（可选）：

```powershell
python scripts/run_cad_validation.py --block-alpha-only --output-dir output/validation_runs/lcad-07-block-alpha-cad
```
