# CAD Agent Training Workbench Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild `capability-map.html` into a CAD Agent training workbench centered on the training plan matrix and Chinese agent prompt contracts.

**Architecture:** Keep the existing static artifact chain: `scripts/build_capability_map_data.py` generates `capability-map-data.js`, and `capability-map.html` renders it without a framework. Add schema v2 fields beside the current data first, then rebuild the page around `trainingPrograms`, `agentProfiles`, `promptContracts`, and `tableCBoundary`.

**Tech Stack:** Python data generator, generated JavaScript data snapshot, static HTML/CSS/vanilla JS, Playwright/browser visual verification.

---

## Files

- Modify: `scripts/build_capability_map_data.py`
  - Add schema v2 data: `capabilityCatalog`, `trainingPrograms`, `agentProfiles`, `promptContracts`, `tableCBoundary`, `trainingStages`.
  - Preserve legacy fields during transition where cheap.
  - Fix scene status parsing so `primary_training` remains intact.
- Regenerate: `capability-map-data.js`
  - Generated only by the Python script.
- Modify: `capability-map.html`
  - Replace the current dashboard with a training workbench.
  - Keep the liked capability matrix as the default plan table.
  - Rebuild agent details around Chinese prompt contracts and maturity indicators.
- Modify: `docs/status/current.md`
  - Record the new page scope and evidence boundary.
- Modify: `docs/status/changelog.md`
  - Add a concise package note after verification.
- Optional if package completion is claimed: `docs/handoffs/current.md`, `docs/handoffs/package-index.md`
  - Update only after the implementation is verified.

## Verification Commands

Use these during and after implementation:

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\build_capability_map_data.py
& $py -m py_compile scripts\build_capability_map_data.py
node --check capability-map-data.js
node -e "const fs=require('fs'); const html=fs.readFileSync('capability-map.html','utf8'); const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n'); new Function(scripts); console.log('inline-js-ok')"
```

For visual checks, use the Browser plugin or Playwright against `file:///C:/Users/User/Desktop/CAD-AGENT/capability-map.html`.

---

### Task 1: Data Schema v2

**Files:**
- Modify: `scripts/build_capability_map_data.py`
- Regenerate: `capability-map-data.js`

- [ ] **Step 1: Add explicit training stages**

Add `TRAINING_STAGE_DEFS` near the constants:

```python
TRAINING_STAGE_DEFS = [
    {"id": "not_started", "label": "未开训", "rank": 0},
    {"id": "prompt_defined", "label": "Prompt 已定义", "rank": 1},
    {"id": "case_training", "label": "案例训练中", "rank": 2},
    {"id": "user_feedback_pass", "label": "用户反馈通过", "rank": 3},
    {"id": "systemized", "label": "已沉淀", "rank": 4},
]
```

- [ ] **Step 2: Add derivation helpers**

Add helpers that derive `capabilityCatalog`, `trainingPrograms`, `agentProfiles`, `promptContracts`, and `tableCBoundary` from existing sources. The minimum interface must include:

```python
def capability_catalog() -> list[dict[str, Any]]:
    ...

def training_programs(capabilities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ...

def agent_profiles(agents: list[dict[str, Any]], programs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ...

def prompt_contracts(agents: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ...

def table_c_boundary() -> dict[str, Any]:
    ...
```

Every user-facing field must be Chinese or a known file/API token.

- [ ] **Step 3: Fix status parsing**

Update `parse_training_statuses()` so markdown bold markers do not remove underscores:

```python
raw_status = match.group(2).replace("**", "").replace("*", "").strip()
```

Expected output for `residential` is `primary_training`, not `primarytraining`.

- [ ] **Step 4: Wire schema v2 into `build_data()`**

Return both v2 and transition fields:

```python
capabilities = enrich_capabilities()
agents = scene_agents() + pipeline_agents() + demand_agent_summary()
programs = training_programs(capabilities)
return {
    "schemaVersion": 2,
    "generatedAt": datetime.now(UTC).replace(microsecond=0).isoformat(),
    "trainingStages": TRAINING_STAGE_DEFS,
    "capabilityCatalog": capability_catalog(),
    "trainingPrograms": programs,
    "agentProfiles": agent_profiles(agents, programs),
    "promptContracts": prompt_contracts(agents),
    "tableCBoundary": table_c_boundary(),
    ...
}
```

- [ ] **Step 5: Regenerate and inspect**

Run:

```powershell
& $py scripts\build_capability_map_data.py
node --check capability-map-data.js
```

Expected: script writes `capability-map-data.js`; `node --check` exits 0.

### Task 2: Training Plan Matrix Workbench

**Files:**
- Modify: `capability-map.html`

- [ ] **Step 1: Replace the masthead with a compact status bar**

Use a compact top area with title `CAD Agent 训练工作台`, current primary scene, capability count, agent count, and table C boundary.

- [ ] **Step 2: Make the plan matrix the default view**

The first tab should be `训练计划表单`. It keeps:

