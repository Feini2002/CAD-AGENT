# commercial_fitout Rules

## Scene Product Alpha v1

- 仅当用户或项目 manifest 明确指定工装 / `commercial_fitout` 时启用本场景模块。
- 子场景限定为 `open_office`、`meeting_room`、`reception`；不确定子场景时先追问，不静默默认。
- 不得把范围文档、preferences 或 non-CAD benchmark 写成完整施工图或 `geometry_verified` 已成立。

## 子场景差异（声明性）

### open_office

- 工位组优先沿采光面或结构柱网排布，保留主通道。
- 打印区、文件柜靠近工位区边缘，不阻断主通道。

### meeting_room

- 会议桌居中或靠墙布置时，须保留门洞开启扇与疏散宽度。
- AV / 边柜贴墙，不占用会议主通道。

### reception

- 前台面向入口可视；等候区不阻塞消防门与主通道。
- 形象墙、储物与接待台成组，避免零散孤立物件。

## Defaults

- 主通道偏好：1200 mm（开放办公与接待区）。
- 次通道偏好：900 mm。
- 预览图层：`CODEX_PREVIEW`。

## Core Boundary

- Do not implement drawing analysis here.
- Do not implement collision checks here.
- Do not implement `CAD_PLAN` validation, dry-run, execution, screenshot, or entity readback here.
- Store only scene preferences, subscene scope, and workflow intent.
