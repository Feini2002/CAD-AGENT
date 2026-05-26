# sample_blank_shell_too_small

## 样本标识

| 字段 | 值 |
| --- | --- |
| `sample_id` | `sample_blank_shell_too_small` |
| `domain` | `generic` |
| `deidentified` | `true` |
| 用途 | **失败** benchmark（空间不足） |

## 输入说明

| 文件 | 角色 |
| --- | --- |
| `input/shell.manual.json` | 过小空壳（3600×2600） |
| `fixtures/design_brief.json` | brief |
| `fixtures/drawing_model.json` | drawing |

Workflow：`examples/workflows/sample_blank_shell_too_small_loop.json`（`layout_expectation` 要求全部落位）。

## 预期输出

- pipeline **`status=blocked`**，`failure_category=insufficient_space`
- **`cad_plan_count=0`**（禁止静默少放对象后 pass）
- verification 仍为 non-CAD / unverified

## 不可声称

- **不能** 把 blocked 结果当成可用布局方案。
- **不能** 声称几何已验证。