```text
全部 / 基础家具 / 储位家具 / 厨卫对象 / 基础绘图 / 标注表达
能力项 / 训练阶段 / 责任智能体 / 下一轮训练 / 标准图库 / 常识整理 / 训练流淀 / 自产资产
```

Rename or map categories so the user sees `基础家具` and `储位家具` as separate filters.

- [ ] **Step 3: Add richer stage cells**

Replace blank boxes with state chips:

```text
空 = 未纳入
计划 = 计划中
训 = 案例训练中
证 = 已有证据
沉 = 已沉淀
```

Use color sparingly: gray, amber, blue, green.

- [ ] **Step 4: Add right-side inspector**

Clicking a row updates an inspector with:

```text
本轮训练目标
责任智能体分工
要补的 prompt 约束
成功门槛
不算通过的情况
证据边界
```

Avoid opening a large modal for ordinary row inspection.

- [ ] **Step 5: Keep training plan modal only for deep view**

If retained, the modal should show detailed training plan and agent route, not duplicate the inspector.

### Task 3: Agent Prompt Workbench

**Files:**
- Modify: `capability-map.html`

- [ ] **Step 1: Replace agent card grid with a two-pane workbench**

Left pane: grouped agent list:

```text
主训智能体
训练流水线智能体
暂停场景智能体
需求侧角色
```

Right pane: selected agent prompt contract.

- [ ] **Step 2: Make Chinese prompt summary the default**

Selected agent detail must start with:

```text
中文 Prompt 摘要
角色设定
职责边界
输入要求
输出格式
硬门槛
禁止事项
```

- [ ] **Step 3: Add maturity bars**

Show four maturity indicators:

```text
Prompt 完整度
调用能力成熟度
训练覆盖度
证据成熟度
```

Each bar must include a percent and a short Chinese explanation. Make clear that these are not table C CAD pass rates.

- [ ] **Step 4: Add editable training guidance**

Add a `可调 Prompt 点` section that lists the next likely rule changes after training.

- [ ] **Step 5: Keep source files folded**

Move JSON/MD file paths and document explanations into a collapsed or visually secondary section.

### Task 4: Failure And Learning View

**Files:**
- Modify: `capability-map.html`

- [ ] **Step 1: Replace heatmap-first layout**

Make failures actionable:

```text
问题 / 影响能力 / 责任智能体 / 下一步训练 / 应沉淀到哪里
```

- [ ] **Step 2: Connect failure chips to plan matrix**

Clicking a failure mode filters or highlights related training programs.

- [ ] **Step 3: Keep learning routes as the bottom explanation**

Show `case feedback -> training-errors -> scene rules -> pipeline -> core/tests -> system library` as a quiet route map.

### Task 5: First Visual Verification

**Files:**
- Inspect rendered `capability-map.html`
- Save screenshots if using Playwright.

- [ ] **Step 1: Open desktop viewport**

Check 1365x900:

```text
No text overlap.
Plan matrix visible on first screen.
Agent prompt detail readable.
Table C boundary not visually dominant.
```

- [ ] **Step 2: Open mobile viewport**

Check 390x844:

```text
Tabs scroll or stack.
Plan rows remain readable.
Inspector appears below selected row or as a non-overlapping panel.
```

- [ ] **Step 3: Record visual issues**

List concrete issues for second-round agents.

### Task 6: Second-Round Agent Review And Refinement

**Files:**
- Modify: `capability-map.html`
- Modify if needed: `scripts/build_capability_map_data.py`

- [ ] **Step 1: Dispatch visual critique agent**

Ask for issues in hierarchy, density, Chinese readability, and prompt workbench utility.

- [ ] **Step 2: Dispatch bug-risk agent**

Ask for broken interactions, missing data fallbacks, misleading percentages, and table C boundary issues.

- [ ] **Step 3: Apply scoped refinements**

Fix only issues that improve the target state:

```text
plan matrix clarity
agent prompt usefulness
maturity visibility
no misleading CAD-proof claims
responsive readability
```

### Task 7: Final Verification And Status Records

**Files:**
- Modify: `docs/status/current.md`
- Modify: `docs/status/changelog.md`
- Optional: `docs/handoffs/current.md`, `docs/handoffs/package-index.md`

- [ ] **Step 1: Run syntax and data checks**

Run all verification commands listed above.

- [ ] **Step 2: Run browser visual checks again**

Check desktop and mobile after refinements.

- [ ] **Step 3: Update status docs**

Record:

```text
CAPABILITY-MAP-TRAINING-WORKBENCH-03
capability-map.html
capability-map-data.js
scripts/build_capability_map_data.py
boundary: training plan and prompt visualization only; not table C replacement
```

- [ ] **Step 4: Final diff review**

Run:

```powershell
git status --short
git diff -- capability-map.html scripts/build_capability_map_data.py docs/status/current.md docs/status/changelog.md
```

Expected: only intended files changed, generated data changed by script, no unrelated reversions.
