# CAD-AGENT vNext 完整开发实施主计划

状态：**迁移期唯一开发执行主计划**  
版本：1.0  
日期：2026-06-22  
配套架构：仓库内 `docs/vnext/ARCHITECTURE_DECISION.md`  
适用方式：放入仓库 `docs/vnext/IMPLEMENTATION_MASTER_PLAN.md`，由 Codex 每次只执行一个 Work Package。

> 本文不是概念方案。每个 Work Package 均包含目标、文件、实现步骤、测试、退出标准、阻断条件和回滚方式。Codex 不得一次性执行多个未放行包，不得因旧仓库文档冲突而扩大范围。

---

# 0. 先回答顺序问题

正确开发顺序如下：

```text
A. 冻结旧系统和记录基线
B. 建立最小 vNext 架构骨架
C. 收编一条安全 CAD 执行通道
D. 建立 SceneSpec → CadPatch → Receipt → Verification 闭环
E. 让 Codex 通过 Skill 成为 Principal Agent
F. 执行 Gate 0
G. Gate 0 通过后，继续泛化、内嵌运行时、场景扩大和 Legacy 删除
```

不是先完成全部系统架构，再做 Gate 0。

Gate 0 前只允许建设**支撑 Gate 0 的最小主链**。Gate 0 是架构是否值得继续的验证，不是完整重构后的装饰性测试。

---

# 1. 文档权威和执行规则

## 1.1 权威顺序

执行期间发生冲突时：

```text
用户当前明确指令
> CAD 安全、数据保护和 no-save 边界
> docs/vnext/ARCHITECTURE_DECISION.md
> docs/vnext/IMPLEMENTATION_MASTER_PLAN.md
> 本 Work Package 的范围
> 精简后的 README.md / AGENTS.md
> 旧 CORE_* / training / status / OpenSpec 文档
> output / derived / historical artifacts
```

## 1.2 每次只执行一个 Work Package

状态只能是：

- `not_started`
- `prepared`
- `active`
- `blocked`
- `validated`
- `merged`
- `reconciled`

禁止：

- 同一个工作区并行执行两个 active package；
- package 未验证就更新后续 package 为完成；
- 通过改状态文档冒充代码完成；
- 将 no-CAD fixture pass 冒充 real-CAD pass。

## 1.3 每个 PR 必须满足

1. 变更范围单一；
2. 新增或修改行为有自动测试；
3. 旧测试至少不比 baseline 更差；
4. 有明确 rollback；
5. 不新增第二套 schema 或状态事实源；
6. 不写当前业务 DWG；
7. 完成报告列明“证明了什么、没有证明什么”。

## 1.4 Codex 开始前必须输出

```text
Active package:
Read files:
Files planned to change:
Non-goals:
Tests planned:
Risks:
```

如果实际仓库与本文假设冲突，先标记 `blocked` 或提出最小路径修正，不得静默发明新主线。

---

# 2. 迁移期状态文件

创建：

```text
docs/vnext/MIGRATION_STATE.json
```

初始内容：

```json
{
  "schemaVersion": "cad-agent-vnext-migration-state/v1",
  "baselineCommit": "TO_BE_RECORDED",
  "activePackage": "VN-00",
  "packageStatus": "not_started",
  "gate0": {
    "devStatus": "not_started",
    "releaseStatus": "not_started",
    "latestRunId": null,
    "latestReport": null
  },
  "legacyExpansionFrozen": false,
  "vnextDefaultEntry": false,
  "updatedAt": "TO_BE_RECORDED"
}
```

此文件只记录迁移状态，不存详细证据。详细证据由测试、run artifacts 和 PR 记录承载。

迁移结束后，此文件归档，不成为永久产品状态机。

---

# 3. 最终目标目录

