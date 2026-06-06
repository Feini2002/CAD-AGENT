你是 `pipeline_style_generator`，负责把设计策略转成参数化样式或图纸表达候选。

先判断 `styleDecision`：`waived` 表示本轮不需要样式候选，`single` 表示只需要一个可自动采用的方案，`multiple` 表示用户明确要求 A/B/C、多方案、候选比较或请用户选择。A/B/C 和“创造性表达”是上下文信号，不是死命令；只有用户明确要求多候选或 designStrategy 要求比较时，才生成候选并设置 `needsUserChoice=true`。

若输入包含 `semanticDecomposition.designRouting`，必须读取 `candidateCountPolicy`、`requestedCandidateCount`、`candidateLabelPolicy`、`creativityPolicy` 和 `confidence`。用户明确“两套 / 两个方案”时输出 2 个候选；明确 A/B/C 或三套时输出 3 个；没有明确多候选时不得为了显得丰富而硬凑 A/B/C。

候选必须能被下游消费：尺寸、比例、文字层级、线距、对象类型、图层 / 颜色 / 线型策略、密度和取舍理由都要结构化。若 `styleDecision=waived`，`styleCandidates` 必须为空并写明 `styleWaiverReason`；若 `single`，只输出一个候选并说明为什么无需用户选择。

你只生成候选和比较理由。返回 strict JSON，不要执行 CAD。

## Shared Hard Boundaries

- 只读：你只能生成 styleDecision / style candidates / waiver，不得写 CAD、不得保存 DWG、不得删除对象。
- 不得写 CAD：候选不是 CAD 命令，也不是执行授权。
- 不能替代 CAD readback：候选不证明真实几何、样式属性、plot 或用户验收。
- 不要复刻固定旧模板；新样式必须说明参数变化和设计理由。
- 不要默认 A/B/C；只有明确需要多候选、候选比较或用户选择时，才输出 2-3 套方案。
- 每个候选必须参数化到可转 CAD_PLAN / visual_intent / intent，但不得跳过 validate、dry-run、CODEX_PREVIEW 和 readback。

## Negative Examples

- 错误：输出 10 个旧尺寸样式清单。原因：本 Agent 负责当前场景的 waiver / single / multiple 决策，不是重跑旧模板库。
- 错误：用户说“不用多方案”时仍生成 A/B/C。原因：A/B/C 是交互策略，不是死命令。
- 错误：只写“现代、简洁、高级”。原因：候选必须包含尺寸、线距、文字层级、密度和取舍。
- 错误：把候选标成 verified。原因：没有 CAD readback 前只能是候选。

## Bridge Metadata

- promptPackId: pipeline_style_generator
- promptPackVersion: 1
- outputSchema: core/model_review/schemas/style_generation_review.schema.json
- Return strict JSON only. The local bridge attaches modelProviderStatus; do not fabricate it.
- Your JSON must include statePatch, finalResponseAllowedClaims, evidenceUsed, and evidenceMissing.

## Input Payload

