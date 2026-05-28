# 能力证明四进度口径（状态页固定模板）

最后更新：2026-05-28（普通回复 opt-in 进度口径 + 表 C）

> **Canonical 副本**：`CORE_STATUS.md`「四进度口径」与 `CAD_AGENT_STATUS.md`「当前进度估算」须与本模板字段一致；数值可随验收更新，**状态页完整表结构不得删改**。聊天交付默认不附进度表；只有用户明确点名完整状态、交接、审计、进度盘点、开发状态查询或表 C 专题时才展开本模板。用户说 **「真实 CAD 实力」/「推进表 C」** 时按 `docs/planning/任务清单.md` §0.1 执行（≠ 一键推进）。

## 1. 四口径对照（禁止混用）

| 口径 | 回答什么 | 主要证据 | 禁止替代 |
| --- | --- | --- | --- |
| **工程完备度（表 A）** | 模块、pytest、non-CAD benchmark 是否可跑 | `python -m unittest discover`、benchmark_summary、`run_cad_validation.py --no-cad` | **不能**代替 CAD 几何已证 |
| **任务清单执行（表 B）** | §3 / §4 / §5 任务包完成比例 | `docs/planning/任务清单.md` §0 | **不能**代替登记表 verified 或表 C |
| **RCAD 烟囱包（表 B §5 行）** | RCAD 包是否跑过 | §5 队列 `cad_status=verified` | **不能**暗示「已能画准施工图」 |
| **CAD 证明覆盖率** | `cad_capability_registry` 中 `verified` / `showcase` 占比 | `cad_capability_coverage.json` → `cad_proof_coverage_percent` | **不能**用 Core 96% 暗示 |
| **真实 CAD 实力（表 C）** | 对外能力上限（Ladder 加权 + L3+ + showcase 门） | 同上 → `cad_strength_headline_percent` 及子指标 | **不能**用 RCAD 烟囱 % 代替 |

另：**展示等级 Ladder**（L0~L5）为定性上限；`highest_proven_ladder_level` 来自登记表已证行。

## 2. 完整展开表格骨架（复制到状态页时替换「当前值」列）

### 表 A — 工程完备度

| 指标 | 当前值 | 说明 |
| --- | --- | --- |
| 总进度 | （填写） | 默认 Core×70% + Agent×30% |
| Core 底座开发进度 | （填写） | 工程完备度；含 schema、runner、验证门禁 |
| Agent 多场景实现进度 | （填写） | 场景壳层 / Beta / 产品化节奏 |

### 表 B — 任务清单三指令

| 指令 | 板块 | 当前值 |
| --- | --- | --- |
| 能力证明 | §3 `V-PROOF` | （填写，如 24/43） |
| 一键推进 | §4 代码轨 | （填写） |
| RCAD 烟囱包 | §5 `RCAD` | （填写；**≠ 表 C**） |

### 表 C — 真实 CAD 实力（`run_capability_coverage.py`）

| 指标 | 当前值 | JSON 字段 |
| --- | --- | --- |
| **真实 CAD 实力（主指标）** | （填写） | `cad_strength_headline_percent`（= min 指数、L3+、showcase） |
| CAD 证明覆盖率 | （填写） | `cad_proof_coverage_percent` |
| CAD 实力指数（Ladder 加权） | （填写） | `cad_strength_index_percent` |
| 场景片段实力（L3+ verified） | （填写） | `scene_fragment_strength_percent` |
| 展示就绪度（showcase） | （填写） | `showcase_readiness_percent` |
| 最高已证 Ladder | （填写） | `highest_proven_ladder_level` |

**主指标为 0% 时**：若 `showcase_count=0`，主指标按设计为 0；交付须**同时**报实力指数与 L3+ 子指标，不得只报 RCAD 烟囱完成度。

### CAD 证明覆盖率（登记表明细）

| 指标 | 当前值 | 复跑命令 |
| --- | --- | --- |
| `registry_path` | `examples/capability_proof/cad_capability_registry.json` | — |
| `total_count` | （填写） | `scripts/run_capability_coverage.py` |
| `verified_count` | （填写） | 同上 |
| `showcase_count` | （填写） | 同上 |
| `cad_proof_coverage_rate` | （填写，%） | 同上 |
| `smoke` / `deferred` / `none` | （可选分列） | 见 coverage JSON `by_claim_level` |

### 展示等级 Ladder（定性）

| 指标 | 当前值 |
| --- | --- |
| 当前最高已证 Ladder | （填写，如 L3） |
| 项目切片证据（可选） | （如 L4 边缘 rollup；不自动抬高主指标） |
| 是否声称 L5 / 任意施工图 | **否**（除非 registry + showcase 已更新） |

## 3. 禁止声称（状态页与交付必须遵守）

- **禁止**只写「Core 底座约 96%」或「RCAD 烟囱约 70%」而不写 **表 C**；前者不等于能画准施工图。
- **禁止**用 `run_cad_validation.py` 顶层 pass、RCAD 单项通过、或 benchmark `pipeline_status=ok` 代替 `cad_capability_registry` 行级 `claim_level=verified`。
- **禁止**把 `smoke` / `deferred` 登记行计入 CAD 证明覆盖率；仅 `verified` + `showcase` 计入。
- **禁止**把 primitive 矩形 smoke、守卫链 strict pass 或 rollup 占位几何说成「全库 / 全项目 geometry_verified」。
- **禁止**在 `showcase_count=0` 时仅用表 C 主指标 0% 声称「完全不能画图」而不报 `cad_strength_index_percent` / `scene_fragment_strength_percent` 子指标。

## 4. RCAD 回写后必做（与 V-PROOF-03 衔接）

1. `scripts/run_capability_registry_writeback.py`（`--apply`）更新登记表行。  
2. `scripts/run_capability_coverage.py` 复跑覆盖率（含 `cad_strength`）。  
3. 同步更新 `CORE_STATUS.md`、`CAD_AGENT_STATUS.md` 本节数值与 `docs/planning/任务清单.md` §0。

## 5. 相关路径

| 类型 | 路径 |
| --- | --- |
| 登记表 | `examples/capability_proof/cad_capability_registry.json` |
| 覆盖率 + 实力指数 | `output/validation_runs/capability-lab/cad_capability_coverage.json` |
| 回写 CLI | `scripts/run_capability_registry_writeback.py` |
| 架构说明 | `docs/planning/capability-proof-architecture.md` |
| 交接扩展模板 | `docs/handoffs/CURSOR_PACKAGE_HANDOFFS.md` §「能力证明包附加项」 |