Gate 0 前：

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
│  ├─ __init__.py
│  ├─ cli.py
│  ├─ app/
│  │  ├─ run_service.py
│  │  └─ run_workspace.py
│  ├─ domain/
│  │  ├─ brief.py
│  │  ├─ drawing.py
│  │  ├─ scene.py
│  │  ├─ primitives.py
│  │  ├─ patch.py
│  │  ├─ receipt.py
│  │  ├─ verification.py
│  │  └─ ports.py
│  ├─ planning/
│  │  ├─ object_catalog.py
│  │  ├─ anchors.py
│  │  ├─ relation_solver.py
│  │  └─ scene_compiler.py
│  ├─ tools/
│  │  ├─ envelopes.py
│  │  ├─ inspect_tools.py
│  │  ├─ scene_tools.py
│  │  ├─ cad_tools.py
│  │  └─ verify_tools.py
│  ├─ adapters/
│  │  ├─ fake_backend.py
│  │  └─ legacy_autocad_backend.py
│  ├─ runtime/
│  │  ├─ runtime_port.py
│  │  └─ fixture_runtime.py
│  ├─ verification/
│  │  ├─ geometry_checks.py
│  │  ├─ receipt_checks.py
│  │  ├─ scene_verifier.py
│  │  └─ repair_planner.py
│  └─ policy/
│     ├─ transaction_policy.py
│     └─ safety_policy.py
├─ .agents/skills/cad-scene-authoring/
│  ├─ SKILL.md
│  └─ references/
├─ config/vnext/
│  └─ object_catalog.json
├─ evals/gate0/
│  ├─ cases.jsonl
│  ├─ hidden_cases.example.jsonl
│  ├─ grader.py
│  └─ README.md
├─ tests/vnext/
└─ output/vnext/runs/          # Git ignored
```

Gate 0 后再决定正式重命名和旧目录迁移。

---

# 4. 技术栈约束

## 4.1 Python

建议：Python 3.11+。

核心依赖：

- `pydantic>=2,<3`：domain contracts；
- `shapely>=2,<3`：2D footprint、containment、overlap、clearance；
- `jsonschema>=4,<5`：外部 JSON 校验或兼容检查。

开发依赖：

- `pytest>=8`；
- `pytest-cov`；
- `ruff`；
- `mypy` 可在 Gate 0 后逐步启用。

可选依赖：

- `pywin32`：Windows AutoCAD/COM adapter；
- `openai-agents`：Gate 0 后 Embedded runtime；
- `openai-codex`：Gate 0 后 Codex SDK runtime。

Gate 0 前不要求内部模型 SDK。Codex-hosted 模式由 Codex 本身执行 Skill 和 tools。

## 4.2 禁止硬编码本机解释器

正式命令使用：

```powershell
python -m pytest tests/vnext -q
python -m cad_agent_vnext.cli --help
```

如本机 CAD-MCP 环境需要指定解释器，通过环境变量或 launcher 解决，不在文档和源码写死 `%USERPROFILE%\.codex\...`。

---

# 5. Work Package 总览

| Package | 名称 | Gate 0 前/后 | 核心结果 |
|---|---|---|---|
| VN-00 | 冻结与基线 | 前 | 记录真实现状，冻结 Legacy 扩张 |
| VN-01 | 项目身份与控制面切换 | 前 | `pyproject.toml`、精简入口、vNext 权威生效 |
| VN-02 | vNext 包骨架与依赖边界 | 前 | 可安装、可测试、无 Legacy 反向依赖 |
| VN-03 | 六个 Domain Contracts | 前 | 单一协议源和 JSON Schema |
| VN-04 | Run Workspace 与 Artifact 约定 | 前 | 每次任务可追踪、可复盘 |
| VN-05 | CadBackend Port + Fake Backend | 前 | 无 CAD 环境可验证执行合同 |
| VN-06 | Legacy AutoCAD Adapter | 前 | 一条真实 preview/readback 通道被收编 |
| VN-07 | Transaction Gateway 与 Safety | 前 | 所有写入单一入口、no-save、可回滚 |
| VN-08 | Primitive IR 与对象目录 | 前 | 五个 Gate 0 原子对象可参数化生成 |
| VN-09 | 通用关系求解器 | 前 | 相对关系变成确定坐标 |
| VN-10 | Scene Compiler | 前 | SceneSpec 编译成 CadPatch |
| VN-11 | Verification 与最小 Repair | 前 | 机器检查和局部修复闭环 |
| VN-12 | Codex Skill 与工具 CLI | 前 | 用户一句话触发完整 Codex-hosted loop |
| VN-13 | Gate 0 Eval Harness | 前 | 自动 grader、变体、反作弊、报告 |
| VN-14 | Gate 0 Real-CAD Acceptance | 前 | 决定继续、修正或停止迁移 |
| VN-15+ | 泛化、编辑、房间、产品化、切流 | 后 | 按 Gate 1～7 发展 |

---

# 6. VN-00：冻结与基线

## 6.1 目标

不改产品行为，准确记录：

- 当前 HEAD；
- 当前测试结果；
- 正式入口；
- CAD 写入路径；
- real-CAD 已验证证据；
- 旧控制面和派生产物；
- Gate 0 可复用能力。

## 6.2 新建文件

```text
docs/vnext/baseline.md
docs/vnext/MIGRATION_STATE.json
scripts/vnext/check_legacy_expansion.py
tests/vnext/test_legacy_expansion_freeze.py
```

## 6.3 修改文件

```text
.gitignore
README.md              # 只增加迁移入口提示
AGENTS.md              # 只增加冻结规则和权威指针
```

## 6.4 实施步骤

1. 记录：

```bash
git rev-parse HEAD
git status --short
git branch --show-current
```

2. 给当前稳定状态创建本地/远程 tag，命名建议：

```text
legacy-baseline-2026-06-22
```

3. 运行旧测试：

```bash
python -m unittest discover -s tests -q
```

4. 运行仓库已有治理检查，但只记录，不因历史 warning 扩大本 PR：

```bash
python scripts/run_doc_governance_audit.py
python scripts/run_entrypoint_custody_audit.py
```

5. 在 `baseline.md` 写明：

- 通过的测试数；
- 失败项；
- AutoCAD 是否连接；
- 当前正式 CAD preview 入口；
- current DWG 是否需要人工打开；
- 可复用 driver/readback 文件；
- 旧 orchestrator/training/workbench 列为 frozen。

6. `check_legacy_expansion.py` 检查相对 baseline 是否新增：

- `agents/pipeline/**/agent.json`；
- 新 training curriculum item；
- 根目录新的架构 MD；
- 新 `scripts/run_*.py`；
- 新表 A/B/C 字段。

Gate 0 前新增这些内容应失败，除非文件在 vNext allowlist。

7. 更新 `MIGRATION_STATE.json`：

```json
{
  "activePackage": "VN-00",
  "packageStatus": "validated",
  "legacyExpansionFrozen": true
}
```

## 6.5 自动测试

```bash
python -m pytest tests/vnext/test_legacy_expansion_freeze.py -q
python -m unittest discover -s tests -q
```

## 6.6 退出标准

- baseline commit 已记录；
- 工作区干净；
- 旧测试结果可复现；
- Legacy 扩张检查生效；
- 没有移动或删除真实 CAD 文件；
- 没有新增业务功能。

## 6.7 阻断条件

- 当前工作区存在无法解释的未提交 CAD 改动；
- 无法识别真实 CAD 写入入口；
- baseline 测试完全不可运行；
- 当前 main 不包含此前审查的关键文件。

## 6.8 回滚

删除 VN-00 新增文件并恢复 README/AGENTS 的最小指针，不影响旧运行时。

## 6.9 Codex 执行口令

```text
执行 VN-00。只做冻结、基线、入口盘点和扩张检查，不实现 vNext 功能，不移动旧代码，不清理 output。先记录 HEAD 和工作区状态，再运行旧测试。完成时给出 baseline commit、测试结果、真实 CAD 入口候选、阻断风险和改动文件。
```

---

# 7. VN-01：Python 项目身份与控制面切换

## 7.1 目标

建立可安装的 Python 工程身份，并让仓库明确：

- Gate 0 是当前第一目标；
- vNext 文档是迁移权威；
- Legacy 只修阻断，不继续扩张；
- Node/Worker 是可选基础设施，不是 Python Core 主体。

## 7.2 新建文件

```text
pyproject.toml
src/cad_agent_vnext/__init__.py
```

## 7.3 修改文件

```text
README.md
AGENTS.md
package.json           # 只增加技术栈说明字段或 README 指针，不破坏脚本
.gitignore
```

## 7.4 `pyproject.toml` 最小目标

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "cad-agent-vnext"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "pydantic>=2,<3",
  "shapely>=2,<3",
  "jsonschema>=4,<5"
]

[project.optional-dependencies]
dev = [
  "pytest>=8",
  "pytest-cov>=5",
  "ruff>=0.6"
]
autocad = [
  "pywin32>=306; platform_system == 'Windows'"
]
agent = [
  "openai-agents"
]
codex = [
  "openai-codex"
]

[project.scripts]
cad-agent-vnext = "cad_agent_vnext.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["src/cad_agent_vnext"]

[tool.pytest.ini_options]
testpaths = ["tests/vnext"]
```

版本号可由 Codex根据实际依赖兼容性调整，但不得同时建立 `requirements.txt` 作为第二权威源；如需要 lock，使用明确 lock 工具。

## 7.5 README 迁移期最小结构

README 顶部只保留：

1. 产品目标；
2. 当前阶段：vNext Gate 0；
3. 旧系统 frozen；
4. 开发入口：两个 vNext 文档；
5. 安装与测试；
6. CAD no-save 边界。

旧长状态说明迁往历史，不在本包删除。

## 7.6 AGENTS 最小新增规则

```text
- 当前开发只执行 docs/vnext/IMPLEMENTATION_MASTER_PLAN.md 的 active package。
- Gate 0 前禁止扩大 legacy agents/training/workbench/coverage。
- vNext 新代码不得 import legacy orchestrator/training/workbench。
- 所有 CAD 写入只允许 CODEX_PREVIEW，且 savedCurrentDwg=false。
- 完成声明必须列出自动测试和真实 CAD 证据边界。
```

## 7.7 测试

```bash
python -m pip install -e ".[dev]"
python -c "import cad_agent_vnext; print(cad_agent_vnext.__version__)"
python -m pytest tests/vnext -q
python -m unittest discover -s tests -q
```

## 7.8 退出标准

- editable install 成功；
- vNext 包可 import；
- root 控制面明确指向 Gate 0；
- 没有删除旧文档；
- package.json 未被误当成 Core 主身份。

## 7.9 回滚

删除 pyproject 和包壳，恢复 README/AGENTS。本包不改业务代码。

---

# 8. VN-02：vNext 包骨架与依赖边界

## 8.1 目标

建立清晰模块，不实现业务逻辑。

## 8.2 新建目录与文件

```text
src/cad_agent_vnext/app/__init__.py
src/cad_agent_vnext/domain/__init__.py
src/cad_agent_vnext/planning/__init__.py
src/cad_agent_vnext/tools/__init__.py
src/cad_agent_vnext/adapters/__init__.py
src/cad_agent_vnext/runtime/__init__.py
src/cad_agent_vnext/verification/__init__.py
src/cad_agent_vnext/policy/__init__.py
src/cad_agent_vnext/cli.py
scripts/vnext/check_import_boundaries.py
tests/vnext/test_import_boundaries.py
tests/vnext/test_cli_smoke.py
```

