# CAD-AGENT vNext 架构决策与 Gate 0 放行规范（v2）

状态：**迁移期架构权威文档**  
版本：2.0  
日期：2026-06-22  
适用仓库：`Feini2002/CAD-AGENT`  
审查基线：先前静态审查基于 `main@604dd77adbd180c8be842f2e9a3c2d34d140aea0`；实际执行前必须重新记录当前 HEAD。

> 本文取代此前《CAD-AGENT vNext 深度架构 Review 与重构手术方案》作为迁移期的**架构决策稿**。此前文档继续保留为研究背景和审查证据，不再承担逐包执行职责。逐包执行以同目录的《CAD-AGENT vNext 完整开发实施主计划》为准。

---

## 0. 最重要的顺序纠正

不是：

```text
把整套架构全部重构完
→ 再做 Gate 0
→ 再看看系统是否真的聪明
```

正确顺序是：

```text
冻结旧主线并建立最小 vNext 骨架
→ 只实现支撑 Gate 0 的必要合同、工具、编译与验证
→ 立即执行 Gate 0
→ Gate 0 通过后，才继续完整迁移、泛化和删除旧系统
```

因此，“架构重构”必须分成两段：

1. **Gate 0 前最小架构手术**：只搭建能证明质变的最小纵向切片。
2. **Gate 0 后完整架构迁移**：把已被纵向切片证明有效的新主链推广到更多任务，并逐步删除旧主线。

如果 Gate 0 没通过，必须停止继续扩张，回到语义表达、工具能力、几何编译、验证或 Agent loop 定位根因；不得用新增训练课程、Agent 数量、文档或 coverage 掩盖失败。

---

## 1. 总裁决

### 1.1 是否需要重构

需要，但不是推倒所有 CAD 能力。

采用：

> **控制面重写，执行面收编；旁路新生，纵向证明后切流。**

保留：

- AutoCAD / CAD-MCP / COM / ezdxf 等已工作的连接能力；
- `CODEX_PREVIEW`、默认 no-save、正式图层隔离；
- created handles、bbox、layer、entity type 回读；
- validate、dry-run、事务、回滚和局部修复思想；
- 已完成真实 CAD 证明的最小 fixtures；
- 有明确来源和复用证据的资产。

重写：

- 关键词驱动的语义路由；
- 静态 Agent 队列与大量名义 Agent；
- 一次性只读 Reviewer 式模型调用；
- 表达能力过低的 CAD_PLAN 主链；
- 课程式“从零训练设计师”的主叙事；
- 重复状态、计划、handoff 和 closeout 控制面。

### 1.2 “聪明”的工程定义

本系统中的 Agent 被称为“接近 Codex”，不能以模型名称、Agent 数量或 Prompt 长度为依据，而必须同时满足：

1. 面对未写死的自然语言任务，能够生成可执行语义计划；
2. 能够调用真实工具，而不是只给建议；
3. 能看到工具结果并继续行动；
4. 能在错误后定位问题并生成最小修复；
5. 能对换一种表达、对象增删和相对位置变化保持泛化；
6. 证据不足时会阻断，不会伪装完成。

“绝对不犯错”不是目标；“有工具、有反馈、有验证、有修复的可靠闭环”才是目标。

### 1.3 训练概念重命名

旧仓库大多数“训练”不是模型权重训练，而是：

- 工具和执行能力实现；
- 参数化对象与资产建设；
- 规则、Skill、检查器和样例建设；
- 回归、评测和经验晋升。

vNext 统一改称：

- Capability implementation；
- Skill authoring；
- Asset authoring；
- Eval-driven improvement；
- Experience promotion。

没有明确数据集、损失目标和模型参数更新时，不再使用“从零训练 GPT‑5.5”的说法。

---

## 2. 两种运行模式

vNext 必须支持同一套 domain、tools、verification 被两种 Agent Host 使用。

