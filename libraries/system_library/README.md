# System Library

系统自产、可复用、可测试的 CAD 资产。这里的资产必须能被系统独立重建或受控调用，并带有来源链、验证状态和证据边界。

最小定义：

```text
metadata + generator/recipe + tests or checks + verified examples + evidence_boundary
```

只有截图、DWG、PNG 或单个 preview 不算系统资产。

子目录：

- `objects/`：自产对象定义。
- `parts/`：可组合部件。
- `blocks/`：受控 block metadata。
- `symbols/`：2D 平面符号语法。
- `compositions/`：多对象组合模板。
- `generated/`：已晋升图样索引，不放临时运行图。
