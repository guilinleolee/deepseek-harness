# Step 06: 工作流构建

## 目标
使用 n8n-mcp 或手动方式创建工作流 JSON，实现完整的节点配置和连接。

## 执行流程

### 1. n8n_create_workflow (使用 MCP)

如果已安装 n8n-mcp：

```javascript
// 调用 create_workflow 工具
const workflow = {
  name: "工作流名称",
  nodes: [
    // 节点配置数组
  ],
  connections: {
    // 节点连接配置
  },
  settings: {
    // 工作流设置
  }
};

// MCP 调用
await create_workflow(workflow);
```

### 2. 社区节点检查与安装

检查是否需要社区节点：

```yaml
检查流程:
  1. 遍历 design.md 中的节点清单
  2. 识别非内置节点（不在 @n8n/n8n-nodes-* 下）
  3. 使用 REST API 或手动安装

安装方式:
  # 方式1: REST API (需要 n8n 实例 API)
  POST /api/community-nodes/install
  {
    "packageName": "n8n-nodes-xxx"
  }

  # 方式2: 手动安装
  cd ~/.n8n
  npm install n8n-nodes-xxx
  # 重启 n8n
```

### 3. typeVersion 信任链

确保节点版本配置正确：

```yaml
验证流程:
  1. 从 knowledge.md 获取节点 typeVersion
  2. 检查 n8n 实例支持的版本
  3. 使用兼容版本

示例:
  节点: @n8n/n8n-nodes-gmail
  文档版本: 2
  实例支持: [1, 2]
  使用版本: 2

  节点: @n8n/n8n-nodes-slack
  文档版本: 2.1
  实例支持: [1, 2]
  使用版本: 2 (降级到兼容版本)
```

### 4. formTrigger 特殊处理

如果使用 Webhook 或 Form Trigger：

```yaml
特殊配置:
  Webhook 节点:
    - path: 需要唯一标识
    - responseMode: "responseNode" (如需自定义响应)
    - options:
        - httpResponseHeaders: CORS 头

  Form Trigger 节点:
    - formTitle: 表单标题
    - formFields: 字段定义
    - respondMode: "form"
    - responseMessage: 提交成功消息

注意事项:
  - Webhook URL 在激活后才会生成
  - 测试和生产 URL 不同
  - 需要配置 n8n 实例的公网访问
```

## 工作流 JSON 结构

### 完整示例

```json
{
  "name": "邮件通知工作流",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "0 9 * * 1-5"
            }
          ]
        }
      },
      "id": "node-1",
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1.1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "operation": "getAll",
        "limit": 50,
        "filters": {
          "hasAttachment": true
        }
      },
      "id": "node-2",
      "name": "Gmail",
      "type": "n8n-nodes-base.gmail",
      "typeVersion": 2,
      "position": [450, 300],
      "credentials": {
        "gmailOAuth2": {
          "id": "credential-id",
          "name": "Gmail account"
        }
      }
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.labelIds }}",
              "operation": "contains",
              "value2": "IMPORTANT"
            }
          ]
        }
      },
      "id": "node-3",
      "name": "Filter",
      "type": "n8n-nodes-base.filter",
      "typeVersion": 1,
      "position": [650, 300]
    },
    {
      "parameters": {
        "jsCode": "// 生成邮件摘要\nconst emails = items.map(item => item.json);\nconst results = emails.map(email => ({\n  json: {\n    subject: email.subject || '(无主题)',\n    from: email.from,\n    summary: (email.snippet || '').substring(0, 100),\n    url: email.url\n  }\n}));\nreturn results;"
      },
      "id": "node-4",
      "name": "Code",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [850, 300]
    },
    {
      "parameters": {
        "resource": "message",
        "operation": "post",
        "channel": "#alerts",
        "text": "=🔔 **{{ $json.subject }}**\n\n{{ $json.summary }}\n\n来自: {{ $json.from }}"
      },
      "id": "node-5",
      "name": "Slack",
      "type": "n8n-nodes-base.slack",
      "typeVersion": 2.2,
      "position": [1050, 300],
      "credentials": {
        "slackApi": {
          "id": "credential-id",
          "name": "Slack account"
        }
      }
    }
  ],
  "connections": {
    "Schedule Trigger": {
      "main": [
        [
          {
            "node": "Gmail",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Gmail": {
      "main": [
        [
          {
            "node": "Filter",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Filter": {
      "main": [
        [
          {
            "node": "Code",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Code": {
      "main": [
        [
          {
            "node": "Slack",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "settings": {
    "executionOrder": "v1"
  },
  "staticData": null,
  "tags": [],
  "triggerCount": 1,
  "updatedAt": "2026-02-26T10:00:00.000Z",
  "versionId": "1"
}
```

