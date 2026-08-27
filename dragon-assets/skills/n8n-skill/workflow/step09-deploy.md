# Step 09: 部署激活

## 目标
将验证通过的工作流部署到 n8n 实例，激活并获取运行时信息。

## 执行流程

### 1. 部署工作流

使用 n8n-mcp 或 REST API：

```javascript
// 方式1: 使用 n8n-mcp
const { workflowId } = await create_workflow(workflow);

// 方式2: 使用 REST API
POST /api/workflows
{
  "name": "工作流名称",
  "nodes": [...],
  "connections": {...},
  "settings": {...},
  "active": false  // 先不激活
}

// 响应
{
  "id": "workflow-id",
  "name": "工作流名称",
  "active": false,
  "createdAt": "2026-02-26T10:00:00.000Z"
}
```

### 2. 激活工作流

```bash
# 激活工作流
PATCH /api/workflows/{id}

{
  "active": true
}

# 响应
{
  "id": "workflow-id",
  "active": true,
  "activatedAt": "2026-02-26T10:00:00.000Z"
}
```

### 3. 运行时验证

```yaml
验证项:
  - 工作流状态: active
  - 触发器状态: running
  - 最近执行: 无错误

API 检查:
  GET /api/workflows/{id}

  GET /api/executions?workflowId={id}&limit=5
```

### 4. Form URL 获取

对于 Webhook 或 Form Trigger：

```yaml
获取方式:
  方式1: API 查询
    GET /api/workflows/{id}

    响应中的 webhooks 数组:
    "webhooks": [
      {
        "path": "webhook-xxx",
        "httpMethod": "POST",
        "testUrl": "https://n8n.example.com/webhook/test-webhook-xxx",
        "productionUrl": "https://n8n.example.com/webhook/webhook-xxx"
      }
    ]

  方式2: UI 查看
    1. 打开工作流编辑器
    2. 点击 Webhook 节点
    3. 查看 "Test URL" 和 "Production URL"

URL 说明:
  - Test URL: 用于测试执行
  - Production URL: 用于生产环境
  - 差异: Test URL 会等待响应，Production URL 不会
```

## 部署场景

### 场景1: 全新部署

```yaml
步骤:
  1. 创建工作流 (POST /api/workflows)
  2. 上传工作流 JSON
  3. 激活工作流 (PATCH /api/workflows/{id})
  4. 验证激活状态
```

### 场景2: 更新现有工作流

```yaml
步骤:
  1. 查询现有工作流 (GET /api/workflows)
  2. 更新工作流 (PATCH /api/workflows/{id})
  3. 或创建新版本 (POST /api/workflows/{id}/versions)
  4. 激活新版本
```

### 场景3: 导入导出

```yaml
导出:
  GET /api/workflows/{id}

  保存为 JSON 文件

导入:
  POST /api/workflows/import

  {
    "workflow": workflowJson
  }
```

## 部署检查清单

### 部署前检查

- [ ] 工作流已通过验证
- [ ] 所有凭据已配置
- [ ] 社区节点已安装
- [ ] 表达式已测试
- [ ] 错误处理已配置

### 部署中检查

- [ ] 工作流创建成功
- [ ] 节点配置完整
- [ ] 连接关系正确
- [ ] 凭据绑定有效

### 部署后检查

- [ ] 工作流已激活
- [ ] 触发器状态正常
- [ ] 测试执行成功
- [ ] Webhook URL 可访问（如适用）
- [ ] 日志记录正常

## 输出格式

### deploy-report.md

