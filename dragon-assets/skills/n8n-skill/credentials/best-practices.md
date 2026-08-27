# 凭据管理最佳实践

## 概述

本文档提供 n8n 凭据管理的安全最佳实践指南。

## 核心原则

### 1. 最小权限原则

始终为凭据分配完成工作所需的最低权限。

**示例**:
```javascript
// ✅ 好的做法：只请求读取权限
scopes: ['read:user', 'read:repo']

// ❌ 不好的做法：请求完全访问权限
scopes: ['repo', 'user', 'admin:org', 'workflow']
```

### 2. 环境隔离

为不同环境使用不同的凭据。

| 环境 | 凭据 | 用途 |
|------|------|------|
| Development | Test keys | 开发和测试 |
| Staging | Staging keys | 预生产验证 |
| Production | Production keys | 生产流量 |

### 3. 凭据轮换

定期轮换凭据以减少安全风险。

| 凭据类型 | 轮换周期 | 轮换方法 |
|----------|----------|----------|
| API Keys | 90 天 | 生成新密钥并更新配置 |
| OAuth Tokens | 根据提供商标准 | 使用 refresh token |
| 数据库密码 | 180 天 | 更新密码并重启服务 |

### 4. 审计与监控

- 记录所有凭据使用情况
- 监控异常访问模式
- 设置过期警报

## 安全配置

### 加密存储

n8n 默认使用 AES-256-GCM 加密存储凭据。

**配置**:
```json
{
  "encryptionKey": "your-32-character-encryption-key"
}
```

**生成加密密钥**:
```bash
# Linux/macOS
openssl rand -hex 32

# Windows PowerShell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})
```

### 访问控制

**环境变量**:
```bash
# .env 文件（不提交到版本控制）
N8N_ENCRYPTION_KEY=your-encryption-key
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=your-password
```

**n8n 用户权限**:
- 只授予必要的管理员权限
- 使用团队/组织功能隔离访问
- 定期审查用户访问权限

## 凭据类型选择指南

### 选择合适的凭据类型

| 场景 | 推荐类型 | 理由 |
|------|----------|------|
| 第三方 API (OAuth2) | OAuth2 | 标准化、安全、自动刷新 |
| 内部 API | API Key Header | 简单、无状态 |
| 数据库连接 | 专用凭据类型 | 预配置、连接池 |
| Webhook | Webhook 凭据 | 验证签名 |
| 自定义认证 | HTTP Header Auth | 灵活配置 |

### 凭据命名规范

使用描述性命名便于管理：

```
Production-OpenAI-API-Key
Staging-SendGrid-SMTP
Dev-Database-PostgreSQL-Primary
GitHub-OAuth-User-Repos
```

## 常见安全问题

### 1. 硬编码凭据

**问题**: 在代码或工作流中硬编码 API 密钥。

**解决方案**:
```javascript
// ❌ 错误做法
const apiKey = 'sk_live_abc123...';

// ✅ 正确做法
const apiKey = $env.OPENAI_API_KEY;
// 或使用 n8n 凭据系统
```

### 2. 凭据泄露到日志

**问题**: 敏感信息被记录到日志文件。

**解决方案**:
- 在 n8n 设置中禁用敏感日志记录
- 使用日志过滤工具
- 定期清理日志文件

### 3. 共享凭据

**问题**: 多个服务使用同一凭据。

**解决方案**:
- 为每个服务/环境创建独立凭据
- 使用凭据轮换策略
- 实施访问审计

### 4. 弱密码

**问题**: 使用容易猜测的密码。

**解决方案**:
- 使用强密码生成器
- 最小长度 16 字符
- 包含大小写字母、数字、特殊字符

## 故障排除

### 凭据过期

**症状**: 工作流执行失败，显示认证错误。

**解决方案**:
1. 检查凭据过期时间
2. 更新或重新生成凭据
3. 测试连接后重新部署

### OAuth Token 失效

**症状**: API 返回 401 Unauthorized。

**解决方案**:
1. 使用 refresh token 更新 access token
2. 或重新进行 OAuth 授权流程
3. 检查 scopes 是否正确

### 连接超时

**症状**: 凭据验证失败或超时。

**解决方案**:
1. 检查网络连接
2. 验证 API 端点 URL
3. 增加 timeout 设置
4. 检查防火墙规则

## 合规性考虑

### GDPR（通用数据保护条例）

- 加密存储所有凭据
- 记录凭据访问日志
- 支持用户数据导出
- 提供凭据删除功能

### SOC 2

- 实施访问控制
- 定期安全审计
- 变更管理流程
- 事件响应计划

### HIPAA（医疗数据）

- 端到端加密
- 访问审计追踪
- 最小权限原则
- 定期风险评估

## 管理工具

### 凭据审计脚本

```javascript
// 检查即将过期的凭据
async function auditCredentials() {
  const credentials = await list_credentials();
  const warnings = [];
  const now = Date.now();
  const thirtyDays = 30 * 24 * 60 * 60 * 1000;

  for (const cred of credentials.credentials) {
    // 检查凭据年龄
    if (cred.createdAt) {
      const age = now - new Date(cred.createdAt).getTime();
      if (age > thirtyDays * 6) { // 6个月
        warnings.push({
          id: cred.id,
          name: cred.name,
          issue: 'Old credential',
          recommendation: 'Consider rotating'
        });
      }
    }

    // 检查是否使用默认名称
    if (cred.name.startsWith('New')) {
      warnings.push({
        id: cred.id,
        name: cred.name,
        issue: 'Default name',
        recommendation: 'Rename to something descriptive'
      });
    }
  }

  return warnings;
}
```

### 批量更新脚本

```javascript
// 批量更新使用特定凭据的工作流
async function updateWorkflowsUsingCredential(credentialId) {
  const workflows = await list_workflows();

  const affected = [];
  for (const workflow of workflows.workflows) {
    const usesCredential = JSON.stringify(workflow)
      .includes(credentialId);

    if (usesCredential) {
      affected.push({
        id: workflow.id,
        name: workflow.name
      });
    }
  }

  return affected;
}
```

## 相关文档

- [OAuth2 认证](oauth2-api.md)
- [常用 API 配置](common-apis.md)
- [n8n 安全文档](https://docs.n8n.io/security/)