## 节点配置模板

### Trigger 节点模板

```json
// Schedule Trigger
{
  "parameters": {
    "rule": {
      "interval": [
        {
          "field": "cronExpression",
          "expression": "0 9 * * 1-5"
        }
      ]
    }
  },
  "type": "n8n-nodes-base.scheduleTrigger",
  "typeVersion": 1.1
}

// Webhook Trigger
{
  "parameters": {
    "path": "webhook-{{ $workflow.id }}",
    "responseMode": "responseNode",
    "options": {
      "httpResponseHeaders": {
        "entries": [
          {
            "name": "Access-Control-Allow-Origin",
            "value": "*"
          }
        ]
      }
    }
  },
  "type": "n8n-nodes-base.webhook",
  "typeVersion": 1.1
}
```

### Action 节点模板

```json
// HTTP Request
{
  "parameters": {
    "url": "https://api.example.com/endpoint",
    "authentication": "genericCredentialType",
    "genericAuthType": "httpHeaderAuth",
    "method": "POST",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {
          "name": "key",
          "value": "={{ $json.value }}"
        }
      ]
    }
  },
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4.1
}

// IF 节点
{
  "parameters": {
    "conditions": {
      "string": [
        {
          "value1": "={{ $json.status }}",
          "operation": "equals",
          "value2": "success"
        }
      ]
    }
  },
  "type": "n8n-nodes-base.if",
  "typeVersion": 2
}

// Switch 节点
{
  "parameters": {
    "dataType": "string",
    "propertyName": "type",
    "rules": {
      "values": [
        {
          "output": 0,
          "value": "email"
        },
        {
          "output": 1,
          "value": "sms"
        }
      ]
    }
  },
  "type": "n8n-nodes-base.switch",
  "typeVersion": 3
}
```

## 输出格式

### workflow.json

保存在 `runs/{timestamp}-{slug}/workflow.json`

```json
{
  "name": "工作流名称",
  "nodes": [...],
  "connections": {...},
  "settings": {...}
}
```

### build-report.md

```markdown
# 工作流构建报告

## 基本信息
- **工作流名称**: [name]
- **节点数量**: X
- **构建时间**: [timestamp]

## 节点配置清单

| 节点 | 类型 | 版本 | 凭据 | 状态 |
|------|------|------|------|------|
| Schedule Trigger | n8n-nodes-base.scheduleTrigger | 1.1 | - | ✅ |
| Gmail | n8n-nodes-base.gmail | 2 | gmailOAuth2 | ✅ |
| Filter | n8n-nodes-base.filter | 1 | - | ✅ |
| Code | n8n-nodes-base.code | 2 | - | ✅ |
| Slack | n8n-nodes-base.slack | 2.2 | slackApi | ✅ |

## 社区节点安装

| 节点包 | 版本 | 状态 |
|--------|------|------|
| n8n-nodes-xxx | 1.0.0 | ✅ 已安装 |

## 连接关系

```
Schedule Trigger → Gmail → Filter → {
                                       → Code → Slack
                                     }
```

## 特殊配置

### Webhook 配置
- **Path**: `webhook-{{ $workflow.id }}`
- **Test URL**: (待激活后生成)
- **Production URL**: (待激活后生成)

### 凭据引用
- **Gmail**: `gmailOAuth2:credential-id`
- **Slack**: `slackApi:credential-id`

## 验证检查
- [ ] 所有节点 typeVersion 匹配
- [ ] 社区节点已安装
- [ ] 节点连接正确
- [ ] 表达式语法验证
- [ ] 凭据引用有效

## 下一步
Step 07: 配置凭据
```

## 验证条件

- [ ] workflow.json 已生成
- [ ] 所有节点配置完整
- [ ] 节点连接关系正确
- [ ] typeVersion 已验证
- [ ] 社区节点已安装（如需要）
- [ ] build-report.md 已生成

## 错误处理

| 错误 | 处理 |
|------|------|
| 节点不存在 | 检查节点类型，确认是内置还是社区 |
| typeVersion 不匹配 | 降级到兼容版本 |
| 凭据未配置 | 占位符，等待 Step 07 |
| 表达式语法错误 | 验证并修正 |

## 下一步

Step 07: 凭据配置 - 使用 REST API 配置工作流凭据
