# BETA-DRAWING-READ 父包验收（01–05）

最后更新：2026-05-26

## 可声称

| 小包 | 能力 |
| --- | --- |
| READ-01 | 只读 `dwg_entity_summary`（层/类型/bbox/handle） |
| READ-02 | 墙/门/柱/禁放区几何候选启发式 |
| READ-03 | 置信度、gaps、人工确认点、草案 shell |
| READ-04 | 确认文件回写为通过 `shell_loader` 的 `SHELL_MODEL` |
| READ-05 | 读图链路 benchmark（pass + 结构化 blocker） |

证据：`drawing_read_benchmark` 3/3 pass；全量 unittest 见 CHANGELOG。

## 不可声称

- 任意 DWG 自动读图准确或 `geometry_verified`。
- 未人工确认的草案可直接进入 blank-shell 落 CAD。
- fixture 启发式等价于建筑语义推理。

## 下一后置主线

`BETA-SCENE-01`（场景 Agent Beta）或用户指定的其它后置包。
