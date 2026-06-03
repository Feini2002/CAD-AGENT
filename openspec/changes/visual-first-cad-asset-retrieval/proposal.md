## Why

当前 CAD 图块查找主要依赖枚举块参照、读取线弧构造后再人工判断；这能证明结果，但不适合未来大图库。需要建立视觉优先的 CAD 图库检索底座，让用户用语义和截图描述时，系统先快速召回相似块，再用 CAD 回读确认。

## What Changes

- 新增当前 DWG 内的视觉优先块检索能力：从语义/截图意图生成视觉画像，先按类别、比例、图层、粗视觉特征召回候选，再对少量候选做 CAD 证明。
- 新增检索报告，记录候选排序、用时、证据来源、命中块的 `handle` / `block_name` / `bbox` / `layer`。
- 新增 CLI 自测入口，支持模拟“根据截图寻找沙发”的命令并输出耗时。
- 保留 CAD 几何回读作为最终确认，不把截图相似度或缩略图判断声明为真实尺寸准确。
- 不改变表 C、capability registry 或施工图能力口径。

## Capabilities

### New Capabilities

- `visual-cad-asset-retrieval`: 根据语义和视觉画像在当前 CAD 模型空间中快速召回相似块，并输出 CAD 回读确认。

### Modified Capabilities

- 无。

## Impact

- 新增 `core/visual_retrieval/` 作为视觉优先资产检索底座的 V0 实现。
- 新增 `scripts/run_visual_block_retrieval.py` 作为当前 DWG 内检索和验收入口。
- 新增单元测试覆盖语义画像、候选评分、Top-K 召回和证据边界。
- 真实 AutoCAD 验收只读连接当前会话；不保存 DWG、不删除实体、不写正式图层。
