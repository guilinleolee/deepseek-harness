---
name: dify-deploy
description: Dify 自动化部署专家。触发词：dify部署、dify安装、dify环境搭建。当需要部署 Dify 到 Docker、配置工作流、设置 Agent 时使用。
version: 1.0.0
created: 2026-08-22
tags: [dify, deployment, docker, workflow, agent, llm]
related:
  - fastgpt-deploy
  - n8n-deploy
  - workflow-designer
author: 天龙引擎 / 老李
---

# Dify 部署专家

> 本技能帮助快速部署 Dify，支持 Docker Compose 一键部署、配置工作流、构建 Agent 应用。

---

## 一、部署方案

### 1.1 快速部署（推荐）

```bash
# 克隆官方仓库
git clone https://github.com/dify-ai/dify.git
cd dify/docker

# 一键部署
docker-compose up -d

# 或使用 Docker Compose v2
docker compose up -d
```

### 1.2 环境配置

**.env 文件配置**：

```bash
# 必填配置
SECRET_KEY=your-secret-key-here

# 数据库配置
DB_USERNAME=postgres
DB_PASSWORD=dify123456
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=dify

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=dify123456

# LLM 配置（可选，使用 Dify 内置的模型供应商）
# 或配置 OneAPI
CODE_EXECUTION_ENDPOINT=http://localhost:3000/api

# 向量数据库（可选，默认使用 pgvector）
# PGVECTOR_HOST=localhost
# PGVECTOR_PORT=5432
```

### 1.3 完整 docker-compose 配置

```yaml
version: '3'
services:
  api:
    image: langgenius/dify-api:latest
    restart: always
    ports:
      - "5001:5001"
    environment:
      SECRET_KEY: ${SECRET_KEY}
      DB_USERNAME: ${DB_USERNAME}
      DB_PASSWORD: ${DB_PASSWORD}
      DB_HOST: db
      DB_PORT: 5432
      DB_DATABASE: ${DB_DATABASE}
      REDIS_HOST: redis
      REDIS_PORT: 6379
      REDIS_PASSWORD: ${REDIS_PASSWORD}
    volumes:
      - ./volumes/db:/var/lib/postgresql/data
    depends_on:
      - db
      - redis
    networks:
      - dify-net

  worker:
    image: langgenius/dify-api:latest
    restart: always
    environment:
      SECRET_KEY: ${SECRET_KEY}
      DB_USERNAME: ${DB_USERNAME}
      DB_PASSWORD: ${DB_PASSWORD}
      DB_HOST: db
      DB_PORT: 5432
      DB_DATABASE: ${DB_DATABASE}
      REDIS_HOST: redis
      REDIS_PORT: 6379
      REDIS_PASSWORD: ${REDIS_PASSWORD}
    volumes:
      - ./volumes/db:/var/lib/postgresql/data
    depends_on:
      - db
      - redis
    networks:
      - dify-net

  web:
    image: langgenius/dify-web:latest
    restart: always
    ports:
      - "3000:3000"
    environment:
      CONSOLE_WEB_URL: http://localhost:3000
      APP_WEB_URL: http://localhost:3000
      API_URL: http://api:5001
    depends_on:
      - api
    networks:
      - dify-net

  db:
    image: pgvector/pgvector:0.5.1-pg16
    restart: always
    environment:
      POSTGRES_USER: ${DB_USERNAME}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_DATABASE}
    volumes:
      - ./volumes/db:/var/lib/postgresql/data
    networks:
      - dify-net

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - ./volumes/redis:/data
    networks:
      - dify-net

  nginx:
    image: nginx:latest
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web
      - api
    networks:
      - dify-net

networks:
  dify-net:
    driver: bridge
```

---

## 二、应用创建

### 2.1 应用类型选择

| 类型 | 适用场景 | 特点 |
|------|---------|------|
| **Chatbot** | 客服对话 | 支持多轮对话 |
| **Agent** | 复杂推理任务 | Tool 调用能力 |
| **Workflow** | 流程自动化 | 可视化编排 |
| **Completion** | 文本生成 | 单次生成 |

### 2.2 工作流节点

