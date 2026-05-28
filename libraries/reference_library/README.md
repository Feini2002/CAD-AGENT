# Reference Library

外部参考资产索引。这里记录用户截图、脱敏参考、公开资料摘要、vendor catalog 或根目录 raw 图库的来源与边界，但不声明系统已经会画这些对象。

规则：

- 默认状态是 `reference_only`。
- 用户明确需要随 git 迁移的标准图库原始文件统一放 `standard_cad_library_raw/`；这里不复制原始大图库，只登记索引、来源、标注和边界。
- `standard_cad_library_raw/` 里的文件即使进入 git，也仍然默认是 `reference_only`，不能直接当作系统自产能力。
- 可进 `reference_library` 的是 manifest、来源说明、Agent 推断 / 用户确认标注、小型脱敏缩略图或占位索引。
- 任何条目要进入系统自产图库，必须经过 `knowledge`、`benchmarks` 和 promotion gate。

子目录：

- `sources/`：来源、授权、脱敏和采集批次说明。
- `images/`：轻量缩略图或占位索引。
- `manifests/`：`reference_asset` JSON 清单。
- `annotations/`：Agent 推断 / 用户确认的对象、部件、风格标注。
