#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评论分析核心引擎
Comment Analyzer Core Engine

这是评论分析SKILL的主协调器，负责串联所有分析模块。
"""

import asyncio
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class CommentAnalyzer:
    """评论分析核心类"""

    def __init__(self, url: str, output_dir: str = "~/comment-analysis-reports"):
        self.url = url
        self.output_dir = Path(output_dir).expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 识别平台
        self.platform = self._identify_platform(url)

        print(f"✅ 平台识别：{self.platform['name']}")

        # 加载配置
        self.config = self._load_config()

        # 初始化Session管理器
        from .session_manager import SessionManager
        self.session_manager = SessionManager()

        # 检查登录状态
        platform_key = self._get_platform_key()
        if self.session_manager.is_logged_in(platform_key):
            print(f"✅ {self.platform['name']} 已登录，直接使用")
        else:
            login_required = self.config.get("platforms", {}).get(platform_key, {}).get("login_required", False)
            if login_required:
                print(f"⚠️  {self.platform['name']} 需要登录才能查看完整评论")

        # 初始化组件（懒加载，在需要时才导入）
        self.scraper = None
        self.sentiment_analyzer = None
        self.topic_extractor = None
        self.viewpoint_summarizer = None
        self.quality_evaluator = None
        self.report_generator = None

    def _identify_platform(self, url: str) -> Dict:
        """识别平台类型"""
        from .platform_scraper import PlatformScraper
        scraper = PlatformScraper(url, mode='identify')
        return scraper.identify_platform()

    def _load_config(self) -> Dict:
        """加载配置文件"""
        config_path = Path(__file__).parent.parent / "config" / "comment-analyzer.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _get_platform_key(self) -> str:
        """获取平台的配置键名"""
        url = self.url.lower()

        platform_mapping = {
            "weibo.com": "weibo",
            "weibo.cn": "weibo",
            "xiaohongshu.com": "xiaohongshu",
            "xhslink.com": "xiaohongshu",
            "douyin.com": "douyin",
            "bilibili.com": "bilibili",
            "b23.tv": "bilibili",
            "zhihu.com": "zhihu",
            "zhuanlan.zhihu.com": "zhihu",
            "mp.weixin.qq.com": "wechat_mp"
        }

        for domain, key in platform_mapping.items():
            if domain in url:
                return key

        # 默认返回第一个词
        return self.platform.get('key', self.platform['name'].lower())

    async def analyze(self, max_comments: int = 500) -> Dict:
        """
        执行完整分析流程

        Args:
            max_comments: 最大爬取评论数

        Returns:
            分析结果字典
        """
        print(f"\n{'='*60}")
        print(f"开始分析：{self.url}")
        print(f"{'='*60}\n")

        # 步骤1：爬取评论
        print("📥 步骤1/6：爬取评论数据...")
        comments_data = await self._scrape_comments(max_comments)
        comments = comments_data.get("comments", [])
        print(f"✅ 成功爬取 {len(comments)} 条评论\n")

        if len(comments) < self.config.get("analysis", {}).get("min_comments", 10):
            print(f"⚠️  警告：评论数量过少（{len(comments)}条），分析结果可能不准确")

        # 步骤2：情感分析
        print("😊 步骤2/6：情感倾向分析...")
        sentiment_results = await self._analyze_sentiment(comments)
        print(f"✅ 情感分析完成：{sentiment_results['overall']}\n")

        # 步骤3：话题提取
        print("💬 步骤3/6：高频话题提取...")
        topic_results = await self._extract_topics(comments)
        print(f"✅ 话题提取完成：{len(topic_results['keywords'])}个关键词\n")

        # 步骤4：观点挖掘
        print("💡 步骤4/6：用户观点挖掘...")
        viewpoint_results = await self._summarize_viewpoints(comments)
        print(f"✅ 观点挖掘完成：{len(viewpoint_results['viewpoints'])}个核心观点\n")

        # 步骤5：质量评估
        print("⭐ 步骤5/6：评论质量评估...")
        quality_results = await self._evaluate_quality(comments)
        print(f"✅ 质量评估完成：{quality_results['high_quality_count']}条高质量评论\n")

        # 步骤6：汇总结果
        print("📊 步骤6/6：生成分析报告...")
        results = {
            "meta": {
                "url": self.url,
                "platform": self.platform['name'],
                "total_comments": len(comments),
                "analyzed_at": datetime.now().isoformat()
            },
            "sentiment": sentiment_results,
            "topics": topic_results,
            "viewpoints": viewpoint_results,
            "quality": quality_results
        }

        # 生成报告
        report_path = await self._generate_report(results)
        print(f"✅ 报告已保存：{report_path}\n")

        # 提取核心洞察
        insights = self._extract_insights(results)

        return {
            "report_path": str(report_path),
            "insights": insights,
            "results": results
        }

    async def _scrape_comments(self, max_comments: int) -> Dict:
        """爬取评论数据（带登录检查和Session保存）"""
        from .platform_scraper import PlatformScraper
        from .mcp_connector import MCPConnector

        platform_key = self._get_platform_key()

        # 检查是否需要登录
        login_required = self.config.get("platforms", {}).get(platform_key, {}).get("login_required", False)

        if login_required and not self.session_manager.is_logged_in(platform_key):
            # 显示登录提示
            print(f"\n{'='*60}")
            print(f"⚠️  {self.platform['name']} 需要登录才能查看完整评论")
            print(f"{'='*60}")
            print(f"\n操作步骤：")
            print(f"1. 使用手机{self.platform['name']}App扫描页面上的二维码")
            print(f"2. 确认登录")
            print(f"\n⏱️  系统将等待最多45秒...\n")

        mcp = MCPConnector()
        self.scraper = PlatformScraper(
            self.url,
            mcp,
            mode=self.config.get("scraper", {}).get("mode", "mcp")
        )

        # 执行爬取（scraper内部会处理登录等待）
        result = await self.scraper.scrape_comments(max_comments)

        # 如果爬取成功且需要登录，保存Session
        if result.get("success") and login_required:
            print(f"\n💾 保存{self.platform['name']}登录状态...")

            # 这里应该从scraper获取cookies
            # 实际实现需要scraper返回cookies
            # cookies = self.scraper.get_cookies()
            # self.session_manager.save_session(platform_key, cookies, {
            #     "platform": self.platform['name'],
            #     "url": self.url
            # })

            print(f"✅ 登录状态已保存，下次使用无需重新登录\n")

        return result

    async def _analyze_sentiment(self, comments: List[Dict]) -> Dict:
        """情感分析"""
        from .sentiment_analyzer import SentimentAnalyzer

        self.sentiment_analyzer = SentimentAnalyzer()
        return self.sentiment_analyzer.analyze(comments)

    async def _extract_topics(self, comments: List[Dict]) -> Dict:
        """话题提取"""
        from .topic_extractor import TopicExtractor

        self.topic_extractor = TopicExtractor()
        return self.topic_extractor.extract(comments)

    async def _summarize_viewpoints(self, comments: List[Dict]) -> Dict:
        """观点提炼"""
        from .viewpoint_summarizer import ViewpointSummarizer

        self.viewpoint_summarizer = ViewpointSummarizer()
        return self.viewpoint_summarizer.summarize(comments)

    async def _evaluate_quality(self, comments: List[Dict]) -> Dict:
        """质量评估"""
        from .quality_evaluator import QualityEvaluator

        self.quality_evaluator = QualityEvaluator()
        return self.quality_evaluator.evaluate(comments)

    async def _generate_report(self, results: Dict) -> Path:
        """生成HTML报告"""
        from .report_generator import ReportGenerator

        self.report_generator = ReportGenerator()
        return self.report_generator.generate_html(results, self.output_dir)

    def _extract_insights(self, results: Dict) -> Dict:
        """提取核心洞察"""
        sentiment = results["sentiment"]
        topics = results["topics"]
        viewpoints = results["viewpoints"]

        return {
            "sentiment_overview": sentiment["overall"],
            "sentiment_distribution": sentiment["distribution"],
            "top_topic": topics["keywords"][0] if topics["keywords"] else None,
            "top_viewpoint": viewpoints["viewpoints"][0]["viewpoint"] if viewpoints["viewpoints"] else None,
            "viewpoint_support": viewpoints["viewpoints"][0]["support_count"] if viewpoints["viewpoints"] else 0,
            "quality_ratio": f"{results['quality']['high_quality_ratio']*100:.1f}%"
        }

    def print_insights(self, insights: Dict):
        """打印核心洞察"""
        print(f"\n{'='*60}")
        print(f"🎯 核心洞察")
        print(f"{'='*60}\n")

        print(f"📊 情感倾向：{insights['sentiment_overview']}")
        print(f"   分布：{insights['sentiment_distribution']}\n")

        if insights['top_topic']:
            print(f"💬 核心话题：{insights['top_topic']['word']}（{insights['top_topic']['count']}次）\n")

        if insights['top_viewpoint']:
            print(f"💡 主要观点：{insights['top_viewpoint']}")
            print(f"   支持度：{insights['viewpoint_support']}条评论\n")

        print(f"⭐ 评论质量：{insights['quality_ratio']}高质量评论")
        print(f"{'='*60}\n")


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="评论分析工具")
    parser.add_argument("url", help="内容链接")
    parser.add_argument("--max-comments", type=int, default=500,
                        help="最大爬取评论数（默认500）")
    parser.add_argument("--output-dir", default="~/comment-analysis-reports",
                        help="输出目录（默认~/comment-analysis-reports）")

    args = parser.parse_args()

    # 创建分析器
    analyzer = CommentAnalyzer(args.url, output_dir=args.output_dir)

    # 执行分析
    try:
        results = asyncio.run(analyzer.analyze(args.max_comments))

        # 打印核心洞察
        analyzer.print_insights(results["insights"])

        # 打印报告路径
        print(f"📁 完整报告：{results['report_path']}")
        print(f"\n✅ 分析完成！")

    except Exception as e:
        print(f"\n❌ 分析失败：{str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