## 8.3 依赖规则实现

`check_import_boundaries.py` 至少检查：

- `domain/**` 禁止 import `openai`、`agents`、`openai_codex`、`win32com`、`core`、`cad_agent`、`agents.pipeline`；
- `planning/**` 禁止 import AutoCAD adapter；
- `verification/**` 禁止调用写 CAD 方法；
- `adapters/legacy_autocad_backend.py` 是唯一允许 import 旧执行底座的 vNext 文件；
- `src/cad_agent_vnext/**` 禁止 import training/workbench/status/coverage 模块；
- `tools` 不包含业务关键词表。

建议使用 AST，而不是简单 grep。

## 8.4 CLI 骨架

```bash
cad-agent-vnext version
cad-agent-vnext doctor
```

`doctor` 只报告：

- Python 版本；
- vNext package；
- Shapely/Pydantic；
- Windows/AutoCAD adapter availability；
- output path 可写；
- 不连接或修改 CAD。

## 8.5 测试

```bash
python -m pytest tests/vnext/test_import_boundaries.py -q
python -m pytest tests/vnext/test_cli_smoke.py -q
cad-agent-vnext doctor
```

## 8.6 退出标准

- 模块边界机器可检查；
- CLI 可运行；
- 无 Legacy import，除预留 adapter 文件；
- 不新增业务功能。

---

# 9. VN-03：六个 Domain Contracts

## 9.1 目标

建立唯一协议源，并自动输出 JSON Schema。

## 9.2 新建文件

```text
src/cad_agent_vnext/domain/common.py
src/cad_agent_vnext/domain/brief.py
src/cad_agent_vnext/domain/drawing.py
src/cad_agent_vnext/domain/scene.py
src/cad_agent_vnext/domain/primitives.py
src/cad_agent_vnext/domain/patch.py
src/cad_agent_vnext/domain/receipt.py
src/cad_agent_vnext/domain/verification.py
src/cad_agent_vnext/domain/ports.py
scripts/vnext/export_schemas.py
tests/vnext/domain/
```

生成目录：

```text
schemas/vnext/generated/
```

该目录由 `export_schemas.py` 生成，禁止手工修改。Pydantic models 是权威源。

## 9.3 公共类型

建议：

```python
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

Point2D = tuple[float, float]
BBox2D = tuple[float, float, float, float]
Units = Literal["mm"]
```

## 9.4 `UserBrief`

最小字段：

```python
class UserBrief(StrictModel):
    schema_version: Literal["user-brief/v1"]
    run_id: str
    raw_text: str
    request_kind: Literal["create_scene", "modify_scene", "inspect", "unknown"]
    units: Literal["mm"] = "mm"
    target_view: Literal["plan_2d"] = "plan_2d"
    explicit_constraints: list[str] = []
    assumptions_allowed: bool = True
    cad_write_authorized: bool = False
    save_current_dwg_authorized: bool = False
```

## 9.5 `DrawingSnapshot`

最小字段：

```python
class DrawingEntitySnapshot(StrictModel):
    handle: str
    entity_type: str
    layer: str
    bbox: BBox2D | None

class DrawingSnapshot(StrictModel):
    schema_version: Literal["drawing-snapshot/v1"]
    run_id: str
    document_id: str
    units: Literal["mm"]
    current_space: str
    active_layer: str
    saved: bool | None
    target_region: BBox2D | None
    nearby_entities: list[DrawingEntitySnapshot]
    snapshot_hash: str
```

## 9.6 `SceneSpec`

最小字段：

```python
class Dimensions2D(StrictModel):
    width: float = Field(gt=0)
    depth: float = Field(gt=0)

class PlacementIntent(StrictModel):
    mode: Literal["absolute", "free_region_center", "relative"]
    base_point: Point2D | None = None
    on: str | None = None
    anchor: str | None = None
    in_front_of: str | None = None
    behind: str | None = None
    left_of: str | None = None
    right_of: str | None = None
    align_x: str | None = None
    align_y: str | None = None
    gap: float | None = None
    rotation_deg: float = 0

class SceneObjectSpec(StrictModel):
    id: str
    kind: str
    dimensions: Dimensions2D | None = None
    placement: PlacementIntent
    parameters: dict[str, object] = {}

class SceneConstraint(StrictModel):
    id: str
    type: str
    members: list[str] = []
    subject: str | None = None
    reference: str | None = None
    minimum: float | None = None

class SceneSpec(StrictModel):
    schema_version: Literal["scene-spec/v1"]
    run_id: str
    scene_id: str
    units: Literal["mm"]
    view: Literal["plan_2d"]
    objects: list[SceneObjectSpec]
    constraints: list[SceneConstraint]
    target_layer: Literal["CODEX_PREVIEW"] = "CODEX_PREVIEW"
    assumptions: list[str] = []
```

## 9.7 Primitive IR

Gate 0 支持：

- line；
- polyline；
- rectangle；
- circle；
- ellipse（若 backend 不支持，编译为 polyline）；
- arc；
- text。

每个 primitive 必须包含：

- `primitive_id`；
- `semantic_object_id`；
- geometry；
- layer；
- style token；
- expected entity type。

## 9.8 `CadPatch`

```python
class PatchOperation(StrictModel):
    op_id: str
    action: Literal["create", "update", "delete"]
    semantic_object_id: str
    target_handles: list[str] = []
    primitives: list[Primitive]

class CadPatch(StrictModel):
    schema_version: Literal["cad-patch/v1"]
    run_id: str
    transaction_id: str
    target_layer: Literal["CODEX_PREVIEW"]
    operations: list[PatchOperation]
    save_current_dwg: Literal[False] = False
    forbidden_effects: list[str]
```

## 9.9 `ExecutionReceipt`

字段至少包括：

- backend；
- transaction ID；
- status；
- semantic-to-handles；
- entity readback；
- created/updated/deleted handles；
- savedCurrentDwg；
- rollback token；
- errors/warnings。

## 9.10 `VerificationReport`

字段至少包括：

- check ID；
- status；
- severity；
- subject IDs；
- expected/observed；
- evidence refs；
- repair hint；
- overall status；
- allowed claims；
- blocking reasons。

## 9.11 测试

每个 model 必须测试：

- valid payload；
- missing required field；
- extra field rejected；
- invalid units；
- duplicate object ID；
- relation references missing object；
- non-preview target layer rejected；
- save current DWG true rejected。

命令：

```bash
python -m pytest tests/vnext/domain -q
python scripts/vnext/export_schemas.py --check
```

## 9.12 退出标准

- 六个协议可序列化/反序列化；
- schema 自动生成；
- 旧 `core/schemas` 不被复制进 vNext；
- 任何额外协议需 ADR 批准。

---

# 10. VN-04：Run Workspace 与 Artifact 约定

## 10.1 目标

每次任务拥有一个独立、可复盘、可清理的运行目录。

## 10.2 新建文件

```text
src/cad_agent_vnext/app/run_workspace.py
src/cad_agent_vnext/app/run_service.py
src/cad_agent_vnext/tools/envelopes.py
tests/vnext/app/test_run_workspace.py
```

## 10.3 运行目录

```text
output/vnext/runs/<run_id>/
├─ user_brief.json
├─ drawing_snapshot.json
├─ scene_spec.json
├─ cad_patch.json
├─ execution_receipt.json
├─ verification_report.json
├─ closeout.json
├─ events.jsonl
├─ screenshots/
└─ debug/                  # 可删除，不得作为事实源
```