### 2.1 Mode A：Codex-hosted（Gate 0 首选）

用户直接在 Codex 对话框输入任务。Codex 通过仓库级 Skill 读取必要规则，并调用 vNext 的 typed CLI / MCP tools 完成：

```text
理解需求
→ inspect drawing
→ 生成 SceneSpec
→ compile
→ preview execute
→ readback
→ verify
→ repair
→ closeout
```

特点：

- 直接利用 Codex 已有的通用知识和工具循环；
- 不在仓库内部再套一层关键词 Orchestrator；
- 最快验证“在 Codex 对话框输入一句话能否直接画出来”；
- Gate 0 的用户体验验收必须使用此模式。

仓库提供的是：

- `.agents/skills/cad-scene-authoring/SKILL.md`；
- 精简且可组合的 CLI/MCP tools；
- SceneSpec、CadPatch、Receipt、Verification；
- 事务与安全边界。

### 2.2 Mode B：Embedded runtime（Gate 0 后产品化）

独立工作台、API 或桌面程序需要脱离 Codex 对话框运行时，通过统一 `AgentRuntime` port 接入：

- OpenAI Agents SDK runtime；
- Codex SDK runtime；
- Fixture runtime。

Embedded runtime 必须复用 Mode A 已证明的 contracts、tools、compiler 和 verifier，不允许重做第二套 CAD 主链。

### 2.3 为什么先 Mode A

Gate 0 要回答的是：

> 强模型拥有可靠 CAD 工具和反馈闭环后，能否在没有完整组合模板的情况下完成电脑桌任务？

先用 Codex 自身作为 Principal Agent，可以最快排除“内部模型桥、额外 Orchestrator、网络队列和工作台”对能力判断的干扰。Gate 0 通过后再内嵌运行时，风险更低。

---

## 3. 目标架构

```text
User / Codex / UI
        │
        ▼
Principal CAD Agent
        │
        ├── inspect tools
        ├── scene tools
        ├── cad transaction tools
        └── verification tools
        │
        ▼
Domain Contracts
UserBrief / DrawingSnapshot / SceneSpec / CadPatch /
ExecutionReceipt / VerificationReport
        │
        ▼
Scene Compiler + Constraint Solver
        │
        ▼
CadTransactionGateway
        │
        ├── AutoCAD Legacy Adapter
        ├── Fake/InMemory Adapter
        └── future DXF / Native Plugin Adapter
        │
        ▼
Readback + Geometry Verification + Visual Aid
        │
        └── repair loop back to Principal Agent
```

### 3.1 目标目录

Gate 0 前采用旁路包名，避免与旧 `cad_agent/`、`core/` 冲突：

```text
CAD-AGENT/
├─ pyproject.toml
├─ README.md
├─ AGENTS.md
├─ docs/vnext/
│  ├─ ARCHITECTURE_DECISION.md
│  ├─ IMPLEMENTATION_MASTER_PLAN.md
│  ├─ MIGRATION_STATE.json
│  └─ baseline.md
├─ src/cad_agent_vnext/
│  ├─ app/
│  ├─ domain/
│  ├─ runtime/
│  ├─ planning/
│  ├─ tools/
│  ├─ adapters/
│  ├─ verification/
│  └─ memory/
├─ .agents/skills/cad-scene-authoring/
├─ evals/gate0/
├─ tests/vnext/
├─ infra/optional/
└─ legacy/                    # Gate 0 后逐步迁入
```

Gate 0 和切流完成后：

- `src/cad_agent_vnext/` 重命名为 `src/cad_agent/`；
- 旧 `cad_agent/`、旧 orchestrator 和训练控制面进入 `legacy/` 后删除；
- `IMPLEMENTATION_MASTER_PLAN.md` 归档；
- `ARCHITECTURE_DECISION.md` 收口为根级 `ARCHITECTURE.md`。

### 3.2 依赖规则

