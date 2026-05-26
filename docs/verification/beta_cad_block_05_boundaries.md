# BETA-CAD-BLOCK-05 CAD Beta 证据汇总

最后更新：2026-05-26

> 后置主线：**真实 CAD 能力扩展** 第 5 小包（**父包收口**）。机器入口：`core/verification/cad_beta_evidence_rollup.py`。

## 目标

汇总 `BETA-CAD-BLOCK-01` 到 `04` 的 **non-CAD** 证据为单一机器报告，并固化 **可声称 / 不可声称** 边界文档包。

## 已交付

| 项 | 说明 |
| --- | --- |
| Rollup | `run_cad_beta_evidence_rollup()` |
| CLI | `scripts/run_cad_beta_evidence_rollup.py` |
| 父包验收 | `beta_cad_block_acceptance.md` |
| Rollup 说明 | `beta_cad_block_evidence_rollup.md` |
| Fake driver | `core/verification/fake_cad_driver.py`（probe rollup 复用） |
| 测试 | `tests/core/test_cad_beta_block_acceptance.py` |

## 不能声称什么

- rollup `pass` **≠** `geometry_verified`。
- 不包含自动重跑真实 AutoCAD COM（仅引用历史 validation 路径）。

## 子校验

```powershell
& $py -m unittest tests.core.test_cad_beta_block_acceptance -v
& $py scripts\run_cad_beta_evidence_rollup.py
```

## 父包状态

**`BETA-CAD-BLOCK` 01–05 已收口**。下一后置：`BETA-PROJECT-SAMPLE-01`。
