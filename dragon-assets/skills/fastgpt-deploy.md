---
name: fastgpt-deploy
description: FastGPT 自动化部署专家。触发词：fastgpt部署、fastgpt安装、fastgpt环境搭建。当需要部署 FastGPT 到 Docker、配置知识库、设置 RAG 管道时使用。
version: 1.0.0
created: 2026-08-22
tags: [fastgpt, deployment, docker, rag, knowledge-base]
related:
  - dify-deploy
  - n8n-deploy
  - rag-knowledge-builder
author: 天龙引擎 / 老李
---

# FastGPT 部署专家

> 本技能帮助快速部署 FastGPT，支持 Docker Compose 一键部署、配置知识库、优化 RAG 管道。

---

## 一、部署方案

### 1.1 快速部署（推荐）

```bash
# 方式一：使用官方 docker-compose
git clone https://github.com/labring/fastgpt.git
cd fastgpt
docker-compose -f docker-compose.yml up -d

# 方式二：OneAPI 中转（推荐用于国产模型）
# 先部署 OneAPI
docker run -d --name oneapi \
  -p 3000:3000 \
  -v ./data:/app/data \
  songmagic/oneapi:latest
```

### 1.2 环境配置

**docker-compose.yml 示例**：

```yaml
version: '3.8'
services:
  mongo:
    image: mongo:6.0
    container_name: fastgpt-mongo
    restart: always
    ports:
      - "27017:27017"
    volumes:
      - ./mongo/data:/data/db
    networks:
      - fastgpt-net

  pg:
    image: pgvector/pgvector:0.5.1
    container_name: fastgpt-pg
    restart: always
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: fastgpt
      POSTGRES_PASSWORD: fastgpt123456
      POSTGRES_DB: fastgpt
    volumes:
      - ./pg/data:/var/lib/postgresql/data
    networks:
      - fastgpt-net

  fastgpt:
    image: registry.cn-hangzhou.aliyuncs.com/fastgpt/fastgpt:latest
    container_name: fastgpt
    restart: always
    ports:
      - "3000:3000"
    depends_on:
      - mongo
      - pg
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      API_URL: http://oneapi: 3000  # 如使用 OneAPI
      DB_MAX: 5
      TOKEN: ${TOKEN}
    volumes:
      - ./config.json:/app/data/config.json
      - ./logo.svg:/app/logo.svg
    networks:
      - fastgpt-net

networks:
  fastgpt-net:
    driver: bridge
```

### 1.3 OneAPI 配置（国产模型支持）

```json
{
  "channel": "openai",
  "key": "sk-xxx",
  "base_url": "https://api.deepseek.com/v1",
  "name": "DeepSeek"
}
```

---

## 二、知识库配置

### 2.1 文档上传设置

| 配置项 | 推荐值 | 说明 |
|--------|--------|------|
| **切片模式** | naive | 按段落切片 |
| **切片大小** | 500 | token 数量 |
| **重叠大小** | 50 | 相邻切片重叠 |
| **检索模式** | 混合检索 | 向量+关键词 |

### 2.2 RAG 参数优化

```json
{
  "rerank": true,
  "rerankModel": "bge-reranker-base",
  "topK": 5,
  "similarityThreshold": 0.5,
  "vectorStore": "pgvector"
}
```

---

## 三、API 集成

### 3.1 调用示例

```bash
# 获取应用列表
curl -X GET http://localhost:3000/api/model/requestList \
  -H "Authorization: Bearer ${TOKEN}"

# 创建知识库
curl -X POST http://localhost:3000/api/kb/create \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "产品知识库",
    "intro": "产品手册和FAQ"
  }'

# 上传文档
curl -X POST http://localhost:3000/api/kb/file/upload \
  -F "file=@./manual.pdf" \
  -F "kbId=${KB_ID}" \
  -H "Authorization: Bearer ${TOKEN}"
```

### 3.2 与 N8N/Dify 集成

```javascript
// N8N HTTP Request 节点配置
const response = await fetch('http://fastgpt:3000/api/chat/completions', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + $credentials.fastgpt.apiKey,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    chatId: $json.chatId,
    appId: $json.appId,
    messages: $json.messages
  })
});
```

---

## 四、运维命令

### 4.1 常用 Docker 命令

```bash
# 查看日志
docker logs -f fastgpt

# 重启服务
docker-compose restart fastgpt

# 更新版本
docker-compose pull && docker-compose up -d

# 数据备份
docker exec fastgpt-pg pg_dump -U fastgpt fastgpt > backup.sql
```

### 4.2 健康检查

```bash
# 检查服务状态
curl http://localhost:3000/api/version

# 检查数据库连接
docker exec fastgpt-pg psql -U fastgpt -d fastgpt -c "SELECT 1"
```

---

## 五、故障排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 无法上传文档 | 文件太大 | 修改 `maxFileSize` 配置 |
| 检索不准 | 切片策略不当 | 调整切片大小和 overlap |
| 模型调用失败 | API Key 错误 | 检查环境变量 |
| 响应慢 | 硬件资源不足 | 增加 CPU/内存 |

---

## 六、快速检查清单

- [ ] Docker 和 Docker Compose 已安装
- [ ] MongoDB 和 PostgreSQL 容器运行正常
- [ ] OneAPI 已配置（如使用国产模型）
- [ ] 环境变量已设置（API_KEY, TOKEN）
- [ ] 知识库已创建并上传文档
- [ ] API 调用测试通过

---

*本文档配套：[[dify-deploy]] [[n8n-deploy]] [[rag-knowledge-builder]]*
