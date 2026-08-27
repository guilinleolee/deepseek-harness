---
license: UNKNOWN
triggers: ["n8n workflow patterns", "n8n-workflow-patterns"]
---
# n8n-workflow-patterns

## L0: 一句话描述 (≤15字)
4,343个生产级工作流模板库

## L1: 使用场景 (50-100字)
当用户需要构建自动化工作流时（如客户投诉处理、数据同步、定时报告），匹配最相似的n8n工作流模板，自动适配天龙引擎参数并生成可导入的工作流JSON。

## L2: 详细文档

### 核心能力
- **4,343个生产级n8n工作流**按188个类别组织
- **365个应用集成**覆盖主流SaaS/数据库/DevOps工具
- **29,445个节点**提供丰富的自动化模式参考
- **100% n8n兼容**直接导入即用

### 分类目录（188个集成类别）

#### 触发器类 (Triggers)
| 类别 | 说明 |
|------|------|
| Webhook | HTTP触发的自动化 |
| Cron | 定时调度任务 |
| Form | 表单收集触发 |
| Schedule | 间隔执行 |
| Manual | 手动触发 |
| RSS Feed Read | RSS源触发 |

#### 通信与消息
| 类别 | 说明 |
|------|------|
| Slack | Slack消息/频道操作 |
| Telegram | 电报Bot消息 |
| Discord | Discord消息/Webhook |
| Email | Gmail/IMAP/SMTP邮件 |
| Twilio | SMS/WhatsApp |
| Microsoft Outlook | 邮件/日历 |

#### CRM与销售
| 类别 | 说明 |
|------|------|
| HubSpot | CRM自动化 |
| Salesforce | 销售自动化 |
| Jira | 项目跟踪 |
| Pipedrive | CRM管道 |
| Zoho CRM | 客户管理 |
| ActiveCampaign | 营销自动化 |

#### 数据库与存储
| 类别 | 说明 |
|------|------|
| PostgreSQL | 关系数据库 |
| MySQL | 关系数据库 |
| MongoDB | NoSQL数据库 |
| Supabase | Firebase替代 |
| Google Sheets | 在线表格 |
| AWS S3 | 云存储 |

#### 营销与表单
| 类别 | 说明 |
|------|------|
| Mailchimp | 邮件营销 |
| Typeform | 表单收集 |
| Facebook Lead Ads | 社交线索 |
| WooCommerce | 电商订单 |
| Shopify | 电商平台 |

#### AI与数据
| 类别 | 说明 |
|------|------|
| OpenAI | GPT/LLM调用 |
| Google Analytics | 数据分析 |
| Google BigQuery | 大数据 |
| PostHog | 产品分析 |

#### DevOps与开发
| 类别 | 说明 |
|------|------|
| GitHub | 代码/Issue管理 |
| GitLab | CI/CD触发 |
| HTTP Request | API调用 |
| Code | JS/Python脚本 |
| Netlify | 部署触发 |

### 使用命令

```bash
# 搜索工作流模板
n8n-search "客户投诉自动处理"
n8n-search "CRM数据同步" --category hubspot
n8n-search "定时报告生成" --trigger cron

# 查看分类
n8n-categories
n8n-category gmail
n8n-category slack --list

# 生成工作流
n8n-generate "用户注册欢迎流程" --output workflow.json

# 导入到n8n
n8n-import workflow.json
```

### 模式匹配示例

| 用户需求 | 匹配的n8n模式 | 输出 |
|---------|--------------|------|
| 客户投诉自动回复 | Telegram通知 + Email回复 + Jira建单 | 3节点工作流JSON |
| 每日数据报表 | Cron触发 → HTTP请求 → Email发送 | 4节点工作流JSON |
| 社交媒体监控 | Webhook → Filter → Discord通知 | 4节点工作流JSON |
| 数据库备份 | Cron → Code(Python) → AWS S3 | 5节点工作流JSON |

### 协同天龙岗位

| 天龙岗位 | n8n协同方式 |
|---------|-----------|
| 09-02编排协调师 | 工作流模板匹配与输出 |
| 35-01数字营销 | Mailchimp/Typeform自动化 |
| 47-03 IM运营师 | Slack/Telegram/Discord工作流 |
| 38-02销售管理 | HubSpot/Salesforce/Pipedrive自动化 |
| 19-01数据工程师 | 数据库工作流设计 |
| 08发布师 | GitHub Actions/DevOps工作流 |

### 模板文件结构

```json
{
  "name": "客户投诉自动处理",
  "description": "自动处理客户投诉的全流程",
  "category": "crm",
  "integration": ["telegram", "email", "jira"],
  "nodes": [
    {"type": "trigger", "name": "Webhook", "config": {...}},
    {"type": "action", "name": "Telegram", "config": {...}},
    {"type": "action", "name": "Jira", "config": {...}}
  ],
  "天龙适配": {
    "trigger_config": {"天龙参数映射": {...}},
    "action_configs": {"天龙配置覆盖": {...}}
  }
}
```

### 索引与搜索

```bash
# 构建本地索引
n8n-index build

# 快速搜索
n8n-search "关键词" --limit 10

# 高级过滤
n8n-search "邮件" --trigger cron --category automation --complexity simple
```

### 与其他技能的协同

```
用户需求 → 09-02编排协调师
  → n8n-workflow-patterns（匹配模板）
  → fastapi-best-practices（API工作流）
  → paperclip-ticket（工单系统）

输出: n8n可导入工作流JSON / Make.com场景 / Zapier Zaps
```

## 技术规格

- **模板总数**: 4,343个
- **分类数**: 188个集成类别
- **节点数**: 29,445个
- **兼容性**: n8n标准JSON格式
- **导入成功率**: 100%