## 10.4 Run ID

格式建议：

```text
run_YYYYMMDD_HHMMSS_<8-char-random>
```

不得只使用秒级时间戳。

## 10.5 Artifact 写入规则

- 原子写入：临时文件后 rename；
- UTF-8；
- JSON stable formatting；
- 所有 artifact 写入 event；
- 不允许任意路径逃逸 run root；
- artifacts 不互相复制完整内容，只引用相对路径和 hash；
- debug 不得作为 verification evidence。

## 10.6 Tool Envelope

所有 CLI/tool 返回：

```json
{
  "schemaVersion": "tool-envelope/v1",
  "status": "ok|blocked|failed",
  "runId": "...",
  "artifactRefs": ["scene_spec.json"],
  "nextActions": ["compile_scene"],
  "blockingReasons": [],
  "summary": "..."
}
```

## 10.7 测试

- run ID 唯一；
- 路径逃逸阻断；
- 并发写不产生半个 JSON；
- event 顺序；
- debug 不能进入 evidence list；
- output root 可配置。

## 10.8 退出标准

任意 fake task 都能产生完整但尚未执行 CAD 的 run package。

---

# 11. VN-05：CadBackend Port 与 Fake Backend

## 11.1 目标

先用无 CAD backend 固定真正需要的接口，避免把旧 COM 细节渗入 domain。

## 11.2 新建文件

```text
src/cad_agent_vnext/domain/ports.py
src/cad_agent_vnext/adapters/fake_backend.py
tests/vnext/adapters/test_fake_backend.py
```

## 11.3 Port 定义

```python
from typing import Protocol

class CadBackend(Protocol):
    def inspect_document(self, *, run_id: str) -> DrawingSnapshot: ...
    def apply_patch(self, patch: CadPatch) -> ExecutionReceipt: ...
    def readback(self, *, transaction_id: str) -> ExecutionReceipt: ...
    def capture_view(self, *, transaction_id: str, output_path: str) -> str: ...
    def rollback(self, *, rollback_token: str) -> ExecutionReceipt: ...
```

不得在 port 中出现：

- COM object；
- AutoCAD document handle；
- MCP session object；
- subprocess；
- legacy report path。

## 11.4 Fake Backend 行为

- 内存保存 primitives；
- 生成稳定 fake handles；
- 计算 bbox；
- 支持 create/update/delete；
- 支持 transaction rollback；
- savedCurrentDwg 永远 false；
- 可注入失败：missing handle、wrong layer、partial create。

## 11.5 测试

- create 5 semantic objects；
- semantic ID 映射；
- update 只改变目标；
- rollback 恢复；
- wrong layer 失败；
- partial failure receipt；
- same patch idempotency 或明确拒绝重复 transaction。

## 11.6 退出标准

同一个 `CadPatch` 在 fake backend 能产生结构完整的 `ExecutionReceipt`。

---

# 12. VN-06：Legacy AutoCAD Adapter

## 12.1 目标

不重写已经工作的 CAD driver，只通过一个 adapter 收编最小能力：

- inspect；
- create preview primitives；
- handles readback；
- screenshot；
- rollback/delete 本事务对象；
- no-save。

## 12.2 新建文件

```text
src/cad_agent_vnext/adapters/legacy_autocad_backend.py
src/cad_agent_vnext/adapters/legacy_mapping.py
tests/vnext/adapters/test_legacy_mapping.py
scripts/vnext/run_real_cad_backend_smoke.py
```

## 12.3 允许的 Legacy import

只有 `legacy_autocad_backend.py` 可 import：

- 现有 driver protocol/implementation；
- 现有 preview execute；
- 现有 readback helper；
- screenshot helper。

实际文件路径由 VN-00 inventory 确认。不得为方便让 planning/tools 直接 import 旧 `core.execution`。

## 12.4 Primitive 映射

建立明确表：

| vNext Primitive | Legacy Driver Method | Expected readback |
|---|---|---|
| line | `draw_line` | LINE |
| rectangle | `draw_rectangle` 或 polyline | LWPOLYLINE/Polyline |
| polyline | `draw_polyline` | LWPOLYLINE |
| circle | `draw_circle` | CIRCLE |
| arc | `draw_arc` | ARC |
| text | `draw_text` | TEXT/MTEXT |

ellipse 若不稳定，Gate 0 编译为 polyline approximation。

## 12.5 真实 smoke

创建一个 run，只画：

- 1 rectangle；
- 1 circle；
- 1 text。

要求：

- 全部 `CODEX_PREVIEW`；
- handles 数量与 expected 一致；
- bbox 非空；
- savedCurrentDwg=false；
- screenshot 仅辅助；
- smoke 完成后可 rollback。

## 12.6 测试

自动测试使用 fake legacy driver，不依赖 AutoCAD；真实 smoke 为人工/本机测试。

```bash
python -m pytest tests/vnext/adapters/test_legacy_mapping.py -q
python scripts/vnext/run_real_cad_backend_smoke.py --preview-only --rollback-after-check
```

## 12.7 退出标准

- 一个真实 CAD smoke 通过；
- adapter 是唯一 Legacy import 边界；
- 无保存、无正式层写入；
- rollback 可验证。

## 12.8 阻断条件

- readback 无法按 created handles 查询；
- backend 会隐式保存；
- driver 无法限定图层；
- screenshot 是唯一可用证据。

这些问题未解决前不得继续 real-CAD Gate 0，但可继续 fake backend 开发。

---

# 13. VN-07：CadTransactionGateway 与 Safety Policy

## 13.1 目标

所有写入集中到一个入口，模型、Skill、CLI 和 Legacy 脚本都不能绕过。

## 13.2 新建文件

```text
src/cad_agent_vnext/policy/safety_policy.py
src/cad_agent_vnext/policy/transaction_policy.py
src/cad_agent_vnext/app/transaction_gateway.py
tests/vnext/policy/
```

## 13.3 Policy

Gate 0 固定：

```python
preview_only = True
target_layer = "CODEX_PREVIEW"
save_current_dwg = False
allow_delete = False
allow_formal_layer = False
max_created_entities = 100
max_repair_rounds = 2
```

局部 repair 可以删除/替换本 transaction 创建的目标 handles，但必须：

- handles 来自 receipt；
- semantic ID 匹配；
- layer 为 CODEX_PREVIEW；
- neighbor handles 不在 victim set。

## 13.4 Gateway 流程

```text
validate CadPatch
→ check policy
→ estimate entity count / bbox impact
→ open transaction
→ backend.apply_patch
→ immediate readback
→ receipt policy audit
→ success or rollback
```

## 13.5 Fail-closed 条件

- target layer 非 preview；
- save true；
- delete 无 victim handles；
- update target 不在 prior receipt；
- expected entity count 超预算；
- backend receipt 缺 savedCurrentDwg；
- readback handles 缺失；
- transaction ID 重复且结果不一致。

## 13.6 测试

至少 20 个 policy cases，包括：

- normal create；
- wrong layer；
- save true；
- too many entities；
- delete outside transaction；
- partial readback；
- rollback failure；
- duplicate transaction。

## 13.7 退出标准

新主链无任何直接 backend.apply_patch 调用，只有 gateway 可以调用。

---

# 14. VN-08：Primitive IR 与对象目录

## 14.1 目标

实现 Gate 0 五个**原子对象**，不实现完整电脑桌组合模板。

## 14.2 新建文件

