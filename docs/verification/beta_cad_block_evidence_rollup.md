# BETA-CAD-BLOCK 证据 Rollup 说明

最后更新：2026-05-26

## 机器报告

| 字段 | 说明 |
| --- | --- |
| 入口 | `scripts/run_cad_beta_evidence_rollup.py` |
| 默认输出 | `output/test_artifacts/cad_beta_evidence/beta_cad_block_05/cad_beta_evidence_rollup.json` |
| Trend 输出 | `<output-root>/evidence_trend/cad_beta_evidence_rollup_trend.json` |
| 顶层 `status` | 全部 5 个子包 `pass` 时为 `pass` |
| `evidence_summary.geometry_verified_count` | **固定为 0**（rollup 不声称几何已验证） |

## 子包执行内容

| subpackage_id | rollup 动作 |
| --- | --- |
| `BETA-CAD-BLOCK-01` | 运行 `block_alpha_beta_suite`（8 cases） |
| `BETA-CAD-BLOCK-02` | 合成 attribute probe 检查（probe / base 计划） |
| `BETA-CAD-BLOCK-03` | Fake-driver `run_cad_capability_probe` |
| `BETA-CAD-BLOCK-04` | 运行 `drawing_standard_beta_suite`（6 cases） |
| `BETA-CAD-BLOCK-05` | 校验 `docs/verification/beta_cad_block_*.md` 文档包齐全 |

## 与总验收关系

人类可读声称边界见 [`beta_cad_block_acceptance.md`](beta_cad_block_acceptance.md)。Codex 校验时应对照 rollup JSON 的 `claims.forbidden` 与 `evidence_summary.non_cad_only`。
