# 客服工作台 V0.1 · 本地部署骨架

> 天龙引擎 dragon-engine V2.5 · 客服子系统 MVP 部署包
>
> 本骨架提供 C 端客服系统的最小可运行环境：PostgreSQL + MinIO + FastGPT + faster-whisper + 客服后端

---

## 包含服务

| 服务 | 端口 | 用途 |
|------|------|------|
| PostgreSQL 16 | 5432 | 客服独立数据库（10 张表 + 音频字段） |
| MinIO | 9000/9001 | 音频/文件对象存储 |
| FastGPT | 3000 | RAG 知识库底座 |
| faster-whisper | 8001 | 本地 ASR（语音转文字） |
| 客服后端 | 8080 | 业务服务（Fastify） |

---

## 快速启动（3 步）

### 1. 启动 Docker Desktop

Win 键 → 输入 "Docker Desktop" → 打开。等右下角托盘图标变绿。

### 2. 复制环境配置并启动

方法 A（推荐）：双击 `start.bat`

方法 B（PowerShell）：

```powershell
cd "D:\deepseek-harness\dragon-engine\customer-service-deploy"
Copy-Item .env.example .env
# 编辑 .env，至少修改 POSTGRES_PASSWORD 和 OPENAI_API_KEY
docker compose up -d
```

第一次启动会拉镜像 + 初始化数据库，约 5-10 分钟。

### 3. 验证启动成功

```powershell
docker compose ps
curl http://localhost:8080/health
```

浏览器访问：
- http://localhost:8080/health — 后端健康检查
- http://localhost:3000 — FastGPT 管理后台
- http://localhost:9001 — MinIO 控制台

---

## LLM 配置（OpenAI 兼容 · MiniMax）

在 .env 中填入：

```
OPENAI_BASE_URL=https://api.minimax.chat/v1
OPENAI_API_KEY=sk-cp-your-key-here
OPENAI_MODEL=MiniMax-M3
```

直接复用 D:\deepseek-harness\dragon-engine\.env 里的 OPENAI_API_KEY 和 OPENAI_BASE_URL。

---

## 音频链路（完全本地 · 零费用）

- ASR：faster-whisper（本地）
- TTS：edge-tts（微软 Edge 免费 API）

无需任何 API Key，无需任何付费。

---

## 目录结构

```
customer-service-deploy/
├── docker-compose.yml
├── .env.example
├── .env
├── .gitignore
├── README.md
├── start.bat / start.ps1
├── postgres/init/001_init.sql
├── fastgpt/
├── minio/
└── backend/
    ├── Dockerfile
    ├── package.json
    ├── tsconfig.json
    └── src/
        ├── app.ts
        ├── routes/health.ts
        └── adapters/{llm,asr,tts}.ts
```

---

## 常用命令

```powershell
docker compose ps
docker compose logs -f backend
docker compose restart backend
docker compose exec postgres psql -U cs_admin -d customer_service
docker compose down          # 停止
docker compose down -v        # 完全清理（含数据卷）
```

---

## 硬件需求

| 配置 | 最低 | 推荐 |
|------|------|------|
| CPU | 4 核 | 8 核 |
| 内存 | 8 GB | 16 GB |
| 磁盘 | 50 GB SSD | 100 GB SSD |

---

## 协议

- 编排文件：MIT
- PostgreSQL：PostgreSQL License
- MinIO：AGPL-3.0（仅自用部署）
- FastGPT：MIT
- faster-whisper：MIT
- edge-tts：MIT（基于微软 Edge 公开 API）