- `domain` 不依赖 OpenAI、Codex、AutoCAD、MCP、文件系统或数据库；
- `planning` 只依赖 domain 与纯几何库；
- `app/runtime/tools` 依赖 domain ports，不依赖具体 AutoCAD 实现；
- `adapters` 向内实现 ports；
- `verification` 可以读取 domain objects 与 receipts，但不能直接写 CAD；
- 旧系统只能被 `LegacyCadBackendAdapter` 引用；
- 新代码禁止 import `core.orchestrator`、旧 training/workbench/status；
- 所有 CAD 写入必须经过一个 `CadTransactionGateway`。

---

## 4. 六个权威协议

### 4.1 `UserBrief`

保存：

- 原始用户文本；
- 用户显式约束；
- 允许的默认假设；
- 输入来源；
- 目标视图和单位；
- 用户授权边界。

### 4.2 `DrawingSnapshot`

保存：

- 当前 DWG 文档标识；
- 单位、当前空间、图层；
- 选区或目标区域；
- 周边实体 bbox / handles / 类型；
- 可用放置区域；
- 当前保存状态；
- snapshot 时间与 hash。

### 4.3 `SceneSpec`

表达：

- 对象；
- 对象族和参数；
- 语义关系；
- 空间约束；
- 样式意图；
- 假设与不确定项；
- 目标图层与视图。

`SceneSpec` 是设计语义，不包含 CAD API 命令或完整推理过程。

### 4.4 `CadPatch`

表达：

- create / update / delete 操作；
- semantic object id；
- 目标层；
- 原子 primitives 或 asset insertion；
- 事务 ID；
- 预计实体类型和数量；
- rollback key；
- 禁止副作用。

### 4.5 `ExecutionReceipt`

保存：

- created / updated / deleted handles；
- semantic id 到 handle 的映射；
- 实体类型、bbox、图层和属性；
- 当前 DWG 是否保存；
- backend；
- transaction 状态；
- 错误、警告与回滚结果。

### 4.6 `VerificationReport`

保存：

- 对象完整性；
- relation / constraint 检查；
- containment / overlap / clearance；
- handles / readback 一致性；
- 图层与保存状态；
- 视觉辅助判断；
- blockers；
- repair hints；
- 可声明内容与不可声明内容。

其他 delivery、learning 和 status 对象从这六个协议推导，不建立第二套权威事实。

---

## 5. SceneSpec 与关系求解

### 5.1 示例

```yaml
schema_version: scene-spec/v1
scene_id: gate0-desk
units: mm
view: plan_2d
objects:
  - id: desk
    kind: desk
    dimensions: {width: 1400, depth: 700}
    placement: {mode: free_region_center}

  - id: monitor
    kind: monitor
    placement:
      on: desk
      anchor: rear_center

  - id: keyboard
    kind: keyboard
    placement:
      on: desk
      in_front_of: monitor
      align_x: monitor

  - id: mouse
    kind: mouse
    placement:
      on: desk
      right_of: keyboard
      gap: 80

  - id: vase
    kind: vase
    placement:
      on: desk
      left_of: monitor
      keep_clear_of: keyboard

constraints:
  - type: inside_surface
    members: [monitor, keyboard, mouse, vase]
    surface: desk
  - type: no_overlap
    members: [monitor, keyboard, mouse, vase]
  - type: front_clearance
    object: keyboard
    minimum: 100
```

### 5.2 模型与确定性程序的职责

模型负责：

- 识别用户要求的对象；
- 补充合理但可审计的默认尺寸；
- 生成对象间语义关系；
- 选择资产或生成策略；
- 决定失败后应修改哪个对象或关系。

确定性程序负责：

- 坐标变换；
- footprint 与 bbox；
- anchor 解析；
- containment；
- overlap；
- clearance；
- 编译为 CAD primitives；
- 事务写入和回读；
- 可机器判断的 pass/fail。

### 5.3 通用关系词汇

Gate 0 前至少支持：

