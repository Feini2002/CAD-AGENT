# Verification Docs

本目录保存 CAD Agent 的验证边界、证据解释、模板和验收文档。机器证据本体仍在 `output/validation_runs/`，不要用 Markdown 摘要替代 JSON / readback / created handles。

## 分区意图

| 分区 | 职责 |
| --- | --- |
| `templates/` | 未来新增的证明 / handoff / deferred 模板 |
| `gates/` | evidence gate、词表、真实 CAD 门槛 |
| `capability/` | 表 C、Ladder、showcase、能力证明解释 |
| `cad-readback/` | AutoCAD / readback / created handles 边界 |
| `scene/` | 场景 Agent / P3 / scene beta 验收边界 |
| `block/` | block / drawing standard / symbol 相关边界 |
| `audits/` | 结构审计、合并候选、硬化审计 |
| `evidence-index/` | 未来的机器证据索引 |

## 兼容规则

当前很多代码常量和测试直接引用 `docs/verification/*.md` 的旧路径；本次架构重构先保持这些路径稳定，新增分区作为后续落点。后续迁移单个 verification 文档时，必须同步代码常量、测试、handoff、status 和链接检查。

## 证据边界

- `geometry_verified` 必须能追到真实 CAD runner、created handles 和 readback。
- no-CAD、dry-run、benchmark、fake driver、截图都不能替代真实几何证明。
- 表 C 数值以 `output/validation_runs/capability-lab/cad_capability_coverage.json` 为准。
