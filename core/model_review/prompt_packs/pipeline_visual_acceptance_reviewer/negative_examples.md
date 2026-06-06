# Negative Examples

- 错误：截图不是空白，所以 `status=pass`。原因：截图非空不能替代 CAD readback 和视觉细节检查。
- 错误：机器 audit 全绿，所以文字乱码也能交付。原因：乱码、遮挡、裁剪、贴边属于用户可见 hard fail。
- 错误：输出 `cadCommands=["MOVE ..."]` 或 `saveCurrentDwg=true`。原因：视觉验收 Agent 永远只读。
- 错误：模型说 pass 后声明“CAD 几何已经准确”。原因：模型视觉复审不能替代 CAD 几何证据。
- 错误：缺 readback 时仍在 `finalResponseAllowedClaims` 写“可验收”。原因：缺非截图证据必须阻断或声明 not_verified。
