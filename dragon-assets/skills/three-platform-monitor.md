---
name: three-platform-monitor
description: 三平台统一监控专家。触发词：三平台监控、运维监控、平台状态、故障排查。当需要监控 N8N/FastGPT/Dify 三平台运行状态、排查故障时使用。
version: 1.0.0
created: 2026-08-22
tags: [monitoring, ops, n8n, fastgpt, dify, dashboard]
related:
  - n8n-deploy
  - fastgpt-deploy
  - dify-deploy
author: 天龙引擎 / 老李
---

# 三平台统一监控专家

> 本技能提供 N8N、FastGPT、Dify 三平台的统一监控方案，包括状态检查、指标收集、告警配置和故障排查。

---

## 一、监控架构

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        三平台统一监控架构                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐            │
│   │    N8N     │     │   FastGPT   │     │    Dify     │            │
│   │  编排层    │     │  知识库层   │     │   AI层     │            │
│   └──────┬──────┘     └──────┬──────┘     └──────┬──────┘            │
│          │                    │                    │                     │
│          └────────────────────┼────────────────────┘                     │
│                               ▼                                          │
│   ┌──────────────────────────────────────────────────────────────┐    │
│   │                     监控收集层 (Exporter)                      │    │
│   │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │    │
│   │   │ N8N Metrics │  │ FastGPT     │  │ Dify        │        │    │
│   │   │             │  │ Metrics     │  │ Metrics     │        │    │
│   │   └─────────────┘  └─────────────┘  └─────────────┘        │    │
│   └──────────────────────────────────────────────────────────────┘    │
│                               │                                          │
│                               ▼                                          │
│   ┌──────────────────────────────────────────────────────────────┐    │
│   │                     Prometheus / 数据存储                      │    │
│   └──────────────────────────────────────────────────────────────┘    │
│                               │                                          │
│                               ▼                                          │
│   ┌──────────────────────────────────────────────────────────────┐    │
│   │                     Grafana 可视化                            │    │
│   │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │    │
│   │   │ 服务状态 │  │ API调用  │  │ 错误率  │  │ 响应延迟 │       │    │
│   │   └─────────┘  └─────────┘  └─────────┘  └─────────┘       │    │
│   └──────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 监控指标矩阵

| 平台 | 核心指标 | 告警阈值 | 采集方式 |
|------|---------|---------|---------|
| **N8N** | 工作流执行次数 | >1000/小时 | API |
| **N8N** | 失败率 | >5% | 日志 |
| **FastGPT** | 对话响应时间 | >10s | API |
| **FastGPT** | 知识库检索时间 | >2s | 日志 |
| **Dify** | API 响应时间 | >5s | Prometheus |
| **Dify** | Worker 队列长度 | >100 | API |

---

## 二、快速检查命令

### 2.1 N8N 健康检查

```bash
# 检查容器状态
docker ps | grep n8n

# 检查服务状态
curl -s http://localhost:5678/healthz

# 检查 Webhook 可达性
curl -s -o /dev/null -w "%{http_code}" http://localhost:5678/webhook/test

# 查看最近错误
docker logs n8n --tail 100 | grep -i error

# 检查数据库连接
docker exec n8n-postgres psql -U n8n -c "SELECT 1"
```

### 2.2 FastGPT 健康检查

```bash
# 检查容器状态
docker ps | grep fastgpt

# 检查 API 状态
curl -s http://localhost:3000/api/version

# 检查数据库连接
docker exec fastgpt-pg psql -U fastgpt -d fastgpt -c "SELECT 1"

# 检查向量数据库
docker exec fastgpt-pg psql -U fastgpt -d fastgpt -c "SELECT COUNT(*) FROM vectors"

# 测试知识库检索
curl -X POST http://localhost:3000/api/kb/search \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"kbId":"test","query":"测试"}'
```

### 2.3 Dify 健康检查

```bash
# 检查容器状态
docker compose ps

# 检查 API 健康
curl -s http://localhost:5001/health

# 检查 Worker 状态
curl -s http://localhost:5001/info | jq '.provider'

# 检查 Web 服务
curl -s http://localhost:3000/api/datasets

# 查看 Worker 日志
docker compose logs worker --tail 100 | grep -i error

# 检查数据库
docker exec dify-db psql -U postgres -d dify -c "SELECT 1"
```

