# n8n 错误目录与修复策略

## 1. 认证错误 (Authentication Errors)

### 错误代码: `401 Unauthorized`

**症状**:
```
"Authentication failed"
"Invalid API key"
"Token expired"
```

**常见原因**:
- API Key 过期或无效
- OAuth Token 失效
- 凭据配置错误

**修复策略**:
1. 检查 n8n 凭据管理中的配置
2. 重新授权 OAuth
3. 更新 API Key
4. 验证凭据作用域 (Scopes)

**预防措施**:
- 定期刷新 Token（使用 `Wait` 节点调度）
- 监控 Token 到期时间

---

## 2. 限流错误 (Rate Limit Errors)

### 错误代码: `429 Too Many Requests`

**症状**:
```
"Rate limit exceeded"
"Too many requests"
"Quota exceeded"
```

**常见原因**:
- API 调用频率超限
- 并发请求过多
- 短时间内大量请求

**修复策略**:
```yaml
# 方案1: Wait 节点（简单）
[HTTP Request] → [Wait: 2s] → [HTTP Request]

# 方案2: Split In Batches（批量）
[Data] → [Split In Batches: 10] → [Process] → [Wait: 1s] → [Loop]

# 方案3: 指数退避（Code 节点）
// 在 Code 节点中实现
let retryCount = $node["Retry Counter"].json.count || 0;
let waitTime = Math.pow(2, retryCount) * 1000; // 1s, 2s, 4s, 8s...
return [{ json: { waitTime } }];
```

**预防措施**:
- 批量处理而非单个请求
- 添加请求间延迟
- 监控 API 配额使用情况

---

## 3. 超时错误 (Timeout Errors)

### 错误症状:
```
"Request timeout"
"ETIMEDOUT"
"Network timeout"
```

**常见原因**:
- 目标服务器响应慢
- 网络连接问题
- 数据量过大

**修复策略**:
```yaml
# HTTP Request 节点配置:
timeout: 60000  # 增加到 60 秒

# 数据量大时使用分页:
# 1. Code 节点构建分页请求
# 2. 循环处理每页
# 3. Merge 节点聚合结果
```

**预防措施**:
- 设置合理的超时时间
- 实现分页/流式处理
- 添加重试逻辑

---

## 4. 数据格式错误 (Data Format Errors)

### 错误症状:
```
"Cannot read property 'x' of undefined"
"Unexpected token"
"Validation failed"
```

**常见原因**:
- API 返回结构与预期不同
- 数据类型不匹配
- 字段名拼写错误

**修复策略**:
```javascript
// Code 节点: 安全访问
const value = $json.data?.nested?.field || 'default';

// 添加类型检查
const email = $json.email;
if (!email || !email.includes('@')) {
  throw new Error('Invalid email format');
}

// 使用 Set 节点设置默认值
// Field: description
// Value: {{ $json.description || 'No description' }}
```

**预防措施**:
- 使用 IF 节点验证数据
- 添加数据转换层
- 保存 API 响应样本用于测试

---

## 5. 节点连接错误 (Connection Errors)

### 错误症状:
```
"Node connection failed"
"No data available"
"Cannot execute node"
```

**常见原因**:
- 前一节点无输出
- 数据结构不匹配
- 分支逻辑错误

**修复策略**:
```yaml
# 检查前一节点输出:
# 在 IF 节点中添加
{{ $node["Previous Node"].json !== undefined }}

# 使用 Merge 节点的默认模式:
mode: "mergeByIndex"
# 确保两边都有数据

# 添加空数据检查:
# IF 节点条件
{{ $json !== null && Object.keys($json).length > 0 }}
```

**预防措施**:
- 使用 Split In Batches 确保数据流动
- 添加数据验证节点
- 测试所有分支路径

---

## 6. 内存错误 (Memory Errors)

### 错误症状:
```
"JavaScript heap out of memory"
"RangeError: Invalid string length"
```

**常见原因**:
- 处理超大文件
- 无限循环
- 数组过大

**修复策略**:
```yaml
# 使用分批处理:
[Big Data] → [Split In Batches: 100] → [Process] → [Aggregate]

# 避免在 Code 节点中累积大量数据:
// ❌ 错误做法
let allData = [];
for (let item of items) {
  allData.push(process(item));
}
return allData; // 可能内存溢出

// ✅ 正确做法
return items.map(item => ({ json: process(item.json) }));
```

