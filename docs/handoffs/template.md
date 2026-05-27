# 交接包模板

最后更新：2026-05-28
维护者：Cursor / Codex Agent 会话
用途：供 Codex 或其它 agent **按开发包**做高智力校验、审计与换机接手。

> 本文是交接包填写模板。当前活跃交接写入 `docs/handoffs/current.md`，全量索引写入 `docs/handoffs/package-index.md`；机器可读证据在 `output/validation_runs/`，简版流水在 `docs/status/changelog.md`。

---

## 目录

| 序号 | 开发包 | 状态 | 真实 CAD |
| --- | --- | --- | --- |
| 0 | [会话探针：CAD-MCP + 截图自检](#0-会话探针cad-mcp--截图自检无代码变更) | 只读核查 | 未执行仓库脚本 |
| 1 | [R-CAD-VIEW-CAPTURE](#1-r-cad-view-capture) | baseline 完成 | 是 |
| 2 | [R-CAD-CONTRACT](#2-r-cad-contract) | baseline 完成 | 是 |
| 3 | [R-BLOCK-METADATA](#3-r-block-metadata) | baseline 完成 | 否 |
| 4 | [R-BLOCK-PLAN](#4-r-block-plan) | baseline 完成 | 否 |
| 5 | [R-BLOCK-CAD-01](#5-r-block-cad-01) | 完成 | 否 |
| 6 | [R-BLOCK-CAD-02](#6-r-block-cad-02) | 完成 | 否 |
| 7 | [R-BLOCK-CAD-03](#7-r-block-cad-03) | 完成 | 否 |
| 8 | [R-BLOCK-CAD-04](#8-r-block-cad-04) | 完成 | 否（no-CAD 实跑） |
| 9 | [R-BLOCK-CAD-05](#9-r-block-cad-05) | 完成 | **是** |
| audit | [Codex 深度全量安全复盘](#codex-深度全量安全复盘非-planmd-开发包) | 审计完成 | 否 |
| struct-audit-01 | [STRUCT-AUDIT-01](#struct-audit-01全仓-python-结构审计) | 审计完成 | 否 |
| struct-merge-prep-01 | [STRUCT-MERGE-PREP-01](#struct-merge-prep-01合并规则与候选清单) | 规则 / 候选完成 | 否 |
| struct-merge-01 | [STRUCT-MERGE-01](#struct-merge-01drawing_policy-合并小包--bug-筛查) | 完成 | 否 |
| maintenance-4-7 | [Codex 维护 4-7 包](#codex-维护-4-7-包结构整理路径公共化schema-registry文档主从治理) | 完成 | 否 |
| neg-cad-proof-sync | [NEG-CAD-PROOF-SYNC](#neg-cad-proof-sync负向安全-runner--覆盖率可读证据--composition-收口) | 完成 | 否（包内 real-CAD 当时 external_blocker；后续 RCAD-20 已补验） |
| lcad-10.4 | [LCAD-10.4](#lcad-104negative-boundary-doc负向-cad-安全边界文档) | 完成 | 否 |
| lcad-10.5 | [LCAD-10.5](#lcad-105parent-rollup父包-lcad-10-negative-safety-收口) | 完成 | 否 |
| lcad-11.1 | [LCAD-11.1](#lcad-111evidence-vocab趋势-evidence-词表契约) | 完成 | 否 |
| lcad-11.2 | [LCAD-11.2](#lcad-112regression-trend-jsonlocal-cad-regression-趋势-json) | 完成 | 否 |
| lcad-11.3 | [LCAD-11.3](#lcad-113validation-trend-indexcad-validation-历史趋势索引) | 完成 | 否 |
| lcad-11.4 | [LCAD-11.4](#lcad-114coverage-trend-hookcoverage-趋势-hook) | 完成 | 否 |
| lcad-11.5 | [LCAD-11.5](#lcad-115trend-boundary-doc趋势报告声明边界) | 完成 | 否 |
| cad-val-02 | [CAD-VAL-02](#cad-val-02environment-gate-optional环境门禁可选化) | 完成 | 否 |
| lcad-12 | [LCAD-12](#lcad-12hatch-comstructured-deferred) | 完成 | 否 |
| lcad-13 | [LCAD-13](#lcad-13session-snapshot-cad能力探针会话快照) | 完成 | 否 |
| lcad-14 | [LCAD-14](#lcad-14guard-full-cadguard-全链路-strict-包装) | 完成 | 否 |
| cfit-09 | [CFIT-09](#cfit-09second-project-sample第二组工装脱敏样本) | 完成 | 否 |
| cfit-10 | [CFIT-10](#cfit-10reception-project-sample前台接待脱敏样本) | 完成 | 否 |
| cfit-11 | [CFIT-11](#cfit-11three-sample-boundary-sync三样本-boundaryrollup-口径同步) | 完成 | 否 |
| cfit-12 | [CFIT-12](#cfit-12fitout-subscene-object-cad-smoke子场景代表对象-cad-smoke) | 完成 | 否 |
| rcad-15 | [RCAD-15](#rcad-15symbol-glyph-sofa沙发-glyph-补验) | verified | **是** |
| scene-prod-06 | [SCENE-PROD-06](#scene-prod-06multi-scene-regression-gate多场景回归门禁) | 完成 | 否 |
| scene-prod-05 | [SCENE-PROD-05](#scene-prod-05-scene-explanation-template) | 完成 | 否 |
| rest-prod-04 | [REST-PROD-04](#rest-prod-04-multi-scene-p3-rollup) | 完成 | 否 |
| rest-prod-03 | [REST-PROD-03](#rest-prod-03-restaurant-p3-wave-rollup) | 完成 | 否 |
| rest-prod-02 | [REST-PROD-02](#rest-prod-02-restaurant-beta-boundary) | 完成 | 否 |
| rest-prod-01 | [REST-PROD-01](#rest-prod-01-restaurant-alpha-boundary) | 完成 | 否 |
| office-prod-03 | [OFFICE-PROD-03](#office-prod-03office-p3-wave-rollupp3-办公波次父包收口) | 完成 | 否 |
| office-prod-02 | [OFFICE-PROD-02](#office-prod-02office-beta-boundaryp3-第二包) | 完成 | 否 |
| office-prod-01 | [OFFICE-PROD-01](#office-prod-01office-alpha-boundaryp3-进波首包) | 完成 | 否 |
| core-p4 | [CORE-P4](#core-p4p4-core-波次父包收口) | 完成 | 否 |
| rblock-08 | [RBLOCK-08](#rblock-08p5-wave-parent-rollupp5-图块波次父包收口) | 完成 | 否 |
| rblock-07 | [RBLOCK-07](#rblock-07block-matrix-registry-rowsp5-矩阵-registry-绑定) | 完成 | 否 |
| rblock-06 | [RBLOCK-06](#rblock-06block-attribute-boundaryp5-属性块探针边界) | 完成 | 否 |
| rblock-05 | [RBLOCK-05](#rblock-05second-controlled-blockp5-第二受控块-metadata) | 完成 | 否 |
| rblock-04 | [RBLOCK-04](#rblock-04block-matrix-manifestp5-块矩阵-manifest) | 完成 | 否 |
| rblock-03 | [RBLOCK-03](#rblock-03block-alpha-boundaryp5-图块波次首包) | 完成 | 否 |
| symbol-09 | [SYMBOL-09](#symbol-09block-first-tierp4-block-first-入口) | 完成 | 否 |
| symbol-08 | [SYMBOL-08](#symbol-08glyph-fallback-boundaryp4-fallback-边界) | 完成 | 否 |
| draw-02 | [DRAW-02](#draw-02drawing-standard-registry-rowsp4-registry-绑定) | 完成 | 否 |
| draw-01 | [DRAW-01](#draw-01drawing-standard-boundaryp4-core-首包) | 完成 | 否 |
| cfit-13 | [CFIT-13](#cfit-13p2-wave-parent-rollupp2-工装波次父包收口) | 完成 | 否 |
| v-proof-40 | [V-PROOF-40](#v-proof-40block-matrix-plan表-c-收口) | 完成 | 否 |
| v-proof-63 | [V-PROOF-63](#v-proof-63l4-project-slicel4-工装项目切片-showcase) | 完成 | **是** |
| v-proof-61 | [V-PROOF-61 / 60](#v-proof-61--60l2-symbol-gallery--showcase-index) | 完成 | **是** |
| v-proof-62 | [V-PROOF-62](#v-proof-62l3-fitout-snippetl3-工装微场景-showcase) | 完成 | **是** |
| rcad-20 | [RCAD-20](#rcad-20negative-cad真实-cad-负向安全补验) | verified（guard-only） | 是 |
| rcad-06 | [RCAD-06](#rcad-06hatch-com受控-smoke-真实-cad-补验) | verified | **是** |
| rcad-27 | [RCAD-27](#rcad-27trend-rollup-cadlocal-cad-regression-trend-rollup-真实-cad-补验) | verified | **是** |
| rcad-28 | [RCAD-28](#rcad-28beta-evidence-rollupbeta-cad-block-evidence-rollup--trend-补验) | verified（non-CAD rollup） | 否 |
| v-proof-33 | [V-PROOF-33](#v-proof-33readability-report-rows可读性状态登记行绑定) | 完成 | 否 |
| — | [当前交接说明](#当前交接说明) | 只引用 PlanMD | — |

---

## 交接包标准模板（每包 9 项）

1. 本次开发包名
2. 修改文件列表
3. 关键设计说明
4. 新增/修改测试
5. 实际运行的命令和结果
6. 是否运行真实 CAD（**必须**写「是」或「否」）
7. 机器可读证据路径（见下表）
8. **结论分类表**（**必须**区分 non-CAD 与 `geometry_verified`）
9. 剩余风险（未做 CAD 时须写明几何未验证）

**Evidence gate 必读**：[`docs/verification/evidence_gate_handoff_rules.md`](../verification/evidence_gate_handoff_rules.md)（R4-05）；词表见 [`evidence_state_vocabulary.md`](../verification/evidence_state_vocabulary.md)。

压缩旧交接时仍必须保留 1~9 项标题；§3 `V-PROOF`、RCAD 回写包或任何改动 `cad_capability_registry.json` 的包必须补 10~12 项。允许压缩叙述，不允许压掉真实 CAD 证据路径、created handles、`external_blocker`、`geometry_verified` 或 `visual_aid_only` 边界。

### 第 7 项：证据路径（按运行类型）

| 运行类型 | 路径示例 |
| --- | --- |
| `--no-cad` validation | `output/validation_runs/<包名>-no-cad/report.json`（核对 `evidence_summary.non_cad_only`） |
| 全量 CAD validation | 上列 + `readback_report.json`、步骤子报告、窗口截图 |
| Benchmark suite | `output/test_artifacts/benchmarks/<run>/benchmark_summary.json` |
| 受控 block alpha CAD | `output/validation_runs/r-block-alpha-cad/block_alpha_report.json` |

### 第 8 项：结论分类表（必填格式）

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| （本包完成了什么） | `non_cad_only` / `benchmark_pass_non_cad` / `readback_geometry_verified` 等 | **是** 或 **否** |

禁止：仅用「测试通过」「suite pass」代替证据类型；禁止把截图写成几何已验证。

### 能力证明包附加项（V-PROOF-05；§3 `V-PROOF` / RCAD 回写包必填）

在标准 9 项之外，下列能力证明相关包 **必须** 追加本节（其它包可写「不适用」一行）：

- `V-PROOF-*`（V0~V7）、任何修改 `cad_capability_registry.json` 的包、任何要求 **回写 registry** 的 RCAD 包。

**10. 能力登记表（registry）**

| 字段 | 必填内容 |
| --- | --- |
| `registry_path` | 如 `examples/capability_proof/cad_capability_registry.json` |
| 本包触及行 | 下表至少一行；无变更时写「无行变更」 |

| `capability_id` | `claim_level`（前→后） | `ladder_level` | `evidence.report_path`（若 verified） |
| --- | --- | --- | --- |
| （例 `regression.baseline_cad_validation`） | deferred → verified | L1 | `output/validation_runs/.../readback_report.json` |

**11. CAD 证明覆盖率**

| 字段 | 必填内容 |
| --- | --- |
| 回写前 `cad_proof_coverage_rate` | 数字或「未复跑」 |
| 回写后 `cad_proof_coverage_rate` | `scripts/run_capability_coverage.py` 输出 |
| 覆盖率 JSON 路径 | `output/validation_runs/capability-lab/cad_capability_coverage.json` |

**12. 展示等级 Ladder**

| 字段 | 必填内容 |
| --- | --- |
| 本包最高触及 Ladder | L0~L5 之一 |
| 是否对外提升 Ladder 声称 | **是/否** + 一句边界 |

规范全文：[`docs/verification/capability_proof_handoff_template.md`](../verification/capability_proof_handoff_template.md)、[`evidence_gate_handoff_rules.md`](../verification/evidence_gate_handoff_rules.md) §7。

---
