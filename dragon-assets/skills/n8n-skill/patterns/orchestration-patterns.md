# n8n 编排模式

## 1. 顺序编排 (Sequential)

最简单直接的线性流程。

```
[Trigger] → [Step 1] → [Step 2] → [Step 3] → [Output]
```

**适用场景**:
- 数据转换流水线
- 简单的 ETL 流程
- 单一目标的自动化任务

**示例**: 定时获取数据 → 转换格式 → 存入数据库

---

## 2. 条件分支 (Conditional)

根据条件路由到不同分支。

```
[Trigger] → [IF] → {condition=true}  → [Branch A]
                 → {condition=false} → [Branch B]
```

**适用场景**:
- 数据过滤
- 异常处理
- 不同用户类型的处理

**示例**:
```javascript
// IF 节点条件
{{ $json.priority === 'high' }}  // 高优先级走 A 分支
{{ $json.priority === 'low' }}   // 低优先级走 B 分支
```

---

## 3. 并行分支 (Parallel)

同时执行多个独立分支。

```
         → [Branch A] →
[Trigger] → [Branch B] → [Merge] → [Output]
         → [Branch C] →
```

**适用场景**:
- 多平台同时发布
- 多数据源并行获取
- 独立任务并行处理

**实现**: 使用 `Split In Batches` + 多个输出分支

**注意**: n8n 默认并行度有限，大量并行需配置环境变量

---

## 4. 循环处理 (Loop)

遍历数组或批量处理。

```
[Trigger] → [Split In Batches] → [Process Item] → [Loop Back] → (继续处理)
                                                ↓
                                           [Done] → [Output]
```

**适用场景**:
- 批量数据处理
- API 分页请求
- 数组遍历操作

**Split In Batches 配置**:
```yaml
batchSize: 10           # 每批处理数量
options:
  reset: false          # 是否重置
```

---

## 5. 聚合模式 (Aggregation)

收集多个数据源的结果。

```
         → [Source A] ─┐
[Trigger]              → [Aggregate] → [Output]
         → [Source B] ─┘
```

**适用场景**:
- 多数据源汇总
- 等待多个异步操作完成
- 数据合并处理

**实现**: 使用 `Merge` 节点
```yaml
mode: "combine"         # 或 "append", "mergeByIndex"
```

---

## 6. 错误处理模式 (Error Handling)

```
[Trigger] → [Try Block] → {success} → [Continue]
               ↓
            {error} → [Error Handler] → [Log/Retry/Notify]
```

**适用场景**:
- API 调用重试
- 降级处理
- 错误通知

**实现**:
1. 节点级别的 `Continue On Fail` = true
2. IF 节点检查 `{{ $json.error }}`
3. 使用 `Switch` 节点路由错误

**示例**:
```javascript
// 检查上一节点是否失败
{{ $node["HTTP Request"].json.error !== undefined }}
```

---

## 7. 发布-订阅 (Pub-Sub)

触发多个独立的消费者。

```
[Trigger] → [Broadcast] → [Consumer A] → [Output A]
                      → [Consumer B] → [Output B]
                      → [Consumer C] → [Output C]
```

**适用场景**:
- 事件通知到多个系统
- 多平台同步发布
- 审计日志 + 业务处理

**实现**: 使用多个连接或 `Split Out` 节点

---

## 8. 补偿模式 (Compensating)

事务失败后回滚操作。

```
[Action 1] → [Action 2] → [Action 3] → (失败)
     ↓           ↓           ↓
[Compensate] [Compensate] [Compensate]
```

**适用场景**:
- 分布式事务
- 多步骤操作需原子性
- 清理中间状态

**实现**: 使用 IF 检查错误 + Switch 路由到清理逻辑

---

## 9. 节流模式 (Throttling)

控制处理速率，避免 API 限流。

```
[Trigger] → [Queue] → [Rate Limiter] → [Process] → [Output]
```

**适用场景**:
- API 限流保护
- 资源消耗控制
- 成本控制

**实现**:
1. `Wait` 节点（固定间隔）
2. `Split In Batches` + 小批量
3. 外部队列 + 轮询

---

## 10. 缓存模式 (Caching)

减少重复计算或 API 调用。

```
[Trigger] → [Check Cache] → {hit} → [Return Cached]
               ↓
            {miss} → [Compute] → [Update Cache] → [Return]
```

**适用场景**:
- 减少 API 调用
- 加速响应
- 降低成本

**实现**:
1. Redis 节点
2. Google Sheets 作为简单缓存
3. 内存变量（单次执行）

---

## 模式选择决策树

```
是否有条件分支?
├─ 是 → 条件分支 (Conditional)
└─ 否 → 是否需要并行处理?
    ├─ 是 → 并行分支 (Parallel)
    └─ 否 → 是否需要批量处理?
        ├─ 是 → 循环处理 (Loop)
        └─ 否 → 是否需要多数据源?
            ├─ 是 → 聚合模式 (Aggregation)
            └─ 否 → 顺序编排 (Sequential)
```

## 组合模式示例

### 批量并行处理 + 错误处理

```
[Trigger] → [Split Batches] → {
    Batch 1 → [Process A] → {success} → [Aggregate]
                          → {error} → [Log] → [Retry]
    Batch 2 → [Process B] → {success} → [Aggregate]
                          → {error} → [Log] → [Retry]
} → [Output]
```

### 条件 + 并行 + 缓存

```
[Trigger] → [Check Cache] → {hit} → [Return]
               ↓
            {miss} → [IF: 高优先级?] → {
                → Yes: [Parallel A, B, C]
                → No:  [Sequential A, B, C]
            } → [Update Cache] → [Return]
```

## 最佳实践

1. **可视化**: 复杂编排先画图再实现
2. **错误隔离**: 每个关键节点都考虑错误处理
3. **日志追踪**: 关键节点添加日志节点
4. **测试策略**: 简单流程先测试，再组合
5. **性能考虑**: 注意并行度和 API 限流
