---
license: UNKNOWN
name: api-design
description: REST API design patterns including resource naming, status codes, pagination, filtering, error responses, versioning, and rate limiting for production APIs. Use when designing API endpoints, reviewing contracts, implementing authentication, or planning versioning strategies.
github_repo: affaan-m/everything-claude-code
github_hash: 4e66b2882da9afb9747468b08a253ca2f09c85f3
last_updated: 2026-04-25
source_type: derived
origin: ECC (everything-claude-code)
triggers: ["api design", "API Design Patterns — API设计模式"]
---

# API Design Patterns — API设计模式

> 来源: [affaan-m/everything-claude-code/skills/api-design](https://github.com/affaan-m/everything-claude-code)

## 功能概述

REST API设计规范，覆盖资源命名、状态码、分页、过滤、错误处理、版本控制和速率限制。

## 何时使用

- 设计新的API端点
- 审查现有API契约
- 添加分页、过滤或排序
- 实现API错误处理
- 规划API版本策略
- 构建公开或合作伙伴API

## 核心概念

| 组件 | 说明 | 最佳实践 |
|------|------|---------|
| **资源URL** | 名词、复数、kebab-case | `/api/v1/users` |
| **HTTP方法** | GET/POST/PUT/PATCH/DELETE | 语义正确 |
| **状态码** | 2xx/4xx/5xx语义正确 | 不用200返回所有 |
| **错误格式** | code + message + details | 字段级错误 |
| **分页** | Cursor/Offset | 按场景选择 |
| **认证** | Bearer Token/API Key | Authorization头 |

## 资源设计模式

### URL结构

```
# 资源：名词、复数、小写、kebab-case
GET    /api/v1/users
GET    /api/v1/users/:id
POST   /api/v1/users
PUT    /api/v1/users/:id
PATCH  /api/v1/users/:id
DELETE /api/v1/users/:id

# 子资源表示关系
GET    /api/v1/users/:id/orders
POST   /api/v1/users/:id/orders

# 非CRUD操作（少用动词）
POST   /api/v1/orders/:id/cancel
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
```

### 命名规则

```
# ✅ GOOD
/api/v1/team-members              # kebab-case多词资源
/api/v1/orders?status=active       # 查询参数过滤
/api/v1/users/123/orders           # 嵌套资源表示所有权

# ❌ BAD
/api/v1/getUsers                  # URL中有动词
/api/v1/user                      # 单数（用复数）
/api/v1/team_members              # URL中snake_case
/api/v1/users/123/getOrders       # 嵌套资源中有动词
```

## HTTP方法与状态码

### 方法语义

| 方法 | 幂等 | 安全 | 用途 |
|------|------|------|------|
| GET | Yes | Yes | 获取资源 |
| POST | No | No | 创建资源、触发操作 |
| PUT | Yes | No | 完整替换资源 |
| PATCH | No* | No | 部分更新资源 |
| DELETE | Yes | No | 删除资源 |

### 状态码参考

```
# 成功
200 OK                    — GET, PUT, PATCH (带响应体)
201 Created               — POST (包含Location头)
204 No Content           — DELETE, PUT (无响应体)

# 客户端错误
400 Bad Request           — 验证失败、畸形JSON
401 Unauthorized          — 缺失或无效认证
403 Forbidden             — 已认证但无权限
404 Not Found            — 资源不存在
409 Conflict              — 重复条目、状态冲突
422 Unprocessable Entity  — 语义无效（合法JSON，坏数据）
429 Too Many Requests     — 速率限制

# 服务器错误
500 Internal Server Error — 意外失败（永不暴露细节）
502 Bad Gateway           — 上游服务失败
503 Service Unavailable    — 临时过载，包含Retry-After
```

## 响应格式

### 成功响应

```json
{
  "data": {
    "id": "abc-123",
    "email": "alice@example.com",
    "name": "Alice",
    "created_at": "2025-01-15T10:30:00Z"
  }
}
```

### 分页集合响应

```json
{
  "data": [
    { "id": "abc-123", "name": "Alice" },
    { "id": "def-456", "name": "Bob" }
  ],
  "meta": {
    "total": 142,
    "page": 1,
    "per_page": 20,
    "total_pages": 8
  },
  "links": {
    "self": "/api/v1/users?page=1&per_page=20",
    "next": "/api/v1/users?page=2&per_page=20",
    "last": "/api/v1/users?page=8&per_page=20"
  }
}
```

### 错误响应

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address",
        "code": "invalid_format"
      },
      {
        "field": "age",
        "message": "Must be between 0 and 150",
        "code": "out_of_range"
      }
    ]
  }
}
```

## 分页策略

### Offset分页（简单）

```
GET /api/v1/users?page=2&per_page=20
```

**适用**：管理后台、小数据集(<10K)、用户期望跳页

### Cursor分页（可扩展）

```
GET /api/v1/users?cursor=eyJpZCI6MTIzfQ&limit=20
```

```json
{
  "data": [...],
  "meta": {
    "has_next": true,
    "next_cursor": "eyJpZCI6MTQzfQ"
  }
}
```

**适用**：无限滚动、 feeds、大数据集、公开API

### 何时选择

| 场景 | 分页类型 |
|------|---------|
| 管理后台、小数据集(<10K) | Offset |
| 无限滚动、feeds、大数据集 | Cursor |
| 公开API | Cursor(默认)+Offset(可选) |
| 搜索结果 | Offset（用户期望页码） |

## 过滤、排序、搜索

### 过滤

```
# 简单相等
GET /api/v1/orders?status=active&customer_id=abc-123

