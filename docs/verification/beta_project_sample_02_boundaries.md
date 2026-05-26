# BETA-PROJECT-SAMPLE-02 样本 Shell / Project Model Fixture

最后更新：2026-05-26

> 后置主线：**真实项目样本闭环** 第 2 小包。机器入口：`core/project_samples/loader.py`、`projects/sample_blank_shell/`。

## 目标

为 `sample_blank_shell` 建立可复用的 **shell + brief + drawing + PROJECT_MODEL 金样**，并通过 manifest 驱动 loader / builder 测试。

## 已交付

| 路径 | 说明 |
| --- | --- |
| `fixtures/design_brief.json` | 样本专用 brief |
| `fixtures/drawing_model.json` | 占位 drawing（schema 合法） |
| `expected/project_model.expected.json` | `build_project_model` 金样 |
| `core/project_samples/loader.py` | `load_sample_inputs`、`build_sample_project_model` |
| `tests/core/test_project_sample_loader.py` | loader + schema + 金样对比 |

## 现在可以声称什么

- 可通过 manifest **一键加载** 样本 shell 与输入，并构建 schema 合法的 `PROJECT_MODEL`。
- 金样对比锁定 `shell_context`（洞口、柱、禁布区）与约束 ID。

## 不能声称什么

- **不是** 真实 CAD / DWG readback 已验证。
- **不是** 完整 blank-shell workflow 或 benchmark 已纳入本样本（`BETA-PROJECT-SAMPLE-03` 起）。

## 子校验

```powershell
& $py -m unittest tests.core.test_project_sample_loader tests.core.test_shell_loader tests.core.test_project_model -v
```

## 下一小包

`BETA-PROJECT-SAMPLE-04`：样本 benchmark。
