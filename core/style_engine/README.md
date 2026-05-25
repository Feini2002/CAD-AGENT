# core/style_engine

职责：把白话风格转换成可绘制、可复用的风格参数，输出 `STYLE_PROFILE`。

首批目标风格：

- 现代。
- 欧式。
- 极简。

示例方向：

- 欧式：顶线、踢脚、门板分格、装饰线。
- 现代：平板、隐藏把手、低装饰线。
- 极简：少分缝、少线条、弱装饰。

当前状态：prototype。`style_profile.py` 已支持加载 `libraries/styles/modern.json`、`european.json`、`minimal.json`，尚未把风格 token 深度转为复杂 CAD 细节。

边界：

- 本模块不直接创建 CAD 实体。
- 风格参数应被对象、立面、布局表达复用。
- 场景 Agent 可以设置偏好，但不复制风格引擎。
