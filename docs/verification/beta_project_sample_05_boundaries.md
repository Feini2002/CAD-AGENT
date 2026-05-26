# BETA-PROJECT-SAMPLE-05 样本可选真实 CAD 验证

最后更新：2026-05-26

> 后置主线「真实项目样本闭环」收口小包。机器入口：`core/project_samples/cad_check.py`、`scripts/run_project_sample_cad_check.py`。

## 目标

在 `sample_blank_shell` workflow 产出的多份 `CAD_PLAN` 上：

- 仅写入 **`CODEX_PREVIEW`** 图层
- 对本轮 **created handles** 做几何回读
- **不保存 / 覆盖** 用户 DWG

## 已交付

| 项 | 说明 |
| --- | --- |
| CAD check | `run_project_sample_cad_check()`、`collect_sample_plan_paths()` |
| Workflow 串联 | `run_project_sample_cad_check_with_workflow()` |
| CLI | `scripts/run_project_sample_cad_check.py`（`--no-cad` / `--require-cad-verified` / `--start-x` / `--start-y`） |
| 测试 | `tests/core/test_project_sample_cad_check.py`（`FakeCadDriver` 几何 verified） |

## 证据契约

| 模式 | `status` | `evidence_state` | `geometry_verified` |
| --- | --- | --- | --- |
| 真实 / fake CAD 成功 | `geometry_verified` | `readback_geometry_verified` | **true** |
| `--no-cad` / 无 driver | `deferred` | `deferred_cad_readback_required` | **false** |
| CAD 执行失败 | `failed` | `deferred_cad_readback_required` | **false** |

报告路径：`project_sample_cad_check_report.json`。

当前仓库存档的 no-CAD 检查报告是 `deferred`，不是真实 AutoCAD `geometry_verified`。`--require-cad-verified` 用于 CI / 交接硬门禁：只要报告不是 `geometry_verified`（包括 `--no-cad` deferred），CLI 就返回非 0，但仍会保存报告供审计。

## 不能声称什么

- deferred / non-CAD benchmark **≠** 样本已在真实 AutoCAD 几何准确。
- 本样本闭环 **不覆盖** 用户原始 DWG 或任意项目图纸。
- 不能把 `sample_blank_shell_too_small` blocked 样本说成 CAD 已验证。

## 子校验

```powershell
& $py -m unittest tests.core.test_project_sample_cad_check -v
& $py scripts\run_project_sample_cad_check.py --no-cad
& $py scripts\run_project_sample_cad_check.py --no-cad --require-cad-verified
```

真实 CAD（用户会话，可选）：

```powershell
& $py scripts\run_project_sample_cad_check.py --start-x 28000 --start-y 12000
```

## 父包收口

`BETA-PROJECT-SAMPLE-01`～`05` 完成脱敏样本从 `projects/` → shell / workflow / benchmark / 可选 CAD check 入口的闭环。fake driver 可证明 readback 逻辑；真实项目样本 CAD 几何证据必须在用户 AutoCAD 会话下单独运行并取得 `geometry_verified` 后才可声称。下一后置主线：`BETA-PROPOSAL-01`。
