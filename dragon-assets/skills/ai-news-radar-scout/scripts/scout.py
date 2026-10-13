#!/usr/bin/env python3
"""
AI News Radar Scout - 伯乐信息源评估脚本
智能判断信息源类型并分流处理
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# 信息源类型判断规则
SOURCE_TYPE_RULES = {
    "official": {
        "keywords": ["changelog", "release-notes", "api", "blog", "official"],
        "domains": ["openai.com", "anthropic.com", "deepmind.google",
                   "meta.ai", "mistral.ai", "perplexity.ai", "groq.com",
                   "google.com", "microsoft.com", "amazon.com"],
        "priority": 0
    },
    "opml": {
        "extensions": [".opml", ".xml"],
        "keywords": ["feed", "rss", "atom", "subscription"],
        "priority": 1
    },
    "publicFeed": {
        "keywords": ["github.com", "feed", "releases"],
        "patterns": ["/releases.atom", "/releases/tags", "/commits/"],
        "priority": 2
    },
    "staticPage": {
        "extensions": [".html", ".htm", ".md"],
        "priority": 3
    },
    "privateMail": {
        "keywords": ["mail", "email", "smtp", "imap"],
        "priority": 4
    }
}


def classify_source(url: str) -> dict:
    """
    伯乐Skill核心：判断信息源类型
    """
    url_lower = url.lower()

    # P0: 官方RSS/changelog
    for domain in SOURCE_TYPE_RULES["official"]["domains"]:
        if domain in url_lower:
            return {
                "type": "official",
                "priority": 0,
                "reason": f"官方域名: {domain}",
                "action": "高优先级抓取"
            }

    # P1: OPML订阅
    if url_lower.endswith((".opml", ".xml")):
        return {
            "type": "opml",
            "priority": 1,
            "reason": "OPML批量订阅文件",
            "action": "标准处理"
        }

    # P2: GitHub公开Feed
    if "github.com" in url_lower:
        if any(p in url_lower for p in ["/releases.atom", "/commits/", "/releases/tags"]):
            return {
                "type": "publicFeed",
                "priority": 2,
                "reason": "GitHub公开Feed",
                "action": "常规处理"
            }

    # P3: 静态页面
    if url_lower.endswith((".html", ".htm", ".md")) or "feed" in url_lower:
        return {
            "type": "staticPage",
            "priority": 3,
            "reason": "静态页面",
            "action": "Jina Reader兜底"
        }

    # P4: 私有邮箱
    if any(kw in url_lower for kw in ["mail", "email", "smtp", "imap"]):
        return {
            "type": "privateMail",
            "priority": 4,
            "reason": "私有邮箱",
            "action": "需API"
        }

    # Skip: 高风险来源
    return {
        "type": "skip",
        "priority": 5,
        "reason": "未识别类型",
        "action": "跳过"
    }


def evaluate_source(url: str, check_health: bool = True) -> dict:
    """
    评估单个信息源
    """
    import requests

    result = classify_source(url)
    result["url"] = url

    if check_health and result["priority"] < 5:
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            result["status"] = "healthy" if response.status_code < 400 else "unhealthy"
            result["status_code"] = response.status_code
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
    else:
        result["status"] = "not_checked"

    return result


def batch_evaluate(opml_path: Optional[str] = None, output_path: Optional[str] = None):
    """
    批量评估OPML文件中的信息源
    """
    import feedparser

    sources = []

    if opml_path:
        opml_file = Path(opml_path)
        if opml_file.exists() and opml_file.suffix == ".opml":
            feed = feedparser.parse(str(opml_file))
            for entry in feed.entries:
                url = entry.get("href") or entry.get("link", "")
                if url:
                    result = classify_source(url)
                    result["title"] = entry.get("title", "")
                    result["url"] = url
                    sources.append(result)

    report = {
        "timestamp": str(Path().cwd()),
        "total_sources": len(sources),
        "by_type": {},
        "sources": sources
    }

    # 统计各类型数量
    for s in sources:
        t = s["type"]
        report["by_type"][t] = report["by_type"].get(t, 0) + 1

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

    return report


def main():
    parser = argparse.ArgumentParser(description="AI News Radar Scout - 伯乐信息源评估")
    parser.add_argument("command", choices=["evaluate", "batch", "audit", "health"],
                        help="子命令")
    parser.add_argument("--source", "-s", help="单个信息源URL")
    parser.add_argument("--opml", "-o", help="OPML文件路径")
    parser.add_argument("--output", help="输出文件路径")

    args = parser.parse_args()

    if args.command == "evaluate":
        if not args.source:
            print("错误: evaluate命令需要 --source 参数")
            sys.exit(1)
        result = evaluate_source(args.source)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "batch":
        result = batch_evaluate(args.opml, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "audit":
        print("伯乐审计报告生成中...")

    elif args.command == "health":
        print("源健康状态检查...")


if __name__ == "__main__":
    main()