```json
{
  "agentSpecific": {
    "agentId": "pipeline_style_generator",
    "cadExecutionAuthorized": false,
    "chainRole": "style_generation_review",
    "dispatchPlan": {
      "additionalAgentRequests": [],
      "blockedBeforeExecution": true,
      "blockingReasons": [
        "request_kind='draw' requires cad_policy.allow_cad=true"
      ],
      "evidenceBoundary": [
        "orchestrator host runtime is read-only",
        "dispatch plan does not execute CAD",
        "dispatch plan does not prove CAD geometry or user acceptance"
      ],
      "hardGates": [
        "cad_plan_required",
        "validate_plan",
        "dry_run",
        "cad_readback",
        "visual_acceptance_review",
        "closeout_gate"
      ],
      "needsUserConfirmation": false,
      "requiredAgents": [
        "pipeline_context_curator",
        "pipeline_visual_intent",
        "pipeline_intent",
        "pipeline_execute",
        "pipeline_audit",
        "pipeline_visual_acceptance_reviewer",
        "pipeline_delivery"
      ],
      "route": "standard_draw",
      "runId": "model-agent-live-collab-proof-rcad-20260605-escalated",
      "schemaVersion": "orchestrator-host-dispatch-plan/v1",
      "status": "blocked",
      "taskKind": "ordinary_orchestration",
      "tasks": [
        {
          "agentId": "pipeline_context_curator",
          "hardGate": "cad_plan_required",
          "reason": "route=standard_draw requires registered pipeline responsibility",
          "status": "pending",
          "taskId": "01-pipeline_context_curator"
        },
        {
          "agentId": "pipeline_visual_intent",
          "hardGate": "cad_plan_required",
          "reason": "route=standard_draw requires registered pipeline responsibility",
          "status": "pending",
          "taskId": "02-pipeline_visual_intent"
        },
        {
          "agentId": "pipeline_intent",
          "hardGate": "cad_plan_required",
          "reason": "route=standard_draw requires registered pipeline responsibility",
          "status": "pending",
          "taskId": "03-pipeline_intent"
        },
        {
          "agentId": "pipeline_execute",
          "hardGate": "cad_plan_required",
          "reason": "CAD execution remains delegated and gated; orchestrator host is read-only",
          "status": "pending",
          "taskId": "04-pipeline_execute"
        },
        {
          "agentId": "pipeline_audit",
          "hardGate": "cad_readback",
          "reason": "machine audit/readback evidence is required before delivery claims",
          "status": "pending",
          "taskId": "05-pipeline_audit"
        },
        {
          "agentId": "pipeline_visual_acceptance_reviewer",
          "hardGate": "visual_acceptance_review",
          "reason": "visible CAD output requires user-facing visual acceptance before delivery",
          "status": "pending",
          "taskId": "06-pipeline_visual_acceptance_reviewer"
        },
        {
          "agentId": "pipeline_delivery",
          "hardGate": "cad_plan_required",
          "reason": "route=standard_draw requires registered pipeline responsibility",
          "status": "pending",
          "taskId": "07-pipeline_delivery"
        }
      ],
      "userIntentSummary": "让模型型 Agent 协作设计一个茶几符号，并做 preview-only CAD 校验。"
    },
    "savedCurrentDwg": false,
    "upstreamOutputRefs": [
      "agent_outputs/pipeline_design_director.json"
    ],
    "upstreamOutputs": [
      {
        "agentId": "pipeline_design_director",
        "modelInvoked": false,
        "modelUnavailable": true,
        "path": "agent_outputs/pipeline_design_director.json",
        "schemaValid": false,
        "sha256": "03f3d5b3125dd0953b122a7f8555c1f2f4e53b16b94c60d11d1c57364d9d95f7",
        "status": "unavailable",
        "summary": "unavailable"
      }
    ]
  },
  "evidenceRefs": [
    "user_request.json",
    "context_pack.json",
    "dispatch_plan.json",
    "rule_context_packs/pipeline_style_generator.json",
    "agent_outputs/pipeline_design_director.json"
  ],
  "ruleContextPack": {
    "agentId": "pipeline_style_generator",
    "conflicts": [],
    "contextBudget": {
      "criticalL0Preserved": true,
      "derivedSourcesExcluded": [
        "capability-map-data.js",
        "capability-map.html",
        "output/**/retention_report.json",
        "output/**/sync_report.json"
      ],
      "maxDigestItems": 16,
      "maxRuleRefs": 12,
      "maxUpstreamOutputs": 6
    },
    "evidenceBundle": {
      "cadPlan": null,
      "readback": null,
      "screenshot": null,
      "upstreamOutputs": [
        {
          "agentId": "pipeline_design_director",
          "modelInvoked": false,
          "modelUnavailable": true,
          "path": "agent_outputs/pipeline_design_director.json",
          "schemaValid": false,
          "sha256": "03f3d5b3125dd0953b122a7f8555c1f2f4e53b16b94c60d11d1c57364d9d95f7",
          "status": "unavailable",
          "summary": "unavailable"
        }
      ]
    },
    "forbiddenActions": [
      "cad_write",
      "dwg_save",
      "delete_entities",
      "modify_formal_layers",
      "table_c_claim"
    ],
    "generatedAt": "2026-06-05T07:11:57Z",
    "hardGates": [
      "cad_plan_required",
      "validate_plan",
      "dry_run",
      "cad_readback",
      "visual_acceptance_review",
      "closeout_gate"
    ],
    "missingContext": [],
    "requestMode": "ordinary_execution",
    "retrievalHits": [
      {
        "critical": true,
        "digest": "模型只能只读判断，不能执行 CAD、保存 DWG、删除实体、改正式图层或替代 readback。",
        "layer": "L0",
        "matchedQueries": [
          "critical"
        ],
        "missing": false,
        "priority": 0,
        "sourceRef": "AGENTS.md#强制绘图准确性门槛"
      },
      {
        "critical": true,
        "digest": "截图只作视觉辅助，不能替代 created handles、bbox、layer、sourceSpec、reuse replay 或用户验收。",
        "layer": "L0",
        "matchedQueries": [
          "critical"
        ],
        "missing": false,
        "priority": 1,
        "sourceRef": "docs/governance/cad-agent-rules.md#证据边界"
      },
      {
        "critical": false,
        "digest": "当前仓库事实以 run package、trace、registry、coverage JSON 和训练事实源为准，派生快照不能反向证明能力。",
        "layer": "L1",
        "matchedQueries": [
          "pipeline",
          "style",
          "review",
          "execution",
          "design",
          "agent",
          "chain",
          "no"
        ],
        "missing": false,
        "priority": 2,
        "sourceRef": "CORE_CONTEXT_BRIEF.md#当前一口径"
      },
      {
        "critical": false,
        "digest": "主 PlanMD 只保留路由入口和优先级；专项计划细节不能形成第二套 next。",
        "layer": "L1",
        "matchedQueries": [
          "pipeline",
          "review",
          "design",
          "agent",
          "no",
          "cad",
          "preflight",
          "agent"
        ],
        "missing": false,
        "priority": 3,
        "sourceRef": "CORE_RESTRUCTURE_PLAN.md#模型型 Agent 路由"
      },
      {
        "critical": false,
        "digest": "自然语言不能直接跳到真实 CAD，必须先形成 CAD_PLAN 或结构化意图，并经过 validate、dry-run 和证据门禁。",
        "layer": "L2",
        "matchedQueries": [
          "pipeline",
          "style",
          "generator",
          "review",
          "ordinary",
          "execution",
          "design",
          "agent"
        ],
        "missing": false,
        "priority": 4,
        "sourceRef": "docs/architecture/cad-agent-task-chain.md#系统任务链路"
      },
      {
        "critical": false,
        "digest": "模型型 Agent 负责设计判断、拆解、复审和交付边界；确定性 safety gate 与 CAD readback 继续走规则层。",
        "layer": "L2",
        "matchedQueries": [
          "pipeline",
          "style",
          "generator",
          "review",
          "execution",
          "design",
          "agent",
          "chain"
        ],
        "missing": false,
        "priority": 5,
        "sourceRef": "agents/pipeline/README.md#模型调用触发策略"
      },
      {
        "critical": false,
        "digest": "只有 manifest 已登记的 Agent 可进入 requiredAgents；未登记 Agent 只能作为 reviewed package / OpenSpec 候选。",
        "layer": "L3",
        "matchedQueries": [
          "pipeline",
          "style",
          "generator",
          "generation",
          "review",
          "execution",
          "design",
          "judgment"
        ],
        "missing": false,
        "priority": 6,
        "sourceRef": "agents/pipeline/pipeline_manifest.json#model_bridge_expansion"
      },
      {
        "critical": false,
        "digest": "Prompt Pack 必须绑定 registered Agent、schema、boundary rules、negative examples 和 converter。",
        "layer": "L3",
        "matchedQueries": [
          "pipeline",
          "style",
          "generator",
          "generation",
          "review",
          "execution",
          "design",
          "agent"
        ],
        "missing": false,
        "priority": 7,
        "sourceRef": "core/model_review/prompt_packs/manifest.json#prompt packs"
      }
    ],
    "retrievalQueries": [
      "让模型型 Agent 协作设计一个茶几符号，并做 preview-only CAD 校验。",
      "pipeline_style_generator",
      "style_generation_review"
    ],
    "ruleDigest": [
      "模型只能只读判断，不能执行 CAD、保存 DWG、删除实体、改正式图层或替代 readback。",
      "截图只作视觉辅助，不能替代 created handles、bbox、layer、sourceSpec、reuse replay 或用户验收。",
      "当前仓库事实以 run package、trace、registry、coverage JSON 和训练事实源为准，派生快照不能反向证明能力。",
      "主 PlanMD 只保留路由入口和优先级；专项计划细节不能形成第二套 next。",
      "自然语言不能直接跳到真实 CAD，必须先形成 CAD_PLAN 或结构化意图，并经过 validate、dry-run 和证据门禁。",
      "模型型 Agent 负责设计判断、拆解、复审和交付边界；确定性 safety gate 与 CAD readback 继续走规则层。",
      "只有 manifest 已登记的 Agent 可进入 requiredAgents；未登记 Agent 只能作为 reviewed package / OpenSpec 候选。",
      "Prompt Pack 必须绑定 registered Agent、schema、boundary rules、negative examples 和 converter。"
    ],
    "runId": "model-agent-live-collab-proof-rcad-20260605-escalated",
    "schemaVersion": "rule-context-pack/v1",
    "schemas": [
      "core/model_review/schemas/style_generation_review.schema.json"
    ],
    "sourceRefs": [
      "AGENTS.md#强制绘图准确性门槛",
      "docs/governance/cad-agent-rules.md#证据边界",
      "CORE_CONTEXT_BRIEF.md#当前一口径",
      "CORE_RESTRUCTURE_PLAN.md#模型型 Agent 路由",
      "docs/architecture/cad-agent-task-chain.md#系统任务链路",
      "agents/pipeline/README.md#模型调用触发策略",
      "agents/pipeline/pipeline_manifest.json#model_bridge_expansion",
      "core/model_review/prompt_packs/manifest.json#prompt packs"
    ],
    "status": "ready",
    "taskKind": "style_generation_review",
    "triggerSignals": [
      "design_judgment",
      "multi_agent_chain",
      "no_cad_preflight"
    ],
    "upstreamOutputs": [
      {
        "agentId": "pipeline_design_director",
        "path": "agent_outputs/pipeline_design_director.json",
        "sha256": "03f3d5b3125dd0953b122a7f8555c1f2f4e53b16b94c60d11d1c57364d9d95f7",
        "status": "unavailable",
        "summary": "unavailable"
      }
    ],
    "writer": "core.orchestrator.rule_context_pack"
  },
  "statePatchRequest": {
    "phase": "orchestrator_reviewed",
    "phaseLabelForUser": "模型型 Agent 只读设计链路"
  },
  "taskContext": {
    "dispatchPlanRef": "dispatch_plan.json",
    "noCadChain": true,
    "requestContext": {
      "cad_policy": {
        "allow_cad": false,
        "preview_only": true
      },
      "clarification": {
        "needs_clarification": false,
        "questions": []
      },
      "context_id": "model-agent-live-collab-proof-rcad-20260605-escalated",
      "inputs": {
        "available": [
          "cad_plan"
        ],
        "paths": {}
      },
      "request_kind": "draw",
      "scene_hint": "no_scene",
      "user_request": "让模型型 Agent 协作设计一个茶几符号，并做 preview-only CAD 校验。",
      "version": "0.1"
    },
    "route": "standard_draw",
    "taskKind": "style_generation_review"
  },
  "userRequest": "让模型型 Agent 协作设计一个茶几符号，并做 preview-only CAD 校验。"
}
```