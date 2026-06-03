## Context

当前系统已经有 `a_to_a_task_contract`，能识别系统资产沉淀、资产 DWG 仓库式布局和视觉布局复审，并能在缺少固定责任 Agent 输出时阻断 `workflow_dispatch`。这个底座解决了“哪些 Agent 必须来”的第一层问题，但还没有解决主 Agent 自身的责任显式化：

- 主 Agent 没有机器可读字段说明自己的身份、使命、任务理解和责任边界。
- 加派 Agent 目前主要由固定 `taskKind -> requiredAgents` 映射决定，缺少“为什么加派 / 为什么不加派”的审计链。
- 未登记的新 Agent 需求没有统一出口，容易在口头方案里被当作已经生效的能力。
- 已有 visual layout reviewer 的 pass 字段和测试期待存在漂移风险，主 Agent 缺少显式 hard gate 自检来发现这类漂移。

本设计在既有 A-to-A TaskContract 上叠加一层“主 Agent 自检与加派决策”，不重做工作流、不新增真正可执行 Agent、不改变真实 CAD 验证门槛。

## Goals / Non-Goals

**Goals:**

- 让主 Agent 在高风险任务前显式声明：我是主编排 Agent、我要完成什么、我不能替谁背书、我这轮是否需要加派 Agent。
- 将动态加派分成两类：已登记 Agent 可加入本轮 `requiredAgents`；未登记 Agent 只能进入 reviewed-package / OpenSpec 候选。
- 让 `workflow_dispatch` 能阻断主 Agent 自检缺失、加派理由缺失、未登记 Agent 被当成已生效、或被阻断仍尝试完成交付的情况。
- 将主 Agent 的自检、加派决策、缺失 Agent、失败 gate 和交付边界一起写入报告，供后续状态汇报、训练沉淀和回归测试读取。
- 修正视觉布局复审字段漂移，把 readability 类字段纳入同一 hard gate 和检查脚本。

**Non-Goals:**

- 不创建真正的新全局 Agent。新 Agent 只记录为 `additionalAgentRequests`，后续必须通过 reviewed package / OpenSpec。
- 不让主 Agent 亲自替代 asset governor、visual layout reviewer、reuse auditor、CAD readback 或用户验收。
- 不保存用户当前业务 DWG，不改正式图层，不删除实体。
- 不提升表 C，不声称真实 CAD 几何能力已增强。
- 不把人格化“意识”当成证据；系统里的“有意识”只等价于可验证的身份、目标、边界、决策和责任分发记录。

## Decisions

### Decision 1: 自检放在 `a_to_a_task_contract`，不另建主 Agent 执行器

主 Agent 自检应作为合同字段生成，而不是新增一个会执行任务的 Agent。字段建议：

```json
{
  "mainAgentSelfCheck": {
    "status": "pass",
    "identity": "pipeline_orchestrator_main_agent",
    "mission": "classify request, build task contract, dispatch responsible agents, block unsupported completion claims",
    "taskUnderstanding": {
      "taskKind": "asset_dwg_layout",
      "triggeredSemantics": ["system_asset", "visual_layout"],
      "riskLevel": "high"
    },
    "responsibilityBoundary": {
      "mayDispatchAgents": true,
      "mayExecuteCad": false,
      "mayClaimCompleteWithoutAgentOutputs": false
    },
    "knownLimits": [
      "cannot replace CAD readback",
      "cannot approve visual layout without visual_layout_review",
      "cannot activate unregistered agents"
    ],
    "decisionBasis": [
      "request semantics",
      "semantic asset route",
      "pipeline manifest",
      "hard gate definitions",
      "agent output status"
    ]
  }
}
```

理由：合同已经是阻断 `workflow_dispatch` 的中心入口，主 Agent 自检放在这里最容易被每个编排报告、测试和治理脚本复用。

替代方案：新增 `core/orchestrator/main_agent_awareness.py` 独立模块。优点是文件更小；缺点是早期会分散合同逻辑。可以在字段稳定后再拆。

### Decision 2: 动态加派只允许使用 manifest 已登记 Agent

`dispatchDecision` 负责说明本轮 Agent 派发：

```json
{
  "dispatchDecision": {
    "status": "blocked",
    "baseRequiredAgents": ["pipeline_asset_governor"],
    "registeredAdditionalAgents": [
      {
        "agentId": "pipeline_visual_layout_reviewer",
        "reason": "request asks for warehouse shelf layout and retrieval path readability"
      }
    ],
    "effectiveRequiredAgents": ["pipeline_asset_governor", "pipeline_visual_layout_reviewer"],
    "additionalAgentRequests": [
      {
        "requestedAgentId": "pipeline_asset_polish_reviewer",
        "reason": "repeated asset DWG polish failures need a specialized reviewer",
        "status": "needs_reviewed_package"
      }
    ],
    "blockedUntilAgentsReport": true,
    "reviewedPackageRequired": true
  }
}
```