---

## 三、监控仪表板

### 3.1 Grafana 仪表板配置

```json
{
  "dashboard": {
    "title": "三平台统一监控",
    "panels": [
      {
        "title": "服务状态总览",
        "type": "stat",
        "targets": [
          { "expr": "up{job='n8n'}", "legendFormat": "N8N" },
          { "expr": "up{job='fastgpt'}", "legendFormat": "FastGPT" },
          { "expr": "up{job='dify'}", "legendFormat": "Dify" }
        ]
      },
      {
        "title": "API 请求量",
        "type": "graph",
        "targets": [
          { "expr": "rate(http_requests_total[5m])", "legendFormat": "{{service}}" }
        ]
      },
      {
        "title": "响应时间 P95",
        "type": "graph",
        "targets": [
          { "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))", "legendFormat": "{{service}}" }
        ]
      },
      {
        "title": "错误率",
        "type": "graph",
        "targets": [
          { "expr": "rate(http_requests_errors_total[5m]) / rate(http_requests_total[5m])", "legendFormat": "{{service}}" }
        ]
      }
    ]
  }
}
```

### 3.2 告警规则 (Prometheus AlertManager)

```yaml
groups:
  - name: three-platform-alerts
    rules:
      # N8N 告警
      - alert: N8NDown
        expr: up{job="n8n"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "N8N 服务不可用"
          description: "N8N 服务已停止运行超过 1 分钟"

      - alert: N8NHighFailureRate
        expr: rate(n8n_workflow_executions_failed_total[5m]) / rate(n8n_workflow_executions_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "N8N 工作流失败率过高"
          description: "工作流失败率超过 10%"

      # FastGPT 告警
      - alert: FastGPTDown
        expr: up{job="fastgpt"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "FastGPT 服务不可用"
          description: "FastGPT 服务已停止运行超过 1 分钟"

      - alert: FastGPTSlowResponse
        expr: histogram_quantile(0.95, rate(fastgpt_request_duration_seconds_bucket[5m])) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "FastGPT 响应时间过长"
          description: "P95 响应时间超过 10 秒"

      # Dify 告警
      - alert: DifyDown
        expr: up{job="dify"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Dify 服务不可用"
          description: "Dify 服务已停止运行超过 1 分钟"

      - alert: DifyWorkerQueueLong
        expr: dify_worker_queue_length > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Dify Worker 队列积压"
          description: "Worker 队列长度超过 100"
```

---

## 四、日志收集

### 4.1 ELK 配置

```yaml
# docker-compose.yml 中添加 Filebeat
filebeat:
  image: elastic/filebeat:8.11.0
  container_name: filebeat
  volumes:
    - ./filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
    - /var/lib/docker/containers:/var/lib/docker/containers:ro
  networks:
    - elastic
  depends_on:
    - elasticsearch
```

```yaml
# filebeat.yml
filebeat.inputs:
  - type: container
    paths:
      - /var/lib/docker/containers/n8n/*.log
    processors:
      - add_kubernetes_metadata:
          host: ${NODE_NAME}
          matchers:
            - logs_path:
                logs_path: "/var/lib/docker/containers/n8n/"
    fields:
      service: n8n

  - type: container
    paths:
      - /var/lib/docker/containers/fastgpt/*.log
    fields:
      service: fastgpt

  - type: container
    paths:
      - /var/lib/docker/containers/dify-api/*.log
    fields:
      service: dify-api

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "three-platform-%{+yyyy.MM.dd}"
```

### 4.2 日志分析命令

```bash
# N8N 错误日志
docker logs n8n 2>&1 | grep -E "ERROR|Exception|Failed" | tail -50

# FastGPT 检索日志
docker logs fastgpt 2>&1 | grep -E "search|retrieve" | tail -50

# Dify Worker 日志
docker compose logs worker 2>&1 | grep -E "error|timeout" | tail -50

# 聚合查看最近 1 小时错误
docker logs --since 1h n8n fastgpt dify-api 2>&1 | grep -i error | wc -l
```

---

## 五、故障排查手册

### 5.1 故障诊断流程