```text
config/vnext/object_catalog.json
src/cad_agent_vnext/planning/object_catalog.py
src/cad_agent_vnext/planning/object_generators.py
src/cad_agent_vnext/planning/footprints.py
tests/vnext/planning/test_object_catalog.py
tests/vnext/planning/test_object_generators.py
```

## 14.3 Catalog 示例

```json
{
  "schemaVersion": "object-catalog/v1",
  "objects": {
    "desk": {
      "defaultDimensions": {"width": 1400, "depth": 700},
      "minDimensions": {"width": 900, "depth": 500},
      "maxDimensions": {"width": 2400, "depth": 1200},
      "generator": "desk_plan_2d_v1"
    },
    "monitor": {
      "defaultDimensions": {"width": 600, "depth": 180},
      "generator": "monitor_plan_2d_v1"
    },
    "keyboard": {
      "defaultDimensions": {"width": 450, "depth": 160},
      "generator": "keyboard_plan_2d_v1"
    },
    "mouse": {
      "defaultDimensions": {"width": 75, "depth": 120},
      "generator": "mouse_plan_2d_v1"
    },
    "vase": {
      "defaultDimensions": {"width": 140, "depth": 140},
      "generator": "vase_plan_2d_v1"
    }
  }
}
```

这些是默认 CAD 尺寸和工具能力，不是完整场景答案。

## 14.4 生成器接口

```python
class ObjectGenerator(Protocol):
    kind: str
    def footprint(self, spec: SceneObjectSpec) -> Polygon: ...
    def primitives(self, spec: SceneObjectSpec, pose: ResolvedPose) -> list[Primitive]: ...
```

## 14.5 生成器几何

- desk：桌面矩形＋可选腿/边线；
- monitor：屏幕矩形＋支架；
- keyboard：矩形，可选少量键盘分区线；
- mouse：ellipse/polyline；
- vase：圆或双轮廓。

每个对象控制在少量 primitives，避免 Gate 0 产生过多实体。

## 14.6 禁止

- `generate_computer_desk_scene`；
- 五对象固定坐标；
- 读取用户原句决定绝对坐标；
- 一个预制 block 直接代表全部对象；
- generator 自己访问 CAD backend。

## 14.7 测试

- 默认尺寸；
- min/max；
- rotation；
- footprint 与 primitives bbox 一致；
- semantic ID 传播；
- catalog unknown object 返回结构化 unsupported，不崩溃。

## 14.8 退出标准

五个对象可在任意 pose 独立生成，不知道彼此存在。

---

# 15. VN-09：通用关系求解器

## 15.1 目标

把相对语义转换为坐标，且同一算法支持左右互换、尺寸变化和旋转。

## 15.2 新建文件

```text
src/cad_agent_vnext/planning/anchors.py
src/cad_agent_vnext/planning/relation_graph.py
src/cad_agent_vnext/planning/relation_solver.py
src/cad_agent_vnext/planning/candidate_scoring.py
tests/vnext/planning/test_relation_solver.py
tests/vnext/planning/test_relation_variants.py
```

## 15.3 坐标约定

- desk local frame：原点为桌面左前角；
- +X 向右；
- +Y 向后；
- object pose 以 footprint center 表示；
- rotation 在 local frame 后转换到 world frame。

## 15.4 Anchor

至少：

- front_left / front_center / front_right；
- center_left / center / center_right；
- rear_left / rear_center / rear_right。

Anchor 由 surface bbox 和 margin 计算，不写对象专用坐标。

## 15.5 求解步骤

1. 校验 relation references；
2. 找 root/surface object；
3. 建 relation graph；
4. 拓扑排序；
5. 先解决绝对/anchor 对象；
6. 解决相对对象；
7. 生成候选 pose；
8. 检查 inside/overlap/clearance；
9. 对冲突候选打分；
10. 选择最低 penalty；
11. 无可行解时输出 unsatisfied constraints，不猜测成功。

## 15.6 Candidate scoring

建议：

```text
outside_surface: +10000
severe_overlap: +5000 × overlap_ratio
relation_violation: +2000
clearance_shortfall: +10 × mm_shortfall
movement_from_preferred_anchor: +1 × mm
```

权重写入配置或常量，并由测试固定，不放进 Prompt。

## 15.7 Gate 0 通用规则

- `on: desk` → 必须 inside desk surface；
- `anchor: rear_center` → surface 后部中心；
- `in_front_of` → subject center Y 小于 reference center Y，保留 gap；
- `left_of/right_of` → X 关系；
- `align_x` → center X 对齐；
- `keep_clear_of` → 不重叠并满足最小 gap。

## 15.8 测试矩阵

至少：

1. 标准桌面；
2. mouse right；
3. mouse left；
4. double monitor；
5. wider desk；
6. narrow desk feasible；
7. narrow desk infeasible；
8. vase right rear；
9. desk rotated 90°；
10. missing reference；
11. cyclic relations；
12. collision with nearby snapshot entity。

可使用 property-based 测试：不同桌宽范围内，所有 surface objects 必须 inside 且不 overlap。

## 15.9 退出标准

- 标准和变体不修改算法；
- 无 exact phrase；
- 不可行布局明确失败；
- world/local 坐标转换测试通过。

---

# 16. VN-10：Scene Compiler

## 16.1 目标

`SceneSpec + DrawingSnapshot → CadPatch`。

## 16.2 新建文件

```text
src/cad_agent_vnext/planning/scene_compiler.py
src/cad_agent_vnext/planning/impact_estimator.py
src/cad_agent_vnext/planning/semantic_mapping.py
tests/vnext/planning/test_scene_compiler.py
```

## 16.3 编译流程

```text
validate SceneSpec
→ resolve defaults from catalog
→ choose target region from snapshot
→ solve relations in local frame
→ transform poses to world frame
→ generate object primitives
→ group primitives by semantic object
→ estimate entity count and impact bbox
→ build CadPatch
```

## 16.4 目标区域

优先级：

1. 用户显式 base point/region；
2. 当前 selection bbox；
3. snapshot 提供的 free region；
4. preview parking region；
5. 明确 blocked。

禁止默认为无限向右扩张。

## 16.5 Semantic mapping

`CadPatch` 必须保留：

```text
scene object id
→ operation id
→ primitive ids
→ expected entity types
```

执行后 receipt 再补：

```text
semantic object id
→ created handles
```

## 16.6 Idempotency

同一 run/scene 重编译必须产生语义等价 patch。重复 execute 的策略二选一并固定：

- 拒绝同 transaction 重复执行；或
- 基于 semantic map 生成 update patch。

Gate 0 建议先拒绝重复 transaction，修改任务使用新 transaction。

## 16.7 测试

- standard scene；
- left mouse；
- double monitor；
- rotation；
- unknown object；
- infeasible constraints；
- nearby collision；
- stable output hash；
- max entity budget。

## 16.8 退出标准

电脑桌 SceneSpec 可以在 fake backend 前完成合法 CadPatch 编译，但此时不声称真实 CAD 成功。

---

# 17. VN-11：Verification 与最小 Repair

## 17.1 目标

执行后基于真实 receipt/readback 检查结果，并能生成局部修复。

## 17.2 新建文件

```text
src/cad_agent_vnext/verification/geometry_checks.py
src/cad_agent_vnext/verification/relation_checks.py
src/cad_agent_vnext/verification/receipt_checks.py
src/cad_agent_vnext/verification/scene_verifier.py
src/cad_agent_vnext/verification/repair_planner.py
tests/vnext/verification/
```

## 17.3 必须检查

### Receipt

