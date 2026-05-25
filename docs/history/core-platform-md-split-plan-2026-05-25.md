# 主平台 Markdown 精细化拆分归档记录

> 已归档：本文记录 2026-05-25 主平台 Markdown 精细化拆分的执行过程，不再作为当前计划入口。当前唯一 PlanMD / 主计划是根目录 `CORE_RESTRUCTURE_PLAN.md`；Phase 执行剧本入口见 `docs/planning/README.md`。

> 历史说明：下文保留当时的实施计划格式和复核命令，仅用于追溯，不再要求后续 agent 按本文执行。

**Goal:** 将当前根目录主平台 Markdown 拆成短入口、状态页、路线页、总控索引和分 Phase 执行剧本，下一轮先完成文档结构治理，不修改 Python、CAD 执行、测试或业务代码。

**Architecture:** 根目录继续承担“快速恢复和当前口径”的职责，`CORE_RESTRUCTURE_PLAN.md` 收缩为主计划索引；长篇 Phase W/X/Y/Z 执行细节迁入 `docs/planning/`。拆分采用先复制成新文档、再缩短根目录引用、最后自查引用的方式，避免丢失历史依据。

**Tech Stack:** Markdown、PowerShell、`rg`、`git diff`、现有 CAD-MCP Python 验证命令；本计划不新增依赖，不运行会修改 CAD 图纸的命令。

---

## 当前判断

当前根目录 Markdown 已经能恢复上下文，但主平台文档开始过重：

| 文件 | 当前职责 | 拆分压力 |
| --- | --- | --- |
| `CORE_RESTRUCTURE_PLAN.md` | 当时的主计划，含 Phase W/X/Y/Z、证据边界、执行矩阵和完成判定 | 约 38 KB，既是总控索引又是执行剧本，后续执行容易滚动过多上下文 |
| `README.md` | 用户入口、换机清单、常用命令、当前状态 | 约 22 KB，入口说明和换机手册混在同一层 |
| `CORE_CONTEXT_BRIEF.md` | 日常短上下文入口 | 内容仍可用，但应只指向拆分后的详细文件 |
| `CORE_STATUS.md` | 能力矩阵和成熟度 | 职责清晰，保持根目录 |
| `CAD_AGENT_STATUS.md` | 当前进展页 | 职责清晰，保持根目录 |
| `CAD_AGENT_CHANGELOG.md` / `CAD_AGENT_ISSUES.md` | 历史流水和问题教训 | 体量大但用途明确，不在本轮拆分 |
| `SHELL_LAYOUT_FOUNDATION_DESIGN.md` | 空壳布局设计说明 | 是设计文档，暂不迁移；后续可归入 `docs/architecture/` |

本轮用户明确要求“先不改代码，进行计划的构建”。因此下一轮执行本计划时，允许修改 Markdown 和文档目录，不允许修改 `core/`、`scripts/`、`drivers/`、`tests/`、`agents/` 的代码或数据文件，除非用户重新授权。

## 目标文档结构

### 根目录保留

| 文件 | 目标职责 | 目标体量 |
| --- | --- | --- |
| `README.md` | 首次入口、仓库定位、快速恢复、常用命令和换机入口 | 保持可扫读；换机清单可在后续单独迁出 |
| `AGENTS.md` | Codex 强制行为规则 | 不承载阶段计划 |
| `CORE_CONTEXT_BRIEF.md` | 每轮默认短入口 | 只写当前结论、按需展开表和验证命令入口 |
| `CORE_RESTRUCTURE_PLAN.md` | 主计划索引 | 收缩为 Phase 总览、当前优先级、拆分文档链接和完成判定 |
| `CORE_STATUS.md` | 能力成熟度矩阵 | 保持现状，按阶段同步 |
| `CORE_ROADMAP.md` | 高层路线图 | 保持现状，按方向同步 |
| `CAD_AGENT_STATUS.md` | 当前进展页 | 保持现状，按阶段同步 |
| `CAD_AGENT_RULES.md` | 长期规则 | 保持现状 |
| `CAD_AGENT_CHANGELOG.md` | 历史流水 | 保持现状，只追加不迁移 |
| `CAD_AGENT_ISSUES.md` | 问题与教训库 | 保持现状，只追加不迁移 |

