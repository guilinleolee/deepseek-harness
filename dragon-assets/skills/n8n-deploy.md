---
name: n8n-deploy
description: N8N 自动化部署专家。触发词：n8n部署、n8n安装、n8n环境搭建。当需要部署 N8N 到 Docker、配置工作流、集成外部系统时使用。
version: 1.0.0
created: 2026-08-22
tags: [n8n, deployment, docker, workflow, automation, integration]
related:
  - fastgpt-deploy
  - dify-deploy
  - workflow-designer
author: 天龙引擎 / 老李
---

# N8N 部署专家

> 本技能帮助快速部署 N8N，支持 Docker Compose 一键部署、配置工作流、集成外部系统。

---

## 一、部署方案

### 1.1 快速部署（推荐）

```bash
# 方式一：Docker Compose
mkdir n8n && cd n8n
wget https://raw.githubusercontent.com/n8n-io/n8n/master/docker-compose/docker-compose.yml
docker-compose up -d

# 方式二：单个容器
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n
```

### 1.2 环境配置

**docker-compose.yml**：

```yaml
version: '3'
services:
  n8n:
    image: n8nio/n8n:latest
    restart: always
    ports:
      - "5678:5678"
    environment:
      # 基础配置
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_HOST=${N8N_HOST:-localhost}
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      
      # Webhook 配置
      - WEBHOOK_URL=${WEBHOOK_URL:-http://localhost:5678}
      
      # 执行配置
      - EXECUTIONS_MODE=regular
      - EXECUTIONS_TIMEOUT=300
      - EXECUTIONS_TIMEOUT_MAX=600
      
      # AI 配置（可选）
      - AI_OPENAI_API_KEY=${OPENAI_API_KEY}
      - AI_AZURE_OPENAI_API_KEY=${AZURE_OPENAI_KEY}
      
      # 代理配置
      - HTTP_PROXY=${HTTP_PROXY:-}
      - HTTPS_PROXY=${HTTPS_PROXY:-}
      
    volumes:
      - n8n_data:/home/node/.n8n
    networks:
      - n8n-net

  # 可选：PostgreSQL 数据库
  postgres:
    image: postgres:16-alpine
    restart: always
    environment:
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - n8n-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U n8n"]
      interval: 10s
      timeout: 5s
      retries: 5

networks:
  n8n-net:
    driver: bridge

volumes:
  n8n_data:
  postgres_data:
```

### 1.3 外部配置

**.env 文件**：

```bash
# N8N 配置
N8N_PASSWORD=your-secure-password
N8N_HOST=your-domain.com
WEBHOOK_URL=https://your-domain.com
N8N_PROTOCOL=https

# 数据库
POSTGRES_PASSWORD=your-db-password

# AI API Keys
OPENAI_API_KEY=sk-xxx
AZURE_OPENAI_KEY=xxx

# 代理
HTTP_PROXY=
HTTPS_PROXY=
```

---

## 二、常用工作流模板

### 2.1 调用 FastGPT/Dify API

```json
{
  "name": "AI知识库查询",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "httpMethod": "POST",
        "path": "ai-query"
      }
    },
    {
      "name": "调用FastGPT",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://fastgpt:3000/api/chat/completions",
        "method": "POST",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Authorization",
              "value": "Bearer {{ $env.FASTGPT_TOKEN }}"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "appId",
              "value": "{{ $json.appId }}"
            },
            {
              "name": "chatId",
              "value": "{{ $json.chatId }}"
            },
            {
              "name": "messages",
              "value": "{{ $json.messages }}"
            }
          ]
        }
      }
    }
  ]
}
```

### 2.2 定时任务 + 数据同步

```json
{
  "name": "每日数据同步",
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cron",
              "expression": "0 2 * * *"
            }
          ]
        }
      }
    },
    {
      "name": "获取源数据",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://api.source.com/data",
        "method": "GET"
      }
    },
    {
      "name": "转换数据",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "// 数据转换逻辑\nconst items = $input.all();\nreturn items.map(item => ({\n  id: item.json.id,\n  name: item.json.name,\n  timestamp: new Date().toISOString()\n}));"
      }
    },
    {
      "name": "写入目标数据库",
      "type": "n8n-nodes-base.postgres",
      "parameters": {
        "operation": "insert",
        "table": "sync_data",
        "columns": "id, name, timestamp"
      }
    }
  ]
}
```

### 2.3 AI Agent 工作流

```json
{
  "name": "AI智能客服",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "httpMethod": "POST",
        "path": "customer-service"
      }
    },
    {
      "name": "意图识别",
      "type": "n8n-nodes-base.openAi",
      "parameters": {
        "resource": "chat",
        "operation": "complete",
        "messages": {
          "values": [
            {
              "role": "system",
              "content": "判断用户意图：1=咨询，2=投诉，3=下单，4=其他"
            },
            {
              "role": "user",
              "content": "{{ $json.message }}"
            }
          ]
        }
      }
    },
    {
      "name": "路由",
      "type": "n8n-nodes-base.switch",
      "parameters": {
        "dataType": "string",
        "value1": "={{ $json.choices[0].message.content }}",
        "rules": {
          "rules": [
            { "value2": "1", "operation": "equals", "output": 0 },
            { "value2": "2", "operation": "equals", "output": 1 },
            { "value2": "3", "operation": "equals", "output": 2 }
          ]
        },
        "fallbackOutput": 3
      }
    }
  ]
}
```

