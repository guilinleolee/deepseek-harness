# n8n 核心架构模式

## 1. ETL 模式 (Extract-Transform-Load)

最常用的数据处理模式。

```
[Trigger] → [Extract] → [Transform] → [Load] → [Output]
```

**适用场景**:
- 数据迁移
- 数据同步
- 报表生成

**示例**: MySQL → PostgreSQL 数据同步

```
[Schedule] → [MySQL] → [Data Transform] → [Postgres] → [Log]
```

### Extract (数据提取)
- HTTP Request: API 调用
- Database: 查询数据
- File: 读取文件

### Transform (数据转换)
- Set: 字段映射
- Code: 复杂转换
- Function: 数据处理

### Load (数据加载)
- Database: 插入/更新
- HTTP Request: 推送数据
- File: 写入文件

---

## 2. API 链式调用模式

依次调用多个 API，传递数据。

```
[Trigger] → [API 1] → [API 2] → [API 3] → [Output]
```

**适用场景**:
- 多步骤 API 流程
- 数据聚合
- 工作流编排

**示例**: 用户注册流程

```
[Webhook] → [Create User] → [Send Welcome Email] → [Add to CRM] → [Log]
```

### 链式调用要点
1. **数据传递**: 使用 `$json` 传递
2. **错误处理**: Continue On Fail + IF 分支
3. **幂等性**: API 调用支持重试

---

## 3. 批处理模式

处理大量数据的分批处理。

```
[Trigger] → [Get Data] → [Split Batches] → [Process] → [Aggregate] → [Output]
                                           ↑______________|
```

**适用场景**:
- 大量数据导入
- 批量 API 调用
- 定期数据清理

**示例**: 处理1000条用户数据

```yaml
配置:
  批量大小: 100
  总批次: 10
  并发: 1 (避免 API 限流)

节点配置:
  - Split In Batches: batchSize: 100
  - Process: 单条处理
  - Loop: 批次循环
  - Aggregate: 合并结果
```

### 批处理最佳实践
- 使用 `Split In Batches` 控制批次
- 添加 `Wait` 节点防止限流
- 记录处理进度到文件/数据库
- 错误时记录失败项，不中断整体

---

## 4. 扇出-扇入模式 (Fan-out Fan-in)

并行执行多个独立任务，然后聚合结果。

```
         → [Task A] ─┐
[Trigger] → [Task B] ─→ [Merge] → [Output]
         → [Task C] ─┘
```

**适用场景**:
- 多平台发布
- 多数据源聚合
- 并行 API 调用

**示例**: 发布到多个社交媒体

```
[Webhook] → {
               → [Twitter] ─┐
               → [Facebook] ─→ [Aggregate Stats] → [Response]
               → [LinkedIn] ─┘
             }
```

### 实现方式
1. **使用多个连接**: 一个节点连接多个下游
2. **使用 Split In Batches**: 并行执行相同任务
3. **使用 Merge 节点**: 聚合结果

---

## 5. 错误分支模式

主流程失败时执行备用逻辑。

```
[Main Flow] → {success} → [Continue]
               ↓
            {error} → [Error Handler] → [Retry/Log/Notify]
```

**适用场景**:
- API 调用失败重试
- 降级处理
- 错误通知

**示例**: API 调用失败时使用缓存

```
[API Call] → {success} → [Use Data]
              ↓
           {error} → [Check Cache] → {hit} → [Use Cached]
                                → {miss} → [Return Default]
```

### 错误处理策略
1. **重试**: 使用 `Loop Over` 节点
2. **降级**: 切换到备用服务
3. **缓存**: 返回缓存数据
4. **通知**: 发送错误告警

---

## 6. 状态机模式

基于状态转换处理业务逻辑。

```
[Trigger] → [Check State] → {
                              → [State A] → [Action A] → [Update State]
                              → [State B] → [Action B] → [Update State]
                              → [State C] → [Action C] → [Update State]
                            } → [Loop/End]
```

**适用场景**:
- 订单处理流程
- 审批流程
- 用户生命周期管理

**示例**: 订单状态流转

```
[Webhook: Order Created] → [IF: Payment?] → {
                                                   → Yes: [Process Payment] → [IF: Success?] → {
                                                                                                               → Yes: [Ship Order] → [State: Shipped]
                                                                                                               → No: [Cancel Order] → [State: Cancelled]
                                                                                                             }
                                                   → No: [State: Pending]
                                                 }
```

### 状态机设计要点
1. **明确状态定义**: 枚举所有可能状态
2. **状态转换规则**: 定义状态间的转换条件
3. **持久化状态**: 保存状态到数据库
4. **状态转换日志**: 记录每次转换

---

## 7. 事件驱动模式

响应外部事件并触发动作。

```
[Event Source] → [Event Processor] → [Action Dispatcher] → [Actions] → [Response]
```

**适用场景**:
- Webhook 处理
- 消息队列消费
- 实时数据同步

**示例**: GitHub Webhook 处理

```
[Webhook] → [Parse Event] → [Switch: Event Type] → {
                                                   → push: [Run Tests]
                                                   → pull_request: [Review PR]
                                                   → issue: [Assign Team]
                                                 }
```

### 事件驱动设计要点
1. **事件解析**: 识别事件类型
2. **事件路由**: 使用 Switch 分发
3. **异步处理**: 使用 Queue 解耦
4. **事件确认**: 返回响应确认处理

---

## 模式选择指南

```
你的需求是什么？

├─ 数据迁移/同步
│  └─ 使用 ETL 模式
│
├─ 多步骤 API 调用
│  └─ 使用 API 链式调用模式
│
├─ 处理大量数据
│  └─ 使用批处理模式
│
├─ 多平台并行操作
│  └─ 使用扇出-扇入模式
│
├─ 需要容错处理
│  └─ 使用错误分支模式
│
├─ 复杂业务流程
│  └─ 使用状态机模式
│
└─ 响应外部事件
   └─ 使用事件驱动模式
```

## 组合模式示例

### ETL + 批处理 + 错误分支

```
[Schedule] → [MySQL: Get Data] → [Split Batches: 1000] → [Transform] → [Postgres: Insert] → {success} → [Log Success]
                                                                                       ↓
                                                                                    {error} → [Log Error] → [Retry Queue]
```

### 扇出-扇入 + 错误分支

```
[Webhook] → {
                → [API A] → {success} → [Result A] ─┐
                → [API B] → {success} → [Result B] ─→ [Merge] → [Response]
                → [API C] → {error} → [Fallback C] ─┘
              }
```

## 最佳实践

1. **模块化**: 复杂工作流拆分为可复用子工作流
2. **可观测性**: 添加日志节点记录关键步骤
3. **幂等性**: 设计支持重试的幂等操作
4. **错误处理**: 为每个关键节点添加错误处理
5. **性能优化**: 使用批处理和并行处理提升效率
6. **安全考虑**: 验证输入数据，保护敏感信息

## 相关文档

- [编排模式详解](orchestration-patterns.md)
- [错误目录](../rules/error-catalog.md)
- [验证规则](../rules/validation-rules.md)
