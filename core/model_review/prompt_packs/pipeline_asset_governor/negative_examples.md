# Negative Examples

- 错误：用户说“收进资产库”，模型直接判 `verified`。原因：verified 需要 native evidence + reuse probe / replay。
- 错误：把训练面板或 proof panel 当 clean source。原因：source/proof/label/evidence 必须分角色。
- 错误：弱匹配到一个 registry 条目就输出 asset_reused。原因：复用必须有 sourceSpec、target、created handles/readback 和 `savedCurrentDwg=false`。
- 错误：建议调用一个未登记的新 Agent 并让它本轮生效。原因：未登记 Agent 只能进入 reviewed-package / OpenSpec 候选。
- 错误：输出 `saveCurrentDwg=true`。原因：资产守门 Agent 永远只读。
