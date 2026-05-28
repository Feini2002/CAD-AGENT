# CAD 常识资产开发实施计划

> **面向后续 Agent:** 执行本计划时，建议使用 `superpowers:subagent-driven-development` 或 `superpowers:executing-plans` 逐项推进。步骤使用 checkbox (`- [ ]`) 语法，便于按批次追踪。

**Goal:** 用可迁移的标准 CAD 图库快速建设 CAD 常识底座，同时保证“原始参考输入”和“系统自产能力”不混淆。

**Architecture:** 原始标准图库统一进根目录 `standard_cad_library_raw/` 并跟随 git 迁移；系统只把经过标注、总结、检查和晋升的内容写入 `libraries/system_library/`。`libraries/reference_library/`、`libraries/knowledge/`、`libraries/benchmarks/` 负责把 raw 文件变成可读、可查、可测、可声明边界的资产管线。

**Tech Stack:** Markdown 文档、JSON manifest、既有 asset schema、`scripts/run_asset_raw_intake.py`、`scripts/run_asset_retrieval_pack.py`、`scripts/run_asset_promotion_gate.py`、训练案例 `projects/<case_id>/`、真实 CAD `CODEX_PREVIEW` 证据。

---

## 结论先行

| 用途 | 根目录 / 仓库路径 | 是否等于系统能力 |
| --- | --- | --- |
| 下载的标准 CAD 图库原始文件 | `standard_cad_library_raw/` | 否，只是 raw reference input |
| 参考图库索引、来源、标注 | `libraries/reference_library/` | 否，只是可检索参考 |
| 系统自产图库 | `libraries/system_library/` | 只有通过 gate 的条目才算系统资产 |
| 常识摘要、规则候选、证据边界 | `libraries/knowledge/` | 不是几何证明，但可参与检索和审计 |
| 对象 / 部件 / 晋升检查 | `libraries/benchmarks/` | 检查入口，不替代真实 CAD 证据 |

本计划接受用户的新约束：**标准图库原始文件可以进入 git**，用于家里和公司两头同步。风险控制不是把它们排除出仓库，而是把它们限制在 `standard_cad_library_raw/`，并在进入系统资产前强制走标注、总结、检查和晋升。

## 目录职责

```text
standard_cad_library_raw/
  README.md
  <source_slug>/
    original/            # 下载的 DWG/DXF/PDF/图片/压缩包等原始资料
    preview/             # 可选截图，帮助快速浏览
    source_note.md       # 该批次来源、授权、适用范围和禁止用途

libraries/reference_library/
  sources/               # 批次来源说明和授权边界
  manifests/             # reference_asset JSON 清单
  annotations/           # Agent 推断 / 用户确认的对象、部件、风格标注
  images/                # 轻量缩略图或索引，不承载原始大图库职责

libraries/knowledge/
  source_notes/          # 从 raw/source_note 整理出的资料摘要
  summaries/             # 用本系统语言重写的对象常识
  rules/                 # 对象或场景规则候选
  evidence_boundaries/   # checked / not_checked / assumptions

libraries/system_library/
  objects/               # 自产对象定义，如 sofa、bed、table
  parts/                 # 可组合部件，如 sofa.back、bed.headboard
  blocks/                # 受控 block metadata
  symbols/               # 2D 平面符号语法
  compositions/          # 多对象组合模板
  generated/             # 已晋升图样索引，不放临时运行图
```

## 关键边界

- `standard_cad_library_raw/` 可以进 git，但它是“资料库”，不是“能力库”。
- `libraries/reference_library/` 记录 raw 文件对应的来源、对象标签、授权边界、适用场景和 Agent 推断 / 用户确认标注。
- `libraries/system_library/` 只收被系统重写、可复用、可测试、可追溯的自产资产。
- 一个下载的沙发 DWG 存在，不代表系统会画沙发；至少要形成 `knowledge_summary`、`rule_candidate`、`executable_check`、`evidence_boundary`，再通过训练案例和 promotion gate。
- 真实 CAD 能力声明仍必须看 `CAD_PLAN`、validate、dry-run、`CODEX_PREVIEW`、created handles 回读、审计和用户验收。

## 风险控制