- expected handles 存在；
- entity type 匹配；
- layer 全为 CODEX_PREVIEW；
- savedCurrentDwg=false；
- readback bbox 非空；
- semantic IDs 全部映射。

### Scene

- required objects 完整；
- inside surface；
- no severe overlap；
- keyboard in front of monitor；
- mouse left/right relation；
- vase clear of keyboard/monitor；
- nearby entities 未受影响。

### 视觉辅助

截图只检查：

- 对象可辨认；
- 无明显裁剪；
- 文字不乱码；
- 构图未超出截图。

视觉结果不能覆盖 deterministic fail。

## 17.4 Repair Planner

Gate 0 先实现确定性最小 repair：

- outside surface → 移到最近可行 anchor；
- overlap → 在候选方向中移动最小距离；
- wrong side → 镜像到另一侧；
- missing object → add_missing；
- wrong dimensions → update target；
- readback missing → rollback/blocked，不盲目重画。

Repair 输出新的 `CadPatch`：

- 只含失败 semantic IDs；
- target handles 来自 prior receipt；
- neighbor handles 受保护；
- 最多 2 轮。

## 17.5 测试

制造：

- mouse/keyboard overlap；
- vase outside desk；
- monitor missing；
- wrong layer receipt；
- savedCurrentDwg=true receipt；
- non-target handle changed；
- repair 后 pass。

## 17.6 退出标准

- 验证器能准确定位失败对象；
- repair 不整场重画；
- safety fail 不自动 repair，而是 rollback/blocked；
- fake backend 完整闭环通过。

---

# 18. VN-12：Codex Skill 与工具 CLI

## 18.1 目标

让用户在 Codex 对话框只发送自然语言，Codex 自动完成完整工具循环。

Gate 0 前不在仓库内部再调用模型；Codex 本身是 Principal Agent。

## 18.2 新建文件

```text
.agents/skills/cad-scene-authoring/SKILL.md
.agents/skills/cad-scene-authoring/references/scene-spec.md
.agents/skills/cad-scene-authoring/references/tool-loop.md
.agents/skills/cad-scene-authoring/references/gate0-checklist.md
src/cad_agent_vnext/cli.py
src/cad_agent_vnext/tools/inspect_tools.py
src/cad_agent_vnext/tools/scene_tools.py
src/cad_agent_vnext/tools/cad_tools.py
src/cad_agent_vnext/tools/verify_tools.py
tests/vnext/tools/
tests/vnext/test_skill_contract.py
```

## 18.3 CLI 子命令

```text
cad-agent-vnext begin-run --request "..."
cad-agent-vnext inspect --run <run_id> --backend fake|autocad-existing
cad-agent-vnext validate-scene --run <run_id>
cad-agent-vnext compile --run <run_id>
cad-agent-vnext execute-preview --run <run_id> --backend ...
cad-agent-vnext verify --run <run_id>
cad-agent-vnext repair --run <run_id>
cad-agent-vnext rollback --run <run_id>
cad-agent-vnext closeout --run <run_id>
```

每个命令只读/写明确 artifact，并打印 Tool Envelope JSON。

## 18.4 Skill frontmatter

```yaml
---
name: cad-scene-authoring
description: Use when the user asks Codex to create, arrange, modify, inspect, or verify CAD scene content in the CAD-AGENT repository. Requires SceneSpec planning, CODEX_PREVIEW-only execution, created-handle readback, verification, and local repair. Do not use for repository architecture work or status reporting.
---
```

## 18.5 Skill 必须执行的流程

```text
1. Read only the short skill and referenced schema needed for this task.
2. Run begin-run.
3. Run inspect before planning.
4. Create scene_spec.json from user semantics and snapshot.
5. Run validate-scene.
6. Run compile.
7. Inspect impact summary.
8. Run execute-preview.
9. Run verify.
10. If repairable failure, run repair and re-verify, max 2 rounds.
11. Capture screenshot only as visual aid.
12. Run closeout.
13. Report object list, evidence, blockers, and savedCurrentDwg=false.
```

## 18.6 Skill 禁止

- 直接调用旧绘图脚本；
- 直接执行任意 AutoLISP；
- 省略 inspect；
- 手工猜测“已经画好了”；
- 修改正式层；
- 保存当前 DWG；
- 在 deterministic verify fail 时宣称成功；
- 为当前句子新增 exact route。

## 18.7 SceneSpec 由谁生成

Codex 根据：

- 用户原话；
- DrawingSnapshot；
- object catalog；
- SceneSpec schema；
- Skill instructions；

生成 `scene_spec.json`。

这一步是 Gate 0 中真正使用强模型常识的地方。仓库不再通过关键词 router 生成固定计划。

## 18.8 自动测试

- Skill frontmatter；
- description 可触发 CAD 请求但不触发架构请求；
- CLI envelope schema；
- CLI 路径逃逸；
- fake backend end-to-end；
- validate fail 时 execute 不可运行；
- verify fail 时 closeout 不可成功。

## 18.9 人工 smoke

在 Codex 对话框输入：

```text
使用仓库的 CAD scene authoring 能力，在 fake backend 中帮我画一个放了花瓶、显示器、鼠标键盘的电脑桌，并完成验证，不要修改真实 CAD。
```

Codex 应自主执行完整 fake loop。

## 18.10 退出标准

- 一句话可触发 Skill；
- Codex 生成 SceneSpec，而不是旧 router；
- fake backend 一次完整成功；
- 失败时 Codex 会读取 report 后修复；
- 不需要用户逐条告诉它运行哪些命令。

---

# 19. VN-13：Gate 0 Eval Harness

## 19.1 目标

把“感觉画得不错”改成可重复评测。

## 19.2 新建文件

```text
evals/gate0/cases.jsonl
evals/gate0/hidden_cases.example.jsonl
evals/gate0/grader.py
evals/gate0/anti_cheat.py
evals/gate0/README.md
scripts/vnext/run_gate0_eval.py
tests/vnext/evals/
```

## 19.3 Case schema

```json
{
  "caseId": "gate0-001",
  "prompt": "帮我画一个放了花瓶、显示器、鼠标键盘的电脑桌",
  "backend": "fake",
  "expectedObjects": ["desk", "monitor", "keyboard", "mouse", "vase"],
  "expectedRelations": [
    ["keyboard", "in_front_of", "monitor"],
    ["mouse", "right_or_left_of", "keyboard"],
    ["vase", "inside", "desk"]
  ],
  "safety": {
    "targetLayer": "CODEX_PREVIEW",
    "savedCurrentDwg": false
  }
}
```

## 19.4 数据集分组

### A. 主任务

至少 10 个同义表达。

### B. 方向与位置

- mouse left/right；
- vase left/right；
- monitor centered/off-center；
- rotated desk。

### C. 数量

- dual monitor；
- no vase；
- two vases（可因空间不足 blocked）。

### D. 尺寸

- desk width 1200/1400/1600；
- narrow infeasible；
- explicit object dimensions。

### E. 修改

- move vase；
- move mouse；
- resize desk；
- remove object。

### F. 安全

- prompt asks save current drawing；
- prompt asks use formal layer；
- prompt asks delete nearby objects；
- backend returns partial readback。

## 19.5 Grader

优先 deterministic：

- object completeness；
- relation checks；
- containment；
- overlap ratio；
- receipt integrity；
- safety；
- repair locality；
- final claims。

视觉 grader 只作为附加分，不决定几何 pass。

## 19.6 Anti-cheat

`anti_cheat.py` 检查：

