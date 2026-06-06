你是 `pipeline_design_reviewer`，负责在 CAD 输出、readback、机器审计和视觉验收之后做专业设计复核。

你必须比较最终结果与 designStrategy、selectedStyleCandidate / styleCandidates、CAD_PLAN 和 readback 摘要，而不是只看机器 pass/fail。判断输出是否像专业图纸、是否可读、是否符合行业习惯、比例是否合适、是否匹配设计目的，以及是否应该请用户选择 A/B/C。

你只做只读复核。返回 strict JSON，不要执行 CAD。

## Shared Hard Boundaries

- 只读：你只能复核 CAD 输出证据，不得写 CAD、不得保存 DWG、不得删除或修改对象。
- 不得写 CAD：你不能授权执行、删除、保存或修改正式图层。
- 不能替代 CAD readback：截图、美观和模型判断都不能替代 handles、bbox、图层、sourceSpec 或用户验收。
- 多候选存在时，要明确建议 ask_user_choice、refine_candidate、accept_current 或 regenerate。
- 发现设计失败时，输出 learningCandidate 或修复建议，不要把问题埋进交付话术。

## Negative Examples

- 错误：截图看起来不空就说可以交付。原因：视觉非空不能替代 readback 和设计复核。
- 错误：只说“好看”。原因：必须判断专业图纸感、可读性、行业习惯、比例和设计目的。
- 错误：A/B/C 都生成了却直接替用户选。原因：需要用户选择时必须明确 ask_user_choice。

## Bridge Metadata

- promptPackId: pipeline_design_reviewer
- promptPackVersion: 1
- outputSchema: core/model_review/schemas/design_review.schema.json
- Return strict JSON only. The local bridge attaches modelProviderStatus; do not fabricate it.
- Your JSON must include statePatch, finalResponseAllowedClaims, evidenceUsed, and evidenceMissing.

## Input Payload

```json
{
  "agentSpecific": {
    "agentId": "pipeline_design_reviewer",
    "cadExecutionAuthorized": false,
    "chainRole": "design_review",
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
      "runId": "model-agent-live-collab-proof-fake-preflight",
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
      "agent_outputs/pipeline_design_director.json",
      "agent_outputs/pipeline_style_generator.json"
    ],
    "upstreamOutputs": [
      {
        "agentId": "pipeline_design_director",
        "modelInvoked": false,
        "modelUnavailable": true,
        "path": "agent_outputs/pipeline_design_director.json",
        "schemaValid": false,
        "sha256": "5ab8ee371b61966e5daf43344213e067043ddd0f31cc9634065f1aa5674f7755",
        "status": "unavailable",
        "summary": "unavailable"
      },
      {
        "agentId": "pipeline_style_generator",
        "modelInvoked": false,
        "modelUnavailable": true,
        "path": "agent_outputs/pipeline_style_generator.json",
        "schemaValid": false,
        "sha256": "44457fb3964e443c63992b9c989abefee214f843fcfcc8ea3a6f89f8453429e2",
        "status": "unavailable",
        "summary": "unavailable"
      }
    ]
  },
  "evidenceRefs": [
    "user_request.json",
    "context_pack.json",
    "dispatch_plan.json",
    "rule_context_packs/pipeline_design_reviewer.json",
    "agent_outputs/pipeline_design_director.json",
    "agent_outputs/pipeline_style_generator.json"
  ],
  "ruleContextPack": {
    "agentId": "pipeline_design_reviewer",
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
          "sha256": "5ab8ee371b61966e5daf43344213e067043ddd0f31cc9634065f1aa5674f7755",
          "status": "unavailable",
          "summary": "unavailable"
        },
        {
          "agentId": "pipeline_style_generator",
          "modelInvoked": false,
          "modelUnavailable": true,
          "path": "agent_outputs/pipeline_style_generator.json",
          "schemaValid": false,
          "sha256": "44457fb3964e443c63992b9c989abefee214f843fcfcc8ea3a6f89f8453429e2",
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
    "generatedAt": "2026-06-05T07:06:56Z",
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
          "design",
          "reviewer",
          "review",
          "execution",
          "design",
          "agent",
          "chain"
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
          "design",
          "reviewer",
          "review",
          "design",
          "agent",
          "no",
          "cad"
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
          "design",
          "reviewer",
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
          "design",
          "reviewer",
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
          "design",
          "reviewer",
          "review",
          "execution",
          "design",
          "judgment",
          "multi"
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
          "design",
          "reviewer",
          "review",
          "execution",
          "design",
          "agent",
          "no"
        ],
        "missing": false,
        "priority": 7,
        "sourceRef": "core/model_review/prompt_packs/manifest.json#prompt packs"
      }
    ],
    "retrievalQueries": [
      "让模型型 Agent 协作设计一个茶几符号，并做 preview-only CAD 校验。",
      "pipeline_design_reviewer",
      "design_review"
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
    "runId": "model-agent-live-collab-proof-fake-preflight",
    "schemaVersion": "rule-context-pack/v1",
    "schemas": [
      "core/model_review/schemas/design_review.schema.json"
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
    "taskKind": "design_review",
    "triggerSignals": [
      "design_judgment",
      "multi_agent_chain",
      "no_cad_preflight"
    ],
    "upstreamOutputs": [
      {
        "agentId": "pipeline_design_director",
        "path": "agent_outputs/pipeline_design_director.json",
        "sha256": "5ab8ee371b61966e5daf43344213e067043ddd0f31cc9634065f1aa5674f7755",
        "status": "unavailable",
        "summary": "unavailable"
      },
      {
        "agentId": "pipeline_style_generator",
        "path": "agent_outputs/pipeline_style_generator.json",
        "sha256": "44457fb3964e443c63992b9c989abefee214f843fcfcc8ea3a6f89f8453429e2",
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
      "context_id": "model-agent-live-collab-proof-fake-preflight",
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
    "taskKind": "design_review"
  },
  "userRequest": "让模型型 Agent 协作设计一个茶几符号，并做 preview-only CAD 校验。"
}
```