# residential_training_template

家装 Agent 训练用空案例模板（方案 A）。复制本目录为 `projects/<your_case_id>/` 后开始第一轮。

## 复制后必改

| 文件 | 动作 |
| --- | --- |
| 文件夹名 | 改为你的 `case_id` |
| `sample.manifest.json` | `sample_id`、`display_name` |
| `brief.md` | 粘贴白话需求（可脱敏） |
| `feedback.md` | 每轮训练后填写（含 §用户指出的错因、§Agent 根因与修复） |
| `expected/intent.template.json` | 复制为 `runs/round1_intent.json` 并填写 |
| `expected/audit_checklist.template.json` | 复制为 `expected/audit_checklist.json` |
| `input/shell.manual.json` | 脱敏户型空壳 |

## 禁止

- 不要提交 `.dwg` / `.dxf`。
- 不要因模板存在就声称 `geometry_verified`。
- 不要未经确认写正式图层或保存 DWG。

## 下一步

对话：**「开一轮训练，案例 id 是 \<your_case_id\>」**。协议见 `docs/runbooks/project-sample-intake.md`。

训练主链路与 feedback 后记错因的约定：`docs/training/README.md`。
