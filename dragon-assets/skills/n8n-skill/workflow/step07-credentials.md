# Step 07: 凭据配置

## 目标
使用 REST API 或手动方式配置工作流所需的凭据，并绑定到节点。

## 重要说明

⚠️ **MCP 限制**: n8n-mcp 当前不支持凭据管理，必须使用 REST API

## REST API 凭据管理

### 1. 扫描现有凭据

```bash
# 列出所有凭据
GET /api/credentials

# 响应示例
{
  "data": [
    {
      "id": "cred-1",
      "name": "Gmail account",
      "type": "gmailOAuth2"
    },
    {
      "id": "cred-2",
      "name": "Slack account",
      "type": "slackApi"
    }
  ]
}
```

### 2. 查询特定凭据

```bash
# 按类型查询
GET /api/credentials?type=gmailOAuth2

# 按名称查询
GET /api/credentials?name=Gmail%20account
```

### 3. 创建新凭据

```bash
# 创建凭据
POST /api/credentials

# 请求体
{
  "name": "Gmail account",
  "type": "gmailOAuth2",
  "data": {
    "clientId": "your-client-id",
    "clientSecret": "your-client-secret",
    "redirectUri": "https://your-n8n.com/rest/oauth2-credential/callback"
  }
}

# 响应
{
  "id": "cred-new",
  "name": "Gmail account",
  "type": "gmailOAuth2"
}
```

### 4. 绑定凭据到节点

更新 workflow.json 中的 credentials 引用：

```json
{
  "nodes": [
    {
      "id": "node-2",
      "name": "Gmail",
      "type": "n8n-nodes-base.gmail",
      "credentials": {
        "gmailOAuth2": {
          "id": "cred-1",
          "name": "Gmail account"
        }
      }
    }
  ]
}
```

## 常见凭据类型配置

### OAuth2 凭据

**适用**: Gmail, Google Sheets, Google Drive 等

```yaml
配置步骤:
  1. 在 Google Cloud Console 创建 OAuth 应用
  2. 获取 Client ID 和 Client Secret
  3. 在 n8n 中创建凭据
  4. 完成授权流程

API 创建:
  POST /api/credentials
  {
    "name": "Gmail account",
    "type": "gmailOAuth2",
    "data": {
      "clientId": "...",
      "clientSecret": "..."
    }
  }

授权:
  # 获取授权 URL
  GET /api/credentials/cred-1/oauth2-credential/auth-url

  # 用户访问授权 URL 并授权

  # 完成授权
  POST /api/credentials/cred-1/oauth2-credential/redirect
  {
    "code": "授权码"
  }
```

### API Key 凭据

**适用**: OpenAI, Slack, HTTP Request 等

```yaml
API 创建:
  POST /api/credentials
  {
    "name": "OpenAI API",
    "type": "openAiApi",
    "data": {
      "apiKey": "sk-..."
    }
  }

Slack Bot Token:
  POST /api/credentials
  {
    "name": "Slack Bot",
    "type": "slackApi",
    "data": {
      "accessToken": "xoxb-..."
    }
  }
```

### Basic Auth 凭据

```yaml
API 创建:
  POST /api/credentials
  {
    "name": "HTTP Basic Auth",
    "type": "httpBasicAuth",
    "data": {
      "user": "username",
      "password": "password"
    }
  }
```

### Header Auth 凭据

```yaml
API 创建:
  POST /api/credentials
  {
    "name": "API Header Auth",
    "type": "httpHeaderAuth",
    "data": {
      "name": "Authorization",
      "value": "Bearer token123"
    }
  }
```

## 凭据配置流程

### Step 1: 识别凭据需求

从 design.md 提取凭据需求：

```yaml
节点凭据映射:
  Gmail:
    类型: gmailOAuth2
    作用域: https://www.googleapis.com/auth/gmail.readonly

  Slack:
    类型: slackApi
    需要: botToken

  OpenAI:
    类型: openAiApi
    需要: apiKey
```

### Step 2: 检查现有凭据

```javascript
// 伪代码
const existingCreds = await GET('/api/credentials');
const neededTypes = ['gmailOAuth2', 'slackApi', 'openAiApi'];

const available = {};
const missing = [];

for (const type of neededTypes) {
  const found = existingCreds.data.find(c => c.type === type);
  if (found) {
    available[type] = found;
  } else {
    missing.push(type);
  }
}

console.log('可用凭据:', available);
console.log('缺失凭据:', missing);
```

### Step 3: 创建缺失凭据

对于每个缺失的凭据类型：

