#!/usr/bin/env python3
"""
GEO Content Generator CLI
决策级GEO内容生成引擎

Usage:
    geo-generate "AI Agent发展趋势" --depth decision
    geo-brief "主题" --output brief.json
    geo-quality-gate content_id
"""

import argparse
import json
import os
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.dageno_client import DagenoClient
from scripts.fanout_extractor import FanoutExtractor
from scripts.citation_crawl import CitationCrawler
from scripts.brief_builder import BriefBuilder
from scripts.quality_gate import QualityGate
from scripts.wordpress_publisher import WordPressPublisher


class GEOContentGenerator:
    """GEO内容生成器"""

    def __init__(self):
        self.dageno = DagenoClient()
        self.fanout_extractor = FanoutExtractor()
        self.citation_crawler = CitationCrawler()
        self.brief_builder = BriefBuilder()
        self.quality_gate = QualityGate()
        self.wordpress = WordPressPublisher()

    def generate(self, topic: str, depth: str = "full") -> dict:
        """
        生成GEO内容

        Args:
            topic: 内容主题
            depth: 生成深度 (brief/full/decision)

        Returns:
            dict: 生成结果
        """
        print(f"🎯 开始生成GEO内容: {topic}")
        print(f"📊 生成深度: {depth}")

        # Step 1: 发现Prompt机会
        print("\n[1/5] 发现Prompt机会...")
        opportunities = self.dageno.discover_opportunities(topic)

        # Step 2: 提取Fanout
        print("[2/5] 提取Fanout...")
        fanouts = self.fanout_extractor.extract(opportunities)

        # Step 3: 爬取引用页面
        print("[3/5] 爬取引用页面...")
        citations = self.citation_crawler.crawl(fanouts[:5])

        # Step 4: 构建Editorial Brief
        print("[4/5] 构建Editorial Brief...")
        brief = self.brief_builder.build(topic, fanouts, citations, depth)

        # Step 5: 质量门控检查
        print("[5/5] 质量门控检查...")
        quality_result = self.quality_gate.check(brief, citations)

        if not quality_result["passed"]:
            print(f"⚠️  质量门控未通过: {quality_result['reason']}")
            return {"success": False, "quality_result": quality_result}

        print("✅ 质量门控通过!")
        return {
            "success": True,
            "brief": brief,
            "fanouts": fanouts,
            "citations": citations,
            "quality_result": quality_result
        }

    def generate_from_backlog(self, limit: int = 5) -> list:
        """
        从Backlog生成内容

        Args:
            limit: 最多生成数量

        Returns:
            list: 生成结果列表
        """
        from scripts.backlog_manager import BacklogManager

        backlog = BacklogManager()
        items = backlog.select_next(limit)

        results = []
        for item in items:
            result = self.generate(item["topic"], item.get("depth", "full"))
            results.append({
                "item": item,
                "result": result
            })

            if result["success"]:
                backlog.mark_completed(item["id"])
            else:
                backlog.mark_failed(item["id"])

        return results


def main():
    parser = argparse.ArgumentParser(description="GEO Content Generator CLI")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # geo-generate 命令
    gen_parser = subparsers.add_parser("generate", help="生成GEO内容")
    gen_parser.add_argument("topic", help="内容主题")
    gen_parser.add_argument("--depth", choices=["brief", "full", "decision"],
                          default="full", help="生成深度")

    # geo-brief 命令
    brief_parser = subparsers.add_parser("brief", help="构建Editorial Brief")
    brief_parser.add_argument("topic", help="内容主题")
    brief_parser.add_argument("--output", help="输出文件")

    # geo-quality 命令
    quality_parser = subparsers.add_parser("quality-gate", help="质量门控检查")
    quality_parser.add_argument("content_id", help="内容ID")

    # geo-backlog 命令
    backlog_parser = subparsers.add_parser("backlog", help="Backlog管理")
    backlog_parser.add_argument("action", choices=["list", "add", "select"])
    backlog_parser.add_argument("--topic", help="Backlog主题")
    backlog_parser.add_argument("--priority", default="P1", help="优先级")

    # geo-publish 命令
    publish_parser = subparsers.add_parser("publish", help="发布内容")
    publish_parser.add_argument("content_id", help="内容ID")
    publish_parser.add_argument("--cms", default="wordpress", help="CMS类型")
    publish_parser.add_argument("--mode", default="draft", choices=["draft", "publish"])

    args = parser.parse_args()

    if args.command == "generate":
        generator = GEOContentGenerator()
        result = generator.generate(args.topic, args.depth)

        if result["success"]:
            print("\n✅ 内容生成成功!")
            print(f"📝 Brief: {result['brief']['working_title']}")
            print(f"🔗 Fanouts: {len(result['fanouts'])}")
            print(f"📚 Citations: {len(result['citations'])}")
            print(f"🎯 Quality Score: {result['quality_result']['score']}")
        else:
            print(f"\n❌ 生成失败: {result['quality_result']['reason']}")
            sys.exit(1)

    elif args.command == "brief":
        generator = GEOContentGenerator()
        opportunities = generator.dageno.discover_opportunities(args.topic)
        fanouts = generator.fanout_extractor.extract(opportunities)
        brief = generator.brief_builder.build(args.topic, fanouts, [], "full")

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(brief, f, ensure_ascii=False, indent=2)
            print(f"✅ Brief已保存到: {args.output}")
        else:
            print(json.dumps(brief, ensure_ascii=False, indent=2))

    elif args.command == "quality-gate":
        gate = QualityGate()
        result = gate.check_by_id(args.content_id)

        print(f"\n🎯 Quality Gate Result for {args.content_id}")
        print(f"Passed: {result['passed']}")
        print(f"Score: {result['score']}")
        print(f"Issues: {result.get('issues', [])}")

    elif args.command == "backlog":
        from scripts.backlog_manager import BacklogManager
        backlog = BacklogManager()

        if args.action == "list":
            items = backlog.list_all()
            print(f"\n📋 Backlog Items ({len(items)} total)")
            for item in items:
                status_icon = {"pending": "⏳", "running": "🔄", "completed": "✅", "failed": "❌"}[item["status"]]
                print(f"{status_icon} [{item['priority']}] {item['topic']} - {item['status']}")

        elif args.action == "add":
            item = backlog.add(args.topic, args.priority)
            print(f"✅ Added: {item['id']}")

        elif args.action == "select":
            items = backlog.select_next(1)
            if items:
                print(f"📌 Selected: {items[0]['topic']}")
            else:
                print("📭 No items available")

    elif args.command == "publish":
        publisher = WordPressPublisher()
        result = publisher.publish(args.content_id, args.cms, args.mode)
        print(f"{'✅' if result['success'] else '❌'} {result.get('message', '')}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
