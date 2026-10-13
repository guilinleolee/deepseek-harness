# n8n-mcp 配置指南

## 概述

n8n-mcp 是一个 Model Context Protocol (MCP) 服务器，用于与 n8n 工作流自动化平台进行交互。本指南将帮助您安装和配置 n8n-mcp。

## 系统要求

- Node.js >= 18.x
- n8n 实例（自托管或云版本）
- Claude Code 桌面工具

## 安装步骤

### 步骤 1: 安装 n8n-mcp

```bash
# 全局安装
npm install -g @n8n/mcp-server

# 或使用 npx（推荐）
npx @n8n/mcp-server --version
```

### 步骤 2: 配置 Claude Code

编辑 Claude Code 配置文件：

**Windows**: `C:\Users\<username>\.claude\settings.json`
**macOS/Linux**: `~/.claude/settings.json`

```json
{
  "mcpServers": {
    "n8n": {
      "command": "n8n-mcp",
      "args": [],
      "env": {
        "N8N_URL": "http://localhost:5678",
        "N8N_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### 步骤 3: 配置 n8n 实例

#### 3.1 启用 API 访问

在 n8n 实例中启用 API 访问：

**环境变量方式**:
```bash
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your-password
N8N_HOST=localhost
N8N_PORT=5678
N8N_PROTOCOL=http
```

**Docker 方式**:
```bash
docker run -it --rm \
  -p 5678:5678 \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=your-password \
  -e N8N_HOST=localhost \
  -e N8N_PORT=5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

#### 3.2 生成 API Key

```bash
# 在 n8n UI 中
# 1. 进入 Settings → API
# 2. 创建新的 API Key
# 3. 复制 API Key
```

### 步骤 4: 验证连接

```bash
# 测试连接
n8n-mcp health-check

# 搜索节点测试
n8n-mcp search-nodes --query gmail

# 如果成功，应该返回节点列表
```

## 配置选项

### 基础配置

| 参数 | 说明 | 默认值 | 必需 |
|------|------|--------|------|
| `N8N_URL` | n8n 实例 URL | http://localhost:5678 | ✅ |
| `N8N_API_KEY` | API 认证密钥 | - | ✅ |
| `TIMEOUT` | 请求超时（毫秒） | 30000 | ❌ |

### 高级配置

```json
{
  "mcpServers": {
    "n8n": {
      "command": "n8n-mcp",
      "args": [
        "--url", "http://localhost:5678",
        "--timeout", "60000"
      ],
      "env": {
        "NODE_ENV": "production",
        "DEBUG": "n8n-mcp:*"
      }
    }
  }
}
```

## n8n 实例配置

### 自托管 n8n

#### 使用 npm

```bash
# 安装 n8n
npm install n8n -g

# 启动 n8n
n8n start
```

#### 使用 Docker

```bash
# 基础启动
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# 带环境变量
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -e N8N_ENCRYPTION_KEY=your-encryption-key \
  -e WEBHOOK_URL=https://your-domain.com \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

### n8n 云版本

如果您使用 n8n 云服务：

1. 获取云实例 URL
2. 生成 API Key
3. 更新配置：
```json
{
  "mcpServers": {
    "n8n-cloud": {
      "command": "n8n-mcp",
      "args": ["--url", "https://your-instance.n8n.cloud"],
      "env": {
        "N8N_API_KEY": "your-cloud-api-key"
      }
    }
  }
}
```

## 故障排除

### 问题1: 连接失败

**症状**: `Connection refused` 或 `ECONNREFUSED`

**解决方案**:
1. 确认 n8n 实例正在运行
2. 检查 URL 和端口配置
3. 验证防火墙设置

```bash
# 测试 n8n 可访问性
curl http://localhost:5678/healthz

# 应该返回 n8n 版本信息
```

### 问题2: 认证失败

**症状**: `401 Unauthorized` 或 `Invalid API Key`

**解决方案**:
1. 确认 API Key 正确
2. 检查基本认证配置
3. 验证用户权限

```bash
# 测试 API Key
curl -u admin:password http://localhost:5678/api/workflows
```

### 问题3: 工具不可用

**症状**: `Tool not found` 错误

**解决方案**:
1. 确认 n8n-mcp 已安装
2. 重启 Claude Code
3. 检查 MCP 服务器配置

```bash
# 检查 n8n-mcp 安装
npm list -g @n8n/mcp-server

# 重新安装
npm install -g @n8n/mcp-server
```

### 问题4: 超时错误

**症状**: 请求超时或无响应

**解决方案**:
1. 增加 timeout 配置
2. 检查网络连接
3. 验证 n8n 实例性能

```json
{
  "mcpServers": {
    "n8n": {
      "args": ["--timeout", "120000"]
    }
  }
}
```

## 安全最佳实践

### 1. 保护 API Key

- 不要在代码中硬编码 API Key
- 使用环境变量存储
- 定期轮换 API Key
- 使用最小权限原则

### 2. 网络安全

- 使用 HTTPS（生产环境）
- 配置防火墙规则
- 限制 API 访问来源
- 启用请求日志

### 3. 访问控制

```bash
# 在 n8n 中配置用户权限
# Settings → Users → 创建用户并分配角色
```

## 性能优化

### 1. 连接池配置

```json
{
  "mcpServers": {
    "n8n": {
      "env": {
        "MAX_CONNECTIONS": "10",
        "KEEP_ALIVE": "true"
      }
    }
  }
}
```

### 2. 缓存策略

```javascript
// 缓存节点信息
const nodeCache = new Map();
const CACHE_TTL = 3600000; // 1小时

async function getCachedNode(nodeType) {
  const cached = nodeCache.get(nodeType);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }

  const node = await get_node({ nodeType });
  nodeCache.set(nodeType, {
    data: node,
    timestamp: Date.now()
  });

  return node;
}
```

## 下一步

配置完成后，您可以：

1. 使用 [节点发现工具](../tools/node-discovery.md) 查找节点
2. 使用 [模板管理工具](../tools/template-management.md) 搜索模板
3. 使用 [工作流 CRUD](../tools/workflow-crud.md) 管理工作流
4. 开始构建您的第一个自动化工作流！

## 相关资源

- [n8n-mcp GitHub](https://github.com/n8n-io/n8n-mcp)
- [n8n 官方文档](https://docs.n8n.io)
- [MCP 规范](https://modelcontextprotocol.io)