```markdown
## 需要创建: Gmail OAuth2

**创建步骤**:
1. 访问 https://console.cloud.google.com/
2. 创建项目或选择现有项目
3. 启用 Gmail API
4. 创建 OAuth 2.0 客户端 ID
5. 配置重定向 URI: `https://your-n8n.com/rest/oauth2-credential/callback`
6. 复制 Client ID 和 Client Secret

**在 n8n 中创建**:
方式1: UI 创建
- 进入 Settings → Credentials
- 点击 "Add Credential"
- 选择 "Gmail OAuth2 API"
- 填入 Client ID 和 Client Secret

方式2: API 创建
```bash
POST /api/credentials
{
  "name": "Gmail account",
  "type": "gmailOAuth2",
  "data": {
    "clientId": "your-client-id",
    "clientSecret": "your-client-secret"
  }
}
```

完成 OAuth 授权:
```bash
# 获取授权 URL
GET /api/credentials/{cred-id}/oauth2-credential/auth-url

# 访问返回的 URL 并授权

# 完成授权
POST /api/credentials/{cred-id}/oauth2-credential/redirect
{
  "code": "授权码"
}
```
```

### Step 4: 绑定凭据到工作流

更新 workflow.json：

```javascript
// 更新节点凭据引用
const workflow = loadWorkflowJson();

for (const node of workflow.nodes) {
  const credType = getCredentialType(node.type);
  if (credType && available[credType]) {
    node.credentials = {
      [credType]: {
        id: available[credType].id,
        name: available[credType].name
      }
    };
  }
}

saveWorkflowJson(workflow);
```

## 输出格式

### credentials-report.md

```markdown
# 凭据配置报告

## 凭据需求分析

### 所需凭据
| 节点 | 凭据类型 | 用途 | 状态 |
|------|----------|------|------|
| Gmail | gmailOAuth2 | 读取邮件 | ✅ 已配置 |
| Slack | slackApi | 发送消息 | ✅ 已配置 |
| OpenAI | openAiApi | AI 分析 | ❌ 需要配置 |

## 现有凭据

### Gmail account
- **ID**: cred-1
- **类型**: gmailOAuth2
- **状态**: ✅ 已授权
- **作用域**:
  - https://www.googleapis.com/auth/gmail.readonly

### Slack Bot
- **ID**: cred-2
- **类型**: slackApi
- **状态**: ✅ 可用
- **权限**: chat:write, channels:read

## 待创建凭据

### OpenAI API
- **类型**: openAiApi
- **获取方式**: https://platform.openai.com/api-keys
- **配置步骤**:
  1. 登录 OpenAI Platform
  2. 创建 API Key
  3. 在 n8n 中创建凭据

## 工作流凭据绑定

```json
{
  "nodes": [
    {
      "name": "Gmail",
      "credentials": {
        "gmailOAuth2": {
          "id": "cred-1",
          "name": "Gmail account"
        }
      }
    },
    {
      "name": "Slack",
      "credentials": {
        "slackApi": {
          "id": "cred-2",
          "name": "Slack Bot"
        }
      }
    }
  ]
}
```

## 安全提示

⚠️ **重要安全注意事项**:
1. 不要在工作流 JSON 中硬编码 API 密钥
2. 使用 n8n 的凭据管理系统
3. 定期轮换敏感凭据
4. 限制 API 密钥的权限范围
5. 启用 n8n 的加密功能

## 下一步
- [ ] 创建缺失的凭据
- [ ] 完成授权流程
- [ ] 验证凭据绑定
- [ ] 进入 Step 08: 验证
```

## 验证条件

- [ ] 所需凭据已识别
- [ ] 现有凭据已查询
- [ ] 缺失凭据已创建
- [ ] OAuth 授权已完成
- [ ] 凭据已绑定到工作流
- [ ] credentials-report.md 已生成

## 错误处理

| 错误 | 处理 |
|------|------|
| 凭据已存在 | 查询并复用现有凭据 |
| OAuth 授权失败 | 检查 Client ID/Secret 和重定向 URI |
| API Key 无效 | 验证密钥格式和权限 |
| 凭据绑定失败 | 检查凭据类型匹配 |

## 安全最佳实践

1. **最小权限原则**: 只授予必要的权限范围
2. **凭据轮换**: 定期更新 API 密钥
3. **环境变量**: 敏感信息使用环境变量
4. **审计日志**: 记录凭据使用情况
5. **加密存储**: 确保 n8n 使用加密存储

## 下一步

Step 08: 验证修复 - 最多10轮验证循环确保工作流正确
