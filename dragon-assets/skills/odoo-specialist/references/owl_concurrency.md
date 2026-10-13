# OWL Concurrency & Race Condition Defense

## 痛点
OWL 组件中的异步 `onWillStart` 或 `onWillUpdateProps` 可能导致状态覆盖。

## 防御策略
1. **Task Queue**: 使用 `KeepLast` 或 `DropPrevious` 模式处理异步请求。
2. **Component Lifecycle**: 在 `onWillUnmount` 中取消所有待处理的 Promise。
3. **Internal State**: 异步更新前校验 `this.__owl__.isDestroyed`。

## 范式
```javascript
import { useService } from "@web/core/utils/hooks";
// 使用专用的异步锁或原子计数器防止竞态
```
