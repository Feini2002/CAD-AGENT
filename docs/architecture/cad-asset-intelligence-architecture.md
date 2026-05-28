# CAD-ASSET-INTELLIGENCE-ARCH-01

最后更新：2026-05-29

本文是一次架构包，不是能力证明包。它把“参考图库 -> 系统自产图库 -> 检索 / 生成 / 审计 / 晋升”的方案写成系统级设计，并已落地基础设施：目录、schema、轻量 `retrieval_pack`、自动 raw intake、Agent 职责、训练 intake 模板和晋升 gate。后续仍需跑对象族试点和真实 CAD 证据。

一句话：

```text
Catalog-first, but not template-only.
```

系统要减少 LLM 凭空构思 CAD 对象，但不能退化成“只会套旧图库”。正确方向是把标准图库和用户截图变成对象语法、参数化对象族、可执行审计、训练反馈和证据边界。

## 本包完成什么

本包完成的是架构层固化：

- 定义参考图库和系统自产图库的边界。
- 定义目录分层、调用链、Agent 职责和晋升生命周期。
- 定义生产模式和探索模式，避免图库锁死创造性。
- 定义什么能声称，什么不能声称。
- 给后续 schema、测试、RAG、Agent 编排和训练案例提供主设计。

本包当前不完成这些事：

- 不导入外部 CAD 图库、DWG、厂商块或图片包。
- 允许后续把用户确认要随 git 迁移的原始标准图库放入根目录 `standard_cad_library_raw/`，但该目录仍只是 raw reference input，不是系统能力。
- 不建立真实 RAG / embedding 检索系统。
- 不完成 schema 全量严格验证、RAG、自动晋升写回或对象族验证。
- 不改表 C、不新增真实 CAD 几何证据。
- 不声明系统已经会稳定生成沙发、床、桌子等对象。

所以，生成本架构包只算完成“方案固化”。它不是整套方案完成。

## 架构目标

目标不是做一个素材仓库，而是做 CAD 对象能力资产管线：

```text
reference_library
  -> knowledge
  -> benchmarks
  -> system_library
  -> retrieval_pack
  -> OBJECT_SPEC / SYMBOL_SPEC / visual_parts
  -> CAD_PLAN
  -> CODEX_PREVIEW
  -> audit / feedback
  -> promotion
```

关键原则：

```text
standard_cad_library_raw 是 tracked raw input，不是 capability output。
reference_library 是 evidence input，不是 capability output。
system_library 是 promoted asset，必须有 schema、lineage、check、evidence_boundary。
```

## 目录分层建议

后续落地时优先采用下面的语义分层。先写架构，不要求本包立即创建全部目录。

```text
standard_cad_library_raw/
  <source_slug>/
    original/            # 用户下载的标准 CAD 图库原始文件，可随 git 迁移
    preview/             # 可选轻量截图
    source_note.md       # Agent 自动生成或后续人工修订的来源、边界和适用范围

libraries/
  reference_library/
    sources/              # 来源、授权、脱敏、采集批次
    images/               # 轻量缩略图或索引；原始大图库仍留在 standard_cad_library_raw
    manifests/            # reference_asset 清单
    annotations/          # Agent 推断 / 用户确认的对象、部件、风格标注
    README.md

  system_library/
    objects/              # 系统自产对象定义
    parts/                # 可组合部件，如 sofa.back / sofa.seat
    blocks/               # 受控 block metadata
    symbols/              # 2D 平面符号语法
    compositions/         # 多对象组合模板
    generated/            # 已晋升自产图样索引，不放临时运行图
    README.md

  knowledge/
    source_notes/         # 外部资料摘要、授权、适用范围
    summaries/            # 用本系统语言重写后的知识页
    rules/                # 对象 / 场景规则候选
    evidence_boundaries/  # checked / not_checked / assumptions
    README.md

  benchmarks/
    object_checks/        # 对象结构检查
    part_checks/          # 部件级检查
    visual_checks/        # 视觉语义检查
    retrieval_checks/     # 检索命中检查
    promotion_checks/     # 晋升门槛
    README.md

schemas/
  reference_asset.schema.json
  system_asset.schema.json
  asset_annotation.schema.json
  asset_promotion.schema.json
  asset_evidence_boundary.schema.json

projects/<case_id>/
  references/             # 本案例使用的参考索引或用户图
  runs/                   # 检索、生成、审计、反馈证据
  runs/training_state.json

output/
  asset_runs/<run_id>/    # 大图、临时候选、缓存、审计输出
```

`core/` 只放检索、匹配、晋升 gate、schema 校验和审计算法，不放图片、图库包、用户项目资料或训练案例证据。

