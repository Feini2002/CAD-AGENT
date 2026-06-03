# System Library

系统自产、可复用、可测试的 CAD 资产。这里的资产必须能被系统独立重建或受控调用，并带有来源链、验证状态和证据边界。

最小定义：

```text
metadata + generator/recipe + tests or checks + verified examples + evidence_boundary
```

只有截图、DWG、PNG 或单个 preview 不算系统资产。

用户明确说“沉淀 XX 资产”时，默认按系统资产四件套登记：

```text
machine contract + native CAD library location + apply/verify tools + registry index
```

沉淀前必须先经过 `pipeline_asset_governor`。守门员会判断来源边界、是否允许进入 clean reusable source、是否需要派 `pipeline_asset_librarian` / `pipeline_asset_dwg_curator` / `pipeline_asset_reuse_auditor`，并输出 `polishHardeningDecision`。如果来源不清，资产只能进入 `metadata_only` 或 `03_REVIEW_QUARANTINE`，不能放进可复制源区。

全局索引为 `registry.json`。分类包可先预留 `*_assets.dwg` / `.dwt` 路径；当 `nativeDwgExists=false` 时，只代表合同和索引已建立，不代表原生 DWG 已导出或新 CAD 文件已自动具备该资产。协议说明见 `docs/architecture/system-asset-sedimentation-protocol.md`，当前登记入口为 `scripts/sediment_system_asset.py`。

资产状态分四档：

- `candidate`：已登记，可作为候选，不代表稳定能力。
- `systemized`：已沉淀到规则、Prompt、检查器或训练证据，可优先考虑。
- `verified`：已有复用验收或 CAD readback 证据，可作为稳定系统资产。
- `deprecated`：历史保留，不优先使用。

每条资产还应带 `retrieval`、`native.layoutPlan` v2、`libraryGovernance`、`versioning`、`verification`、`feedbackLoop`、`exportManifest` 和 `antiContamination`。`scripts/sediment_system_asset.py --verify --category <category>` 只做元数据验收；当报告里 `native DWG geometry` 仍在 `notChecked` 时，不得声称原生 DWG 复用已经通过。

系统资产 DWG 默认分为 `00_INDEX`、`01_CLEAN_ASSETS`、`02_PREVIEW_CARDS`、`03_REVIEW_QUARANTINE` 和 `99_EVIDENCE_LINKS`。训练标题、临时说明、边框、尺寸线、审计文字和证据路径默认不得进入 `01_CLEAN_ASSETS`。

分类包的 `nativeLayout.visualRackPlan` 必须通过视觉仓库审计后才算当前仓库排版过关。审计范围包括 v2 schema、仓库架构、rack family 归属、slot ownership、copy policy、扩展空位、zone bbox 比例；真实写入货架脚手架时还要保留 created handles 的实体回读摘要、保护资产内容 bbox 和 shelf/content clearance 审计。任何货架框线、标签、route 或 slot grid 与既有资产内容 bbox 相交都不能验收；截图只是人工复审入口，不替代 handles / bbox / readback / clearance audit。

对象资产只有来源边界精确时才允许进入 `block_export`，例如 `selected_handles`、`created_handles`、`active_dwg_handles`、`explicit_bbox` 或 `named_block`。不得把整个 `CODEX_PREVIEW`、全模型空间、当前屏幕、全部可见对象、训练面板或全局预览 bbox 默认打成 block；来源不清时只登记 `metadata_only`。绘图标准、线宽、线型、尺寸、文字和引线等资产走 `style_standard` / `style_export`，不做 block。

子目录：

- `objects/`：自产对象定义。
- `parts/`：可组合部件。
- `blocks/`：受控 block metadata。
- `symbols/`：2D 平面符号语法。
- `compositions/`：多对象组合模板。
- `drawing_standards/`：绘图标准资产包，例如线宽、线型、尺寸样式、文字和引线样式。
- `furniture/`：家具对象资产包，例如沙发、茶几、床、柜体等。
- `generated/`：已晋升图样索引，不放临时运行图。
