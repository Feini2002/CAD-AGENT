# Model Agent Local Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不依赖 OpenAI / 网络可用性的前提下，把模型型 Agent 的本地边界、可审计决策链、Agent 连续性、工具请求链和 closeout 闭环先加固到可测试状态。

**Architecture:** 外部网络、OpenAI provider、Codex 登录态和模型权限统一归入 `provider_unavailable` / `network_unavailable` 类问题，本计划不解决这些外部问题。计划先让本地 Orchestrator 只发送显式 payload，所有模型型 Agent 通过标准 `handoff_packet` 交接，所有“思考”以可审计决策字段表达，所有工具请求走 Tool Contract ReAct，所有交付口径由 closeout 状态机放行或阻断。真实 `gpt-5.5` 恢复后，只替换模型输出来源，不改变本地 gate。

**Tech Stack:** Python stdlib、JSON Schema、Codex CLI bridge、`unittest`、现有 `core/model_review`、`core/orchestrator`、`scripts/run_model_agent_live_collab_proof.py`、`scripts/run_doc_governance_audit.py`。

---

## Scope Boundary

本计划刻意不处理以下外部问题：

- 网络 / 沙箱无法连接 `api.openai.com`。
- Codex CLI 登录态、模型权限、额度、OpenAI 组织审批。
- OpenAI 侧数据使用策略、ZDR / MAM / abuse monitoring 配置。
- 真实 AutoCAD / COM 是否打开、窗口是否可截图。

这些问题后续仍要解决，但不应阻塞本地架构先变严谨。本计划只解决“即使网络不可用，本地链路也能证明自己边界清楚、状态可审计、失败不乱归因”的部分。

## Current Findings To Preserve

- 本地文件内容技术上可以进入模型上下文；最小 probe 已证明 `codex.cmd exec` 能在只读沙箱读取当前 cwd 的 `marker.txt` 并回传内容。
- `--ignore-rules` 只忽略 execpolicy `.rules`，不等于忽略 `AGENTS.md`。现有 trace 中出现过 `Project doc C:\Users\User\Desktop\CAD-AGENT\AGENTS.md exceeds remaining budget - truncating`，说明仓库子目录作为 model cwd 时仍可能加载项目文档。
- 现有模型链已能产生 `modelInvoked=true`、`schemaValid=true`、trace、`modelProviderStatus` 和 downstream JSON handoff，但完成审计仍会因真实 CAD readback、截图、visual acceptance、neighbor protection 缺失而 blocked。
- 原始 chain-of-thought 不是可交付目标；目标应改为“可审计决策链”：结构化输出证据、假设、缺口、替代方案、阻断原因和下一步。

## File Structure

### New files planned

- `core/model_review/export_manifest.py`
  - 负责在真实模型调用前生成 `model-export-manifest/v1`，列出所有拟发送内容、来源、字节数、hash、授权依据、禁止项扫描和阻断原因。
- `core/schemas/model_export_manifest.schema.json`
  - 约束 export manifest 的字段、状态和 sent / blocked artifacts 结构。
- `core/orchestrator/agent_handoff.py`
  - 负责生成、校验和归一化 `handoff_packet/v1`，让独立模型调用之间靠显式状态交接。
- `core/schemas/agent_handoff_packet.schema.json`
  - 约束 handoff packet 的 evidence refs、state patch、open questions、downstream instructions 和 allowed claims。
- `core/orchestrator/closeout_state_machine.py`
  - 负责把 provider / schema / tool / CAD / visual / delivery 的状态映射为固定 closeout states。
- `core/orchestrator/error_taxonomy.py`
  - 统一错误分类，避免把 provider unavailable、schema invalid、业务 fail、CAD evidence missing 混成一个 blocked。
- `scripts/run_model_agent_local_hardening_proof.py`
  - 无网络 fixture proof，跑 export manifest、handoff、decision chain、toolIntent、closeout state machine。
- `tests/core/test_model_export_manifest.py`
- `tests/core/test_agent_handoff.py`
- `tests/core/test_closeout_state_machine.py`
- `tests/core/test_error_taxonomy.py`
- `tests/core/test_model_agent_local_hardening_proof.py`

