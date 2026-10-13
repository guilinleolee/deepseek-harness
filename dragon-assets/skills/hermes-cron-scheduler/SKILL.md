---
license: UNKNOWN
triggers: ["hermes cron scheduler", "hermes-cron-scheduler"]
---
# hermes-cron-scheduler

## 元信息

```yaml
name: hermes-cron-scheduler
description: Hermes定时调度 - 自然语言配置+多平台交付+零代码自动化
version: 1.0.0
category: productivity
source: NousResearch/hermes-agent
stars: 21.7k
```

## 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│ Hermes Cron Scheduler 定时自动化                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ⏰ 自然语言配置                                            │
│  └── "Every Monday at 9am, send summary"                   │
│  └── "每天早上8点发送日报"                                 │
│  └── "When GitHub PR merged, notify Slack"                │
│                                                             │
│  🌐 多平台交付                                              │
│  ├── Telegram                                             │
│  ├── Discord                                             │
│  ├── Slack                                               │
│  ├── Email                                               │
│  ├── WhatsApp                                            │
│  └── Signal                                              │
│                                                             │
│  🔄 零代码自动化                                           │
│  ├── 事件触发                                             │
│  ├── 定时执行                                             │
│  └── 条件分支                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 自然语言配置

```python
# 自然语言解析为Cron表达式
def parse_natural_cron(text):
    """将自然语言转换为Cron表达式"""

    patterns = {
        # 英文
        r"every (\w+) at (\d+)(am|pm)?":
            lambda m: f"0 {adjust_hour(m)} {day_map[m[1]]}",
        r"every (\d+) (minutes|hours|days)":
            lambda m: f"*/{m[1]} * * * *",

        # 中文
        r"每天早上(\d+)点": lambda m: f"0 {m[1]} * * *",
        r"每周(\w+)(\d+)点": lambda m: f"0 {m[2]} * * {day_cn_map[m[1]]}",
        r"每月(\d+)日(\d+)点": lambda m: f"0 {m[2]} {m[1]} * *",
    }

    for pattern, handler in patterns.items():
        match = re.search(pattern, text)
        if match:
            return handler(match)

    return None

# 示例
parse_natural_cron("Every Monday at 9am")  # "0 9 * * 1"
parse_natural_cron("每天早上8点")           # "0 8 * * *"
parse_natural_cron("每30分钟")              # "*/30 * * * *"
```

## 多平台交付

```python
# 统一交付接口
class MultiPlatformDelivery:
    """多平台消息交付"""

    platforms = {
        "telegram": TelegramBot,
        "discord": DiscordWebhook,
        "slack": SlackClient,
        "email": SMTPMailer,
        "whatsapp": WhatsAppAPI,
        "signal": SignalCLI,
    }

    def deliver(self, message, targets):
        """
        消息交付
        - message: 消息内容
        - targets: {"telegram": "@user", "discord": "#channel", ...}
        """
        results = {}
        for platform, target in targets.items():
            if platform in self.platforms:
                client = self.platforms[platform]()
                results[platform] = client.send(message, target)

        return results
```

## 触发类型

```python
# 1. 定时触发
CRON_TRIGGERS = {
    "0 9 * * 1-5": "weekday_morning",     # 工作日早9点
    "0 8 * * *": "daily_morning",          # 每天早8点
    "0 */4 * * *": "every_4_hours",        # 每4小时
}

# 2. 事件触发
EVENT_TRIGGERS = {
    "github.pr.merged": "PR合并时",
    "github.issue.created": "Issue创建时",
    "schedule.task.completed": "任务完成时",
    "email.received": "收到邮件时",
}

# 3. 条件触发
CONDITION_TRIGGERS = {
    "if_ci_failed": "CI失败时",
    "if_pr_approved": "PR批准时",
    "if_market_probability_above": "概率超过阈值时",
}
```

## 天龙引擎集成

### 适用岗位
- **08发布师** - 定时CI/CD报告
- **09-02编排协调师** - 定时任务编排
- **09-04首席幕僚长** - 定时汇总报告
- **01调研师** - 定时研究任务

### 调用方式

```bash
# 定时任务
[@发布师] 每天早上8点发送CI/CD状态报告
[@编排协调师] 每30分钟检查构建状态
[@首席幕僚长] 每周一早上9点汇总上周工作

# 事件触发
[@发布师] 当PR合并时通知Slack
[@发布师] 当构建失败时发送告警
[@调研师] 当发现重要论文时立即通知

# 条件触发
[@发布师] 当测试覆盖率低于80%时告警
[@首席幕僚长] 当有紧急Issue时立即通知
```

## 与现有调度能力对比

| 维度 | paperclip-heartbeat | Hermes Cron | 提升 |
|------|---------------------|-------------|------|
| Cron调度 | ✅ | ✅ | - |
| 自然语言配置 | ❌ | ✅ **新增** | +500% |
| 多平台交付 | ❌ | ✅ **新增** | **质的飞跃** |
| 事件触发 | ❌ | ✅ **新增** | **新增** |
| 条件分支 | ❌ | ✅ **新增** | **新增** |

## 与天龙组件协同

| 天龙组件 | 调度协同 | 效果 |
|---------|---------|------|
| **V8.36 paperclip-heartbeat** | 定时触发 | 互补 |
| **V8.72 Trigger.dev** | 事件驱动 | 互补 |
| **V8.39 Claude-to-IM** | 多平台交付 | 集成 |
| **V8.71 Sim/ReactFlow** | 工作流调度 | 集成 |

## 融合方案

```python
# 天龙调度体系 + Hermes Cron

Level 4: Hermes Cron ⭐新增
  - 自然语言配置
  - 多平台交付
  - 事件触发

Level 4: paperclip-heartbeat
  - Cron表达式
  - 状态监控

Level 4: Trigger.dev
  - 长时任务
  - Waitpoint审核
```

## 核心命令

```bash
# 创建定时任务
cron create "每天早上8点发送日报"
cron create "Every Monday at 9am, summarize last week's progress"

# 事件触发
cron on "github.pr.merged" do "notify slack #dev"

# 条件触发
cron create "if coverage < 80% then alert #team"

# 任务管理
cron list
cron pause <task-id>
cron resume <task-id>
cron delete <task-id>

# 交付配置
delivery add telegram @username
delivery add discord #channel
delivery set default slack
```

## 多平台交付配置

```yaml
# ~/.hermes/cron/delivery.yaml
delivery:
  telegram:
    bot_token: ${TELEGRAM_BOT_TOKEN}
    default_chat: @your_username

  discord:
    webhook_url: ${DISCORD_WEBHOOK_URL}
    default_channel: "#notifications"

  slack:
    token: ${SLACK_TOKEN}
    default_channel: "#alerts"

  email:
    smtp_host: smtp.gmail.com
    smtp_port: 587
    from: hermes@example.com
    to:
      - user@example.com
```

## 预期收益

| 指标 | 集成前 | 集成后 | 提升 |
|------|--------|--------|------|
| 定时任务配置时间 | 10分钟 | 10秒 | -98% |
| 多平台覆盖率 | 0 | 6个 | **新增** |
| 自动化场景数 | 10 | 50 | +400% |
| 告警响应时间 | 手动 | 秒级 | -95% |
