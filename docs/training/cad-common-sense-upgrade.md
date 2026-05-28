# CAD 常识底座升级

最后更新：2026-05-28

本文记录一次训练期的小型系统升级：吸收外部 CAD / Agent 项目的方法论，但不 clone、不复制代码、不把外部项目变成运行依赖。升级目标是把“资料、图库、测试、证据声明”纳入现有训练体系，让基础物件常识先被系统化，再通过案例反馈校准。

后续更完整的资产化架构见 `docs/architecture/cad-asset-intelligence-architecture.md`。该架构把参考图库、系统自产图库、对象语法、检索、审计和晋升生命周期分开；本文仍只负责常识底座和训练期方法论口径。

## 目标

当前训练链路已经能做到：

```text
brief
  -> Visual-First / intent
  -> CAD_PLAN 或 case_script
  -> validate / dry-run
  -> CODEX_PREVIEW
  -> geometry_audit / agent_review
  -> feedback
```

但基础常识仍容易散在对话、案例脚本、`rules.md` 和截图自检里。以后不应反复让用户教“沙发要有靠背”“床要有床头”“桌子要有桌面”这类基础事实。常识底座升级要把这些内容变成可读、可查、可测、可声明边界的系统资产。

一句话：

```text
资料能沉淀
对象能查表
正确性能测试
能力能诚实声明
```

## 只吸收方法论

| 来源 | 吸收什么 | 不吸收什么 |
| --- | --- | --- |
| `llm-wiki-skill` | 原始资料先编译成持久 Markdown 知识，再 lint / audit / 修订 | 不把 RAG、wiki 工具链或外部代码直接搬进仓库 |
| `text-to-cad` / `step.parts` | 标准件和常见件先查 catalog；找不到时显式 fallback | 不把机械 STEP 标准件逻辑照搬成家装图库 |
| `CADTestBench` | 把 prompt 要求转成可执行检查，而不是只看参考图相似度 | 不引入它的 CadQuery / B-rep 测试栈作为当前依赖 |
| `CADCLAW` | 每个 CAD 声明都报告 checked / not_checked / assumptions | 不把 STEP assembly 检查等同于 AutoCAD 平面图证明 |

## 常识进入系统的标准

文件放进仓库不等于 Agent 已经学会。常识必须经过四步：

```text
source_note
  -> knowledge_summary
  -> object_or_rule_candidate
  -> executable_check
  -> evidence_boundary
```

| 阶段 | 说明 | 例子 |
| --- | --- | --- |
| `source_note` | 记录资料来源、授权边界、适用范围 | “来自用户给的脱敏块库说明” |
| `knowledge_summary` | 用项目自己的语言重写成可读知识 | “沙发俯视符号至少区分座面、靠背、扶手或座缝” |
| `object_or_rule_candidate` | 变成候选对象常识或场景规则 | `sofa` 的 parts、aliases、forbidden patterns |
| `executable_check` | 变成审计项或 benchmark case | 三人沙发必须有 2 条座缝 |
| `evidence_boundary` | 写清楚证明了什么、没证明什么 | 只证明 `CODEX_PREVIEW` 中该对象族，不证明施工图交付 |

没有进入 `executable_check` 的资料，只算参考知识；不能拿来证明系统会画准。

## 对象常识和训练反馈的分工

| 内容 | 应归入 | 说明 |
| --- | --- | --- |
| 沙发要有座面、靠背、扶手 / 座缝 | 常识底座 | 基础物件结构，不应靠用户反复训练 |
| 某款沙发参考图的弧线、厚薄、软硬层级 | 案例训练 | 需要截图、自检和用户目视反馈 |
| 家装里“参照不等于 clone”的口径 | 场景规则 | `agents/residential/rules.md` |
| “机器审计绿但视觉仍错不得交付” | 流水线规则 | `docs/training/README.md`、`pipeline-changelog.md` |
| created handles / 图层 / bbox 是否真实存在 | Core / 审计 | 机器证据，不靠常识文本替代 |

## 建议目录语义

本次只写架构口径，不要求立即创建所有目录。后续落地时可按现有仓库边界放置：

