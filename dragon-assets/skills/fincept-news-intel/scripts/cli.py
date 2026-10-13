#!/usr/bin/env python3
"""
fincept-news-intel CLI

命令行接口，支持新闻搜索、情感分析、主题聚类、SEC 公告查询等功能。
"""

import argparse
import json
import sys
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from client import NewsIntelligence, NewsIntelError


def cmd_search(args):
    """新闻搜索命令"""
    intel = NewsIntelligence()

    news = intel.search(
        query=args.query,
        start_date=args.start_date,
        end_date=args.end_date,
        source=args.source,
        limit=args.limit
    )

    print(f"\n找到 {len(news)} 条新闻:\n")

    for i, article in enumerate(news[:args.limit], 1):
        print(f"{i}. {article['title']}")
        print(f"   来源: {article['source']} | 日期: {article['date']}")
        print(f"   摘要: {article['summary'][:150]}...")
        print()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(news, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {args.output}")


def cmd_sentiment(args):
    """情感分析命令"""
    intel = NewsIntelligence()

    if args.text:
        result = intel.sentiment(args.text)
        print(f"\n情感分析结果:")
        print(f"  情感: {result['label']}")
        print(f"  得分: {result['score']:.4f}")
        print(f"  置信度: {result['confidence']:.4f}")

    elif args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            news = json.load(f)

        texts = []
        for item in news:
            text = item.get("summary") or item.get("content") or item.get("title", "")
            texts.append(text)

        results = intel.batch_sentiment(news)

        total = len(results)
        positive = sum(1 for r in results if r["label"] == "positive")
        negative = sum(1 for r in results if r["label"] == "negative")
        neutral = sum(1 for r in results if r["label"] == "neutral")

        avg_score = sum(r["score"] for r in results) / total if total else 0

        print(f"\n批量情感分析结果 ({total} 条):")
        print(f"  正面: {positive} ({positive/total*100:.1f}%)")
        print(f"  负面: {negative} ({negative/total*100:.1f}%)")
        print(f"  中性: {neutral} ({neutral/total*100:.1f}%)")
        print(f"  平均得分: {avg_score:.4f}")

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"\n详细结果已保存到: {args.output}")