| 风险 | 怎么控 |
| --- | --- |
| 误追踪 | 只把标准图库放 `standard_cad_library_raw/`；提交前看 `git status --short standard_cad_library_raw libraries/reference_library libraries/system_library`，不要把临时解压缓存、失败下载、重复压缩包、软件锁文件混进来 |
| 误提交 | 每个批次由 `run_asset_raw_intake.py` 生成 `source_note.md` 草稿；来源、授权和商业限制不确定时保持 `unknown` / `reference_only`，不得在交付口径中说“可复用生产资产” |
| 误当系统能力 | raw 批次默认 `reference_only`；只有 promotion gate 通过后，才允许在 `libraries/system_library/` 生成 `case_verified` 或 `system_verified` 条目 |
| 创造性收缩 | retrieval 不能只取 top-1 图块拉伸；图库弱命中时走对象语法、参数化部件、style modifiers 和 `visual_review_required` |
| 体积膨胀 | 批次粒度从小做起，先导入一个对象族的少量标准样本；大批量图库进入 git 前先看体积和必要性 |

## Task 1: 自动建立原始图库批次入口

**Files:**
- Create or use: `standard_cad_library_raw/<source_slug>/original/`
- Use: `scripts/run_asset_raw_intake.py`
- Create: `standard_cad_library_raw/<source_slug>/source_note.md`
- Create: `libraries/reference_library/sources/<source_slug>.md`
- Create: `libraries/knowledge/source_notes/<source_slug>.md`

- [ ] **Step 1: 创建批次目录**

```powershell
New-Item -ItemType Directory -Force -Path standard_cad_library_raw\<source_slug>\original
New-Item -ItemType Directory -Force -Path standard_cad_library_raw\<source_slug>\preview
```

- [ ] **Step 2: 放入下载的标准图库原始文件**

把同一来源、同一授权边界的一批文件放进：

```text
standard_cad_library_raw/<source_slug>/original/
```

一个 `<source_slug>` 只对应一个来源或一个清晰批次，例如：

```text
standard_cad_library_raw/residential-furniture-pack-202606/
standard_cad_library_raw/office-blocks-vendor-a-202606/
```

- [ ] **Step 3: 运行自动 raw intake**

用户不需要先填表。Agent 根据文件夹、文件名、扩展名和一句说明自动推断对象、图纸类型和适用范围；不确定项写 `unknown`，资料边界默认 `reference_only`。

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_asset_raw_intake.py --source-slug <source_slug> --description "这批大概是什么" --write
```

该脚本会生成 `source_note.md`、`libraries/reference_library/sources/<source_slug>.md`、`libraries/knowledge/source_notes/<source_slug>.md`，并跳过 CAD 锁文件、下载临时文件等不应入库的文件。

- [ ] **Step 4: 检查自动推断结果**

重点看 `license_status` 是否仍为 `unknown`、`usage_boundary` 是否为 `reference_only`、`review_status` 是否为 `agent_inferred`。如用户没有明确授权或确认，不要把推断字段改成事实。

- [ ] **Step 5: 提交前检查范围**

```powershell
git status --short standard_cad_library_raw libraries/reference_library
```

Expected: 只出现本批次 raw 文件、source note、reference source、reference manifest 和 inferred annotation，不出现 CAD 锁文件、临时下载文件或无关输出。

## Task 2: 生成 reference manifest 和 Agent 推断标注

**Files:**
- Use: `scripts/run_asset_raw_intake.py`
- Create: `libraries/reference_library/manifests/<source_slug>/ref.*.json`
- Create: `libraries/reference_library/annotations/<source_slug>/ann.*.json`

- [ ] **Step 1: 建 reference manifest**

每个有效 raw 文件生成一条单对象 `reference_asset` JSON，匹配现有 schema 和检索实现：

```json
{
  "id": "ref.residential.source_slug.0001",
  "source_type": "user_provided",
  "source_name": "<source_slug>",
  "source_uri_or_local_ref": "standard_cad_library_raw/<source_slug>/original/<file_name>",
  "license_status": "unknown",
  "ingest_date": "YYYY-MM-DD",
  "domain": "residential",
  "object_tags": ["sofa"],
  "part_tags": ["seat", "back", "arm_left", "arm_right"],
  "style_tags": [],
  "view_type": "plan",
  "usage_boundary": "reference_only",
  "privacy_boundary": "raw",
  "review_status": "agent_inferred",
  "notes": "Auto raw intake: reference-only candidate; not a system asset."
}
```

- [ ] **Step 2: 建 Agent 推断标注**

`annotations` 记录从文件夹、文件名和一句说明推断出的对象语义。它是候选标注，不是用户确认：

```json
{
  "annotation_id": "ann.residential.source_slug.0001",
  "asset_ref": "ref.residential.source_slug.0001",
  "object_tags": ["sofa"],
  "part_tags": ["seat", "back", "arm_left", "arm_right"],
  "style_tags": [],
  "view_type": "plan",
  "annotator": "agent:auto_raw_intake",
  "review_status": "agent_inferred"
}
```

- [ ] **Step 3: 保持 raw 与 reference 分离**

manifest 可以引用 `standard_cad_library_raw/...`，但不要把原始 DWG/DXF 复制进 `libraries/reference_library/`。

## Task 3: 编译对象常识

**Files:**
- Create: `libraries/knowledge/source_notes/<source_slug>.md`
- Create: `libraries/knowledge/summaries/<object_type>.md`
- Create: `libraries/knowledge/rules/<object_type>.rules.json`
- Create: `libraries/knowledge/evidence_boundaries/<object_type>.boundary.md`

- [ ] **Step 1: 写 source note 摘要**

把 raw 批次里的对象、可用范围、不可用范围写成短文。要求能回答：这个资料教了什么、没教什么、能否生产复用。

- [ ] **Step 2: 写对象常识页**

以 `sofa` 为例，`libraries/knowledge/summaries/sofa.md` 至少包含：

```markdown
# Sofa CAD Plan Symbol

