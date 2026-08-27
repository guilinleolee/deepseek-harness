---
license: UNKNOWN
name: docker-patterns
description: Docker and Docker Compose patterns for local development, container security, networking, volume strategies, and multi-service orchestration.
github_repo: affaan-m/everything-claude-code
github_hash: 4e66b2882da9afb9747468b08a253ca2f09c85f3
last_updated: 2026-04-25
source_type: derived
origin: ECC (everything-claude-code)
triggers: ["docker patterns", "Docker Patterns — Docker模式"]
---

# Docker Patterns — Docker模式

> 来源: [affaan-m/everything-claude-code/skills/docker-patterns](https://github.com/github.com/affaan-m/everything-claude-code)

## 功能概述

本地开发、多容器架构的Docker和Docker Compose最佳实践，覆盖容器安全、网络、卷策略和多服务编排。

## 何时激活

- 为本地开发设置Docker Compose
- 设计多容器架构
- 排查容器网络或卷问题
- 审查Dockerfile的安全性和大小
- 从本地开发迁移到容器化工作流

## Docker Compose本地开发

### 标准Web应用栈

```yaml
# docker-compose.yml
services:
  app:
    build:
      context: .
      target: dev
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - DATABASE_URL=postgres://postgres:postgres@db:5432/app_dev
      - REDIS_URL=redis://redis:6379/0
      - NODE_ENV=development
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    command: npm run dev

  db:
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: app_dev
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data

  mailpit:
    image: axllent/mailpit
    ports:
      - "8025:8025"
      - "1025:1025"

volumes:
  pgdata:
  redisdata:
```

## 网络模式

### 服务发现

同一Compose网络中的服务通过服务名解析：
```
# 从"app"容器:
postgres://postgres:postgres@db:5432/app_dev
redis://redis:6379/0
```

### 自定义网络

```yaml
services:
  frontend:
    networks:
      - frontend-net
  api:
    networks:
      - frontend-net
      - backend-net
  db:
    networks:
      - backend-net    # 仅api可访问,frontend不可

networks:
  frontend-net:
  backend-net:
```

## 容器安全

### Dockerfile加固

```dockerfile
# 1. 使用特定标签(从不: latest)
FROM node:22.12-alpine3.20

# 2. 以非root用户运行
RUN addgroup -g 1001 -S app && adduser -S app -u 1001
USER app

# 3. Compose中丢弃能力
# 4. 尽可能使用只读根文件系统
# 5. 镜像层中不包含密钥
```

### Compose安全配置

```yaml
services:
  app:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
      - /app/.cache
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
```

## 天龙引擎集成

### 适用岗位

| 岗位 | 集成方式 | 增强能力 |
|------|---------|---------|
| **08发布师** | 生产容器编排 | Docker Compose + 安全配置 |
| **03构建师** | 本地开发环境 | 容器化开发栈 |
| **05安全师** | 容器安全审查 | 安全加固 + 密钥管理 |

### 天龙引擎增强

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎 Docker容器体系                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   开发栈:                                                   │
│   ├── Docker Compose → 本地多服务编排                      │
│   ├── 多阶段Dockerfile → 镜像优化                         │
│   └── .dockerignore → 减小构建上下文                       │
│                                                             │
│   安全加固:                                                │
│   ├── 非root用户 → 能力丢弃                               │
│   ├── 只读根文件系统 → tmpfs                             │
│   └── 密钥管理 → env_file / Docker secrets                 │
│                                                             │
│   协同技能:                                                 │
│   ├── /deployment-patterns → CI/CD流水线                 │
│   ├── /security-scan     → 安全扫描                       │
│   └── /benchmark         → 容器性能测试                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心命令

```bash
# 本地开发环境
[@构建师] 使用Docker Compose搭建本地开发环境
[@构建师] 配置多阶段Dockerfile优化镜像

# 安全审查
[@05] 审查Dockerfile安全配置
[@05] 检查docker-compose.yml密钥暴露

# 容器调试
docker compose logs -f app
docker compose exec app sh
docker compose top

# 清理
docker compose down -v
docker system prune
```

### .dockerignore模板

```
node_modules
.git
.env
.env.*
dist
coverage
*.log
.next
.cache
docker-compose*.yml
Dockerfile*
README.md
tests/
```

## 参考资料

- [Everything Claude Code](https://github.com/affaan-m/everything-claude-code)
- [ECC docker-patterns](https://github.com/affaan-m/everything-claude-code/tree/main/skills/docker-patterns)

---

**版本**: V1.0 | **兼容性**: 天龙引擎 V8.67+ | **来源**: ECC