### 新增或承接到 `docs/planning/`

| 文件 | 来源 | 目标职责 |
| --- | --- | --- |
| `docs/planning/README.md` | 本轮已创建 | 规划类文档索引 |
| `docs/planning/core-platform-md-split-plan.md` | 本轮已创建 | 本拆分计划 |
| `docs/planning/phase-w-cad-validation-plan.md` | `CORE_RESTRUCTURE_PLAN.md` Phase W | 真实 CAD 回读闭环执行剧本 |
| `docs/planning/phase-x-scene-agent-alpha-plan.md` | `CORE_RESTRUCTURE_PLAN.md` Phase X | 场景 Agent Alpha 验收执行剧本 |
| `docs/planning/phase-y-blank-shell-hardening-plan.md` | `CORE_RESTRUCTURE_PLAN.md` Phase Y | blank-shell pipeline 硬化执行剧本 |
| `docs/planning/phase-z-doc-governance-plan.md` | `CORE_RESTRUCTURE_PLAN.md` Phase Z | 文档治理、回归基线和状态同步执行剧本 |

### 暂不迁移

| 文件 | 原因 |
| --- | --- |
| `CAD_AGENT_AUTONOMOUS_VALIDATION.md` | 真实 CAD 验证手册已经独立，Phase W 文档只链接它 |
| `CAD_AGENT_BLOCKER_PLAYBOOK.md` | 卡壳流程是长期规则型文档，保持根目录入口 |
| `SHELL_LAYOUT_FOUNDATION_DESIGN.md` | 仍是设计依据，待 Phase Y 结束后再评估是否迁到 `docs/architecture/` |
| `SHELL_LAYOUT_TIME_ESTIMATE.md` | 已标注为历史估算，暂不影响执行 |
| `CAD_AGENT_DECISIONS.md` | 架构决策记录，暂不拆 |

## 拆分原则

- 先复制成新文档，再缩短根目录正文；不直接删除历史依据。
- 每个 Phase 文档必须能被单独打开执行，包含目标、边界、文件范围、验证命令、退出标准和状态同步要求。
- `CORE_RESTRUCTURE_PLAN.md` 不再写长表格细节，只保留到各 Phase 文档的链接和当前优先级。
- 所有状态口径仍以 `CORE_CONTEXT_BRIEF.md`、`CORE_STATUS.md`、`CAD_AGENT_STATUS.md` 三者同步为准。
- 真实 CAD 几何结论不得因文档迁移被放大；baseline 通过仍只覆盖已验证的 baseline plan 和能力探针。
- 文档迁移期间不运行会写入 CAD 的命令，不保存 DWG，不修改正式图层。

## File Structure

本计划执行时预计只创建或修改以下 Markdown 文件：

- Create: `docs/planning/phase-w-cad-validation-plan.md`
- Create: `docs/planning/phase-x-scene-agent-alpha-plan.md`
- Create: `docs/planning/phase-y-blank-shell-hardening-plan.md`
- Create: `docs/planning/phase-z-doc-governance-plan.md`
- Modify: `docs/planning/README.md`
- Modify: `CORE_RESTRUCTURE_PLAN.md`
- Modify: `CORE_CONTEXT_BRIEF.md`
- Modify: `CAD_AGENT_STATUS.md`
- Modify: `CAD_AGENT_CHANGELOG.md`
- Optional Modify: `README.md`，仅在需要新增 planning 入口时修改

不得修改：

- `core/**`
- `scripts/**`
- `drivers/**`
- `tests/**`
- `agents/**`
- `libraries/**`
- `projects/**`
- `examples/**`
- `schemas/**`

## Task 1: 建立 Phase 文档骨架

**Files:**
- Create: `docs/planning/phase-w-cad-validation-plan.md`
- Create: `docs/planning/phase-x-scene-agent-alpha-plan.md`
- Create: `docs/planning/phase-y-blank-shell-hardening-plan.md`
- Create: `docs/planning/phase-z-doc-governance-plan.md`
- Modify: `docs/planning/README.md`

- [x] **Step 1: 创建 Phase W 文档骨架**

写入 `docs/planning/phase-w-cad-validation-plan.md`：

