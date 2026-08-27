#!/usr/bin/env python3
"""
Dageno Analyzer - GEO机会分析器
分析机会重要性、来源权威性、内容Gap、引用密度

Usage:
    python dageno_analyzer.py analyze <opportunity_id>
    python dageno_analyzer.py score --file opportunities.json
    python dageno_analyzer.py gaps --file report.json
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional, List
from datetime import datetime


# ============== 分析模型 ==============

@dataclass
class AuthorityMetrics:
    """权威性指标"""
    authority_score: float = 0.0
    citation_density: float = 0.0
    source_diversity: float = 0.0
    top_domain_ratio: float = 0.0


@dataclass
class OpportunityMetrics:
    """机会指标"""
    query_volume_score: float = 0.0
    competition_score: float = 0.0
    trending_score: float = 0.0
    authority_metrics: AuthorityMetrics = field(default_factory=AuthorityMetrics)


@dataclass
class ContentGap:
    """内容Gap"""
    gap_id: str
    topic: str
    importance: str  # high/medium/low
    description: str
    suggested_sources: List[str] = field(default_factory=list)


@dataclass
class OpportunityAnalysis:
    """机会分析结果"""
    opportunity_id: str
    topic: str
    overall_score: float = 0.0
    opportunity_metrics: OpportunityMetrics = field(default_factory=OpportunityMetrics)
    authority_analysis: AuthorityMetrics = field(default_factory=AuthorityMetrics)
    content_gaps: List[ContentGap] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    priority: str = "medium"  # high/medium/low
    estimated_effort: str = ""  # hours
    confidence: float = 0.0


# ============== 评分计算 ==============

class OpportunityScorer:
    """机会评分器"""

    # 权威域名权重
    AUTHORITY_DOMAINS = {
        'research': {
            'nature.com': 1.0, 'science.org': 1.0, 'arxiv.org': 0.9,
            'ieee.org': 0.9, 'acm.org': 0.9, 'pubmed.ncbi.nlm.nih.gov': 0.9,
        },
        'official': {
            'gov.cn': 1.0, 'who.int': 1.0, 'cdc.gov': 0.95,
            'nih.gov': 0.95, 'gov.uk': 0.95,
        },
        'editorial': {
            'forbes.com': 0.8, 'hbr.org': 0.85, 'economist.com': 0.85,
            'bloomberg.com': 0.8, 'techcrunch.com': 0.7,
        },
        'community': {
            'github.com': 0.75, 'stackoverflow.com': 0.6,
            'medium.com': 0.5, 'dev.to': 0.5,
        }
    }

    @classmethod
    def calculate_authority_score(cls, citations: List[dict]) -> AuthorityMetrics:
        """计算权威性指标"""
        if not citations:
            return AuthorityMetrics()

        metrics = AuthorityMetrics()

        # 1. 权威性得分 - 基于来源域名
        authority_weights = []
        for citation in citations:
            url = citation.get('url', '')
            score = 0.3  # 默认分数

            for domain_type, domains in cls.AUTHORITY_DOMAINS.items():
                for domain, weight in domains.items():
                    if domain in url:
                        score = max(score, weight)
                        break

            authority_weights.append(score)

        metrics.authority_score = sum(authority_weights) / len(authority_weights) if authority_weights else 0

        # 2. 引用密度 - 引用数/机会规模
        metrics.citation_density = len(citations) / max(
            sum(c.get('cited_by_count', 1) for c in citations), 1
        )

        # 3. 来源多样性 - 不同域名的比例
        domains = set()
        for c in citations:
            if 'url' in c:
                import re
                match = re.search(r'://([^/]+)', c['url'])
                if match:
                    domains.add(match.group(1))

        total_sources = len(citations)
        unique_domains = len(domains)
        metrics.source_diversity = unique_domains / total_sources if total_sources > 0 else 0

        # 4. 顶级域名比例
        top_domains = ['.org', '.edu', '.gov', '.int']
        top_count = sum(1 for c in citations if any(
            td in c.get('url', '') for td in top_domains
        ))
        metrics.top_domain_ratio = top_count / total_sources if total_sources > 0 else 0

        return metrics

    @classmethod
    def calculate_opportunity_score(cls, opportunity: dict, citations: List[dict]) -> OpportunityMetrics:
        """计算机会指标"""
        metrics = OpportunityMetrics()

        query_volume = opportunity.get('query_volume', 0)

        # 1. 查询量得分 - 归一化
        metrics.query_volume_score = min(query_volume / 50000, 1.0) * 100

        # 2. 竞争得分 - 基于引用密度
        citation_count = len(citations)
        if citation_count < 5:
            metrics.competition_score = 30  # 低竞争
        elif citation_count < 20:
            metrics.competition_score = 50  # 中等竞争
        else:
            metrics.competition_score = 70  # 高竞争

        # 3. 趋势得分 - 基于机会类型
        opp_type = opportunity.get('opportunity_type', '')
        type_trends = {
            'comparison': 80,  # 比较类最热
            'how-to': 70,
            'informational': 60,
            'definitional': 50,
        }
        metrics.trending_score = type_trends.get(opp_type, 50)

        # 4. 权威性指标
        metrics.authority_metrics = cls.calculate_authority_score(citations)

        return metrics

    @classmethod
    def calculate_overall_score(cls, opp_metrics: OpportunityMetrics, auth_metrics: AuthorityMetrics) -> float:
        """计算综合得分"""
        weights = {
            'query_volume': 0.20,
            'competition': 0.15,
            'trending': 0.15,
            'authority': 0.25,
            'citation_density': 0.15,
            'source_diversity': 0.10,
        }

        score = (
            opp_metrics.query_volume_score * weights['query_volume'] +
            opp_metrics.competition_score * weights['competition'] +
            opp_metrics.trending_score * weights['trending'] +
            auth_metrics.authority_score * 100 * weights['authority'] +
            auth_metrics.citation_density * 100 * weights['citation_density'] +
            auth_metrics.source_diversity * 100 * weights['source_diversity']
        )

        return round(score, 2)


# ============== Gap分析 ==============

class GapAnalyzer:
    """内容Gap分析器"""

    @classmethod
    def identify_gaps(cls, opportunity: dict, fanouts: List[dict], citations: List[dict]) -> List[ContentGap]:
        """识别内容Gap"""
        gaps = []
        gap_id_prefix = f"gap_{opportunity.get('opportunity_id', 'unknown')}"

        topic = opportunity.get('topic', '')
        existing_platforms = {f.get('platform', '') for f in fanouts}

        # 1. 平台Gap
        all_platforms = ['academic_blog', 'tech_community', 'product_docs', 'news_outlet',
                         'video_content', 'social_media', 'forum_discussion']
        missing_platforms = set(all_platforms) - existing_platforms

        if missing_platforms:
            gaps.append(ContentGap(
                gap_id=f"{gap_id_prefix}_platform",
                topic=f"{topic} - 平台覆盖",
                importance="high" if len(missing_platforms) > 3 else "medium",
                description=f"缺少{len(missing_platforms)}个平台的覆盖：{', '.join(missing_platforms)}",
                suggested_sources=["选择高权威性平台", "优先覆盖核心受众"]
            ))

        # 2. 来源Gap
        authority_domains = OpportunityScorer.AUTHORITY_DOMAINS
        covered_domains = set()
        for c in citations:
            url = c.get('url', '')
            for domain_type, domains in authority_domains.items():
                for domain in domains:
                    if domain in url:
                        covered_domains.add(domain_type)

        missing_types = set(authority_domains.keys()) - covered_domains
        if missing_types:
            type_names = {
                'research': '学术研究',
                'official': '官方来源',
                'editorial': '权威媒体',
                'community': '社区讨论'
            }
            gaps.append(ContentGap(
                gap_id=f"{gap_id_prefix}_source",
                topic=f"{topic} - 来源权威性",
                importance="high",
                description=f"缺少{len(missing_types)}类权威来源：{', '.join(type_names.get(t, t) for t in missing_types)}",
                suggested_sources=["添加学术论文引用", "补充官方文档", "引用权威媒体报道"]
            ))

        # 3. 深度Gap
        citation_count = len(citations)
        if citation_count < 10:
            gaps.append(ContentGap(
                gap_id=f"{gap_id_prefix}_depth",
                topic=f"{topic} - 内容深度",
                importance="medium",
                description=f"引用数量不足（{citation_count}个），建议增加更多来源以增强权威性",
                suggested_sources=["增加案例研究", "补充数据支撑", "添加专家观点"]
            ))

        # 4. 时效性Gap
        gaps.append(ContentGap(
            gap_id=f"{gap_id_prefix}_recency",
            topic=f"{topic} - 时效性",
            importance="medium",
            description="检查是否有最新发布的内容（近6个月）",
            suggested_sources=["搜索最新行业报告", "查找近期新闻", "更新统计数据"]
        ))

        return gaps


# ============== 分析器主类 ==============

class DagenoAnalyzer:
    """Dageno机会分析器"""

    def __init__(self, bridge=None):
        self.bridge = bridge
        self.scorer = OpportunityScorer()
        self.gap_analyzer = GapAnalyzer()

    def analyze_opportunity(self, opportunity: dict, fanouts: List[dict], citations: List[dict]) -> OpportunityAnalysis:
        """分析单个机会"""
        analysis = OpportunityAnalysis(
            opportunity_id=opportunity.get('opportunity_id', ''),
            topic=opportunity.get('topic', ''),
            confidence=0.8  # 基础置信度
        )

        # 计算指标
        opp_metrics = self.scorer.calculate_opportunity_score(opportunity, citations)
        auth_metrics = opp_metrics.authority_metrics

        analysis.opportunity_metrics = opp_metrics
        analysis.authority_analysis = auth_metrics

        # 计算综合得分
        analysis.overall_score = self.scorer.calculate_overall_score(opp_metrics, auth_metrics)

        # 识别Gap
        analysis.content_gaps = self.gap_analyzer.identify_gaps(opportunity, fanouts, citations)

        # 生成推荐
        analysis.recommendations = self._generate_recommendations(opportunity, opp_metrics, auth_metrics)

        # 确定优先级
        analysis.priority = self._determine_priority(analysis.overall_score, len(analysis.content_gaps))

        # 估算工作量
        analysis.estimated_effort = self._estimate_effort(analysis.priority, len(analysis.content_gaps))

        return analysis

    def analyze_full_workflow(self, workflow_result: dict) -> dict:
        """分析完整工作流结果"""
        results = {
            'query': workflow_result.get('query', ''),
            'total_opportunities': workflow_result['summary']['total_opportunities'],
            'analyses': [],
            'summary': {
                'high_priority': 0,
                'medium_priority': 0,
                'low_priority': 0,
                'avg_score': 0.0,
                'total_gaps': 0,
            }
        }

        total_score = 0.0

        for opp in workflow_result.get('opportunities', []):
            fanouts = opp.get('fanouts', [])
            citations = []
            for f in fanouts:
                citations.extend(f.get('citations', []))

            analysis = self.analyze_opportunity(opp, fanouts, citations)
            results['analyses'].append(analysis.to_dict() if hasattr(analysis, 'to_dict') else asdict(analysis))

            # 汇总
            priority = analysis.priority
            if priority == 'high':
                results['summary']['high_priority'] += 1
            elif priority == 'medium':
                results['summary']['medium_priority'] += 1
            else:
                results['summary']['low_priority'] += 1

            total_score += analysis.overall_score
            results['summary']['total_gaps'] += len(analysis.content_gaps)

        # 计算平均分
        opp_count = results['total_opportunities']
        results['summary']['avg_score'] = round(total_score / opp_count, 2) if opp_count > 0 else 0

        return results

    def _generate_recommendations(self, opportunity: dict, opp_metrics: OpportunityMetrics, auth_metrics: AuthorityMetrics) -> List[str]:
        """生成推荐"""
        recommendations = []
        topic = opportunity.get('topic', '')

        # 查询量推荐
        if opp_metrics.query_volume_score < 50:
            recommendations.append(f"查询量偏低({opp_metrics.query_volume_score:.0f}分)，考虑扩展相关关键词")

        # 竞争推荐
        if opp_metrics.competition_score < 40:
            recommendations.append("竞争较低，是切入的好时机，建议快速产出高质量内容")
        elif opp_metrics.competition_score > 60:
            recommendations.append("竞争激烈，需要差异化角度和高质量引用支撑")

        # 权威性推荐
        if auth_metrics.authority_score < 0.5:
            recommendations.append("来源权威性不足，建议增加学术/官方来源的比例")
        if auth_metrics.top_domain_ratio < 0.3:
            recommendations.append("顶级域名来源较少，考虑引用更多.org/.edu来源")

        # 来源多样性推荐
        if auth_metrics.source_diversity < 0.3:
            recommendations.append("来源多样性低，建议增加不同类型平台的引用")

        # 引用密度推荐
        if auth_metrics.citation_density < 0.01:
            recommendations.append("引用密度低，建议增加被广泛引用的权威来源")

        # 通用推荐
        recommendations.append(f"创作内容时嵌入[comparison]和[decision engine]元素")
        recommendations.append(f"添加[not ideal when]说明适用边界，增强说服力")

        return recommendations

    def _determine_priority(self, score: float, gap_count: int) -> str:
        """确定优先级"""
        if score >= 70 and gap_count <= 2:
            return "high"
        elif score >= 50 or gap_count <= 4:
            return "medium"
        else:
            return "low"

    def _estimate_effort(self, priority: str, gap_count: int) -> str:
        """估算工作量"""
        base_hours = {
            'high': 4,
            'medium': 3,
            'low': 2,
        }
        hours = base_hours.get(priority, 3) + gap_count * 0.5
        return f"{hours:.1f}小时"


# 添加to_dict方法
OpportunityAnalysis.to_dict = lambda self: {
    'opportunity_id': self.opportunity_id,
    'topic': self.topic,
    'overall_score': self.overall_score,
    'priority': self.priority,
    'estimated_effort': self.estimated_effort,
    'confidence': self.confidence,
    'opportunity_metrics': {
        'query_volume_score': self.opportunity_metrics.query_volume_score,
        'competition_score': self.opportunity_metrics.competition_score,
        'trending_score': self.opportunity_metrics.trending_score,
        'authority_metrics': asdict(self.opportunity_metrics.authority_metrics),
    },
    'authority_analysis': asdict(self.authority_analysis),
    'content_gaps': [asdict(g) for g in self.content_gaps],
    'recommendations': self.recommendations,
}


# ============== CLI接口 ==============

def cmd_analyze(args):
    """分析单个机会"""
    # 导入桥接器
    sys.path.insert(0, str(Path(__file__).parent))
    from dageno_bridge import DagenoBridge

    bridge = DagenoBridge()
    fanouts = bridge.get_fanouts(args.opportunity_id)

    # 收集所有引用
    citations = []
    for f in fanouts[:2]:  # 只分析前2个Fanout
        cits = bridge.get_citations(f['fanout_id'], limit=20)
        citations.extend(cits)

    # 模拟机会数据（实际应该从API获取）
    opportunity = {
        'opportunity_id': args.opportunity_id,
        'topic': f'分析主题 (ID: {args.opportunity_id})',
        'query_volume': 25000,
        'opportunity_type': 'comparison',
    }

    analyzer = DagenoAnalyzer(bridge)
    analysis = analyzer.analyze_opportunity(opportunity, fanouts, citations)

    if args.format == 'json':
        print(json.dumps(asdict(analysis), ensure_ascii=False, indent=2))
    else:
        print_report(analysis)


def cmd_score(args):
    """批量评分"""
    from dageno_bridge import DagenoBridge

    bridge = DagenoBridge()

    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        print("需要提供 --file 参数")
        sys.exit(1)

    if 'opportunities' in data:
        results = analyzer.analyze_full_workflow(data)
    else:
        print("无效的数据格式")
        sys.exit(1)

    if args.format == 'json':
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_full_report(results)


def cmd_gaps(args):
    """Gap分析"""
    from dageno_bridge import DagenoBridge

    bridge = DagenoBridge()
    analyzer = DagenoAnalyzer(bridge)

    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        print("需要提供 --file 参数")
        sys.exit(1)

    all_gaps = []
    for opp in data.get('opportunities', []):
        fanouts = opp.get('fanouts', [])
        citations = []
        for f in fanouts:
            citations.extend(f.get('citations', []))
        analysis = analyzer.analyze_opportunity(opp, fanouts, citations)
        all_gaps.extend(analysis.content_gaps)

    if args.format == 'json':
        print(json.dumps([asdict(g) for g in all_gaps], ensure_ascii=False, indent=2))
    else:
        print(f"\n发现 {len(all_gaps)} 个内容Gap:")
        print("=" * 60)
        for gap in all_gaps:
            priority_icon = "🔴" if gap.importance == "high" else "🟡" if gap.importance == "medium" else "🟢"
            print(f"\n{priority_icon} [{gap.importance.upper()}] {gap.topic}")
            print(f"   {gap.description}")
            if gap.suggested_sources:
                print(f"   建议: {', '.join(gap.suggested_sources[:2])}")


def print_report(analysis: OpportunityAnalysis):
    """打印分析报告"""
    print("\n" + "=" * 60)
    print(f"📊 GEO机会分析报告")
    print("=" * 60)

    priority_icon = "🔴" if analysis.priority == "high" else "🟡" if analysis.priority == "medium" else "🟢"
    print(f"\n{priority_icon} 优先级: {analysis.priority.upper()}")
    print(f"📈 综合得分: {analysis.overall_score:.1f}/100")
    print(f"⏱️  估算工时: {analysis.estimated_effort}")
    print(f"🎯 置信度: {analysis.confidence:.0%}")

    # 机会指标
    opp = analysis.opportunity_metrics
    print(f"\n📊 机会指标:")
    print(f"   查询量得分: {opp.query_volume_score:.1f}/100")
    print(f"   竞争程度: {opp.competition_score:.1f}/100")
    print(f"   趋势热度: {opp.trending_score:.1f}/100")

    # 权威性指标
    auth = analysis.authority_analysis
    print(f"\n📚 权威性分析:")
    print(f"   权威性得分: {auth.authority_score:.1f%}")
    print(f"   引用密度: {auth.citation_density:.4f}")
    print(f"   来源多样性: {auth.source_diversity:.1%}")
    print(f"   顶级域名占比: {auth.top_domain_ratio:.1%}")

    # 内容Gap
    if analysis.content_gaps:
        print(f"\n⚠️  内容Gap ({len(analysis.content_gaps)}个):")
        for gap in analysis.content_gaps:
            icon = "🔴" if gap.importance == "high" else "🟡"
            print(f"   {icon} {gap.topic}: {gap.description[:50]}...")

    # 推荐
    if analysis.recommendations:
        print(f"\n💡 建议:")
        for rec in analysis.recommendations[:3]:
            print(f"   • {rec}")

    print("\n" + "=" * 60)


def print_full_report(results: dict):
    """打印完整分析报告"""
    print("\n" + "=" * 60)
    print(f"📊 GEO机会批量分析报告")
    print("=" * 60)

    print(f"\n查询: {results['query']}")
    print(f"分析机会数: {results['total_opportunities']}")

    summary = results['summary']
    print(f"\n📈 统计汇总:")
    print(f"   🔴 高优先级: {summary['high_priority']}个")
    print(f"   🟡 中优先级: {summary['medium_priority']}个")
    print(f"   🟢 低优先级: {summary['low_priority']}个")
    print(f"   平均得分: {summary['avg_score']:.1f}")
    print(f"   总Gap数: {summary['total_gaps']}个")

    # TOP机会
    analyses = results['analyses']
    analyses.sort(key=lambda x: x['overall_score'], reverse=True)

    print(f"\n🏆 TOP 5 机会:")
    for i, a in enumerate(analyses[:5], 1):
        priority_icon = "🔴" if a['priority'] == "high" else "🟡"
        print(f"\n{i}. {priority_icon} {a['topic']}")
        print(f"   得分: {a['overall_score']:.1f} | 优先级: {a['priority']} | 工时: {a['estimated_effort']}")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Dageno Analyzer - GEO机会分析器")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # analyze命令
    analyze_parser = subparsers.add_parser('analyze', help='分析单个机会')
    analyze_parser.add_argument('opportunity_id', help='机会ID')
    analyze_parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')

    # score命令
    score_parser = subparsers.add_parser('score', help='批量评分')
    score_parser.add_argument('--file', required=True, help='工作流结果文件')
    score_parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')

    # gaps命令
    gaps_parser = subparsers.add_parser('gaps', help='Gap分析')
    gaps_parser.add_argument('--file', required=True, help='工作流结果文件')
    gaps_parser.add_argument('--format', choices=['text', 'json'], default='text', help='输出格式')

    args = parser.parse_args()

    if args.command == 'analyze':
        cmd_analyze(args)
    elif args.command == 'score':
        cmd_score(args)
    elif args.command == 'gaps':
        cmd_gaps(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
