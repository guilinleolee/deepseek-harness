# Step 01: 需求获取

## 目标
将用户的一句话需求转化为结构化的工作流规格说明。

## 执行流程

### 1. 需求澄清（6问题集）

请向用户确认以下信息：

| 问题 | 目的 | 示例答案 |
|------|------|----------|
| **触发方式** | 什么启动工作流？ | "每天9点" / "收到邮件时" / "Webhook" |
| **数据源** | 数据从哪里来？ | "Gmail" / "Google Sheets" / "API" |
| **处理逻辑** | 需要做什么处理？ | "过滤垃圾邮件" / "提取摘要" / "AI分类" |
| **输出目标** | 结果送到哪里？ | "Slack通知" / "存入数据库" / "发送邮件" |
| **条件分支** | 有什么特殊条件？ | "如果重要邮件则立即通知" |
| **异常处理** | 出错了怎么办？ | "记录日志并重试3次" |

### 2. Keyword 标准化

将用户描述映射到 n8n 标准术语：

```yaml
触发器关键词:
  定时: "Schedule Trigger"
  邮件: "Email Trigger" / "Gmail Trigger"
  Webhook: "Webhook"
  手动: "Manual Trigger"

数据源关键词:
  Gmail: "@n8n/n8n-nodes-gmail"
  Sheets: "@n8n/n8n-nodes-google-sheets"
  Slack: "@n8n/n8n-nodes-slack"
  API: "HTTP Request"

操作关键词:
  过滤: "Filter"
  转换: "Set" / "Code"
  分支: "IF" / "Switch"
  AI: "AI Agent" / "OpenAI" / "Anthropic"
```

### 3. runs/ 目录初始化

```bash
# 为每次执行创建独立目录
runs/{timestamp}-{slug}/
├── requirements.md      # 本步骤输出
├── research.md          # Step 02 输出
├── discussion.md        # Step 03 输出
├── design.md            # Step 05 输出
├── workflow.json        # Step 06 输出
├── validation-report.md # Step 08 输出
├── deploy-report.md     # Step 09 输出
└── progress.json        # 进度追踪
```

## 输出格式

### requirements.md

```markdown
# 工作流需求规格

## 基本信息
- **工作流名称**: [name]
- **创建时间**: [timestamp]
- **运行目录**: [runs/xxx]

## 需求描述
[用户原始描述]

## 触发器设计
- **类型**: [Schedule/Webhook/Email/etc]
- **配置**: [cron表达式/监听地址/etc]

## 节点序列（初步）
1. [Trigger] → 2. [Action1] → 3. [Action2] → ... → N. [Output]

## 特殊需求
- [列出条件分支、错误处理、重试策略等]

## 关键词映射
- 用户词汇 → n8n标准术语
```

### progress.json

```json
{
  "workflow_id": "{timestamp}-{slug}",
  "current_step": 1,
  "completed_steps": [1],
  "status": "in_progress",
  "errors": [],
  "created_at": "2026-02-26T10:00:00Z",
  "updated_at": "2026-02-26T10:05:00Z"
}
```

## 验证条件

- [ ] 至少回答了 4 个核心问题（触发、数据源、处理、输出）
- [ ] runs/ 目录已创建
- [ ] requirements.md 已生成
- [ ] progress.json 已初始化

## 错误处理

| 错误 | 处理 |
|------|------|
| 用户描述模糊 | 使用示例引导用户明确需求 |
| 无法匹配触发器 | 列出常用触发器供选择 |
| runs/ 目录创建失败 | 检查权限，使用绝对路径 |
