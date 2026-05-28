# V-PROOF-72：Nightly Capability Lab 入口

最后更新：2026-05-28

> 机器入口：`core/verification/capability_lab.py`、`scripts/run_capability_lab.py`
> Tier 清单：`examples/capability_proof/nightly_lab_tier_manifest.json`
> CI / 手动剧本：`docs/runbooks/nightly_capability_lab.md`

## 登记行（2）

| capability_id | 说明 |
| --- | --- |
| `lab.nightly.rollup` | 顶层 `capability_lab_report.json` |
| `lab.nightly.tier_l1` | 默认 nightly **L1** no-CAD 栈 |

全部 `claim_level=smoke`、`ladder_level=L0`。

## 退出条件

- `run_capability_lab --tier L1` 产出 `capability_lab_report.json`，`status=pass`
- L1 含 6 步：self_check、negative plan、local regression no-CAD、cad validation no-CAD（`--environment-optional`）、coverage、project protocol
- regression / validation 在 no-CAD 下允许 `accept_mode=no_cad_lab`（deferred 预期，见 manifest）
- schema 校验通过；2 行 registry smoke；2/2 writeback

## Tier 口径

| Tier | 用途 | 真实 CAD |
| --- | --- | --- |
| **L0** | 仅 coverage（快速 smoke） | 否 |
| **L1** | 默认 nightly / CI no-CAD 栈 | 否（deferred 预期） |

真实 CAD strict 补验仍走 §5 RCAD 队列，**不**并入 L1 nightly 默认路径。

## 不得声称

- 不得把 L1 pass 升为 `verified` / `showcase` 或抬高表 C 主指标。
- 不得把 no-CAD deferred / dry-run pass 说成 `geometry_verified`。
- 表 C 仍以 `output/validation_runs/capability-lab/cad_capability_coverage.json` 为准。

## 复跑

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_capability_lab.py --tier L1
& $py scripts\run_vproof_72_nightly_lab_sync.py
```