### Existing files planned to modify

- `core/model_review/codex_cli_client.py`
  - 在 `run_codex_cli_review()` 前写 `export_manifest.json`；manifest fail 时不启动 `codex.cmd exec`。
  - 将 model cwd 改为 repo 外隔离目录，trace 仍写回当前 run package。
  - 扫描 stderr 中的非预期 project doc / plugin context warning，并写入 context leak audit。
- `core/model_review/prompt_library.py`
  - 在 rendered prompt metadata 中声明 export manifest id、allowed refs 和 explicit payload policy。
- `core/model_review/provider_status.py`
  - 接入 error taxonomy，保持 provider availability 与业务状态分离。
- `core/orchestrator/model_agent_chain_runtime.py`
  - 每个模型型 Agent 输出后生成 / 校验 `handoff_packet`。
  - 下游 payload 只读上游 handoff packet 和明确 evidence refs，不依赖隐式模型记忆。
  - completion audit 引用 closeout state machine 结果。
- `core/orchestrator/tool_contract.py`
  - 增加 fixture-driven chain checks：模型请求工具不等于工具执行，工具执行不等于 CAD / closeout 证明。
- `core/orchestrator/closeout_gate.py`
  - 若保留现有 closeout gate，则把状态判定委托给 `closeout_state_machine.py`。
- `core/schemas/registry.py`
  - 登记新 schema。
- `scripts/probe_codex_cli_model_review.py`
  - dry-run 报告中输出 `exportManifestStatus`、`repoExternalCwd` 和 `unexpectedProjectContextLoaded`。
- `scripts/run_model_agent_live_collab_proof.py`
  - 增加本地 hardening proof 可复用的 fixture / no-network 参数，或明确调用新脚本。
- `docs/status/changelog.md`
  - 实施完成后记录包名和边界，不在本计划阶段提前写完成事实。
- `docs/architecture/README.md`
  - 已由本计划阶段加入索引。
- `CORE_RESTRUCTURE_PLAN.md`
  - 已由本计划阶段加入主路由入口。

## Target Local Chain

```text
model task request
  -> explicit payload builder
  -> export_manifest gate
  -> repo-external isolated model cwd
  -> prompt pack / strict schema
  -> model output or fixture output
  -> schema validation + provider status
  -> auditable decision fields
  -> handoff_packet
  -> toolIntent gate, if any
  -> tool_trace / candidate / validation report
  -> closeout_state_machine
  -> delivery allowed claims or blocked reasons
```

## Required States And Error Taxonomy

### Provider / model states

- `provider_ready`: Codex CLI / SDK 调用成功，模型输出可读。
- `provider_unavailable`: CLI 不存在、登录态缺失、模型无权限、API 不通、返回非零。
- `network_unavailable`: 明确是 websocket / HTTPS / DNS / sandbox 网络失败。
- `schema_invalid`: 模型有输出但 strict schema 不通过。
- `model_business_blocked`: 模型正常调用，但业务判断为 `fail` / `unavailable` / `needs_more_evidence`。

### Local chain states

- `context_export_blocked`: export manifest 发现未授权文件、敏感项、整仓 / 全屏 / whole output 外传倾向。
- `handoff_invalid`: 上游 JSON 缺 handoff packet 或下游引用丢失。
- `tool_contract_blocked`: `toolIntent` 越权、缺 target scope、风险等级不允许或试图保存 / 删除 / 改正式图层。
- `cad_evidence_missing`: validate / dry-run / created handles / bbox / layer / readback 缺失。
- `visual_evidence_missing`: 截图、视觉复审或 neighbor protection 缺失。
- `closeout_blocked`: 本地状态机不允许交付声明。
- `ready_for_user_review`: 本地证据足以请用户目视验收，但仍不等于用户已验收。

## Task 1: Export Manifest Gate

