#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
opportunity-scout - 机会分析脚本

分析信号，生成机会评分和推荐
灵感来源: BuilderPulse 信号→机会转化逻辑
"""
import io
import sys

# 设置标准输出编码为 UTF-8
try:
    if hasattr(sys.stdout, 'buffer') and not sys.stdout.closed:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except Exception:
    pass

import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# ============ 配置 ============
DEFAULT_SIGNALS_PATH = Path.home() / ".claude" / "opportunity-scout" / "signals"

# 评分权重
WEIGHTS = {
    'heat': 0.30,      # 热度
    'recency': 0.25,   # 时效性
    'cross': 0.20,     # 交叉验证
    'trend': 0.15,      # 趋势强度
    'signal': 0.10      # 信号强度
}

# 关键词配置
BOOST_KEYWORDS = ['AI', 'Agent', 'LLM', 'Memory', 'Claude', 'MCP', 'RAG',
                  'embedding', 'vector', 'workflow', 'automation', 'coding']
SUPPRESS_KEYWORDS = ['crypto', 'NFT', 'blockchain', 'gambling', 'casino']


class OpportunityAnalyzer:
    """机会分析器"""

    def __init__(self):
        self.opportunities = []

    def analyze(self, signals: List[Dict],
               boost_keywords: List[str] = None,
               suppress_keywords: List[str] = None,
               min_confidence: float = 0.0) -> List[Dict]:
        """
        分析信号，生成机会评分

        Args:
            signals: 信号列表
            boost_keywords: 加权关键词
            suppress_keywords: 抑制关键词
            min_confidence: 最小置信度

        Returns:
            机会列表
        """
        boost_keywords = boost_keywords or BOOST_KEYWORDS
        suppress_keywords = suppress_keywords or SUPPRESS_KEYWORDS

        print(f"📊 开始分析 {len(signals)} 条信号...")

        opportunities = []

        # 按来源分组（交叉验证）
        source_groups = {}
        for sig in signals:
            source = sig.get('source', 'Unknown')
            if source not in source_groups:
                source_groups[source] = []
            source_groups[source].append(sig)

        # 分析每个信号
        for sig in signals:
            # 基础评分
            heat_score = self._calc_heat_score(sig)
            recency_score = self._calc_recency_score(sig)
            signal_score = self._calc_signal_score(sig, boost_keywords, suppress_keywords)

            # 交叉验证分数（同标题跨平台）
            cross_score = self._calc_cross_score(sig, signals)

            # 趋势分数（检查是否快速增长）
            trend_score = self._calc_trend_score(sig)

            # 综合评分
            confidence = (
                WEIGHTS['heat'] * heat_score +
                WEIGHTS['recency'] * recency_score +
                WEIGHTS['cross'] * cross_score +
                WEIGHTS['trend'] * trend_score +
                WEIGHTS['signal'] * signal_score
            )

            # 过滤低置信度
            if confidence < min_confidence:
                continue

            # 生成机会
            opportunity = {
                'id': sig.get('id', ''),
                'title': sig.get('title', ''),
                'url': sig.get('url', ''),
                'source': sig.get('source', ''),
                'confidence': round(confidence, 3),
                'scores': {
                    'heat': round(heat_score, 3),
                    'recency': round(recency_score, 3),
                    'cross': round(cross_score, 3),
                    'trend': round(trend_score, 3),
                    'signal': round(signal_score, 3)
                },
                'urgency': self._calc_urgency(sig, boost_keywords),
                'action': self._generate_action(sig),
                'why_now': self._generate_why_now(sig),
                'keywords_matched': self._get_matched_keywords(sig, boost_keywords)
            }

            opportunities.append(opportunity)

        # 按置信度排序
        opportunities.sort(key=lambda x: x['confidence'], reverse=True)

        self.opportunities = opportunities
        print(f"✅ 分析完成: {len(opportunities)} 个高置信度机会")

        return opportunities

    def _calc_heat_score(self, sig: Dict) -> float:
        """计算热度分数"""
        score = sig.get('score', 0) or sig.get('stars', 0) or sig.get('votes', 0)

        # 归一化到 0-1
        if score >= 1000:
            return 1.0
        elif score >= 500:
            return 0.9
        elif score >= 200:
            return 0.7
        elif score >= 100:
            return 0.5
        elif score >= 50:
            return 0.3
        else:
            return score / 100

    def _calc_recency_score(self, sig: Dict) -> float:
        """计算时效性分数"""
        try:
            created_at = sig.get('created_at', '')
            if not created_at:
                return 0.5

            # 简单时间检查
            if isinstance(created_at, str):
                if 'hour' in created_at.lower() or '分钟' in created_at:
                    return 1.0
                elif 'day' in created_at.lower() or '天' in created_at:
                    return 0.7
                else:
                    return 0.3
            return 0.5
        except:
            return 0.5

    def _calc_signal_score(self, sig: Dict, boost: List[str], suppress: List[str]) -> float:
        """计算信号强度分数"""
        text = (sig.get('title', '') + ' ' + sig.get('description', '') + ' ' +
                sig.get('text', '')).lower()

        score = 0.5

        # 加权关键词命中
        for kw in boost:
            if kw.lower() in text:
                score += 0.15

        # 抑制关键词
        for kw in suppress:
            if kw.lower() in text:
                score -= 0.3

        return max(0, min(1, score))

    def _calc_cross_score(self, sig: Dict, signals: List[Dict]) -> float:
        """计算交叉验证分数（同标题跨平台）"""
        title = sig.get('title', '').lower()

        # 统计同标题在不同平台的出现次数
        sources = set()
        for s in signals:
            if s.get('title', '').lower() == title:
                sources.add(s.get('source', 'Unknown'))

        # 跨平台越多，分数越高
        count = len(sources)
        if count >= 3:
            return 1.0
        elif count == 2:
            return 0.7
        elif count == 1:
            return 0.3
        return 0.0

    def _calc_trend_score(self, sig: Dict) -> float:
        """计算趋势分数"""
        # 简化实现：检查评论数增长
        comments = sig.get('comments', 0) or 0
        score = sig.get('score', 0) or sig.get('stars', 0)

        if comments > score:
            return 0.9  # 高互动比
        return 0.5

    def _calc_urgency(self, sig: Dict, boost_keywords: List[str]) -> str:
        """计算紧迫度"""
        confidence = (
            WEIGHTS['heat'] * self._calc_heat_score(sig) +
            WEIGHTS['recency'] * self._calc_recency_score(sig) +
            WEIGHTS['cross'] * self._calc_cross_score(sig, [sig]) +
            WEIGHTS['trend'] * self._calc_trend_score(sig) +
            WEIGHTS['signal'] * self._calc_signal_score(sig, boost_keywords, [])
        )

        if confidence >= 0.8:
            return 'P0'
        elif confidence >= 0.6:
            return 'P1'
        elif confidence >= 0.4:
            return 'P2'
        return 'P3'

    def _generate_action(self, sig: Dict) -> str:
        """生成行动建议"""
        source = sig.get('source', '')

        if 'GitHub' in source:
            return f"⭐ Star + Fork + 深入研究实现细节"
        elif 'Hacker News' in source:
            return f"📰 阅读原文 + 在评论区了解更多信息"
        elif 'Product Hunt' in source:
            return f"🛍️ 试用产品 + 了解商业模式"
        return "🔍 深入调研"

    def _generate_why_now(self, sig: Dict) -> str:
        """生成为什么是现在"""
        title = sig.get('title', '').lower()

        # 关键词触发
        if any(kw.lower() in title for kw in BOOST_KEYWORDS):
            return "技术热点窗口期，先发优势明显"
        elif sig.get('score', 0) >= 500:
            return "热度快速上升，正在形成趋势"
        elif sig.get('comments', 0) >= 100:
            return "社区讨论活跃，需求被验证"
        return "值得关注的技术方向"

    def _get_matched_keywords(self, sig: Dict, keywords: List[str]) -> List[str]:
        """获取匹配的关键词"""
        text = (sig.get('title', '') + ' ' + sig.get('description', '')).lower()
        return [kw for kw in keywords if kw.lower() in text]

    def print_report(self, top: int = 10):
        """打印报告"""
        print()
        print("=" * 60)
        print("🎯 机会分析报告")
        print("=" * 60)

        if not self.opportunities:
            print("⚠️ 未发现高置信度机会")
            return

        print(f"\n发现 {len(self.opportunities)} 个机会 (显示 Top {top}):\n")

        for i, opp in enumerate(self.opportunities[:top], 1):
            urgency = opp['urgency']
            emoji = '🔴' if urgency == 'P0' else '🟡' if urgency == 'P1' else '🟢'

            print(f"{emoji} #{i} [{urgency}] {opp['title']}")
            print(f"   📊 置信度: {opp['confidence']:.1%}")
            print(f"   🔗 来源: {opp['source']}")
            print(f"   💡 {opp['why_now']}")
            if opp['keywords_matched']:
                print(f"   🏷️ 匹配: {', '.join(opp['keywords_matched'])}")
            print(f"   🚀 建议: {opp['action']}")
            print()

        # 统计
        print("-" * 60)
        print("📈 统计:")
        priority_counts = {'P0': 0, 'P1': 0, 'P2': 0, 'P3': 0}
        for opp in self.opportunities:
            priority_counts[opp['urgency']] = priority_counts.get(opp['urgency'], 0) + 1

        for p, count in priority_counts.items():
            if count > 0:
                print(f"   {p}: {count} 个")

    def save(self, output_path: Path = None) -> Path:
        """保存分析结果"""
        if not output_path:
            output_path = Path.home() / ".claude" / "opportunity-scout" / "opportunities"
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_path / f"opportunities_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'count': len(self.opportunities),
                'opportunities': self.opportunities
            }, f, ensure_ascii=False, indent=2)

        print(f"✅ 分析结果已保存: {output_file}")
        return output_file


def main():
    parser = argparse.ArgumentParser(description="Opportunity Analyzer - 机会分析")
    parser.add_argument("--input", type=Path, help="输入信号文件")
    parser.add_argument("--keywords", help="加权和键词 (逗号分隔)")
    parser.add_argument("--exclude", help="排除关键词 (逗号分隔)")
    parser.add_argument("--min-confidence", type=float, default=0.0,
                        help="最小置信度")
    parser.add_argument("--top", type=int, default=10, help="显示 Top N")
    parser.add_argument("--output", type=Path, help="输出路径")

    args = parser.parse_args()

    analyzer = OpportunityAnalyzer()

    # 加载信号
    if args.input and args.input.exists():
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
            signals = data.get('signals', data)
    else:
        # 使用默认路径的最新文件
        default_dir = DEFAULT_SIGNALS_PATH
        if default_dir.exists():
            files = sorted(default_dir.glob("signals_*.json"), reverse=True)
            if files:
                print(f"📂 使用最新信号文件: {files[0]}")
                with open(files[0], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    signals = data.get('signals', data)
            else:
                print("⚠️ 未找到信号文件，请先运行 scout.py")
                return
        else:
            print("⚠️ 未找到信号文件，请先运行 scout.py")
            return

    # 解析关键词
    boost = args.keywords.split(',') if args.keywords else None
    suppress = args.exclude.split(',') if args.exclude else None

    # 分析
    analyzer.analyze(
        signals,
        boost_keywords=boost,
        suppress_keywords=suppress,
        min_confidence=args.min_confidence
    )

    # 输出
    if analyzer.opportunities:
        analyzer.print_report(top=args.top)
        analyzer.save(args.output)


if __name__ == "__main__":
    main()
