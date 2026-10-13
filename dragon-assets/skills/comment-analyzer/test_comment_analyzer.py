#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评论分析SKILL测试脚本
"""

import asyncio
import json
import sys
from pathlib import Path

# 添加scripts目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "scripts"))


def load_mock_data():
    """加载模拟评论数据"""
    return {
        "platform": "微博",
        "post_url": "https://weibo.com/7762107285/QkRZnufTd",
        "post_title": "测试微博",
        "comments": [
            {
                "id": "1",
                "content": "完全支持这个观点！说得非常好。",
                "author": "用户A",
                "publish_time": "2025-01-15 10:00:00",
                "likes": 150
            },
            {
                "id": "2",
                "content": "建议增加更多实例，这样更容易理解。",
                "author": "用户B",
                "publish_time": "2025-01-15 10:05:00",
                "likes": 85
            },
            {
                "id": "3",
                "content": "这是什么意思？能详细说明一下吗？",
                "author": "用户C",
                "publish_time": "2025-01-15 10:10:00",
                "likes": 23
            },
            {
                "id": "4",
                "content": "内容太差了，浪费时间，不建议观看。",
                "author": "用户D",
                "publish_time": "2025-01-15 10:15:00",
                "likes": 12
            },
            {
                "id": "5",
                "content": "真的很棒！学到了很多，强烈推荐给大家！",
                "author": "用户E",
                "publish_time": "2025-01-15 10:20:00",
                "likes": 200
            },
            {
                "id": "6",
                "content": "支持！希望能继续出这样高质量的内容。",
                "author": "用户F",
                "publish_time": "2025-01-15 10:25:00",
                "likes": 95
            },
            {
                "id": "7",
                "content": "不喜欢，感觉有点失望。",
                "author": "用户G",
                "publish_time": "2025-01-15 10:30:00",
                "likes": 18
            },
            {
                "id": "8",
                "content": "非常优秀的作品，质量很高，值得一看！",
                "author": "用户H",
                "publish_time": "2025-01-15 10:35:00",
                "likes": 175
            },
            {
                "id": "9",
                "content": "可以考虑换个方式表达，效果可能会更好。",
                "author": "用户I",
                "publish_time": "2025-01-15 10:40:00",
                "likes": 45
            },
            {
                "id": "10",
                "content": "希望能改进一下，有些地方不太清楚。",
                "author": "用户J",
                "publish_time": "2025-01-15 10:45:00",
                "likes": 67
            }
        ],
        "total_count": 10,
        "scrape_method": "mock"
    }


async def test_analyzer():
    """测试分析器"""
    print("\n" + "="*60)
    print("🧪 评论分析SKILL测试")
    print("="*60 + "\n")

    # 加载模拟数据
    print("📥 加载模拟评论数据...")
    comments_data = load_mock_data()
    comments = comments_data["comments"]
    print(f"✅ 加载了 {len(comments)} 条评论\n")

    # 测试情感分析
    print("😊 测试情感分析模块...")
    from sentiment_analyzer import SentimentAnalyzer

    sentiment_analyzer = SentimentAnalyzer()
    sentiment_results = sentiment_analyzer.analyze(comments)

    print(f"✅ 情感分析完成")
    print(f"   整体倾向：{sentiment_results['overall']}")
    print(f"   分布：")
    for category, count in sentiment_results['distribution'].items():
        print(f"     - {category}: {count}条")
    print()

    # 测试话题提取
    print("💬 测试话题提取模块...")
    from topic_extractor import TopicExtractor

    topic_extractor = TopicExtractor()
    topic_results = topic_extractor.extract(comments)

    print(f"✅ 话题提取完成")
    print(f"   TOP5关键词：")
    for kw in topic_results['keywords'][:5]:
        print(f"     - {kw['word']}: {kw['count']}次")
    print()

    # 测试观点提炼
    print("💡 测试观点提炼模块...")
    from viewpoint_summarizer import ViewpointSummarizer

    viewpoint_summarizer = ViewpointSummarizer()
    viewpoint_results = viewpoint_summarizer.summarize(comments)

    print(f"✅ 观点提炼完成")
    print(f"   TOP3观点：")
    for vp in viewpoint_results['viewpoints'][:3]:
        print(f"     - {vp['viewpoint'][:50]}... ({vp['polarity']})")
    print()

    # 测试质量评估
    print("⭐ 测试质量评估模块...")
    from quality_evaluator import QualityEvaluator

    quality_evaluator = QualityEvaluator()
    quality_results = quality_evaluator.evaluate(comments)

    print(f"✅ 质量评估完成")
    print(f"   高质量评论：{quality_results['high_quality_count']}条")
    print(f"   高质量占比：{quality_results['high_quality_ratio']*100:.1f}%")
    print()

    # 汇总结果
    results = {
        "meta": {
            "url": comments_data["post_url"],
            "platform": comments_data["platform"],
            "total_comments": len(comments),
            "analyzed_at": "2025-01-15T12:00:00"
        },
        "sentiment": sentiment_results,
        "topics": topic_results,
        "viewpoints": viewpoint_results,
        "quality": quality_results
    }

    # 生成HTML报告
    print("📊 生成HTML报告...")
    from report_generator import ReportGenerator

    report_generator = ReportGenerator()
    output_dir = Path("~/comment-analysis-reports").expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = report_generator.generate_html(results, output_dir)
    print(f"✅ 报告已保存：{report_path}\n")

    # 打印核心洞察
    print("="*60)
    print("🎯 核心洞察")
    print("="*60 + "\n")

    print(f"📊 情感倾向：{sentiment_results['overall']}")
    dist = sentiment_results['distribution']
    print(f"   分布：正面{dist['positive']}条、建议{dist['suggestion']}条、中性{dist['neutral']}条、负面{dist['negative']}条\n")

    if topic_results['keywords']:
        top_kw = topic_results['keywords'][0]
        print(f"💬 核心话题：{top_kw['word']}（{top_kw['count']}次）\n")

    if viewpoint_results['viewpoints']:
        top_vp = viewpoint_results['viewpoints'][0]
        print(f"💡 主要观点：{top_vp['viewpoint']}")
        print(f"   极性：{top_vp['polarity']}")
        print(f"   支持度：{top_vp['support_count']}条评论\n")

    print(f"⭐ 评论质量：{quality_results['high_quality_ratio']*100:.1f}%高质量评论")

    print(f"\n📁 完整报告：{report_path}")
    print("\n✅ 测试完成！\n")


if __name__ == "__main__":
    asyncio.run(test_analyzer())