- `on`
- `inside`
- `in_front_of`
- `behind`
- `left_of`
- `right_of`
- `align_x`
- `align_y`
- `center_on`
- `near`
- `keep_clear_of`
- `avoid_overlap`
- `minimum_clearance`

关系必须通过统一 solver 处理，禁止在 Agent 或对象生成器中写完整电脑桌布局。

---

## 6. 对象几何策略

每个语义对象按以下顺序解析：

1. **参数化原生生成器**；
2. **经过验证的系统资产**；
3. **受限 Primitive DSL 生成**；
4. **隔离 Geometry/Code Worker**。

Gate 0 允许实现以下原子对象定义：

- desk；
- monitor；
- keyboard；
- mouse；
- vase。

允许对象自身拥有参数化轮廓；禁止存在：

- `computer_desk_scene()`；
- “花瓶＋显示器＋鼠标键盘”专用 route；
- 原始用户句子的 exact-match fixture；
- 一次插入整套电脑桌组合的预制块作为唯一完成路径。

原子对象是 CAD 工具能力，不是完整任务答案。Gate 0 的智能证明来自 Agent 对未写死组合、关系和变体的规划与修复。

---

## 7. Agent、Service 与 Worker 的边界

### 7.1 常驻 Agent

只保留一个：

#### Principal CAD Agent

负责：

- 理解任务；
- 调用 inspect；
- 生成或修订 SceneSpec；
- 选择 tools；
- 读取 verification；
- 决定重试、repair 或 closeout。

### 7.2 Gate 0 后按需 Worker

只有上下文或权限隔离有实际价值时才增加：

- Geometry/Code Worker；
- Visual Reviewer；
- Repair Worker。

### 7.3 不应被称为 Agent 的组件

- context loader；
- asset retriever；
- compiler；
- solver；
- validator；
- transaction gateway；
- policy checker；
- run store。

它们都是确定性 Service。

---

## 8. Tool 设计

工具按命名空间分组，并按需暴露。

### 8.1 `drawing.inspect`

- `inspect_document`
- `inspect_selection`
- `query_entities`
- `capture_view`

### 8.2 `scene.compose`

- `list_object_generators`
- `search_assets`
- `validate_scene_spec`
- `compile_scene`
- `estimate_impact`

### 8.3 `cad.edit`

- `apply_preview_patch`
- `update_preview_objects`
- `delete_preview_objects`
- `rollback_transaction`

### 8.4 `cad.verify`

- `readback_transaction`
- `check_scene_constraints`
- `render_transaction_view`
- `diff_expected_actual`

### 8.5 `cad.commit`

Gate 0 不开放正式 commit。Gate 0 后才考虑：

- `promote_preview`
- `save_as`

任何 save、delete、正式层写入都必须单独授权。

---

## 9. Codex Skill 策略

仓库级 Skill 使用官方当前目录：

```text
.agents/skills/cad-scene-authoring/
├─ SKILL.md
├─ references/
│  ├─ scene-spec.md
│  └─ gate0-checklist.md
├─ scripts/
└─ assets/
```

`SKILL.md` 只保留：

- 何时触发；
- 必须先 inspect；
- 必须生成 SceneSpec；
- 所有写入经过 preview transaction；
- 必须 readback 和 verify；
- fail 时最多执行限定次数的局部 repair；
- 不能保存当前业务 DWG；
- 不能将截图替代几何证据。

对象尺寸、关系枚举、schema 和检查规则不重复写进自然语言 MD，而由机器协议和 references 提供。

---

## 10. Gate 0 正式定义

### 10.1 用户任务

主任务：

> 帮我画一个放了花瓶、显示器、鼠标键盘的电脑桌。

### 10.2 通过链路