| 节点类型 | 功能 | 适用场景 |
|---------|------|---------|
| **LLM** | 调用大模型 | AI 生成内容 |
| **Knowledge Retrieval** | 知识库检索 | RAG 问答 |
| **Condition** | 条件分支 | 逻辑判断 |
| **IF/ELSE** | 多条件分支 | 复杂流程 |
| **Loop** | 循环迭代 | 批量处理 |
| **HTTP Request** | HTTP 调用 | 外部集成 |
| **Code** | 代码执行 | 自定义逻辑 |
| **Template** | 模板渲染 | 格式化输出 |

### 2.3 Agent 配置示例

```yaml
# Agent 提示词模板
model: gpt-4
prompt: |
  你是一个智能助手，可以调用以下工具来完成任务：
  
  可用工具：
  - search_knowledge: 搜索知识库
  - call_api: 调用外部API
  - calculate: 数学计算
  
  请根据用户的问题，选择合适的工具来回答。

tools:
  - name: search_knowledge
    type: http
    config:
      url: http://fastgpt:3000/api/kb/search
      method: POST
      headers:
        Authorization: Bearer ${FASTGPT_TOKEN}
  
  - name: call_api
    type: http
    config:
      url: ${EXTERNAL_API_URL}
      method: GET
```

---

## 三、API 集成

### 3.1 调用示例

```bash
# 获取应用信息
curl -X GET http://localhost:5001/v1/app-info \
  -H "Authorization: Bearer ${API_KEY}"

# 发送消息
curl -X POST http://localhost:5001/v1/chat-messages \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {},
    "query": "你好",
    "response_mode": "blocking",
    "conversation_id": "",
    "user": "user-123"
  }'

# 流式响应
curl -X POST http://localhost:5001/v1/chat-messages \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {},
    "query": "你好",
    "response_mode": "streaming",
    "user": "user-123"
  }'
```

### 3.2 与 N8N/FastGPT 集成

```javascript
// N8N HTTP Request 节点
const response = await fetch('http://dify:5001/v1/chat-messages', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + $credentials.dify.apiKey,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    inputs: {},
    query: $json.userMessage,
    response_mode: 'streaming',
    user: 'n8n-integration'
  })
});
```

---

## 四、运维命令

### 4.1 常用 Docker 命令

```bash
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f api
docker compose logs -f worker
docker compose logs -f web

# 重启服务
docker compose restart

# 更新版本
docker compose pull && docker compose up -d

# 数据备份
docker exec dify-db pg_dump -U postgres dify > backup.sql
```

### 4.2 健康检查

```bash
# API 健康检查
curl http://localhost:5001/health

# Web 健康检查
curl http://localhost:3000/health
```

---

## 五、故障排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| API 500 错误 | 数据库连接失败 | 检查 DB 配置 |
| 工作流不执行 | Worker 未启动 | `docker compose up -d worker` |
| 模型调用失败 | API Key 未配置 | 在 Dify 控制台配置模型供应商 |
| 知识库检索不准 | 向量数据未索引 | 重新索引知识库 |

---

## 六、快速检查清单

- [ ] Docker 和 Docker Compose 已安装
- [ ] .env 文件已正确配置
- [ ] 所有容器运行正常
- [ ] 模型供应商已配置（OpenAI/Claude/国产）
- [ ] 应用已创建并测试通过
- [ ] API 调用测试通过

---

## 七、与 FastGPT/N8N 的协作

```
┌─────────────────────────────────────────────────────────────────┐
│                    Dify + FastGPT + N8N 协作架构               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   N8N (编排层)                                                   │
│   ├── Webhook 触发                                               │
│   ├── 业务逻辑处理                                               │
│   └── 调用 Dify API / FastGPT API                               │
│                           ↓                                     │
│              ┌─────────────┴─────────────┐                      │
│              ↓                           ↓                       │
│      ┌───────────────┐         ┌───────────────┐              │
│      │     Dify      │         │   FastGPT    │              │
│      │  Agent/工作流  │         │   RAG知识库   │              │
│      └───────────────┘         └───────────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

*本文档配套：[[fastgpt-deploy]] [[n8n-deploy]] [[workflow-designer]]*