**Files:**
- Create: `core/model_review/export_manifest.py`
- Create: `core/schemas/model_export_manifest.schema.json`
- Modify: `core/model_review/codex_cli_client.py`
- Modify: `core/schemas/registry.py`
- Test: `tests/core/test_model_export_manifest.py`

- [x] **Step 1: Write tests for allowed explicit payload**

Create tests that build a prompt from known strings and a schema path under `core/model_review/schemas/`. Expected manifest:

```python
def test_export_manifest_allows_explicit_prompt_schema_and_payload(tmp_path):
    manifest = build_model_export_manifest(
        agent_id="pipeline_design_director",
        trace_id="trace-1",
        prompt_text="safe prompt",
        schema_path=PROJECT_ROOT / "core/model_review/schemas/design_director_review.schema.json",
        payload_refs=["user_request.json", "context_pack.json"],
        image_paths=[],
        approval_basis=["MODEL_DATA_EXPORT_AUTHORIZATION.md#默认允许的数据"],
    )

    assert manifest["status"] == "pass"
    assert manifest["route"] == "codex_cli_local"
    assert manifest["sentArtifacts"][0]["kind"] == "prompt_text"
    assert manifest["forbiddenScan"]["secretLikeCount"] == 0
    assert manifest["unexpectedLocalFiles"] == []
```

- [x] **Step 2: Write tests for blocked unauthorized local files**

```python
def test_export_manifest_blocks_unapproved_local_file(tmp_path):
    secret = tmp_path / "not_in_evidence_bundle.txt"
    secret.write_text("LOCAL_ONLY_PROBE", encoding="utf-8")

    manifest = build_model_export_manifest(
        agent_id="pipeline_design_director",
        trace_id="trace-2",
        prompt_text=f"read {secret}",
        schema_path=PROJECT_ROOT / "core/model_review/schemas/design_director_review.schema.json",
        payload_refs=[],
        image_paths=[],
        approval_basis=["MODEL_DATA_EXPORT_AUTHORIZATION.md#默认允许的数据"],
    )

    assert manifest["status"] == "blocked"
    assert "unauthorized_local_path" in manifest["blockingReasons"]
```

- [x] **Step 3: Implement `build_model_export_manifest()`**

Implement the function with these required output keys:

```python
{
  "schemaVersion": "model-export-manifest/v1",
  "status": "pass|blocked",
  "route": "codex_cli_local",
  "agentId": "pipeline_design_director",
  "traceId": "trace-1",
  "approvalBasis": ["MODEL_DATA_EXPORT_AUTHORIZATION.md#默认允许的数据"],
  "sentArtifacts": [
    {"kind": "prompt_text", "byteCount": 11, "sha256": "sha256-of-prompt-text"},
    {"kind": "schema_snapshot", "path": "core/model_review/schemas/design_director_review.schema.json", "byteCount": 2048, "sha256": "sha256-of-schema"}
  ],
  "blockedArtifacts": [],
  "unexpectedLocalFiles": [],
  "forbiddenScan": {
    "secretLikeCount": 0,
    "wholeRepoRequested": False,
    "wholeOutputRequested": False,
    "fullScreenScreenshotRequested": False
  },
  "blockingReasons": [],
  "evidenceBoundary": ["manifest pass only proves export boundary, not model quality or CAD geometry"]
}
```

The function must be deterministic and must not call OpenAI.

- [x] **Step 4: Wire the manifest into `run_codex_cli_review()`**

Before starting the subprocess:

- write `trace_dir/export_manifest.json`;
- if `status=blocked`, return `modelProviderStatus.route="codex_cli_local"` with `modelInvoked=false`, `modelUnavailable=true`, `reason="context_export_blocked"`;
- include the manifest path in `trace_summary.md`.

- [x] **Step 5: Verify**

