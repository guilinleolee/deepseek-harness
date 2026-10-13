# Odoo 19.0 View Architectures (19.0 视图架构)

## 1. 视图红旗 (Red Flags)
- ❌ 在 `Grid` 视图中缺失必填的 `Schema` 声明。
- ❌ 滥用 `XPath` 的绝对路径（如 `/form/sheet/...`），应使用属性定位。

## 2. 19.0 新特性
- **Grid View**: 支持 `Server Hooks`，必须定义数据聚合逻辑。
- **Settings View**: 强制使用 `app` -> `block` -> `setting` 的语义化结构。

## 3. 继承准则
- 优先修改 `attributes` 而非重写整段 XML。
- 确保 `__manifest__.py` 中的 `data` 加载顺序符合依赖链。