def cmd_cluster(args):
    """主题聚类命令"""
    intel = NewsIntelligence()

    with open(args.input, "r", encoding="utf-8") as f:
        news = json.load(f)

    clusters = intel.cluster(
        news,
        n_clusters=args.n_clusters,
        method=args.method
    )

    print(f"\n发现 {len(clusters)} 个主题:\n")

    for i, cluster in enumerate(clusters, 1):
        print(f"主题 {i}: {cluster['topic']}")
        print(f"  文章数: {cluster['size']}")
        print(f"  关键词: {', '.join(cluster['keywords'][:5])}")
        print()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(clusters, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {args.output}")


def cmd_correlate(args):
    """关联分析命令"""
    intel = NewsIntelligence()

    date_range = None
    if args.start_date and args.end_date:
        date_range = (args.start_date, args.end_date)

    result = intel.correlate(
        entity=args.entity,
        date_range=date_range
    )

    print(f"\n实体: {result['entity']}")
    print(f"相关实体: {', '.join(result['entities'])}")
    print(f"\n事件时间线 ({len(result['timeline'])} 个事件):")

    for event in result["timeline"][:args.limit]:
        print(f"  {event['date']} [{event['type']}] {event['description']}")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {args.output}")


def cmd_sec(args):
    """SEC 公告命令"""
    intel = NewsIntelligence()

    filings = intel.sec_filings(
        ticker=args.ticker,
        form_type=args.form_type,
        limit=args.limit
    )

    print(f"\n{args.ticker} SEC 公告 ({len(filings)} 条):\n")

    for i, filing in enumerate(filings, 1):
        print(f"{i}. [{filing['form_type']}] {filing['filing_date']}")
        print(f"   {filing['description']}")
        print(f"   {filing['url']}")
        print()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(filings, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {args.output}")


def cmd_earnings(args):
    """财报电话会命令"""
    intel = NewsIntelligence()

    result = intel.earnings_call(
        ticker=args.ticker,
        quarter=args.quarter
    )

    print(f"\n{result['ticker']} {result['quarter']} 财报电话会:")
    print(f"  日期: {result['date']}")
    print(f"  管理层语调: {result['mgmt_sentiment']}")
    print(f"\n关键指标:")

    for metric in result["highlights"]:
        print(f"  {metric['name']}: {metric['value']}")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存到: {args.output}")


def main():
    parser = argparse.ArgumentParser(
        description="fincept-news-intel - 新闻智能分析 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # search 命令
    search_parser = subparsers.add_parser("search", help="搜索新闻")
    search_parser.add_argument("query", help="搜索关键词")
    search_parser.add_argument("--start-date", help="开始日期 (YYYY-MM-DD)")
    search_parser.add_argument("--end-date", help="结束日期 (YYYY-MM-DD)")
    search_parser.add_argument("--source", default="all", help="新闻源")
    search_parser.add_argument("--limit", type=int, default=10, help="返回数量")
    search_parser.add_argument("--output", "-o", help="输出文件 (JSON)")

    # sentiment 命令
    sentiment_parser = subparsers.add_parser("sentiment", help="情感分析")
    sentiment_parser.add_argument("--text", "-t", help="分析文本")
    sentiment_parser.add_argument("--input", "-i", help="输入文件 (JSON, 新闻列表)")
    sentiment_parser.add_argument("--output", "-o", help="输出文件 (JSON)")

    # cluster 命令
    cluster_parser = subparsers.add_parser("cluster", help="主题聚类")
    cluster_parser.add_argument("--input", "-i", required=True, help="输入文件 (JSON, 新闻列表)")
    cluster_parser.add_argument("--n-clusters", "-n", type=int, default=5, help="聚类数量")
    cluster_parser.add_argument("--method", "-m", default="hdbscan", choices=["hdbscan", "kmeans"])
    cluster_parser.add_argument("--output", "-o", help="输出文件 (JSON)")

    # correlate 命令
    correlate_parser = subparsers.add_parser("correlate", help="关联分析")
    correlate_parser.add_argument("entity", help="实体名称")
    correlate_parser.add_argument("--start-date", help="开始日期 (YYYY-MM-DD)")
    correlate_parser.add_argument("--end-date", help="结束日期 (YYYY-MM-DD)")
    correlate_parser.add_argument("--limit", type=int, default=10, help="事件数量")
    correlate_parser.add_argument("--output", "-o", help="输出文件 (JSON)")

    # sec 命令
    sec_parser = subparsers.add_parser("sec", help="SEC 公告查询")
    sec_parser.add_argument("ticker", help="股票代码")
    sec_parser.add_argument("--form-type", "-f", help="表单类型 (8-K/10-K/10-Q/4)")
    sec_parser.add_argument("--limit", "-n", type=int, default=10, help="返回数量")
    sec_parser.add_argument("--output", "-o", help="输出文件 (JSON)")

    # earnings 命令
    earnings_parser = subparsers.add_parser("earnings", help="财报电话会查询")
    earnings_parser.add_argument("ticker", help="股票代码")
    earnings_parser.add_argument("--quarter", "-q", help="季度 (Q1-2024)")
    earnings_parser.add_argument("--output", "-o", help="输出文件 (JSON)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "search":
            cmd_search(args)
        elif args.command == "sentiment":
            cmd_sentiment(args)
        elif args.command == "cluster":
            cmd_cluster(args)
        elif args.command == "correlate":
            cmd_correlate(args)
        elif args.command == "sec":
            cmd_sec(args)
        elif args.command == "earnings":
            cmd_earnings(args)

    except NewsIntelError as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n已取消")
        return 130
    except Exception as e:
        print(f"未知错误: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
