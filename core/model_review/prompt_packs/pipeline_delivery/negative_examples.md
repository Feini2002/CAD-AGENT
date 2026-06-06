# Negative Examples

- 错误：closeout 缺失仍输出 `可验收`。原因：缺 closeout 只能 not_verified。
- 错误：把截图非空说成 CAD 几何准确。原因：截图只是 visual_aid_only。
- 错误：把模型 pass 写成用户已验收。原因：用户验收必须来自用户反馈。
- 错误：普通训练交付自动报表 C。原因：表 C 只有用户点名时展开。
- 错误：visual acceptance fail 时还请求用户验收。原因：应阻断并说明下一步修复。
