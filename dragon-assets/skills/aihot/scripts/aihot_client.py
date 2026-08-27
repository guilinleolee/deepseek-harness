# ~/.claude/skills/aihot/scripts/aihot_client.py
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "https://aihot.virxact.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def get_daily(date: str = None) -> list:
    """获取指定日期的AI热点"""
    if date is None:
        url = f"{BASE_URL}/api/public/daily"
    else:
        url = f"{BASE_URL}/api/public/daily/{date}"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_dailies(days: int = 7) -> list:
    """获取近期N天的AI热点"""
    url = f"{BASE_URL}/api/public/dailies"
    resp = requests.get(url, params={"days": days}, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_items(ids: str) -> list:
    """获取热点详情"""
    url = f"{BASE_URL}/api/public/items"
    resp = requests.get(url, params={"ids": ids}, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()


def format_report(items: list) -> str:
    """格式化输出为天龙报告"""
    lines = ["# AI热点日报\n"]
    lines.append(f"日期: {datetime.now().strftime('%Y-%m-%d')}\n")
    for i, item in enumerate(items, 1):
        ts = datetime.fromtimestamp(item.get('ct', 0)).strftime('%m-%d') if item.get('ct') else ''
        lines.append(f"{i}. {item.get('title', '')}")
        lines.append(f"   来源: {item.get('source', '')} | 时间: {ts}")
        lines.append(f"   摘要: {item.get('desc', '')}")
        lines.append(f"   链接: {item.get('url', '')}\n")
    return '\n'.join(lines)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="aihot CLI")
    parser.add_argument("action", choices=["daily", "dailies", "items", "report"], help="Action to perform")
    parser.add_argument("--date", help="Date in YYYY-MM-DD format")
    parser.add_argument("--days", type=int, default=7, help="Number of days for dailies")
    parser.add_argument("--ids", help="Comma-separated IDs for items")
    parser.add_argument("--output", help="Output file path")
    args = parser.parse_args()

    if args.action == "daily":
        result = get_daily(args.date)
    elif args.action == "dailies":
        result = get_dailies(args.days)
    elif args.action == "items":
        result = get_items(args.ids)
    elif args.action == "report":
        days = args.days if hasattr(args, 'days') else 7
        items = get_dailies(days)
        result = format_report(items)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"报告已保存到: {args.output}")
            return

    print(json.dumps(result, ensure_ascii=False, indent=2))
