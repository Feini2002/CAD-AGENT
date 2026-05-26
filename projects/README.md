# Projects

真实或**脱敏样例**项目放在 `projects/`。项目资料不得写入通用 `core/` 规则或 `agents/` 实现。

## 用途

- 存放可复现的**项目级输入**（`SHELL_MODEL`、brief、上下文等）与**预期说明**。
- 为 benchmark、workflow 回归与可选真实 CAD 验证提供**隔离目录**。
- 与 `examples/` 区分：`examples/` 是通用最小样例；`projects/` 是端到端项目样本包。

## 目录结构

每个样本一个子目录：

```text
projects/<sample_id>/
  README.md                 # 必需：人类可读说明（固定章节，见下）
  sample.manifest.json      # 必需：机器可读清单（schema: project_sample_manifest）
  input/                    # 必需：结构化输入（JSON），不提交原始 DWG
    shell.manual.json       # 示例：SHELL_MODEL
  expected/                 # 必需：非 CAD 预期
    expected_notes.md       # 必需
  output/                   # 可选：本地生成物（默认不提交大产物）
  source/                   # 可选：仅当用户明确批准；脱敏样本默认为空或不含 DWG
```

扫描入口：`core/project_samples/protocol.py`、`scripts/run_project_sample_protocol_scan.py`。

## 脱敏要求

| 规则 | 说明 |
| --- | --- |
| `deidentified: true` | manifest 必须声明已脱敏 |
| 禁止提交 DWG/DXF | 协议扫描拒绝 `.dwg` / `.dxf` / `.bak` |
| 无客户/地址/电话 | README 与 JSON 不得含可识别隐私 |
| 尺寸可保留 | 空壳 bbox、洞口、柱网等业务几何可用抽象 ID |
| 真实 CAD | 仅在用户会话 + `CODEX_PREVIEW` 下可选执行，不覆盖原 DWG |

## 可提交字段

`sample.manifest.json`（`version: "0.1"`）必填字段：

| 字段 | 说明 |
| --- | --- |
| `sample_id` | 与目录名一致 |
| `display_name` | 简短标题 |
| `domain` | 与 `CAD_PLAN` domain 枚举一致 |
| `deidentified` | 必须为 `true` 方可进入公共仓库 |
| `cad_policy` | `preview_layer_only` / `allow_formal_layers` / `allow_save_dwg` |
| `input_files[]` | `role`、`path`（相对样本根）、`schema` |
| `expected_artifacts[]` | 管道应能产出的模型/报告类型 |
| `evidence_claim` | `non_cad_pipeline_only` 或 `non_cad_with_optional_cad_preview` |

`input_files[].role` 允许：`shell_model`、`project_model`、`design_brief`、`cad_context`、`drawing_model`。

## 禁止事项

- 不要把公司块库、正式图层定义或场景算法放进 `projects/`。
- 不要提交未脱敏原始图纸、合同、报价单。
- 不要把 `geometry_verified` 写进 `expected_notes.md`（除非后续包有真实 readback 证据路径且单独说明）。
- 不要用 `projects/` 替代 `core/` 测试 fixture（单元测试优先 `tests/fixtures`、`examples/`）。

## 证据声称边界

| 证据 | 可声称 | 不可声称 |
| --- | --- | --- |
| 协议扫描 `pass` | 目录与 manifest 符合脱敏样本协议 | `geometry_verified` |
| `evidence_claim=non_cad_pipeline_only` | pipeline / dry-run / benchmark non-CAD | 真实 CAD 已全面准确 |
| 可选 CAD preview（后续包） | 受控 `CODEX_PREVIEW` + created-handle readback | 任意 DWG 自动准确 |

## 参考样本

- `sample_blank_shell/` — 手工 `SHELL_MODEL`，blank-shell 非 CAD 回归（`BETA-PROJECT-SAMPLE-01` 基线）。
- `sample_blank_shell_too_small/` — 过小 shell，用于 `project_sample_benchmark` 的 `blocked_expected_non_cad` 失败断言（`BETA-PROJECT-SAMPLE-04`）。