---

## 三、常用节点配置

### 3.1 数据库节点

**PostgreSQL**：
```json
{
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "user": "postgres",
  "password": "{{ $env.POSTGRES_PASSWORD }}",
  "ssl": false
}
```

**MySQL**：
```json
{
  "host": "localhost",
  "port": 3306,
  "database": "mydb",
  "user": "root",
  "password": "{{ $env.MYSQL_PASSWORD }}"
}
```

### 3.2 HTTP 节点

```json
{
  "method": "POST",
  "url": "https://api.example.com/endpoint",
  "authentication": "genericCredentialType",
  "genericAuthType": "httpQueryAuth",
  "sendHeaders": true,
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer {{ $credentials.api.token }}"
  },
  "sendBody": true,
  "body": "={{ $json }}",
  "options": {
    "timeout": 30000,
    "response": {
      "response": {
        "responseFormat": "json"
      }
    }
  }
}
```

### 3.3 代码节点（JavaScript）

```javascript
// 输入数据处理
const input = $input.first().json;

// 数据转换
const result = {
  id: input.id,
  name: input.name.toUpperCase(),
  score: calculateScore(input)
};

function calculateScore(data) {
  return data.metrics.reduce((sum, m) => sum + m.value, 0);
}

return [{ json: result }];
```

---

## 四、运维命令

### 4.1 常用 Docker 命令

```bash
# 查看日志
docker logs -f n8n

# 进入容器
docker exec -it n8n /bin/sh

# 重启服务
docker-compose restart

# 更新版本
docker-compose pull && docker-compose up -d

# 备份数据
docker exec n8n tar -czf /tmp/backup.tar.gz -C /home/node/.n8n .
docker cp n8n:/tmp/backup.tar.gz ./n8n-backup-$(date +%Y%m%d).tar.gz
```

### 4.2 N8N CLI

```bash
# 进入 N8N 容器
docker exec -it n8n n8n

# 导出工作流
docker exec n8n n8n export:workflow --id=xxx --output=/tmp/workflow.json

# 导入工作流
docker exec -i n8n n8n import:workflow --input=/tmp/workflow.json

# 更新凭据
docker exec -i n8n n8n update:credentials --id=xxx --input=/tmp/credentials.json
```

---

## 五、与 FastGPT/Dify 集成

### 5.1 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                      N8N 编排层                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   触发器                                                         │
│   ├── Webhook ──────── 外部系统调用                              │
│   ├── Schedule ────── 定时任务                                   │
│   └── Event ───────── 事件触发                                   │
│                           ↓                                      │
│   处理节点                                                       │
│   ├── Code ────────── 自定义逻辑                                  │
│   ├── Switch ─────── 条件路由                                   │
│   ├── Loop ───────── 循环处理                                   │
│   └── HTTP Request ─ 外部API调用                                 │
│                           ↓                                      │
│   集成节点                                                       │
│   ├── Database ────── 数据读写                                   │
│   ├── Redis ──────── 缓存/队列                                  │
│   ├── AI Nodes ───── OpenAI/Claude                              │
│   └── Custom ──────── FastGPT/Dify API                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 调用示例

**调用 FastGPT**：
```javascript
// N8N HTTP Request 节点
const response = await fetch('http://fastgpt:3000/api/chat/completions', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${$env.FASTGPT_TOKEN}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    appId: $node["Webhook"].json["appId"],
    messages: $node["Webhook"].json["messages"]
  })
});

const result = await response.json();
return [{ json: result }];
```

**调用 Dify**：
```javascript
// N8N HTTP Request 节点
const response = await fetch('http://dify:5001/v1/chat-messages', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${$env.DIFY_API_KEY}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    inputs: {},
    query: $input.first().json.message,
    response_mode: 'blocking',
    user: 'n8n'
  })
});

const result = await response.json();
return [{ json: result }];
```

---

## 六、故障排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 无法访问 5678 端口 | 容器未启动 | `docker compose ps` 检查 |
| Webhook 不触发 | 抄送未启用 | 在设置中启用抄送 |
| API 调用失败 | 凭据过期 | 重新配置凭据 |
| 执行超时 | 任务耗时过长 | 增加 `EXECUTIONS_TIMEOUT` |

---

## 七、快速检查清单

- [ ] Docker 和 Docker Compose 已安装
- [ ] .env 文件已正确配置
- [ ] N8N 容器运行正常
- [ ] 基本认证已设置
- [ ] 数据库连接已测试
- [ ] Webhook 可正常触发
- [ ] 与 FastGPT/Dify API 集成测试通过

---

*本文档配套：[[fastgpt-deploy]] [[dify-deploy]] [[workflow-designer]]*
