# OAuth2 API 认证模板

## 概述

OAuth2 是最常用的 API 认证方式之一。本模板提供常见服务的 OAuth2 配置指南。

## OAuth2 流程类型

### 1. Authorization Code Flow（授权码模式）

适用于有用户交互的服务端应用。

**配置步骤**:
1. 在服务提供商处创建 OAuth 应用
2. 获取 Client ID 和 Client Secret
3. 配置回调 URL
4. 完成授权流程

**常见服务**:

| 服务 | Authorization URL | Token URL | Scopes |
|------|------------------|-----------|--------|
| Google | `https://accounts.google.com/o/oauth2/v2/auth` | `https://oauth2.googleapis.com/token` | `https://www.googleapis.com/auth/...` |
| GitHub | `https://github.com/login/oauth/authorize` | `https://github.com/login/oauth/access_token` | `repo,user` |
| Microsoft | `https://login.microsoftonline.com/common/oauth2/v2.0/authorize` | `https://login.microsoftonline.com/common/oauth2/v2.0/token` | `User.Read` |
| Slack | `https://slack.com/oauth/v2/authorize` | `https://slack.com/api/oauth.v2.access` | `chat:write,channels:read` |

### 2. Client Credentials Flow（客户端凭据模式）

适用于无用户交互的服务端到服务端通信。

**配置**:
```
Authentication: Client Credentials
Token URL: https://auth.example.com/oauth/token
Client ID: your_client_id
Client Secret: your_client_secret
Scope: api_read api_write
```

**使用场景**:
- 后台任务处理
- 系统集成
- 批量数据同步

### 3. API Key / Bearer Token

最简单的认证方式。

**配置**:
```
Authentication: Generic Credential Type
Header Name: Authorization
Header Value: Bearer YOUR_API_TOKEN
```

**常见服务**:
- OpenAI: `Authorization: Bearer sk-...`
- Stripe: `Authorization: Bearer sk_test_...`
- Twilio: `Authorization: Bearer AC...`

## 常见服务配置

### Google APIs

**OAuth2 凭据**:
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目或选择现有项目
3. 启用所需 API
4. 创建 OAuth 2.0 凭据

**Scopes**:
```
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/calendar
https://www.googleapis.com_auth/drive
```

**n8n 配置**:
```
Credential Type: OAuth2
Authorization URL: https://accounts.google.com/o/oauth2/v2/auth
Token URL: https://oauth2.googleapis.com/token
Scope: https://www.googleapis.com/auth/gmail.readonly
Client ID: your_client_id
Client Secret: your_client_secret
Redirect URL: https://your-n8n-instance.com/rest/oauth2-credential/callback
```

### GitHub

**Personal Access Token**:
1. 访问 GitHub Settings → Developer settings → Personal access tokens
2. 生成新 token
3. 选择所需权限

**OAuth App**:
1. 访问 Developer settings → OAuth Apps
2. 创建新 OAuth App
3. 记录 Client ID 和 Secret

**Scopes**:
```
repo - 完整仓库访问
user - 用户信息
read:org - 组织读取权限
```

### Slack

**Bot Token**:
1. 访问 [Slack API](https://api.slack.com/apps)
2. 创建新 App
3. 配置 OAuth Scopes
4. 安装到 Workspace

**常用 Scopes**:
```
chat:write - 发送消息
channels:read - 读取频道
files:write - 上传文件
users:read - 读取用户信息
```

**n8n 配置**:
```
Credential Type: OAuth2
Authorization URL: https://slack.com/oauth/v2/authorize
Token URL: https://slack.com/api/oauth.v2.access
Scope: chat:write,channels:read
Client ID: your_client_id
Client Secret: your_client_secret
```

### Microsoft Graph API

**Azure AD 配置**:
1. 访问 [Azure Portal](https://portal.azure.com/)
2. Azure Active Directory → App registrations
3. 创建新应用注册
4. 配置 API 权限
5. 创建客户端密钥

**常用 Scopes**:
```
User.Read - 读取用户信息
Mail.Read - 读取邮件
Calendars.ReadWrite - 日历读写
Files.Read.All - 读取文件
```

### Salesforce

**Connected App 配置**:
1. Setup → App Manager → New Connected App
2. 启用 OAuth Settings
3. 配置 Callback URL
4. 选择 OAuth Scopes

**Token URL**:
```
Sandbox: https://test.salesforce.com/services/oauth2/token
Production: https://login.salesforce.com/services/oauth2/token
```

## 安全最佳实践

### 1. 密钥存储

```javascript
// ✅ 好的做法：使用环境变量
const apiToken = $env.API_TOKEN;

// ❌ 不好的做法：硬编码
const apiToken = 'sk_live_abc123...';
```

### 2. 轮换策略

- 定期轮换 API 密钥（建议 90 天）
- 使用不同的密钥用于开发和生产
- 立即撤销泄露的密钥

### 3. 最小权限原则

```javascript
// ✅ 只请求必需的权限
scopes: ['read:user']

// ❌ 请求过多权限
scopes: ['repo', 'user', 'admin:org', 'workflow']
```

### 4. 审计日志

- 记录所有 API 调用
- 监控异常使用模式
- 设置警报通知

## 故障排除

### 常见错误

| 错误代码 | 描述 | 解决方案 |
|----------|------|----------|
| `invalid_client` | Client ID/Secret 错误 | 验证凭据是否正确 |
| `invalid_grant` | 授权码无效或过期 | 重新进行授权流程 |
| `access_denied` | 用户拒绝授权 | 检查请求的权限范围 |
| `redirect_uri_mismatch` | 回调 URL 不匹配 | 确认回调 URL 配置正确 |
| `invalid_scope` | 作用域无效 | 检查 scopes 参数 |

### Token 刷新

```javascript
// 使用 refresh token 获取新 access token
async function refreshAccessToken(refreshToken) {
  const response = await fetch('https://auth.example.com/oauth/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
      client_id: 'your_client_id',
      client_secret: 'your_client_secret'
    })
  });

  return await response.json();
}
```

## n8n 凭据配置

### 创建 OAuth2 凭据

1. 在 n8n 中，访问 Credentials → Add Credential
2. 选择 OAuth2 类型
3. 填写配置：
   - **Authorization URL**: OAuth 提供商的授权端点
   - **Token URL**: 获取 access token 的端点
   - **Scope**: 请求的权限范围
   - **Client ID**: 应用客户端 ID
   - **Client Secret**: 应用客户端密钥
   - **Authentication**: 认证方式（通常是 header 或 basic）

4. 点击 "Sign in with OAuth" 完成授权

### 使用凭据

在节点中配置：
```
Credential: 选择已创建的 OAuth2 凭据
Resource: 选择要访问的资源
Operation: 选择操作类型
```

## 相关文档

- [API Key 认证](api-key-auth.md)
- [Basic Auth 认证](basic-auth.md)
- [凭据最佳实践](credentials-best-practices.md)
- [n8n 凭据文档](https://docs.n8n.io/credentials/)