```markdown
# 部署报告

## 基本信息

**工作流名称**: [name]
**工作流 ID**: [id]
**部署时间**: [timestamp]
**部署状态**: ✅ 成功 / ❌ 失败

## 部署过程

### 步骤1: 创建工作流

**API 调用**:
```bash
POST /api/workflows
```

**响应**:
```json
{
  "id": "workflow-abc123",
  "name": "邮件通知工作流",
  "active": false,
  "createdAt": "2026-02-26T10:00:00.000Z"
}
```

**状态**: ✅ 成功

### 步骤2: 激活工作流

**API 调用**:
```bash
PATCH /api/workflows/workflow-abc123
{
  "active": true
}
```

**响应**:
```json
{
  "id": "workflow-abc123",
  "active": true,
  "activatedAt": "2026-02-26T10:00:05.000Z"
}
```

**状态**: ✅ 成功

### 步骤3: 运行时验证

**工作流状态**:
- 活跃: ✅
- 触发器: ✅ Schedule Trigger (running)
- 最近执行: ✅ 无错误

**执行测试**:
```json
{
  "executionId": "exec-xyz789",
  "status": "success",
  "finishedAt": "2026-02-26T10:01:00.000Z",
  "data": {
    "processed": 5,
    "errors": 0
  }
}
```

## Webhook 信息

### Test URL
```
https://n8n.example.com/webhook/test-webhook-abc123
```

### Production URL
```
https://n8n.example.com/webhook/webhook-abc123
```

**使用说明**:
- Test URL: 用于开发测试，会等待响应
- Production URL: 用于生产环境，异步执行
- HTTP Method: POST
- Content-Type: application/json

**测试示例**:
```bash
curl -X POST https://n8n.example.com/webhook/test-webhook-abc123 \
  -H "Content-Type: application/json" \
  -d '{"test": true, "message": "Hello"}'
```

## 运行时信息

### 调度信息
- **触发器**: Schedule Trigger
- **Cron 表达式**: 0 9 * * 1-5
- **下次执行**: 2026-02-27T09:00:00.000Z
- **时区**: UTC

### 凭据状态
| 凭据 | 类型 | 状态 |
|------|------|------|
| Gmail account | gmailOAuth2 | ✅ 已授权 |
| Slack Bot | slackApi | ✅ 有效 |

### 社区节点
| 节点 | 版本 | 状态 |
|------|------|------|
| (无) | - | - |

## 监控建议

1. **执行监控**
   - 定期查看执行历史
   - 关注错误率
   - 检查执行时长

2. **性能监控**
   - 监控 API 调用次数
   - 跟踪内存使用
   - 观察响应时间

3. **告警配置**
   - 执行失败通知
   - 性能异常告警
   - API 限流提醒

## 维护建议

1. **日志管理**
   - 定期清理旧日志
   - 保留关键执行记录
   - 导出执行报告

2. **版本管理**
   - 创建工作流版本
   - 记录变更日志
   - 支持快速回滚

3. **安全更新**
   - 定期轮换凭据
   - 更新社区节点
   - 升级 n8n 版本

## 故障排除

### 常见问题

**工作流未执行**:
- 检查激活状态
- 验证触发器配置
- 查看执行日志

**Webhook 未触发**:
- 确认 URL 正确
- 检查网络连接
- 验证请求格式

**凭据错误**:
- 重新授权 OAuth
- 更新 API 密钥
- 检查权限范围

**节点执行失败**:
- 查看节点日志
- 验证输入数据
- 检查 API 状态

## 下一步

- [ ] 设置监控和告警
- [ ] 配置日志记录
- [ ] 创建备份
- [ ] 进入 Step 10: 输出导出
```

## 验证条件

- [ ] 工作流已部署到 n8n
- [ ] 工作流已激活
- [ ] 触发器状态正常
- [ ] 测试执行成功
- [ ] Webhook URL 已获取（如适用）
- [ ] deploy-report.md 已生成

## 错误处理

| 错误 | 处理 |
|------|------|
| 部署失败 | 检查工作流 JSON 格式 |
| 激活失败 | 检查凭据和节点配置 |
| 执行失败 | 查看执行日志，修复问题 |
| Webhook 不可访问 | 检查 n8n 实例网络配置 |

## 安全注意事项

⚠️ **重要**:
1. 不要在生产环境使用 Test URL
2. Webhook URL 应该通过 HTTPS 访问
3. 限制 Webhook 的访问来源
4. 定期审计工作流权限
5. 敏感信息不要记录在日志中

## 下一步

Step 10: 输出导出 - 导出工作流 JSON 并生成最终报告