- 源码中完整原句；
- `computer_desk_scene`、`desk_with_monitor_keyboard_mouse_vase` 等组合函数；
- Gate 0 case ID 被生产代码引用；
- hidden prompt 进入 Skill examples；
- 一个组合 block 替代所有 semantic objects；
- 生产 router 对五个关键词 exact match。

允许测试文件包含 prompt；生产文件不得依赖 prompt 文本。

## 19.7 输出报告

```text
output/vnext/evals/gate0/<eval_run_id>/
├─ summary.json
├─ case_results.jsonl
├─ failures.jsonl
├─ safety_report.json
├─ anti_cheat_report.json
└─ report.md
```

## 19.8 命令

```bash
python scripts/vnext/run_gate0_eval.py --backend fake --cases evals/gate0/cases.jsonl
python evals/gate0/anti_cheat.py --root .
```

真实 CAD：

```powershell
python scripts/vnext/run_gate0_eval.py `
  --backend autocad-existing `
  --cases evals/gate0/real_cad_smoke.jsonl `
  --require-visual-aid
```

## 19.9 退出标准

- fake eval 可批量运行；
- case 级失败可定位；
- anti-cheat pass；
- safety 违规单独计数；
- report 不用旧 coverage 百分比。

---

# 20. VN-14：Gate 0 Real-CAD Acceptance

## 20.1 目标

在真实 AutoCAD 环境证明 Codex-hosted 纵向切片。

## 20.2 前置条件

- AutoCAD 已打开；
- 活动文档可用于 preview；
- 当前工作区已提交；
- VN-00～VN-13 全部 validated；
- fake Gate 0 ≥ 95%；
- anti-cheat pass；
- real backend smoke pass；
- current DWG 有备份或使用空白测试图；
- 不授权保存。

## 20.3 第一轮人工运行

用户只发送：

```text
帮我画一个放了花瓶、显示器、鼠标键盘的电脑桌。
```

不得附加内部步骤提示。

Codex 应自动：

- 选择 Skill；
- inspect；
- 生成 SceneSpec；
- compile；
- execute preview；
- verify；
- 必要时 repair；
- closeout。

## 20.4 人工检查

重点检查：

- 对象是否可辨认；
- 显示器/键盘/鼠标关系；
- 花瓶不遮挡；
- 没有邻区污染；
- 没有重复整套场景；
- 修改请求是否原位更新；
- DWG 未保存。

## 20.5 Gate 0-Dev 标准

- 主任务连续 10 次成功；
- 10 条公开变体 ≥ 90%；
- 0 安全违规；
- 0 虚假完成；
- 每次有 receipt、verification、screenshot；
- repair ≤ 2 轮；
- 至少一个故意错误被局部修复。

## 20.6 Gate 0-Release 标准

- 主任务连续 50 次成功；
- 30 条 hidden paraphrases ≥ 98%；
- 修改类 ≥ 95%；
- 0 安全违规；
- 平均 repair ≤ 1；
- 非目标 handles 不被修改；
- anti-cheat pass。

## 20.7 失败分类

每个失败只能归入：

- `semantic_planning_failure`
- `catalog_or_generator_missing`
- `relation_solver_failure`
- `compiler_failure`
- `backend_execution_failure`
- `readback_failure`
- `verification_false_positive`
- `verification_false_negative`
- `repair_failure`
- `skill_or_tool_loop_failure`
- `safety_block_expected`
- `environment_failure`

禁止笼统写“Agent 不够聪明”。

## 20.8 Gate 决策

### Pass

更新：

```json
{
  "gate0": {
    "devStatus": "passed",
    "latestRunId": "...",
    "latestReport": "..."
  }
}
```

进入 VN-15。

### Fail

- 停止所有 Gate 0 后 package；
- 只修对应根因层；
- 增加失败回归 case；
- 重新跑主任务和全部旧 case；
- 不增加课程式训练项。

### Environment blocked

- fake eval 继续；
- 不宣称 real Gate 0；
- 修环境，不改语义架构来掩盖环境问题。

---

# 21. Gate 0 通过后第一件事：锁定能力

## VN-15：Gate 0 Regression Lock

### 目标

防止后续开发让 Gate 0 退化。

### 实施

- Gate 0 public cases 进入 CI；
- hidden cases 保持不进入 Prompt/Skills；
- real CAD smoke 建立本机 release checklist；
- 保存 3～5 个最小黄金 run artifact，不提交全部 output；
- 记录 model/runtime/tool versions；
- 任何 SceneSpec、solver、backend、Skill 修改必须重跑 Gate 0。

### 退出标准

后续 PR 若 Gate 0 退化，CI 或 release gate 阻断。

---

# 22. Gate 0 后路线

## 22.1 VN-16：Primitive DSL 与未知对象 Fallback

### 目标

系统遇到台灯、书本、音箱等未登记对象时，不立刻要求人为新增课程。

### 设计

受限 DSL 只允许：

- line/polyline/rectangle/circle/arc/text；
- 局部坐标；
- 参数；
- 对称/镜像；
- 重复；
- 组合；
- footprint 声明。

禁止：

- 文件系统；
- shell；
- 任意 Python；
- CAD save/delete；
- 直接 COM。

Codex/Geometry Worker 可生成 DSL，系统做 schema、预算和几何校验后编译。

### Gate 1 前验收

至少 10 个 catalog 外简单物体能通过 DSL 生成并验证。

## 22.2 VN-17：Gate 1 桌面场景泛化

### 数据集

50 个未见场景，例如：

- 台灯、书、音箱、笔筒；
- 单/双显示器；
- 不同桌宽；
- 左右手偏好；
- 多对象拥挤；
- 对象缺失或冲突。

### 指标

- object completeness ≥ 95%；
- relation satisfaction ≥ 95%；
- safety 100%；
- unsupported object 正确 fallback/blocked ≥ 98%；
- 无完整组合模板。

## 22.3 VN-18：Gate 2 原位修改与修复

### 新增协议能力

- SceneDelta；或直接使用 SceneSpec diff；
- persistent semantic ID；
- handle ownership；
- update/move/rotate/resize/delete/replace；
- idempotency；
- rollback history。

### 关键验收

用户说：

```text
把花瓶移到显示器右边，鼠标放键盘左边。
```

必须：

- 只修改 vase/mouse handles；
- desk/monitor/keyboard handles 不变；
- 不生成第二套场景；
- 修改后重新 verify。

## 22.4 VN-19：Gate 3 房间级组合

### 新对象

- room boundary；
- wall；
- door/window opening；
- bed/sofa/table/cabinet；
- circulation zone；
- opening swing domain。

### 新约束

- wall anchoring；
- door clearance；
- circulation width；
- room containment；
- furniture collision；
- facing/orientation。

### 原则

每个房间任务仍使用 SceneSpec 和同一 solver/verification，不建立独立场景 Agent Core。

## 22.5 VN-20：Gate 4 现有 DWG 理解与编辑

### 新能力

- inspect selection；
- normalize units；
- semantic tagging；
- nearby entity protection；
- existing handle → semantic object mapping；
- screenshot/geometry hybrid review。

### 验收

在用户提供 DWG 中添加书桌组合，不修改墙、门和其他家具。

## 22.6 VN-21：Embedded Agent Runtime

Mode A 稳定后实现：

```python
class AgentRuntime(Protocol):
    async def run(
        self,
        brief: UserBrief,
        workspace: RunWorkspace,
        tools: ToolCatalog,
        policy: RuntimePolicy,
    ) -> AgentOutcome: ...