```markdown
# Phase W CAD Validation Plan

状态：由 `CORE_RESTRUCTURE_PLAN.md` 拆分而来
最后同步：2026-05-25

## 目标

把 `CODEX_PREVIEW` 落图、截图、created handles、实体回读和 `VERIFICATION_REPORT.geometry_verified` 证据链作为真实 CAD 验证闭环。

## 当前证据边界

- baseline `examples\plans\draw_test_cabinet.json` 已在真实 CAD 中通过。
- `cad_capability_probe` 已覆盖矩形、独立直线、圆、弧、闭合多段线、文字和标注。
- 该结论不扩大到真实项目图纸、块库、块插入或任意 CAD_PLAN。

## 执行入口

- `CAD_AGENT_AUTONOMOUS_VALIDATION.md`
- `scripts/run_cad_validation.py`
- `core/verification/inspect_dwg.py`
- `core/verification/verification_report.py`

## 安全边界

- 只写入 `CODEX_PREVIEW`。
- 不保存当前 DWG。
- 不覆盖原始 DWG。
- 不删除实体。
- 不修改正式图层，除非用户明确批准。

## 待迁移内容

从 `CORE_RESTRUCTURE_PLAN.md` 迁移 Phase W 的 W.0 到 W.12 全部小节。
```

- [x] **Step 2: 创建 Phase X 文档骨架**

写入 `docs/planning/phase-x-scene-agent-alpha-plan.md`：

```markdown
# Phase X Scene Agent Alpha Plan

状态：由 `CORE_RESTRUCTURE_PLAN.md` 拆分而来
最后同步：2026-05-25

## 目标

证明场景 Agent 是轻量复用层，而不是复制 Core 算法。至少 3 个场景复用同一 `workflow.blank_shell_pipeline`，并通过 preferences 改变候选排序、对象组合或约束解释。

## 文件范围

- `agents/commercial_fitout/preferences.json`
- `agents/residential/preferences.json`
- `agents/office/preferences.json`
- `agents/restaurant/preferences.json`
- `agents/SCENE_AGENT_RULES.md`
- `tests/agents/test_scene_preferences.py`
- `tests/agents/test_blank_shell_scene_preferences.py`
- `examples/benchmarks/blank_shell_core_benchmark.json`

## 待迁移内容

从 `CORE_RESTRUCTURE_PLAN.md` 迁移 Phase X 的当前前置事实、文件范围、执行计划、验证命令和退出标准。
```

- [x] **Step 3: 创建 Phase Y 文档骨架**

写入 `docs/planning/phase-y-blank-shell-hardening-plan.md`：

