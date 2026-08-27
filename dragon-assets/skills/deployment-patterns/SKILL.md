---
license: UNKNOWN
name: deployment-patterns
description: Deployment workflows, CI/CD pipeline patterns, Docker containerization, health checks, rollback strategies, and production readiness checklists for web applications.
github_repo: affaan-m/everything-claude-code
github_hash: 4e66b2882da9afb9747468b08a253ca2f09c85f3
last_updated: 2026-04-25
source_type: derived
origin: ECC (everything-claude-code)
triggers: ["deployment patterns", "Deployment Patterns — 部署模式"]
---

# Deployment Patterns — 部署模式

> 来源: [affaan-m/everything-claude-code/skills/deployment-patterns](https://github.com/affaan-m/everything-claude-code)

## 功能概述

生产部署工作流和CI/CD最佳实践，覆盖部署策略、Docker容器化、健康检查、回滚策略和生产就绪检查清单。

## 何时使用

- 设置CI/CD流水线
- Docker化应用程序
- 规划部署策略（蓝绿、金丝雀、滚动）
- 实现健康检查和就绪探针
- 准备生产发布
- 配置环境特定设置

## 部署策略

### 滚动部署（默认）

逐步替换实例——新旧版本在推出期间同时运行。

```
实例1: v1 → v2  (先更新)
实例2: v1        (仍在运行v1)
实例3: v1        (仍在运行v1)
```

**适用场景:** 标准部署、向后兼容的变更

### 蓝绿部署

运行两个完全相同的环境。原子切换流量。

```
Blue  (v1) ← 流量
Green (v2)   空闲，运行新版本

# 验证后:
Blue  (v1)   空闲(成为备用)
Green (v2) ← 流量
```

**适用场景:** 关键服务、零容忍问题

### 金丝雀部署

首先将小部分流量路由到新版本。

```
v1: 95% 流量
v2:  5% 流量  (金丝雀)

# 指标正常后:
v1: 50% 流量
v2: 50% 流量

# 最终:
v2: 100% 流量
```

**适用场景:** 高流量服务、风险变更、功能开关

## 多阶段Dockerfile

### Node.js

```dockerfile
# Stage 1: 安装依赖
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# Stage 2: 构建
FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build && npm prune --production

# Stage 3: 生产镜像
FROM node:22-alpine AS runner
WORKDIR /app
RUN addgroup -g 1001 -S appgroup && adduser -S appuser -u 1001
USER appuser
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appgroup /app/dist ./dist
COPY --from=builder --chown=appuser:appgroup /app/package.json ./
ENV NODE_ENV=production
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:3000/health || exit 1
CMD ["node", "dist/server.js"]
```

### Go

```dockerfile
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /server ./cmd/server

FROM alpine:3.19 AS runner
RUN apk --no-cache add ca-certificates && adduser -D -u 1001 appuser
USER appuser
COPY --from=builder /server /server
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:8080/health || exit 1
CMD ["/server"]
```

### Python/Django

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

FROM python:3.12-slim AS runner
WORKDIR /app
RUN useradd -r -u 1001 appuser
USER appuser
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" || exit 1
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

## 天龙引擎集成

### 适用岗位

| 岗位 | 集成方式 | 增强能力 |
|------|---------|---------|
| **08发布师** | 部署流水线 | CI/CD模式 + 健康检查 + 回滚策略 |
| **03构建师** | 容器化构建 | 多阶段Dockerfile + 安全加固 |
| **02架构师** | 部署架构设计 | 蓝绿/金丝雀/滚动策略选择 |

### 天龙引擎增强

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎部署体系                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   部署策略选择:                                             │
│   ├── 滚动部署 → 标准变更                                  │
│   ├── 蓝绿部署 → 关键服务零风险                           │
│   └── 金丝雀 → 高流量 + 风险变更                         │
│                                                             │
│   协同技能:                                                 │
│   ├── /docker-patterns  → 容器安全                        │
│   ├── /benchmark        → 性能验证                        │
│   ├── /canary-watch     → 部署后监控                      │
│   └── /security-scan     → 安全扫描                       │
│                                                             │
│   发布师工作流:                                             │
│   构建 → 测试 → 镜像 → 验证 → 金丝雀 → 全量              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心命令

```bash
# GitHub Actions CI/CD
[@发布师] 设置CI/CD流水线，支持滚动/蓝绿/金丝雀部署

# Docker安全构建
[@构建师] 使用多阶段Dockerfile优化镜像大小
[@05] 审查Docker安全配置

# 部署验证
[@发布师] 部署后启用canary-watch监控
[@04] 运行冒烟测试验证部署

# 回滚操作
[@发布师] 执行回滚到上一版本
[@发布师] 验证回滚完成
```

### 生产就绪检查清单

**应用:**
- [ ] 所有测试通过
- [ ] 代码和配置中无硬编码密钥
- [ ] 错误处理覆盖所有边缘情况
- [ ] 日志结构化(JSON)且不含PII
- [ ] 健康检查端点返回有意义状态

**基础设施:**
- [ ] Docker镜像可重现构建
- [ ] 环境变量已记录并在启动时验证
- [ ] 设置资源限制(CPU、内存)
- [ ] 配置水平扩展(最小/最大实例)
- [ ] 所有端点启用SSL/TLS

**监控:**
- [ ] 导出应用指标(请求率、延迟、错误)
- [ ] 配置错误率告警
- [ ] 设置日志聚合
- [ ] 健康端点配置正常运行监控

**安全:**
- [ ] 依赖扫描CVE
- [ ] CORS配置为仅允许的来源
- [ ] 公共端点启用速率限制
- [ ] 验证认证和授权
- [ ] 设置安全头(CSP、HSTS、X-Frame-Options)

## 参考资料

- [Everything Claude Code](https://github.com/affaan-m/everything-claude-code)
- [ECC deployment-patterns](https://github.com/affaan-m/everything-claude-code/tree/main/skills/deployment-patterns)

---

**版本**: V1.0 | **兼容性**: 天龙引擎 V8.67+ | **来源**: ECC
