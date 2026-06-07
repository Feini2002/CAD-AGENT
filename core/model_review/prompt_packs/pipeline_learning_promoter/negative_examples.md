# Negative Examples

## 直接写事实层

错误：模型输出“我已经把经验写入 training_memory.json”。

原因：本 prompt pack 只能 proposal-only，不允许写事实层。

## 泛化口号冒充学习

错误：把“以后更谨慎检查”作为 memory patch。

原因：没有 errorPattern、correctPattern、责任 Agent、证据引用和行为改变目标。

## 用截图替代训练证据

错误：只因截图看起来正常，就建议训练通过并推广规则。

原因：截图不能替代 CAD readback、用户反馈、机器审计和回测证据。

## 越权推进表 C

错误：把一次学习补丁提案说成 Core Proof Coverage 或真实项目交付准备度提升。

原因：learning proposal 不证明表 C、Agent Task Maturity 或 Project Delivery Readiness。
