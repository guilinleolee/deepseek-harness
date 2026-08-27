# 常用 API 凭据配置指南

## 概述

本指南提供常用 SaaS API 的 n8n 凭据配置说明。

## AI/ML 服务

### OpenAI

**认证方式**: API Key

**获取步骤**:
1. 访问 [OpenAI Platform](https://platform.openai.com/)
2. API Keys → Create new secret key
3. 复制并安全保存密钥

**n8n 配置**:
```
Credential Type: OpenAI API
API Key: sk-proj-...
Organization ID: (可选)
Base URL: https://api.openai.com/v1 (或自定义端点)
```

**节点**:
- OpenAI Model
- OpenAI Chat Model
- OpenAI Image

### Anthropic Claude

**认证方式**: API Key

**获取步骤**:
1. 访问 [Anthropic Console](https://console.anthropic.com/)
2. API Keys → Create Key
3. 记录密钥

**n8n 配置**:
```
Credential Type: HTTP Header Auth
Header Name: x-api-key
Header Value: sk-ant-...
```

**API 端点**: `https://api.anthropic.com/v1/messages`

### Hugging Face

**认证方式**: API Token

**获取步骤**:
1. 访问 [Hugging Face Settings](https://huggingface.co/settings/tokens)
2. 创建新 token
3. 选择权限类型

**n8n 配置**:
```
Credential Type: HTTP Header Auth
Header Name: Authorization
Header Value: Bearer hf_xxx...
```

## 通信服务

### SendGrid

**认证方式**: API Key

**获取步骤**:
1. 登录 [SendGrid](https://sendgrid.com/)
2. Settings → API Keys
3. Create API Key
4. 选择权限（Mail Send 推荐）

**n8n 配置**:
```
Credential Type: SendGrid API
API Key: SG.xxxxx...
```

**常用 API**: `https://api.sendgrid.com/v3/mail/send`

### Twilio

**认证方式**: Account SID + Auth Token

**获取步骤**:
1. 登录 [Twilio Console](https://console.twilio.com/)
2. Settings → General Settings
3. 复制 Account SID 和 Auth Token

**n8n 配置**:
```
Credential Type: Twilio
Account SID: ACxxxxx...
Auth Token: your_auth_token
```

### Resend

**认证方式**: API Key

**获取步骤**:
1. 访问 [Resend Dashboard](https://resend.com/api-keys)
2. Create API Key
3. 选择权限

**n8n 配置**:
```
Credential Type: HTTP Header Auth
Header Name: Authorization
Header Value: Bearer re_xxxxx...
```

## 云存储

### AWS S3

**认证方式**: Access Key + Secret Key

**获取步骤**:
1. AWS IAM Console
2. Users → Create user
3. Attach "AmazonS3FullAccess" policy
4. Create access key

**n8n 配置**:
```
Credential Type: AWS
Access Key ID: AKIAIOSFODNN7EXAMPLE
Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
Region: us-east-1 (或你的区域)
```

### Google Cloud Storage

**认证方式**: Service Account Key

**获取步骤**:
1. GCP Console → IAM & Admin → Service Accounts
2. Create Service Account
3. Create Key → JSON
4. 下载 JSON 文件

**n8n 配置**:
```
Credential Type: Google Cloud
Service Account JSON: {粘贴 JSON 内容}
Project ID: your-project-id
```

### Azure Blob Storage

**认证方式**: Connection String 或 SAS Token

**获取步骤**:
1. Azure Portal → Storage Account
2. Access Keys → Copy connection string

**n8n 配置**:
```
Credential Type: Azure Blob Storage
Connection String: DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...
Container Name: your-container
```

## 数据库

### PostgreSQL

**n8n 配置**:
```
Credential Type: PostgreSQL
Host: localhost
Database: mydb
User: postgres
Password: your_password
Port: 5432
SSL: Disable (或 Require)
```

### MySQL

**n8n 配置**:
```
Credential Type: MySQL
Host: localhost
Database: mydb
User: root
Password: your_password
Port: 3306
SSL: false
```

### MongoDB

**n8n 配置**:
```
Credential Type: MongoDB
Connection String: mongodb://username:password@host:port/database
```

**示例**:
```
mongodb+srv://user:password@cluster.mongodb.net/mydb
```

### Redis

**n8n 配置**:
```
Credential Type: Redis
Host: localhost
Port: 6379
Database: 0
Password: (可选)
```

## CRM/营销

### Salesforce

**认证方式**: OAuth2

**获取步骤**:
1. Salesforce Setup → App Manager
2. New Connected App
3. Enable OAuth Settings
4. Callback URL: `https://your-n8n.com/rest/oauth2-credential/callback`

**n8n 配置**:
```
Credential Type: Salesforce OAuth2
Consumer Key: your_consumer_key
Consumer Secret: your_consumer_secret
Login URL: https://login.salesforce.com (或测试环境)
```

### HubSpot

**认证方式**: API Key 或 OAuth2

**API Key 方式**:
```
Credential Type: HTTP Header Auth
Header Name: Authorization
Header Value: Bearer your_api_key
```

**OAuth2 方式**:
```
Authorization URL: https://app.hubspot.com/oauth/authorize
Token URL: https://api.hubapi.com/oauth/v1/token
Scope: crm.objects.contacts.read crm.objects.contacts.write
```

### Stripe

**认证方式**: API Key

**获取步骤**:
1. Stripe Dashboard → Developers → API keys
2. 复制 Publishable key 和 Secret key

**n8n 配置**:
```
Credential Type: HTTP Header Auth
Header Name: Authorization
Header Value: Bearer sk_live_xxxxx... (或 sk_test_... 用于测试)
```

## 电商

### Shopify

**认证方式**: API Key + Password

**获取步骤**:
1. Shopify Admin → Apps → Manage private apps
2. Create private app
3. Enable Admin API
4. 复制 API Key 和 Password

**n8n 配置**:
```
Credential Type: HTTP Basic Auth
Username: your_api_key
Password: your_api_password
```

**API 端点**: `https://your-store.myshopify.com/admin/api/2024-01/`

### WooCommerce

**认证方式**: Consumer Key + Secret

**获取步骤**:
1. WooCommerce Settings → Advanced → REST API
2. Add Key
3. 选择 Read/Write 权限
4. 复制 Key 和 Secret

**n8n 配置**:
```
Credential Type: HTTP Header Auth
Header Name: Authorization
Header Value: Basic base64(consumer_key:consumer_secret)
```

## 项目管理

### Jira

**认证方式**: API Token 或 OAuth2

**API Token 方式**:
1. Atlassian Account Settings → Security → API tokens
2. Create API token
3. 复制 token

**n8n 配置**:
```
Credential Type: HTTP Basic Auth
Username: your_email@example.com
Password: your_api_token
```

**Base URL**: `https://your-domain.atlassian.net`

### Linear

**认证方式**: Personal API Key

**获取步骤**:
1. Linear Settings → API
2. Create Personal API Key
3. 复制密钥

**n8n 配置**:
```
Credential Type: HTTP Header Auth
Header Name: Authorization
Header Value: YOUR_API_KEY
```

**API 端点**: `https://api.linear.app/graphql`

### Notion

**认证方式**: Integration Token

**获取步骤**:
1. Notion → My Integrations
2. Create integration
3. 复制 Internal Integration Token
4. 在目标页面中添加集成

**n8n 配置**:
```
Credential Type: HTTP Header Auth
Header Name: Authorization
Header Value: Bearer secret_xxxxx...
```

## 监控与日志

### Datadog

**认证方式**: API Key + Application Key

**n8n 配置**:
```
Credential Type: HTTP Header Auth
Header Name: DD-API-KEY
Header Value: your_api_key
```

### Sentry

**认证方式**: DSN 或 Auth Token

**n8n 配置**:
```
Credential Type: HTTP Header Auth
Header Name: Authorization
Header Value: Bearer your_auth_token
```

## 安全建议

### 1. 环境变量

```bash
# .env 文件
OPENAI_API_KEY=sk-proj-xxx
SENDGRID_API_KEY=SG.xxx
TWILIO_ACCOUNT_SID=ACxxx
TWILIO_AUTH_TOKEN=xxx
```

### 2. 凭据加密

n8n 会自动加密存储在数据库中的凭据。

### 3. 审计与轮换

- 定期轮换 API 密钥
- 监控 API 使用情况
- 设置异常警报

## 相关文档

- [OAuth2 认证](oauth2-api.md)
- [API Key 认证](api-key-auth.md)
- [凭据最佳实践](credentials-best-practices.md)