`standard_cad_library_raw/` 是用户为跨机器开发而设置的 tracked exception。它可以进 git，但其中任何 DWG / DXF / PDF / 图片 / 压缩包都不能绕过 `reference_asset`、`knowledge_summary`、`executable_check` 和 promotion gate 直接进入 `system_library`。

## Raw Intake 自动化默认策略

默认不是“用户先填表”，而是：

```text
用户放文件 + 一句说明
  -> Agent 扫描 standard_cad_library_raw/<source_slug>/original/
  -> 推断 object_tags / view_type / domain / part_tags
  -> 不确定字段写 unknown
  -> 只生成 reference_only manifest 和 agent_inferred annotations
  -> 后续进入 retrieval / knowledge / promotion gate
```

执行入口：

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_asset_raw_intake.py --source-slug <source_slug> --description "这批大概是什么" --write
```

该入口只写 `standard_cad_library_raw/<source_slug>/source_note.md`、`libraries/reference_library/` 和 `libraries/knowledge/source_notes/`。它不解析 CAD 几何，不复制 raw 文件，不写 `libraries/system_library/`，也不改变表 C。

## 资产类型

### reference_asset

外部参考资产，只能回答“参考过什么、来源边界是什么、表达哪些对象 / 部件 / 风格”。

最小字段：

```json
{
  "id": "ref.residential.sofa.0001",
  "source_type": "user_provided | public_reference | vendor_catalog | generated_reference",
  "source_name": "string",
  "source_uri_or_local_ref": "string",
  "license_status": "allowed | restricted | unknown | internal_only",
  "ingest_date": "YYYY-MM-DD",
  "domain": "residential",
  "object_tags": ["sofa"],
  "part_tags": ["seat", "back", "armrest"],
  "style_tags": ["modern"],
  "view_type": "plan | elevation | perspective | detail | unknown",
  "usage_boundary": "reference_only | annotation_allowed | derived_summary_only",
  "privacy_boundary": "raw | redacted | synthetic",
  "notes": "string"
}
```

### system_asset

系统自产资产，必须能回答“系统内部有什么可复用对象 / 部件 / 组合，它有哪些参数、语义、CAD 表达、验证状态和证据边界”。

最小字段：

```json
{
  "id": "sys.residential.sofa.two_seat.v1",
  "asset_type": "object | part | block | symbol | composition | style_sample",
  "domain": "residential",
  "canonical_name": "two_seat_sofa",
  "aliases": ["2-seat sofa", "二人沙发"],
  "parts": ["seat", "back", "armrest"],
  "parameters": {
    "width_mm": 1600,
    "depth_mm": 850
  },
  "representation": {
    "cad_plan_ref": "path-or-id",
    "block_ref": "path-or-id",
    "preview_ref": "path-or-id"
  },
  "source_lineage": ["ref.residential.sofa.0001"],
  "generation_method": "manual | pipeline | cad_run | promoted_from_case",
  "validation_status": "draft | checked | case_verified | system_verified | deprecated",
  "evidence_refs": ["projects/.../runs/..."],
  "evidence_boundary_ref": "libraries/knowledge/evidence_boundaries/...",
  "version": "1.0.0"
}
```

### rule_candidate

把参考资料和用户反馈转成可执行规则候选。

```json
{
  "id": "rule.sofa.parts.required.v1",
  "object": "sofa",
  "claim": "sofa plan symbol should distinguish seat and back",
  "applies_to": ["residential", "generic"],
  "required_parts": ["seat", "back"],
  "forbidden_shortcuts": ["single_plain_rectangle_without_semantics"],
  "source_notes": ["source.sofa.reference_pack.001"],
  "status": "candidate | active | deprecated",
  "executable_checks": ["bench.sofa.parts.required.v1"],
  "evidence_boundary": "checked/not_checked/assumptions"
}
```

### promotion_record

记录候选资产是否能进入系统自产图库。

```json
{
  "id": "promotion.sofa.two_seat.20260528",
  "candidate_ref": "projects/.../runs/round14_intent.json",
  "promoted_to": "sys.residential.sofa.two_seat.v1",
  "decision": "promoted | rejected | needs_more_evidence",
  "gates_passed": ["schema", "dry_run", "geometry_audit", "visual_review"],
  "reviewer": "agent | user | maintainer",
  "evidence_refs": ["projects/.../runs/..."],
  "assumptions": ["top-view residential symbol only"]
}
```

## 调用链

白话生成 CAD 的链路必须把资产检索放到 `CAD_PLAN` 之前：

```text
brief
  -> classify
  -> retrieve
  -> route
  -> adapt / generate contract
  -> validate + dry-run
  -> CODEX_PREVIEW execute
  -> audit
  -> delivery / repair
  -> promote