Run:

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_model_export_manifest tests.core.test_model_review
```

Expected: all tests pass; no network call is made.

## Task 2: Repo-External Model CWD And Context Leak Audit

**Files:**
- Modify: `core/model_review/codex_cli_client.py`
- Modify: `scripts/probe_codex_cli_model_review.py`
- Test: `tests/core/test_model_review.py`

- [x] **Step 1: Write fake-runner test for repo-external cwd**

The fake runner should capture the subprocess `cwd` and assert it is not under `PROJECT_ROOT`.

```python
def test_codex_cli_review_uses_repo_external_cwd(tmp_path):
    captured = {}

    def fake_runner(command, **kwargs):
        captured["cwd"] = Path(kwargs["cwd"]).resolve()
        output_path = Path(command[command.index("--output-last-message") + 1])
        output_path.write_text(valid_model_json(), encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    run_codex_cli_review(
        prompt="safe prompt",
        schema_path=PROJECT_ROOT / "core/model_review/schemas/design_director_review.schema.json",
        output_path=tmp_path / "review.json",
        image_paths=[],
        input_summary_refs=[],
        config=CodexCliReviewConfig(enabled=True, ignore_user_config=True, skip_git_repo_check=True),
        runner=fake_runner,
        cwd=PROJECT_ROOT / "output/model_reviews/codex_cli_isolated_workdir",
        agent_id="pipeline_design_director",
        task_type="design_director_review",
        trace_id="trace-1",
        trace_dir=tmp_path / "trace",
    )

    assert not captured["cwd"].is_relative_to(PROJECT_ROOT.resolve())
```

- [x] **Step 2: Implement repo-external cwd**

Use a local temp directory such as:

```text
%TEMP%/cad-agent-model-bridge/<trace_id>/
```

Only place files there that are required for the call. Keep trace artifacts in the run package under `output/runs/**` or `output/model_reviews/**`.

- [x] **Step 3: Add context leak audit**

Scan stderr for known warnings:

- `Project doc`
- `AGENTS.md exceeds remaining budget`
- `reading additional input from stdin` if unexpected
- plugin remote sync warnings that imply nonessential context loading

Write:

```json
{
  "schemaVersion": "model-context-leak-audit/v1",
  "unexpectedProjectContextLoaded": false,
  "warnings": [],
  "blocking": false
}
```

For the first implementation, make project-doc loading `blocking=true` in model-review strict mode.

- [x] **Step 4: Verify**

Run:

```powershell
& $py -m unittest tests.core.test_model_review tests.core.test_model_prompt_library
```

Expected: fake-runner tests pass without network.

## Task 3: Auditable Decision Chain Fields

**Files:**
- Modify: `core/model_review/schemas/*.schema.json`
- Modify: `core/model_review/prompt_library.py`
- Modify: `core/model_review/prompt_packs/*/prompt.md`
- Test: `tests/core/test_model_prompt_library.py`
- Test: `tests/core/test_model_review.py`

- [x] **Step 1: Standardize visible decision fields**

Every model-backed Agent schema must require or normalize these fields:

```json
{
  "decision": "pass|fail|needs_more_evidence|unavailable",
  "evidenceUsed": [],
  "evidenceMissing": [],
  "assumptions": [],
  "alternativesConsidered": [],
  "blockingReasons": [],
  "nextRequiredEvidence": [],
  "finalResponseAllowedClaims": [],
  "learningCandidate": {},
  "toolIntent": null
}
```

Do not call these fields chain-of-thought. They are visible audit summaries.

- [x] **Step 2: Add schema tests**

Use fixtures that intentionally omit `assumptions` or `alternativesConsidered`; they should fail schema validation until the schema and normalizer are updated.

- [x] **Step 3: Update Prompt Pack bridge metadata**

Add a stable instruction:

```text
Do not expose raw chain-of-thought. Return visible audit fields only: evidenceUsed, evidenceMissing, assumptions, alternativesConsidered, blockingReasons, nextRequiredEvidence, and finalResponseAllowedClaims.
```

- [x] **Step 4: Verify**

Run:

```powershell
& $py -m unittest tests.core.test_model_prompt_library tests.core.test_model_review
```

Expected: all prompt-pack rendered prompts include the visible audit instruction; schemas reject missing audit fields.

## Task 4: Agent Handoff Packet Protocol

**Files:**
- Create: `core/orchestrator/agent_handoff.py`
- Create: `core/schemas/agent_handoff_packet.schema.json`
- Modify: `core/orchestrator/model_agent_chain_runtime.py`
- Modify: `core/schemas/registry.py`
- Test: `tests/core/test_agent_handoff.py`
- Test: `tests/core/test_model_agent_chain_runtime.py`

- [x] **Step 1: Define `handoff_packet/v1`**

Required fields:

```json
{
  "schemaVersion": "handoff_packet/v1",
  "fromAgentId": "pipeline_design_director",
  "toAgentIds": ["pipeline_style_generator"],
  "status": "ready|blocked|needs_more_evidence",
  "decisionSummary": "",
  "statePatch": {},
  "evidenceRefs": [],
  "evidenceMissing": [],
  "openQuestions": [],
  "downstreamInstructions": [],
  "allowedClaims": [],
  "forbiddenClaims": [],
  "sha256OfSourceOutput": ""
}
```

- [x] **Step 2: Write tests for downstream citation**

The downstream payload must include the upstream handoff packet path and hash. If the packet is missing, chain status becomes `handoff_invalid`.

- [x] **Step 3: Implement packet builder**

`build_handoff_packet(agent_output, from_agent_id, to_agent_ids, source_path)` should derive the packet from the model output without inventing evidence.

- [x] **Step 4: Wire chain runtime**

After each model-backed Agent output:

- write `agent_outputs/<agent>.handoff.json`;
- add this path to downstream `evidenceRefs`;
- include handoff summary in downstream `agentSpecific.upstreamOutputs`;
- if packet invalid, stop chain with `handoff_invalid`.

- [x] **Step 5: Verify**

Run:

```powershell
& $py -m unittest tests.core.test_agent_handoff tests.core.test_model_agent_chain_runtime
```

Expected: no-CAD chain writes handoff packets and downstream payloads cite them.

## Task 5: Closeout State Machine

**Files:**
- Create: `core/orchestrator/closeout_state_machine.py`
- Modify: `core/orchestrator/closeout_gate.py`
- Modify: `core/orchestrator/model_agent_chain_runtime.py`
- Test: `tests/core/test_closeout_state_machine.py`
- Test: `tests/core/test_closeout_gate.py`

- [x] **Step 1: Write state transition tests**

Required examples:

```python
def test_missing_readback_blocks_cad_preview_verified():
    result = evaluate_closeout_state(model_ok=True, validation_ok=True, dry_run_ok=True, readback_ok=False)
    assert result["state"] == "cad_evidence_missing"

def test_fake_driver_never_proves_geometry():
    result = evaluate_closeout_state(driver_mode="fake_driver_preflight", cadGeometryVerified=False)
    assert result["state"] == "cad_evidence_missing"

def test_visual_missing_blocks_delivery_claim():
    result = evaluate_closeout_state(readback_ok=True, visual_acceptance_ok=False)
    assert result["state"] == "visual_evidence_missing"

def test_all_required_evidence_ready_for_user_review():
    result = evaluate_closeout_state(readback_ok=True, visual_acceptance_ok=True, neighbor_protection_ok=True)
    assert result["state"] == "ready_for_user_review"
```

- [x] **Step 2: Implement `evaluate_closeout_state()`**

The state machine must not use model status alone to pass CAD or delivery. It must require:

- `schemaValid=true` for model-backed outputs, when model is required;
- validate pass;
- dry-run pass;
- created handles readback ok;
- `targetLayer=CODEX_PREVIEW`;
- `savedCurrentDwg=false`;
- visual acceptance pass when visible delivery is claimed;
- neighbor protection pass when CAD objects are near existing content.

- [x] **Step 3: Replace ad hoc closeout checks**

Keep existing report shape if needed, but add:

```json
{
  "closeoutState": "ready_for_user_review",
  "stateMachineVersion": "closeout-state-machine/v1",
  "requiredEvidence": [],
  "missingEvidence": []
}
```

- [x] **Step 4: Verify**

Run:

```powershell
& $py -m unittest tests.core.test_closeout_state_machine tests.core.test_closeout_gate tests.core.test_model_agent_chain_runtime
```

Expected: blocked cases stay blocked for the exact missing evidence reason.

## Task 6: ToolIntent Fixture Chain

**Files:**
- Modify: `core/orchestrator/tool_contract.py`
- Modify: `core/orchestrator/model_agent_chain_runtime.py`
- Test: `tests/core/test_tool_contract_react.py`
- Test: `tests/core/test_model_agent_chain_runtime.py`

- [x] **Step 1: Add fixture model outputs**

Create fixture payloads in tests for:

- Stage 1 read-only evidence summary request.
- Stage 2 candidate CAD_PLAN write request.
- Stage 3 validate / dry-run request.
- Stage 4 preview CAD execute request.
- Blocked save current DWG request.
- Blocked delete / formal layer modification request.

- [x] **Step 2: Assert tool trace semantics**

Each accepted tool request must write:

```json
{
  "schemaVersion": "tool-trace/v1",
  "orchestratorDecision": "allowed|blocked|needs_more_evidence",
  "executionStatus": "executed|not_executed",
  "resultStatus": "pass|fail|not_verified",
  "downstreamReadableSummary": "",
  "evidenceBoundary": []
}
```

Blocked tool requests must still be traceable and must not write candidate or CAD artifacts.

- [x] **Step 3: Verify downstream handoff**

Downstream Agent payloads should receive tool trace refs, not raw tool side effects.

- [x] **Step 4: Verify**

Run:

```powershell
& $py -m unittest tests.core.test_tool_contract_react tests.core.test_model_agent_chain_runtime
```

Expected: all allowed / blocked / needs_more_evidence fixture paths are deterministic.

## Task 7: Error Taxonomy

**Files:**
- Create: `core/orchestrator/error_taxonomy.py`
- Modify: `core/model_review/provider_status.py`
- Modify: `core/model_review/trace_review.py`
- Modify: `core/orchestrator/model_agent_chain_runtime.py`
- Test: `tests/core/test_error_taxonomy.py`
- Test: `tests/core/test_model_review.py`

- [x] **Step 1: Define canonical error codes**

Use stable strings:

```python
PROVIDER_UNAVAILABLE = "provider_unavailable"
NETWORK_UNAVAILABLE = "network_unavailable"
SCHEMA_INVALID = "schema_invalid"
CONTEXT_EXPORT_BLOCKED = "context_export_blocked"
MODEL_BUSINESS_BLOCKED = "model_business_blocked"
HANDOFF_INVALID = "handoff_invalid"
TOOL_CONTRACT_BLOCKED = "tool_contract_blocked"
CAD_EVIDENCE_MISSING = "cad_evidence_missing"
VISUAL_EVIDENCE_MISSING = "visual_evidence_missing"
CLOSEOUT_BLOCKED = "closeout_blocked"
```

- [x] **Step 2: Add classifier tests**

Examples:

- websocket / HTTPS error text -> `network_unavailable`;
- non-zero Codex return without network clue -> `provider_unavailable`;
- schema missing required fields -> `schema_invalid`;
- business `status=unavailable` with `modelInvoked=true` and schema valid -> `model_business_blocked`, not provider unavailable.

- [x] **Step 3: Wire taxonomy into reports**

Add `errorCategory` to provider status, trace review and completion audit.

- [x] **Step 4: Verify**

Run:

```powershell
& $py -m unittest tests.core.test_error_taxonomy tests.core.test_model_review tests.core.test_model_agent_chain_runtime
```

Expected: external provider failures and local business blockers are separated.

## Task 8: No-Network Local Hardening Proof

**Files:**
- Create: `scripts/run_model_agent_local_hardening_proof.py`
- Test: `tests/core/test_model_agent_local_hardening_proof.py`
- Modify: `docs/status/changelog.md` after implementation passes.

- [x] **Step 1: Write the proof script contract**

The script must run without OpenAI and without AutoCAD. It should produce:

```json
{
  "schemaVersion": "model-agent-local-hardening-proof/v1",
  "status": "pass|fail",
  "exportManifestGate": "pass",
  "repoExternalCwd": true,
  "unexpectedProjectContextLoaded": false,
  "decisionChainFields": "pass",
  "handoffPackets": "pass",
  "toolIntentFixtures": "pass",
  "closeoutStateMachine": "pass",
  "errorTaxonomy": "pass",
  "notProven": [
    "real OpenAI provider availability",
    "real gpt-5.5 judgement quality",
    "real AutoCAD geometry",
    "user acceptance"
  ]
}
```

- [x] **Step 2: Implement fixture runner**

Use local fixture outputs shaped like model outputs. Do not call `codex.cmd exec`.

- [x] **Step 3: Verify**

Run:

```powershell
& $py scripts\run_model_agent_local_hardening_proof.py --run-id local-hardening-proof
& $py -m unittest tests.core.test_model_agent_local_hardening_proof
```

Expected: proof report is `status=pass`, with explicit `notProven` boundaries.

## Task 9: Documentation And Main Plan Sync

**Files:**
- Modify: `docs/architecture/model-agent-local-hardening-plan.md`
- Modify: `docs/architecture/README.md`
- Modify: `CORE_RESTRUCTURE_PLAN.md`
- Modify after implementation: `docs/status/changelog.md`

- [x] **Step 1: Keep this plan as architecture detail**

This document is the detailed hardening plan. It must not become a second global backlog; execution priority remains in `CORE_RESTRUCTURE_PLAN.md` and `docs/planning/任务清单.md`.

- [x] **Step 2: Record completion only after implementation**

When executed, add one changelog package such as:

```text
MODEL-AGENT-LOCAL-HARDENING-01
```

Do not mark it completed until local proof and tests pass.

- [x] **Step 3: Verify docs**

Run:

```powershell
& $py scripts\run_doc_governance_audit.py --fail-on-findings
```

Expected: no new doc governance findings from this plan.

## Acceptance Criteria

This plan is complete only when all of these are true:

- `export_manifest.json` exists for every model bridge call and blocks unauthorized local context before network call.
- Codex CLI model cwd is repo-external for model review, or a test proves project docs cannot be implicitly loaded.
- Trace includes context leak audit and flags unexpected `AGENTS.md` / project doc loading.
- All model-backed Agent outputs contain visible audit fields, not raw chain-of-thought.
- Each model-backed Agent writes a `handoff_packet/v1`; downstream payloads cite packet path and hash.
- ToolIntent fixtures prove allowed and blocked Stage 1 / 2 / 3 / 4 paths without relying on real model output.
- Closeout state machine blocks delivery until CAD, visual and neighbor evidence is present.
- Error taxonomy separates external provider/network issues from local schema/business/evidence issues.
- A no-network local hardening proof passes and clearly lists what it does not prove.

## Execution Order

Recommended order:

1. Export manifest gate.
2. Repo-external cwd and context leak audit.
3. Error taxonomy.
4. Auditable decision fields.
5. Handoff packet protocol.
6. ToolIntent fixture chain.
7. Closeout state machine.
8. No-network local hardening proof.
9. Documentation and changelog sync.

This order gives the safest early win: first stop accidental context export, then make failures legible, then strengthen continuity and closeout.

## Final Verification Bundle

Run after implementation:

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py -m unittest tests.core.test_model_export_manifest tests.core.test_agent_handoff tests.core.test_closeout_state_machine tests.core.test_error_taxonomy tests.core.test_model_agent_local_hardening_proof tests.core.test_model_review tests.core.test_model_prompt_library tests.core.test_model_agent_chain_runtime tests.core.test_tool_contract_react
& $py scripts\run_model_agent_local_hardening_proof.py --run-id local-hardening-proof
& $py scripts\run_doc_governance_audit.py --fail-on-findings
```

Expected:

- targeted tests pass;
- local proof `status=pass`;
- doc governance has no new findings;
- final report states OpenAI/network/real AutoCAD are still outside this proof unless separately tested.
