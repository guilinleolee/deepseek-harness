#!/usr/bin/env python3
"""
Dageno Bridge - 连接GEO Agent与Dageno API服务的桥接脚本
封装三层API调用，提供命令行接口

Usage:
    python dageno_bridge.py discover "RAG optimization" --limit 10
    python dageno_bridge.py fanouts <opportunity_id>
    python dageno_bridge.py citations <fanout_id> --limit 20
    python dageno_bridge.py workflow "LLM evaluation" --limit 5
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

# 添加父目录到路径以导入dageno_client
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "geo-content-generator" / "scripts"))

try:
    from dageno_client import DagenoClient
except ImportError:
    print("Warning: dageno_client not found, using mock mode")
    DagenoClient = None


# ============== 数据模型 ==============

@dataclass
class GeoOpportunity:
    """GEO机会数据模型"""
    opportunity_id: str
    topic: str
    query_volume: int
    opportunity_type: str
    fanouts: list = None

    def to_dict(self):
        d = asdict(self)
        d['fanouts'] = self.fanouts or []
        return d


@dataclass
class Fanout:
    """Fanout传播路径数据模型"""
    fanout_id: str
    platform: str
    title: str
    citation_count: int
    authority_score: float = 0.0

    def to_dict(self):
        return asdict(self)


@dataclass
class Citation:
    """引用数据模型"""
    citation_id: str
    url: str
    source_type: str
    authority_score: float
    context_snippet: str
    cited_by_count: int = 0

    def to_dict(self):
        return asdict(self)


# ============== Mock数据 ==============

def get_mock_opportunities(query: str, limit: int = 10) -> list:
    """生成Mock GEO机会数据"""
    mock_topics = [
        {"topic": "best AI models 2024", "query_volume": 45000, "type": "informational"},
        {"topic": "how do neural networks work", "query_volume": 38000, "type": "informational"},
        {"topic": "what is RAG", "query_volume": 32000, "type": "informational"},
        {"topic": "LLM evaluation metrics", "query_volume": 28000, "type": "comparison"},
        {"topic": "AI agent framework comparison", "query_volume": 25000, "type": "comparison"},
        {"topic": "transformer architecture explained", "query_volume": 22000, "type": "informational"},
        {"topic": "machine learning vs deep learning", "query_volume": 20000, "type": "comparison"},
        {"topic": "GPT-4 capabilities", "query_volume": 18000, "type": "informational"},
        {"topic": "vector database for AI", "query_volume": 15000, "type": "informational"},
        {"topic": "prompt engineering best practices", "query_volume": 12000, "type": "how-to"},
    ]

    opportunities = []
    for i, item in enumerate(mock_topics[:limit]):
        opp = GeoOpportunity(
            opportunity_id=f"op_mock_{i+1:03d}",
            topic=item["topic"],
            query_volume=item["query_volume"],
            opportunity_type=item["type"],
            fanouts=get_mock_fanouts(f"op_mock_{i+1:03d}")
        )
        opportunities.append(opp.to_dict())

    return opportunities


def get_mock_fanouts(opportunity_id: str) -> list:
    """生成Mock Fanout数据"""
    platforms = [
        {"platform": "academic_blog", "title": "Research Blog Analysis"},
        {"platform": "tech_community", "title": "Community Discussion"},
        {"platform": "product_docs", "title": "Official Documentation"},
        {"platform": "news_outlet", "title": "Industry News"},
    ]

    fanouts = []
    for i, pf in enumerate(platforms):
        fanout = Fanout(
            fanout_id=f"{opportunity_id}_fn_{i+1}",
            platform=pf["platform"],
            title=pf["title"],
            citation_count=25 - i * 4,
            authority_score=0.85 - i * 0.1
        )
        fanouts.append(fanout.to_dict())

    return fanouts


def get_mock_citations(fanout_id: str, limit: int = 20) -> list:
    """生成Mock引用数据"""
    sources = [
        {"type": "research_paper", "domain": "arxiv.org", "score": 0.92},
        {"type": "research_paper", "domain": "nature.com", "score": 0.95},
        {"type": "editorial", "domain": "forbes.com", "score": 0.78},
        {"type": "official", "domain": "github.com", "score": 0.82},
        {"type": "blog", "domain": "medium.com", "score": 0.65},
        {"type": "product_docs", "domain": "openai.com", "score": 0.88},
    ]

    citations = []
    for i in range(min(limit, 20)):
        src = sources[i % len(sources)]
        citation = Citation(
            citation_id=f"{fanout_id}_ct_{i+1}",
            url=f"https://{src['domain']}/article/{i+1}",
            source_type=src["type"],
            authority_score=src["score"],
            context_snippet=f"This study explores key findings about the topic in context {i+1}...",
            cited_by_count=150 - i * 7
        )
        citations.append(citation.to_dict())

    return citations


# ============== 桥接类 ==============

class DagenoBridge:
    """Dageno API桥接类"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.client = None
        self.mock_mode = True

        if DagenoClient and api_key:
            try:
                self.client = DagenoClient(api_key=api_key)
                self.mock_mode = False
            except Exception as e:
                print(f"Warning: Failed to initialize DagenoClient: {e}")
                self.mock_mode = True

    def discover_opportunities(self, query: str, limit: int = 10) -> list:
        """发现GEO机会"""
        if self.mock_mode:
            return get_mock_opportunities(query, limit)

        try:
            result = self.client.discover_opportunities(query, limit)
            return result.get('opportunities', [])
        except Exception as e:
            print(f"API Error: {e}, falling back to mock data")
            return get_mock_opportunities(query, limit)

    def get_fanouts(self, opportunity_id: str) -> list:
        """获取Fanout传播路径"""
        if self.mock_mode:
            return get_mock_fanouts(opportunity_id)

        try:
            result = self.client.get_fanouts(opportunity_id)
            return result.get('fanouts', [])
        except Exception as e:
            print(f"API Error: {e}, falling back to mock data")
            return get_mock_fanouts(opportunity_id)

    def get_citations(self, fanout_id: str, limit: int = 20) -> list:
        """获取引用数据"""
        if self.mock_mode:
            return get_mock_citations(fanout_id, limit)

        try:
            result = self.client.get_citations(fanout_id, limit)
            return result.get('citations', [])
        except Exception as e:
            print(f"API Error: {e}, falling back to mock data")
            return get_mock_citations(fanout_id, limit)

    def full_workflow(self, query: str, limit: int = 5) -> dict:
        """完整工作流：机会发现 → Fanout获取 → 引用获取"""
        result = {
            'query': query,
            'opportunities': [],
            'summary': {
                'total_opportunities': 0,
                'total_fanouts': 0,
                'total_citations': 0
            }
        }

        # Phase 1: 机会发现
        opportunities = self.discover_opportunities(query, limit)
        result['opportunities'] = opportunities
        result['summary']['total_opportunities'] = len(opportunities)

        # Phase 2 & 3: Fanout和引用获取
        for opp in opportunities:
            opp_id = opp['opportunity_id']
            fanouts = self.get_fanouts(opp_id)
            opp['fanouts'] = fanouts
            result['summary']['total_fanouts'] += len(fanouts)

            for fanout in fanouts[:2]:  # 每个机会只获取前2个Fanout的引用
                citations = self.get_citations(fanout['fanout_id'], limit=10)
                fanout['citations'] = citations
                result['summary']['total_citations'] += len(citations)

        return result


