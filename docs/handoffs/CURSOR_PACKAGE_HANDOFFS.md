# Cursor 开发包交付交接包（汇总）

最后更新：2026-05-27
维护者：Cursor / Codex Agent 会话
用途：供 Codex 或其它 agent **按开发包**做高智力校验、审计与换机接手。

> 本文是**唯一按包汇总的交接入口**。机器可读证据在 `output/validation_runs/`；简版流水在根目录 `CAD_AGENT_CHANGELOG.md`。

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
| v-proof-63 | [V-PROOF-63](#v-proof-63l4-project-slicel4-工装项目切片-showcase) | 完成 | **是** |
| v-proof-61 | [V-PROOF-61 / 60](#v-proof-61--60l2-symbol-gallery--showcase-index) | 完成 | **是** |
| v-proof-62 | [V-PROOF-62](#v-proof-62l3-fitout-snippetl3-工装微场景-showcase) | 完成 | **是** |
| rcad-20 | [RCAD-20](#rcad-20negative-cad真实-cad-负向安全补验) | verified（guard-only） | 是 |
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

## RCAD-15：SYMBOL-GLYPH-SOFA（沙发 glyph 补验）

**日期**：2026-05-27
**性质**：§5 RCAD；`seating_sofa_plan` 真实 CAD smoke；`CODEX_PREVIEW`、未保存 DWG。

### 1. 包名

`RCAD-15-SYMBOL-GLYPH-SOFA`

### 2. 修改文件

- `examples/symbol_specs/seating_sofa_plan.json`
- `examples/capability_proof/cad_capability_registry.json`（刷新 `object.sofa.glyph` 与 `symbol.spec.symbol_sofa_plan` 证据路径）
- `docs/planning/任务清单.md`
- `CORE_CONTEXT_BRIEF.md`
- `CAD_AGENT_CHANGELOG.md`

### 3. 关键设计说明

- 只在 `CODEX_PREVIEW` 中绘制 sofa glyph，验证对象为单一 `seating_sofa_plan` spec。
- `object.sofa.glyph` 保持 `verified`，`symbol.spec.symbol_sofa_plan` 保持 `showcase`；真实 CAD 证据刷新不得把 showcase 降级成 verified。

### 4. 新增/修改测试

- 未新增单测；本包用真实 AutoCAD smoke 报告作为几何证据。

### 5. 命令

```powershell
& $py scripts\run_symbol_glyph_cad_smoke.py --symbol-spec examples\symbol_specs\seating_sofa_plan.json --output-dir output\validation_runs\rcad-15-symbol-glyph-sofa-20260527
```

→ `geometry_verified`、6 handles（line×6）、bbox 2200×900 mm

### 6. 真实 CAD

**是**

### 7. 证据

`output/validation_runs/rcad-15-symbol-glyph-sofa-20260527/symbol_glyph_cad_smoke_report.json`

### 8. 结论

| capability_id | claim_level | geometry_verified |
| --- | --- | --- |
| `object.sofa.glyph` | verified | **是** |
| `symbol.spec.symbol_sofa_plan` | showcase（证据路径已刷新） | **是** |

### 9. 风险

L2 glyph 单 spec；不等同 L3 办公微场景或工装 composition。

### 10–12. 能力证明附加项

| 字段 | 值 |
| --- | --- |
| registry 行 | `object.sofa.glyph`（verified 证据刷新）；`symbol.spec.symbol_sofa_plan`（showcase 证据刷新） |
| 覆盖率复跑 | 当前以 `output/validation_runs/capability-lab/cad_capability_coverage.json` 为准 |
| 本包最高触及 Ladder | L2 / showcase；不提升到 L3+ |

---

## OFFICE-PROD-02：OFFICE-BETA-BOUNDARY（P3 第二包）

**日期**：2026-05-27
**性质**：§4.2 P3；办公 scene_beta benchmark 边界；链式 `OFFICE-PROD-01`；不运行真实 CAD。

### 1. 包名

`OFFICE-PROD-02-OFFICE-BETA-BOUNDARY`

### 2. 修改文件

- `core/agents/office_beta_boundary.py`
- `examples/capability_proof/office_prod_beta_manifest.json`
- `docs/verification/office_prod_02_office_beta_boundary.md`
- `scripts/run_office_beta_boundary_contract.py`
- `tests/core/test_office_prod_02_office_beta_boundary.py`

### 5. 命令

`python -m unittest tests.core.test_office_prod_02_office_beta_boundary -v` → 6 tests OK

### 6. 真实 CAD

**否**

### 8. 结论

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| office-scene-beta-benchmark 9/9 no-CAD pass + scene_beta preferences | `benchmark_pass_non_cad` / `dry_run_valid_plan_only` | **否** |

### 9. 风险

beta 四 tier 未在真实 CAD 回读；`V-PROOF-24` verified 仍待 RCAD。

---

## OFFICE-PROD-01：OFFICE-ALPHA-BOUNDARY（P3 进波首包）

**日期**：2026-05-27
**性质**：§4.2 P3 进波；办公 alpha benchmark + agents/office 边界；不运行真实 CAD。

### 1. 包名

`OFFICE-PROD-01-OFFICE-ALPHA-BOUNDARY`

### 2. 修改文件

- `core/agents/office_alpha_boundary.py`
- `examples/capability_proof/office_prod_alpha_manifest.json`
- `docs/verification/office_prod_01_office_alpha_boundary.md`
- `scripts/run_office_alpha_boundary_contract.py`
- `tests/core/test_office_prod_01_office_alpha_boundary.py`

### 5. 命令

`python -m unittest tests.core.test_office_prod_01_office_alpha_boundary -v` → 7 tests OK

### 6. 真实 CAD

**否**

### 8. 结论

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| office-alpha-benchmark 18/18 no-CAD pass + preferences 契约 | `benchmark_pass_non_cad` | **否** |

### 9. 风险

`agents/office` 仍为 scaffold；`OFFICE-PROD-02` beta 边界待交付。

---

## CORE-P4：P4 Core 波次父包收口

**日期**：2026-05-27
**性质**：§4.2 P4 父包；`DRAW-01`~`09` 四子包 rollup；drawing 6/6 + block-first 3/3 复验；不运行真实 CAD。

### 1. 包名

`CORE-P4-WAVE-PARENT-ROLLUP`

### 2. 修改文件

- `core/p4_core_wave.py`
- `docs/verification/p4_core_wave_acceptance.md`
- `scripts/run_p4_core_wave_contract.py`
- `tests/core/test_p4_core_wave_parent_rollup.py`

### 5. 命令

`python -m unittest tests.core.test_p4_core_wave_parent_rollup -v` → 6 tests OK

### 6. 真实 CAD

**否**

### 8. 结论

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| P4 四子包契约收口 + no-CAD 复验 pass | `dry_run_valid_plan_only` | **否** |

### 9. 风险

P4 曾标「已收口」但缺正式父包；本包补齐。`OFFICE-PROD` 等 P3 仍为 user_gate。

---

## RBLOCK-08：P5-WAVE-PARENT-ROLLUP（P5 图块波次父包收口）

**日期**：2026-05-27
**性质**：§4.2 P5 父包；`RBLOCK-03`~`07` rollup + acceptance；beta 8/8 + matrix 8/8 复验；不运行真实 CAD。

### 1. 包名

`RBLOCK-08-P5-WAVE-PARENT-ROLLUP`

### 2. 修改文件

- `core/block_engine/block_p5_wave.py`
- `docs/verification/block_p5_wave_acceptance.md`
- `scripts/run_block_p5_wave_contract.py`
- `tests/core/test_rblock_08_p5_wave_parent_rollup.py`

### 5. 命令

`python -m unittest tests.core.test_rblock_08_p5_wave_parent_rollup -v` → 6 tests OK

### 6. 真实 CAD

**否**

### 8. 结论

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| P5 六子包契约收口 + no-CAD 复验 pass | `dry_run_valid_plan_only` | **否** |

### 9. 风险

P5 代码轨已收口；`V-PROOF-40`/`41` 与 RCAD 真实 CAD 仍待用户会话；§4.2 P3 为 user_gate。

---

## RBLOCK-07：BLOCK-MATRIX-REGISTRY-ROWS（P5 矩阵 registry 绑定）

**日期**：2026-05-27
**性质**：§4.2 P5；矩阵 manifest → 5 行 registry 绑定 + smoke writeback API；不运行真实 CAD。

### 1. 包名

`RBLOCK-07-BLOCK-MATRIX-REGISTRY-ROWS`

### 2. 修改文件

- `core/block_engine/block_matrix_registry.py`
- `examples/capability_proof/cad_capability_registry.json`（+1 smoke 行 + 4 manifest source_refs）
- `scripts/run_block_matrix_registry_sync.py`
- `docs/verification/rblock_07_block_matrix_registry_rows.md`
- `tests/core/test_rblock_07_block_matrix_registry_rows.py`

### 5. 命令

`python -m unittest tests.core.test_rblock_07_block_matrix_registry_rows -v` → 8 tests OK

### 6. 真实 CAD

**否**

### 8. 结论

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 矩阵 5 行 registry 绑定 + suite smoke writeback | `dry_run_valid_plan_only` | **否** |

### 9. 风险

verified 四维行保留历史 readback 证据；`RBLOCK-08` P5 父包收口待交付。

---

## RBLOCK-06：BLOCK-ATTRIBUTE-BOUNDARY（P5 属性块探针边界）

**日期**：2026-05-27
**性质**：§4.2 P5；`BETA-CAD-BLOCK-02` 探针边界 manifest + 契约；no-CAD attribute smoke；不运行真实 CAD。

### 1. 包名

`RBLOCK-06-BLOCK-ATTRIBUTE-BOUNDARY`

### 2. 修改文件

- `examples/capability_proof/block_attribute_probe_manifest.json`
- `core/block_engine/block_attribute_boundary.py`
- `scripts/run_block_attribute_boundary_contract.py`
- `docs/verification/rblock_06_block_attribute_boundary.md`
- `tests/core/test_rblock_06_block_attribute_boundary.py`

### 5. 命令

`python -m unittest tests.core.test_rblock_06_block_attribute_boundary -v` → 7 tests OK

### 6. 真实 CAD

**否**

### 8. 结论

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 属性探针 deferred/不误报 契约 + smoke pass | `dry_run_valid_plan_only` | **否** |

### 9. 风险

COM 仍拒绝带 attributes 写入；真实 CAD attribute 仍走 `RCAD-05`；`RBLOCK-07` registry writeback 待交付。

---

## RBLOCK-05：SECOND-CONTROLLED-BLOCK（P5 第二受控块 metadata）

**日期**：2026-05-27
**性质**：§4.2 P5；第二受控测试块 library + sidecar metadata；`insert_block_alpha` 仍仅 001；不运行真实 CAD。

### 1. 包名

`RBLOCK-05-SECOND-CONTROLLED-BLOCK`

### 2. 修改文件

- `libraries/blocks/block_library.example.json`（+`controlled-test-block-002`）
- `libraries/blocks/controlled/CODEX_TEST_BLOCK_002.metadata.json`
- `examples/capability_proof/second_controlled_block_manifest.json`
- `core/block_engine/second_controlled_block_boundary.py`
- `scripts/run_second_controlled_block_contract.py`
- `docs/verification/rblock_05_second_controlled_block.md`
- `tests/core/test_rblock_05_second_controlled_block.py`

### 5. 命令

`python -m unittest tests.core.test_rblock_05_second_controlled_block -v` → 8 tests OK

### 6. 真实 CAD

**否**

### 8. 结论

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 第二受控块 metadata 登记 + allowlist 未放宽 | `dry_run_valid_plan_only` | **否** |

### 9. 风险

002 仅 metadata；`V-PROOF-41` 多块真实 CAD 仍待用户会话；`RBLOCK-06` 属性块边界仍待交付。

---

## RBLOCK-04：BLOCK-MATRIX-MANIFEST（P5 块矩阵 manifest）

**日期**：2026-05-27
**性质**：§4.2 P5；anchor/rotation/scale/attribute 四维矩阵 manifest + registry 四行绑定；不运行真实 CAD。

### 1. 包名

`RBLOCK-04-BLOCK-MATRIX-MANIFEST`

### 2. 修改文件

- `examples/capability_proof/block_insert_matrix_manifest.json`
- `core/block_engine/block_matrix_manifest.py`
- `scripts/run_block_insert_matrix_manifest.py`
- `docs/verification/rblock_04_block_matrix_manifest.md`
- `tests/core/test_rblock_04_block_matrix_manifest.py`

### 5. 命令

`python -m unittest tests.core.test_rblock_04_block_matrix_manifest -v` → 7 tests OK

### 6. 真实 CAD

**否**

### 8. 结论

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 四维矩阵 manifest + no-CAD runner 8/8 case pass | `dry_run_valid_plan_only` | **否** |

### 9. 风险

不得因 manifest pass 声称四维度均已真实 CAD verified；`RBLOCK-05` 第二受控块 metadata 仍待交付。

---

## RBLOCK-03：BLOCK-ALPHA-BOUNDARY（P5 图块波次首包）

**日期**：2026-05-27
**性质**：§4.2 P5 进波首包；受控 block alpha 边界契约；不运行真实 CAD。

### 1. 包名

`RBLOCK-03-BLOCK-ALPHA-BOUNDARY`

### 2. 修改文件

- `core/block_engine/block_alpha_boundary.py`
- `docs/verification/rblock_03_block_alpha_boundary.md`
- `tests/core/test_rblock_03_block_alpha_boundary.py`

### 5. 命令

`python -m unittest tests.core.test_rblock_03_block_alpha_boundary -v` → 5 tests OK

### 6. 真实 CAD

**否**

### 8. 结论

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 受控 block alpha 边界 + beta 8/8 | `dry_run_valid_plan_only` | **否** |

### 9. 风险

不得扩大到公司块库；`RBLOCK-04` 块矩阵仍待交付。

---

## SYMBOL-09：BLOCK-FIRST-TIER（P4 block-first 入口）

**日期**：2026-05-27
**性质**：§4.2 P4；block-first tier smoke + registry 四行 + deferred 边界；不运行真实 CAD。

### 1. 包名

`SYMBOL-09-BLOCK-FIRST-TIER`

### 2. 修改文件

- `core/symbol_engine/block_first_tier.py`、`block_first_boundary.py`
- `examples/capability_proof/symbol_block_first_tier_manifest.json`
- `scripts/run_block_first_tier_smoke.py`
- `docs/verification/symbol_09_block_first_tier_boundary.md`
- `examples/capability_proof/cad_capability_registry.json`（+4 行）
- `tests/core/test_symbol_09_block_first_tier.py`

### 5. 命令

`python -m unittest tests.core.test_symbol_09_block_first_tier -v` → 7 tests OK

### 6. 真实 CAD

**否**

### 8. 结论

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| block-first smoke 3/3 + registry 绑定 | `dry_run_valid_plan_only` | **否** |

### 9. 风险

`metadata_only` 块库不能当 block tier 已证；`RCAD-25` / `V-PROOF-34` verified 仍待用户会话。

---

## SYMBOL-08：GLYPH-FALLBACK-BOUNDARY（P4 fallback 边界）

**日期**：2026-05-27
**性质**：§4.2 P4；四级 symbol fallback tier 边界 + silent degradation 契约；不运行真实 CAD。

### 1. 包名

`SYMBOL-08-GLYPH-FALLBACK-BOUNDARY`

### 2. 修改文件

- `core/symbol_engine/symbol_fallback_boundary.py`
- `docs/verification/symbol_08_glyph_fallback_boundary.md`
- `tests/core/test_symbol_08_glyph_fallback_boundary.py`
- `docs/planning/任务清单.md`、`CORE_CONTEXT_BRIEF.md`、`CAD_AGENT_CHANGELOG.md`

### 5. 命令

`python -m unittest tests.core.test_symbol_08_glyph_fallback_boundary tests.core.test_symbol_fallback_policy -v` → 11 tests OK

### 6. 真实 CAD

**否**

### 8. 结论

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 四级 fallback 契约 + benchmark 3 case 无静默退化 | `dry_run_valid_plan_only` / `benchmark_pass_non_cad` | **否** |

### 9. 风险

不得将 fallback 解析 pass 说成 glyph 真实几何已证；`V-PROOF-35` registry 行仍待后续包。

---

## DRAW-02：DRAWING-STANDARD-REGISTRY-ROWS（P4 registry 绑定）

**日期**：2026-05-27
**性质**：§4.2 P4；beta suite 6 case + suite 父行登记；smoke evidence writeback；不运行真实 CAD。

### 1. 包名

`DRAW-02-DRAWING-STANDARD-REGISTRY-ROWS`

### 2. 修改文件

- `core/drawing_standard/drawing_standard_registry.py`
- `docs/verification/draw_02_drawing_standard_registry_rows.md`
- `examples/capability_proof/cad_capability_registry.json`（+7 行）
- `tests/core/test_draw_02_drawing_standard_registry_rows.py`
- `docs/planning/任务清单.md`、`CORE_CONTEXT_BRIEF.md`、`CAD_AGENT_CHANGELOG.md`

### 5. 命令

`python -m unittest tests.core.test_draw_02_drawing_standard_registry_rows -v` → 8 tests OK

### 6. 真实 CAD

**否**

### 8. 结论

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 7 行 registry 绑定 + smoke writeback dry-run 7/7 | `dry_run_valid_plan_only` | **否** |

### 9. 风险

smoke 行与 writeback 不抬表 C；`V-PROOF-44` verified 与 `RCAD-23` 仍待真实 CAD。

---

## DRAW-01：DRAWING-STANDARD-BOUNDARY（P4 Core 首包）

**日期**：2026-05-27
**性质**：§4.2 P4 进波首包；drawing_standard 边界契约；不运行真实 CAD。

### 1. 包名

`DRAW-01-DRAWING-STANDARD-BOUNDARY`

### 2. 修改文件

- `core/drawing_standard/drawing_standard_boundary.py`
- `docs/verification/draw_01_drawing_standard_boundary.md`
- `tests/core/test_draw_01_drawing_standard_boundary.py`
- `docs/planning/任务清单.md`、`CORE_CONTEXT_BRIEF.md`、`CAD_AGENT_CHANGELOG.md`

### 5. 命令

`python -m unittest tests.core.test_draw_01_drawing_standard_boundary -v` → 4 tests OK

### 6. 真实 CAD

**否**

### 8. 结论

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| drawing_standard 边界契约 + no-CAD beta 6/6 | `dry_run_valid_plan_only` / `non_cad_only` | **否** |

### 9. 风险

不得将 beta suite pass 说成正式图层已落地或表 C 已抬升；`V-PROOF-44` / `RCAD-23` 仍待后续包。

---

## CFIT-13：P2-WAVE-PARENT-ROLLUP（P2 工装波次父包收口）

**日期**：2026-05-27
**性质**：§4.2 P2 父包；收口 `CFIT-09`…`CFIT-12`；不运行真实 CAD。

### 1. 包名

`CFIT-13-P2-WAVE-PARENT-ROLLUP`

### 2. 修改文件

- `core/agents/commercial_fitout_p2_wave.py`
- `docs/verification/commercial_fitout_p2_wave_acceptance.md`
- `tests/core/test_cfit_13_p2_wave_parent_rollup.py`

### 5. 命令

`python -m unittest tests.core.test_cfit_13_p2_wave_parent_rollup -v` → 6 tests OK

### 6. 真实 CAD

**否**

### 8. 结论

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| P2 工装波次契约 + no-CAD rollup/smoke 复验 | `non_cad_fixture` + contract assert | **否** |

### 9. 风险

不得将父包收口或 fake 4/4 说成工装产品或项目级真实几何已证；`RCAD-10`/`18`/`19` 仍须用户会话。

---

## V-PROOF-63：L4-PROJECT-SLICE（L4 工装项目切片 showcase）

**日期**：2026-05-27
**性质**：§0.1 真实 CAD 实力；双工装脱敏项目切片 rollup；真实 AutoCAD；`CODEX_PREVIEW`；不保存 DWG。

### 1. 包名

`V-PROOF-63-L4-PROJECT-SLICE`

### 2. 修改文件

- `examples/capability_proof/cad_capability_registry.json`
- `docs/verification/capability_showcase/showcase_index.json`
- `showcase/L4/`（双工装项目切片 showcase 索引）
- `docs/planning/任务清单.md`
- `CORE_CONTEXT_BRIEF.md`
- `CAD_AGENT_CHANGELOG.md`

### 3. 关键设计说明

- 将 meeting + reception 两组脱敏项目样本 rollup 作为 L4 项目切片 showcase，不扩大为 L5 交付预备。
- 表 C 主指标仍由 `min(实力指数, L3+片段, showcase)` 决定；本包提升 showcase，但不替代完整施工图能力。

### 4. 新增/修改测试

- 未新增单元测试；以真实 CAD rollup 报告、registry writeback 和 coverage 复跑作为能力证明证据。

### 5. 实际运行的命令和结果

```powershell
& $py scripts\run_project_sample_cad_rollup.py --output-dir output\validation_runs\capability-proof-vproof63-20260527
& $py scripts\run_capability_registry_writeback.py --batch output\validation_runs\capability-proof-vproof63-20260527\writeback_batch.json --apply
& $py scripts\run_capability_coverage.py --output output\validation_runs\capability-lab\cad_capability_coverage.json
```

结果：project rollup 4/4 `geometry_verified`；L4 showcase 2 行；后续机器复跑当前为 `cad_strength_headline_percent=4.35`。

### 6. 是否运行真实 CAD

是

### 7. 机器可读证据路径

- `output/validation_runs/capability-proof-vproof63-20260527/`
- `output/validation_runs/capability-lab/cad_capability_coverage.json`
- `showcase/L4/`

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 双工装项目切片 rollup 4/4 + L4 showcase 登记 | `readback_geometry_verified` / `showcase` | **是** |

### 9. 剩余风险

- L4 showcase 只证明脱敏项目切片，不证明任意真实项目、公司块库、正式图层或 L5 交付预备。
- 后续 registry 增加 smoke/none 行后，覆盖率分母会变大；当前表 C 必须以最新 coverage JSON 为准。

### 10–12. 能力证明附加项

| 字段 | 值 |
| --- | --- |
| registry 行 | `project.sample.*` L4 showcase 行 + 相关 composition showcase 刷新 |
| 当前 coverage | `cad_proof_count=130/276`，`cad_strength_headline_percent=4.35` |
| 本包最高触及 Ladder | **L4**；不得对外提升为 L5 |

---

## V-PROOF-61 / 60：L2-SYMBOL-GALLERY + SHOWCASE-INDEX

**日期**：2026-05-27
**性质**：§0.1 真实 CAD 实力；L2 glyph 画廊 + showcase 索引；真实 AutoCAD；`CODEX_PREVIEW`。

### 1. 包名

`V-PROOF-61-L2-SYMBOL-GALLERY` / `V-PROOF-60-SHOWCASE-INDEX`

### 2. 修改文件

- `docs/verification/capability_showcase/README.md`
- `docs/verification/capability_showcase/showcase_index.json`
- `showcase/L2/`
- `examples/capability_proof/cad_capability_registry.json`
- `docs/planning/任务清单.md`
- `CAD_AGENT_CHANGELOG.md`

### 3. 关键设计说明

- L2 画廊把 desk/chair/table/sofa glyph 真实 CAD 证据串入 showcase 索引。
- showcase 索引只回答“能展示什么”，不能替代 CAD 证明覆盖率或施工图交付能力。

### 4. 新增/修改测试

- 未新增单元测试；以真实 CAD glyph smoke、registry writeback 和 coverage 复跑作为能力证明证据。

### 5. 实际运行的命令和结果

```powershell
& $py scripts\run_symbol_glyph_cad_smoke.py ...
& $py scripts\run_capability_registry_writeback.py --apply ...
& $py scripts\run_capability_coverage.py --output output\validation_runs\capability-lab\cad_capability_coverage.json
```

结果：desk/chair/table/sofa glyph 真实 CAD 通过；当时 showcase_count 从 1 扩至 7，后续 V-PROOF-63 扩至 12。

### 6. 是否运行真实 CAD

是

### 7. 机器可读证据路径

- `output/validation_runs/capability-proof-vproof61-20260527/`
- `showcase/L2/`
- `docs/verification/capability_showcase/showcase_index.json`

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 4 个 L2 glyph showcase 行可展示 | `readback_geometry_verified` / `showcase` | **是** |

### 9. 剩余风险

- L2 glyph 画廊不等于 L3 微场景或 L4 项目切片；不证明任意家具符号或任意块库。

### 10–12. 能力证明附加项

| 字段 | 值 |
| --- | --- |
| registry 行 | desk/chair/table/sofa glyph 相关 showcase / verified 行 |
| 当前 coverage | 以 `output/validation_runs/capability-lab/cad_capability_coverage.json` 为准 |
| 本包最高触及 Ladder | **L2**；索引包本身不提升到 L3/L4 |

---

## V-PROOF-62：L3-FITOUT-SNIPPET（L3 工装微场景 showcase）

**日期**：2026-05-27
**性质**：§0.1 真实 CAD 实力；`V-PROOF-62` + `V-PROOF-60` partial；链式 fitout composition 真实 CAD。

### 1. 包名

`V-PROOF-62-L3-FITOUT-SNIPPET`

### 2. 修改文件

- `docs/verification/capability_showcase/README.md`
- `docs/verification/capability_showcase/showcase_index.json`
- `showcase/L3/fitout_open_office_desk_chair/snippet_index.json`
- `examples/capability_proof/cad_capability_registry.json`（writeback：`showcase`×1 + `verified` 刷新×2）
- `docs/planning/任务清单.md`、`CORE_CONTEXT_BRIEF.md`、`CAD_AGENT_CHANGELOG.md`

### 3. 关键设计说明

- 首条 L3 showcase 绑定 `composition.fitout_open_office_desk_chair`（开放办公工位+椅微场景，非 primitive 矩形 smoke）。
- 同轮刷新 reception / meeting 两行 composition 证据路径（仍为 `verified`）。

### 5. 命令

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_composition_cad_registry.py --manifest examples\capability_proof\fitout_composition_cad_registry_manifest.json --output-dir output\validation_runs\capability-proof-vproof62-20260527
& $py scripts\run_capability_registry_writeback.py --batch output\validation_runs\capability-proof-vproof62-20260527\writeback_batch.json --apply
& $py scripts\run_capability_coverage.py --output output\validation_runs\capability-lab\cad_capability_coverage.json
```

→ 3/3 `geometry_verified`；writeback applied×3；`showcase_count=1`。

### 6. 真实 CAD

**是**（AutoCAD 用户会话；`CODEX_PREVIEW`；不保存 DWG）

### 7. 机器可读证据路径

- `output/validation_runs/capability-proof-vproof62-20260527/composition_cad_registry_report.json`
- `output/validation_runs/capability-proof-vproof62-20260527/composition_cad/composition_cad_check_report.json`
- Showcase 行报告：`.../fitout_open_office_desk_chair_micro_scene/verification_reports/verification_report_001.json`

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 3 工装微场景 composition CAD + 1 行 showcase 登记 | `readback_geometry_verified` | **是**（3 case；showcase 行 8 handles） |

### 9. 剩余风险

- 表 C 主指标仍受 showcase 分母约束（**0.38%**）；须继续 `V-PROOF-60`/`61` 扩册，不得声称 L5 施工图。
- `V-PROOF-34` / `RCAD-25` block-first 仍 pending。

### 10–12. 能力证明附加（registry / 覆盖率 / Ladder）

| 字段 | 值 |
| --- | --- |
| registry 行 | `composition.fitout_open_office_desk_chair` → `showcase`；另 2 composition 行 `verified` 刷新 |
| 回写后 `cad_strength_headline_percent` | **0.38%** |
| 本包最高触及 Ladder | **L3**（showcase 片段）；不抬高 L4/L5 对外声称 |

---

## CFIT-12：FITOUT-SUBSCENE-OBJECT-CAD-SMOKE（子场景代表对象 CAD smoke）

**日期**：2026-05-27
**性质**：§4.2 P2；`V-PROOF-25`；meeting/reception 代表 catalog 对象 CAD smoke；不运行真实 CAD。

### 1. 包名

`CFIT-12-FITOUT-SUBSCENE-OBJECT-CAD-SMOKE`

### 2. 修改文件

- `examples/capability_proof/fitout_subscene_object_cad_smoke_manifest.json`
- `core/verification/fitout_subscene_object_cad_smoke.py`
- `scripts/run_fitout_subscene_object_cad_smoke.py`
- `docs/verification/cfit_12_fitout_subscene_object_cad_smoke_boundary.md`
- `tests/core/test_cfit_12_fitout_subscene_object_cad_smoke.py`

### 5. 命令

`python -m unittest tests.core.test_cfit_12_fitout_subscene_object_cad_smoke` → 6 tests OK

### 6. 真实 CAD

**否**

### 8. 结论

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| meeting/reception 各 2 代表对象 fake readback pass | unit_test_readback | **否**（项目/真实会话级） |

### 9. 风险

`RCAD-18` 真实 CAD 待用户会话；不得将 4/4 fake smoke 说成全 catalog 或项目样本已 verified。

---

## CFIT-11：THREE-SAMPLE-BOUNDARY-SYNC（三样本 boundary/rollup 口径同步）

**日期**：2026-05-27
**性质**：§4.2 P2；`CFIT-09`/`10` 后收口 product boundary 与 LCAD-08 rollup 登记一致性；不运行真实 CAD。

### 1. 包名

`CFIT-11-THREE-SAMPLE-BOUNDARY-SYNC`

### 2. 修改文件

- `agents/commercial_fitout/capabilities/product_alpha_boundary.json`（+`deidentified_project_samples[]`）
- `core/schemas/commercial_fitout_product_alpha_boundary.schema.json`
- `core/agents/commercial_fitout_product_boundary.py`、`fitout_sample_specs.py`
- `docs/verification/cfit_11_three_sample_product_boundary_sync.md`、`project_sample_cad_boundaries.md`
- `tests/core/test_cfit_11_three_sample_boundary_sync.py`、`tests/agents/test_commercial_fitout_product_boundary.py`

### 5. 命令

`python -m unittest tests.core.test_cfit_11_three_sample_boundary_sync tests.agents.test_commercial_fitout_product_boundary tests.core.test_project_sample_cad_rollup` → 14 tests OK

### 6. 真实 CAD

**否**

### 8. 结论

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 三子场景样本与 boundary/rollup manifest 口径一致 | non_cad_fixture + unit_test | **否**（项目级） |

### 9. 风险

`RCAD-10` / `RCAD-19` 仍待真实 AutoCAD；fake rollup 4/4 不得扩大为全子场景真实几何证明。

---

## CFIT-10：RECEPTION-PROJECT-SAMPLE（前台接待脱敏样本）

**日期**：2026-05-27
**性质**：§4.2 P2；第三组工装脱敏样本；三子场景样本路径齐全。

### 1. 包名

`CFIT-10-RECEPTION-PROJECT-SAMPLE`

### 2. 修改文件

- `projects/commercial_fitout_reception_sample/**`
- `examples/workflows/commercial_fitout_reception_sample_confirmation_loop.json`
- `core/agents/fitout_sample_specs.py`（+reception）
- `project_sample_cad_rollup.json`、`project_sample_cad_rollup.py`
- `tests/core/test_cfit_10_reception_sample.py`

### 5. 命令

`python -m unittest tests.core.test_cfit_10_reception_sample tests.core.test_project_sample_cad_rollup` → pass

### 6. 真实 CAD

**否**

### 9. 风险

`RCAD-19` 待用户会话 rollup；product boundary 三样本口径已在 `CFIT-11` 同步。

---

## CFIT-09：SECOND-PROJECT-SAMPLE（第二组工装脱敏样本）

**日期**：2026-05-27
**性质**：§4.2 P2 工装波次首包；第二脱敏项目样本路径定稿，不运行真实 CAD。

### 1. 本次开发包名

`CFIT-09-SECOND-PROJECT-SAMPLE`：`commercial_fitout_meeting_sample` 脱敏样本 + rollup 登记。

### 2. 修改文件列表

| 类型 | 文件 |
| --- | --- |
| 新增 | `projects/commercial_fitout_meeting_sample/**` |
| 新增 | `examples/workflows/commercial_fitout_meeting_sample_confirmation_loop.json` |
| 新增 | `core/agents/fitout_sample_specs.py` |
| 修改 | `core/agents/commercial_fitout_sample_confirmation.py`、`commercial_fitout_cad_smoke.py` |
| 修改 | `core/project_samples/project_sample_cad_rollup.py`、`examples/cad_regression/project_sample_cad_rollup.json` |
| 新增 | `tests/core/test_cfit_09_meeting_sample.py` |
| 新增 | `docs/verification/cfit_09_second_project_sample_boundary.md` |

### 3. 关键设计说明

- 会议室子场景样本与开放办公样本共用 confirmation / CAD smoke 代码，经 `fitout_sample_specs` 区分 workflow 与 bundle 文件名。
- `project_sample_cad_rollup` 现含 3 个样本；`REQUIRED_SAMPLE_IDS` 含 `commercial_fitout_meeting_sample`。

### 4. 新增/修改测试

| 测试 | 覆盖点 |
| --- | --- |
| `tests.core.test_cfit_09_meeting_sample` | 协议扫描、pre-confirmation、边界文档 |
| `tests.core.test_project_sample_cad_rollup` | 3 样本 manifest + fake geometry_verified |

### 5. 实际运行的命令和结果

| 命令 | 结果 |
| --- | --- |
| `python -m unittest tests.core.test_cfit_09_meeting_sample` | 4 tests OK |
| `python -m unittest tests.core.test_project_sample_cad_rollup` | 3 samples OK |

### 6. 是否运行真实 CAD

**否**。

### 7. 机器可读证据路径

| 路径 | 说明 |
| --- | --- |
| `projects/commercial_fitout_meeting_sample/sample.manifest.json` | 脱敏样本清单 |
| `examples/cad_regression/project_sample_cad_rollup.json` | 第三样本登记 |

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 第二工装脱敏样本路径已定稿 | protocol + rollup manifest | **否**（项目级） |

### 9. 剩余风险

- `RCAD-10` 需在用户 AutoCAD 会话跑 rollup 真实 CAD。
- `CFIT-10`~`13` 尚未展开。

---

## LCAD-14：GUARD-FULL-CAD（Guard 全链路 strict 包装）

**日期**：2026-05-27
**性质**：一键推进代码轨；LCAD-03 守卫链 strict 子报告包装，不运行真实 CAD。

### 1. 本次开发包名

`LCAD-14-GUARD-FULL-CAD`：write guard + negative CAD + capability probe 的 strict rollup。

### 2. 修改文件列表

| 类型 | 文件 |
| --- | --- |
| 新增 | `core/verification/guard_full_cad_runner.py` |
| 新增 | `scripts/run_guard_full_cad_runner.py` |
| 新增 | `tests/core/test_guard_full_cad_runner.py` |
| 新增 | `docs/verification/guard_full_cad_boundary.md` |
| 修改 | `docs/planning/任务清单.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md`、本文 |

### 3. 关键设计说明

- 三段子报告目录：`subreports/write_guard`、`subreports/negative_cad`、`subreports/capability_probe`。
- 顶层 `strict_gate` 复用 `validate_capability_probe_evidence()` 与 `session_guard.status=consistent`。
- `--real-cad` 预留给 `RCAD-21`；本包证据为 fake strict pass。

### 4. 新增/修改测试

| 测试 | 覆盖点 |
| --- | --- |
| `tests.core.test_guard_full_cad_runner` | fake strict pass、strict_gate 失败路径、边界文档 |

### 5. 实际运行的命令和结果

| 命令 | 结果 |
| --- | --- |
| `python -m unittest tests.core.test_guard_full_cad_runner` | 3 tests OK |
| `python scripts/run_guard_full_cad_runner.py --output-dir output/validation_runs/lcad-14-guard-full-no-cad` | `status=pass` |

### 6. 是否运行真实 CAD

**否**（FakeCadDriver strict rollup）。

### 7. 机器可读证据路径

| 路径 | 说明 |
| --- | --- |
| `output/validation_runs/lcad-14-guard-full-no-cad/guard_full_cad_report.json` | 顶层 strict rollup |
| `.../subreports/capability_probe/cad_capability_probe.json` | `cad_capability_verified` + `session_guard` |
| `.../subreports/negative_cad/negative_cad_runner_report.json` | `negative_guard_verified` |

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| LCAD-03 guard 链 strict 字段可机器断言 | fake strict pass | **否** |

### 9. 剩余风险

- 真实 AutoCAD 会话 strict 仍待 `RCAD-21`（`run_guard_full_cad_runner.py --real-cad`）。
- §4.1 活跃队列已收口；§4.2 积压包尚未逐行展开。

**能力证明附加项**：不适用（未改 registry）。

---

## LCAD-13：SESSION-SNAPSHOT-CAD（能力探针会话快照）

**日期**：2026-05-27
**性质**：一键推进代码轨；capability probe 接入 ActiveDocument before/after snapshot，不运行真实 CAD。

### 1. 本次开发包名

`LCAD-13-SESSION-SNAPSHOT-CAD`：真实 CAD 会话 before/after snapshot 断言（capability probe 扩展）。

### 2. 修改文件列表

| 类型 | 文件 |
| --- | --- |
| 修改 | `core/verification/cad_capability_probe.py` |
| 修改 | `core/verification/cad_session_guard.py` |
| 修改 | `core/verification/evidence_contract.py` |
| 修改 | `tests/core/cad_validation_payloads.py` |
| 修改 | `tests/core/test_cad_capability_probe.py` |
| 新增 | `tests/core/test_session_snapshot_capability_probe_boundary.py` |
| 新增 | `docs/verification/session_snapshot_capability_probe_boundary.md` |
| 修改 | `docs/planning/任务清单.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md`、本文 |

### 3. 关键设计说明

- 写入前 `capture_active_document_snapshot(..., phase="after_connect")`，写入后 `after_write`，再 `build_session_guard_report`。
- `cad_capability_verified` 必须 `session_guard.status=consistent`；多文档打开时探针失败并阻断 verified。
- 同目录写出 `active_document_snapshot.json`，供 `RCAD-21` / `LCAD-14` 后续 strict 包装复用字段。

### 4. 新增/修改测试

| 测试 | 覆盖点 |
| --- | --- |
| `tests.core.test_session_snapshot_capability_probe_boundary` | session_guard 字段、snapshot 工件、多文档阻断、边界文档 |
| `tests.core.test_cad_capability_probe` | 成功探针含 session_guard |
| `tests.core.cad_validation_payloads` | validation runner mock 含 consistent session_guard |

### 5. 实际运行的命令和结果

| 命令 | 结果 |
| --- | --- |
| `python -m unittest tests.core.test_cad_capability_probe tests.core.test_cad_session_guard tests.core.test_session_snapshot_capability_probe_boundary` | 12 tests OK |
| `python -m unittest tests.core.test_cad_validation_runner ...` | 15 tests OK（含 session_guard 门禁） |
| `python scripts/run_cad_capability_probe.py --output-dir output/validation_runs/lcad-13-session-snapshot-no-cad` | `status=cad_capability_verified` |
| `python scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings` | 0 findings |

### 6. 是否运行真实 CAD

**否**（FakeCadDriver + no-CAD 探针证据）。

### 7. 机器可读证据路径

| 路径 | 说明 |
| --- | --- |
| `output/validation_runs/lcad-13-session-snapshot-no-cad/cad_capability_probe.json` | `session_guard.status=consistent` |
| `output/validation_runs/lcad-13-session-snapshot-no-cad/active_document_snapshot.json` | 会话快照工件 |

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| capability probe 已输出可断言的 session_guard 字段 | `cad_capability_verified`（fake/no-CAD） | **否** |

### 9. 剩余风险

- 真实 AutoCAD 会话下的 snapshot 一致性仍待 `LCAD-14` / `RCAD-21` 全链路 strict 复验。
- `session_guard.status=consistent` 不等于任意 CAD_PLAN 或正式图层已通过 guard。

**能力证明附加项**：不适用（未改 registry）。

---

## LCAD-12：HATCH-COM（structured deferred）

**日期**：2026-05-27
**性质**：一键推进代码轨；hatch 能力槽位安全收口，不运行真实 CAD。

### 1. 本次开发包名

`LCAD-12-HATCH-COM`：hatch COM 最小实现或 structured deferred。本轮选择 structured deferred。

### 2. 修改文件列表

| 类型 | 文件 |
| --- | --- |
| 修改 | `core/cad_io/autocad_com.py` |
| 修改 | `core/verification/fake_cad_driver.py` |
| 修改 | `tests/core/test_autocad_write_guard.py` |
| 新增 | `tests/core/test_hatch_com_deferred_boundary.py` |
| 新增 | `docs/verification/hatch_com_deferred_boundary.md` |
| 修改 | `docs/planning/任务清单.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md`、本文 |

### 3. 关键设计说明

- `AutoCADComDriver.draw_hatch()` 与 `FakeCadDriver.draw_hatch()` 都先走 preview-only 写入守卫。
- 预览层调用只返回 structured deferred：`primitive=hatch`、`status=deferred`、`failure_category=hatch_unverified`、`created_handles=[]`、`geometry_verified=false`。
- 真实 COM driver 不调用 `AddHatch`，因此不会制造未回读的 hatch handle。

### 4. 新增/修改测试

| 测试 | 覆盖点 |
| --- | --- |
| `tests.core.test_autocad_write_guard` | formal layer 在 hatch 写入前被拦截；预览层 hatch 不调用 `AddHatch` |
| `tests.core.test_hatch_com_deferred_boundary` | fake driver hatch deferred、不创建实体；边界文档包含声明口径 |

### 5. 实际运行的命令和结果

| 命令 | 结果 |
| --- | --- |
| `python -m unittest tests.core.test_autocad_write_guard tests.core.test_hatch_com_deferred_boundary` | RED：5 errors（缺 `draw_hatch` 与边界文档）→ GREEN：8 tests OK |
| `python -m unittest tests.core.test_autocad_write_guard tests.core.test_hatch_com_deferred_boundary tests.core.test_entity_level_probe tests.core.test_cad_block_attribute_hatch_boundary tests.core.test_planmd_governance` | 25 tests OK |
| `python -m unittest discover -s tests` | 沙箱内 685 tests 跑到 2 个 Windows Temp ACL errors；沙箱外重跑 685 tests OK |
| `python scripts/run_repo_audit.py --max-python-lines 500 --fail-on-findings` | pass，0 findings |
| `git diff --check` | pass；仅 LF→CRLF 提示 |

### 6. 是否运行真实 CAD

否。

### 7. 机器可读证据路径

| 类型 | 路径 |
| --- | --- |
| 证据文档 | `docs/verification/hatch_com_deferred_boundary.md` |
| 运行输出 | 无独立 `output/validation_runs`；本包是 driver contract + focused tests |

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| hatch 入口已有显式 structured deferred 和写入守卫 | `non_cad_only` / `structured_deferred` | **否** |

### 9. 剩余风险

- 真实 AutoCAD hatch COM 写入、boundary loop、created-handle readback 和 hatch 几何对照仍未实现。
- `V-PROOF-53` 只能登记为 deferred / 可读失败分类，不能回写为 verified。

### 10. 能力登记表（registry）

| 字段 | 内容 |
| --- | --- |
| `registry_path` | `examples/capability_proof/cad_capability_registry.json` |
| 本包触及行 | 无行变更 |

### 11. CAD 证明覆盖率

| 字段 | 内容 |
| --- | --- |
| 回写前 `cad_proof_coverage_rate` | 48.85% |
| 回写后 `cad_proof_coverage_rate` | 未复跑；无 registry 行变更，预期不变 |
| 覆盖率 JSON 路径 | 沿用 `output/validation_runs/vproof-33-readability-rows/cad_capability_coverage.json` |

### 12. 展示等级 Ladder

| 字段 | 内容 |
| --- | --- |
| 本包最高触及 Ladder | L1 槽位边界 |
| 是否对外提升 Ladder 声称 | **否**；本包只收口 hatch deferred，不新增几何展示能力 |

---

## V-PROOF-33：READABILITY-REPORT-ROWS（可读性状态登记行绑定）

**日期**：2026-05-27
**性质**：能力证明包；只绑定 non-CAD readability 状态行，不新增 `geometry_verified`。

### 1. 本次开发包名

`V-PROOF-33-READABILITY-REPORT-ROWS`：把 5 个 `READABILITY_STATUSES` 固定进 capability registry。

### 2. 修改文件列表

| 类型 | 文件 |
| --- | --- |
| 修改 | `core/schemas/cad_capability_registry.schema.json` |
| 修改 | `examples/capability_proof/cad_capability_registry.json` |
| 修改 | `tests/core/test_capability_readability.py` |
| 修改 | `docs/planning/任务清单.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md`、本文 |
| 新增证据 | `output/validation_runs/vproof-33-readability-rows/capability_readability_report.json` |
| 新增证据 | `output/validation_runs/vproof-33-readability-rows/cad_capability_coverage.json` |

### 3. 关键设计说明

- registry 新增 `symbol.readability_status.*` 5 行，对应 `symbol_readable`、`visual_review_required`、`fallback_component_preview`、`fallback_bbox_placeholder`、`deferred_unsupported_symbol`。
- 这些行全部是 `claim_level=smoke` + `benchmark_pass_non_cad`，只证明可读性分类状态已登记，不证明 CAD 几何准确。
- schema 新增 `readability_status` 字段，避免状态只藏在 `capability_id` 字符串里。

### 4. 新增/修改测试

| 测试 | 覆盖点 |
| --- | --- |
| `tests.core.test_capability_readability` | 先 RED：registry 缺 5 个 readability rows；后 GREEN：5 状态齐全、schema valid、claim contract valid |

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_capability_readability
```

RED：新增测试先失败，缺少 5 个 `symbol.readability_status.*` 行。

GREEN：`2 tests OK`。

```powershell
& $py scripts\run_capability_readability_report.py --output-dir output\validation_runs\vproof-33-readability-rows --guard-report output\validation_runs\rcad-20-negative-cad-20260527-escalated\negative_cad_runner_report.json
& $py scripts\run_capability_coverage.py --output output\validation_runs\vproof-33-readability-rows\cad_capability_coverage.json
```

结果：`total_count=262`、`verified_count=128`、`smoke_count=56`、`cad_proof_coverage_percent=48.85`；readability report `status=pass`，`verified_guard_count=1`。

```powershell
& $py -m unittest tests.core.test_capability_readability tests.core.test_cad_capability_registry_schema tests.core.test_capability_coverage tests.core.test_schema_validation tests.core.test_planmd_governance
& $py -m unittest discover -s tests
& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
git diff --check
```

结果：focused `29 tests OK`；全量 `674 tests OK`；repo audit `finding_count=0`；`git diff --check` 无空白错误（仅 CRLF warning）。

### 6. 是否运行真实 CAD

否。本包只做 registry/schema/readability 报告绑定；真实 CAD guard 只引用既有 `RCAD-20` 报告。

### 7. 机器可读证据路径

| 证据 | 路径 |
| --- | --- |
| 可读性报告 | `output/validation_runs/vproof-33-readability-rows/capability_readability_report.json` |
| 覆盖率报告 | `output/validation_runs/vproof-33-readability-rows/cad_capability_coverage.json` |

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 5 个 readability 状态已进入 registry | `benchmark_pass_non_cad` | **否** |
| CAD 证明覆盖率复算完成 | `registry_coverage_summary` | **否** |
| guard-only 证据仍只来自 RCAD-20 | `negative_guard_verified` | **否** |

### 9. 剩余风险

- 本包增加了分母，不增加 verified；覆盖率从 49.81% 降到 48.85% 是正常口径。
- `V-PROOF-34` block-first tier 与 fitout composition CAD 仍需后续推进。

### 10. 能力登记表（registry）

| 字段 | 内容 |
| --- | --- |
| `registry_path` | `examples/capability_proof/cad_capability_registry.json` |
| 本包触及行 | 新增 5 个 `symbol.readability_status.*` 行 |

| `capability_id` | `claim_level`（前→后） | `ladder_level` | `evidence.report_path` |
| --- | --- | --- | --- |
| `symbol.readability_status.symbol_readable` | absent → smoke | L2 | `output/validation_runs/vproof-33-readability-rows/capability_readability_report.json` |
| `symbol.readability_status.visual_review_required` | absent → smoke | L2 | `output/validation_runs/vproof-33-readability-rows/capability_readability_report.json` |
| `symbol.readability_status.fallback_component_preview` | absent → smoke | L2 | `output/validation_runs/vproof-33-readability-rows/capability_readability_report.json` |
| `symbol.readability_status.fallback_bbox_placeholder` | absent → smoke | L2 | `output/validation_runs/vproof-33-readability-rows/capability_readability_report.json` |
| `symbol.readability_status.deferred_unsupported_symbol` | absent → smoke | L2 | `output/validation_runs/vproof-33-readability-rows/capability_readability_report.json` |

### 11. CAD 证明覆盖率

| 字段 | 内容 |
| --- | --- |
| 回写前 `cad_proof_coverage_rate` | 49.81%（128/257） |
| 回写后 `cad_proof_coverage_rate` | 48.85%（128/262） |
| 覆盖率 JSON 路径 | `output/validation_runs/vproof-33-readability-rows/cad_capability_coverage.json` |

### 12. 展示等级 Ladder

| 字段 | 内容 |
| --- | --- |
| 本包最高触及 Ladder | L2 symbol readability |
| 是否对外提升 Ladder 声称 | 否；只登记可读性状态，不提升几何能力等级 |

---

## RCAD-20：NEGATIVE-CAD（真实 CAD 负向安全补验）

**日期**：2026-05-27
**性质**：CAD 补验包；只补真实 CAD 负向安全守卫，不新增 `geometry_verified`。

### 1. 本次开发包名

`RCAD-20-NEGATIVE-CAD`：对 `LCAD-10.3` 的负向 runner 执行真实 AutoCAD 会话补验。

### 2. 修改文件列表

| 类型 | 文件 |
| --- | --- |
| 修改 | `docs/planning/任务清单.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md`、`CORE_RESTRUCTURE_PLAN.md`、`docs/verification/negative_cad_safety_acceptance.md`、`docs/verification/negative_cad_safety_boundaries.md`、本文 |
| 新增证据 | `output/validation_runs/rcad-20-negative-cad-20260527-escalated/negative_cad_runner_report.json` |
| 新增证据 | `output/validation_runs/rcad-20-negative-cad-20260527-escalated/cad_capability_coverage_after_rcad20.json`、`output/validation_runs/rcad-20-negative-cad-20260527-escalated/cad_capability_coverage_after_doc_sync.json` |

### 3. 关键设计说明

- 先在沙箱身份运行 `--real-cad`，得到 `external_blocker`，用于证明沙箱无法代表用户桌面 CAD 会话。
- 再在用户 CAD 会话下补跑同一 runner，要求负向 fixture、write guard、session guard、no handles/no save/no delete/no formal-layer delta 全部通过。
- `negative_guard_verified` 仍被限定为 guard-only；覆盖率复跑后几何证明仍为 `128/257 = 49.81%`。

### 4. 新增/修改测试

| 测试 | 覆盖点 |
| --- | --- |
| `tests.core.test_evidence_trend`、`test_evidence_classifier`、`test_capability_coverage`、`test_schema_validation`、`test_planmd_governance` | 本轮文档、schema、覆盖率与趋势口径不漂移 |

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_evidence_trend tests.core.test_evidence_classifier tests.core.test_capability_coverage tests.core.test_schema_validation tests.core.test_planmd_governance tests.core.test_lcad_10_parent_rollup tests.core.test_negative_cad_safety_boundaries_doc
```

结果：`34 tests OK`。

```powershell
& $py -m unittest discover -s tests
```

结果：隔离 `tempfile` 到仓库 `output/test_tmp_runner_manual` 后，`673 tests OK`。

```powershell
& $py scripts\self_check.py
& $py scripts\render_preview.py --check
```

结果：`self_check` pass；截图依赖 ready，当前窗口级 AutoCAD 截图探测不可用，截图仍为 `visual_aid_only`。

```powershell
& $py scripts\run_negative_cad_runner.py --real-cad --output-dir output\validation_runs\rcad-20-negative-cad-20260527
```

结果：沙箱身份 `status=external_blocker`。

```powershell
& $py scripts\run_negative_cad_runner.py --real-cad --output-dir output\validation_runs\rcad-20-negative-cad-20260527-escalated
```

结果：用户 CAD 会话 `status=pass`、`evidence_state=negative_guard_verified`、`created_handles=[]`、`preview_layer_entity_delta=0`、`modelspace_entity_delta=0`，且不保存、不删除、不修改正式图层。

```powershell
& $py scripts\run_capability_coverage.py --output output\validation_runs\rcad-20-negative-cad-20260527-escalated\cad_capability_coverage_after_doc_sync.json
```

结果：`verified_count=128`、`total_count=257`、`cad_proof_coverage_percent=49.81`。

### 6. 是否运行真实 CAD

是。沙箱身份先得到 `external_blocker`；用户 CAD 会话补跑通过。未保存 DWG，未删除实体，未修改正式图层。

### 7. 机器可读证据路径

| 证据 | 路径 |
| --- | --- |
| 沙箱身份 blocker | `output/validation_runs/rcad-20-negative-cad-20260527/negative_cad_runner_report.json` |
| 真实 CAD 负向安全 pass | `output/validation_runs/rcad-20-negative-cad-20260527-escalated/negative_cad_runner_report.json` |
| 补验后覆盖率 | `output/validation_runs/rcad-20-negative-cad-20260527-escalated/cad_capability_coverage_after_rcad20.json`、`output/validation_runs/rcad-20-negative-cad-20260527-escalated/cad_capability_coverage_after_doc_sync.json` |

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 真实 CAD 负向 runner 安全守卫通过 | `negative_guard_verified` | **否** |
| 负向补验没有新增 handles、保存 DWG、删除实体或修改正式层 | `cad_safety_guard` | **否** |
| 覆盖率复跑仍为 128/257，未新增几何证明 | `registry_coverage_summary` | **否** |

### 9. 剩余风险

- `negative_guard_verified` 不证明任何正向 CAD_PLAN 几何准确。
- `V-PROOF-50` / `V-PROOF-51` 的 registry/document 行绑定仍待后续能力证明包。
- 下一项 CAD 补验顺位已切到 `RCAD-15-SYMBOL-GLYPH-SOFA`。

### 10. 能力登记表（registry）

| 字段 | 内容 |
| --- | --- |
| `registry_path` | `examples/capability_proof/cad_capability_registry.json` |
| 本包触及行 | 无行变更；本包只新增 guard-only 真实 CAD 证据，不回写 `geometry_verified` |

| `capability_id` | `claim_level`（前→后） | `ladder_level` | `evidence.report_path` |
| --- | --- | --- | --- |
| 无行变更 | unchanged | 不适用 | 不适用 |

### 11. CAD 证明覆盖率

| 字段 | 内容 |
| --- | --- |
| 回写前 `cad_proof_coverage_rate` | 49.81%（128/257） |
| 回写后 `cad_proof_coverage_rate` | 49.81%（128/257） |
| 覆盖率 JSON 路径 | `output/validation_runs/rcad-20-negative-cad-20260527-escalated/cad_capability_coverage_after_doc_sync.json` |

### 12. 展示等级 Ladder

| 字段 | 内容 |
| --- | --- |
| 本包最高触及 Ladder | L1/L2 安全守卫与证据治理层 |
| 是否对外提升 Ladder 声称 | 否；只证明真实 CAD 负向安全守卫，不提升几何能力等级 |

---

## NEG-CAD-PROOF-SYNC：负向安全 runner + 覆盖率可读证据 + composition 收口

**日期**：2026-05-27
**性质**：Codex 验证优化包；覆盖 `LCAD-10.3`、`V-PROOF-33` partial、composition 模板收口。

### 1. 本次开发包名

`NEG-CAD-PROOF-SYNC`：

- `LCAD-10.3-NEGATIVE-CAD-RUNNER`：负向真实 CAD 安全 runner。
- `V-PROOF-33-READABILITY-REPORT-ROWS`：覆盖率可读证据报告先行，registry 行绑定待后续包。
- composition 模板收口：保留 JSON catalog + schema，预览全局默认无标注。

### 2. 修改文件列表

| 类型 | 文件 |
| --- | --- |
| 新增 | `core/verification/negative_cad_runner.py` |
| 新增 | `scripts/run_negative_cad_runner.py` |
| 新增 | `tests/core/test_negative_cad_runner.py` |
| 新增 | `core/verification/capability_readability.py` |
| 新增 | `scripts/run_capability_readability_report.py` |
| 新增 | `tests/core/test_capability_readability.py` |
| 修改 | `core/cad_io/autocad_com.py` |
| 修改 | `core/drawing_analysis/shell_confirmation.py` |
| 修改 | `core/verification/negative_cad_plans.py` |
| 修改 | `core/verification/evidence_vocabulary.py` |
| 修改 | `core/schemas/cad_capability_registry.schema.json` |
| 修改 | `core/composition_engine/drawing_policy.py` |
| 修改 | `tests/core/test_autocad_write_guard.py` |
| 修改 | `tests/core/test_composition_engine.py` |
| 修改 | `CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CORE_RESTRUCTURE_PLAN.md`、`CAD_AGENT_CHANGELOG.md`、`CAD_AGENT_ISSUES.md`、`docs/planning/任务清单.md`、本文 |

### 3. 关键设计说明

- 负向 runner 统一汇总 8 个 negative `CAD_PLAN` fixture、write guard、ActiveDocument snapshot 和 no-handle/no-save/no-delete/no-formal-layer 证据。
- `AutoCADComDriver` 的写入守卫前移到 COM `Add*` 之前，避免正式层写入被拒绝前已经创建实体。
- `shell_confirmation.py` 对临时 JSON 清理 `PermissionError` 做兜底，避免沙箱/ACL 清理失败掩盖已成功的模型构建。
- 新增 `negative_guard_verified` 作为安全守卫证据态；该状态不计入 `geometry_verified` 或 CAD 几何覆盖率。
- 覆盖率可读报告把 registry + coverage 拆成 geometry verified、guard-only、deferred、smoke、none、blocked，供状态页引用。
- composition 模板采用 `libraries/composition_templates/catalog.json` + `core/schemas/composition_template_catalog.schema.json`；预览策略全局默认无标注，运行时对象级 `include_label` / `include_dimensions` 被忽略。

### 4. 新增/修改测试

| 测试 | 覆盖点 |
| --- | --- |
| `tests/core/test_autocad_write_guard.py` | 正式图层 COM 写入必须在 `AddLine` 前被拦截 |
| `tests/core/test_negative_cad_runner.py` | fake/no-CAD 负向 runner 无 handles、无保存、无正式层 delta |
| `tests/core/test_capability_readability.py` | 可读覆盖率报告分组 geometry / guard-only / unverified |
| `tests/core/test_composition_engine.py` | composition 对象级标注覆盖被全局无标注策略忽略 |
| `tests/core/test_composition_catalog.py` | JSON catalog + schema 加载、类型与策略约束 |

### 5. 实际运行的命令和结果

```powershell
$env:PYTHONIOENCODING = "utf-8"
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_autocad_write_guard tests.core.test_cad_write_guard tests.core.test_negative_cad_plans tests.core.test_write_guard_cad_runner tests.core.test_negative_cad_runner tests.core.test_capability_readability tests.core.test_capability_coverage tests.core.test_composition_engine tests.core.test_composition_catalog tests.core.test_schema_validation
```

结果：`35 tests OK`。

自检阶段又跑了全量回归；普通 `unittest discover` 在当前沙箱中会因 Python `tempfile` 随机目录 ACL 报 `PermissionError`，隔离 `tempfile` 后：

```powershell
& $py -c "<set safe tempfile under output/test_tmp_runner, then unittest discover('tests')>"
```

结果：`667 tests OK`。

```powershell
& $py scripts\run_negative_cad_runner.py --output-dir output\validation_runs\neg-cad-proof-sync\negative-runner-fake-final
```

结果：`status=pass`、`mode=fake_cad`、`evidence_state=negative_guard_verified`、`created_handles=[]`、`blocked_attempt_count=4`、`preview_layer_entity_delta=0`、`modelspace_entity_delta=0`。

```powershell
& $py scripts\run_negative_cad_runner.py --real-cad --output-dir output\validation_runs\neg-cad-proof-sync\negative-runner-real
```

结果：`status=external_blocker`，当前沙箱身份看不到用户 AutoCAD COM；不新增真实 CAD 几何结论。后续 `RCAD-20` 已在用户 CAD 会话补验通过，仍为 guard-only。

```powershell
& $py scripts\run_capability_coverage.py --output output\validation_runs\neg-cad-proof-sync\cad_capability_coverage-final.json
& $py scripts\run_capability_readability_report.py --output-dir output\validation_runs\neg-cad-proof-sync\capability-readability-final --guard-report output\validation_runs\neg-cad-proof-sync\negative-runner-fake-final\negative_cad_runner_report.json
```

结果：coverage `128/257 = 49.81%`；readability summary 中 `verified_geometry_count=128`、`verified_guard_count=1`。

### 6. 是否运行真实 CAD

否。包内已尝试 `--real-cad`，但当时 Codex 沙箱身份无法连接用户桌面 AutoCAD COM，报告为 `external_blocker`。后续独立 `RCAD-20` 包已完成真实 CAD 负向安全补验；本包没有新增 `geometry_verified` 结论。

### 7. 机器可读证据路径

| 证据 | 路径 |
| --- | --- |
| fake/no-CAD 负向 runner | `output/validation_runs/neg-cad-proof-sync/negative-runner-fake-final/negative_cad_runner_report.json` |
| real-CAD 尝试 blocker | `output/validation_runs/neg-cad-proof-sync/negative-runner-real/negative_cad_runner_report.json` |
| CAD 覆盖率 | `output/validation_runs/neg-cad-proof-sync/cad_capability_coverage-final.json` |
| 覆盖率可读报告 | `output/validation_runs/neg-cad-proof-sync/capability-readability-final/capability_readability_report.json` |

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 负向 runner 在 fake/no-CAD 模式证明无 handles、无保存、无删除、无正式层 delta | `negative_guard_verified` | **否** |
| 正式图层 COM 写入在 `Add*` 前被拦截 | `unit_test_guard` | **否** |
| registry CAD 证明覆盖率可读分组已生成 | `registry_coverage_summary` | **否** |
| composition 预览全局无标注策略已锁定 | `unit_test_policy` | **否** |

### 9. 剩余风险

- `RCAD-20-NEGATIVE-CAD` 已在用户 AutoCAD 会话下补验通过；该结论仍是 guard-only，不是几何证明。
- `negative_guard_verified` 只证明安全守卫，不证明几何绘制准确。
- `V-PROOF-33` 已在后续能力证明包完成 registry rows / 文档行绑定；本包自身仍只提供先行报告。
- `LCAD-10.4-NEGATIVE-BOUNDARY-DOC` 已在后续一键推进包完成；下一步代码轨为 `LCAD-10.5-PARENT-ROLLUP`。

### 10. 能力登记表（registry）

| 字段 | 内容 |
| --- | --- |
| `registry_path` | `examples/capability_proof/cad_capability_registry.json` |
| 本包触及行 | 无 registry 行变更；本包只新增 guard-only 外部报告与可读覆盖率报告 |

| `capability_id` | `claim_level`（前→后） | `ladder_level` | `evidence.report_path` |
| --- | --- | --- | --- |
| 无行变更 | unchanged | 不适用 | 不适用 |

### 11. CAD 证明覆盖率

| 字段 | 内容 |
| --- | --- |
| 回写前 `cad_proof_coverage_rate` | 49.81%（128/257） |
| 回写后 `cad_proof_coverage_rate` | 49.81%（128/257） |
| 覆盖率 JSON 路径 | `output/validation_runs/neg-cad-proof-sync/cad_capability_coverage-final.json` |
| guard-only 可读证据 | `verified_guard_count=1`，不计入几何覆盖率 |

### 12. 展示等级 Ladder

| 字段 | 内容 |
| --- | --- |
| 本包最高触及 Ladder | L1/L2 安全与证据治理层 |
| 是否对外提升 Ladder 声称 | 否；只提升负向安全 runner 和覆盖率可读性，不提升几何能力等级 |

---

## LCAD-10.4：NEGATIVE-BOUNDARY-DOC（负向 CAD 安全边界文档）

**日期**：2026-05-27

### 1. 本次开发包名

`LCAD-10.4-NEGATIVE-BOUNDARY-DOC`：负向与安全边界扫描文档。

### 2. 修改文件列表

| 类型 | 文件 |
| --- | --- |
| 新增 | `docs/verification/negative_cad_safety_boundaries.md` |
| 新增 | `tests/core/test_negative_cad_safety_boundaries_doc.py` |
| 修改 | `docs/planning/任务清单.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CORE_RESTRUCTURE_PLAN.md`、`CAD_AGENT_CHANGELOG.md`、本文 |

### 3. 关键设计说明

- 文档把 `LCAD-10.1` 到 `LCAD-10.4` 的职责串起来：负向 fixture、write guard、负向 runner、声明边界。
- 边界表列出 8 类 `failure_category`，强调这些只证明“正确拒绝”，不证明正向绘图能力。
- 安全扫描表固定 `created_handles=[]`、`CODEX_PREVIEW`、不保存、不删除、不修改正式图层、ActiveDocument 稳定和 entity delta 为 0 的检查口径。
- `RCAD-20` 已从后续真实 CAD 会话补验更新为已通过；即便真实负向 pass，也仍是 guard-only，不计入几何证明。

### 4. 新增/修改测试

| 测试 | 覆盖点 |
| --- | --- |
| `tests/core/test_negative_cad_safety_boundaries_doc.py` | 文档存在，且包含 LCAD-10.1~10.4、`failure_category`、`negative_guard_verified`、`created_handles=[]`、`RCAD-20`、`V-PROOF-50/51` 和不得声称边界 |

### 5. 实际运行的命令和结果

```powershell
$env:PYTHONIOENCODING = "utf-8"
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_negative_cad_safety_boundaries_doc
```

结果：`1 test OK`。

```powershell
& $py -m unittest tests.core.test_negative_cad_safety_boundaries_doc tests.core.test_negative_cad_plans tests.core.test_write_guard_cad_runner tests.core.test_negative_cad_runner
```

结果：`4 tests OK`。

```powershell
& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
```

结果：`status=pass`、`finding_count=0`。

全量回归：当前普通 `unittest discover` 仍会受沙箱 `tempfile` 随机目录 ACL 影响；隔离 `tempfile` 到 `output/test_tmp_runner` 后，`668 tests OK`。

### 6. 是否运行真实 CAD

否。本包是边界文档与文档测试，不连接 AutoCAD，不新增 `geometry_verified`。

### 7. 机器可读证据路径

| 证据 | 路径 |
| --- | --- |
| 负向 fake runner 基线 | `output/validation_runs/neg-cad-proof-sync/negative-runner-fake-final/negative_cad_runner_report.json` |
| 可读覆盖率报告 | `output/validation_runs/neg-cad-proof-sync/capability-readability-final/capability_readability_report.json` |

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 负向 CAD 安全边界文档已存在并包含关键声明 | `doc_contract_test` | **否** |
| `negative_guard_verified` 被明确写为 guard-only | `boundary_doc` | **否** |
| `RCAD-20` 真实 CAD 补验结果与 guard-only 边界已写清楚 | `boundary_doc` | **否** |

### 9. 剩余风险

- `RCAD-20-NEGATIVE-CAD` 已在用户 AutoCAD 会话下执行并通过；本包自身仍不新增几何证明。
- `V-PROOF-50` 的负向 registry 行尚未绑定。
- `LCAD-10.5` 已在后续一键推进包完成；下一步代码轨为 `LCAD-11.1-EVIDENCE-VOCAB`。

### 10. 能力登记表（registry）

| 字段 | 内容 |
| --- | --- |
| `registry_path` | `examples/capability_proof/cad_capability_registry.json` |
| 本包触及行 | 无 registry 行变更；只补文档边界 |

### 11. CAD 证明覆盖率

| 字段 | 内容 |
| --- | --- |
| 回写前 `cad_proof_coverage_rate` | 49.81%（128/257） |
| 回写后 `cad_proof_coverage_rate` | 49.81%（128/257） |
| 覆盖率 JSON 路径 | `output/validation_runs/neg-cad-proof-sync/cad_capability_coverage-final.json` |

### 12. 展示等级 Ladder

| 字段 | 内容 |
| --- | --- |
| 本包最高触及 Ladder | L1/L2 安全与证据治理层 |
| 是否对外提升 Ladder 声称 | 否；文档化 guard 边界，不提升几何能力等级 |

---

## LCAD-10.5：PARENT-ROLLUP（父包 LCAD-10 Negative Safety 收口）

**日期**：2026-05-27

### 1. 本次开发包名

`LCAD-10.5-PARENT-ROLLUP`：父包 `LCAD-10-NEGATIVE-SAFETY` 收口与 handoff。

### 2. 修改文件列表

| 类型 | 文件 |
| --- | --- |
| 新增 | `docs/verification/negative_cad_safety_acceptance.md` |
| 新增 | `tests/core/test_lcad_10_parent_rollup.py` |
| 修改 | `docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` |
| 修改 | `docs/planning/任务清单.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CORE_RESTRUCTURE_PLAN.md`、`CAD_AGENT_CHANGELOG.md` |

### 3. 关键设计说明

- `negative_cad_safety_acceptance.md` 汇总 `LCAD-10.1` 到 `LCAD-10.5`，把父包可声称、不得声称、已补验 `RCAD-20` / 后续 `V-PROOF-50/51` 映射写清楚。
- 父包收口只证明负向安全链路完整，不新增真实 CAD `geometry_verified`。
- 代码轨 next 推进到 `LCAD-11.1-EVIDENCE-VOCAB`，进入 evidence trend rollup。

### 4. 新增/修改测试

| 测试 | 覆盖点 |
| --- | --- |
| `tests/core/test_lcad_10_parent_rollup.py` | 父包 acceptance 文档存在，包含 LCAD-10.1~10.5、三类 runner、guard-only 边界、`RCAD-20`、`V-PROOF-50/51` 和下一包 `LCAD-11.1`；handoff 索引 acceptance 文档 |

### 5. 实际运行的命令和结果

```powershell
$env:PYTHONIOENCODING = "utf-8"
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_lcad_10_parent_rollup
```

结果：RED 阶段 2 failures（acceptance 文档和 handoff 索引缺失）；补文档后 `2 tests OK`。

```powershell
& $py -m unittest tests.core.test_lcad_10_parent_rollup tests.core.test_negative_cad_safety_boundaries_doc tests.core.test_negative_cad_plans tests.core.test_write_guard_cad_runner tests.core.test_negative_cad_runner
```

结果：`6 tests OK`。

```powershell
& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
```

结果：`status=pass`、`finding_count=0`。

全量回归：当前普通 `unittest discover` 仍会受沙箱 `tempfile` 随机目录 ACL 影响；隔离 `tempfile` 到 `output/test_tmp_runner` 后，`670 tests OK`。

### 6. 是否运行真实 CAD

否。本包是父包文档收口与 handoff，不连接 AutoCAD，不新增 `geometry_verified`。

### 7. 机器可读证据路径

| 证据 | 路径 |
| --- | --- |
| 负向 fake runner 基线 | `output/validation_runs/neg-cad-proof-sync/negative-runner-fake-final/negative_cad_runner_report.json` |
| 覆盖率可读报告 | `output/validation_runs/neg-cad-proof-sync/capability-readability-final/capability_readability_report.json` |

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| `LCAD-10-NEGATIVE-SAFETY` 父包已文档收口 | `doc_contract_test` | **否** |
| `negative_guard_verified` 仍被限定为 guard-only | `boundary_doc` | **否** |
| 下一代码轨切到 `LCAD-11.1` | `task_ledger_sync` | **否** |

### 9. 剩余风险

- `RCAD-20-NEGATIVE-CAD` 已在用户 AutoCAD 会话下执行并通过；本父包自身仍不新增几何证明。
- `V-PROOF-50` / `V-PROOF-51` 的 registry 绑定尚未完成。
- `LCAD-11.1` 已在后续一键推进包完成；`LCAD-11.2-REGRESSION-TREND-JSON` 也已完成，下一步代码轨为 `LCAD-11.3-VALIDATION-TREND-INDEX`。

### 10. 能力登记表（registry）

| 字段 | 内容 |
| --- | --- |
| `registry_path` | `examples/capability_proof/cad_capability_registry.json` |
| 本包触及行 | 无 registry 行变更；只做父包收口 |

### 11. CAD 证明覆盖率

| 字段 | 内容 |
| --- | --- |
| 回写前 `cad_proof_coverage_rate` | 49.81%（128/257） |
| 回写后 `cad_proof_coverage_rate` | 49.81%（128/257） |
| 覆盖率 JSON 路径 | `output/validation_runs/neg-cad-proof-sync/cad_capability_coverage-final.json` |

### 12. 展示等级 Ladder

| 字段 | 内容 |
| --- | --- |
| 本包最高触及 Ladder | L1/L2 安全与证据治理层 |
| 是否对外提升 Ladder 声称 | 否；父包收口不提升几何能力等级 |

---

## LCAD-11.1：EVIDENCE-VOCAB（趋势 evidence 词表契约）

**日期**：2026-05-27

### 1. 本次开发包名

`LCAD-11.1-EVIDENCE-VOCAB`：趋势 JSON 字段与统一 evidence 词表对齐。

### 2. 修改文件列表

| 类型 | 文件 |
| --- | --- |
| 新增 | `core/verification/evidence_trend.py` |
| 新增 | `core/schemas/evidence_trend.schema.json` |
| 新增 | `examples/evidence_trends/minimal_evidence_trend.json` |
| 新增 | `tests/fixtures/invalid_models/evidence_trend.invalid.json` |
| 新增 | `tests/core/test_evidence_trend.py` |
| 修改 | `core/schemas/registry.py` |
| 修改 | `tests/core/test_schema_validation.py` |
| 修改 | `docs/planning/任务清单.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CORE_RESTRUCTURE_PLAN.md`、`CAD_AGENT_CHANGELOG.md`、本文 |

### 3. 关键设计说明

- 新增 `evidence_trend` 契约模块，后续 LCAD-11 trend rollup 都以同一组字段输出：`snapshots[]`、`source_kind`、`evidence_state_counts`、`geometry_accuracy_counts`、`screenshot_role_counts`、`summary`、`metrics`。
- `evidence_state_counts` 固定包含全部 `EVIDENCE_STATE_VALUES`，避免趋势 JSON 因某次没有出现某个状态而缺列。
- schema enum 与共享 evidence 词表对齐，新增状态必须同步更新趋势契约。
- `negative_guard_verified` 在趋势汇总中只进入 `guard_only_count`，不进入 `cad_proof_state_count` / `geometry_verified_count`。

### 4. 新增/修改测试

| 测试 | 覆盖点 |
| --- | --- |
| `tests/core/test_evidence_trend.py` | trend snapshot 补齐所有 evidence count 字段；拒绝未知 evidence_state；schema enum 与共享词表一致 |
| `tests/core/test_schema_validation.py` | `evidence_trend.schema.json` 注册、最小样例校验、invalid fixture 覆盖 |

### 5. 实际运行的命令和结果

```powershell
$env:PYTHONIOENCODING = "utf-8"
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_evidence_trend
```

结果：RED 阶段 `ModuleNotFoundError: No module named 'core.verification.evidence_trend'`。

```powershell
& $py -m unittest tests.core.test_evidence_trend tests.core.test_schema_validation
```

结果：补实现与 schema 后 `13 tests OK`。

```powershell
& $py -m unittest tests.core.test_evidence_trend tests.core.test_evidence_classifier tests.core.test_capability_coverage tests.core.test_schema_validation
```

结果：`24 tests OK`。

```powershell
& $py -m unittest tests.core.test_evidence_trend tests.core.test_evidence_classifier tests.core.test_capability_coverage tests.core.test_schema_validation tests.core.test_planmd_governance
```

结果：`31 tests OK`。

```powershell
& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
git diff --check
```

结果：repo audit `status=pass`、`finding_count=0`；`git diff --check` 无空白错误（仅 CRLF warning）。

全量回归：普通 `unittest discover` 在当前沙箱仍会受 Python `tempfile` 随机目录 ACL 影响；隔离 `tempfile` 到 `output/test_tmp_runner_manual` 后，`673 tests OK`。

### 6. 是否运行真实 CAD

否。本包只建立趋势 JSON 契约与 schema，不连接 AutoCAD，不新增 `geometry_verified`。

### 7. 机器可读证据路径

| 证据 | 路径 |
| --- | --- |
| trend schema | `core/schemas/evidence_trend.schema.json` |
| 最小样例 | `examples/evidence_trends/minimal_evidence_trend.json` |
| invalid fixture | `tests/fixtures/invalid_models/evidence_trend.invalid.json` |

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| evidence trend JSON 字段契约已建立 | `schema_contract` | **否** |
| 趋势字段与共享 evidence 词表对齐 | `unit_test_contract` | **否** |
| `negative_guard_verified` 被固定为 guard-only 趋势计数 | `unit_test_contract` | **否** |
| 下一代码轨切到 `LCAD-11.2`（已在后续包完成） | `task_ledger_sync` | **否** |

### 9. 剩余风险

- `LCAD-11.2` 已把 `run_local_cad_regression` 结果输出为 trend JSON；`LCAD-11.3` 也已接入 validation index，后续风险转为 `LCAD-11.4` coverage trend hook。
- `LCAD-11.4` 的 coverage hook 已接入该契约；后续只剩 `LCAD-11.5` 趋势边界文档。
- 本包不提供新的真实 CAD 几何证据，覆盖率仍为 128/257。

### 10. 能力登记表（registry）

| 字段 | 内容 |
| --- | --- |
| `registry_path` | `examples/capability_proof/cad_capability_registry.json` |
| 本包触及行 | 无 registry 行变更；只建立 V-PROOF-71 趋势契约 |

### 11. CAD 证明覆盖率

| 字段 | 内容 |
| --- | --- |
| 回写前 `cad_proof_coverage_rate` | 49.81%（128/257） |
| 回写后 `cad_proof_coverage_rate` | 49.81%（128/257） |
| 覆盖率 JSON 路径 | `output/validation_runs/neg-cad-proof-sync/cad_capability_coverage-final.json` |

### 12. 展示等级 Ladder

| 字段 | 内容 |
| --- | --- |
| 本包最高触及 Ladder | L0/L1 证据治理层 |
| 是否对外提升 Ladder 声称 | 否；只是趋势字段契约，不提升几何能力等级 |

---

## LCAD-11.2：REGRESSION-TREND-JSON（local CAD regression 趋势 JSON）

**日期**：2026-05-27

### 1. 本次开发包名

`LCAD-11.2-REGRESSION-TREND-JSON`：`run_local_cad_regression` 输出可复跑 evidence trend rollup。

### 2. 修改文件列表

| 类型 | 文件 |
| --- | --- |
| 修改 | `core/verification/local_cad_regression_matrix.py` |
| 修改 | `tests/core/test_local_cad_regression.py` |
| 新增 | `tests/core/test_local_cad_regression_trend.py` |
| 修改 | `docs/planning/任务清单.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md`、本文 |

### 3. 关键设计说明

- local regression 主报告写出后，同步生成 `evidence_trend/local_cad_regression_trend.json`。
- trend snapshot 复用 `LCAD-11.1` 的统一字段：完整 `evidence_state_counts`、`geometry_accuracy_counts`、`screenshot_role_counts`、`summary` 与 `metrics`。
- no-CAD 运行中的真实 CAD case 统一计为 `deferred_cad_readback_required`；趋势 JSON 可用于 Dashboard，但不把 deferred 误算为几何证明。

### 4. 新增/修改测试

| 测试 | 覆盖点 |
| --- | --- |
| `tests/core/test_local_cad_regression_trend.py::test_no_cad_mode_writes_evidence_trend_rollup` | no-CAD regression 写出 trend JSON，且 `validate_evidence_trend_report` 无错误 |

### 5. 实际运行的命令和结果

```powershell
$env:PYTHONIOENCODING = "utf-8"
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_local_cad_regression.LocalCadRegressionTests.test_no_cad_mode_writes_evidence_trend_rollup
```

结果：RED 阶段 `trend_path.is_file()` 失败；补实现后 `1 test OK`。

```powershell
& $py -m unittest tests.core.test_local_cad_regression tests.core.test_evidence_trend tests.core.test_schema_validation
```

结果：`24 tests OK`。

```powershell
& $py scripts\run_local_cad_regression.py --no-cad --output-dir output\validation_runs\lcad-11-2-regression-trend-json
```

结果：沙箱内首次运行受 Windows Temp ACL 误伤；按审批沙箱外重跑后 `status=pass`，内部 `unittest discover` 为 `675 tests OK`。

### 6. 是否运行真实 CAD

否。本包只跑 no-CAD local regression，不连接 AutoCAD，不新增 `geometry_verified`。

### 7. 机器可读证据路径

| 证据 | 路径 |
| --- | --- |
| local regression report | `output/validation_runs/lcad-11-2-regression-trend-json/local_cad_regression_report.json` |
| evidence trend report | `output/validation_runs/lcad-11-2-regression-trend-json/evidence_trend/local_cad_regression_trend.json` |

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| local regression 已输出 trend JSON | `machine_readable_trend` | **否** |
| trend schema 校验无错误 | `schema_contract` | **否** |
| no-CAD regression 为 pass，但 8 项均为 deferred/non-CAD 趋势证据 | `deferred_cad_readback_required` | **否** |
| 下一代码轨切到 `LCAD-11.3` | `task_ledger_sync` | **否** |

### 9. 剩余风险

- `LCAD-11.3` 已把 `run_cad_validation` 历次报告索引接入趋势体系。
- `LCAD-11.4` 的 coverage trend hook 已接入；后续剩余 `LCAD-11.5` 趋势边界文档。
- 本包没有真实 CAD created-handle readback，因此不改变 CAD 证明覆盖率。

### 10. 能力登记表（registry）

| 字段 | 内容 |
| --- | --- |
| `registry_path` | `examples/capability_proof/cad_capability_registry.json` |
| 本包触及行 | 无 registry 行变更；只把 local regression 结果滚入 `V-PROOF-71` 趋势证据 |

### 11. CAD 证明覆盖率

| 字段 | 内容 |
| --- | --- |
| 回写前 `cad_proof_coverage_rate` | 48.85%（128/262） |
| 回写后 `cad_proof_coverage_rate` | 48.85%（128/262） |
| 覆盖率 JSON 路径 | `output/validation_runs/vproof-33-readability-rows/cad_capability_coverage.json` |

### 12. 展示等级 Ladder

| 字段 | 内容 |
| --- | --- |
| 本包最高触及 Ladder | L0/L1 证据治理层 |
| 是否对外提升 Ladder 声称 | 否；只是趋势 rollup，不提升几何能力等级 |

---

## LCAD-11.3：VALIDATION-TREND-INDEX（cad validation 历史趋势索引）

**日期**：2026-05-27

### 1. 本次开发包名

`LCAD-11.3-VALIDATION-TREND-INDEX`：`run_cad_validation` 历次报告机器可读索引。

### 2. 修改文件列表

| 类型 | 文件 |
| --- | --- |
| 新增 | `core/verification/cad_validation_trend_index.py` |
| 修改 | `core/verification/cad_validation_runner.py` |
| 新增 | `tests/core/test_cad_validation_trend_index.py` |
| 修改 | `docs/planning/任务清单.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md`、本文 |

### 3. 关键设计说明

- `run_cad_validation` 写出 `report.json/md` 后，会扫描同级 validation run 下的直接子目录 `report.json`。
- 每个有效 `report.json` 转成 `source_kind=cad_validation` 的 evidence trend snapshot，输出到当前 run 的 `evidence_trend/cad_validation_trend_index.json`。
- 索引可吸收历史真实 CAD 几何 snapshots，但本包本身只做 no-CAD 复跑，不新增真实 CAD created-handle readback。

### 4. 新增/修改测试

| 测试 | 覆盖点 |
| --- | --- |
| `tests/core/test_cad_validation_trend_index.py::test_run_cad_validation_writes_historical_trend_index` | 历史 `report.json` + 本次 `report.json` 同时进入 trend index，且 schema 校验无错误 |

### 5. 实际运行的命令和结果

```powershell
$env:PYTHONIOENCODING = "utf-8"
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_cad_validation_trend_index
```

结果：RED 阶段 `ModuleNotFoundError: No module named 'core.verification.cad_validation_trend_index'`；补实现后 `1 test OK`。

```powershell
& $py -m unittest tests.core.test_cad_validation_runner tests.core.test_cad_validation_trend_index tests.core.test_evidence_trend tests.core.test_schema_validation
```

结果：`26 tests OK`。

```powershell
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\lcad-11-3-validation-trend-index
```

结果：沙箱内首次运行受 Windows Temp ACL 误伤；按审批沙箱外重跑后 `status=pass`，内部 `unittest discover` 为 `676 tests OK`。

### 6. 是否运行真实 CAD

否。本包只跑 no-CAD cad validation，不连接 AutoCAD，不新增 `geometry_verified`。

### 7. 机器可读证据路径

| 证据 | 路径 |
| --- | --- |
| cad validation report | `output/validation_runs/lcad-11-3-validation-trend-index/report.json` |
| validation trend index | `output/validation_runs/lcad-11-3-validation-trend-index/evidence_trend/cad_validation_trend_index.json` |

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| cad validation 历史报告索引已输出 | `machine_readable_trend` | **否** |
| trend schema 校验无错误 | `schema_contract` | **否** |
| 本轮 no-CAD validation 为 pass | `deferred_cad_readback_required` | **否** |
| 下一代码轨切到 `LCAD-11.4` | `task_ledger_sync` | **否** |

### 9. 剩余风险

- `LCAD-11.4` 的 coverage trend hook 尚未接入。
- 当前索引会吸收历史真实 CAD snapshots；展示时必须区分“历史索引含几何证据”和“本包新增几何证据”。本包没有真实 CAD created-handle readback。

### 10. 能力登记表（registry）

| 字段 | 内容 |
| --- | --- |
| `registry_path` | `examples/capability_proof/cad_capability_registry.json` |
| 本包触及行 | 无 registry 行变更；只把 cad validation 报告滚入 `V-PROOF-71` 趋势证据 |

### 11. CAD 证明覆盖率

| 字段 | 内容 |
| --- | --- |
| 回写前 `cad_proof_coverage_rate` | 48.85%（128/262） |
| 回写后 `cad_proof_coverage_rate` | 48.85%（128/262） |
| 覆盖率 JSON 路径 | `output/validation_runs/vproof-33-readability-rows/cad_capability_coverage.json` |

### 12. 展示等级 Ladder

| 字段 | 内容 |
| --- | --- |
| 本包最高触及 Ladder | L0/L1 证据治理层 |
| 是否对外提升 Ladder 声称 | 否；只是 validation 趋势索引，不提升几何能力等级 |

---

## LCAD-11.4：COVERAGE-TREND-HOOK（coverage 趋势 hook）

**日期**：2026-05-27

### 1. 本次开发包名

`LCAD-11.4-COVERAGE-TREND-HOOK`：为 `cad_capability_coverage` 输出统一 evidence trend hook。

### 2. 修改文件列表

| 类型 | 文件 |
| --- | --- |
| 修改 | `core/verification/capability_coverage.py` |
| 修改 | `tests/core/test_capability_coverage.py` |
| 修改 | `docs/planning/任务清单.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md`、本文 |

### 3. 关键设计说明

- `run_capability_coverage` 写出常规 coverage JSON 后，同步生成 `evidence_trend/capability_coverage_trend.json`。
- coverage 的 V-PROOF-02 字段放在 `snapshot.metrics`：`total_count`、`verified_count`、`showcase_count`、`cad_proof_count`、`cad_proof_coverage_rate`、`cad_proof_coverage_percent` 等。
- trend summary 的 evidence-state 计数保持 0，避免把本包误解为新增真实 CAD 几何证据。

### 4. 新增/修改测试

| 测试 | 覆盖点 |
| --- | --- |
| `tests/core/test_capability_coverage.py::test_run_capability_coverage_writes_evidence_trend_hook` | coverage 输出时同步写 trend hook，且 `validate_evidence_trend_report` 无错误 |

### 5. 实际运行的命令和结果

```powershell
$env:PYTHONIOENCODING = "utf-8"
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_capability_coverage.CapabilityCoverageTests.test_run_capability_coverage_writes_evidence_trend_hook
```

结果：RED 阶段 `trend_path.is_file()` 失败；补实现后 `1 test OK`。

```powershell
& $py -m unittest tests.core.test_capability_coverage tests.core.test_evidence_trend tests.core.test_schema_validation
```

结果：`18 tests OK`。

```powershell
& $py scripts\run_capability_coverage.py --output output\validation_runs\lcad-11-4-coverage-trend-hook\cad_capability_coverage.json
```

结果：`status=pass`，`total_count=262`、`verified_count=128`、`cad_proof_coverage_percent=48.85`。

### 6. 是否运行真实 CAD

否。本包只生成 coverage trend hook，不连接 AutoCAD，不新增 `geometry_verified`。

### 7. 机器可读证据路径

| 证据 | 路径 |
| --- | --- |
| coverage report | `output/validation_runs/lcad-11-4-coverage-trend-hook/cad_capability_coverage.json` |
| coverage trend hook | `output/validation_runs/lcad-11-4-coverage-trend-hook/evidence_trend/capability_coverage_trend.json` |

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| coverage trend hook 已输出 | `machine_readable_trend` | **否** |
| trend schema 校验无错误 | `schema_contract` | **否** |
| CAD 证明覆盖率仍为 48.85% | `coverage_metric` | **否** |
| 下一代码轨切到 `LCAD-11.5` | `task_ledger_sync` | **否** |

### 9. 剩余风险

- `LCAD-11.5` 尚未把趋势报告的「不能声称」边界写成审计文档。
- coverage trend hook 只承载 registry 覆盖率指标；不能替代 created-handle readback 或新的真实 CAD 几何证明。

### 10. 能力登记表（registry）

| 字段 | 内容 |
| --- | --- |
| `registry_path` | `examples/capability_proof/cad_capability_registry.json` |
| 本包触及行 | 无 registry 行变更；只把 coverage 指标滚入 `V-PROOF-71` 趋势证据 |

### 11. CAD 证明覆盖率

| 字段 | 内容 |
| --- | --- |
| 回写前 `cad_proof_coverage_rate` | 48.85%（128/262） |
| 回写后 `cad_proof_coverage_rate` | 48.85%（128/262） |
| 覆盖率 JSON 路径 | `output/validation_runs/lcad-11-4-coverage-trend-hook/cad_capability_coverage.json` |

### 12. 展示等级 Ladder

| 字段 | 内容 |
| --- | --- |
| 本包最高触及 Ladder | L0/L1 证据治理层 |
| 是否对外提升 Ladder 声称 | 否；只是 coverage 趋势 hook，不提升几何能力等级 |

---

## LCAD-11.5：TREND-BOUNDARY-DOC（趋势报告声明边界）

**日期**：2026-05-27

### 1. 本次开发包名

`LCAD-11.5-TREND-BOUNDARY-DOC`：趋势报告「不能声称」说明。

### 2. 修改文件列表

| 类型 | 文件 |
| --- | --- |
| 新增 | `docs/verification/evidence_trend_boundaries.md` |
| 新增 | `tests/core/test_evidence_trend_boundaries_doc.py` |
| 修改 | `docs/planning/任务清单.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md`、本文 |

### 3. 关键设计说明

- 将 `LCAD-11.1`~`11.4` 的 trend JSON 统一解释为机器可读索引与 Dashboard 输入，而不是新的绘图证明。
- 固定三类趋势报告边界：`local_cad_regression_trend.json`、`cad_validation_trend_index.json`、`capability_coverage_trend.json`。
- 明确 coverage 字段位于 `snapshot.metrics`，`cad_proof_coverage_rate` 不是几何准确率，不能替代 registry 行回写或真实 CAD readback。

### 4. 新增/修改测试

| 测试 | 覆盖点 |
| --- | --- |
| `tests/core/test_evidence_trend_boundaries_doc.py` | 文档存在；覆盖 LCAD-11.1~11.4、三类 trend 文件、`snapshot.metrics`、`cad_proof_coverage_rate`、created-handle readback 与不得声称边界 |

### 5. 实际运行的命令和结果

```powershell
$env:PYTHONIOENCODING = "utf-8"
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_evidence_trend_boundaries_doc
```

结果：RED 阶段文档不存在；补文档后 `1 test OK`。

```powershell
& $py -m unittest tests.core.test_evidence_trend_boundaries_doc tests.core.test_evidence_trend tests.core.test_capability_coverage tests.core.test_cad_validation_trend_index tests.core.test_local_cad_regression_trend
```

结果：`11 tests OK`。

### 6. 是否运行真实 CAD

否。本包只补趋势声明边界文档，不连接 AutoCAD，不新增 `geometry_verified`。

### 7. 机器可读证据路径

| 证据 | 路径 |
| --- | --- |
| local regression trend | `output/validation_runs/lcad-11-2-regression-trend-json/evidence_trend/local_cad_regression_trend.json` |
| validation trend index | `output/validation_runs/lcad-11-3-validation-trend-index/evidence_trend/cad_validation_trend_index.json` |
| coverage trend hook | `output/validation_runs/lcad-11-4-coverage-trend-hook/evidence_trend/capability_coverage_trend.json` |

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| LCAD-11 trend 边界已文档化 | `boundary_doc` | **否** |
| trend JSON 不能替代 created-handle readback | `claim_boundary` | **否** |
| coverage metric 不能替代几何准确率 | `claim_boundary` | **否** |
| 下一代码轨切到 `CAD-VAL-02` | `task_ledger_sync` | **否** |

### 9. 剩余风险

- `CAD-VAL-02` 尚未把 Pillow / 截图 / unit_tests 与几何门禁进一步拆分为可选或独立门禁。
- LCAD-11 trend 系列已经具备 schema、regression、validation、coverage 与边界文档，但还不是最终 Dashboard UI。

### 10. 能力登记表（registry）

| 字段 | 内容 |
| --- | --- |
| `registry_path` | `examples/capability_proof/cad_capability_registry.json` |
| 本包触及行 | 无 registry 行变更；只固定 `V-PROOF-71` trend 声明边界 |

### 11. CAD 证明覆盖率

| 字段 | 内容 |
| --- | --- |
| 回写前 `cad_proof_coverage_rate` | 48.85%（128/262） |
| 回写后 `cad_proof_coverage_rate` | 48.85%（128/262） |
| 覆盖率 JSON 路径 | `output/validation_runs/lcad-11-4-coverage-trend-hook/cad_capability_coverage.json` |

### 12. 展示等级 Ladder

| 字段 | 内容 |
| --- | --- |
| 本包最高触及 Ladder | L0/L1 证据治理层 |
| 是否对外提升 Ladder 声称 | 否；只是 trend 边界文档，不提升几何能力等级 |

---

## CAD-VAL-02：ENVIRONMENT-GATE-OPTIONAL（环境门禁可选化）

**日期**：2026-05-27

### 1. 本次开发包名

`CAD-VAL-02-ENVIRONMENT-GATE-OPTIONAL`：Pillow / 截图 / unit_tests 改为可选或独立门禁。

### 2. 修改文件列表

| 类型 | 文件 |
| --- | --- |
| 修改 | `core/verification/cad_validation_runner.py` |
| 修改 | `tests/core/test_cad_validation_geometry_gate.py` |
| 新增 | `docs/verification/cad_validation_environment_gate.md` |
| 新增 | `tests/core/test_cad_validation_environment_gate_doc.py` |
| 修改 | `docs/planning/任务清单.md`、`CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md`、本文 |

### 3. 关键设计说明

- `run_cad_validation` 新增 `environment_optional` 参数，CLI 新增 `--environment-optional`。
- 开启后，顶层 `status` 按 `geometry_gate` 计算；非几何失败仍保留在 `infrastructure_gate.failed_required_step_ids`。
- 当 `geometry_gate=pass` 且 `infrastructure_gate!=pass` 时，报告保留 `infrastructure_debt=true` 和中文 next action。

### 4. 新增/修改测试

| 测试 | 覆盖点 |
| --- | --- |
| `tests/core/test_cad_validation_geometry_gate.py::test_environment_optional_mode_reports_infrastructure_debt_without_failing_geometry` | `unit_tests` 失败时，`status=pass`、`legacy_status=fail`、`infrastructure_debt=true` |
| `tests/core/test_cad_validation_environment_gate_doc.py` | 环境门禁文档存在并覆盖 `--environment-optional`、`geometry_gate`、`infrastructure_gate`、非几何失败与不得声称 |

### 5. 实际运行的命令和结果

```powershell
$env:PYTHONIOENCODING = "utf-8"
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_cad_validation_geometry_gate.CadValidationGeometryGateTests.test_environment_optional_mode_reports_infrastructure_debt_without_failing_geometry
```

结果：RED 阶段 `run_cad_validation()` 不支持 `environment_optional`；补实现后 `1 test OK`。

```powershell
& $py -m unittest tests.core.test_cad_validation_geometry_gate tests.core.test_cad_validation_environment_gate_doc tests.core.test_cad_validation_runner
```

结果：`16 tests OK`。

```powershell
& $py scripts\run_cad_validation.py --no-cad --environment-optional --output-dir output\validation_runs\cad-val-02-environment-optional
```

结果：exit 0；`status=pass`、`legacy_status=fail`、`geometry_gate.status=pass`、`infrastructure_gate.status=fail`、`infrastructure_debt=true`。当前失败项为沙箱内 `unit_tests` 的 Windows Temp ACL 误伤。

### 6. 是否运行真实 CAD

否。本包只跑 no-CAD validation，不连接 AutoCAD，不新增 `geometry_verified`。

### 7. 机器可读证据路径

| 证据 | 路径 |
| --- | --- |
| environment optional report | `output/validation_runs/cad-val-02-environment-optional/report.json` |
| environment gate doc | `docs/verification/cad_validation_environment_gate.md` |

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 环境失败可独立保留，不拖死几何 gate | `gate_contract` | **否** |
| 非几何失败边界已文档化 | `boundary_doc` | **否** |
| `unit_tests` Temp ACL 失败保留为 `infrastructure_debt` | `environment_debt` | **否** |
| 下一代码轨切到 `LCAD-12` | `task_ledger_sync` | **否** |

### 9. 剩余风险

- `LCAD-12` 尚未处理 hatch COM 最小实现或 structured deferred。
- `--environment-optional` 不是默认吞错；完整 baseline 仍应修复 `infrastructure_gate` 失败。

### 10. 能力登记表（registry）

| 字段 | 内容 |
| --- | --- |
| `registry_path` | `examples/capability_proof/cad_capability_registry.json` |
| 本包触及行 | 无 registry 行变更；只调整 validation runner 的门禁口径 |

### 11. CAD 证明覆盖率

| 字段 | 内容 |
| --- | --- |
| 回写前 `cad_proof_coverage_rate` | 48.85%（128/262） |
| 回写后 `cad_proof_coverage_rate` | 48.85%（128/262） |
| 覆盖率 JSON 路径 | `output/validation_runs/lcad-11-4-coverage-trend-hook/cad_capability_coverage.json` |

### 12. 展示等级 Ladder

| 字段 | 内容 |
| --- | --- |
| 本包最高触及 Ladder | L0/L1 门禁治理层 |
| 是否对外提升 Ladder 声称 | 否；只是环境门禁口径，不提升几何能力等级 |

---

## 0. 会话探针：CAD-MCP + 截图自检（无代码变更）

**日期**：2026-05-26（Cursor 会话首轮）
**性质**：环境核查，**未改仓库代码**。

### 1. 开发包名

无（非 PlanMD 开发包）；会话目标为确认 Cursor 是否具备 CAD-MCP 与截图自检能力。

### 2. 修改文件列表

无。

### 3. 关键设计说明

- 核查 `C:\Users\123235\.cursor\mcp.json`：`cad-mcp` 已注册，入口为 `.cursor\mcp\CAD-MCP\.venv` + `server.py`。
- 当前会话 MCP 工具目录 `mcps/user-cad-mcp` 约 11 个绘图工具可用。
- 仓库内 `scripts/self_check.py`、`scripts/render_preview.py --check` 在本机通过；检测到 AutoCAD 2026 窗口。

### 4. 新增/修改测试

无。

### 5. 实际运行的命令和结果

```powershell
$py = "C:\Users\123235\.cursor\mcp\CAD-MCP\.venv\Scripts\python.exe"
cd "D:\工作文件\CAD-AGENT"
& $py scripts\self_check.py          # status: pass
& $py scripts\render_preview.py --check   # status: ready, autocad_window ready
```

### 6. 是否运行真实 CAD

未运行 `run_cad_validation.py` 或落图；仅环境探针与 `--check`。

### 7. CAD 证据路径

无（无 `output/validation_runs` 本轮目录）。

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| MCP 已配置、截图依赖就绪 | 环境 non-CAD 探针 |
| 几何准确 | **未声称** |

### 9. 剩余风险

- Cursor MCP 路径与文档中的 `\.codex\mcp\CAD-MCP` 可能并存，执行脚本时需以本机 `mcp.json` 为准。

---

## 1. R-CAD-VIEW-CAPTURE

**日期**：2026-05-26
**PlanMD 顺序**：开发包 #5（先于 CONTRACT 实现，同日完成）

### 1. 开发包名

`R-CAD-VIEW-CAPTURE` — AutoCAD 窗口级 / 视口级视觉辅助截图，避免 Codex 全屏遮挡。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/render_preview.py` | `--check` 结构化能力；`--capture-autocad-window`；`--execution-summary` 聚焦 |
| `scripts/render_preview.py` | 兼容包装 |
| `core/cad_io/autocad_com.py` | `zoom_to_bbox` / `zoom_to_handles` |
| `core/verification/cad_validation_runner.py` | 总控改用窗口截图 `cad-validation-window.png` |
| `tests/core/test_render_preview.py` | 窗口截图与能力字段 |
| `tests/core/test_cad_validation_runner.py` | 总控命令断言 |
| `CORE_*` / `CAD_AGENT_*` / `docs/planning/phase-r-rebirth-implementation-plan.md` 等 | 状态与执行记录 |

### 3. 关键设计说明

- 截图范围：AutoCAD **客户区**，非全屏；可选按本轮 `created_handles` bbox 缩放视图后再截。
- 总控步骤 `capture_screen` 使用 `--capture-autocad-window --execution-summary ...`。
- **硬规则**：`screenshot_role=visual_aid_only`；截图不参与 `geometry_verified` 判定。
- 无 CAD 时 `--check` 不得误报 `autocad_window` ready。

### 4. 新增/修改测试

- `tests.core.test_render_preview`
- `tests.core.test_cad_validation_runner`
- 聚焦运行：**11 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_render_preview tests.core.test_cad_validation_runner
& $py scripts\render_preview.py --check
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\r-cad-view-no-cad
# status=pass（含 unittest discover）
& $py scripts\run_cad_validation.py --output-dir output\validation_runs\r-cad-view-cad
# status=pass
```

### 6. 是否运行真实 CAD

**是**（`r-cad-view-cad`）。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| 总控 | `output/validation_runs/r-cad-view-cad/report.json` → `status=pass` |
| 回读 | `output/validation_runs/r-cad-view-cad/readback_report.json` → `status=geometry_verified` |
| 能力探针 | `output/validation_runs/r-cad-view-cad/cad_capability_probe.json` → `status=cad_capability_verified` |
| 截图 | `output/validation_runs/r-cad-view-cad/cad-validation-window.png` |
| 执行摘要 | `output/validation_runs/r-cad-view-cad/execution_summary.json` |

**baseline `draw_test_cabinet` created handles（本轮落图）**：

`631`, `632`, `633`, `634`, `635`, `636`, `67B`

**截图元数据（stdout 摘录）**：`mode=autocad_window`，`focus.status=zoomed_to_bbox`，`handle_count=7`

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| 窗口级截图可用、总控 pass | non-CAD + 真实 CAD 流程 |
| baseline 柜体 readback | **`geometry_verified`**（created handles 定向回读） |
| 能力探针 | **`cad_capability_verified`**（primitive probe，≠ 任意 CAD_PLAN） |
| 截图本身 | **visual_aid_only**，非几何证据 |

### 9. 剩余风险

- 未覆盖多显示器、更细绘图区裁剪、遮挡边界。
- 不能把截图 pass 扩大为块库或任意 plan 几何通过。

---

## 2. R-CAD-CONTRACT

**日期**：2026-05-26
**PlanMD 顺序**：开发包 #1

### 1. 开发包名

`R-CAD-CONTRACT` — 基础图元探针与 readback 报告固化为机器可读 CAD 能力契约。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/evidence_contract.py` | **新增**：证据词表、`ENTITY_CONTRACTS`、probe/readback 注解与门禁校验 |
| `core/verification/cad_capability_probe.py` | 输出 `evidence_state` / `geometry_accuracy` / `screenshot_role` / `contract` |
| `core/verification/verification_report.py` | readback 报告证据字段 |
| `core/verification/cad_validation_runner.py` | 证据字段硬门禁；步骤透传 |
| `core/schemas/verification_report.schema.json` | 可选证据字段 |
| `examples/verification_reports/minimal_cabinet_verification.json` | 示例补字段 |
| `docs/planning/phase-r-cad-capability-contract.md` | 契约文档 + 机器可读字段表 |
| `tests/core/test_cad_capability_probe.py` | 证据字段断言 |
| `tests/core/test_cad_validation_runner.py` | 缺证据字段门禁 |
| `CORE_*` / `CAD_AGENT_*` | 状态同步 |

### 3. 关键设计说明

- 分离两类几何结论：
  - `cad_capability_verified` + `verified_by_cad_capability_readback`（primitive 探针）
  - `readback_geometry_verified` + `verified_by_cad_readback`（plan 级 created handles 回读）
- `cad_validation_runner` 顶层 pass 仍依赖 `readback_report.status=geometry_verified` 与 `cad_capability_probe.status=cad_capability_verified`。
- `block_reference` / `insert_block_alpha` 在契约中标记为 **deferred**。

### 4. 新增/修改测试

- `tests.core.test_cad_capability_probe`
- `tests.core.test_cad_validation_runner`
- `tests.core.test_geometry_checks`
- `tests.core.test_verification_report`
- 相关集：**28 tests OK**（该包子集）；全量随后 **228 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_cad_capability_probe tests.core.test_cad_validation_runner tests.core.test_geometry_checks tests.core.test_verification_report
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\r-cad-contract-no-cad
# status=pass
& $py scripts\run_cad_validation.py --output-dir output\validation_runs\r-cad-contract-cad
# status=pass
```

### 6. 是否运行真实 CAD

**是**（`r-cad-contract-cad`）。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| 总控 | `output/validation_runs/r-cad-contract-cad/report.json` → `status=pass` |
| 回读 | `output/validation_runs/r-cad-contract-cad/readback_report.json` → `status=geometry_verified`，`evidence_state=readback_geometry_verified` |
| 能力探针 | `output/validation_runs/r-cad-contract-cad/cad_capability_probe.json` → `cad_capability_verified`，`evidence_state=cad_capability_verified` |
| 截图 | `output/validation_runs/r-cad-contract-cad/cad-validation-window.png` |

**baseline created handles**：`751`–`756`, `79B`

**capability probe created handles（独立探针落图）**：`7E0`–`7E9`, `82D`（共 11）

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| 证据字段、runner 门禁、schema | **non-CAD**（+ 真实 CAD 总控流程 pass） |
| baseline plan readback | **`geometry_verified`** |
| capability probe | **`cad_capability_verified`**（有限 primitive 样本） |
| block insertion | **未验证**（契约中 deferred） |

### 9. 剩余风险

- 不能把 `cad_capability_verified` 说成任意 CAD_PLAN 或真实块库已通过。
- `r-cad-view-cad` 的 readback 若在 CONTRACT 之前生成，可能无 `evidence_state` 字段（后续 run 会有）。

---

## 3. R-BLOCK-METADATA

**日期**：2026-05-26
**PlanMD 顺序**：开发包 #2

### 1. 开发包名

`R-BLOCK-METADATA` — `BLOCK_LIBRARY v0.2`、受控测试块 metadata、`object_spec_to_block_reference`。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/schemas/block_library.schema.json` | 支持 `0.1` / `0.2` |
| `libraries/blocks/block_library.example.json` | 升为 `0.2`；`controlled-test-block-001` + symbol_fallback 块 |
| `libraries/blocks/controlled/CODEX_TEST_BLOCK_001.metadata.json` | **新增**侧车 metadata |
| `core/block_engine/block_library.py` | `normalize_block`、`validate_block_library`、`object_spec_to_block_reference` |
| `core/block_engine/block_selector.py` | `validation.status` 过滤 |
| `core/block_engine/block_placement.py` | `cad_identity`、`layer_role` |
| `tests/core/test_block_engine.py` | v0.2 / 受控块 / fallback |
| `tests/fixtures/invalid_models/block_library*.invalid.json` | 反例 |
| `docs/planning/phase-r-block-library-roadmap.md` | 状态更新 |
| `CORE_*` / `CAD_AGENT_*` | 状态同步 |

### 3. 关键设计说明

- `controlled-test-block-001` → `CODEX_TEST_BLOCK_001`，`validation.status=metadata_only`。
- 其余示例块为 `symbol_fallback`，不接真实公司块库。
- `0.1` 库（`examples/block_libraries/minimal_builtin_blocks.json`）仍可加载，`normalize_block` 补全 v0.2 派生字段。
- selector 排除 `deferred_cad_readback` 等不可选状态。

### 4. 新增/修改测试

- `tests.core.test_block_engine`
- `tests.core.test_schema_validation`（block_library 反例）
- 全量：**234 tests OK**；`run_repo_audit.py --fail-on-findings` → **0 findings**；blank-shell benchmark **pass**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_block_engine tests.core.test_schema_validation
& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\r-block-metadata-check
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\r-block-metadata-no-cad
# status=pass
```

### 6. 是否运行真实 CAD

**否**（仅 no-CAD 总控）。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| 总控 | `output/validation_runs/r-block-metadata-no-cad/report.json` → `status=pass` |

无 `readback_report.json`、无截图、无 `created_handles`（符合预期）。

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| schema、loader、selector、benchmark、repo audit | **non-CAD** |
| 真实块插入 / block readback | **未验证** |
| `geometry_verified` | **未达到** |

### 9. 剩余风险

- metadata 就绪 ≠ AutoCAD 中已有 `CODEX_TEST_BLOCK_001` 块定义。
- 下一包 `R-BLOCK-CAD-ALPHA` 才做真实插入与 readback。

---

## 4. R-BLOCK-PLAN

**日期**：2026-05-26
**PlanMD 顺序**：开发包 #3

### 1. 开发包名

`R-BLOCK-PLAN` — 受控 `insert_block_alpha` CAD_PLAN intent（validate / dry-run / fake execute）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/plan_engine/block_alpha_plan.py` | **新增** validate + dry-run |
| `examples/plans/insert_block_alpha_test.json` | **新增**合法示例 |
| `tests/fixtures/invalid_plans/insert_block_alpha_formal_layer.invalid.json` | 反例 |
| `core/plan_engine/validate_plan.py` | 支持 `insert_block_alpha` |
| `core/plan_engine/dry_run_report.py` | 分支 dry-run |
| `core/plan_engine/dry_run_plan.py` | 改用 `create_dry_run_report` |
| `core/execution/execute_plan.py` | fake `insert_block_alpha` 执行路径 |
| `core/schemas/cad_plan.schema.json` | intent 扩展 |
| `schemas/cad_plan.schema.json` | 同步 |
| `tests/core/test_plan_engine.py` | validate / dry-run / 反例 |
| `tests/core/test_execute_plan.py` | fake driver 记录 |
| `CORE_*` / `CAD_AGENT_*` | 状态同步 |

### 3. 关键设计说明

- 最小合法 plan：`block_id`、`cad_identity.block_name`、`base_point`、`rotation`、`scale`、`layer=CODEX_PREVIEW`。
- validate 拒绝：正式图层、`空 block_name`、非法 `scale`、缺 `base_point`。
- dry-run 输出 bbox / anchor / rotation / layer role，`evidence_state=dry_run_valid_plan_only`。
- `execute_plan` 仅调用 fake driver `insert_block_alpha()`，**不连 AutoCAD**。
- 与 `draw_object` 分 intent 维护，避免混用 width/depth 规则。

### 4. 新增/修改测试

- `tests.core.test_plan_engine`（含 insert_block_alpha 用例）
- `tests.core.test_execute_plan`
- `tests.core.test_validation_edges`
- 全量：**239 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\validate_plan.py examples\plans\insert_block_alpha_test.json
# VALID CAD_PLAN
& $py scripts\dry_run_plan.py examples\plans\insert_block_alpha_test.json
# status valid, geometry_accuracy=not_verified_without_cad_readback
& $py -m unittest tests.core.test_plan_engine tests.core.test_execute_plan tests.core.test_validation_edges
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\r-block-plan-no-cad
# status=pass
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| 总控 | `output/validation_runs/r-block-plan-no-cad/report.json` → `status=pass` |

无 `readback_report.json`、无截图。fake execute 测试桩 handle：`BLOCK-H1`（仅单测，非 CAD 文件）。

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| validate / dry-run / fake execute / 总控 no-CAD | **non-CAD** |
| `dry_run_valid_plan_only` | **non-CAD**（明确未几何验证） |
| `geometry_verified` | **未达到** |
| 真实块插入 | **deferred** → `R-BLOCK-CAD-ALPHA` |

### 9. 剩余风险

- `AutoCADComDriver` 尚未实现真实 `insert_block_alpha`。
- 不能把 dry-run / fake execute pass 说成块已在 DWG 中插准。

---

## 5. R-BLOCK-CAD-01

**日期**：2026-05-26
**父包**：`R-BLOCK-CAD-ALPHA`
**PlanMD 顺序**：二级小包 #1

### 1. 开发包名

`R-BLOCK-CAD-01` — 受控块定义查找 / 最小创建策略（`CODEX_TEST_BLOCK_001`）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/cad_io/autocad_com.py` | `ensure_controlled_block_definition()`、`block_definition_exists()`、结构化 `definition_missing` |
| `tests/core/test_autocad_com_driver.py` | 5 项受控块定义单测 |
| `docs/planning/phase-r-cad-capability-contract.md` | 受控块定义解析说明 |
| `docs/planning/phase-r-rebirth-implementation-plan.md` | 标记小包完成 |
| `CAD_AGENT_CHANGELOG.md` / `CAD_AGENT_STATUS.md` / `CORE_CONTEXT_BRIEF.md` | 状态同步 |

### 3. 关键设计说明

- 优先 `doc.Blocks.Item("CODEX_TEST_BLOCK_001")` 复用已有块表记录。
- 缺失时在块定义空间用 layer `0` 画 100×50 矩形（4 条 `AddLine`），**不保存 DWG、不写正式项目图层**。
- 成功返回 `status=ready` + `source=existing|created`；失败返回 `status=definition_missing` + `failure_category=definition_missing`。
- 本包不实现 `insert_block_alpha` COM 插入，也不声称 `geometry_verified`。

### 4. 新增/修改测试

- `tests.core.test_autocad_com_driver.ControlledBlockDefinitionTests`（5 项）
- 全量：**244 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_autocad_com_driver -v
# Ran 9 tests OK
& $py -m unittest discover -s tests -q
# Ran 244 tests OK
```

### 6. 是否运行真实 CAD

**否**（仅 mock `doc.Blocks` 单测）。

### 7. CAD 证据路径

无 `output/validation_runs` 证据。本包只验证 driver 策略与失败分类，不连 AutoCAD。

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| 块定义解析策略 / driver 单测 | **non-CAD** |
| `geometry_verified` | **未达到** |
| 真实块引用插入 | **deferred** → `R-BLOCK-CAD-02` |

### 9. 剩余风险

- DWG 中是否已有 `CODEX_TEST_BLOCK_001` 仍须在真实 CAD 会话下由 `R-BLOCK-CAD-02` 起验证。
- 不能把“可创建块定义”说成“块引用已插准”。

---

## 6. R-BLOCK-CAD-02

**日期**：2026-05-26
**父包**：`R-BLOCK-CAD-ALPHA`
**PlanMD 顺序**：二级小包 #2

### 1. 开发包名

`R-BLOCK-CAD-02` — `AutoCADComDriver.insert_block_alpha()` 最小 COM 写入（`CODEX_PREVIEW`、统一 scale）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/cad_io/autocad_com.py` | `insert_block_alpha()`、`BlockAlphaInsertionError`、`block_insert_failure()` |
| `tests/core/test_autocad_com_driver.py` | 5 项 insert 单测 |
| `tests/core/test_execute_plan.py` | COM driver 与 `execute_plan` 契约单测 |
| `docs/planning/phase-r-cad-capability-contract.md` | 补充写入路径说明 |
| `docs/planning/phase-r-rebirth-implementation-plan.md` | 标记小包完成 |
| `CAD_AGENT_CHANGELOG.md` / `CAD_AGENT_STATUS.md` / `CORE_CONTEXT_BRIEF.md` | 状态同步 |

### 3. 关键设计说明

- 执行顺序：`ensure_controlled_block_definition()` → `ModelSpace.InsertBlock` → `_apply_common(layer=CODEX_PREVIEW)`。
- 仅接受 `layer=CODEX_PREVIEW` 与统一 `scale`；非 preview layer 在 driver 层 `ValueError`，validate/execute 上游也会拒绝。
- 块属性（`attributes`）显式 deferred，抛出 `attribute_unverified`。
- 返回 `handle` + `geometry_accuracy=not_verified_without_cad_readback`；不得据此声称几何通过。

### 4. 新增/修改测试

- `ControlledBlockDefinitionTests` 内 5 项 `insert_block_alpha` 用例
- `test_insert_block_alpha_autocad_driver_matches_execute_plan_contract`
- 全量：**250 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_autocad_com_driver tests.core.test_execute_plan -q
& $py -m unittest discover -s tests -q
# Ran 250 tests OK
```

### 6. 是否运行真实 CAD

**否**（mock `InsertBlock` / `execute_plan` 桩）。

### 7. CAD 证据路径

无 `output/validation_runs` 证据。

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| COM 写入接口 / driver+execute 单测 | **non-CAD** |
| `geometry_verified` | **未达到** |
| `block_reference` readback | **deferred** → `R-BLOCK-CAD-03` |

### 9. 剩余风险

- 真实 AutoCAD `InsertBlock` 行为（旋转弧度、块基点）须在用户会话下由 `R-BLOCK-CAD-05` 验证。
- 不能把“接口可调用”说成“块引用几何已 verified”。

---

## 7. R-BLOCK-CAD-03

**日期**：2026-05-26
**父包**：`R-BLOCK-CAD-ALPHA`
**PlanMD 顺序**：二级小包 #3

### 1. 开发包名

`R-BLOCK-CAD-03` — `block_reference` readback 标准化（normalize + 几何对照检查）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/inspect_dwg.py` | `AcDbBlockReference` normalize + `GetBoundingBox` |
| `core/verification/geometry_checks.py` | `check_block_reference_readback()`、失败分类 |
| `core/verification/evidence_contract.py` | `readback_normalize_baseline` |
| `tests/core/test_geometry_checks.py` | 5 项 block readback 用例 |
| `tests/core/test_verification_report.py` | block normalize 用例 |
| `docs/planning/phase-r-cad-capability-contract.md` | 状态说明 |
| `CAD_AGENT_*` / `CORE_CONTEXT_BRIEF.md` | 状态同步 |

### 3. 关键设计说明

- COM 实体标准化输出契约字段：`handle`、`type`、`block_name`、`insertion_point`、`rotation`（度）、`scale`、`layer`、`bbox`。
- `check_block_reference_readback()` 对照 `insert_block_alpha` plan 期望值，容差：插入点 1mm、旋转 0.5°、bbox 2mm。
- 缺字段 → `readback_missing`；块名/插入点/旋转不符 → 对应 failure_category。
- 本包不接入 CAD validation runner，不运行真实 CAD。

### 4. 新增/修改测试

- `tests.core.test_geometry_checks`（block readback 5 项）
- `tests.core.test_verification_report`（normalize block）
- 全量：**255 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_geometry_checks tests.core.test_verification_report tests.core.test_autocad_com_driver -q
& $py -m unittest discover -s tests -q
# Ran 255 tests OK
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

无 `output/validation_runs` 证据。

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| readback normalize / 几何对照单测 | **non-CAD** |
| `geometry_verified` | **未达到** |
| validation runner block alpha step | **deferred** → `R-BLOCK-CAD-04` |

### 9. 剩余风险

- 真实 AutoCAD `EffectiveName` / `GetBoundingBox` / 旋转弧度语义须在 `R-BLOCK-CAD-05` 用户会话下复验。
- 不能把 normalize 单测 pass 说成块 alpha 已在 DWG 中几何 verified。

---

## 8. R-BLOCK-CAD-04

**日期**：2026-05-26
**父包**：`R-BLOCK-CAD-ALPHA`
**PlanMD 顺序**：二级小包 #4

### 1. 开发包名

`R-BLOCK-CAD-04` — CAD validation runner 接入 block alpha（no-CAD deferred + CAD 步骤骨架）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/cad_validation_runner.py` | block alpha steps + gate + `report.block_alpha` |
| `core/verification/block_alpha_validation.py` | **新增** 报告构建与证据校验 |
| `scripts/run_block_alpha_validation.py` | **新增** CLI |
| `tests/core/test_block_alpha_validation.py` | **新增** |
| `tests/core/test_cad_validation_runner.py` | no-CAD deferred + CAD 步骤用例 |
| `CAD_AGENT_*` / `CORE_CONTEXT_BRIEF.md` | 状态同步 |

### 3. 关键设计说明

- **no-CAD**：`block_alpha_deferred_evidence` 写 `block_alpha_report.json`，`evidence_state=deferred_cad_readback_required`；硬门禁禁止 `geometry_verified`。
- **CAD**：`block_alpha_execute` + `block_alpha_readback`；readback 须 `geometry_verified` 才 pass（`R-BLOCK-CAD-05` 真实验收）。
- 顶层 `report.json` 增加 `block_alpha.geometry_verified`，避免把总控 pass 误解为块几何已 verified。

### 4. 新增/修改测试

- `tests.core.test_block_alpha_validation`（3 项）
- `tests.core.test_cad_validation_runner`（含 no-CAD deferred）
- 全量：**259 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_block_alpha_validation tests.core.test_cad_validation_runner -q
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\r-block-alpha-no-cad-test
# report.status=pass; block_alpha.geometry_verified=false
```

### 6. 是否运行真实 CAD

**否**（no-CAD 总控实跑；未执行 `block_alpha_execute` COM 插入）。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| 总控 | `output/validation_runs/r-block-alpha-no-cad-test/report.json` |
| block alpha | `output/validation_runs/r-block-alpha-no-cad-test/block_alpha_report.json` → `status=deferred` |

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| validate / dry-run / no-CAD deferred / 总控 pass | **non-CAD** |
| `block_alpha.geometry_verified` | **false**（符合预期） |
| 真实块引用几何 verified | **deferred** → `R-BLOCK-CAD-05` |

### 9. 剩余风险

- 真实 AutoCAD 下 `block_alpha_readback` 是否达到 `geometry_verified` 须在用户会话执行 `R-BLOCK-CAD-05`。
- 不能把 no-CAD 总控 pass 说成块已在 DWG 中插准。

---

## 9. R-BLOCK-CAD-05

**日期**：2026-05-26
**父包**：`R-BLOCK-CAD-ALPHA`（**二级小包全部完成**）

### 1. 开发包名

`R-BLOCK-CAD-05` — 真实 AutoCAD 受控块 alpha：插入 + created handles 定向 readback + 窗口截图。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/cad_io/autocad_com.py` | 受控块定义 footprint 与 metadata 对齐（900×450） |
| `core/verification/cad_validation_runner.py` | `--block-alpha-only`、`block_alpha_capture_screen` |
| `core/verification/block_alpha_validation.py` | readback 报告挂截图路径 |
| `scripts/run_block_alpha_validation.py` | 截图证据 |
| `docs/verification/block_alpha_cad_evidence.md` | **新增** 证据索引 |
| `CAD_AGENT_*` / `CORE_CONTEXT_BRIEF.md` | 状态同步 |

### 3. 关键设计说明

- 使用 `run_cad_validation.py --block-alpha-only` 只跑 block alpha 相关步骤，避免与 cabinet baseline 混跑。
- 真实插入 `CODEX_TEST_BLOCK_001` 到 `CODEX_PREVIEW`，`created_handles` 定向 readback，不用全 ModelSpace 扫描。
- 截图 `block-alpha-window.png` 仅为 `visual_aid_only`，不参与几何 pass 判定。

### 4. 新增/修改测试

- 全量：**259 tests OK**（footprint 对齐后无回归）

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_cad_validation.py --block-alpha-only --output-dir output\validation_runs\r-block-alpha-cad
# report.status=pass
# block_alpha.geometry_verified=true
# block_alpha_report.status=geometry_verified
```

### 6. 是否运行真实 CAD

**是**（AutoCAD `Drawing1.dwg`，用户会话 COM 可用）。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| 总控 | `output/validation_runs/r-block-alpha-cad/report.json` |
| 执行 | `output/validation_runs/r-block-alpha-cad/block_alpha_execution_summary.json` |
| readback | `output/validation_runs/r-block-alpha-cad/block_alpha_report.json` |
| 截图 | `output/validation_runs/r-block-alpha-cad/block-alpha-window.png` |
| 说明 | `docs/verification/block_alpha_cad_evidence.md` |

`created_handles`: `["878"]`

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| 受控 block alpha 样本 readback | **`geometry_verified`** / `readback_geometry_verified` |
| 截图 | `visual_aid_only`（辅助） |
| 任意块库 / 项目图纸 | **不可声称** |

### 9. 剩余风险

- DWG 中若已存在旧版 100×50 受控块定义，需删除或换名后重跑，否则 bbox 可能不一致（本轮为新插入 + readback pass）。
- 不能把本次 pass 说成公司块库或 office micro-scene 已完成。

---

## 10. R-OFFICE-MICRO-01

**日期**：2026-05-26
**父包**：`R-OFFICE-MICRO`

### 1. 开发包名

`R-OFFICE-MICRO-01` — office alpha 对象级扩展：电脑桌、储物柜柜前净空、文件柜。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `libraries/objects/object_defaults.json` | 新增 `computer_desk`、`storage_cabinet`、`file_cabinet`（含 `placement_role`、`clearance_refs`、`assertion_hints`） |
| `core/object_engine/parametric_objects.py` | `create_object_spec` 透传 `placement_role`、`clearance_refs`、`assertion_hints` |
| `core/benchmarks/runner.py` | `contains_clearance_refs` 断言；object_spec metrics 输出 `clearance_ref_roles`、`placement_role` |
| `examples/benchmarks/office_alpha_benchmark.json` | 新增 3 个 object_spec cases（7 cases 合计） |
| `tests/core/test_benchmarks.py` | office alpha 契约改为 7/7 pass |
| `docs/planning/phase-r-office-benchmark-cases.md` | 落地状态同步 |
| `CAD_AGENT_*` / `CORE_CONTEXT_BRIEF.md` | 状态同步 |

### 3. 关键设计说明

- 电脑桌默认 `1200×700×750`，`placement_role=screen_workstation`，组件含 `monitor_zone`、`cable_side_hint`。
- 储物柜 / 文件柜在 defaults 中带 `cabinet_front_clearance`（`front_depth_mm=800`），benchmark 用 `contains_clearance_refs` 机器断言。
- 仍为 non-CAD object_spec pipeline：`evidence_state=benchmark_pass_non_cad`，几何未做 CAD readback。

### 4. 新增/修改测试

- `tests.core.test_benchmarks.test_office_alpha_benchmark_runs_phase_r_contract`：7 cases、clearance / placement 断言
- 全量：**259 tests OK**（无新增独立单测文件）

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_benchmarks -v
# 11 tests OK

& $py -m unittest discover -s tests -q
# Ran 259 tests OK

& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\office_object_r1
# suite status=pass, 7/7 cases
```

### 6. 是否运行真实 CAD

**否**（仅 object_spec validate / dry-run / unverified verification）。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| benchmark 汇总 | `output/test_artifacts/benchmarks/office_object_r1/`（各 case 子目录含 `object_spec.json`、`dry_run_report.json` 等） |
| 规格参考 | `docs/planning/phase-r-office-benchmark-cases.md` |

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| 7 个 office alpha cases（含 3 个新 object cases） | **`benchmark_pass_non_cad`** |
| 几何准确性 | `not_verified_without_cad_readback` |
| 截图 | `visual_aid_only`（本包未要求截图） |
| micro-scene / failure / 办公真实 CAD | **不可声称** |

### 9. 剩余风险

- `cabinet_front_clearance` 目前只在 object spec 语义层存在，未接入 placement / collision 或真实 CAD 净空几何验证。
- 不能把 7/7 non-CAD pass 说成办公微场景、入口通道或失败样本已完成。

---

## 11. R-OFFICE-MICRO-02

**日期**：2026-05-26
**父包**：`R-OFFICE-MICRO`

### 1. 开发包名

`R-OFFICE-MICRO-02` — office alpha 微场景 benchmark：单桌椅、桌后柜、双工位主通道、入口接待净空。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/composition_engine/templates.py` | 4 个 office micro-scene 模板；`composition_micro_scene_metrics()` |
| `core/benchmarks/runner.py` | `contains_binding_relations`、`contains_circulation_roles`；composition metrics 透传 |
| `examples/benchmarks/office_alpha_benchmark.json` | 4 个 `composition_spec` micro-scene cases（11 cases 合计） |
| `tests/core/test_composition_engine.py`、`tests/core/test_benchmarks.py` | 微场景契约测试 |
| `CAD_AGENT_*` / `CORE_CONTEXT_BRIEF.md` / `phase-r-office-benchmark-cases.md` | 状态同步 |

### 3. 关键设计说明

- 微场景走既有 `composition_spec` pipeline，不新增布局算法；`bindings`、`clearance_refs`、`circulation` 为结构化语义字段。
- `single_desk_chair_pair`：椅绑桌 + `chair_pullback_clearance`。
- `desk_with_back_cabinet`：桌/椅/背柜 + 椅后与柜前双净空 refs。
- `two_workstations_shared_aisle`：双工位 + `main_aisle` circulation 语义。
- `entry_reception_clearance`：接待桌 + `entry_clearance` ref。

### 4. 新增/修改测试

- `test_office_micro_scene_compositions_expose_bindings_and_clearance`
- `test_office_alpha_benchmark_runs_phase_r_contract`：11/11
- 全量：**260 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_benchmarks tests.core.test_composition_engine -v
& $py -m unittest discover -s tests -q
& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\office_micro_r2
# 11/11 pass
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| benchmark 汇总 | `output/test_artifacts/benchmarks/office_micro_r2/` |
| 各 case | 含 `composition_spec.json`、`preview.svg`、`cad_plans.json` 等 |

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| 11 个 office alpha cases | **`benchmark_pass_non_cad`** |
| 微场景绑定 / 净空 / 通道 | 语义层可机器断言；**非几何验证** |
| 场景级扩展 / failure / 办公真实 CAD | **不可声称** |

### 9. 剩余风险

- `main_aisle` / `entry_clearance` 仅为 composition 元数据，未与 blank-shell placement 或 CAD 几何联动。
- 不能把 micro-scene pass 说成通道连续性或入口净空已在 DWG 中验证。

---

## 12. R-OFFICE-MICRO-03

**日期**：2026-05-26
**父包**：`R-OFFICE-MICRO`

### 1. 开发包名

`R-OFFICE-MICRO-03` — office alpha 场景级 blank-shell benchmark：长条主通道、障碍避让、会议/电脑混合区。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `examples/shell_models/office_long_narrow_shell.json` 等 3 个 shell | **新增** 场景 shell |
| `examples/workflows/blank_shell_office_*_layout_loop.json` ×3 | **新增** 场景 workflow |
| `core/workflows/blank_shell_pipeline.py` | metrics 增加 `no_place_zone_count`、`fixed_obstacle_count`、`shell_id` |
| `core/benchmarks/runner.py` | `_actual_from_pipeline` 透传场景 metrics |
| `examples/benchmarks/office_alpha_benchmark.json` | +3 blank_shell scene cases（14 cases 合计） |
| `tests/core/test_benchmarks.py`、`tests/core/test_schema_validation.py` | 契约与 schema 校验 |

### 3. 关键设计说明

- 场景 case 走既有 `blank_shell` pipeline，不新增布局算法。
- `long_narrow_office_main_aisle`：22000×4200 长条 shell，断言 circulation / zone / placement 与 `shell-office-long-narrow`。
- `office_obstacle_avoidance_riser`：双障碍 + 双 `no_place_zone`，断言 `no_place_zone_count` / `fixed_obstacle_count`。
- `meeting_computer_mixed_zone`：混合区 shell，`object_types` 含 `computer_desk` + `table`。

### 4. 新增/修改测试

- `test_office_alpha_benchmark_runs_phase_r_contract`：14/14
- shell schema 校验覆盖 3 个新 shell
- 全量：**260 tests OK**（无新增独立测试文件）

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_benchmarks tests.core.test_schema_validation -v
& $py -m unittest discover -s tests -q
& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\office_scene_r1
# 14/14 pass
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| benchmark 汇总 | `output/test_artifacts/benchmarks/office_scene_r1/` |

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| 14 个 office alpha cases | **`benchmark_pass_non_cad`** |
| 场景 shell / placement 指标 | 可机器断言；**非几何验证** |
| failure cases / 办公真实 CAD 几何 | **不可声称** |

### 9. 剩余风险

- `failed_check_count=0` 只表示当前 Alpha placement 未报 fail，不证明真实通道连续或障碍已避让。
- failure benchmark 已改由 `R-OFFICE-MICRO-04` 承接（见 §13）。

---

## 13. R-OFFICE-MICRO-04

**日期**：2026-05-26
**父包**：`R-OFFICE-MICRO`

### 1. 开发包名

`R-OFFICE-MICRO-04` — office alpha failure benchmark：过小房间、门前净空冲突、椅后/柜前净空冲突。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/layout_engine/office_layout_failure.py` | **新增** failure 分类与 composition 净空冲突检测 |
| `core/workflows/blank_shell_pipeline.py` | `layout_expectation` 硬阻断 partial layout |
| `core/benchmarks/runner.py` | `failure_category`、`contains_blocked_reason`、`blocked_expected_non_cad` |
| `core/composition_engine/templates.py` | +2 failure composition 模板 |
| `examples/shell_models/office_too_small_workstation_shell.json` | **新增** |
| `examples/workflows/blank_shell_office_too_small_workstation_layout_loop.json` | **新增** |
| `examples/benchmarks/office_alpha_benchmark.json` | +3 failure cases（17 cases 合计） |
| `tests/core/test_office_layout_failure.py` | **新增** |
| `tests/core/test_benchmarks.py` | office alpha 17/17 契约 |

### 3. 关键设计说明

- failure case 必须 `pipeline_status=blocked` 且 `evidence_state=blocked_expected_non_cad`，禁止少放对象后返回 pass。
- `too_small_room_for_workstation`：过小 shell + `require_all_placed` → `insufficient_space`。
- `door_clearance_conflict` / `cabinet_pullback_conflict`：composition 模板故意重叠净空语义，runner 在 dry-run 前阻断。

### 4. 新增/修改测试

- `tests/core/test_office_layout_failure.py`：3 tests
- `test_office_alpha_benchmark_runs_phase_r_contract`：17/17
- 全量：**293 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_office_layout_failure tests.core.test_benchmarks -v
& $py -m unittest discover -s tests -q
& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\office_failure_r4
# 17/17 pass（14 benchmark_pass_non_cad + 3 blocked_expected_non_cad）
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| benchmark 汇总 | `output/test_artifacts/benchmarks/office_failure_r4/` |

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| 14 个 pass office cases | **`benchmark_pass_non_cad`** |
| 3 个 failure cases | **`blocked_expected_non_cad`**（`insufficient_space` / `entry_clearance_conflict` / `clearance_conflict`） |
| 办公真实 CAD 几何 | **不可声称** |

### 9. 剩余风险

- failure 检测基于 conservative bbox / 净空语义，不是完整碰撞或通道算法。
- office alpha 汇总见 `docs/verification/office_alpha_benchmark_evidence.md`（`R-OFFICE-MICRO-05`）。

---

## 14. R-OFFICE-MICRO-05

**日期**：2026-05-26
**父包**：`R-OFFICE-MICRO`（**父包 5/5 收口**）

### 1. 开发包名

`R-OFFICE-MICRO-05` — office alpha 报告汇总、证据计数与不可声称边界。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/benchmarks/runner.py` | `summarize_benchmark_evidence()`；suite 写入 `benchmark_summary.json` |
| `docs/verification/office_alpha_benchmark_evidence.md` | **新增** Alpha 证据与退出门槛 |
| `docs/planning/phase-r-office-benchmark-cases.md` | Alpha 退出门槛表、收口证据链接 |
| `tests/core/test_benchmarks.py` | `evidence_summary` 与 summary 文件契约 |
| `CAD_AGENT_*` / `CORE_CONTEXT_BRIEF.md` | 状态同步 |

### 3. 关键设计说明

- `benchmark_summary.json` 为 suite 级机器可读出口：`evidence_state_counts`、`failure_category_counts`、`non_cad_only`。
- office alpha **仅**证明 non-CAD 规格与 failure 语义；`geometry_verified_case_count` 必须为 0。
- 父包 `R-OFFICE-MICRO` 完成后，下一队列按 PlanMD 为 `R4-EVIDENCE-GATES`。

### 4. 新增/修改测试

- `test_office_alpha_benchmark_runs_phase_r_contract`：断言 `evidence_summary`
- `test_summarize_benchmark_evidence_counts_states`
- 全量：**294 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_benchmarks -v
& $py -m unittest discover -s tests -q
& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\office_alpha_r_micro
# 17/17 pass；benchmark_summary.json: 14 benchmark_pass_non_cad + 3 blocked_expected_non_cad
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

| 类型 | 路径 |
| --- | --- |
| benchmark 汇总 | `output/test_artifacts/benchmarks/office_alpha_r_micro/benchmark_summary.json` |
| 证据说明 | `docs/verification/office_alpha_benchmark_evidence.md` |

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| office alpha 17 cases | suite `pass`；**全部 non-CAD** |
| `R-OFFICE-MICRO` 父包 | **5/5 完成** |
| 办公真实 CAD 几何 | **不可声称** |

### 9. 剩余风险

- 证据汇总依赖 runner 派生字段；跨 suite 统一门禁待 `R4-EVIDENCE-GATES`。
- office 布局真实 CAD readback 仍 deferred。

---

## 15. R4-01

**日期**：2026-05-26
**父包**：`R4-EVIDENCE-GATES`

### 1. 开发包名

`R4-01` — 统一 evidence classifier / vocabulary，避免 benchmark / CAD runner 各自拼词。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/evidence_contract.py` | 词表常量、`classify_benchmark_pipeline_evidence`、校验函数 |
| `core/benchmarks/runner.py` | 使用统一分类器；expected/actual 未知词失败 |
| `core/composition_engine/templates.py` | 从契约导入几何/截图常量 |
| `core/plan_engine/block_alpha_plan.py` | `EVIDENCE_DRY_RUN_VALID_PLAN_ONLY` 常量 |
| `core/schemas/verification_report.schema.json` | evidence_state enum 补全 |
| `docs/verification/evidence_state_vocabulary.md` | **新增** 词表说明 |
| `tests/core/test_evidence_classifier.py` | **新增** |

### 3. 关键设计说明

- 所有 benchmark `evidence_state` 必须由 `classify_benchmark_pipeline_evidence` 或契约常量产生。
- `run_benchmark_suite` 汇总时若 actual 含未知 `evidence_state` 会抛错。
- `blocked_expected_non_cad` / `invalid_configuration` 正式纳入 schema 与 `EVIDENCE_STATE_VALUES`。

### 4. 新增/修改测试

- `tests/core/test_evidence_classifier.py`：4 tests
- `test_benchmark_case_rejects_unknown_expected_evidence_state`
- 全量：**299 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_evidence_classifier tests.core.test_benchmarks tests.core.test_verification_report -v
& $py -m unittest discover -s tests -q
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

无（词表与 non-CAD benchmark 校验）。

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| evidence 词表 | 机器可读、可校验 |
| benchmark actual | 统一派生，禁止未知词 |

### 9. 剩余风险

- failure / suite 硬断言已由 `R4-02`、`R4-03` 覆盖；CAD runner gate 见 `R4-04`。

---

## 16. R4-02

**日期**：2026-05-26
**父包**：`R4-EVIDENCE-GATES`

### 1. 开发包名

`R4-02` — blocked / invalid failure benchmark 机器断言与静默 pass 防护。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/evidence_contract.py` | `validate_failure_expected_contract`、`BENCHMARK_FAILURE_CATEGORIES` |
| `core/benchmarks/runner.py` | `maximums`、`_compare_failure_outcome_guards`、配置期 failure 校验 |
| `examples/workflows/blank_shell_office_invalid_input_layout_loop.json` | **新增** invalid 样本 |
| `examples/benchmarks/office_alpha_benchmark.json` | +1 invalid case；too_small `maximums` |
| `docs/verification/evidence_state_vocabulary.md` | failure 断言说明 |
| `tests/core/test_benchmarks.py`、`tests/core/test_evidence_classifier.py` | failure 契约测试 |

### 3. 关键设计说明

- failure case 配置期必须声明 `failure_category` 或 `contains_blocked_reason`。
- 运行期禁止 `pipeline_status=ok` + `blocked_expected_non_cad` 组合（静默 pass guard）。
- `too_small` 用 `maximums.cad_plan_count: 0` 防止“少出图仍 pass”。

### 4. 新增/修改测试

- `test_benchmark_case_rejects_failure_expected_without_structured_reason`
- office alpha **18/18** pass
- 全量：**302 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_benchmarks tests.core.test_evidence_classifier -v
& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\r4_office_r2
# 18/18 pass
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/r4_office_r2/benchmark_summary.json`

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| 3× blocked + 1× invalid failure | 机器断言通过 |
| 14× pass cases | 仍为非 CAD |

### 9. 剩余风险

- suite 汇总已由 `R4-03` 覆盖；CAD runner 见 `R4-04`。

---

## 17. R4-03

**日期**：2026-05-26
**父包**：`R4-EVIDENCE-GATES`

### 1. 开发包名

`R4-03` — 三组 benchmark suite 证据汇总计数与 `expected_evidence_summary` 机器断言。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/evidence_contract.py` | `evidence_summary_rollup`、`validate_evidence_summary` |
| `core/benchmarks/runner.py` | rollup 字段、`expected_evidence_summary` 比对 |
| `examples/benchmarks/*_benchmark.json` ×3 | 增加 `expected_evidence_summary` |
| `docs/verification/evidence_state_vocabulary.md` | suite 汇总说明 |
| `tests/core/test_benchmarks.py` | `test_r4_three_benchmark_suites_match_expected_evidence_summary` |

### 3. 关键设计说明

- `benchmark_summary.json` 的 `evidence_summary` 现含 `benchmark_pass_non_cad_count`、`blocked_expected_non_cad_count`、`invalid_configuration_count` 等 rollup。
- 三组 Core benchmark 均断言 `non_cad_only=true`、`readback_geometry_verified_count=0`。
- office alpha：14 pass + 3 blocked + 1 invalid = 18。

### 4. 新增/修改测试

- `test_r4_three_benchmark_suites_match_expected_evidence_summary`
- 全量：**304 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_benchmarks.BenchmarkRunnerTests.test_r4_three_benchmark_suites_match_expected_evidence_summary -v
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\r4_blank_shell
& $py scripts\run_benchmark_suite.py examples\benchmarks\interior_delivery_benchmark.json --output-root output\test_artifacts\benchmarks\r4_interior
& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\r4_office
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

| suite | 路径 |
| --- | --- |
| blank-shell | `output/test_artifacts/benchmarks/r4_blank_shell/benchmark_summary.json` |
| interior | `output/test_artifacts/benchmarks/r4_interior/benchmark_summary.json` |
| office | `output/test_artifacts/benchmarks/r4_office/benchmark_summary.json` |

### 8. 结论分类

| 结论 | 类型 |
| --- | --- |
| 三组 suite | 全部 `pass`；证据汇总可机器断言 |
| 几何 verified | **0**（`non_cad_only=true`） |

### 9. 剩余风险

- CAD validation 顶层 gate 已由 `R4-04` 落地；交接填写规范见 `R4-05`。

---

## 18. R4-04

**日期**：2026-05-26
**父包**：`R4-EVIDENCE-GATES`

### 1. 开发包名

`R4-04` — CAD validation runner 与统一 evidence 词表对齐，禁止顶层 pass 掩盖子报告未验证。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/cad_validation_evidence.py` | **新增** summary + 顶层 gate |
| `core/verification/cad_validation_runner.py` | `evidence_summary`、步骤证据校验、gate 降级 |
| `tests/core/test_cad_validation_evidence.py` | **新增** |
| `tests/core/test_cad_validation_runner.py` | evidence_summary / 无效 evidence 回归 |
| `docs/verification/evidence_state_vocabulary.md` | CAD validation 小节 |

### 3. 关键设计说明

- `report.json` 新增 `evidence_summary`（与 benchmark 同词表 rollup）。
- `--no-cad` 顶层 pass 必须 `non_cad_only=true`。
- 含 CAD 顶层 pass 必须 `inspect_readback` + `cad_capability_probe` 步骤证据态 verified。
- 步骤 stdout 中未知 `evidence_state` 直接使步骤 fail。

### 4. 新增/修改测试

- `tests/core/test_cad_validation_evidence.py`
- `test_top_level_pass_downgraded_when_readback_evidence_state_invalid`
- 全量：**308 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_cad_validation_runner tests.core.test_cad_validation_evidence -v
& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\r4-no-cad
# status=pass, evidence_summary.non_cad_only=true
```

### 6. 是否运行真实 CAD

**否**（`--no-cad` 探针）。

### 7. CAD 证据路径

`output/validation_runs/r4-no-cad/report.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| no-CAD 总控 pass | `non_cad_only` | **否** |
| 含 CAD 真实几何 | 须用户会话下全量 CAD 复验 | 非本包范围 |

### 9. 剩余风险

- 交接模板 evidence 字段说明待 `R4-05` 统一（已完成见 §19）。

---

## 19. R4-05

**日期**：2026-05-26
**父包**：`R4-EVIDENCE-GATES`（**父包 5/5 收口**）

### 1. 开发包名

`R4-05` — 将 evidence gate 规则写入交接模板、状态文档与 Codex 校验指引。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `docs/verification/evidence_gate_handoff_rules.md` | **新增** 交接与审计规则 |
| `docs/verification/evidence_state_vocabulary.md` | 交叉引用 handoff 规则 |
| `docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` | 扩展 9 项模板；§18 R4-04；§19 本包 |
| `docs/handoffs/README.md` | 维护规则增加 evidence gate 链接 |
| `docs/planning/phase-r-rebirth-implementation-plan.md` | R4 执行记录与勾选 |
| `CAD_AGENT_STATUS.md`、`CAD_AGENT_CHANGELOG.md`、`CORE_CONTEXT_BRIEF.md` | R4 父包收口 |

### 3. 关键设计说明

- 每包第 8 项必须使用「结论 + 证据类型 + geometry_verified」三列表格。
- Codex 校验清单与机器路径约定写入 `evidence_gate_handoff_rules.md`，避免各包重复解释。
- `R4-EVIDENCE-GATES` 代码面（R4-01～04）与文档面（R4-05）均已闭环。

### 4. 新增/修改测试

无（文档包）。回归基线仍为 **308 tests OK**（未改 Core 逻辑）。

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest discover -s tests -p "test_*.py" -q
# 308 tests OK（文档包前基线）
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

无新增；规范引用既有路径见 `evidence_gate_handoff_rules.md` §3。

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 交接 evidence gate 文档化 | `non_cad_only`（文档交付） | **否** |

### 9. 剩余风险

- 历史章节（§0～§14）未逐条回填新表格格式；新包须按扩展模板填写。
- 下一小包：`Y-MC-02`（proposal 比较摘要）。

---

## 20. Y-MC-01

**日期**：2026-05-26
**父包**：`Y-MULTI-CANDIDATE`

### 1. 开发包名

`Y-MC-01` — blank-shell pipeline 在 artifact 中保留 circulation / zone / placement 多候选明细（`candidate_sets.json`）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/workflows/blank_shell_pipeline.py` | `build_blank_shell_candidate_sets()`、`_evaluate_zone_placement_candidates()`、`candidate_sets` 写出 |
| `tests/core/test_blank_shell_pipeline.py` | `candidate_sets` artifact 与分支覆盖测试 |

### 3. 关键设计说明

- `candidate_sets.json` 含 `circulation_branches[]`：每个 circulation 策略下全部 zone 的 placement 尝试（含 `summary`、`placements`、`rank_key`）。
- `selection` 记录最终选用的 circulation / zone（仍优先 `straight_spine` + 最优 placement rank）。
- `circulation_candidates.json` / `placements.json` 保持兼容；下游 layout 仍用选中结果。

### 4. 新增/修改测试

- `test_blank_shell_pipeline_writes_expected_artifacts` 增加 `candidate_sets` 断言
- `test_candidate_sets_include_all_circulation_branches`
- 全量：**309 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_blank_shell_pipeline -v
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\y_mc_01
# 4/4 pass
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/y_mc_01/<case>/candidate_sets.json`（benchmark 各 case 目录）

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 多候选 artifact 可机器读取 | `benchmark_pass_non_cad` | **否** |
| 多 circulation / zone 探索 | `non_cad_only` | **否** |

### 9. 剩余风险

- benchmark 多候选硬断言已由 `Y-MC-03` 覆盖。
- 仍不声称完整自动设计大脑或多方案已自动择优。

---

## 21. Y-MC-02

**日期**：2026-05-26
**父包**：`Y-MULTI-CANDIDATE`

### 1. 开发包名

`Y-MC-02` — proposal 输出可断言的 `comparison_detail`（对象覆盖率、失败分布、通道连续性、排序原因）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/proposal_engine/proposal_comparison.py` | `build_blank_shell_comparison_detail()`、分支候选摘要 |
| `core/proposal_engine/design_proposal.py` | 接入 `candidate_sets`；`comparison_detail` / narrative |
| `core/schemas/design_proposal.schema.json` | 可选 `comparison_detail` |
| `core/workflows/blank_shell_pipeline.py` | 传入 `candidate_sets` / `object_types` |
| `tests/core/test_proposal_multi_candidate.py`、`test_blank_shell_pipeline.py` | 结构化断言 |

### 3. 关键设计说明

- `comparison_detail.metrics`：`object_coverage_rate`、`failed_check_count`、`failed_reason_distribution`、`circulation_branch_count` 等。
- `circulation_continuity.continuity`：`pass` / `degraded` / `blocked`。
- `needs_confirmation` 仅看**选中** circulation 分支 + layout 失败，未选中分支失败仅作说明。

### 4. 新增/修改测试

- `test_blank_shell_comparison_detail_is_structured_and_assertable`
- pipeline artifact 断言 `comparison_detail`
- 全量：**310 tests OK**

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_proposal_multi_candidate tests.core.test_blank_shell_pipeline -v
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\y_mc_02
# 4/4 pass
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/y_mc_02/<case>/design_proposal.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 多候选比较摘要可机器读取 | `benchmark_pass_non_cad` | **否** |
| 候选说明保留 | `non_cad_only` | **否** |

### 9. 剩余风险

- benchmark 对 `comparison_detail` 的硬断言已由 `Y-MC-03` 完成。

---

## 22. Y-MC-03

**日期**：2026-05-26
**父包**：`Y-MULTI-CANDIDATE`

### 1. 开发包名

`Y-MC-03` — blank-shell benchmark 多候选指标机器断言。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/benchmarks/runner.py` | actual 字段 + `requires_comparison_detail` 等 |
| `examples/benchmarks/blank_shell_core_benchmark.json` | 四 case 硬断言 |
| `core/workflows/blank_shell_pipeline.py`、`proposal_comparison.py` | metrics 派生 |
| `tests/core/test_benchmarks.py` | `test_y_mc_03_*` |

### 3. 关键设计说明

- 候选数：`candidate_count`、`zone_placement_candidate_count`、`circulation_branch_count`。
- 对象覆盖：`object_coverage_rate` / `comparison_detail_minimums`。
- 失败分布：`selected_failed_reason_distribution`、`failed_reason_distribution_empty`。

### 4. 新增/修改测试

- `test_y_mc_03_blank_shell_benchmark_multi_candidate_assertions`
- 全量：**311 tests OK**

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_benchmarks.BenchmarkRunnerTests.test_y_mc_03_blank_shell_benchmark_multi_candidate_assertions -v
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\y_mc_03
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/y_mc_03/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 多候选 benchmark 契约 | `benchmark_pass_non_cad` | **否** |

### 9. 剩余风险

- 近真实 / 失败 shell 样本已由 `Y-MC-04` 纳入 blank-shell core benchmark。

---

## 23. Y-MC-04

**日期**：2026-05-26
**父包**：`Y-MULTI-CANDIDATE`

### 1. 开发包名

`Y-MC-04` — blank-shell core 增补近真实 shell 与结构化 failure 样本（8 cases）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `examples/shell_models/blank_shell_corridor_riser_block_shell.json` | **新增** |
| `examples/workflows/blank_shell_corridor_riser_block_layout_loop.json` | **新增** |
| `examples/benchmarks/blank_shell_core_benchmark.json` | +4 cases |
| `core/workflows/blank_shell_pipeline.py` | blocked metrics |
| `tests/core/test_benchmarks.py` | Y-MC-04 测试 |

### 3. 关键设计说明

- Pass：`long_narrow`、`obstacle`（障碍不压、对象仍放置）。
- Blocked：`too_small`、`corridor_riser_blocks_main_path`（`cad_plan_count: 0`）。

### 4. 新增/修改测试

- 全量：**312 tests OK**

### 5. 实际运行的命令和结果

```powershell
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\y_mc_04
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/y_mc_04/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 8-case blank-shell suite | `benchmark_pass_non_cad` / `blocked_expected_non_cad` | **否** |

### 9. 剩余风险

- 多候选边界文档已由 `Y-MC-05` 收口。

---

## 24. Y-MC-05

**日期**：2026-05-26
**父包**：`Y-MULTI-CANDIDATE`（**父包 5/5 收口**）

### 1. 开发包名

`Y-MC-05` — Phase Y 状态同步与多候选不可声称边界文档化。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `docs/verification/blank_shell_multi_candidate_boundaries.md` | **新增** 边界与 benchmark 契约 |
| `docs/planning/phase-y-blank-shell-hardening-plan.md` | `Y-MC` 映射与退出标准更新 |
| `docs/architecture/shell-layout-foundation-design.md` | §0.1 落地状态 |
| `CORE_*` / `CAD_AGENT_*` / `phase-r-rebirth-implementation-plan.md` | 父包收口 |

### 3. 关键设计说明

- 多候选是 **Alpha 硬化**：可解释、可 benchmark，**不是**完整自动设计大脑。
- 全部 blank-shell core 证据为 non-CAD；`geometry_verified` 仍为 0。
- 后置：复杂几何、自动读图、BETA-PROPOSAL 确认流。

### 4. 新增/修改测试

无（文档包）。基线 **312 tests OK**；benchmark 复验 8/8 pass。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_blank_shell_pipeline tests.core.test_proposal_multi_candidate tests.core.test_benchmarks -q
& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\y_mc_05
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/y_mc_05/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| `Y-MULTI-CANDIDATE` 父包收口 | `non_cad_only`（文档 + benchmark） | **否** |

### 9. 剩余风险

- 下一主线 `X-SCENE-ALPHA`；Scene Agent 不得复制 Core 多候选算法。

---

## 25. X-SCENE-01

**日期**：2026-05-26
**父包**：`X-SCENE-ALPHA`

### 1. 开发包名

`X-SCENE-01` — 锁定 office / residential / restaurant 与可观察 preferences 差异。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/agents/scene_alpha.py` | **新增** 场景校验与权重辅助 |
| `agents/scene_alpha_manifest.json` | **新增** 三场景 manifest |
| `agents/*/preferences.json` | `scene_alpha.tier` + `circulation_strategy_weights` |
| `docs/verification/scene_alpha_preferences_contract.md` | **新增** |
| `tests/agents/test_scene_preferences.py` | X-SCENE-01 断言 |

### 3. 关键设计说明

- 场景层只表达偏好，不复制 Core pipeline / 几何算法。
- 可观察差异：对象优先级、通道宽度、动线权重导致的 Top-1 候选变化。

### 4. 新增/修改测试

- **315 tests OK**；`tests/agents/test_scene_preferences.py` 中 `test_x_scene_01_*`。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.agents.test_scene_preferences -v
```

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

无（preferences 契约包）。

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Scene Alpha preferences 契约 | unit tests only | **否** |

### 9. 剩余风险

- 偏好差异须接入同一 Core benchmark（`X-SCENE-02`）。

---

## 26. X-SCENE-02

**日期**：2026-05-26
**父包**：`X-SCENE-ALPHA`

### 1. 开发包名

`X-SCENE-02` — 三场景复用同一 `blank_shell` Core pipeline / benchmark。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `examples/benchmarks/scene_alpha_benchmark.json` | **新增** 3 cases |
| `core/workflows/blank_shell_pipeline.py` | `scene_preferences` 驱动动线选型；metrics 导出场景字段 |
| `core/benchmarks/runner.py` | `selected_circulation_strategy`、`preferences_scenario`、`preferences_path_contains` |
| `core/layout_engine/zone_splitter.py` | L 形走道 `path_surface` 并集切区 |
| `agents/scene_alpha_manifest.json` | 挂接 benchmark suite |
| `tests/core/test_benchmarks.py` | `test_x_scene_02_*` |
| `tests/core/test_zone_splitter.py` | along_wall 可用区断言 |

### 3. 关键设计说明

- 三场景共用 `pipeline: blank_shell` + 既有 workflow；`agents/` 无 Core 逻辑副本。
- `circulation_strategy_weights` 在 pipeline 内选 Top-1（与 X-SCENE-01 单测一致）。
- `zone_splitter` 对多段 `path_surface` 取并集 bbox，避免 along_wall 只按首段切区导致放置失败。

### 4. 新增/修改测试

- **317 tests OK**
- `test_x_scene_02_scene_alpha_multi_scene_benchmark`

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.agents.test_scene_preferences tests.core.test_benchmarks.BenchmarkRunnerTests.test_x_scene_02_scene_alpha_multi_scene_benchmark -v
& $py scripts\run_benchmark_suite.py examples\benchmarks\scene_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\x_scene_02
```

3/3 pass；`selected_circulation_strategy`：office `straight_spine`、residential `along_wall`、restaurant `l_spine`。

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/x_scene_02/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 三场景 blank_shell benchmark | `benchmark_pass_non_cad` | **否** |

### 9. 剩余风险

- 下一小包 `X-SCENE-03`：边界扫描；仍不能把 non-CAD pass 说成几何已验证。

---

## 27. X-SCENE-03

**日期**：2026-05-26
**父包**：`X-SCENE-ALPHA`

### 1. 开发包名

`X-SCENE-03` — 加强 Scene Agent 边界扫描。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/agents/scene_boundary_scan.py` | **新增** 静态扫描器 |
| `tests/agents/test_scene_agent_boundaries.py` | `test_x_scene_03_*`、接入扫描器 |
| `agents/SCENE_AGENT_RULES.md` | 边界扫描章节 |
| `docs/verification/scene_alpha_agent_boundaries.md` | **新增** |
| `agents/residential/rules.md`、`agents/restaurant/rules.md` | Core 边界表述补强 |

### 3. 关键设计说明

- `agents/` 不得含 `*.py`；禁止 CAD 执行、回读、几何库、blank-shell pipeline 实现符号及 `from core.*` 实现导入。
- `SCENE_AGENT_RULES.md` 为禁止项目录文档，扫描时排除以免自引用误报。
- 合成违规样例测试确保扫描器可检出越界。

### 4. 新增/修改测试

- **322 tests OK**
- `test_x_scene_03_agent_tree_passes_boundary_scan` 等

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.agents.test_scene_agent_boundaries tests.agents.test_scene_preferences -v
```

0 violations on `agents/` tree.

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

无（静态边界包）。

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Scene Agent 边界扫描 | unit tests + static scan | **否** |

### 9. 剩余风险

- 静态子串扫描不能替代 runtime 审计；下一小包 `X-SCENE-04` 补解释模板与交接。

---

## 28. X-SCENE-04

**日期**：2026-05-26
**父包**：`X-SCENE-ALPHA`

### 1. 开发包名

`X-SCENE-04` — 场景解释模板与交接（偏好如何影响 Core）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/agents/scene_explanation.py` | **新增** `build_scene_explanation()` |
| `docs/verification/scene_alpha_explanation_template.md` | **新增** |
| `tests/agents/test_scene_explanation.py` | **新增** `test_x_scene_04_*` |
| `agents/office|residential|restaurant/rules.md` | Preference→Core + 不可声称 |
| `docs/onboarding/first-handoff.md` | Scene Alpha 接手段 |
| `core/agents/scene_boundary_scan.py` | `rules.md` 文档引用例外 |

### 3. 关键设计说明

- 场景层只解释偏好如何进入 Core（path_generation、blank_shell_pipeline 等），不声称独立 Agent 大脑。
- `rules.md` 可写 Core 入口名；`preferences.json` 仍受完整边界扫描。

### 4. 新增/修改测试

- **326 tests OK**

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.agents.test_scene_explanation -v
& $py scripts\run_benchmark_suite.py examples\benchmarks\scene_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\x_scene_04
```

3/3 pass。

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/x_scene_04/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Scene Alpha 解释模板 | docs + unit tests + non-CAD benchmark | **否** |

### 9. 剩余风险

- 下一小包 `X-SCENE-05`：父包总验收与状态收口。

---

## 29. X-SCENE-05

**日期**：2026-05-26
**父包**：`X-SCENE-ALPHA`（**父包 5/5 收口**）

### 1. 开发包名

`X-SCENE-05` — Scene Alpha 总验收与状态同步。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `docs/verification/scene_alpha_acceptance.md` | **新增** 父包可声称/不可声称 |
| `tests/agents/test_scene_alpha_acceptance.py` | **新增** `test_x_scene_05_*` |
| `agents/scene_alpha_manifest.json` | `acceptance_doc`、`parent_package_status` |
| `docs/planning/phase-x-scene-agent-alpha-plan.md` | 退出标准已满足 |
| `CORE_*` / `CAD_AGENT_*` / `phase-r-rebirth-implementation-plan.md` | 父包收口 |

### 3. 关键设计说明

- 汇总 01–04：preferences 差异、三场景 benchmark、边界扫描、解释模板。
- **可声称**三场景复用同一 Core `blank_shell` pipeline（non-CAD）。
- **不可声称** `geometry_verified`、Scene Agent 产品完成。

### 4. 新增/修改测试

- **332 tests OK**；`test_scene_alpha_acceptance`（6 cases）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.agents.test_scene_alpha_acceptance tests.agents -v
& $py -m unittest discover -s tests -p test_*.py -q
& $py scripts\run_benchmark_suite.py examples\benchmarks\scene_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\x_scene_05
```

3/3 pass；全量 **332 tests OK**。

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/x_scene_05/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| `X-SCENE-ALPHA` 父包收口 | non-CAD benchmark + agent tests + static scan | **否** |

### 9. 剩余风险

- 后置主线见 `CORE_RESTRUCTURE_PLAN.md`（真实 CAD 扩展、项目样本、Scene Beta 等）。

---

## 父包收口：`X-SCENE-ALPHA`（5/5）

| 小包 | 状态 |
| --- | --- |
| X-SCENE-01 | ✅ preferences 契约 |
| X-SCENE-02 | ✅ 三场景 benchmark |
| X-SCENE-03 | ✅ 边界扫描 |
| X-SCENE-04 | ✅ 解释模板 |
| X-SCENE-05 | ✅ 总验收 |

**统一证据**：`docs/verification/scene_alpha_acceptance.md`；`332 tests OK`；scene alpha benchmark `readback_geometry_verified_count=0`。

---

## 30. BETA-CAD-BLOCK-01

**日期**：2026-05-26
**父包**：后置主线「真实 CAD 能力扩展」

### 1. 开发包名

`BETA-CAD-BLOCK-01` — 受控 block beta：多锚点、rotation、uniform scale。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `examples/plans/block_alpha_beta_suite.json` | **新增** 8 cases |
| `core/verification/block_alpha_beta_suite.py` | **新增** runner |
| `scripts/run_block_alpha_beta_suite.py` | **新增** CLI |
| `tests/core/test_block_alpha_beta_suite.py` | **新增** |
| `docs/verification/beta_cad_block_01_boundaries.md` | **新增** |

### 3. 关键设计说明

- 仍仅限 `controlled-test-block-001` / `CODEX_PREVIEW`；uniform scale only。
- 8 cases 覆盖 3 锚点、2 旋转、2 缩放、1 组合变换。

### 4. 新增/修改测试

- **336 tests OK**（+4）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_block_alpha_beta_suite -v
& $py scripts\run_block_alpha_beta_suite.py --output-root output\test_artifacts\block_alpha_beta\beta_cad_block_01
```

8/8 pass；`geometry_verified_count=0`。

### 6. 是否运行真实 CAD

**否**。

### 7. CAD 证据路径

`output/test_artifacts/block_alpha_beta/beta_cad_block_01/block_alpha_beta_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Block transform beta (no-CAD) | `dry_run_valid_plan_only` | **否** |

### 9. 剩余风险

- 真实 CAD 多变换 readback 留给 `BETA-CAD-BLOCK-02` 及后续。

---

## 31. BETA-CAD-BLOCK-02

**日期**：2026-05-26
**父包**：后置主线「真实 CAD 能力扩展」

### 1. 开发包名

`BETA-CAD-BLOCK-02` — 受控属性块 / tag readback 探针。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/block_attribute_probe.py` | **新增** |
| `core/verification/inspect_dwg.py` | `GetAttributes()` 归一化 |
| `core/verification/block_alpha_validation.py` | 合并 attribute 判定 |
| `core/plan_engine/block_alpha_plan.py` | `attribute_readback_probe` 校验 |
| `examples/plans/insert_block_alpha_attribute_probe.json` | **新增** |
| `tests/core/test_block_attribute_probe.py` | **新增** |

### 3. 关键设计说明

- 无 probe 标记 → attribute 检查 `not_run`（不误报）。
- 有 probe 但实体无 tag → `deferred` / `attribute_unverified`，禁止 `geometry_verified`。
- COM insert 仍拒绝 attributes 写入。

### 4. 新增/修改测试

- **344 tests OK**（+8）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_block_attribute_probe -v
```

### 6. 是否运行真实 CAD

**否**（模拟实体 + 报告逻辑；COM insert 仍 deferred）。

### 7. CAD 证据路径

无（探针逻辑包）。

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Attribute readback probe | unit tests + simulated entity | **否** |

### 9. 剩余风险

- 真实 CAD 受控属性块 DWG 与 COM 写入留给后续包。

---

## §32 `BETA-CAD-BLOCK-03` — Entity-Level Capability Probe Evidence

**日期**：2026-05-26
**父包**：后置主线「真实 CAD 能力扩展」

### 1. 开发包名

`BETA-CAD-BLOCK-03` — hatch / polyline / layer mapping 受控写读探针（entity-level evidence）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/entity_level_evidence.py` | **新增** |
| `core/verification/cad_capability_probe.py` | `entity_evidence[]` + hatch deferred 槽位 |
| `core/verification/evidence_contract.py` | `hatch` 契约、`validate` 门槛 |
| `core/verification/inspect_dwg.py` | Hatch 归一化 |
| `docs/verification/beta_cad_block_03_boundaries.md` | **新增** |
| `tests/core/test_entity_level_probe.py` | **新增** |
| `tests/core/test_cad_capability_probe.py` | entity_evidence 断言 |
| `tests/core/test_cad_validation_runner.py` | probe payload 含 entity_evidence |

### 3. 关键设计说明

- polyline：写入点集 / closed / `layer_role=preview` → readback 对比 + layer mapping。
- hatch：仅结构化 **deferred**（`hatch_unverified`），无 COM 写入。
- `cad_capability_verified` 仍可通过（hatch deferred 不阻断）。

### 4. 新增/修改测试

- **350 tests OK**（+6）

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest discover -s tests -p "test_*.py" -q
# Ran 350 tests in 3.6s — OK
```

### 6. 是否运行真实 CAD

**否**（FakeCadDriver + 报告/门控逻辑）。

### 7. CAD 证据路径

无（non-CAD 单测）。

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Entity-level probe contract | unit tests + fake driver probe | **否**（hatch deferred；非用户 AutoCAD 会话） |

### 9. 剩余风险

- 真实 CAD hatch 写入/readback 留给后续包。
- 正式图层 / `drawing_standard_profile` 未覆盖（`BETA-CAD-BLOCK-04`）。

---

## §33 `BETA-CAD-BLOCK-04` — Drawing Standard Profile

**日期**：2026-05-26
**父包**：后置主线「真实 CAD 能力扩展」

### 1. 开发包名

`BETA-CAD-BLOCK-04` — 最小 `drawing_standard_profile` 与 role→预览层/样式映射。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/drawing_standard/drawing_standard_profile.py` | **新增** |
| `libraries/drawing_standards/codex_preview_beta.json` | **新增** |
| `libraries/layer_presets/codex_preview_beta.json` | **新增** |
| `core/schemas/drawing_standard_profile.schema.json` | **新增** |
| `core/schemas/layer_preset.schema.json` | **新增** |
| `core/verification/drawing_standard_beta_suite.py` | **新增** |
| `examples/plans/drawing_standard_beta_suite.json` | **新增** |
| `scripts/run_drawing_standard_beta_suite.py` | **新增** |
| `core/plan_engine/block_alpha_plan.py` | dry-run 支持 profile |
| `core/verification/entity_level_evidence.py` | profile layer mapping |

### 3. 关键设计说明

- `preview_only`：CAD 执行一律 `CODEX_PREVIEW`；`A-FURN` 等为语义层。
- `object_role_bindings` + `resolve_object_role` / `apply_drawing_standard_to_plan`。
- 6-case beta suite：role 解析 + block insert dry-run + primitive 样式。

### 4. 新增/修改测试

- **359 tests OK**（+9）

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest discover -s tests -p "test_*.py" -q
# Ran 359 tests — OK
```

### 6. 是否运行真实 CAD

**否**（schema + dry-run + fake 逻辑）。

### 7. CAD 证据路径

无（non-CAD）。artifact：`output/test_artifacts/drawing_standard_beta/beta_cad_block_04/`。

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Drawing standard profile beta | schema + dry-run suite | **否** |

### 9. 剩余风险

- 正式图层写入、公司制图标准、真实 CAD 样式仍 deferred（`BETA-CAD-BLOCK-05` 汇总边界）。

---

## §34 `BETA-CAD-BLOCK-05` — CAD Beta 证据 Rollup（父包收口）

**日期**：2026-05-26
**父包**：后置主线「真实 CAD 能力扩展」**5/5 收口**

### 1. 开发包名

`BETA-CAD-BLOCK-05` — 汇总 01–04 non-CAD 证据 + 不可声称边界。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/cad_beta_evidence_rollup.py` | **新增** |
| `core/verification/fake_cad_driver.py` | **新增**（自 probe 测试抽出） |
| `scripts/run_cad_beta_evidence_rollup.py` | **新增** |
| `docs/verification/beta_cad_block_acceptance.md` | **新增** |
| `docs/verification/beta_cad_block_evidence_rollup.md` | **新增** |
| `docs/verification/beta_cad_block_05_boundaries.md` | **新增** |
| `tests/core/test_cad_beta_block_acceptance.py` | **新增** |

### 3. 关键设计说明

- rollup 依次执行 block alpha suite、attribute 合成探针、Fake capability probe、drawing standard suite、文档包校验。
- `evidence_summary.geometry_verified_count` 恒为 0；真实 CAD 仅 `real_cad_reference` 路径引用。

### 4. 新增/修改测试

- **362 tests OK**（+3）

### 5. 实际运行的命令和结果

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_cad_beta_block_acceptance -v
& $py scripts\run_cad_beta_evidence_rollup.py
```

### 6. 是否运行真实 CAD

**否**（rollup non-CAD；引用历史 validation 路径不重跑 COM）。

### 7. CAD 证据路径

`output/test_artifacts/cad_beta_evidence/beta_cad_block_05/cad_beta_evidence_rollup.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| BETA-CAD-BLOCK 父包 rollup | machine rollup + acceptance doc | **否** |

### 9. 剩余风险

- 正式图层 / 公司块库 / hatch 真实 CAD 仍 deferred；见 `BETA-PROJECT-SAMPLE` 后置主线。

---

## §35 `BETA-PROJECT-SAMPLE-01` — 脱敏样本目录协议

**日期**：2026-05-26
**父包**：后置主线「真实项目样本闭环」

### 1. 开发包名

`BETA-PROJECT-SAMPLE-01` — `projects/` 脱敏样本目录协议与 manifest 扫描。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `projects/README.md` | 扩展六大章节协议 |
| `projects/sample_blank_shell/sample.manifest.json` | **新增** |
| `projects/sample_blank_shell/README.md` | **新增** |
| `core/project_samples/protocol.py` | **新增** |
| `core/schemas/project_sample_manifest.schema.json` | **新增** |
| `scripts/run_project_sample_protocol_scan.py` | **新增** |
| `docs/verification/beta_project_sample_01_boundaries.md` | **新增** |

### 3. 关键设计说明

- 每样本：`README.md` + `sample.manifest.json` + `input/` + `expected/expected_notes.md`。
- 禁止提交 `.dwg` / `.dxf`；`evidence_claim` 默认 `non_cad_pipeline_only`。

### 4. 新增/修改测试

- **366 tests OK**（+4）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_project_sample_protocol -v
& $py scripts\run_project_sample_protocol_scan.py
```

### 6. 是否运行真实 CAD

**否**（文档与目录协议 only）。

### 7. CAD 证据路径

`output/test_artifacts/project_samples/beta_project_sample_01/protocol_scan.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Sample protocol scan pass | manifest schema + directory scan | **否** |

### 9. 剩余风险

- 尚无端到端样本 workflow/benchmark（`BETA-PROJECT-SAMPLE-02` 起）。

---

## §36 `BETA-PROJECT-SAMPLE-02` — 样本 Shell / Project Model Fixture

**日期**：2026-05-26
**父包**：后置主线「真实项目样本闭环」

### 1. 开发包名

`BETA-PROJECT-SAMPLE-02` — `sample_blank_shell` shell + PROJECT_MODEL 金样与 manifest loader。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/project_samples/loader.py` | **新增** |
| `projects/sample_blank_shell/fixtures/` | brief + drawing |
| `projects/sample_blank_shell/expected/project_model.expected.json` | **新增** |
| `projects/sample_blank_shell/sample.manifest.json` | 扩展 input_files |
| `tests/core/test_project_sample_loader.py` | **新增** |

### 3. 关键设计说明

- `load_sample_inputs` 先跑协议扫描再按 manifest 加载。
- `build_sample_project_model` = brief + drawing + shell → `PROJECT_MODEL`。
- 金样全量 equality + schema 校验。

### 4. 新增/修改测试

- **371 tests OK**（+5）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_project_sample_loader -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

无（non-CAD fixture / builder）

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Sample PROJECT_MODEL fixture | loader tests + golden JSON | **否** |

### 9. 剩余风险

- 尚未有样本级 workflow / CAD_PLAN 输出（`BETA-PROJECT-SAMPLE-03`）。

---

## §37 `BETA-PROJECT-SAMPLE-03` — 样本 Workflow 输出

**日期**：2026-05-26
**父包**：后置主线「真实项目样本闭环」

### 1. 开发包名

`BETA-PROJECT-SAMPLE-03` — `sample_blank_shell` blank-shell workflow → CAD_PLAN / dry-run / verification。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `examples/workflows/sample_blank_shell_project_loop.json` | **新增** |
| `core/project_samples/workflow.py` | **新增** |
| `scripts/run_project_sample_workflow.py` | **新增** |
| `tests/core/test_project_sample_workflow.py` | **新增** |

### 3. 关键设计说明

- inputs 指向 `projects/sample_blank_shell/` fixtures。
- 契约：`dry_run valid`、`verification unverified`、`CODEX_PREVIEW` layer。
- `sample_workflow_report.json` 固定 `geometry_verified: false`。

### 4. 新增/修改测试

- **373 tests OK**（+2）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_project_sample_workflow -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/project_samples/beta_project_sample_03/`（含 `cad_plan.json`、`dry_run_report.json`、`verification_report.json`）

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Sample workflow non-CAD | pipeline artifacts + contract validator | **否** |

### 9. 剩余风险

- 未纳入 benchmark（已由 `BETA-PROJECT-SAMPLE-04` 收口）；无真实 CAD readback（`05`）。

---

## §38 `BETA-PROJECT-SAMPLE-04` — 样本 Benchmark

**日期**：2026-05-26
**父包**：后置主线「真实项目样本闭环」

### 1. 开发包名

`BETA-PROJECT-SAMPLE-04` — 将 `projects/` 路径样本 workflow 纳入 benchmark（成功 + structured blocked）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `projects/sample_blank_shell_too_small/` | **新增**（过小 shell + manifest + fixtures） |
| `examples/workflows/sample_blank_shell_too_small_loop.json` | **新增** |
| `examples/benchmarks/project_sample_benchmark.json` | **新增**（2 cases） |
| `core/project_samples/benchmark.py` | **新增** |
| `scripts/run_project_sample_benchmark.py` | **新增** |
| `tests/core/test_project_sample_benchmark.py` | **新增** |
| `docs/verification/beta_project_sample_04_boundaries.md` | **新增** |

### 3. 关键设计说明

- **pass**：`sample_blank_shell_project_loop` → `benchmark_pass_non_cad`，`cad_plan_count≥5`。
- **blocked**：过小 shell + `require_all_placed` → `blocked_expected_non_cad`，`cad_plan_count=0`。
- `evidence_summary.readback_geometry_verified_count=0`；禁止把 benchmark pass 当成几何已验证。

### 4. 新增/修改测试

- **377 tests OK**（+4）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_project_sample_benchmark -v
& $py scripts\run_project_sample_benchmark.py
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/beta_project_sample_04/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Sample benchmark pass | `benchmark_pass_non_cad` | **否** |
| Sample benchmark blocked | `blocked_expected_non_cad` | **否** |

### 9. 剩余风险

- 无真实 CAD `CODEX_PREVIEW` readback（已由 `BETA-PROJECT-SAMPLE-05` 提供 CLI；unittest 使用 `FakeCadDriver`）。

---

## §39 `BETA-PROJECT-SAMPLE-05` — 样本可选真实 CAD 验证

**日期**：2026-05-26
**父包**：后置主线「真实项目样本闭环」收口

### 1. 开发包名

`BETA-PROJECT-SAMPLE-05` — `sample_blank_shell` 多 CAD_PLAN 在 `CODEX_PREVIEW` 批量落图 + created-handle readback。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/project_samples/cad_check.py` | **新增** |
| `scripts/run_project_sample_cad_check.py` | **新增** |
| `tests/core/test_project_sample_cad_check.py` | **新增** |
| `docs/verification/beta_project_sample_05_boundaries.md` | **新增** |
| `docs/verification/beta_project_sample_acceptance.md` | **新增**（父包 01–05） |

### 3. 关键设计说明

- 复用 `execute_plan_batch`；默认偏移 `[28000, 12000, 0]` 避开既有 benchmark 区域。
- `--no-cad` → `deferred_cad_readback_required`；真实 CAD 需用户 AutoCAD 会话。
- `safety` 固定：不保存 DWG、不删实体、不改正式图层。

### 4. 新增/修改测试

- **381 tests OK**（+4）；`FakeCadDriver` → `geometry_verified`。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_project_sample_cad_check -v
& $py scripts\run_project_sample_cad_check.py --no-cad
```

### 6. 是否运行真实 CAD

**否**（CI / 本回合）；CLI 支持用户会话下真实 CAD。

### 7. CAD 证据路径

- deferred：`output/validation_runs/beta-project-sample-05-cad/project_sample_cad_check_report.json`
- 真实 CAD：同上路径，`status=geometry_verified`（需用户本地执行）

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Fake driver batch readback | `readback_geometry_verified` | **是**（测试环境） |
| `--no-cad` CLI | `deferred_cad_readback_required` | **否** |

### 9. 剩余风险

- 本回合未在用户 AutoCAD 会话复验真实 COM；不得把 deferred CLI 当成几何已验证。

---

## §40 `BETA-PROPOSAL-01` — 候选评分与排序原因

**日期**：2026-05-26
**父包**：后置主线「多方案设计与交互确认」

### 1. 开发包名

`BETA-PROPOSAL-01` — 固化 `score_breakdown` 与结构化 `ranking_reasons`。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/proposal_engine/candidate_scoring.py` | **新增** |
| `core/schemas/proposal_candidate_scoring.schema.json` | **新增** |
| `core/schemas/design_proposal.schema.json` | 扩展 candidates |
| `core/proposal_engine/proposal_comparison.py` | 接入 scoring |
| `core/proposal_engine/design_proposal.py` | 接入 scoring |
| `tests/core/test_proposal_candidate_scoring.py` | **新增** |
| `examples/design_proposals/*.json` | 补全 scoring 字段 |

### 3. 关键设计说明

- `score_breakdown.components`：`layout_base` / `check_penalty` / `preference_boost`。
- `ranking_reasons[].code` 受控词表（如 `highest_weighted_score`、`scene_preference_boost`）。
- layout comparison 与 design proposal 候选均可机器断言。

### 4. 新增/修改测试

- **384 tests OK**（+3）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_proposal_candidate_scoring -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

无（non-CAD proposal 层）

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Proposal scoring contract | schema + unit tests | **否** |

### 9. 剩余风险

- 尚无 benchmark 级对比摘要硬断言（`BETA-PROPOSAL-02`）；无用户确认流（`03`–`05`）。

---

## §41 `BETA-PROPOSAL-02` — 候选对比摘要 Benchmark

**日期**：2026-05-26
**父包**：后置主线「多方案设计与交互确认」

### 1. 开发包名

`BETA-PROPOSAL-02` — `proposal_comparison_summary` + benchmark 硬断言。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/proposal_engine/comparison_summary.py` | **新增** |
| `core/schemas/proposal_comparison_summary.schema.json` | **新增** |
| `examples/benchmarks/proposal_comparison_benchmark.json` | **新增**（4 cases） |
| `core/workflows/blank_shell_pipeline.py` | summary artifact + metrics |
| `core/benchmarks/runner.py` | 新断言键 + `placed_count` |
| `tests/core/test_proposal_comparison_benchmark.py` | **新增** |

### 3. 关键设计说明

- 从 `comparison_detail` 提炼四类摘要区块；`ranking_reason_codes` 聚合结构化 reason code。
- Benchmark 断言：`requires_proposal_comparison_summary`、`proposal_comparison_summary_minimums`、`contains_ranking_reason_code` 等。

### 4. 新增/修改测试

- **387 tests OK**（+3）；benchmark 4/4 pass。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_proposal_comparison_benchmark -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/beta_proposal_02/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Comparison summary benchmark | `benchmark_pass_non_cad` | **否** |

### 9. 剩余风险

- 无局部修改重算 CAD_PLAN（`BETA-PROPOSAL-04`–`05`）。

---

## §42 `BETA-PROPOSAL-03` — 用户确认输入 Schema

**日期**：2026-05-26
**父包**：后置主线「多方案设计与交互确认」

### 1. 开发包名

`BETA-PROPOSAL-03` — `PROPOSAL_USER_CONFIRMATION` schema + apply round-trip。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/schemas/proposal_user_confirmation.schema.json` | **新增** |
| `core/proposal_engine/user_confirmation.py` | **新增** |
| `examples/confirmations/*.json` | **新增** |
| `scripts/apply_proposal_user_confirmation.py` | **新增** |
| `tests/core/test_proposal_user_confirmation.py` | **新增** |

### 3. 关键设计说明

- `action`: `accept` / `accept_with_risks` / `reject_all`。
- `rejected_candidates[].reason_code` 受控词表；`local_preferences` 承载权重与备注。
- `apply_user_confirmation` 写入 `user_confirmation` 并更新 `confirmed_candidate_id`。

### 4. 新增/修改测试

- **393 tests OK**（+6）

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_proposal_user_confirmation -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

无

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Confirmation schema round-trip | unit tests | **否** |

### 9. 剩余风险

- blank-shell circulation `candidate_id` 与 layout `candidate_id` 对齐仍待 `04`/`05` 深化。

---

## §43 `BETA-PROPOSAL-04` — 局部修改重算 CAD_PLAN

**日期**：2026-05-26
**父包**：后置主线「多方案设计与交互确认」

### 1. 开发包名

`BETA-PROPOSAL-04` — placement 局部修改后仅重算下游 CAD_PLAN 产物。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/proposal_engine/partial_replan.py` | **新增** |
| `scripts/run_proposal_partial_replan.py` | **新增** |
| `tests/core/test_proposal_partial_replan.py` | **新增** |
| `docs/verification/beta_proposal_04_boundaries.md` | **新增** |

### 3. 关键设计说明

- `modules_skipped`：shell / project / circulation / candidate_sets / function_zones。
- `placement_offsets` 按 `object_spec_id` 应用；可来自 CLI 或 `user_confirmation.local_preferences`。
- `ensure_layout_confirmed_candidate_id` 桥接 circulation 与 layout candidate id。

### 4. 新增/修改测试

- **395 tests OK**（+2）；上游 artifact SHA256 不变回归。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_proposal_partial_replan -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/proposal_partial_replan/retail_baseline/partial_replan_report.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Partial replan non-CAD | dry-run valid + module skip report | **否** |

### 9. 剩余风险

- 未选方案证据归档与确认后受控落图（`BETA-PROPOSAL-05`）。

---

## §44 `BETA-PROPOSAL-05` / 父包 `BETA-PROPOSAL` 收口

**日期**：2026-05-26
**父包**：后置主线「多方案设计与交互确认」

### 1. 开发包名

`BETA-PROPOSAL-05` — 确认后受控 CAD_PLAN bundle + 未选方案证据；父包 01–05 收口。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/proposal_engine/confirmed_finalize.py` | **新增** |
| `core/schemas/confirmed_cad_plan_bundle.schema.json` | **新增** |
| `examples/benchmarks/proposal_confirmed_benchmark.json` | **新增** |
| `core/proposal_engine/confirmed_benchmark.py` | **新增** |
| `core/proposal_engine/proposal_acceptance.py` | **新增** |
| `tests/core/test_proposal_confirmed_*.py` | **新增** |

### 3. 关键设计说明

- `finalize_confirmed_cad_plans`：确认 → partial replan → validate + dry-run → bundle。
- `unselected_candidate_evidence` 保留未选候选、拒绝原因、comparison 摘要。
- 受控策略：`CODEX_PREVIEW`、`needs_confirmation=false`、不保存 DWG。

### 4. 新增/修改测试

- **400 tests OK**（+5）；confirmed benchmark 2/2 pass。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_proposal_confirmed_finalize tests.core.test_proposal_confirmed_benchmark -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/beta_proposal_05/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Confirmed CAD_PLAN bundle | validate + dry_run valid | **否** |
| 未选方案证据 | `unselected_candidate_evidence.json` | **否** |

### 9. 剩余风险

- 真实 CAD 落图与 created-handle readback 不在本父包范围。

---

## §45 `BETA-DRAWING-READ-01` — 只读 DWG entity summary

**日期**：2026-05-26
**父包**：后置主线「自动读图 / 空壳识别」

### 1. 开发包名

`BETA-DRAWING-READ-01` — 只读 ModelSpace / fixture 实体汇总（层、类型、bbox、handle 样本）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/drawing_analysis/dwg_read_only.py` | **新增** |
| `core/schemas/dwg_entity_summary.schema.json` | **新增** |
| `examples/drawing_read/sample_modelspace_entities.json` | **新增** |
| `scripts/run_dwg_entity_summary.py` | **新增** |
| `tests/core/test_dwg_read_only.py` | **新增** |
| `core/verification/fake_cad_driver.py` | `snapshot_modelspace()` |
| `docs/verification/beta_drawing_read_01_boundaries.md` | **新增** |

### 3. 关键设计说明

- 只读策略：`READ_ONLY_POLICY` 禁止 mutate/save/write；默认 fixture，可选 `--use-cad` 读活动 AutoCAD。
- `build_dwg_entity_summary` 聚合 `type_counts`、`layer_statistics`、`bbox_union`、`handles_sample`。
- 不解析任意 DWG 文件路径；不输出墙/门/柱语义（留给 READ-02）。

### 4. 新增/修改测试

- **404 tests OK**（+4）；`test_dwg_read_only.py` schema + 计数 + FakeCadDriver。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_dwg_read_only -v
& $py scripts\run_dwg_entity_summary.py
```

### 6. 是否运行真实 CAD

**否**（默认 fixture；`--use-cad` 未在本包验收中执行）

### 7. CAD 证据路径

`output/test_artifacts/drawing_read/beta_drawing_read_01/summary.json`（CLI 默认输出）

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Entity summary fixture | schema + layer/type counts | **否** |
| 只读策略 | `read_only: true` + policy constants | **否** |

### 9. 剩余风险

- 未做墙/门/柱语义提取（`BETA-DRAWING-READ-02`）。
- 真实大 DWG 全 ModelSpace 扫描性能与层过滤待后续 benchmark 覆盖。

---

## §46 `BETA-DRAWING-READ-02` — 几何特征候选提取

**日期**：2026-05-26
**父包**：后置主线「自动读图 / 空壳识别」

### 1. 开发包名

`BETA-DRAWING-READ-02` — 从规范化实体 + entity summary 启发式提取墙线段、门洞、柱、禁放区候选。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/drawing_analysis/geometry_candidates.py` | **新增** |
| `core/schemas/dwg_geometry_candidates.schema.json` | **新增** |
| `examples/drawing_read/sample_geometry_feature_fixture.json` | **新增** |
| `scripts/run_geometry_candidates.py` | **新增** |
| `tests/core/test_geometry_candidates.py` | **新增** |
| `docs/verification/beta_drawing_read_02_boundaries.md` | **新增** |

### 3. 关键设计说明

- 层名 / 块名启发式 + summary 层内 line 主导辅助；每项含 `confidence` 与 `detection_rule`。
- 输出 `dwg_geometry_candidates`；**不**生成 `SHELL_MODEL`，不驱动落 CAD。
- `read_geometry_candidates_from_fixture` 内部复用 READ-01 summary 作为 `entity_summary_ref`。

### 4. 新增/修改测试

- **407 tests OK**（+3）；fixture 断言 4 墙 + 1 门 + 1 柱 + 1 禁放区。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_geometry_candidates -v
& $py scripts\run_geometry_candidates.py
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/drawing_read/beta_drawing_read_02/candidates.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Geometry candidates fixture | schema + counts | **否** |
| 启发式提取 | layer/block heuristics only | **否** |

### 9. 剩余风险

- 置信度与人工确认点未机器化（`BETA-DRAWING-READ-03`）。
- 未确认候选不得进入 blank-shell 落图。

---

## §47 `BETA-DRAWING-READ-03` — Shell 候选置信度报告

**日期**：2026-05-26
**父包**：后置主线「自动读图 / 空壳识别」

### 1. 开发包名

`BETA-DRAWING-READ-03` — 从几何候选汇总置信度、结构化缺口与人工确认点，输出草案 shell。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/drawing_analysis/shell_candidate_report.py` | **新增** |
| `core/schemas/shell_candidate_confidence_report.schema.json` | **新增** |
| `examples/drawing_read/sample_geometry_walls_only_fixture.json` | **新增** |
| `scripts/run_shell_candidate_report.py` | **新增** |
| `tests/core/test_shell_candidate_report.py` | **新增** |
| `docs/verification/beta_drawing_read_03_boundaries.md` | **新增** |

### 3. 关键设计说明

- `confidence` 五维分数 + `shell_candidate_draft`（boundary / openings / obstacles / no_place）。
- `gaps` 含 `missing_entry_opening` 等 blocker；`human_confirmation_items` 含 `confirm_boundary_bbox` / `resolve_gap`。
- `ready_for_human_confirmation_file`：无 blocker 且 overall ≥ 0.65；**不**等同可落 CAD。

### 4. 新增/修改测试

- **410 tests OK**（+3）；完整 fixture ready=true；缺门洞 fixture blocker。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_shell_candidate_report -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/drawing_read/beta_drawing_read_03/report.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Confidence report complete fixture | schema + confidence keys | **否** |
| Blocker gap incomplete fixture | `missing_entry_opening` | **否** |

### 9. 剩余风险

- 人工确认文件 → `SHELL_MODEL` 回写未实现（`BETA-DRAWING-READ-04`）。

---

## §48 `BETA-DRAWING-READ-04` — 人工确认回写 SHELL_MODEL

**日期**：2026-05-26
**父包**：后置主线「自动读图 / 空壳识别」

### 1. 开发包名

`BETA-DRAWING-READ-04` — `shell_drawing_read_confirmation` 校验并合成可通过 `shell_loader` 的 `SHELL_MODEL`。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/drawing_analysis/shell_confirmation.py` | **新增** |
| `core/schemas/shell_drawing_read_confirmation.schema.json` | **新增** |
| `examples/drawing_read/sample_shell_drawing_read_confirmation.json` | **新增** |
| `scripts/apply_shell_drawing_read_confirmation.py` | **新增** |
| `tests/core/test_shell_confirmation.py` | **新增** |
| `docs/verification/beta_drawing_read_04_boundaries.md` | **新增** |

### 3. 关键设计说明

- `validate_confirmation_against_report`：必填 `confirmed_items` 覆盖 report `required` 项；`accept` 要求 `ready_for_human_confirmation_file`。
- `apply_shell_drawing_read_confirmation` → 临时 JSON → `load_manual_shell()`（bbox 内含校验）。
- `overrides.excluded_draft_ids` 可省略草案禁放区/障碍。

### 4. 新增/修改测试

- **414 tests OK**（+4）；`shell_model.schema.json` 校验通过。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_shell_confirmation -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/drawing_read/beta_drawing_read_04/shell_model.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| SHELL_MODEL from confirmation | shell_loader + schema | **否** |
| 缺必填确认项 | validation error | **否** |

### 9. 剩余风险

- 读图链路未 benchmark 化（`BETA-DRAWING-READ-05`）。
- SHELL_MODEL 进入 blank-shell 落图仍须单独 CAD 验证。

---

## §49 `BETA-DRAWING-READ-05` / 父包 `BETA-DRAWING-READ` 收口

**日期**：2026-05-26
**父包**：后置主线「自动读图 / 空壳识别」

### 1. 开发包名

`BETA-DRAWING-READ-05` — 读图链路 benchmark；父包 READ-01..05 收口。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/drawing_analysis/drawing_read_benchmark.py` | **新增** |
| `examples/benchmarks/drawing_read_benchmark.json` | **新增** |
| `scripts/run_drawing_read_benchmark.py` | **新增** |
| `tests/core/test_drawing_read_benchmark.py` | **新增** |
| `docs/verification/beta_drawing_read_05_boundaries.md` | **新增** |
| `docs/verification/beta_drawing_read_acceptance.md` | **新增** |

### 3. 关键设计说明

- 串联 READ-02..04：`geometry_candidates` → `confidence_report` → 可选 `SHELL_MODEL` export。
- 失败样本输出 `structured_blockers`（如 `missing_entry_opening`）；`evidence_state=blocked_expected_non_cad`。
- `expected_evidence_summary` 机器断言：2 pass + 1 blocked。

### 4. 新增/修改测试

- **416 tests OK**（+2）；benchmark 3/3 pass。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_drawing_read_benchmark -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/beta_drawing_read_05/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Full chain pass | benchmark_pass_non_cad + shell export | **否** |
| Walls-only blocked | structured_blockers + blocked_expected_non_cad | **否** |

### 9. 剩余风险

- 真实 DWG / 大图纸读图未纳入 benchmark。
- SHELL_MODEL 进入 blank-shell 仍须单独 CAD 验证。

---

## §50 `BETA-SCENE-01` — Office Scene Beta

**日期**：2026-05-26
**父包**：后置主线「场景 Agent Beta」

### 1. 开发包名

`BETA-SCENE-01` — office 场景 beta 偏好 + 统一 benchmark（对象 / 微场景 / 场景 / 失败）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/agents/scene_beta.py` | **新增** |
| `core/agents/office_scene_beta.py` | **新增** |
| `agents/scene_beta_manifest.json` | **新增** |
| `agents/office/preferences.json` | `scene_beta` + 扩展 object_preferences |
| `examples/benchmarks/office_scene_beta_benchmark.json` | **新增** |
| `scripts/run_office_scene_beta_benchmark.py` | **新增** |
| `tests/agents/test_scene_beta_office.py` | **新增** |

### 3. 关键设计说明

- Scene 层仅偏好与 benchmark 编排；复用 Core `object_spec` / `composition_spec` / `blank_shell`。
- 9 cases 含 `case_tier` 四类；blank-shell 断言 `preferences_scenario=office` 与 `straight_spine`。
- 失败样本保留 `blocked_expected_non_cad` 与结构化 `failure_category`。

### 4. 新增/修改测试

- **418 tests OK**（+2）；benchmark 9/9 pass；evidence 7 pass + 2 blocked。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.agents.test_scene_beta_office -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/beta_scene_01/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Office beta benchmark | benchmark_pass_non_cad + blocked_expected | **否** |
| Scene beta 偏好契约 | manifest + preference validation | **否** |

### 9. 剩余风险

- residential / restaurant beta 未覆盖（`BETA-SCENE-02/03`）。
- 场景解释模板增强在 `BETA-SCENE-04`。

---

## §51 `BETA-SCENE-02` — Residential Scene Beta

**日期**：2026-05-26
**父包**：后置主线「场景 Agent Beta」

### 1. 开发包名

`BETA-SCENE-02` — residential 卧室 / 餐厅 / 收纳组合 + blank-shell benchmark。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/agents/scene_beta.py` | 扩展 residential 校验 |
| `core/agents/residential_scene_beta.py` | **新增** |
| `agents/residential/preferences.json` | `scene_beta` + 对象偏好扩展 |
| `examples/benchmarks/residential_scene_beta_benchmark.json` | **新增** |
| `agents/scene_beta_manifest.json` | 增加 residential |
| `tests/agents/test_scene_beta_residential.py` | **新增** |

### 3. 关键设计说明

- `case_tier`：object / bedroom / dining / storage / blank_shell / failure。
- blank-shell 断言 `along_wall` 与 `preferences_scenario=residential`。
- 复用 Core `bedroom_bed_rug`、`dining_table_set` composition。

### 4. 新增/修改测试

- **420 tests OK**（+2）；benchmark 8/8 pass；7 pass + 1 blocked。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.agents.test_scene_beta_residential -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/beta_scene_02/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Residential beta benchmark | benchmark_pass_non_cad + blocked | **否** |

### 9. 剩余风险

- restaurant/commercial beta 未覆盖（`BETA-SCENE-03`）。

---

## §52 `BETA-SCENE-03` — Restaurant / Commercial Scene Beta

**日期**：2026-05-26
**父包**：后置主线「场景 Agent Beta」

### 1. 开发包名

`BETA-SCENE-03` — restaurant 入口 / 堂食桌椅 / 后场收纳 + blank-shell benchmark。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/agents/scene_beta.py` | 扩展 restaurant 校验 |
| `core/agents/restaurant_scene_beta.py` | **新增** |
| `agents/restaurant/preferences.json` | `scene_beta` |
| `examples/benchmarks/restaurant_scene_beta_benchmark.json` | **新增** |
| `agents/scene_beta_manifest.json` | 增加 restaurant |

### 3. 关键设计说明

- `case_tier`：object / entrance / seating / back_of_house / blank_shell / failure。
- blank-shell 断言 `l_spine`、`shell-restaurant-small-front`、`no_place_zone_count`。
- 入口组合复用 `entry_reception_clearance`；堂食复用 `dining_table_set`。

### 4. 新增/修改测试

- **422 tests OK**（+2）；benchmark 8/8 pass。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.agents.test_scene_beta_restaurant -v
```

### 6. 是否运行真实 CAD

**否**

### 7. CAD 证据路径

`output/test_artifacts/benchmarks/beta_scene_03/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Restaurant beta benchmark | benchmark_pass_non_cad + blocked | **否** |

### 9. 剩余风险

- 餐饮专用 composition 模板仍偏少（`BETA-SCENE-04` 解释模板）。

---

## Codex 深度全量安全复盘（非 PlanMD 开发包）

**日期**：2026-05-26
**性质**：Cursor 大改后的安全审计、Bug 筛查、维护性拆分与证据门禁加固；不是新的功能开发包。

### 1. 开发包名

无（Codex audit / hardening）。

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/benchmarks/runner.py` / `core/benchmarks/expectations.py` | 拆出 expected / evidence summary 比对；强制 case evidence triplet |
| `core/proposal_engine/confirmed_benchmark.py` | 输出并校验 `evidence_summary` |
| `core/verification/evidence_contract.py` / `evidence_vocabulary.py` | 拆出 evidence vocabulary |
| `core/project_samples/cad_check.py` | 修正 no-CAD / failure evidence vocabulary |
| `libraries/drawing_standards/codex_preview_beta.json` | 修正 `screenshot_role=not_applicable` |
| `core/composition_engine/preview.py` / `templates.py` | 拆出 SVG preview helper |
| `core/workflows/blank_shell_candidates.py` / `blank_shell_pipeline.py` | 拆出 candidate set 生成逻辑 |
| `tests/core/*` | 增补 evidence gate、项目样例、benchmark validation、CAD validation payload fixture 回归 |
| `CAD_AGENT_STATUS.md` / `CORE_STATUS.md` / `CAD_AGENT_CHANGELOG.md` / `CAD_AGENT_ISSUES.md` / `CORE_CONTEXT_BRIEF.md` | 同步复盘证据和风险记录 |

### 3. 关键设计说明

- benchmark pass 必须带机器可读 evidence triplet；summary 不匹配即失败。
- project sample / drawing standard 不允许临时发明 evidence 状态词。
- repo audit 的大文件 finding 用低风险职责拆分解决，保持原公开入口兼容。

### 4. 新增/修改测试

- 新增/扩展：benchmark expected evidence triplet、confirmed benchmark evidence summary、project sample CAD check failure vocabulary、drawing standard `screenshot_role`、benchmark validation、CAD validation payload fixture 拆分回归。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest discover -s tests -q
# 424 tests OK

& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
# 0 findings

& $py scripts\run_project_sample_benchmark.py
# pass, 2/2

& $py scripts\run_proposal_confirmed_benchmark.py
# pass, 2/2

& $py scripts\run_cad_beta_evidence_rollup.py
# pass, 5/5

& $py scripts\run_office_scene_beta_benchmark.py
& $py scripts\run_residential_scene_beta_benchmark.py
& $py scripts\run_restaurant_scene_beta_benchmark.py
# pass: 9/9, 8/8, 8/8
```

### 6. 是否运行真实 CAD

**否**。本轮只做 no-CAD / benchmark / fake-driver /静态与测试验证；未写入真实 DWG。

### 7. CAD 证据路径

- `output/test_artifacts/benchmarks/beta_project_sample_04/benchmark_summary.json`
- `output/test_artifacts/benchmarks/beta_proposal_05/benchmark_summary.json`
- `output/test_artifacts/cad_beta_evidence/beta_cad_block_05/`
- `output/test_artifacts/benchmarks/beta_scene_01/benchmark_summary.json`
- `output/test_artifacts/benchmarks/beta_scene_02/benchmark_summary.json`
- `output/test_artifacts/benchmarks/beta_scene_03/benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 全量单测和静态审计通过 | test / repo_audit | **否** |
| benchmark evidence gate 已强制 triplet + summary | benchmark_pass_non_cad / blocked_expected_non_cad | **否** |
| project sample / proposal / scene beta 验收脚本通过 | non-CAD benchmark | **否** |

### 9. 剩余风险

- 本轮不新增真实 CAD `geometry_verified` 结论。
- `render_preview.py --check` ready 只说明截图工具可用；截图仍是 `visual_aid_only`。
- 真实项目 DWG、正式图层、公司块库和 ActiveDocument guard 仍是后续风险。

---

## Codex 维护 1-3 包（证据止血、基线同步、路径安全）

**日期**：2026-05-26
**性质**：用户批准的“先止血、再加固”维护包；不是新的业务功能包。

### 1. 开发包名

`P0-EVIDENCE-TRUTH-FIX` + `BASELINE-SINGLE-SOURCE` + `PATH-AND-OUTPUT-SAFETY`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `scripts/run_project_sample_cad_check.py` | 新增 `--require-cad-verified`，deferred / failed 报告返回非 0 |
| `core/project_samples/protocol.py` / `loader.py` | manifest input path 必须留在样本目录内 |
| `core/benchmarks/runner.py` | benchmark `case_id` 安全 path segment；`output_root` 限制在 `output/` |
| `core/drawing_analysis/drawing_read_benchmark.py` | drawing-read `case_id` 与 `output_root` 边界加固 |
| `core/verification/cad_validation_runner.py` | `output_dir` 限制在 `output/`；清理 stale artifact 前验证派生产物边界 |
| `tests/core/*` | 增补 strict CAD evidence、manifest/path escape、output boundary 回归 |
| `CORE_CONTEXT_BRIEF.md` / `CORE_STATUS.md` / `CAD_AGENT_STATUS.md` / `CORE_RESTRUCTURE_PLAN.md` / `CAD_AGENT_CHANGELOG.md` / `CAD_AGENT_ISSUES.md` / `docs/verification/beta_project_sample_*` | 同步证据口径和风险记录 |

### 3. 关键设计说明

- `BETA-PROJECT-SAMPLE-05` 的 no-CAD 报告只能是 `deferred`，不能被当成真实 AutoCAD `geometry_verified`。
- 所有从 manifest、suite case、CLI output dir 派生的路径，必须先 resolve 并验证仍在预期边界内。
- benchmark/drawing-read case id 只允许作为单个 path segment，不允许 `../`、`\` 或绝对路径形态。

### 4. 新增/修改测试

- `test_cli_require_cad_verified_rejects_deferred_no_cad_report`
- `test_manifest_input_path_must_stay_inside_sample_directory`
- `test_scan_fails_when_manifest_input_escapes_sample_directory`
- benchmark / drawing-read unsafe `case_id` 与 output root 测试
- CAD validation output dir 边界测试

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_project_sample_cad_check tests.core.test_project_sample_loader tests.core.test_project_sample_protocol tests.core.test_benchmarks tests.core.test_drawing_read_benchmark tests.core.test_cad_validation_runner
# 48 tests OK

& $py -m unittest discover -s tests
# 432 tests OK

& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
# 0 findings

& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\codex-maintenance-fix-no-cad
# status=pass

& $py scripts\run_benchmark_suite.py examples\benchmarks\blank_shell_core_benchmark.json --output-root output\test_artifacts\benchmarks\codex_maintenance_fix_blank_shell
# 8/8 pass

& $py scripts\run_benchmark_suite.py examples\benchmarks\office_alpha_benchmark.json --output-root output\test_artifacts\benchmarks\codex_maintenance_fix_office_alpha
# 18/18 pass

& $py scripts\run_benchmark_suite.py examples\benchmarks\interior_delivery_benchmark.json --output-root output\test_artifacts\benchmarks\codex_maintenance_fix_interior_delivery
# 3/3 pass

& $py scripts\run_project_sample_cad_check.py --no-cad --require-cad-verified --output-dir output\validation_runs\codex-maintenance-project-sample-strict-no-cad
# expected exit 1; report status=deferred
```

### 6. 是否运行真实 CAD

**否**。本轮只做 no-CAD / fake-driver / benchmark / 单测验证；未写入真实 DWG。

### 7. CAD 证据路径

- `output\validation_runs\codex-maintenance-fix-no-cad\report.json`
- `output\validation_runs\codex-maintenance-project-sample-strict-no-cad\project_sample_cad_check_report.json`
- `output\test_artifacts\benchmarks\codex_maintenance_fix_blank_shell\benchmark_summary.json`
- `output\test_artifacts\benchmarks\codex_maintenance_fix_office_alpha\benchmark_summary.json`
- `output\test_artifacts\benchmarks\codex_maintenance_fix_interior_delivery\benchmark_summary.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 全量单测与 repo audit 通过 | test / repo_audit | **否** |
| no-CAD validation 通过 | deferred_cad_readback_required / non-CAD gate | **否** |
| project sample strict mode 正确拒绝 deferred | negative evidence gate | **否** |
| blank-shell / office / interior benchmark 通过 | benchmark_pass_non_cad / blocked_expected_non_cad / invalid_configuration | **否** |

### 9. 剩余风险

- 本轮不新增真实 CAD `geometry_verified` 结论。
- `BETA-PROJECT-SAMPLE-05` 真实样本 CAD readback 仍需用户 AutoCAD 会话单独运行。
- ActiveDocument guard、正式图层保护和真实项目 DWG 仍属于后续安全加固范围。

---

## Codex 维护 4-7 包（结构整理、路径公共化、Schema registry、文档主从治理）

**日期**：2026-05-26
**性质**：用户批准的 4-7 包结构整理和优化；承接 1-3 包“先止血、再加固”后的维护收口，不新增业务场景能力。

### 1. 开发包名

`STRUCTURE-GOVERNANCE-DRIFT-FIX` + `SHARED-PATH-SAFETY-CONSOLIDATION` + `SCHEMA-REGISTRY-CONSISTENCY` + `VALIDATION-GATE-CLEANUP`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/path_safety.py` | 新增公共路径安全 helper：project root、output root、safe path segment、relative boundary |
| `core/benchmarks/runner.py` / `core/drawing_analysis/drawing_read_benchmark.py` / `core/verification/cad_validation_runner.py` / `core/workflows/blank_shell_pipeline.py` / `core/capabilities/runners.py` | 替换分散路径判断，统一走 `core.path_safety` |
| `core/verification/block_alpha_beta_suite.py` / `drawing_standard_beta_suite.py` / `cad_beta_evidence_rollup.py` / `core/proposal_engine/*` | beta / proposal 输出目录和 case id 边界加固 |
| `core/project_samples/cad_check.py` | workflow output、CAD output 均限制在 project `output/` 下 |
| `scripts/run_composition_cad_check.py` | 在导入 / 连接 AutoCAD 前先验证 benchmark output root 和 output dir |
| `core/schemas/registry.py` | 登记所有 `core/schemas/*.schema.json` 并补齐模型识别 |
| `tests/core/*` / `tests/fixtures/invalid_models/*` | 增补路径越界、schema registry、文档治理和 non-CAD pipeline invalid 回归 |
| `CORE_CONTEXT_BRIEF.md` / `CORE_STATUS.md` / `CAD_AGENT_STATUS.md` / `CORE_RESTRUCTURE_PLAN.md` / `CAD_AGENT_CHANGELOG.md` / `CAD_AGENT_ISSUES.md` / 本文 | 同步 4-7 包证据、风险和唯一 PlanMD 口径 |

### 3. 关键设计说明

- 路径边界从各 runner 私有实现收敛为 `core.path_safety`，降低后续新增脚本漏检 output root / case id 的风险。
- 真实 CAD 相关脚本必须先验证路径，再连接 AutoCAD；参数非法时不应进入 COM 侧。
- `non_cad_pipeline` 对越界 workflow、越界 output、缺输入文件返回结构化 invalid / blocker，便于 benchmark 和交接机器判断。
- schema registry 以“文件存在即必须登记”为门禁，避免 schema 只停留在静态文档。
- handoff 只记录已完成包，不承载“下一包建议”或后置 Backlog 副表；优先级继续只以 `CORE_RESTRUCTURE_PLAN.md` 为准。

### 4. 新增/修改测试

- 路径边界：block alpha beta suite、drawing standard beta suite、CAD beta rollup、proposal confirmed benchmark、project sample CAD check、composition CAD check。
- schema registry：`test_every_core_schema_file_is_registered`，并补齐每个新增 schema 的 invalid fixture。
- 文档治理：`test_planmd_governance` 禁止 handoff / status / PlanMD 回流第二套计划短语。
- non-CAD pipeline：越界 output、越界 workflow input、缺 required input 返回 structured invalid。

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_block_alpha_beta_suite tests.core.test_drawing_standard_beta_suite tests.core.test_cad_beta_block_acceptance tests.core.test_proposal_confirmed_benchmark tests.core.test_schema_validation tests.core.test_planmd_governance tests.core.test_non_cad_pipeline tests.core.test_project_sample_cad_check tests.core.test_composition_cad_check
# 46 tests OK

& $py -m unittest discover -s tests
# 450 tests OK

& $py scripts\run_repo_audit.py --max-python-lines 500 --fail-on-findings
# 0 findings

& $py scripts\run_cad_validation.py --no-cad --output-dir output\validation_runs\codex-maintenance-4-7-no-cad
# status=pass
```

### 6. 是否运行真实 CAD

**否**。本轮只做 no-CAD / 单测 / repo audit / 文档治理验证；未连接 AutoCAD 写入真实 DWG。

### 7. CAD 证据路径

- `output\validation_runs\codex-maintenance-4-7-no-cad\report.json`
- 本轮 focused / full unittest 和 repo audit 为终端验证证据，无新增 `output\validation_runs` 真实 CAD 目录。

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 全量单测与 repo audit 通过 | test / repo_audit | **否** |
| 路径安全公共化与越界拒绝可回归 | structured invalid / negative path boundary tests | **否** |
| schema registry 覆盖所有 schema 文件 | schema validation tests | **否** |
| no-CAD validation 通过 | deferred_cad_readback_required / non-CAD gate | **否** |
| handoff / status 不再承载副计划 | doc governance tests | **否** |

### 9. 剩余风险

- 本轮不新增真实 CAD `geometry_verified` 结论。
- ActiveDocument guard、正式图层保护、公司块库和真实项目 DWG 仍属于后续真实 CAD 安全主线。
- 文档治理已有回归测试，但未来新增规划文档时仍需人工判断其是否又变成第二套计划。

---

## LOCAL-CAD-REGRESSION（本地 CAD 回归矩阵加固）

**日期**：2026-05-26
**性质**：进入下一开发阶段前的本地 CAD 校验层加固；新增统一矩阵入口，不新增真实 CAD 几何结论。

### 1. 开发包名

`LOCAL-CAD-REGRESSION`

### 2. 修改文件列表

| 路径 | 变更 |
| --- | --- |
| `core/verification/local_cad_regression.py` | 新增本地 CAD 回归矩阵聚合器，汇总 baseline CAD validation、project sample CAD check 和 composition CAD check |
| `scripts/run_local_cad_regression.py` | 新增 CLI wrapper，支持 `--no-cad` 和 `--require-cad-verified` |
| `tests/core/test_local_cad_regression.py` | 新增 no-CAD deferred、严格模式、composition 依赖跳过和 output 边界测试 |
| `CORE_CONTEXT_BRIEF.md` / `CORE_STATUS.md` / `CAD_AGENT_STATUS.md` / `CORE_RESTRUCTURE_PLAN.md` / `CAD_AGENT_CHANGELOG.md` / `CAD_AGENT_ISSUES.md` / 本文 | 同步本包证据、风险和唯一 PlanMD 口径 |

### 3. 关键设计说明

- `--no-cad` 模式默认安全：不连接 AutoCAD，不写真实 DWG，只把真实 CAD 子项记录为 deferred / non-CAD evidence。
- 真实 CAD 严格模式使用 `--require-cad-verified`；project sample 或 composition 任一子项不是 `geometry_verified`，矩阵顶层失败。
- composition CAD check 依赖 `interior_delivery_benchmark` 先成功产出 artifacts；前置失败时记录 `not_run` 和 `blocked_by`，不会继续写 CAD。
- 输出统一落在仓库 `output/` 下，并复用 `core.path_safety` 的 output dir 边界。

### 4. 新增/修改测试

- `test_no_cad_mode_builds_deferred_matrix_without_running_cad_only_checks`
- `test_real_cad_strict_mode_fails_when_project_sample_is_not_geometry_verified`
- `test_composition_cad_check_is_skipped_when_benchmark_artifacts_fail`
- `test_output_dir_must_stay_under_project_output`

### 5. 实际运行的命令和结果

```powershell
& $py -m unittest tests.core.test_local_cad_regression
# 4 tests OK

& $py scripts\run_local_cad_regression.py --no-cad --output-dir output\validation_runs\local-cad-regression-no-cad
# status=pass; step_count=3; deferred_case_count=2; geometry_verified_case_count=0

& $py -m unittest discover -s tests
# 456 tests OK
```

### 6. 是否运行真实 CAD

**否**。本轮只运行 no-CAD 矩阵和单测；未连接 AutoCAD 写入真实 DWG。

### 7. CAD 证据路径

- `output\validation_runs\local-cad-regression-no-cad\local_cad_regression_report.json`
- `output\validation_runs\local-cad-regression-no-cad\baseline_cad_validation\report.json`
- `output\validation_runs\local-cad-regression-no-cad\project_sample_cad\project_sample_cad_check_report.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 本地 CAD 回归矩阵 no-CAD 模式通过 | deferred_cad_readback_required / non-CAD gate | **否** |
| project sample CAD check 在 no-CAD 下输出 deferred | deferred_cad_readback_required | **否** |
| composition CAD check 在 no-CAD 下被明确延期 | deferred local matrix step | **否** |
| 严格模式会拒绝非 `geometry_verified` 子项 | negative evidence gate | **否** |

### 9. 剩余风险

- 本包不新增真实 CAD `geometry_verified` 结论。
- 真实 CAD 矩阵仍需在用户 AutoCAD 会话下单独运行，建议使用 `--require-cad-verified`。
- 该矩阵目前覆盖 baseline、project sample 和 composition 三条入口；公司块库、属性块、hatch 和真实项目 DWG 仍需后续扩样。

---

## 当前交接说明

本文只保留已经交付开发包的 9 项交接记录与 Codex 校验指引，不再承载当前队列、后置 Backlog 或未来小包表。后续优先级、Phase 顺序、退出门槛和后置主线唯一以 `CORE_RESTRUCTURE_PLAN.md` 为准；本文仅在对应小包真正交付后追加交接章节。

---

## Codex 校验快速指引

1. 读本文对应开发包章节（9 项是否齐全）；第 8 项须为「结论 + 证据类型 + geometry_verified」表。
2. 对照 `git diff` 与「修改文件列表」。
3. 按 [`evidence_gate_handoff_rules.md`](../verification/evidence_gate_handoff_rules.md) §4 打开机器路径（`report.json` / `benchmark_summary.json`）。
4. 禁止把截图、`dry_run_valid_plan_only` 或 `benchmark_pass_non_cad` 当成几何已验证。
5. 能力边界以 `CORE_CONTEXT_BRIEF.md`「不能声称的事」为准。

---

## V-PROOF-10-INTENT-INVENTORY / V-PROOF-11-INTENT-CAD-CASES

**日期**：2026-05-27 | **状态**：done | **真实 CAD**：部分（3 intent 标 deferred）

### 1–9. 摘要

- 包名：`V-PROOF-10` + `V-PROOF-11`
- 产物：`intent_lab_manifest.json`、`examples/plans/intent_lab/*.json`、`intent_lab.py`、`run_intent_lab_inventory.py`
- 测试：`tests/core/test_intent_lab.py`
- 真实 CAD：`draw_object` / `draw_symbol_glyph` / `insert_block_alpha` 可执行；`draw_annotation` / `modify_object` / `delete_object` deferred

### 10–12. 能力证明附加项

| capability_id | claim_level | ladder_level | 备注 |
| --- | --- | --- | --- |
| `intent.*`（6 行） | smoke/deferred（未改） | L1 | 最小 plan 已挂 manifest |

覆盖率：见 `cad_capability_coverage.json`（本轮未逐 intent 回写 verified）。

---

## LCAD-10.1-NEG-FIXTURES / CAD-VAL-01

**日期**：2026-05-27 | **状态**：done | **真实 CAD**：否（负向）；RCAD-01 见下

### 1–9. 摘要

- 负向：`examples/plans/negative/` + `run_negative_cad_plan_suite.py`；schema 增 `draw_symbol_glyph`、absolute `base_point`
- 几何门禁：`--geometry-gate` / `--require-geometry-pass` in `cad_validation_runner.py`
- 测试：`test_negative_cad_plans.py`、`test_cad_validation_geometry_gate.py`；**637 tests OK**

### 10–12.

| capability_id | claim_level | ladder_level | 备注 |
| --- | --- | --- | --- |
| *无* | — | — | 负向包未升 claim |

---

## RCAD-01-BASELINE-GEOMETRY（复验）

**日期**：2026-05-27 | **状态**：verified | **真实 CAD**：是

### 证据

- `output/validation_runs/rcad-01-baseline-geometry/report.json`
- `inspect_readback`：`readback_geometry_verified`；`block_alpha_readback`：geometry_verified
- 回写：`regression.baseline_cad_validation` → `verified`

### 10–12.

| capability_id | claim_level | ladder_level | 备注 |
| --- | --- | --- | --- |
| `regression.baseline_cad_validation` | verified | L1 | report_path 指向 rcad-01-baseline-geometry |

覆盖率：**0.4%**（1/252）。

---

## V-PROOF-04-STATUS-SYNC

**日期**：2026-05-27 | **状态**：done | **真实 CAD**：否

### 1–5. 摘要

- 包名：`V-PROOF-04-STATUS-SYNC`
- 修改：`CORE_STATUS.md`、`CAD_AGENT_STATUS.md`、`docs/verification/capability_proof_status_template.md`
- 设计：状态页固定三口径（工程 / 任务包 / CAD 证明覆盖率），禁止单用 Core 96% 暗示几何已证
- 测试：`tests/core/test_planmd_governance.py`（三口径节存在性）

### 6–9.

| 项 | 内容 |
| --- | --- |
| 6 真实 CAD | 否 |
| 7 证据 | `output/validation_runs/capability-lab/cad_capability_coverage.json` |
| 8 结论 | 文档治理；`dry_run_valid_plan_only` | 否 |
| 9 风险 | 数值须随 RCAD 回写后手工/sync 更新 |

### 10–12. 能力证明附加项

| capability_id | claim_level | ladder_level | 备注 |
| --- | --- | --- | --- |
| *无* | — | — | 本包未改 registry |

覆盖率：252 行，`cad_proof_coverage_rate=0%`（见 coverage JSON）。

---

## V-PROOF-05-HANDOFF-TEMPLATE

**日期**：2026-05-27 | **状态**：done | **真实 CAD**：否

### 1–5. 摘要

- 包名：`V-PROOF-05-HANDOFF-TEMPLATE`
- 修改：`CURSOR_PACKAGE_HANDOFFS.md` 模板、`evidence_gate_handoff_rules.md` §7、`capability_proof_handoff_template.md`、`docs/handoffs/README.md`
- 测试：同上 governance 测试

### 10–12. 能力证明附加项

| capability_id | claim_level | ladder_level | 备注 |
| --- | --- | --- | --- |
| *模板定义* | — | — | 后续 V-PROOF/RCAD 包必填 10~12 |

---

## V-PROOF-03-REGISTRY-LOADER

**日期**：2026-05-27
**状态**：done

### 1. 开发包名

`V-PROOF-03-REGISTRY-LOADER`

### 2. 修改文件列表

- `core/verification/capability_registry.py`（bundle + save）
- `core/verification/capability_registry_writeback.py`（新建）
- `scripts/run_capability_registry_writeback.py`（新建）
- `tests/core/test_capability_registry_writeback.py`（新建）

### 3. 关键设计说明

- 默认 **dry-run**；`--apply` 才写入 `cad_capability_registry.json`（写前 schema + claim 合同校验）。
- 仅从 geometry-verified 类报告升级 `claim_level`；拒绝 `deferred_cad_readback_required`。
- `--suggest-from-regression OUTPUT_DIR` 按 `local_cad_regression_manifest.json` 匹配 `regression.*` 行。

### 4. 测试

- `tests/core/test_capability_registry_writeback.py`（6）

### 5. 命令示例

```text
python scripts/run_capability_registry_writeback.py --capability-id regression.complex_cad_smoke --report output/test_artifacts/.../readback_report.json
python scripts/run_capability_registry_writeback.py --suggest-from-regression output/validation_runs/my-rcad-run
python scripts/run_capability_registry_writeback.py --batch writebacks.json --apply
python scripts/run_capability_coverage.py
```

### 6. 真实 CAD

否（单测用 synthetic report payload）

### 7. 证据

- 单测副本 registry 回写后 `verified_count=1`；仓库种子 JSON 未默认 `--apply`

### 8. 结论

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| Loader + 回写 API 可复跑 | 单测 synthetic readback payload | 测试内是，仓库种子否 |

### 9. 剩余风险

- 真实 RCAD 目录需用户会话下 `--suggest-from-regression` + `--apply` 后复跑覆盖率。

---

## V-PROOF-02-COVERAGE-REPORT

**日期**：2026-05-27
**状态**：done

### 1. 开发包名

`V-PROOF-02-COVERAGE-REPORT`

### 2. 修改文件列表

- `core/verification/capability_registry.py`（load + validate）
- `core/verification/capability_coverage.py`（新建）
- `scripts/run_capability_coverage.py`（新建）
- `tests/core/test_capability_coverage.py`（新建）
- `output/validation_runs/capability-lab/cad_capability_coverage.json`（生成物）
- `docs/planning/任务清单.md` §3.4、`CAD_AGENT_CHANGELOG.md`、`CAD_AGENT_STATUS.md`

### 3. 关键设计说明

- `cad_proof_coverage_rate = (verified + showcase) / total_count`；`smoke`/`deferred`/`none` 不计入 CAD 证明覆盖。
- `trend` 块为 LCAD-11.4 预留同一字段集；`evidence_path_audit` 检查 verified 行的 `report_path` 是否存在。

### 4. 测试

- `tests/core/test_capability_coverage.py`（4）

### 5. 命令

```text
python scripts/run_capability_coverage.py  → status=pass, total=252, cad_proof_coverage_rate=0.0
python -m unittest discover -s tests -q  → 623 OK
```

### 6. 真实 CAD

否

### 7. 证据路径

- `output/validation_runs/capability-lab/cad_capability_coverage.json`

### 8. 结论分类

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 覆盖率首算 0%（登记 252，verified 0） | `dry_run_valid_plan_only` | **否** |

### 9. 剩余风险

- RCAD 报告未回写 registry（V-PROOF-03）；覆盖率仍为 0% 直至 `claim_level` 升级。

---

## V-PROOF-01-REGISTRY-SEED

**日期**：2026-05-27
**状态**：done

### 1. 开发包名

`V-PROOF-01-REGISTRY-SEED`

### 2. 修改文件列表

- `core/verification/capability_registry_seed.py`（新建）
- `scripts/build_cad_capability_registry_seed.py`（新建）
- `examples/capability_proof/cad_capability_registry.json`（新建，252 行）
- `tests/core/test_cad_capability_registry_seed.py`（新建）
- `docs/planning/任务清单.md`、`CAD_AGENT_CHANGELOG.md`、`CAD_AGENT_STATUS.md`

### 3. 关键设计说明

- 种子由仓库现有清单推导：6 intent、ENTITY_CONTRACTS primitive、14 object×2、14 fitout catalog、19 composition、symbol、12 Core API、scene、90 benchmark case、6 regression manifest、block library、component roles 等。
- 全部为 `none`/`deferred`/`smoke`；**无** `verified`/`showcase`（待 V-PROOF-03 回写 RCAD）。

### 4. 新增/修改测试

- `tests/core/test_cad_capability_registry_seed.py`（4）

### 5. 命令与结果

```text
python scripts/build_cad_capability_registry_seed.py  → 252 capabilities, VALID SEED REGISTRY
python -m unittest discover -s tests -q  → 619 tests OK
```

### 6. 是否运行真实 CAD

否

### 7. 机器可读证据路径

- `examples/capability_proof/cad_capability_registry.json`

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| 252 行能力种子登记 | `dry_run_valid_plan_only`（结构 + 合同） | **否** |

### 9. 剩余风险

- 覆盖率脚本与 loader 未做（V-PROOF-02~03）；RCAD 报告尚未自动回写 registry 行。

---

## V-PROOF-00-REGISTRY-SCHEMA

**日期**：2026-05-27
**状态**：done（Phase V / §3 能力证明 V0）

### 1. 开发包名

`V-PROOF-00-REGISTRY-SCHEMA`

### 2. 修改文件列表

- `core/schemas/cad_capability_registry.schema.json`（新建）
- `core/schemas/registry.py`
- `core/verification/capability_registry_contract.py`（新建）
- `examples/capability_proof/minimal_cad_capability_registry.json`（新建）
- `tests/fixtures/invalid_models/cad_capability_registry.invalid.json`（新建）
- `tests/core/test_cad_capability_registry_schema.py`（新建）
- `tests/core/test_schema_validation.py`
- `docs/planning/任务清单.md`、`CAD_AGENT_CHANGELOG.md`、`CAD_AGENT_STATUS.md`

### 3. 关键设计说明

- 登记表与 `core/capabilities/`（Core API runner 目录）分离；Phase V 几何证明用 `cad_capability_registry.json`。
- JSON 使用仓库 subset validator；`claim_level` 附加规则在 `capability_registry_contract.py`（V-PROOF-03 loader 将复用）。
- 每行必填：`capability_id`、`display_name`、`category`、`claim_level`、`ladder_level`；`verified`/`showcase` 须 `evidence` + `report_path` + 几何 verified 类 `evidence_state`。

### 4. 新增/修改测试

- `tests/core/test_cad_capability_registry_schema.py`（6）
- `test_schema_validation` 增加 minimal 样例路径

### 5. 实际运行的命令和结果

```text
python -m unittest tests.core.test_cad_capability_registry_schema tests.core.test_schema_validation -q  → OK
python -m unittest discover -s tests -q  → 615 tests OK
```

### 6. 是否运行真实 CAD

否

### 7. 机器可读证据路径

- 样例：`examples/capability_proof/minimal_cad_capability_registry.json`
- Schema：`core/schemas/cad_capability_registry.schema.json`

### 8. 结论分类表

| 结论 | 证据类型 | geometry_verified |
| --- | --- | --- |
| CAD 能力登记表 JSON Schema + claim 合同 + 单测 | `dry_run_valid_plan_only`（结构契约） | **否** |

### 9. 剩余风险

- 首版 200+ 行种子登记未做（**V-PROOF-01**）。
- `run_capability_coverage.py` 与 loader 回写 API 未做（**V-PROOF-02~03**）。
- RCAD §5 已有报告尚未自动映射到 registry 行。

---

## 进度估算（交接时快照）

```text
表 C 真实 CAD 实力主指标：约 4.35%
CAD 证明覆盖率：约 47.10%（130/276）
总进度：约 94%
Core 底座开发进度：约 96%
Agent 多场景实现进度：约 88%
任务台账：§3 约 24/43 done；§4 约 42/55 done；§5 RCAD 22/29 verified
```

*百分比仅作节奏参考，以测试与 `output/validation_runs` 证据为准。*
