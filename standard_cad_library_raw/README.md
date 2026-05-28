# Standard CAD Library Raw

这里放用户下载的标准 CAD 图库原始文件。这个目录是仓库根目录下的受控 raw reference input，允许随 git 在家里和公司之间迁移。

## 你需要做什么

最小操作只有两步：

1. 把同一批资料放进 `standard_cad_library_raw/<source_slug>/original/`。
2. 告诉 Agent 一句大概内容，例如“这是住宅家具图库，主要是沙发、床、桌椅的平面块”。

你不需要先填来源、授权、对象范围、图纸类型表格。Agent 会先自动扫描文件夹、文件名、扩展名和一句说明，生成保守的 reference intake 草稿；无法可靠判断的字段写 `unknown`，只能参考的内容写 `reference_only`。

## 这是什么

- 下载的 DWG / DXF / PDF / 图片 / 压缩包等原始标准图库资料。
- 用于帮助系统整理对象常识和参考边界的 raw input。
- 后续 `libraries/reference_library/`、`libraries/knowledge/`、`libraries/benchmarks/` 和 `libraries/system_library/` 的来源之一。

## 这不是什么

- 不是系统自产图库。
- 不是已经通过验证的 CAD 能力。
- 不是可以绕过 `reference_asset`、常识摘要、可执行检查和 promotion gate 的生产资产。
- 不是表 C 或真实 CAD 实力证明。

## 推荐批次结构

```text
standard_cad_library_raw/
  <source_slug>/
    original/        # 下载文件原样放这里
    preview/         # 可选截图或轻量预览
    source_note.md   # Agent 自动生成或后续人工修订
```

示例：

```text
standard_cad_library_raw/residential-furniture-pack-202606/original/
standard_cad_library_raw/residential-furniture-pack-202606/source_note.md
```

## 自动 intake

推荐让 Agent 运行：

```powershell
$py = "$env:USERPROFILE\.codex\mcp\CAD-MCP\.venv\Scripts\python.exe"
& $py scripts\run_asset_raw_intake.py --source-slug <source_slug> --description "这批大概是什么" --write
```

它会生成：

```text
standard_cad_library_raw/<source_slug>/source_note.md
libraries/reference_library/sources/<source_slug>.md
libraries/reference_library/manifests/<source_slug>/ref.*.json
libraries/reference_library/annotations/<source_slug>/ann.*.json
libraries/knowledge/source_notes/<source_slug>.md
```

默认边界：

```text
license_status: unknown
usage_boundary: reference_only
privacy_boundary: raw
review_status: agent_inferred
```

## 提交前检查

提交 raw 图库前先确认：

- 没有 CAD 锁文件、下载失败文件、临时解压缓存或明显重复的大压缩包。
- `source_note.md` 可以先由 Agent 自动生成；不确定项保留 `unknown`。
- 不把本目录文件直接复制进 `libraries/system_library/`。
- 不在回复里把“raw 文件已存在”说成“系统已经学会”。

自产图库只放在：

```text
libraries/system_library/
```

参考索引和标注只放在：

```text
libraries/reference_library/
```