```text
libraries/
  objects/              # 基础对象定义、部件、别名、默认尺寸和符号语义
  blocks/               # 受控块 metadata、真实 block 的可用边界
  domain_presets/       # 场景常见对象和图层角色
  knowledge/            # 编译后的 CAD 常识 Markdown

projects/<case>/
  expected/             # 本案例 checklist / 参考目标
  runs/                 # 当轮 intent、execution、audit、review

docs/training/
  cad-common-sense-upgrade.md
  learning-loop.md
  pipeline-changelog.md
```

## 流水线影响

常识底座不替代现有链路，只在链路前后加硬边界。

```text
brief
  -> 查常识 / 查 catalog
  -> Visual-First / intent
  -> CAD_PLAN 或 case_script
  -> validate / dry-run
  -> CODEX_PREVIEW
  -> 常识测试 + 几何审计 + Agent 自检
  -> 交付反馈
```

| Agent | 新增责任 |
| --- | --- |
| `pipeline_context_curator` | 识别本轮涉及的常识、对象族、已有知识页和风险边界 |
| `pipeline_visual_intent` | 把常识转成 `visual_semantics`、parts 和 forbidden shortcuts |
| `pipeline_intent` | 在 intent/checklist 中引用基础对象常识，不把空矩形当对象 |
| `pipeline_audit` | 对象结构审计要能说明“常识项是否满足” |
| `pipeline_repair` | 先修违反常识的错误，再修风格微调 |
| `pipeline_delivery` | 用低噪声报告告诉用户：本轮证明了什么、还没证明什么、请看哪里 |
| `pipeline_learning_promoter` | 判断教训应进入知识、对象常识、场景规则、审计项还是仅留案例 |

## 反馈汇报升级

以后训练轮给用户的回复不能只堆 raw count、handle 数和“机器过了”。每次汇报必须帮助用户判断：该不该看、看哪里、为什么还不算通过、下一步怎么反馈。

### 必须回答的 6 个问题

| 问题 | 回复里怎么说 |
| --- | --- |
| 这轮是否可请你验收？ | 第一行直接写：`可验收` / `暂不交付` / `阻断` |
| 本轮相对上一轮解决了什么？ | 用用户语言说变化，不只写实体数 |
| 机器证据证明了什么？ | 把 audit、handles、截图角色翻译成结论 |
| 机器证据没证明什么？ | 明确 `not_checked` 和 assumptions |
| 你应该重点看哪里？ | 列 2-4 个目视检查点 |
| 你的反馈怎么写最有用？ | 给出一句式反馈入口，如“方向错 / 座缝多 / 靠背空” |

### 推荐回复模板

```text
本轮结论：可验收 / 暂不交付 / 阻断。

和上一轮相比：
- 修了什么用户能看见的问题。
- 还保留什么不确定点。

机器证据只证明：
- created handles / 图层 / bbox / gap / overlap / open endpoint 等。

它还没证明：
- 款式是否像参考图。
- 施工图级规范。
- 用户是否认可。

请你重点看：
1. 对象语义是否对。
2. 关键部件是否缺失或方向反了。
3. 线条是否干净、是否有多余白线。

如果不准，直接回一句：
“第 X 点不对，应该是……”
```

### 禁止的低信号汇报

- 只说“机器审计通过：0 gap / 0 overlap / 0 endpoint”，但不解释它和用户验收有什么关系。
- 只贴截图，不告诉用户看哪里。
- 把“实体数变多 / arc 变多”当成视觉改善结论。
- 机器审计绿就说“完成”，忽略 Agent 自检或用户目视。
- 普通训练回复默认带表 C、工程进度或大表格。

## 退出标准

本次架构文字升级完成后，只能声称：

- 已把 4 个外部项目的方法论写入训练架构。
- 已明确常识进入系统的路径。
- 已明确训练反馈汇报模板。

不能声称：

- 已建立自动常识学习系统。
- 已导入外部图库。
- 已提升表 C。
- 已证明沙发、床、桌子等对象全部画准。

后续如果要把常识真正变成能力，仍需选对象族、写结构化知识、写 audit/checklist，再通过测试和真实 CAD 证据逐步证明。