**预防措施**:
- 限制批量大小
- 使用流式处理
- 避免在内存中累积

---

## 7. Webhook 错误 (Webhook Errors)

### 错误症状:
```
"Webhook not responding"
"Invalid webhook URL"
"POST request failed"
```

**常见原因**:
- Webhook URL 错误
- n8n 实例未公网可访问
- Webhook 被触发器禁用

**修复策略**:
```yaml
# 1. 确认 Webhook URL
# 在 Webhook 节点中查看 "Test URL" vs "Production URL"

# 2. 配置 n8n 实例
# N8N_HOST: your-domain.com
# N8N_PROTOCOL: https
# N8N_PORT: 5678
# WEBHOOK_TUNNEL_URL: (可选) 使用 ngrok

# 3. 测试 Webhook
curl -X POST https://your-n8n.com/webhook/xxx \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

**预防措施**:
- 使用 Response 节点返回确认
- 添加 Webhook 日志
- 设置 Webhook 超时

---

## 8. 表达式错误 (Expression Errors)

### 错误症状:
```
"Expression evaluation failed"
"Syntax error in expression"
```

**常见原因**:
- 语法错误
- 引用不存在的节点
- 类型错误

**修复策略**:
```javascript
// 常见表达式语法错误

// ❌ 错误: 单引号嵌套
{{ $json.name + 'user's name' }}

// ✅ 正确: 使用双引号或转义
{{ $json.name + "user's name" }}
{{ $json.name + 'user\'s name' }}

// ❌ 错误: 未检查节点存在性
{{ $node["Non-existent Node"].json.value }}

// ✅ 正确: 检查节点存在性
{{ $node["Node Name"]?.json.value || 'default' }}

// 类型转换
{{ Number($json.price) * 1.1 }}
{{ String($json.count) + ' items' }}
```

---

## 9. 社区节点错误 (Community Node Errors)

### 错误症状:
```
"Node type not found"
"Unknown node"
"Community package error"
```

**修复策略**:
```bash
# 1. 检查节点已安装
# 在 n8n 设置 → Community Nodes 中查看

# 2. 安装社区节点
# 方法1: UI 安装
# Settings → Community Nodes → Add

# 方法2: Docker 安装
docker run -it --rm \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n \
  n8n install:n8n-nodes-my-package

# 3. 重启 n8n
```

---

## 10. 调试技巧 (Debugging Tips)

### 查看节点输出
```yaml
# 方法1: 添加 Code 节点打印
return [{ json: { debug: $input.first().json } }];

# 方法2: 使用 Set 节点创建快照
# 添加一个 Set 节点，字段名: snapshot, 值: {{ $json }}

# 方法3: 执行日志
# 在节点设置中启用 "Always Output Data"
```

### 错误追踪
```yaml
# 在工作流末尾添加错误处理
[Main Flow] → {error} → [Error Logger]

# Error Logger (Code 节点):
const error = $input.first().json;
const errorMessage = {
  timestamp: new Date().toISOString(),
  node: error.node?.name || 'Unknown',
  message: error.message || 'Unknown error',
  stack: error.stack,
  inputData: error.inputData
};
// 写入日志系统或发送通知
```

### 数据追踪
```yaml
# 添加追踪字段
# 在每个关键节点后添加 Set 节点
fields:
  _step: "Step 1 - Gmail"
  _timestamp: {{ $now }}
  _dataCount: {{ $json.length }}
```

---

## 错误分类决策树

```
错误发生
├─ HTTP 状态码?
│   ├─ 401 → 认证错误
│   ├─ 429 → 限流错误
│   ├─ 4xx → 客户端错误（数据格式/参数）
│   ├─ 5xx → 服务端错误（重试）
│   └─ 无 → 继续
├─ 执行错误?
│   ├─ "Cannot read property" → 数据格式错误
│   ├─ "out of memory" → 内存错误
│   ├─ "timeout" → 超时错误
│   └─ "not found" → 节点/连接错误
└─ 其他 → 查看日志 → 手动调试
```

## 最佳实践

1. **防御性编程**: 假设所有外部调用都可能失败
2. **详细日志**: 记录关键步骤和数据状态
3. **重试机制**: 自动重试可恢复的错误
4. **降级策略**: 准备备用方案
5. **监控告警**: 错误时发送通知