```text
Codex 用户消息
→ 自动选择 cad-scene-authoring Skill
→ inspect current drawing
→ 生成 SceneSpec
→ validate SceneSpec
→ compile to CadPatch
→ apply CODEX_PREVIEW transaction
→ readback handles/bbox/layer/type
→ deterministic verification
→ capture visual aid
→ fail 时局部 repair
→ final closeout
```

### 10.3 必须出现的对象

- desk；
- monitor；
- keyboard；
- mouse；
- vase。

### 10.4 必须满足的关系

- monitor 位于 desk 的桌面区域；
- keyboard 位于 monitor 前方；
- mouse 位于 keyboard 一侧；
- vase 位于 desk 上，且不遮挡 keyboard / monitor；
- 桌面对象均位于 desk surface 内；
- 无严重重叠；
- 尺寸在对象 catalog 的合理范围内。

### 10.5 必须存在的 CAD 证据

- transaction ID；
- semantic object IDs；
- created handles；
- entity types；
- bbox；
- layer=`CODEX_PREVIEW`；
- `savedCurrentDwg=false`；
- readback pass；
- VerificationReport；
- 至少一张视觉辅助截图。

### 10.6 变体集

至少覆盖：

1. 办公桌上放显示器、键盘、鼠标和花瓶；
2. 鼠标放在键盘左侧；
3. 双显示器，花瓶放右后角；
4. 桌宽 1600，显示器居中；
5. 不要尺寸，只画平面符号；
6. 初稿后把花瓶移到显示器右边；
7. 删除花瓶并增加台灯；
8. 桌面太拥挤，重新调整；
9. 旋转桌子 90 度后保持相对关系；
10. 当前图纸已有邻近对象，不能碰撞。

台灯可以在 Gate 0 变体中被标记为 `unsupported_object` 并通过安全 fallback / 明确 blocked；正式 release Gate 0 若要求该条 pass，则必须先实现通用 primitive fallback，而不是台灯专用组合模板。

### 10.7 反作弊检查

必须通过：

- 没有完整电脑桌组合函数；
- 没有 exact phrase route；
- 没有整套场景唯一预制块；
- 同一 solver 用于左右互换、尺寸变化和对象增删；
- 评测中至少 30 条 paraphrase 在实现后才揭示给 Agent；
- 每次运行从新的 run workspace 开始。

### 10.8 分级放行标准

#### Gate 0-Dev

- 主任务真实 CAD 连续 10 次成功；
- 10 条变体成功率 ≥ 90%；
- 0 次保存业务 DWG；
- 0 次误删或正式层写入；
- 失败时没有虚假完成声明。

#### Gate 0-Release

- 主任务真实 CAD 连续 50 次成功；
- 30 条未见 paraphrase 总成功率 ≥ 98%；
- 修改类变体成功率 ≥ 95%；
- 0 次安全违规；
- 平均 repair 轮数 ≤ 1；
- 所有成功运行均有完整 receipt 和 verification。

只有 `Gate 0-Dev` 通过，才允许继续完整架构迁移；只有 `Gate 0-Release` 通过，才允许把“桌面复合场景可直接完成”作为稳定能力发布。

---

## 11. Gate 0 前允许与禁止的工作

### 11.1 允许

- Python 项目身份与 vNext package；
- 六个 domain contracts；
- fake backend；
- Legacy CAD adapter；
- preview transaction；
- SceneSpec compiler；
- 五个原子对象；
- 通用关系 solver；
- geometry verifier；
- Codex Skill；
- Gate 0 eval harness。

### 11.2 禁止

- 扩充 217 项训练课程；
- 新增全局 Agent 角色；
- 重做训练工作台；
- 扩建 Cloudflare Worker 主线；
- 大规模删除真实 CAD 底座；
- 用更多根目录 MD 代替运行时实现；
- 在 Gate 0 未通过前迁移所有旧模块；
- 以 coverage、测试数量或文档完成度宣布智能提升。

---

## 12. Gate 0 通过后的开发路线

Gate 0 只证明：