对象：sofa / 沙发
适用视图：plan
常见部件：seat、back、armrest、cushion seam
最低可接受表达：必须能区分座面和靠背；多人位沙发应有座缝或模块分隔。
禁止捷径：单个空矩形不能代表沙发；方向语义不能把靠背和坐垫反过来。
需要用户验收：款式柔软感、弧线比例、是否像具体参考图。
```

- [ ] **Step 3: 写规则候选**

`libraries/knowledge/rules/sofa.rules.json` 使用候选状态：

```json
{
  "id": "rule.sofa.plan_symbol.parts.v1",
  "object": "sofa",
  "status": "candidate",
  "required_parts": ["seat", "back"],
  "recommended_parts": ["armrest", "cushion_seam"],
  "forbidden_patterns": ["single_plain_rectangle_without_semantics"],
  "evidence_boundary": "libraries/knowledge/evidence_boundaries/sofa.boundary.md"
}
```

- [ ] **Step 4: 写证据边界**

`evidence_boundaries/<object_type>.boundary.md` 必须列出 `checked`、`not_checked` 和 `assumptions`。没有这一文件，不允许从 reference 晋升为 system asset。

## Task 4: 建对象检查和训练用 benchmark

**Files:**
- Create: `libraries/benchmarks/object_checks/<object_type>.checks.json`
- Create: `libraries/benchmarks/promotion_checks/<object_type>.promotion.json`

- [ ] **Step 1: 把常识变成可检查项**

以沙发为例：

```json
{
  "id": "bench.sofa.plan_symbol.parts.v1",
  "object": "sofa",
  "checks": [
    {
      "name": "has_seat_and_back",
      "type": "semantic_part_presence",
      "required": ["seat", "back"]
    },
    {
      "name": "not_plain_rectangle_only",
      "type": "forbidden_pattern",
      "patterns": ["single_plain_rectangle_without_semantics"]
    },
    {
      "name": "direction_semantics_not_inverted",
      "type": "visual_semantic_order",
      "required_relation": "back is distinguishable from seat"
    }
  ]
}
```

- [ ] **Step 2: 写 promotion 检查**

promotion check 至少要求 schema、对象常识、训练案例、CAD 证据和用户验收状态齐全。

## Task 5: 生成候选自产资产

**Files:**
- Create: `libraries/system_library/objects/<object_type>/<asset_id>.json`
- Create or reference: `libraries/system_library/parts/<object_type>/*.json`
- Use: `scripts/run_asset_retrieval_pack.py`

- [ ] **Step 1: 先建 draft**

候选自产资产初始必须是 `draft`：

```json
{
  "id": "sys.residential.sofa.two_seat.v1",
  "asset_type": "object",
  "domain": "residential",
  "canonical_name": "two_seat_sofa",
  "aliases": ["二人沙发", "2-seat sofa"],
  "parts": ["seat", "back", "armrest"],
  "parameters": {
    "width_mm": 1600,
    "depth_mm": 850
  },
  "source_lineage": ["ref.residential.sofa.0001"],
  "generation_method": "promoted_from_case",
  "validation_status": "draft",
  "evidence_refs": [],
  "evidence_boundary_ref": "libraries/knowledge/evidence_boundaries/sofa.boundary.md",
  "version": "1.0.0"
}
```

- [ ] **Step 2: 跑 retrieval pack 检查命中**

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_asset_retrieval_pack.py --brief "画一个二人沙发" --scene residential
```

Expected: 输出能命中 `sofa` 对象常识或 draft 系统资产，同时不会把 raw 文件命中报告成 `system_verified`。

## Task 6: 通过训练案例验证

**Files:**
- Create or use: `projects/<case_id>/brief.md`
- Create or use: `projects/<case_id>/references/`
- Create or use: `projects/<case_id>/runs/training_state.json`
- Update: `projects/<case_id>/feedback.md`

- [ ] **Step 1: 复制训练模板开案例**

```powershell
Copy-Item -Recurse projects\residential_training_template projects\<case_id>
```

- [ ] **Step 2: 在 case 里引用 reference asset**

案例不要直接说“图库里有沙发所以已学会”，而要写明本轮参考了哪些 `ref.*`、希望验证哪些对象常识、用户要重点验收什么。

- [ ] **Step 3: 跑真实 CAD 训练轮**

仍按训练链路执行：

```text
brief -> retrieval_pack -> visual_intent -> CAD_PLAN -> validate -> dry-run -> CODEX_PREVIEW -> audit -> screenshot -> agent_review -> feedback
```

- [ ] **Step 4: 用户反馈进入 case**

用户指出“方向反了”“靠背不明显”“桌腿缺失”时，先写入 `projects/<case_id>/feedback.md`，再判断进入 `knowledge`、`benchmarks` 还是 `system_library`。

## Task 7: 晋升到自产图库

**Files:**
- Use: `scripts/run_asset_promotion_gate.py`
- Update: `libraries/system_library/objects/<object_type>/<asset_id>.json`
- Create: `libraries/system_library/generated/<asset_id>.promotion.md`

- [ ] **Step 1: 跑 promotion gate**

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_asset_promotion_gate.py --candidate libraries\system_library\objects\<object_type>\<asset_id>.json
```

Expected: gate 明确返回 `promoted`、`rejected` 或 `needs_more_evidence`，并说明缺哪些证据。

- [ ] **Step 2: 更新 validation_status**

只有当 schema、检查、训练证据、CAD 回读和用户验收满足当前门槛时，才把 `validation_status` 从 `draft` 改成 `case_verified`。跨多个案例稳定后，才允许改成 `system_verified`。

- [ ] **Step 3: 写 promotion 摘要**

`generated/<asset_id>.promotion.md` 必须写清：

```markdown
# <asset_id> Promotion

Decision: promoted / rejected / needs_more_evidence
Status: draft / case_verified / system_verified
Source lineage: ref...
CAD evidence: projects/.../runs/...
Checked: ...
Not checked: ...
Assumptions: ...
```

## Task 8: 每批次收口检查

**Files:**
- Check: `standard_cad_library_raw/`
- Check: `libraries/reference_library/`
- Check: `libraries/knowledge/`
- Check: `libraries/benchmarks/`
- Check: `libraries/system_library/`
- Update if needed: `docs/status/current.md`、`docs/status/changelog.md`、`docs/status/issues.md`

- [ ] **Step 1: 检查 raw 没有污染 system asset**

```powershell
git status --short standard_cad_library_raw libraries/reference_library libraries/system_library
```

Expected: raw 文件只在 `standard_cad_library_raw/`；`libraries/system_library/` 只出现 metadata、recipe、generated index 或已晋升定义。

- [ ] **Step 2: 检查能力声明**

任何最终回复只允许说：

```text
已导入/登记一批参考图库。
已把其中 N 个对象整理成常识候选。
已有 X 个候选通过 case_verified。
尚未证明 system_verified 的对象，不声明为稳定能力。
```

- [ ] **Step 3: 决定下一批对象族**

优先顺序建议：

```text
sofa -> bed -> table -> chair -> cabinet -> door/window symbol -> appliance
```

每次只推进一个对象族或一个小批次，避免 raw 图库体量先失控。

## 本计划的完成判定

本计划不是一次性完成所有常识底座，而是定义后续开发路线。当前只要完成这些，就算本计划书已完成：

- 已指定标准图库原始下载目录：`standard_cad_library_raw/`。
- 已指定自产图库目录：`libraries/system_library/`。
- 已规定 raw、reference、knowledge、benchmark、system asset 的职责。
- 已规定 raw 文件进 git 时的误追踪、误提交和误当能力风险。
- 已给出从下载图库到自产资产晋升的可执行步骤。

真正的 CAD 常识能力提升，仍要在后续对象族训练中逐步证明。
