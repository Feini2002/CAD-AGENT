# Asset Intake Template

用于“用户给标准图库文件夹 / 截图 / 描述 / 参考块”的训练入口。Intake 的目的不是让系统当场学会对象，而是把参考资料先编译成可检索、可审计、可晋升的 `reference_only` 候选资产。

## 默认口径

用户不需要先填表。用户最小输入可以只有两项：

```text
文件夹：standard_cad_library_raw/<source_slug>/original/
一句说明：例如“这是住宅家具图库，主要是沙发和床的平面 CAD 块”
```

Agent 默认先自动扫描文件结构、文件名、扩展名和用户一句说明，生成 `source_note`、`reference_asset`、`agent_inferred_annotations` 和检索入口。缺失或不可靠字段不阻断 intake，统一写成 `unknown` 或 `reference_only`。

推荐命令：

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_asset_raw_intake.py --source-slug <source_slug> --description "这批大概是什么" --write
```

## Agent 自动推断字段

```text
source_slug: 来自 raw 批次文件夹名
file_inventory: 扫描 original/ 下的有效文件
source_type: 默认 user_provided
license_status: 默认 unknown
usage_boundary: 默认 reference_only
privacy_boundary: 默认 raw
domain: 从文件夹名、文件路径和说明推断；不确定则 generic
object_tags: 从文件夹名、文件名和说明推断；不确定则 ["unknown"]
part_tags: 从 object_tags 的常识默认值推断；不确定则 []
style_tags: 从文件夹名、文件名和说明推断；不确定则 []
view_type: plan / elevation / perspective / detail；不确定则 unknown
review_status: agent_inferred
```

## 用户只需确认的字段

这些字段重要，但不是启动前置条件：

```text
这批资料大概是什么对象？
哪些对象优先看？
是否有明确禁止同步或保密要求？
是否要把 license_status 从 unknown 改成 allowed / restricted / owned 等？
```

如果用户没有补充，Agent 仍可继续生成 reference intake，但必须保持保守边界：`unknown`、`reference_only`、`agent_inferred`。

## 本轮应派生产物

```text
standard_cad_library_raw/<source_slug>/source_note.md
libraries/reference_library/sources/<source_slug>.md
libraries/reference_library/manifests/<source_slug>/ref.*.json
libraries/reference_library/annotations/<source_slug>/ann.*.json
libraries/knowledge/source_notes/<source_slug>.md
runs/roundN_retrieval_pack.json（进入具体训练案例时再生成）
evidence_boundary.md 或 libraries/knowledge/evidence_boundaries/*（晋升前必须补齐）
runs/roundN_learning_promotion.json（只有 promotion gate 时才生成）
runs/training_state.json（进入案例训练时才生成）
```

## 交付边界

- `reference_asset` 只能证明“系统看过并记录了参考边界”。
- `agent_inferred_annotations` 是候选标注，不等于用户确认。
- `retrieval_pack` 只能证明“已查本地资产和常识”。
- raw scan 不等于能力证明，不改变表 C。
- 任何 raw / reference 内容都不能直接进入 `libraries/system_library/`。
- `case_verified` 需要真实 `CODEX_PREVIEW`、审计、自检和用户 pass。
- `system_verified` 需要多变体 / benchmark / 负例或第二案例。