已登记 Agent 可以加入 `effectiveRequiredAgents` 并触发 missing / failed gate 阻断。未登记 Agent 只进入 `additionalAgentRequests`，不能进入 `effectiveRequiredAgents`，不能让系统声称已加派成功。

理由：这既满足“主 Agent 能判断要不要加派”，又保护 Agent 体系不被临场创造的角色污染。

### Decision 3: `workflow_dispatch` 只消费合同结果，不重复实现判断

`orchestrate_request()` 继续调用 `build_a_to_a_task_contract()`。若合同出现以下任一情况，dispatch 必须 blocked：

- `mainAgentSelfCheck.status != pass`
- `dispatchDecision.status == blocked`
- 有 `missingRequiredAgents`
- 有 `failedHardGates`
- 有未登记 Agent 被加入 `effectiveRequiredAgents`
- `additionalAgentRequests` 非空且被标记为 `required_now`
- `deliveryBoundary.mayClaimComplete == false`

理由：避免 workflow dispatch 成为第二套规则引擎，只负责执行合同给出的阻断结论。

### Decision 4: Manifest 成为主 Agent 可派发边界

`agents/pipeline/pipeline_manifest.json` 增加：

- `orchestration.main_agent_identity`
- `orchestration.dynamic_dispatch_policy`
- `orchestration.unregistered_agent_request_policy`
- `orchestration.forbidden_patterns.unregistered_agent_activated`

主 Agent 自检必须引用 manifest 中已登记 Agent 列表。若 manifest 缺少主 Agent 身份配置，合同降级为 blocked，提示治理文件不同步。

理由：Agent 注册表是事实源；主 Agent 不能靠代码里硬编码的幻想角色扩大权力。

### Decision 5: 视觉布局复审补齐 readability 字段

将 `layoutReadabilityAcceptable` 纳入 `VISUAL_LAYOUT_CHECKS`、manifest `visual_layout_review.requires`、测试和 A-to-A gate check。`retrievalPathReadable` 仍保留，但不能单独替代整体 layout readability。

理由：已有测试已经表达该期待，设计层明确收口，避免视觉布局“截图非空 / 货架存在”冒充可读。

## Risks / Trade-offs

- 主 Agent 自检字段变多，报告更长 → 仅在合同报告中机器化保留，最终用户回复仍按低噪声模板摘要。
- 动态加派增加误阻断可能 → 初期只对高风险语义启用：系统资产沉淀、资产 DWG 布局、视觉布局复审、复用 verified 声明等。
- Manifest 与代码规则可能漂移 → 用 `scripts/run_a_to_a_orchestration_gate_check.py` 同时检查 manifest、合同和 dispatch。
- 未登记 Agent 只能进入候选，短期不能立刻解决所有新角色需求 → 这是刻意的安全边界；真正新增 Agent 走 reviewed package / OpenSpec。
- 自检可能被误读为“主 Agent 有人格” → 文档明确“意识”是工程上的自我模型、责任边界和决策依据，不是替代证据。

## Migration Plan

1. 在单元测试中先表达新合同字段和阻断行为。
2. 扩展 `a_to_a_task_contract.py`，生成 `mainAgentSelfCheck` 和 `dispatchDecision`。
3. 扩展 `workflow_dispatch.py` 的 blocked reason 展示，但不新增第二套规则。
4. 更新 `pipeline_manifest.json` 的主 Agent 身份和动态派发策略。
5. 更新 A-to-A gate check 脚本，检查 manifest、合同、动态派发、未登记 Agent 候选和 visual readability。
6. 更新架构文档、全局规则、短上下文、状态和 changelog。
7. 运行 focused 单测、workflow dispatch 回归、A-to-A gate check、OpenSpec validate。若不涉及真实 CAD 写入，本轮证据边界声明为 no-CAD orchestration hardening。

Rollback 策略：若新字段导致误阻断，可保留字段但将动态加派策略降级为 observation，只用固定 `requiredAgents` 映射；恢复旧阻断行为不影响 CAD 数据和 DWG。

## Open Questions

- 第一版是否只在 `taskKind != ordinary_orchestration` 时强制 `mainAgentSelfCheck.status=pass`，普通编排先记录 observation？推荐：是，降低回归面。
- 是否把 `pipeline_orchestrator` 的 agent.json 也升级为主 Agent 身份事实源？推荐：若文件已存在则同步；若不存在，先以 manifest 为事实源。
- 是否新增专门的 `main_agent_awareness` 测试文件？推荐：先放在 `test_a_to_a_task_contract.py`，字段稳定后再拆。
