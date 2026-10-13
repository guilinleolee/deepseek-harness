#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
opportunity-scout - 每日简报生成脚本

生成 BuilderPulse 风格的每日机会简报
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
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# ============ 配置 ============
DEFAULT_OPPORTUNITIES_PATH = Path.home() / ".claude" / "opportunity-scout" / "opportunities"
DEFAULT_BRIEFS_PATH = Path.home() / ".claude" / "opportunity-scout" / "briefs"


class OpportunityBriefGenerator:
    """机会简报生成器"""

    def __init__(
        self,
        opportunities_path: Path = None,
        briefs_path: Path = None
    ):
        self.opportunities_path = opportunities_path or DEFAULT_OPPORTUNITIES_PATH
        self.briefs_path = briefs_path or DEFAULT_BRIEFS_PATH
        self.briefs_path.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        date: str = None,
        top: int = 20,
        push_to_obsidian: bool = False
    ) -> str:
        """
        生成每日机会简报

        Args:
            date: 日期 (YYYY-MM-DD)
            top: 显示的 Top 数量
            push_to_obsidian: 是否推送到 Obsidian

        Returns:
            简报内容
        """
        date = date or datetime.now().strftime('%Y-%m-%d')

        # 加载机会数据
        opportunities = self._load_opportunities()

        # 构建简报
        brief = self._build_brief(date, opportunities, top)

        # 保存
        self._save_brief(date, brief)

        # 推送到 Obsidian
        if push_to_obsidian:
            self._push_to_obsidian(date, brief)

        return brief

    def generate_weekly(self, end_date: str = None) -> str:
        """生成周报"""
        end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        start_dt = end_dt - timedelta(days=7)

        # 加载本周数据
        opportunities = self._load_opportunities(date_range=(start_dt, end_dt))

        # 构建周报
        brief = self._build_weekly_brief(start_dt, end_dt, opportunities)

        # 保存
        week_str = start_dt.strftime('%Y%m%d') + '_' + end_dt.strftime('%Y%m%d')
        output_file = self.briefs_path / f"weekly_{week_str}.md"
        output_file.write_text(brief, encoding='utf-8')
        print(f"✅ 周报已保存: {output_file}")

        return brief

    def _load_opportunities(self, date_range: tuple = None) -> List[Dict]:
        """加载机会数据"""
        if not self.opportunities_path.exists():
            return []

        files = sorted(
            self.opportunities_path.glob("opportunities_*.json"),
            reverse=True
        )

        opportunities = []
        for f in files[:5]:  # 加载最近 5 个文件
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    opportunities.extend(data.get('opportunities', []))
            except:
                continue

        # 去重
        seen = set()
        unique = []
        for opp in opportunities:
            if opp['id'] not in seen:
                seen.add(opp['id'])
                unique.append(opp)

        return unique

    def _build_brief(
        self,
        date: str,
        opportunities: List[Dict],
        top: int
    ) -> str:
        """构建简报"""
        lines = []

        # Frontmatter
        lines.append('---')
        lines.append('type: opportunity-brief')
        lines.append(f'date: {date}')
        lines.append('sources: Hacker News, GitHub Trending, Product Hunt')
        lines.append('confidence_threshold: 0.4')
        lines.append('generated_by: opportunity-scout v1.0')
        lines.append('---')
        lines.append('')

        # 标题
        lines.append('# 🎯 天龙引擎 · 每日机会简报')
        lines.append('')
        lines.append(f'**日期**: {date}')
        lines.append(f'**扫描时间**: {datetime.now().strftime("%H:%M")}')
        lines.append(f'**信号总数**: {len(opportunities)}')

        # 按优先级分组
        p0 = [o for o in opportunities if o.get('urgency') == 'P0']
        p1 = [o for o in opportunities if o.get('urgency') == 'P1']
        p2 = [o for o in opportunities if o.get('urgency') == 'P2']

        high_conf = [o for o in opportunities if o.get('confidence', 0) >= 0.6]
        lines.append(f'**高置信度机会**: {len(high_conf)}')
        lines.append('')
        lines.append('---')
        lines.append('')

        # P0 立即跟进
        if p0:
            lines.append('## 🔴 P0 立即跟进')
            lines.append('')
            for i, opp in enumerate(p0[:5], 1):
                lines.append(f'### {i}. {opp["title"]}')
                lines.append('')
                lines.append(f'- **置信度**: {opp["confidence"]:.0%}')
                lines.append(f'- **来源**: {opp["source"]}')
                lines.append(f'- **为什么现在**: {opp["why_now"]}')
                lines.append(f'- **行动建议**: {opp["action"]}')
                if opp.get('keywords_matched'):
                    lines.append(f'- **匹配关键词**: {", ".join(opp["keywords_matched"])}')
                lines.append(f'- **链接**: {opp["url"]}')
                lines.append('')

        # P1 本周跟进
        if p1:
            lines.append('## 🟡 P1 本周跟进')
            lines.append('')
            for i, opp in enumerate(p1[:5], 1):
                lines.append(f'### {i}. {opp["title"]}')
                lines.append('')
                lines.append(f'- **置信度**: {opp["confidence"]:.0%}')
                lines.append(f'- **来源**: {opp["source"]}')
                lines.append(f'- **为什么现在**: {opp["why_now"]}')
                lines.append('')

        # P2 观察
        if p2 and len(p2) > 10:
            lines.append('## 🟢 P2 持续观察')
            lines.append('')
            for opp in p2[:5]:
                lines.append(f'- {opp["title"]} ({opp["confidence"]:.0%})')
            if len(p2) > 5:
                lines.append(f'- ...还有 {len(p2) - 5} 个')
            lines.append('')

        # 关键词分布
        all_keywords = []
        for opp in opportunities:
            all_keywords.extend(opp.get('keywords_matched', []))

        if all_keywords:
            lines.append('## 🔥 热点关键词')
            lines.append('')
            from collections import Counter
            kw_counts = Counter(all_keywords).most_common(10)
            for kw, count in kw_counts:
                bar = '█' * count
                lines.append(f'{bar} {kw} ({count})')
            lines.append('')

        # 来源分布
        source_counts = {}
        for opp in opportunities:
            source = opp.get('source', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1

        if source_counts:
            lines.append('## 📊 信号来源分布')
            lines.append('')
            lines.append('| 平台 | 信号数 | 占比 |')
            lines.append('|------|--------|-------|')
            total = sum(source_counts.values())
            for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
                pct = count / total * 100
                lines.append(f'| {source} | {count} | {pct:.0f}% |')
            lines.append('')

        # 行动建议
        lines.append('## 🚀 本日行动建议')
        lines.append('')

        if p0:
            top_opp = p0[0]
            lines.append(f'1. **立即行动**: {top_opp["title"]} - {top_opp["action"]}')
            lines.append('')

        lines.append('2. 本周重点: 关注 AI Agent 和 LLM 相关项目')

        if high_conf:
            lines.append(f'3. 高置信度机会: {len(high_conf)} 个待深入调研')

        lines.append('')
        lines.append('---')
        lines.append('')
        lines.append('*Generated by Opportunity Scout · BuilderPulse 增强版 · 天龙引擎 01调研师*')

        return '\n'.join(lines)

    def _build_weekly_brief(
        self,
        start_dt: datetime,
        end_dt: datetime,
        opportunities: List[Dict]
    ) -> str:
        """构建周报"""
        lines = []

        start_str = start_dt.strftime('%Y-%m-%d')
        end_str = end_dt.strftime('%Y-%m-%d')

        # Frontmatter
        lines.append('---')
        lines.append('type: opportunity-weekly-brief')
        lines.append(f'date_range: {start_str} ~ {end_str}')
        lines.append('generated_by: opportunity-scout v1.0')
        lines.append('---')
        lines.append('')

        # 标题
        lines.append(f'# 📅 天龙引擎 · 周度机会报告')
        lines.append('')
        lines.append(f'**时间范围**: {start_str} ~ {end_str}')
        lines.append(f'**机会总数**: {len(opportunities)}')

        # 统计
        p0 = len([o for o in opportunities if o.get('urgency') == 'P0'])
        p1 = len([o for o in opportunities if o.get('urgency') == 'P1'])
        high_conf = len([o for o in opportunities if o.get('confidence', 0) >= 0.6])

        lines.append(f'**P0 立即**: {p0}')
        lines.append(f'**P1 本周**: {p1}')
        lines.append(f'**高置信度**: {high_conf}')
        lines.append('')
        lines.append('---')
        lines.append('')

        # Top 机会
        top_opps = sorted(opportunities, key=lambda x: x.get('confidence', 0), reverse=True)[:10]

        lines.append('## 🏆 Top 10 机会')
        lines.append('')

        for i, opp in enumerate(top_opps, 1):
            urgency = opp.get('urgency', 'P3')
            emoji = '🔴' if urgency == 'P0' else '🟡' if urgency == 'P1' else '🟢'

            lines.append(f'{emoji} {i}. **{opp["title"]}**')
            lines.append(f'   - 置信度: {opp["confidence"]:.0%} | 来源: {opp["source"]}')
            lines.append(f'   - {opp["why_now"]}')
            lines.append('')

        # 关键词趋势
        all_keywords = []
        for opp in opportunities:
            all_keywords.extend(opp.get('keywords_matched', []))

        if all_keywords:
            lines.append('## 📈 本周热点趋势')
            lines.append('')
            from collections import Counter
            kw_counts = Counter(all_keywords).most_common(15)
            for kw, count in kw_counts:
                bar = '█' * min(count, 20)
                lines.append(f'{bar} {kw} ({count})')
            lines.append('')

        # 来源汇总
        source_counts = {}
        for opp in opportunities:
            source = opp.get('source', 'Unknown')
            source_counts[source] = source_counts.get(source, 0) + 1

        if source_counts:
            lines.append('## 📊 来源分布')
            lines.append('')
            lines.append('| 平台 | 信号数 |')
            lines.append('|------|--------|')
            total = sum(source_counts.values())
            for source, count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True):
                lines.append(f'| {source} | {count} |')
            lines.append('')

        lines.append('---')
        lines.append('')
        lines.append('*Generated by Opportunity Scout · BuilderPulse 增强版 · 天龙引擎 01调研师*')

        return '\n'.join(lines)

    def _save_brief(self, date: str, content: str):
        """保存简报"""
        output_file = self.briefs_path / f"brief_{date}.md"
        output_file.write_text(content, encoding='utf-8')
        print(f"✅ 简报已保存: {output_file}")

    def _push_to_obsidian(self, date: str, content: str):
        """推送到 Obsidian"""
        import os

        vault_path = os.environ.get('OBSIDIAN_VAULT_PATH')
        if not vault_path:
            print("⚠️ 未设置 OBSIDIAN_VAULT_PATH，跳过推送")
            return

        vault = Path(vault_path)
        briefs_folder = vault / '50-Daily-Notes'

        if not briefs_folder.exists():
            print(f"⚠️ Obsidian 目录不存在: {briefs_folder}")
            return

        output_file = briefs_folder / f"Opportunity-Brief-{date}.md"
        output_file.write_text(content, encoding='utf-8')
        print(f"✅ 已推送至 Obsidian: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Opportunity Brief - 机会简报生成器")
    parser.add_argument("--today", action="store_true", help="生成今日简报")
    parser.add_argument("--week", action="store_true", help="生成周报")
    parser.add_argument("--date", help="指定日期 (YYYY-MM-DD)")
    parser.add_argument("--top", type=int, default=20, help="显示 Top N")
    parser.add_argument("--push", action="store_true", help="推送到 Obsidian")
    parser.add_argument("--summary", action="store_true", help="仅显示摘要")

    args = parser.parse_args()

    generator = OpportunityBriefGenerator()

    if args.week:
        brief = generator.generate_weekly(args.date)
    else:
        date = args.date or datetime.now().strftime('%Y-%m-%d')
        brief = generator.generate(date, top=args.top, push_to_obsidian=args.push)

    if args.summary:
        # 仅显示摘要
        lines = brief.split('\n')
        for line in lines[:30]:
            print(line)
    else:
        print(brief)


if __name__ == "__main__":
    main()
