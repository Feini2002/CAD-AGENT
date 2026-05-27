# Cursor / Codex 交接目录

本目录存放按开发包完成的交接材料。旧巨型汇总已拆为活跃窗口、全量索引、模板和历史归档。

## 当前入口

| 文件 | 职责 |
| --- | --- |
| [`current.md`](current.md) | 最近活跃包的完整 9 项交接 |
| [`package-index.md`](package-index.md) | 全量包索引与归档位置 |
| [`template.md`](template.md) | 9 项模板 + V-PROOF / RCAD 附加项 |
| [`archive/2026-05.md`](archive/2026-05.md) | 2026-05 历史交接归档 |
| [`CURSOR_PACKAGE_HANDOFFS.md`](CURSOR_PACKAGE_HANDOFFS.md) | 兼容 stub，不再承载新交接 |

## 写入规则

每完成一个开发包：

1. 在 `current.md` 写完整 1-9 项。
2. 同步 `package-index.md`。
3. 简短写入 `../status/changelog.md`，必要时更新 `../status/current.md` 和 `../status/issues.md`。
4. 机器证据写入 `output/validation_runs/<包名>/`。
5. V-PROOF、RCAD 或 registry 回写包必须补 10-12 项；不得压掉真实 CAD 证据路径、created handles、`external_blocker` 或 `geometry_verified` 边界。

历史包按月归档，默认不再展开到日常上下文。