# ============== CLI接口 ==============

def cmd_discover(args):
    """机会发现命令"""
    bridge = DagenoBridge()
    opportunities = bridge.discover_opportunities(args.query, args.limit)

    if args.format == 'json':
        print(json.dumps(opportunities, ensure_ascii=False, indent=2))
    else:
        print(f"\n发现 {len(opportunities)} 个GEO机会:")
        print("=" * 60)
        for i, opp in enumerate(opportunities, 1):
            print(f"\n{i}. {opp['topic']}")
            print(f"   查询量: {opp['query_volume']:,}")
            print(f"   类型: {opp['opportunity_type']}")
            print(f"   ID: {opp['opportunity_id']}")
            if opp.get('fanouts'):
                print(f"   Fanouts: {len(opp['fanouts'])} 个")


def cmd_fanouts(args):
    """Fanout获取命令"""
    bridge = DagenoBridge()
    fanouts = bridge.get_fanouts(args.opportunity_id)

    if args.format == 'json':
        print(json.dumps(fanouts, ensure_ascii=False, indent=2))
    else:
        print(f"\n获取 {len(fanouts)} 个Fanout:")
        print("=" * 60)
        for i, fn in enumerate(fanouts, 1):
            print(f"\n{i}. [{fn['platform']}] {fn['title']}")
            print(f"   Fanout ID: {fn['fanout_id']}")
            print(f"   引用数: {fn['citation_count']}")
            print(f"   权威性: {fn['authority_score']:.2f}")


