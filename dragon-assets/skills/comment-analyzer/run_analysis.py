#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行评论分析 - 使用模拟数据演示
"""

import sys
import json
from pathlib import Path

# 添加scripts目录到路径
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

# 模拟评论数据（基于贺娇龙文章主题）
MOCK_COMMENTS = [
    {"id": "1", "content": "太突然了，一路走好。她为新疆做了这么多贡献，真的令人敬佩。", "author": "用户A", "publish_time": "2025-01-15 01:00:00", "likes": 2580},
    {"id": "2", "content": "太可惜了，47岁正是年富力强的时候。她在昭苏骑马的形象还在眼前，没想到就这么走了。", "author": "用户B", "publish_time": "2025-01-15 01:15:00", "likes": 1890},
    {"id": "3", "content": "她是真正为人民服务的好干部，不是作秀的网红。5年500场直播，6亿销售额，这才是实实在在的成绩。", "author": "用户C", "publish_time": "2025-01-15 01:30:00", "likes": 3200},
    {"id": "4", "content": "建议加大对文旅干部的安全保障力度，特别是经常在户外工作的。", "author": "用户D", "publish_time": "2025-01-15 01:45:00", "likes": 890},
    {"id": "5", "content": "意外真的来得太突然，希望相关部门能总结经验，避免类似悲剧。", "author": "用户E", "publish_time": "2025-01-15 02:00:00", "likes": 1200},
    {"id": "6", "content": "她的工作精神值得学习，把流量都留给了新疆，这种奉献精神太难得了。", "author": "用户F", "publish_time": "2025-01-15 02:15:00", "likes": 2100},
    {"id": "7", "content": "太悲伤了，看过她的直播，真的很敬业。新疆失去了一位好干部。", "author": "用户G", "publish_time": "2025-01-15 02:30:00", "likes": 1650},
    {"id": "8", "content": "什么是意外坠马？希望能有更多细节，让公众了解真相。", "author": "用户H", "publish_time": "2025-01-15 02:45:00", "likes": 450},
    {"id": "9", "content": "她的故事应该被更多人知道，这才是真正的网红，正能量满满。", "author": "用户I", "publish_time": "2025-01-15 03:00:00", "likes": 1780},
    {"id": "10", "content": "一路走好，愿天堂没有意外。她的精神会激励更多人投身乡村振兴。", "author": "用户J", "publish_time": "2025-01-15 03:15:00", "likes": 2340},
    {"id": "11", "content": "太可惜了，新疆文旅需要更多像她这样的人。", "author": "用户K", "publish_time": "2025-01-15 03:30:00", "likes": 980},
    {"id": "12", "content": "建议设立贺娇龙基金，继续支持新疆农产品直播带货。", "author": "用户L", "publish_time": "2025-01-15 03:45:00", "likes": 750},
    {"id": "13", "content": "为什么这么突然？47岁太年轻了，希望家属节哀。", "author": "用户M", "publish_time": "2025-01-15 04:00:00", "likes": 890},
    {"id": "14", "content": "她的贡献新疆人民不会忘记，一路走好。", "author": "用户N", "publish_time": "2025-01-15 04:15:00", "likes": 1560},
    {"id": "15", "content": "这是什么情况？能详细说明一下吗？", "author": "用户O", "publish_time": "2025-01-15 04:30:00", "likes": 120},
    {"id": "16", "content": "太突然了，不敢相信。还记得她在雪地骑马的模样。", "author": "用户P", "publish_time": "2025-01-15 04:45:00", "likes": 1120},
    {"id": "17", "content": "她是真正干实事的人，不像有些网红只会作秀。", "author": "用户Q", "publish_time": "2025-01-15 05:00:00", "likes": 1450},
    {"id": "18", "content": "希望媒体能更多报道这类正能量人物。", "author": "用户R", "publish_time": "2025-01-15 05:15:00", "likes": 680},
    {"id": "19", "content": "太让人心痛了，她的工作还没完成。", "author": "用户S", "publish_time": "2025-01-15 05:30:00", "likes": 890},
    {"id": "20", "content": "一路走好，愿她在天之灵安息。", "author": "用户T", "publish_time": "2025-01-15 05:45:00", "likes": 1340},
]

def main():
    print("\n" + "="*60)
    print("🧪 评论分析SKILL - 模拟数据演示")
    print("="*60 + "\n")

    print("📥 使用模拟评论数据...")
    print(f"✅ 加载了 {len(MOCK_COMMENTS)} 条评论\n")

    # 导入分析模块
    from sentiment_analyzer import SentimentAnalyzer
    from topic_extractor import TopicExtractor
    from viewpoint_summarizer import ViewpointSummarizer
    from quality_evaluator import QualityEvaluator
    from report_generator import ReportGenerator
    from pathlib import Path

    # 步骤1：情感分析
    print("😊 步骤1：情感倾向分析...")
    sentiment_analyzer = SentimentAnalyzer()
    sentiment_results = sentiment_analyzer.analyze(MOCK_COMMENTS)
    print(f"✅ 情感分析完成")
    print(f"   整体倾向：{sentiment_results['overall']}")
    print(f"   分布：")
    for category, count in sentiment_results['distribution'].items():
        print(f"     - {category}: {count}条")
    print()

    # 步骤2：话题提取
    print("💬 步骤2：高频话题提取...")
    topic_extractor = TopicExtractor()
    topic_results = topic_extractor.extract(MOCK_COMMENTS)
    print(f"✅ 话题提取完成")
    print(f"   TOP5关键词：")
    for kw in topic_results['keywords'][:5]:
        print(f"     - {kw['word']}: {kw['count']}次")
    print()

    # 步骤3：观点提炼
    print("💡 步骤3：用户观点提炼...")
    viewpoint_summarizer = ViewpointSummarizer()
    viewpoint_results = viewpoint_summarizer.summarize(MOCK_COMMENTS)
    print(f"✅ 观点提炼完成")
    print(f"   TOP3观点：")
    for vp in viewpoint_results['viewpoints'][:3]:
        print(f"     - {vp['viewpoint'][:50]}... ({vp['polarity']})")
    print()

    # 步骤4：质量评估
    print("⭐ 步骤4：评论质量评估...")
    quality_evaluator = QualityEvaluator()
    quality_results = quality_evaluator.evaluate(MOCK_COMMENTS)
    print(f"✅ 质量评估完成")
    print(f"   高质量评论：{quality_results['high_quality_count']}条")
    print(f"   高质量占比：{quality_results['high_quality_ratio']*100:.1f}%")
    print()

    # 汇总结果
    results = {
        "meta": {
            "url": "https://weibo.com/ttarticle/p/show?id=2309405255148850249780",
            "platform": "微博",
            "total_comments": len(MOCK_COMMENTS),
            "analyzed_at": "2025-01-15T12:00:00"
        },
        "sentiment": sentiment_results,
        "topics": topic_results,
        "viewpoints": viewpoint_results,
        "quality": quality_results
    }

    # 步骤5：生成报告
    print("📊 步骤5：生成HTML报告...")
    report_generator = ReportGenerator()
    output_dir = Path.home() / "comment-analysis-reports"
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
    print("\n✅ 分析完成！\n")

if __name__ == "__main__":
    main()