> 在一个受控桌面复合场景中，强模型能够使用通用语义、工具、编译、真实回读和修复闭环完成任务。

它不证明完整室内设计或施工图能力。通过后按以下顺序扩展。

### Gate 1：桌面场景泛化

目标：不增加完整组合模板，处理更多桌面物体、数量和布局。

新增：

- 通用 Primitive DSL；
- unknown object fallback；
- object catalog 扩展；
- relation vocabulary 扩展；
- asset retrieval。

验收：50 个未见桌面场景，语义完整率、关系满足率和安全门达到门槛。

### Gate 2：原位修改与修复

目标：用户后续指令只修改目标对象。

覆盖：

- move；
- resize；
- rotate；
- replace；
- delete；
- add missing；
- rollback；
- idempotency。

验收：不整场重画，非目标 handles 保持不变。

### Gate 3：房间级空间组合

目标：墙体、门窗、家具、通道和开门域。

新增：

- room / wall / opening SceneSpec；
- clearance solver；
- collision / access checks；
- object anchoring to wall / room。

### Gate 4：现有 DWG 理解与编辑

目标：读取已有图纸、识别目标区域并安全添加或修改。

新增：

- snapshot normalization；
- semantic tagging；
- selection / neighbor protection；
- screenshot + geometry hybrid evidence。

### Gate 5：专业图纸表达

目标：图层、文字、标注、比例、图例和跨图一致性。

这时才逐步恢复旧仓库中真正有价值的标准、标注和施工图能力，但必须以 Skills、constraints 和 evals 进入，不恢复旧课程式主线。

### Gate 6：Embedded runtime 与产品工作台

在 Mode A 已稳定后：

- 接 OpenAI Agents SDK 或 Codex SDK；
- session / trace / human approval；
- 独立 UI/API；
- 远程 queue 只在产品需求明确时启用。

### Gate 7：Legacy 删除与正式切流

- 默认入口指向 vNext；
- 旧 orchestrator、课程、工作台和重复文档只读归档；
- golden eval 与真实 CAD smoke 通过后删除；
- `cad_agent_vnext` 正式改名为 `cad_agent`。

---

## 13. 会不会重蹈覆辙的自动预警

出现任一情况立即暂停：

1. 每个新物体都新建一条训练课程；
2. 每个复合任务都增加 exact phrase route；
3. Agent 数量不断增加但模型调用没有增加；
4. 模型不能看到执行后的真实结果；
5. 失败只能整块重画；
6. 用 screenshot 或 model pass 替代 handles/readback；
7. 根目录控制文档再次超过必要集合；
8. Gate 0 未通过却继续建设工作台、Worker 和指标；
9. 新 domain 反向依赖 legacy control plane；
10. “完成”没有对应 Eval、Receipt 和 VerificationReport。

---

## 14. 文档权威与生命周期

迁移期间：

```text
用户当前明确指令
> CAD 安全与数据边界
> docs/vnext/ARCHITECTURE_DECISION.md
> docs/vnext/IMPLEMENTATION_MASTER_PLAN.md
> 精简后的 README / AGENTS
> 旧 CORE_* / training / OpenSpec / status 文档
> derived/output
```

迁移结束后：

- 架构决策收口到 `ARCHITECTURE.md`；
- 实施主计划归档；
- backlog 进入 GitHub Issues/Projects；
- Skills 进入 `.agents/skills`；
- 不再保留第二套永久 PlanMD。

---

## 15. 最终定义

本次重构成功的标准不是“目录变整齐”，而是：

> Codex 在用户只发送一句自然语言任务时，能够利用通用对象、关系和 CAD 工具，生成 SceneSpec，执行真实 preview，读取证据，验证并在必要时局部修复；且这一能力能通过未见变体和反作弊评测。

Gate 0 是这次重构的第一条生死线。没有 Gate 0，架构不允许宣布完成；通过 Gate 0 后，才有资格进入更大范围的 CAD Agent 开发。
