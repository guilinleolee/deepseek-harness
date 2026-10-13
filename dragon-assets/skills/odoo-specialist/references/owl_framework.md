# Odoo OWL Framework (OWL 框架规范)

## 1. 组件架构
- **声明式 UI**: 使用 XML 模版定义布局，将逻辑封装在 JS Class 中。
- **Hooks 使用**: 优先使用 `useService`, `onWillStart`, `onWillPatch` 管理副作用。

## 2. 通信协议
- **RPC 调用**: 使用 `this.rpc(...)` 或 `this.env.services.rpc(...)`，强制捕获捕获网络异常。
- **数据绑定**: 利用 `useState` 实现响应式数据更新。

## 3. 继承与扩展
- **Patch 机制**: 使用 `patch(Component.prototype, ...)` 扩展标准视图组件。
- **Registry**: 通过 `registry.category("views").add("my_view", ...)` 注册自定义视图。
