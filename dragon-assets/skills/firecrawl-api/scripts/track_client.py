#!/usr/bin/env python3
"""
Firecrawl Track Client - 变化追踪监控
监控网页内容变化并通知
"""

import argparse
import json
import os
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='🔥 Firecrawl Track - 变化追踪监控')
    parser.add_argument('url', help='目标URL')
    parser.add_argument('--interval', default='daily',
                       choices=['hourly', 'daily', 'weekly'],
                       help='检查间隔')
    parser.add_argument('--notify', help='通知方式: email, webhook, slack')
    parser.add_argument('--history', action='store_true', help='显示变化历史')
    parser.add_argument('--days', type=int, default=30, help='历史天数')
    parser.add_argument('--setup', action='store_true', help='设置监控任务')
    parser.add_argument('--list', action='store_true', help='列出所有监控任务')
    parser.add_argument('--delete', help='删除监控任务 (URL)')
    args = parser.parse_args()

    print("🔥 Firecrawl Change Tracking")
    print("="*60)
    print()
    print("⚠️  Change Tracking 需要 Firecrawl 订阅服务")
    print("   访问 https://firecrawl.dev/pricing 了解更多")
    print()
    print("="*60)
    print()
    print("💡 天龙引擎替代方案:")
    print()
    print("1. 定时Agent-Reach + diff 比较:")
    print("   ```bash")
    print("   # 定时抓取 + 保存")
    print("   0 * * * * python firecrawl/scrape_client.py url > /tmp/page.txt")
    print()
    print("   # 检测变化")
    print("   diff /tmp/page.txt /tmp/page_prev.txt || echo '变化检测!'")
    print("   ```")
    print()
    print("2. 结合 paperclip-heartbeat:")
    print("   ```bash")
    print("   # 设置心跳调度")
    print("   /paperclip-heartbeat add 01investigator '0 9 * * *' \\\\")
    print("     '监控竞品价格变化'")
    print("   ```")
    print()
    print("3. Python脚本实现:")
    print("   ```python")
    print("   import hashlib, difflib")
    print()
    print("   def check_change(url):")
    print("       content = scrape(url)")
    print("       new_hash = hashlib.md5(content).hexdigest()")
    print("       if new_hash != get_stored_hash(url):")
    print("           notify('变化检测!')")
    print("           store_hash(url, new_hash)")
    print("   ```")

    # 如果是设置模式，显示配置模板
    if args.setup:
        print()
        print("="*60)
        print("配置模板 (firecrawl_config.json):")
        print("="*60)
        config = {
            "track": {
                "enabled": True,
                "tasks": [
                    {
                        "url": args.url,
                        "interval": args.interval,
                        "notify": args.notify or ["email"],
                        "hash": None
                    }
                ]
            }
        }
        print(json.dumps(config, indent=2))

        # 保存配置
        config_file = Path.home() / ".claude" / "firecrawl_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"\n💾 配置已保存: {config_file}")

if __name__ == '__main__':
    main()