def cmd_citations(args):
    """引用获取命令"""
    bridge = DagenoBridge()
    citations = bridge.get_citations(args.fanout_id, args.limit)

    if args.format == 'json':
        print(json.dumps(citations, ensure_ascii=False, indent=2))
    else:
        print(f"\n获取 {len(citations)} 条引用:")
        print("=" * 60)
        for i, ct in enumerate(citations, 1):
            print(f"\n{i}. {ct['source_type']} - {ct['url'][:50]}...")
            print(f"   权威性: {ct['authority_score']:.2f}")
            print(f"   被引用: {ct['cited_by_count']} 次")
            print(f"   上下文: {ct['context_snippet'][:60]}...")


def cmd_workflow(args):
    """完整工作流命令"""
    bridge = DagenoBridge()
    result = bridge.full_workflow(args.query, args.limit)

    if args.format == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"\nGEO机会发现工作流结果:")
        print("=" * 60)
        print(f"查询: {result['query']}")
        print(f"\n统计:")
        print(f"  - 机会数: {result['summary']['total_opportunities']}")
        print(f"  - Fanout数: {result['summary']['total_fanouts']}")
        print(f"  - 引用数: {result['summary']['total_citations']}")

        print(f"\nTOP机会:")
        for i, opp in enumerate(result['opportunities'][:5], 1):
            print(f"\n{i}. {opp['topic']} ({opp['query_volume']:,} 查询)")


def main():
    parser = argparse.ArgumentParser(
        description="Dageno Bridge - GEO机会发现桥接工具",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # discover命令
    discover_parser = subparsers.add_parser('discover', help='发现GEO机会')
    discover_parser.add_argument('query', help='搜索查询')
    discover_parser.add_argument('--limit', type=int, default=10, help='返回数量')
    discover_parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')

    # fanouts命令
    fanouts_parser = subparsers.add_parser('fanouts', help='获取Fanout')
    fanouts_parser.add_argument('opportunity_id', help='机会ID')
    fanouts_parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')

    # citations命令
    citations_parser = subparsers.add_parser('citations', help='获取引用')
    citations_parser.add_argument('fanout_id', help='Fanout ID')
    citations_parser.add_argument('--limit', type=int, default=20, help='返回数量')
    citations_parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')

    # workflow命令
    workflow_parser = subparsers.add_parser('workflow', help='完整工作流')
    workflow_parser.add_argument('query', help='搜索查询')
    workflow_parser.add_argument('--limit', type=int, default=5, help='机会数量')
    workflow_parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')

    args = parser.parse_args()

    if args.command == 'discover':
        cmd_discover(args)
    elif args.command == 'fanouts':
        cmd_fanouts(args)
    elif args.command == 'citations':
        cmd_citations(args)
    elif args.command == 'workflow':
        cmd_workflow(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
