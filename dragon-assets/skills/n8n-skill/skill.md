---
license: UNKNOWN
name: n8n
description: |
github_repo: n8n-io/n8n
github_hash: 9599fb9d5416e1c4aae43679484d717a789c165e
last_updated: 2026-04-25
source_type: derived
version: 2.0.0
author: Frank Chen
created: 2026-02-26
updated: 2026-02-26
category: documentation
triggers: ["n8n skill", "n8n Workflow Automation Skill Pack"]
---

# n8n Workflow Automation Skill Pack

## Overview

This skill helps with:
- **[NEW] 10-Step Workflow Builder**: End-to-end construction system from user requirements to deployed workflows
- Understanding n8n node functionality and usage
- Finding nodes suitable for specific tasks
- Learning common workflow patterns
- Getting node configuration examples
- Solving workflow design problems
- Integrating external community workflows (n8n.io, GitHub)
- GitHub Automation Upload Protocol (Workflow Synchronization)

This skill includes:
- **[NEW] 10-Step Workflow Construction System**: Requirements → Research → Discussion → Knowledge → Design → Build → Credentials → Validate → Deploy → Output
- Detailed information on **545+ built-in n8n nodes**
- **30+ popular community packages** for extended functionality
- **Workflow Patterns**: Core patterns (ETL, API Chaining, Batch Processing, etc.) + Orchestration patterns
- **Validation Rules**: Complete workflow validation framework
- **Error Catalog**: 10 error types with fix strategies
- Node configuration examples and best practices
- External Research Protocol for accessing real-time community assets
- GitHub Automation Upload Protocol for direct repository sync
- Node categorization and indexing for both built-in and community nodes

## Table of Contents