# 比较操作符（括号表示法）
GET /api/v1/products?price[gte]=10&price[lte]=100

# 多值（逗号分隔）
GET /api/v1/products?category=electronics,clothing
```

### 排序

```
# 单字段（前缀-表示降序）
GET /api/v1/products?sort=-created_at

# 多字段（逗号分隔）
GET /api/v1/products?sort=-featured,price,-created_at
```

## 认证与授权

### Token认证

```
# Bearer Token
GET /api/v1/users
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

# API Key（服务端到服务端）
GET /api/v1/data
X-API-Key: sk_live_abc123
```

## 速率限制

### 头部

```
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000

# 超限时
HTTP/1.1 429 Too Many Requests
Retry-After: 60
```

### 速率限制分层

| 分层 | 限制 | 窗口 | 用途 |
|------|------|------|------|
| Anonymous | 30/min | Per IP | 公开端点 |
| Authenticated | 100/min | Per user | 标准API访问 |
| Premium | 1000/min | Per API key | 付费API计划 |
| Internal | 10000/min | Per service | 服务间调用 |

## 版本控制

### URL路径版本（推荐）

```
/api/v1/users
/api/v2/users
```

### 版本策略

```
1. 从/api/v1/开始——不到需要时不版本化
2. 最多维护2个活跃版本（当前+上一个）
3. 弃用时间线：
   - 公告弃用（公开API提前6个月）
   - 添加Sunset头
4. 非破坏性变更不需要新版本：
   - 添加新响应字段
   - 添加新的可选查询参数
   - 添加新端点
5. 破坏性变更需要新版本
```

## 天龙引擎集成

### 适用岗位

| 岗位 | 集成方式 | 增强能力 |
|------|---------|---------|
| **02架构师** | API架构设计 | REST规范 + 版本策略 |
| **03构建师** | API实现 | TypeScript/Python/Go实现模式 |
| **06审查师** | API契约审查 | 端点一致性 + 安全检查 |

### 天龙引擎增强

```
┌─────────────────────────────────────────────────────────────┐
│ 天龙引擎 API设计体系                                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   API设计流程:                                              │
│   ├── 02架构师 → REST资源设计 + 状态码                    │
│   ├── 03构建师 → Zod/Pydantic验证 + 实现                  │
│   └── 06审查师 → 契约审查 + 安全检查                      │
│                                                             │
│   协同技能:                                                 │
│   ├── /mcp-server-patterns  → MCP工具暴露                 │
│   ├── /backend-patterns     → 后端架构模式                 │
│   └── /graphql-schema       → GraphQL设计                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心命令

```bash
# API设计审查
[@架构师] 审查这个API设计是否符合REST规范
[@审查师] 检查API契约一致性

# API实现
[@构建师] 使用api-design实现这个用户管理API
[@构建师] 添加分页和过滤到订单端点

# 协同
[@架构师] 设计API版本策略，支持向后兼容
```

---

**版本**: V1.0 | **兼容性**: 天龙引擎 V8.68+ | **来源**: ECC
