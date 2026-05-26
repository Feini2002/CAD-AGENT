# Evidence State 统一词表（R4-01）

最后更新：2026-05-26

> 机器可读定义以 `core/verification/evidence_contract.py` 为准。benchmark、CAD validation、verification report 必须通过该模块派生或校验 `evidence_state` / `geometry_accuracy` / `screenshot_role`，禁止在各处硬编码新词。

## evidence_state

| 值 | 典型来源 | 几何是否已验证 |
| --- | --- | --- |
| `benchmark_pass_non_cad` | benchmark pipeline ok + dry-run valid + verification unverified | 否 |
| `blocked_expected_non_cad` | benchmark 预期 blocked（failure case） | 否 |
| `invalid_configuration` | workflow / 输入非法 | 否 |
| `dry_run_valid_plan_only` | 仅 CAD_PLAN dry-run 通过 | 否 |
| `deferred_cad_readback_required` | 需补真实 CAD 或子报告未 verified | 否 |
| `readback_geometry_verified` | readback / block alpha `geometry_verified` | 是（created handles 回读） |
| `cad_capability_verified` | capability probe 通过 | 是（探针范围内） |

## geometry_accuracy

| 值 | 含义 |
| --- | --- |
| `not_verified_without_cad_readback` | 默认 non-CAD / 未回读 |
| `verified_by_cad_readback` | readback `geometry_verified` |
| `verified_by_cad_capability_readback` | capability probe verified |
| `not_verified_by_screenshot` | 截图不足以证明几何 |

## screenshot_role

| 值 | 含义 |
| --- | --- |
| `visual_aid_only` | 仅视觉辅助 |
| `not_applicable` | 无截图步骤 |

## Benchmark 映射入口

`classify_benchmark_pipeline_evidence(pipeline_status, dry_run_status, verification_status)` → 上述三字段 triplet。

## Failure benchmark 断言（R4-02）

| expected 字段 | 用途 |
| --- | --- |
| `pipeline_status` | failure case 必须为 `blocked` 或 `invalid`，与 `evidence_state` 配对 |
| `failure_category` | 结构化失败分类（须在 `BENCHMARK_FAILURE_CATEGORIES` 词表内） |
| `contains_blocked_reason` | `blocked_reasons` 列表须含给定子串 |
| `maximums` | 防止“少放对象仍 pass”，例如 `cad_plan_count: 0` |

配置期：`validate_failure_expected_contract()` 要求 failure `evidence_state` 必须带 `failure_category` 或 `contains_blocked_reason`。

运行期：`_compare_failure_outcome_guards()` 拒绝 `pipeline_status=ok` 但期望 blocked/invalid 的静默 pass。

## Suite 证据汇总（R4-03）

`run_benchmark_suite` 写入 `benchmark_summary.json`，其中 `evidence_summary` 包含：

| 字段 | 含义 |
| --- | --- |
| `case_count` | case 总数 |
| `evidence_state_counts` | 各 `evidence_state` 计数（须覆盖全部 case） |
| `benchmark_pass_non_cad_count` | non-CAD pass 样本数 |
| `blocked_expected_non_cad_count` | 预期 blocked failure 数 |
| `invalid_configuration_count` | 预期 invalid 配置 failure 数 |
| `readback_geometry_verified_count` | 真实几何 verified 数（当前三组 benchmark 均为 0） |
| `non_cad_only` | `readback_geometry_verified_count == 0` |

suite JSON 可选 `expected_evidence_summary`，跑完后与 actual 汇总逐字段比对。

## CAD validation 汇总（R4-04）

`run_cad_validation.py` 写入的 `report.json` 现含 `evidence_summary`（词表 rollup）与 `evidence_gate_failure`（若顶层 pass 与子报告证据矛盾）。

| 运行模式 | 顶层 `pass` 时要求 |
| --- | --- |
| `--no-cad` | `evidence_summary.non_cad_only=true`；不得含 readback / capability verified 计数 |
| 含 CAD（全量） | `inspect_readback` 与 `cad_capability_probe` 步骤 `pass` 且证据态分别为 `readback_geometry_verified`、`cad_capability_verified` |
| `--block-alpha-only` + CAD | `block_alpha_readback` 步骤证据为 `readback_geometry_verified` |

步骤 stdout 中未知 `evidence_state` 会使该步骤 `fail`，避免顶层 pass 掩盖。

## 门禁规则（摘要）

- 未知 `evidence_state`：benchmark case 配置校验失败；suite 汇总时 actual 含未知词会抛错。
- `benchmark_pass_non_cad` / `blocked_expected_non_cad` **不得**伴随 `geometry_accuracy=verified_by_cad_readback`。
- 顶层 CAD `pass` 仍须满足 `cad_validation_runner` 子报告硬门禁（`R4-04`）。

## 交接与审计（R4-05）

每包交接第 8 项、Codex 校验路径与禁止声称列表见 [`evidence_gate_handoff_rules.md`](evidence_gate_handoff_rules.md)。`docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` 顶部模板已扩展为必填三列表格。