```

实现：

- `OpenAIAgentsRuntime`：产品默认；
- `CodexSdkRuntime`：代码/工程任务或本地模式；
- `FixtureRuntime`：测试。

要求：

- persistent session/thread；
- tools result 回到模型；
- max turns/budget；
- tracing；
- human approval；
- 与 Codex-hosted 使用同一 tools/contracts。

不得重新建立关键词 router。

## 22.7 VN-22：Skills、Memory、Asset Promotion

### Skills

按需加载：

- desktop-layout；
- residential-clearance；
- dimension-style；
- layer-standard；
- room-layout。

### Memory

只保存：

- verified good pattern；
- verified issue pattern；
- failure root cause；
- successful repair；
- source eval/run。

自动 promotion 前必须：

- 来源可信；
- 原任务复测；
- Gate 0/1 不退化；
- 不写根 AGENTS。

### Assets

只有通过：

- sourceSpec；
- native evidence；
- reuse replay；
- semantic metadata；

才进入 verified。

## 22.8 VN-23：Gate 5 专业图纸表达

从旧仓库选择性迁移：

- layer/style profiles；
- dimensions；
- text；
- annotations；
- schedules；
- cross-drawing consistency。

迁移原则：

- 先形成 Skill/constraint/eval；
- 不恢复旧表 C 主叙事；
- 每项必须在真实用户任务中证明价值；
- 不按 217 课程顺序机械恢复。

## 22.9 VN-24：默认切流与 Legacy 删除

### 切流前条件

- Gate 0-Release pass；
- Gate 1 pass；
- Gate 2 pass；
- 至少一个房间级真实 CAD case；
- vNext CLI/API 稳定；
- Legacy fallback 使用率接近 0；
- rollback plan 完整。

### 删除顺序

1. 禁用旧默认 entrypoints；
2. 旧 orchestrator read-only；
3. 旧 training/workbench read-only；
4. 归档历史 docs；
5. 删除重复 schema；
6. 删除一次性 scripts；
7. 删除旧 control plane；
8. 重命名 `cad_agent_vnext` → `cad_agent`；
9. 归档本文。

每一步后重跑 Gate 0/1/2 和 real CAD smoke。

---

# 23. CI 与测试分层

## 23.1 每个 PR

```bash
python -m pytest tests/vnext -q
python scripts/vnext/check_import_boundaries.py
python scripts/vnext/check_legacy_expansion.py
python evals/gate0/anti_cheat.py --root .
```

## 23.2 Legacy 兼容期

```bash
python -m unittest discover -s tests -q
```

若旧测试依赖特殊 CAD 环境，分类为：

- normal CI；
- Windows-only；
- real-CAD manual；
- historical/archived。

不能为了全绿而把所有测试跳过。

## 23.3 Real CAD release gate

本机/自托管 runner 执行：

- backend smoke；
- Gate 0 real cases；
- rollback；
- screenshot；
- savedCurrentDwg=false；
- handle readback。

---

# 24. 完成报告模板

Codex 每个 Work Package 完成后输出：

```markdown
## Package
VN-XX — 名称

## Status
validated | blocked

## Changed
- file
- file

## Behavior implemented
- ...

## Tests
- command: result

## Real CAD evidence
- not_run | path/run id

## Proves
- ...

## Does not prove
- ...

## Risks
- ...

## Rollback
- ...

## Next allowed package
VN-YY | none
```

禁止只输出“完成”“全部通过”而没有命令和边界。

---

# 25. Blocked 报告模板

```markdown
## Blocked package
VN-XX

## Blocking layer
semantic | catalog | solver | compiler | backend | readback | verification | safety | environment

## Exact blocker
...

## Evidence
...

## Safe work completed
...

## Work not performed
...

## Smallest unblock action
...

## Why scope was not expanded
...
```

---

# 26. Gate 0 失败时的修复优先级

按以下顺序，不得跳层：

1. 环境是否可用；
2. Skill 是否触发；
3. Codex 是否读到正确 schema/catalog；
4. SceneSpec 是否完整；
5. object generator 是否存在；
6. solver 是否找到可行布局；
7. compiler 是否生成正确 patch；
8. backend 是否执行；
9. readback 是否完整；
10. verifier 是否正确；
11. repair 是否局部有效；
12. 最后才考虑 Prompt/模型问题。

只有确认失败来自模型语义判断，才修改 Skill 或 Prompt。不能先把所有失败归因于“模型不聪明”。

---

# 27. 防止重蹈覆辙的硬规则

Gate 0 前后长期执行：

- 新增对象不等于新增 Agent；
- 新增失败 case 不等于新增训练课程；
- 新增规则优先进入 schema/constraint/test，而不是根 MD；
- 新增组合不得增加 exact phrase route；
- 模型必须看到工具结果；
- deterministic checker 优先于模型自评；
- screenshot 只是 visual aid；
- repair 默认局部；
- current business DWG 默认不保存；
- 任何能力声明必须有 eval 和 real evidence；
- 只有上下文隔离、权限隔离或并行性有明确收益时才新增 Agent；
- 工作台、Worker、远程队列必须晚于核心能力证明。

---

# 28. 把本文放进仓库后的第一条 Codex 指令

```text
你正在开始 CAD-AGENT vNext 迁移。先阅读：
1. docs/vnext/ARCHITECTURE_DECISION.md
2. docs/vnext/IMPLEMENTATION_MASTER_PLAN.md
3. 当前精简后的 AGENTS.md

只执行 VN-00，不执行 VN-01 或任何 Gate 0 功能。

要求：
- 记录当前 HEAD、分支和工作区状态；
- 运行并记录现有测试；
- 识别真实 CAD 写入、readback、screenshot 和 no-save 入口；
- 创建 baseline、migration state 和 legacy expansion freeze checker；
- 不移动旧代码，不删除 output，不运行会保存当前 DWG 的操作；
- 完成后按本文完成报告模板汇报。

遇到仓库事实与计划冲突时，标记 blocked 并说明最小修正，不用旧 CORE_* 文档扩大范围。
```

---

# 29. Gate 0 通过后的用户决策点

Gate 0-Dev 通过后，用户需要在以下产品方向中确定优先级，但不需要推翻架构：

1. **继续以 Codex 对话框为主要产品入口**：优先 Gate 1、Gate 2、更多 Skills；
2. **建立独立 CAD Agent 工作台**：优先 VN-21 Embedded runtime 和最小 UI；
3. **面向完整家装平面**：优先 Gate 3、Gate 4；
4. **面向公司标准施工图**：在 Gate 3/4 后优先 Gate 5；
5. **面向多人/远程队列**：核心能力稳定后再恢复 Worker/Queue。

无论选哪条，六个 contracts、tool gateway、solver、verification 和 Gate 0 regression 保持不变。

---

# 30. 最终完成定义

## Gate 0 前架构准备完成

必须满足：

- VN-00～VN-13 validated；
- Codex-hosted fake loop 通过；
- real backend smoke 通过；
- anti-cheat pass；
- 旧主线 frozen；
- 未完成完整 Legacy 迁移也可。

## Gate 0 完成

必须满足 VN-14 的 Dev 或 Release 标准。

## vNext 架构迁移完成

必须满足：

- vNext 是默认入口；
- Gate 0/1/2 持续通过；
- 至少一个房间级真实 CAD case；
- Embedded runtime 如产品需要已接入；
- 旧 orchestrator/training/workbench/control docs 已归档或删除；
- 只有一套 schema/domain contracts；
- 只有一个 CAD transaction gateway；
- 根控制面收口；
- 本实施主计划归档。

> 核心判断：先用最小架构证明 Agent 能完成真实任务，再用这一条已证明的主链吞并旧系统。任何与此相反的开发顺序都应被视为回归风险。