```
发现问题
    ↓
检查服务状态
    ↓
    ├── 容器运行 → 检查日志
    │                 ↓
    │           ┌─────┴─────┐
    │           ▼           ▼
    │        容器异常      API 异常
    │           │           │
    │           ▼           ▼
    │        资源检查    网络检查
    │           │           │
    │           └─────┬─────┘
    │                 ▼
    │            配置检查
    │
    └── 容器未运行 → 启动容器
                      ↓
                检查 Docker 状态
```

### 5.2 常见问题与解决方案

| 问题 | 平台 | 解决方案 |
|------|------|---------|
| 服务无法启动 | N8N | 检查 docker-compose.yml 和环境变量 |
| Webhook 不触发 | N8N | 检查抄送是否启用，检查网络连通性 |
| 知识库检索为空 | FastGPT | 检查向量数据库连接，确认已上传文档 |
| API 500 错误 | FastGPT | 检查 LLM API Key 是否正确，检查 API 限额 |
| Worker 不执行 | Dify | 检查 Worker 容器日志，确认 API 可用 |
| 响应超时 | Dify | 检查模型服务响应时间，增加超时配置 |

### 5.3 自动化恢复脚本

```bash
#!/bin/bash
# auto_recovery.sh - 自动恢复脚本

set -e

echo "[$(date)] 开始自动恢复检查..."

# 检查并重启 N8N
if ! curl -sf http://localhost:5678/healthz > /dev/null; then
    echo "[$(date)] N8N 不健康，正在重启..."
    docker compose -f /path/to/n8n/docker-compose.yml restart n8n
fi

# 检查并重启 FastGPT
if ! curl -sf http://localhost:3000/api/version > /dev/null; then
    echo "[$(date)] FastGPT 不健康，正在重启..."
    docker compose -f /path/to/fastgpt/docker-compose.yml restart fastgpt
fi

# 检查并重启 Dify
if ! curl -sf http://localhost:5001/health > /dev/null; then
    echo "[$(date)] Dify 不健康，正在重启..."
    docker compose -f /path/to/dify/docker-compose.yml restart api worker
fi

echo "[$(date)] 健康检查完成"
```

---

## 六、运维 SOP

### 6.1 日常检查清单

```yaml
每日检查:
  - [ ] 确认所有服务状态正常
  - [ ] 检查错误日志是否有新增错误
  - [ ] 确认 API 调用量在正常范围
  - [ ] 检查磁盘空间使用情况

每周检查:
  - [ ] 分析性能趋势
  - [ ] 检查资源使用率变化
  - [ ] 清理旧日志和临时文件
  - [ ] 备份重要数据

每月检查:
  - [ ] 更新系统和容器镜像
  - [ ] 安全补丁检查
  - [ ] 容量规划评估
  - [ ] 监控告警规则优化
```

### 6.2 备份策略

```yaml
备份计划:
  数据库:
    - 频率: 每日全量
    - 保留: 7天
    - 方式: docker exec pg_dump

  配置:
    - 频率: 变更时
    - 保留: 30天
    - 方式: git 版本控制

  工作流:
    - 频率: 每周
    - 保留: 30天
    - 方式: N8N API 导出

  日志:
    - 频率: 每日归档
    - 保留: 30天
    - 方式: ELK 索引管理
```

---

## 七、监控指标速查

### 7.1 N8N 关键指标

| 指标 | 查询方式 | 健康范围 |
|------|---------|---------|
| 服务状态 | `curl /healthz` | 返回 200 |
| 执行成功率 | API 统计 | >95% |
| 队列积压 | API 统计 | <100 |
| 响应时间 | 日志统计 | P95 < 5s |

### 7.2 FastGPT 关键指标

| 指标 | 查询方式 | 健康范围 |
|------|---------|---------|
| 服务状态 | `curl /api/version` | 返回版本号 |
| 知识库大小 | 数据库查询 | 预期范围内 |
| 检索命中率 | 日志统计 | >80% |
| 响应时间 | API 日志 | P95 < 10s |

### 7.3 Dify 关键指标

| 指标 | 查询方式 | 健康范围 |
|------|---------|---------|
| API 状态 | `curl /health` | 返回 200 |
| Worker 状态 | API 查询 | 运行中 |
| 队列长度 | API 查询 | <100 |
| 响应时间 | 日志统计 | P95 < 5s |

---

*本文档配套：[[n8n-deploy]] [[fastgpt-deploy]] [[dify-deploy]]*
