#!/usr/bin/env python3
"""
n8n Workflow Pattern Search
搜索n8n工作流模板
"""

import sys
import json

# 模拟数据库搜索结果（实际使用时替换为真实索引）
SAMPLE_PATTERNS = [
    {
        "name": "客户投诉自动处理",
        "description": "自动处理客户投诉的全流程：从Webhook接收投诉 → Telegram通知团队 → Email自动回复客户 → Jira创建工单",
        "category": "crm",
        "integration": "telegram,gmail,jira",
        "nodes_count": 4,
        "trigger_type": "Webhook",
        "complexity": "简单",
        "pattern": "webhook-trigger → telegram-notify → email-reply → jira-create"
    },
    {
        "name": "定时数据报告",
        "description": "每日定时从数据库提取数据，生成报告并通过邮件发送",
        "category": "database",
        "integration": "postgresql,code,gmail",
        "nodes_count": 4,
        "trigger_type": "Cron",
        "complexity": "中等",
        "pattern": "cron-trigger → postgresql-query → code-process → gmail-send"
    },
    {
        "name": "社交媒体内容发布",
        "description": "定时检查内容源，筛选后发布到多个社交平台",
        "category": "marketing",
        "integration": "schedule,http,discord,twitter",
        "nodes_count": 5,
        "trigger_type": "Schedule",
        "complexity": "中等",
        "pattern": "schedule-trigger → http-fetch → filter → discord-post → twitter-post"
    },
    {
        "name": "新用户欢迎流程",
        "description": "新用户注册后自动发送欢迎邮件、Slack通知、HubSpot记录",
        "category": "crm",
        "integration": "webhook,gmail,slack,hubspot",
        "nodes_count": 4,
        "trigger_type": "Webhook",
        "complexity": "简单",
        "pattern": "webhook-trigger → gmail-welcome → slack-notify → hubspot-create"
    },
    {
        "name": "数据库自动备份",
        "description": "每日凌晨自动备份数据库到AWS S3",
        "category": "database",
        "integration": "cron,postgresql,code,aws-s3",
        "nodes_count": 4,
        "trigger_type": "Cron",
        "complexity": "中等",
        "pattern": "cron-trigger → postgresql-select → code-compress → aws-s3-upload"
    },
    {
        "name": "电商订单处理",
        "description": "WooCommerce新订单自动处理：创建Supabase记录 → Slack通知 → Email确认",
        "category": "ecommerce",
        "integration": "webhook,woocommerce,supabase,slack,gmail",
        "nodes_count": 5,
        "trigger_type": "Webhook",
        "complexity": "中等",
        "pattern": "webhook-trigger → woocommerce-order → supabase-insert → slack-notify → gmail-confirm"
    },
    {
        "name": "GitHub Issue自动处理",
        "description": "GitHub Issue创建时自动同步到Jira、通知Slack",
        "category": "devops",
        "integration": "github,slack,jira",
        "nodes_count": 4,
        "trigger_type": "Webhook",
        "complexity": "简单",
        "pattern": "github-trigger → jira-create → slack-notify"
    },
    {
        "name": "邮件自动化回复",
        "description": "IMAP读取邮件，根据关键词自动分类回复",
        "category": "communication",
        "integration": "email-read-imap,filter,code,gmail",
        "nodes_count": 5,
        "trigger_type": "Schedule",
        "complexity": "复杂",
        "pattern": "schedule-trigger → imap-read → filter-classify → code-analyze → gmail-reply"
    },
    {
        "name": "AI内容摘要生成",
        "description": "定时抓取新闻源，使用OpenAI生成摘要，发送到Slack",
        "category": "ai",
        "integration": "rss,http,openai,slack",
        "nodes_count": 5,
        "trigger_type": "Schedule",
        "complexity": "复杂",
        "pattern": "schedule-trigger → rss-fetch → http-scrape → openai-summarize → slack-notify"
    },
    {
        "name": "跨系统数据同步",
        "description": "Google Sheets与Supabase双向同步",
        "category": "database",
        "integration": "schedule,google-sheets,code,supabase",
        "nodes_count": 5,
        "trigger_type": "Schedule",
        "complexity": "复杂",
        "pattern": "schedule-trigger → sheets-read → code-transform → supabase-upsert → sheets-write"
    }
]


def search_workflows(keyword, category=None, trigger=None, limit=10):
    """搜索工作流模板"""
    results = []

    for wf in SAMPLE_PATTERNS:
        # 关键词匹配
        if keyword.lower() not in wf['name'].lower() and keyword.lower() not in wf['description'].lower():
            continue

        # 分类过滤
        if category and category.lower() not in wf['category'].lower():
            continue

        # 触发器过滤
        if trigger and trigger.lower() not in wf['trigger_type'].lower():
            continue

        results.append(wf)

        if len(results) >= limit:
            break

    return results


def format_result(workflow, rank):
    """格式化搜索结果"""
    integrations = workflow['integration'].split(',')[:3]
    return f"""#{rank} {workflow['name']}
   分类: {workflow['category']} | 节点: {workflow['nodes_count']}个
   触发: {workflow['trigger_type']} | 复杂度: {workflow['complexity']}
   集成: {', '.join(integrations)}
   描述: {workflow['description']}
   模式: {workflow['pattern']}"""


def main():
    if len(sys.argv) < 2:
        print("用法: n8n-search <keyword> [--category <分类>] [--trigger <触发器>] [--limit <数量>]")
        print("")
        print("示例:")
        print("  n8n-search 客户投诉")
        print("  n8n-search 定时报告 --trigger cron")
        print("  n8n-search 社交媒体 --category marketing")
        sys.exit(1)

    keyword = sys.argv[1]
    category = None
    trigger = None
    limit = 10

    # 解析参数
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == '--category' and i + 1 < len(args):
            category = args[i + 1]
            i += 2
        elif args[i] == '--trigger' and i + 1 < len(args):
            trigger = args[i + 1]
            i += 2
        elif args[i] == '--limit' and i + 1 < len(args):
            limit = int(args[i + 1])
            i += 2
        else:
            i += 1

    results = search_workflows(keyword, category, trigger, limit)

    if not results:
        print(f"\n未找到匹配 '{keyword}' 的工作流")
        print("\n尝试以下关键词:")
        print("  - 客户投诉, 投诉处理, support")
        print("  - 定时报告, 日报, schedule, report")
        print("  - 社交媒体, 社交, social, twitter, discord")
        print("  - 数据同步, sync, import, export")
        print("  - 欢迎, welcome, 注册, signup")
        print("  - 备份, backup, save")
        print("  - 订单, order, ecommerce")
        print("  - AI, openai, 摘要, summary")
        return

    print(f"\n找到 {len(results)} 个匹配的工作流模板:\n")
    print("=" * 70)
    for i, workflow in enumerate(results, 1):
        print(format_result(workflow, i))
        print("-" * 70)


if __name__ == "__main__":
    main()