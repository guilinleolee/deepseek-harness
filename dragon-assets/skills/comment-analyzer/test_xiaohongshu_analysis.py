#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试小红书评论分析
使用现有的评论数据测试分析系统
"""

import json
import sys
from pathlib import Path

# 添加scripts目录到路径
scripts_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(scripts_dir))

def test_sentiment_analysis():
    """测试情感分析模块"""
    from scripts.sentiment_analyzer import SentimentAnalyzer

    # 加载测试数据
    data_file = Path(r"e:\下载\xiaohongshu_comments_2026-01-18T02-49-48.json")
    if not data_file.exists():
        print(f"数据文件不存在: {data_file}")
        return None

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    comments = data.get("comments", [])
    print(f"✅ 加载了 {len(comments)} 条评论\n")

    # 创建情感分析器
    analyzer = SentimentAnalyzer()

    # 分析情感
    print("开始情感分析...")
    results = analyzer.analyze(comments)

    # 打印结果
    print("\n" + "="*60)
    print("情感分析结果")
    print("="*60)
    print(f"整体倾向: {results['overall']}")
    print(f"分布: {results['distribution']}")
    print(f"正面: {results['positive_count']} 条")
    print(f"中性: {results['neutral_count']} 条")
    print(f"负面: {results['negative_count']} 条")

    # 打印正面评论示例
    print("\n正面评论示例:")
    for comment in results['sentiments'][:3]:
        if comment['sentiment'] == '正面':
            print(f"  - {comment['content'][:50]}...")

    # 打印负面评论示例
    print("\n负面评论示例:")
    negative_count = 0
    for comment in results['sentiments']:
        if comment['sentiment'] == '负面' and negative_count < 3:
            print(f"  - {comment['content'][:50]}...")
            negative_count += 1

    return results

def test_topic_extraction():
    """测试话题提取模块"""
    from scripts.topic_extractor import TopicExtractor

    # 加载测试数据
    data_file = Path(r"e:\下载\xiaohongshu_comments_2026-01-18T02-49-48.json")
    if not data_file.exists():
        print(f"数据文件不存在: {data_file}")
        return None

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    comments = data.get("comments", [])

    # 创建话题提取器
    extractor = TopicExtractor()

    # 提取话题
    print("\n开始话题提取...")
    results = extractor.extract(comments)

    # 打印结果
    print("\n" + "="*60)
    print("话题提取结果")
    print("="*60)
    print(f"关键词数量: {len(results['keywords'])}")

    print("\nTOP10 关键词:")
    for i, keyword in enumerate(results['keywords'][:10], 1):
        print(f"  {i}. {keyword['word']} ({keyword['count']}次)")

    if results.get('topics'):
        print(f"\n主题数量: {len(results['topics'])}")
        print("主题聚类:")
        for topic in results['topics'][:5]:
            print(f"  - {topic['name']}: {topic['count']}条评论")

    return results

def main():
    """主测试函数"""
    print("="*60)
    print("小红书评论分析测试")
    print("="*60 + "\n")

    # 测试情感分析
    try:
        sentiment_results = test_sentiment_analysis()
    except Exception as e:
        print(f"情感分析测试失败: {e}")
        import traceback
        traceback.print_exc()
        sentiment_results = None

    # 测试话题提取
    try:
        topic_results = test_topic_extraction()
    except Exception as e:
        print(f"话题提取测试失败: {e}")
        import traceback
        traceback.print_exc()
        topic_results = None

    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    main()