### Workflow Builder
- [10-Step Workflow Construction System](#10-step-workflow-construction-system)
- [Workflow Patterns](#workflow-patterns)
- [Validation & Error Handling](#validation--error-handling)

### Knowledge Base
- [How to Find Nodes](guides/how-to-find-nodes.md)
- [Usage Guide](guides/usage-guide.md)
- [External Research Protocol](#external-research-protocol)
- [GitHub Automation Upload Protocol](#github-automation-upload-protocol)
- [Template Library](#template-library)

### Reference
- [License and Attribution](#license-and-attribution)

---

# 10-Step Workflow Construction System

## System Architecture

```
User Requirement (一句话)
    ↓
┌─────────────────────────────────────────────────────────────┐
│                    10-Step Construction Pipeline              │
├─────────────────────────────────────────────────────────────┤
│ 1. Requirements (需求获取)    → requirements.md              │
│ 2. Research (互联网检索)      → research.md                  │
│ 3. Discussion (方案讨论)      → discussion.md                │
│ 4. Knowledge (知识库查询)     → knowledge.md                 │
│ 5. Design (架构设计)         → design.md                    │
│ 6. Build (工作流构建)        → workflow.json                │
│ 7. Credentials (凭据配置)    → credentials-report.md         │
│ 8. Validate (验证修复)       → validation-report.md         │
│ 9. Deploy (部署激活)         → deploy-report.md             │
│ 10. Output (输出导出)        → workflow-export.json + summary.md │
└─────────────────────────────────────────────────────────────┘
    ↓
Active n8n Workflow + Complete Documentation
```

## Quick Start

**To start building a workflow:**

```
User: "帮我构建一个 n8n 工作流，每天早上9点获取 Gmail 重要邮件，生成摘要并发送到 Slack"

Assistant: [Starts Step 01: Requirements Gathering]
```

## Step Guide Files

Each step has a detailed instruction file:

- [Step 01: Requirements](workflow/step01-requirements.md) - 6问题集 + Keyword 标准化
- [Step 02: Research](workflow/step02-research.md) - 3轮搜索 + 模板对比
- [Step 03: Discussion](workflow/step03-discuss.md) - 3轮调整 + 方案确认
- [Step 04: Knowledge](workflow/step04-knowledge.md) - 三层知识架构
- [Step 05: Design](workflow/step05-design.md) - 节点清单 + 拓扑 + 表达式
- [Step 06: Build](workflow/step06-build.md) - 工作流构建 + 社区节点
- [Step 07: Credentials](workflow/step07-credentials.md) - 凭据配置
- [Step 08: Validate](workflow/step08-validate.md) - 10轮验证循环
- [Step 09: Deploy](workflow/step09-deploy.md) - 部署激活
- [Step 10: Output](workflow/step10-output.md) - 导出 + 报告

## Workflow Patterns

### Core Patterns
- [ETL Pattern](patterns/core-patterns.md#1-etl模式-extract-transform-load)
- [API Chaining Pattern](patterns/core-patterns.md#2-api-链式调用模式)
- [Batch Processing Pattern](patterns/core-patterns.md#3-批处理模式)
- [Fan-out Fan-in Pattern](patterns/core-patterns.md#4-扇出-扇入模式-fan-out-fan-in)
- [Error Branching Pattern](patterns/core-patterns.md#5-错误分支模式)
- [State Machine Pattern](patterns/core-patterns.md#6-状态机模式)
- [Event-Driven Pattern](patterns/core-patterns.md#7-事件驱动模式)

### Orchestration Patterns
- [Sequential](patterns/orchestration-patterns.md#1-顺序编排-sequential)
- [Conditional](patterns/orchestration-patterns.md#2-条件分支-conditional)
- [Parallel](patterns/orchestration-patterns.md#3-并行分支-parallel)
- [Loop](patterns/orchestration-patterns.md#4-循环处理-loop)
- [Aggregation](patterns/orchestration-patterns.md#5-聚合模式-aggregation)
- [Error Handling](patterns/orchestration-patterns.md#6-错误处理模式-error-handling)
- [Compensation](patterns/orchestration-patterns.md#7-补偿模式-compensating)
- [Throttling](patterns/orchestration-patterns.md#9-节流模式-throttling)
- [Caching](patterns/orchestration-patterns.md#10-缓存模式-caching)

## Validation & Error Handling

### Validation Rules
- [Node-level Validation](rules/validation-rules.md#节点级验证)
- [Connection Validation](rules/validation-rules.md#连接级验证)
- [Workflow-level Validation](rules/validation-rules.md#工作流级验证)
- [Expression Validation](rules/validation-rules.md#表达式验证)
- [Credential Validation](rules/validation-rules.md#凭据验证)
- [Performance Validation](rules/validation-rules.md#性能验证)
- [Security Validation](rules/validation-rules.md#安全验证)

### Error Catalog
- [Authentication Errors](rules/error-catalog.md#1-认证错误-authentication-errors)
- [Rate Limit Errors](rules/error-catalog.md#2-限流错误-rate-limit-errors)
- [Timeout Errors](rules/error-catalog.md#3-超时错误-timeout-errors)
- [Data Format Errors](rules/error-catalog.md#4-数据格式错误-data-format-errors)
- [Node Connection Errors](rules/error-catalog.md#5-节点连接错误-node-connection-errors)
- [Memory Errors](rules/error-catalog.md#6-内存错误-memory-errors)
- [Webhook Errors](rules/error-catalog.md#7-webhook-错误-webhook-errors)
- [Expression Errors](rules/error-catalog.md#8-表达式错误-expression-errors)
- [Community Node Errors](rules/error-catalog.md#9-社区节点错误-community-node-errors)
- [Debugging Tips](rules/error-catalog.md#10-调试技巧-debugging-tips)

## Expression Syntax

- [Basic Syntax](specs/expression-syntax.md#基本语法)
- [Expression Types](specs/expression-syntax.md#表达式类型)
- [Built-in Functions](specs/expression-syntax.md#内置函数)
- [Common Errors](specs/expression-syntax.md#常见错误)
- [Performance Tips](specs/expression-syntax.md#性能建议)

---

# Common Workflow Patterns

# External Research Protocol
... (existing protocol content) ...

# GitHub Automation Upload Protocol

To ensure consistent workflow versioning and backup:
1. **Repository Structure**: Store workflows in `workflows/` directory as `.json` files.
2. **Commit Convention**: Use `feat(workflow): add [Name] workflow` for new uploads.
3. **Automated Sync**:
   - Use `gh` CLI to check for existing repository.
   - If not exists, create via `gh repo create n8n`.
   - Perform `git push` to synchronize local modifications with GitHub.
4. **Validation**: Before pushing, ensure sensitive credentials (API Keys, Webhook Secrets) are replaced with placeholders or referenced via n8n expressions.

# Common Workflow Patterns

Here are some common workflow patterns you can use as a starting point:

## 1. HTTP Data Fetching

Fetch data from APIs and process it

Nodes used:
- HTTP Request
- Set
- IF

Example: Use HTTP Request node to fetch data from external APIs, Set node to transform formats, and IF node for conditional logic

## 2. Email Automation

Monitor emails and auto-respond or forward

Nodes used:
- Email Trigger (IMAP)
- Gmail
- IF

Example: Use Email Trigger to monitor inbox, IF node to filter specific conditions, and Gmail node to auto-reply or forward

## 3. Database Synchronization

Sync data between different systems

Nodes used:
- Schedule Trigger
- HTTP Request
- Postgres
- MySQL

Example: Scheduled trigger to read data from one database, transform it, and write to another database

## 4. Webhook Processing

Receive external webhooks and trigger actions

Nodes used:
- Webhook
- Set
- HTTP Request
- Slack

Example: Receive webhook events, process data, and send notifications to Slack or other systems

## 5. AI Assistant Integration

Use AI models to process and generate content

Nodes used:
- AI Agent
- OpenAI
- Vector Store
- Embeddings OpenAI

Example: Build AI assistants to handle user queries, integrate vector databases for semantic search

## 6. File Processing

Automatically process and transform files

Nodes used:
- Google Drive Trigger
- Extract from File
- Move Binary Data
- Dropbox

Example: Monitor Google Drive for new files, extract and process content, then upload to Dropbox

## Complete Template Library

We have collected 20 popular workflow templates from n8n.io, categorized by use case:

- [AI & Chatbots](resources/templates/ai-chatbots/README.md) - AI Agents, RAG systems, intelligent conversations
- [Social Media & Video](resources/templates/social-media/README.md) - TikTok, Instagram, YouTube automation
- [Data Processing & Analysis](resources/templates/data-processing/README.md) - Google Sheets, database integration
- [Communication & Collaboration](resources/templates/communication/README.md) - Email, WhatsApp, Telegram automation

See the [complete template index](resources/templates/README.md) for all available templates.


---

# License and Attribution

## This Skill Pack License

This skill pack project is licensed under the MIT License.
See: https://github.com/haunchen/n8n-skills/blob/main/LICENSE

## Important Notice

This is an unofficial educational project and is not affiliated with n8n GmbH.

This skill content is generated based on the following resources:
- n8n node type definitions (Sustainable Use License)
- n8n official documentation (MIT License)
- n8n-mcp project architecture (MIT License)

For detailed attribution information, please refer to the ATTRIBUTIONS.md file in the project.

## About n8n

n8n is an open-source workflow automation platform developed and maintained by n8n GmbH.

- Official website: https://n8n.io
- Documentation: https://docs.n8n.io
- Source code: https://github.com/n8n-io/n8n
- License: Sustainable Use License

When using n8n software, you must comply with n8n's license terms. See: https://github.com/n8n-io/n8n/blob/master/LICENSE.md