```

### classify

把用户请求分为：

| 类型 | 含义 |
| --- | --- |
| `exact_reuse` | 已有受控 block / 图库对象可直接复用 |
| `parametric_variant` | 命中对象族，但要改尺寸、座数、方向、组合 |
| `semantic_redraw` | 参考图或块只作语义来源，需要按部件重绘 |
| `novel_with_constraints` | 没有现成图库，但能归入对象语法 archetype |
| `unsupported_or_risky` | 语义不清、不可审计或会触碰正式 DWG 风险 |

### retrieve

检索不只是搜对象名，而是生成 `retrieval_pack`：

```text
controlled blocks
object catalog / defaults
symbol grammar / archetype
scene rules
learning memory
known failures
evidence_boundary
```

输出必须包含：

```text
matched_assets
object_family
archetype
required_parts
allowed_render_tiers
known_failures
not_checked
assumptions
```

### route

根据命中强度选择路线：

```text
strong block hit
  -> block reference / allowed transform

object family hit
  -> OBJECT_SPEC -> SYMBOL_SPEC / visual_parts

archetype-only hit
  -> constrained candidate generation

no auditable route
  -> deferred / ask clarification
```

不允许 `top-1` 图块命中后直接落图，也不允许找不到时静默退化成空矩形。

### adapt / generate contract

LLM 不能从 brief 直接吐 CAD primitives。它应输出结构化契约：

```text
roundN_visual_parts.json
roundN_intent.json
optional SYMBOL_SPEC
roundN_cad_plan.json
expected/audit_checklist.json
```

然后继续走 validate、dry-run、`CODEX_PREVIEW` 和审计。

## 生产模式和探索模式

### 生产模式

生产模式面向稳定交付：

```text
brief 已分类
retrieve 至少命中 object_family / archetype / controlled block / 已验证经验之一
render_tier 明确
validate + dry-run + CODEX_PREVIEW + audit 证据齐
delivery 能说清 checked / not_checked / assumptions
```

允许的降级链：

```text
controlled_block
-> symbol_readable
-> component_preview
-> bbox_placeholder（仅用户明确接受，且标为 fallback）
-> deferred
```

### 探索模式

探索模式面向新对象、新款式或图库弱命中：

```text
自产图库无强命中
用户要求新造型 / 新家具 / 新符号
只有参考图但没有可执行对象常识
审计项不足以证明语义正确
```

探索模式输出是候选，不是正式完成：

```text
1-3 个 visual_parts / SYMBOL_SPEC 候选
每个候选写依据、假设、not_checked
先落 CODEX_PREVIEW
审计通过后仍标 visual_review_required
用户 pass 或第二案例复用后再考虑 promote
```

创造性的来源应该是：

```text
archetype + required_parts + style modifiers + parametric variation
```

而不是：

```text
LLM 直接想象 CAD 线段
```

## 生命周期

每个参考样本、派生对象和自产块都应有状态。

| 状态 | 含义 | 能否声明能力 |
| --- | --- | --- |
| `reference_only` | 外部参考，只能用于理解风格、部件、比例、禁忌 | 否 |
| `candidate` | 已转成对象候选、部件语法、参数、审计项 | 否 |
| `case_verified` | 单个训练案例中 CAD 输出、审计、自检、用户反馈通过 | 只能声明该 case |
| `system_verified` | 多样本、多尺寸、负例或回归测试通过，可由系统独立重建 | 可以声明对应对象族边界内能力 |
| `deprecated` | 来源不清、过拟合、被替代、重复失败或授权风险 | 否 |

自产图库最小定义：

```text
metadata + generator/recipe + tests + verified examples + evidence_boundary
```

只有 DWG、PNG、截图或一个看起来能用的 preview，不算系统自产图库。

## Agent 职责调整

这不是推倒现有多 Agent 架构，而是加厚职责。

| Agent | 新职责 |
| --- | --- |
| `pipeline_asset_retriever` | 产出 `retrieval_pack`；查 catalog、block、object defaults、symbol grammar、learning memory；遇到标准图库文件夹时调用 raw intake，缺字段默认 `unknown` / `reference_only` |
| `pipeline_context_curator` | 识别 standard_library_intake 意图；提取 folder + rough note，不要求用户补表格 |
| `pipeline_orchestrator` | 增加 `exact_reuse` / `parametric_variant` / `semantic_redraw` / `novel_with_constraints` / `deferred` 路由；遇到 library intake 走非绘图分支，不进入 CAD execute |
| `pipeline_visual_intent` | 消费 `retrieval_pack`，产出 required_parts、style modifiers、forbidden shortcuts |
| `pipeline_intent` | 从 visual_parts / archetype 生成 intent、SYMBOL_SPEC、audit_checklist，不把 bbox 当对象 |
| `pipeline_execute` | 变成 renderer selector；只接受结构化契约，不接受 arbitrary block name |
| `pipeline_audit` | 增加 retrieval_audit、symbol_readability_audit，再接 geometry audit |
| `pipeline_repair` | 先修检索 / 分类，再修缺件 / 符号语义，再修几何洁净，最后修尺寸微调 |
| `pipeline_learning_promoter` | 判断沉淀到 case、scene rule、system_library、Core probe，还是等待第二案例 |

## 标准图库 / 截图 / 描述的固定产物

以后用户给“标准图库文件夹 / 截图 + 描述”时，不应只把图片或 raw 文件放进目录。一次 intake 至少应派生：

```text
source_note
reference_asset 单对象 JSON
agent_inferred_annotations
retrieval_pack（进入具体训练案例时）
visual_style_brief.md（进入 reference-match 绘图时）
knowledge_summary.md（整理对象常识时）
object_or_rule_candidate.json（准备晋升候选时）
expected/audit_checklist.json（进入训练案例时）
evidence_boundary.md（晋升前必须补齐）
```

raw 文件和截图本身只进 `reference_only`。真正让系统变聪明的是结构化语义、可执行检查、训练反馈和 promotion gate。

## 晋升门槛

进入 `system_verified` 前至少过五道门：

| 门槛 | 要求 |
| --- | --- |
| 来源门 | 证明只是参考，不直接复制外部图库块、线型、版权资产 |
| 结构门 | 有 parts、层级、方向语义、尺寸参数、默认约束、可变项和 forbidden patterns |
| 执行门 | 能从 CAD_PLAN 或 case_script 生成到 CODEX_PREVIEW，有 execution summary、handles、readback |
| 审计门 | geometry audit、symbol readability、retrieval boundary、Agent 自检通过 |
| 泛化门 | 多尺寸 / 多朝向 / 多变体 / 负例或第二案例通过 |

单个截图通过最多到 `case_verified`，不能直接到 `system_verified`。

## RAG 的位置

RAG 可以帮忙：

- 查对象常识。
- 查受控 catalog。
- 查审计规则。
- 查来源边界。
- 查历史失败。

RAG 不能直接证明：

- 系统能画准。
- CAD 几何真实存在。
- 用户会认可款式。
- 可以进入表 C。
- 可以复制或生产使用外部资产。

RAG 返回的内容必须继续进入 `retrieval_pack`、结构化契约和审计链路。

## 禁止声称

本架构明确禁止：

- 不直接搬外部图库代码、DWG 块、厂商资产或受限参考图。
- 不把 RAG、wiki、Markdown、catalog 命中说成 Agent 已学会。
- 不把自产图库做成固定款式池。
- 不把截图、SVG / PNG 预览、dry-run、non-CAD benchmark 当真实 CAD 几何证据。
- 不因新增知识库或图库条目就声称表 C 提升。
- 不声称已建立自动常识学习系统，除非有完整 ingestion、审计、测试和回写闭环。
- 不默认保存、覆盖、删除或修改用户 DWG；真实落图仍默认 `CODEX_PREVIEW`。

## 后续落地计划

架构包之后的推荐顺序与当前状态：

1. **目录与 schema 小包**：基础版已落地，见 `libraries/reference_library/`、`libraries/system_library/`、`libraries/knowledge/`、`libraries/benchmarks/` 与 `core/schemas/*asset*.schema.json`。
2. **检索包**：基础版已落地，见 `core/assets/retrieval.py` 与 `scripts/run_asset_retrieval_pack.py`；当前是 JSON / Markdown 词法检索，不是 embedding RAG。
3. **Agent 包**：基础版已落地，见 `agents/pipeline/asset_retriever/agent.json` 与 `pipeline_manifest.json`。
4. **训练 intake 包**：自动 raw intake 已落地，见 `core/assets/raw_intake.py`、`scripts/run_asset_raw_intake.py`、`docs/training/asset-intake-template.md` 与 `projects/residential_training_template/references/`。
5. **晋升 gate 包**：基础版已落地，见 `core/assets/promotion_gate.py` 与 `scripts/run_asset_promotion_gate.py`；当前只出报告，不自动写回图库。
6. **首个对象族试点**：从沙发或床开始，沉淀对象语法、参数变体、审计门槛和 case 验收。
7. **再考虑 RAG**：等结构化资产和检索字段稳定后，再把索引接到 RAG，而不是先建向量库。

## 退出标准

本架构包完成后，只能说：

- CAD 资产智能升级的架构边界已写入。
- 外部参考图库和自产图库的职责已区分。
- 后续目录、Agent、训练和晋升的路线已确定。

不能说：

- 资产目录已经全部落地。
- 系统已经拥有标准图库。
- RAG 已经可用。
- 沙发、床、桌等对象已经系统级 verified。
- 表 C 或真实 CAD 实力提升。
