# Step 04: 知识库查询

## 目标
通过三层知识架构，查询节点详细配置、API 文档和最佳实践。

## 三层知识架构

### Layer 1: 节点目录 (快速索引)

查询 INDEX.md 或使用 n8n-mcp `search_nodes`：

```yaml
目标:
  - 确认节点存在
  - 获取节点基本信息
  - 了解节点版本

示例输出:
  节点: @n8n/n8n-nodes-gmail
  版本: 2
  分类: output
  文件: resources/output/nodes-base.gmail.md
  或: resources/output/output-merged-1.md (行: 123-200)
```

### Layer 2: MCP get_node (详细配置)

使用 n8n-mcp `get_node` 获取节点详细配置：

```yaml
查询参数:
  nodeType: "@n8n/n8n-nodes-gmail"
  typeVersion: 2

返回内容:
  - displayName: "Gmail"
  - description: "..."
  - properties: [完整属性列表]
  - operations: [支持的操作]
  - credentials: [需要的凭据类型]
```

### Layer 3: 深度文档 (最佳实践)

查询以下资源：

```yaml
本地资源:
  - skills/n8n-skill/guides/usage-guide.md
  - skills/n8n-skill/guides/how-to-find-nodes.md
  - skills/n8n-skill/patterns/core-patterns.md
  - skills/n8n-skill/patterns/orchestration-patterns.md
  - skills/n8n-skill/rules/error-catalog.md

官方文档:
  - https://docs.n8n.io/integrations/builtin/core-nodes/
  - 节点特定的最佳实践
  - 常见问题解答

社区资源:
  - n8n 社区论坛
  - GitHub 工作流示例
  - YouTube 教程
```

## 查询流程

### 1. 节点配置查询

对于 confirmed_plan 中的每个节点：

```markdown
## 节点: Gmail

### Layer 1: 基本信息
- **节点类型**: @n8n/n8n-nodes-gmail
- **版本**: 2
- **分类**: Output
- **内置/社区**: 内置

### Layer 2: 详细配置
**操作**: getAll
**参数**:
```json
{
  "filters": {
    "hasAttachment": true
  },
  "limit": 50
}
```

**表达式支持**:
- 支持动态过滤条件
- 支持批量操作
- 支持分页

**凭据需求**:
- 类型: OAuth2
- 作用域: https://www.googleapis.com/auth/gmail.readonly

### Layer 3: 最佳实践
1. **批量处理**: 一次最多获取50封邮件
2. **错误处理**: 使用 Continue On Fail 处理 API 限流
3. **性能优化**: 使用 filters 而非获取全部后过滤
4. **常见问题**:
   - Token 过期: 重新授权
   - 限流: 添加延迟或重试
```

### 2. 编排模式查询

根据工作流复杂度查询相应模式：

```yaml
简单顺序编排:
  参考: patterns/orchestration-patterns.md
  章节: 1. 顺序编排

条件分支:
  参考: patterns/orchestration-patterns.md
  章节: 2. 条件分支
  示例: IF 节点配置、Switch 节点配置

并行处理:
  参考: patterns/orchestration-patterns.md
  章节: 3. 并行分支
  注意: 并行度限制

循环处理:
  参考: patterns/orchestration-patterns.md
  章节: 4. 循环处理
  实现: Split In Batches
```

### 3. 错误处理查询

查询可能的错误和解决方案：

```yaml
节点级错误:
  参考: rules/error-catalog.md
  章节: 按节点类型查找

表达式错误:
  参考: specs/expression-syntax.md
  常见错误: 语法错误、类型错误

验证规则:
  参考: rules/validation-rules.md
  必填字段检查
  数据类型验证
```

## 输出格式

### knowledge.md

```markdown
# 知识库查询结果

## 节点详细配置

### 节点 1: Schedule Trigger
**文档位置**: resources/trigger/nodes-base.scheduleTrigger.md

**关键配置**:
```json
{
  "mode": "cron",
  "cronExpression": "0 9 * * 1-5"
}
```

**注意事项**:
- cron 表达式使用 6 位格式（秒 分 时 日 月 周）
- 时区默认为 UTC

### 节点 2: Gmail
**文档位置**: resources/output/nodes-base.gmail.md

**操作**: getAll
**参数**:
```json
{
  "limit": 50,
  "filters": {
    "query": "label:IMPORTANT"
  }
}
```

**输出结构**:
```json
{
  "id": "邮件ID",
  "subject": "主题",
  "from": "发送者",
  "snippet": "摘要",
  "body": "正文",
  "labels": ["标签"],
  "timestamp": "时间戳"
}
```

### 节点 3: Filter
**文档位置**: resources/transform/nodes-base.filter.md

**条件配置**:
```javascript
{
  "conditions": {
    "string": [
      {
        "value1": "={{ $json.labelIds }}",
        "operation": "contains",
        "value2": "IMPORTANT"
      }
    ]
  }
}
```

## 编排模式参考

### 使用的模式
1. **顺序编排** (主要流程)
   - 参考: patterns/orchestration-patterns.md §1

2. **条件分支** (Filter 节点)
   - 参考: patterns/orchestration-patterns.md §2
   - 实现方式: IF 节点

3. **错误处理** (Continue On Fail)
   - 参考: patterns/orchestration-patterns.md §6

## 错误预防

### 潜在错误及预防
| 错误类型 | 触发条件 | 预防措施 |
|----------|----------|----------|
| 401 认证错误 | Token 过期 | Continue On Fail + 重试 |
| 429 限流错误 | 请求过快 | Wait 节点延迟 |
| 数据格式错误 | API 变更 | 数据验证节点 |

## 表达式参考

### 常用表达式
```javascript
// 获取字段值
{{ $json.subject }}

// 安全访问
{{ $json.data?.field || 'default' }}

// 条件表达式
{{ $json.priority === 'high' ? 'urgent' : 'normal' }}

// 数据转换
{{ Number($json.price).toFixed(2) }}

// 时间格式化
{{ new Date($json.timestamp).toLocaleString() }}
```

## 参考资料
- [Gmail 节点文档](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.gmail/)
- [Filter 节点文档](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.filter/)
- [表达式语法](https://docs.n8n.io/code-examples/expressions/)
```

## 查询优化

### 高效查询策略

1. **先索引后深度**
   ```javascript
   // 先查 INDEX.md
   Read("INDEX.md")
   // 再查具体节点
   Read("resources/output/nodes-base.gmail.md")
   ```

2. **批量查询**
   - 一次性查询所有节点
   - 避免重复查询

3. **缓存结果**
   - 将常用节点配置存入本地
   - 减少 API 调用

## 验证条件

- [ ] 所有节点的基本信息已查询
- [ ] 关键节点的详细配置已获取
- [ ] 编排模式已确定
- [ ] 错误处理策略已制定
- [ ] 表达式示例已收集
- [ ] knowledge.md 已生成

## 错误处理

| 情况 | 处理 |
|------|------|
| 节点不存在 | 寻找替代节点或社区包 |
| 文档缺失 | 查询官方文档或社区 |
| 版本不匹配 | 使用兼容版本或升级 |
| 配置复杂 | 寻找示例工作流 |

## 下一步

Step 05: 架构设计 - 基于知识库查询结果生成完整设计