```markdown
# Phase Y Blank Shell Hardening Plan

状态：由 `CORE_RESTRUCTURE_PLAN.md` 拆分而来
最后同步：2026-05-25

## 目标

把当前能跑通的 blank-shell pipeline 推进成更可靠的非 CAD 布局实验台，重点补多候选、失败基准、复杂几何和真实样本。

## 文件范围

- `core/workflows/blank_shell_pipeline.py`
- `core/layout_engine/path_generation.py`
- `core/layout_engine/zone_splitter.py`
- `core/layout_engine/placement.py`
- `core/proposal_engine/proposal_comparison.py`
- `examples/workflows/*`
- `examples/shell_models/*`
- `projects/*/expected/*`
- `tests/core/test_blank_shell_pipeline.py`
- `tests/core/test_benchmarks.py`

## 待迁移内容

从 `CORE_RESTRUCTURE_PLAN.md` 迁移 Phase Y 的当前前置事实、文件范围、执行计划、验证命令和退出标准。
```

- [x] **Step 4: 创建 Phase Z 文档骨架**

写入 `docs/planning/phase-z-doc-governance-plan.md`：

```markdown
# Phase Z Documentation Governance Plan

状态：由 `CORE_RESTRUCTURE_PLAN.md` 拆分而来
最后同步：2026-05-25

## 目标

固定状态文档、验证命令、问题记录和审计规则，避免后续 Codex 重新考古或读到过期阶段口径。

## 文件范围

- `CORE_CONTEXT_BRIEF.md`
- `CORE_RESTRUCTURE_PLAN.md`
- `CORE_STATUS.md`
- `CAD_AGENT_STATUS.md`
- `CAD_AGENT_CHANGELOG.md`
- `CAD_AGENT_ISSUES.md`
- `README.md`

## 待迁移内容

从 `CORE_RESTRUCTURE_PLAN.md` 迁移 Phase Z 的执行计划、文档自查命令和固定非 CAD 回归命令。
```

- [x] **Step 5: 更新 planning 索引**

将 `docs/planning/README.md` 中的表格扩展为：

```markdown
| 文档 | 用途 |
| --- | --- |
| `core-platform-md-split-plan.md` | 主平台 Markdown 精细化拆分计划 |
| `phase-w-cad-validation-plan.md` | Phase W 真实 CAD 回读闭环执行剧本 |
| `phase-x-scene-agent-alpha-plan.md` | Phase X 场景 Agent Alpha 验收执行剧本 |
| `phase-y-blank-shell-hardening-plan.md` | Phase Y 空壳布局硬化执行剧本 |
| `phase-z-doc-governance-plan.md` | Phase Z 文档治理与回归基线执行剧本 |
```

## Task 2: 迁移 Phase 细节

**Files:**
- Modify: `docs/planning/phase-w-cad-validation-plan.md`
- Modify: `docs/planning/phase-x-scene-agent-alpha-plan.md`
- Modify: `docs/planning/phase-y-blank-shell-hardening-plan.md`
- Modify: `docs/planning/phase-z-doc-governance-plan.md`

- [x] **Step 1: 迁移 Phase W**

从 `CORE_RESTRUCTURE_PLAN.md` 复制以下完整区段到 `docs/planning/phase-w-cad-validation-plan.md`：

```text
## Phase W：真实 CAD 回读闭环补验
### W.0 已完成内容聚合与证据边界
### W.1 本阶段验证范围
### W.2 执行前条件与停止点
### W.3 输出目录与证据清单
### W.4 执行顺序总表
### W.5 CAD 待检查矩阵
### W.6 分步执行清单
### W.7 失败分类与自动处理策略
### W.8 `geometry_verified` 升级门槛
### W.9 停止问用户的条件
### W.10 继续自动修的条件
### W.11 退出标准
### W.12 完成后同步文档
```

- [x] **Step 2: 迁移 Phase X**

从 `CORE_RESTRUCTURE_PLAN.md` 复制以下完整区段到 `docs/planning/phase-x-scene-agent-alpha-plan.md`：

```text
## Phase X：场景 Agent 接入与 Alpha 验收
### 当前前置事实
### 文件范围
### 执行计划
### 验证命令
### 退出标准
```

- [x] **Step 3: 迁移 Phase Y**

从 `CORE_RESTRUCTURE_PLAN.md` 复制以下完整区段到 `docs/planning/phase-y-blank-shell-hardening-plan.md`：

```text
## Phase Y：空壳布局硬化与真实样本扩展
### 当前前置事实
### 文件范围
### 执行计划
### 验证命令
### 退出标准
```

- [x] **Step 4: 迁移 Phase Z**

从 `CORE_RESTRUCTURE_PLAN.md` 复制以下完整区段到 `docs/planning/phase-z-doc-governance-plan.md`：

```text
## Phase Z：长期维护、文档治理和回归基线
### 执行计划
### 文档自查命令
### 固定非 CAD 回归命令
```

- [x] **Step 5: 每个新文档补统一页脚**

每个 Phase 文档末尾追加：

```markdown
## 状态同步要求

完成或调整本 Phase 后，同步：

- `CORE_CONTEXT_BRIEF.md`
- `CORE_STATUS.md`
- `CAD_AGENT_STATUS.md`
- `CAD_AGENT_CHANGELOG.md`

只有出现失败、回归、CAD 环境问题或验证教训时，才同步 `CAD_AGENT_ISSUES.md`。
```

## Task 3: 收缩主计划为索引

**Files:**
- Modify: `CORE_RESTRUCTURE_PLAN.md`

- [x] **Step 1: 保留主计划头部**

保留 `CORE_RESTRUCTURE_PLAN.md` 的以下区段：

```text
# CAD Agent Core 下一阶段开发执行计划
状态
最后更新
面向后续 Codex / agentic worker 的说明
## 0. 当前复盘结论
## 1. 已落地能力与证据边界
## 2. 文档职责分层
## 3. 下一阶段总路线
```

- [x] **Step 2: 用 Phase 链接表替换长篇 Phase 正文**

将 `CORE_RESTRUCTURE_PLAN.md` 中 Phase W/X/Y/Z 的长篇正文收缩为：

```markdown
## Phase 执行入口

| Phase | 当前状态 | 执行文档 | 说明 |
| --- | --- | --- | --- |
| Phase W | baseline 已完成，后续扩展真实 CAD 补验 | `docs/planning/phase-w-cad-validation-plan.md` | 真实 CAD 回读、截图、created handles 和 geometry_verified 门禁 |
| Phase X | 下一优先级 | `docs/planning/phase-x-scene-agent-alpha-plan.md` | 场景 Agent Alpha 验收 |
| Phase Y | 与 Phase X 并行或随后推进 | `docs/planning/phase-y-blank-shell-hardening-plan.md` | blank-shell 多候选、失败基准和真实样本 |
| Phase Z | 每轮都要同步 | `docs/planning/phase-z-doc-governance-plan.md` | 文档治理、回归基线和状态同步 |
```

- [x] **Step 3: 保留分歧点与完成判定**

保留并更新：

```text
## 4. 停下来问用户的分歧点
## 5. 完成判定
```

完成判定中新增一句：

```markdown
文档拆分完成不等于 Core Alpha 完成；它只让后续 Phase X/Y/W 执行更稳定。
```

## Task 4: 更新短入口和当前状态

**Files:**
- Modify: `CORE_CONTEXT_BRIEF.md`
- Modify: `CAD_AGENT_STATUS.md`
- Optional Modify: `README.md`

- [x] **Step 1: 更新 `CORE_CONTEXT_BRIEF.md` 按需展开表**

在 `CORE_CONTEXT_BRIEF.md` 的“按需展开”表中增加：

```markdown
| `docs/planning/core-platform-md-split-plan.md` | 拆分根目录主平台 Markdown 或执行 Phase Z 文档治理时 | 主平台 MD 精细化拆分计划 |
| `docs/planning/phase-w-cad-validation-plan.md` | 执行 Phase W 时 | 真实 CAD 回读闭环剧本 |
| `docs/planning/phase-x-scene-agent-alpha-plan.md` | 执行 Phase X 时 | 场景 Agent Alpha 验收剧本 |
| `docs/planning/phase-y-blank-shell-hardening-plan.md` | 执行 Phase Y 时 | blank-shell pipeline 硬化剧本 |
| `docs/planning/phase-z-doc-governance-plan.md` | 执行 Phase Z 时 | 文档治理与回归基线剧本 |
```

- [x] **Step 2: 更新 `CAD_AGENT_STATUS.md` 下一步**

将 `CAD_AGENT_STATUS.md` 的“下一步”调整为：

```markdown
1. 先按 `docs/planning/core-platform-md-split-plan.md` 完成主平台 Markdown 拆分，让 `CORE_RESTRUCTURE_PLAN.md` 收缩为总控索引。
2. 文档拆分后，优先执行 Phase X 场景 Agent Alpha 验收，或 Phase Y blank-shell pipeline 硬化与真实样本补验。
3. 后续真实 CAD 命令需要在用户会话/沙箱外运行；默认沙箱身份无法看到用户已打开的 AutoCAD COM 活动对象。
4. 每完成一个阶段：同步 `CORE_RESTRUCTURE_PLAN.md`、`CORE_STATUS.md`、本文和 `CAD_AGENT_CHANGELOG.md`。
```

- [x] **Step 3: 如需更新 `README.md`，只加入口不搬长文**

在 `README.md` 的“Clone 后推荐动手顺序”或“恢复上下文”附近增加一句：

```markdown
文档拆分和 Phase 执行剧本入口见 `docs/planning/`；根目录 `CORE_RESTRUCTURE_PLAN.md` 只作为主计划索引。
```

## Task 5: 追加变更记录

**Files:**
- Modify: `CAD_AGENT_CHANGELOG.md`

- [x] **Step 1: 在 2026-05-25 下追加本次文档拆分记录**

在 `CAD_AGENT_CHANGELOG.md` 的 `## 2026-05-25` 下方靠前位置追加：

```markdown
### 主平台 Markdown 精细化拆分计划

- 用户要求本轮不改代码，先构建主平台 Markdown 拆分计划，为下一步执行降低上下文抖动。
- 新增 `docs/planning/` 作为规划类文档目录，并新增 `docs/planning/core-platform-md-split-plan.md`。
- 计划将 `CORE_RESTRUCTURE_PLAN.md` 收缩为总控索引，把 Phase W/X/Y/Z 的长篇执行剧本迁入 `docs/planning/phase-*.md`。
- 本轮不修改 `core/`、`scripts/`、`drivers/`、`tests/`、`agents/` 或 CAD 图纸；真实 CAD 结论边界保持不变。
```

## Task 6: 文档自查

**Files:**
- Read: `docs/planning/*.md`
- Read: `CORE_RESTRUCTURE_PLAN.md`
- Read: `CORE_CONTEXT_BRIEF.md`
- Read: `CAD_AGENT_STATUS.md`
- Read: `CAD_AGENT_CHANGELOG.md`

- [x] **Step 1: 检查占位词**

Run:

```powershell
rg -n "TB[D]|TO[D]O|以后再[说]|补一[下]|随[便]|先占[位]" docs/planning CORE_RESTRUCTURE_PLAN.md CORE_CONTEXT_BRIEF.md CAD_AGENT_STATUS.md
```

Expected: no matches.

- [x] **Step 2: 检查 planning 引用**

Run:

```powershell
rg -n "docs/planning|phase-w-cad-validation-plan|phase-x-scene-agent-alpha-plan|phase-y-blank-shell-hardening-plan|phase-z-doc-governance-plan" CORE_RESTRUCTURE_PLAN.md CORE_CONTEXT_BRIEF.md CAD_AGENT_STATUS.md README.md docs/planning
```

Expected: matches show the new plan documents and root entry points.

- [x] **Step 3: 检查没有误改代码**

Run:

```powershell
git diff --name-only
```

Expected: this plan execution only adds or modifies Markdown files under root or `docs/planning/`; if output includes `core/`, `scripts/`, `drivers/`, `tests/`, `agents/`, `libraries/`, `projects/`, `examples/`, or `schemas/`, confirm those are pre-existing changes before continuing.

- [x] **Step 4: 检查主计划体量下降**

Run:

```powershell
(Get-Item CORE_RESTRUCTURE_PLAN.md).Length
```

Expected: smaller than the pre-split size `38109` bytes.

## Self-Review

Spec coverage:

- 用户要求“先不改代码”：本计划明确禁止修改代码目录。
- 用户要求“重构主平台 MD”：本计划以 `CORE_RESTRUCTURE_PLAN.md` 收缩和 `docs/planning/` 分 Phase 承接为核心。
- 用户要求“精细化 MD 拆分”：本计划定义了目标文档、迁移来源、索引更新、状态同步和自查命令。
- 用户强调当前能力已具备但未基本可用：本计划保持真实 CAD baseline 边界，并把下一轮执行导向 Phase X/Y/W，而不是宣称已完成。

Placeholder scan:

- 本文没有把禁止占位语写成执行内容；自查命令仍保留对应正则，用于后续拦截。

Type and name consistency:

- 所有新规划文档统一使用 `docs/planning/phase-*.md` 命名。
- 根目录主计划仍是 `CORE_RESTRUCTURE_PLAN.md`。
- 当前短入口仍是 `CORE_CONTEXT_BRIEF.md`。

## Execution Result

Plan executed and saved to `docs/planning/core-platform-md-split-plan.md`.

本轮实际执行方式：

1. 使用只读并行 agent 复核边界与引用风险。
2. 本地机械迁移 Phase W/X/Y/Z 到 `docs/planning/phase-*.md`。
3. 收缩 `CORE_RESTRUCTURE_PLAN.md` 为总控索引。
4. 同步短入口、状态页、README、能力状态和变更记录。
5. 运行文档自查命令并检查主计划体量下降。
