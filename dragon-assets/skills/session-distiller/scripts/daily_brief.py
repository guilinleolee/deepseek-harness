#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io
import sys

# 设置标准输出编码为 UTF-8 (只在非测试环境)
try:
    if hasattr(sys.stdout, 'buffer') and not sys.stdout.closed:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except Exception:
    pass
"""
session-distiller - 每日简报生成器

BuilderPulse 风格的每日记忆简报
灵感来源: BuilderPulse 信号→机会 转化逻辑
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

# ============ 配置 ============
DEFAULT_DB_PATH = Path.home() / ".claude" / "session-distiller" / "memory.db"
DEFAULT_OUTPUT_PATH = Path.home() / ".claude" / "session-distiller" / "daily-briefs"


class DailyBriefGenerator:
    """每日简报生成器"""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.output_path = DEFAULT_OUTPUT_PATH
        self.output_path.mkdir(parents=True, exist_ok=True)

    def generate(
        self,
        date: str = None,
        push_to_obsidian: bool = False
    ) -> dict:
        """
        生成每日简报

        Args:
            date: 日期 (YYYY-MM-DD)，默认今天
            push_to_obsidian: 是否推送到 Obsidian

        Returns:
            简报内容
        """
        date = date or datetime.now().strftime('%Y-%m-%d')

        # 获取当日数据
        sessions = self._get_sessions(date)
        keypoints = self._get_keypoints(date)
        cards = self._get_knowledge_cards(date)

        # 生成洞察
        insights = self._generate_insights(sessions, keypoints, cards)

        # 生成简报
        brief = self._build_brief(
            date,
            sessions,
            keypoints,
            cards,
            insights
        )

        # 保存
        self._save_brief(date, brief)

        # 推送到 Obsidian
        if push_to_obsidian:
            self._push_to_obsidian(date, brief)

        return brief

    def _get_sessions(self, date: str) -> List[dict]:
        """获取指定日期的会话"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            """SELECT id, content, source, created_at FROM sessions
               WHERE date(created_at) = ?""",
            (date,)
        )

        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                'id': row[0],
                'content': row[1],
                'source': row[2],
                'created_at': row[3]
            })

        conn.close()
        return sessions

    def _get_keypoints(self, date: str) -> List[dict]:
        """获取指定日期的关键点"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            """SELECT id, content, category, created_at FROM keypoints
               WHERE date(created_at) = ?""",
            (date,)
        )

        keypoints = []
        for row in cursor.fetchall():
            keypoints.append({
                'id': row[0],
                'content': row[1],
                'category': row[2],
                'created_at': row[3]
            })

        conn.close()
        return keypoints

    def _get_knowledge_cards(self, date: str) -> List[dict]:
        """获取指定日期的知识卡片"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            """SELECT id, title, content, tags, opportunity_signal FROM knowledge_cards
               WHERE date(created_at) = ?""",
            (date,)
        )

        cards = []
        for row in cursor.fetchall():
            cards.append({
                'id': row[0],
                'title': row[1],
                'content': row[2],
                'tags': json.loads(row[3]) if row[3] else [],
                'opportunity_signal': row[4]
            })

        conn.close()
        return cards

    def _generate_insights(
        self,
        sessions: List[dict],
        keypoints: List[dict],
        cards: List[dict]
    ) -> dict:
        """
        生成洞察 (BuilderPulse 核心逻辑)

        信号 → 机会转化
        """
        insights = {
            'opportunities': [],
            'decisions': [],
            'pending_tasks': [],
            'signals': []
        }

        # 提取机会
        for card in cards:
            if card.get('opportunity_signal'):
                insights['opportunities'].append({
                    'title': card['title'],
                    'signal': card['opportunity_signal'],
                    'urgency': self._calculate_urgency(card['opportunity_signal'])
                })

        # 提取决策
        decisions = [kp for kp in keypoints if kp['category'] == 'decision']
        for d in decisions:
            insights['decisions'].append({
                'content': d['content'],
                'impact': self._estimate_impact(d['content'])
            })

        # 提取待办
        todos = [kp for kp in keypoints if kp['category'] == 'todo']
        insights['pending_tasks'] = [t['content'] for t in todos]

        # 提取信号
        for card in cards:
            if card.get('opportunity_signal'):
                insights['signals'].append(card['opportunity_signal'])

        # 按紧迫度排序
        insights['opportunities'].sort(
            key=lambda x: x['urgency'], reverse=True
        )

        return insights

    def _calculate_urgency(self, signal: str) -> float:
        """计算信号紧迫度"""
        urgency = 0.5  # 默认

        high_urgency = ['紧急', '立即', '马上', '现在', '当前', '重要']
        medium_urgency = ['应该', '建议', '考虑', '优化']

        for word in high_urgency:
            if word in signal:
                urgency += 0.3

        for word in medium_urgency:
            if word in signal:
                urgency += 0.15

        return min(urgency, 1.0)

    def _estimate_impact(self, content: str) -> str:
        """估计决策影响"""
        high_impact = ['架构', '设计', '重大', '核心']
        medium_impact = ['功能', '模块', '组件']

        for word in high_impact:
            if word in content:
                return '高'

        for word in medium_impact:
            if word in content:
                return '中'

        return '低'

    def _build_brief(
        self,
        date: str,
        sessions: List[dict],
        keypoints: List[dict],
        cards: List[dict],
        insights: dict
    ) -> str:
        """构建简报内容"""
        lines = []

        # Frontmatter
        lines.append('---')
        lines.append(f'type: daily-brief')
        lines.append(f'date: {date}')
        lines.append('generated_by: session-distiller v1.0')
        lines.append('---')
        lines.append('')

        # 标题
        lines.append(f'# 📊 天龙引擎 · 每日记忆简报')
        lines.append('')
        lines.append(f'**日期**: {date}')
        lines.append(f'**会话数**: {len(sessions)}')
        lines.append(f'**蒸馏笔记**: {len(cards)}')
        lines.append(f'**关键决策**: {len(insights["decisions"])}')
        lines.append('')
        lines.append('---')
        lines.append('')

        # 今日洞察
        lines.append('## 💡 今日洞察')
        lines.append('')

        # 机会发现
        if insights['opportunities']:
            lines.append('### 🎯 机会发现')
            for i, opp in enumerate(insights['opportunities'][:5], 1):
                urgency_emoji = '🔴' if opp['urgency'] > 0.7 else '🟡' if opp['urgency'] > 0.4 else '🟢'
                lines.append(f'{urgency_emoji} **{i}. {opp["title"]}**')
                lines.append(f'    - 信号: {opp["signal"]}')
                lines.append(f'    - 紧迫度: {opp["urgency"]:.0%}')
                lines.append('')
        else:
            lines.append('### 🎯 机会发现')
            lines.append('暂无高优先级机会')
            lines.append('')

        # 决策回顾
        if insights['decisions']:
            lines.append('### 📋 决策回顾')
            for i, decision in enumerate(insights['decisions'][:5], 1):
                impact = decision['impact']
                emoji = '🔴' if impact == '高' else '🟡' if impact == '中' else '🟢'
                lines.append(f'{emoji} {i}. {decision["content"]} (影响: {impact})')
            lines.append('')

        # 待办追踪
        if insights['pending_tasks']:
            lines.append('### 📝 待办追踪')
            for i, task in enumerate(insights['pending_tasks'][:5], 1):
                lines.append(f'- [ ] {i}. {task}')
            lines.append('')

        # 知识网络更新
        lines.append('## 🔗 知识网络更新')
        lines.append('')

        if cards:
            lines.append('### 新增卡片')
            for card in cards[:5]:
                tags_str = ', '.join([f'#{tag}' for tag in card.get('tags', [])])
                lines.append(f'- [[{card["title"]}]] {tags_str}')
            lines.append('')

        # 统计
        lines.append('## 📈 趋势分析')
        lines.append('')

        # 获取昨日数据对比
        yesterday = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
        yesterday_sessions = len(self._get_sessions(yesterday))
        yesterday_cards = len(self._get_knowledge_cards(yesterday))

        today_sessions = len(sessions)
        today_cards = len(cards)

        lines.append('| 指标 | 今日 | 昨日 | 变化 |')
        lines.append('|------|------|------|------|')

        change_sessions = self._calc_change(today_sessions, yesterday_sessions)
        lines.append(f'| 会话数 | {today_sessions} | {yesterday_sessions} | {change_sessions} |')

        change_cards = self._calc_change(today_cards, yesterday_cards)
        lines.append(f'| 知识卡片 | {today_cards} | {yesterday_cards} | {change_cards} |')

        efficiency = (today_cards / today_sessions * 100) if today_sessions > 0 else 0
        lines.append(f'| 蒸馏效率 | {efficiency:.0f}% | - | - |')
        lines.append('')

        # 信号摘要
        if insights['signals']:
            lines.append('## 📡 关键信号')
            lines.append('')
            seen_signals = set()
            for signal in insights['signals']:
                if signal not in seen_signals:
                    seen_signals.add(signal)
                    lines.append(f'- {signal}')
            lines.append('')

        # 底部
        lines.append('---')
        lines.append('')
        lines.append('*Generated by Session Distiller · BuilderPulse 灵感 · 天龙引擎 07记录师*')

        return '\n'.join(lines)

    def _calc_change(self, today: int, yesterday: int) -> str:
        """计算变化"""
        if yesterday == 0:
            return '🆕' if today > 0 else '-'
        change = (today - yesterday) / yesterday * 100
        if change > 0:
            return f'📈 +{change:.0f}%'
        elif change < 0:
            return f'📉 {change:.0f}%'
        return '-'

    def _save_brief(self, date: str, content: str):
        """保存简报"""
        output_file = self.output_path / f"brief_{date}.md"
        output_file.write_text(content, encoding='utf-8')
        print(f"✅ 简报已保存: {output_file}")

    def _push_to_obsidian(self, date: str, content: str):
        """
        推送到 Obsidian

        需要配置 OBSIDIAN_VAULT_PATH 环境变量
        """
        import os

        vault_path = os.environ.get('OBSIDIAN_VAULT_PATH')
        if not vault_path:
            print("⚠️ 未设置 OBSIDIAN_VAULT_PATH，跳过推送")
            return

        vault = Path(vault_path)
        daily_folder = vault / '50-Daily-Notes'

        if not daily_folder.exists():
            print(f"⚠️ Obsidian 目录不存在: {daily_folder}")
            return

        output_file = daily_folder / f"Session-Distiller-{date}.md"
        output_file.write_text(content, encoding='utf-8')
        print(f"✅ 已推送至 Obsidian: {output_file}")

    def generate_weekly(self, end_date: str = None) -> str:
        """生成周报"""
        end_date = end_date or datetime.now().strftime('%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        start_dt = end_dt - timedelta(days=7)

        lines = []
        lines.append('# 📊 天龙引擎 · 周度记忆报告')
        lines.append('')
        lines.append(f'**时间范围**: {start_dt.strftime("%Y-%m-%d")} ~ {end_date}')
        lines.append('')

        # 汇总每日数据
        daily_summaries = []
        for i in range(7):
            date = (start_dt + timedelta(days=i)).strftime('%Y-%m-%d')
            sessions = self._get_sessions(date)
            cards = self._get_knowledge_cards(date)
            keypoints = self._get_keypoints(date)

            daily_summaries.append({
                'date': date,
                'sessions': len(sessions),
                'cards': len(cards),
                'keypoints': len(keypoints),
                'decisions': len([kp for kp in keypoints if kp['category'] == 'decision'])
            })

        # 统计表格
        lines.append('## 📈 每日统计')
        lines.append('')
        lines.append('| 日期 | 会话 | 卡片 | 决策 |')
        lines.append('|------|------|------|------|')

        total_sessions = 0
        total_cards = 0
        total_decisions = 0

        for day in daily_summaries:
            lines.append(f"| {day['date']} | {day['sessions']} | {day['cards']} | {day['decisions']} |")
            total_sessions += day['sessions']
            total_cards += day['cards']
            total_decisions += day['decisions']

        lines.append('')
        lines.append(f'**总计**: 会话 {total_sessions} | 卡片 {total_cards} | 决策 {total_decisions}')
        lines.append('')

        # 本周亮点
        lines.append('## ✨ 本周亮点')
        lines.append('')

        # 获取本周所有卡片中的机会信号
        for i in range(7):
            date = (start_dt + timedelta(days=i)).strftime('%Y-%m-%d')
            cards = self._get_knowledge_cards(date)

            for card in cards:
                if card.get('opportunity_signal') and '紧急' in card['opportunity_signal']:
                    lines.append(f'- [{date}] {card["title"]}: {card["opportunity_signal"]}')

        lines.append('')
        lines.append('---')
        lines.append('')
        lines.append('*Generated by Session Distiller · 天龙引擎 07记录师*')

        content = '\n'.join(lines)

        # 保存
        week_start = start_dt.strftime('%Y%m%d')
        week_end = end_dt.strftime('%Y%m%d')
        output_file = self.output_path / f"weekly_{week_start}_{week_end}.md"
        output_file.write_text(content, encoding='utf-8')
        print(f"✅ 周报已保存: {output_file}")

        return content


def main():
    parser = argparse.ArgumentParser(
        description="Daily Brief - 每日简报生成器"
    )
    parser.add_argument(
        "--today",
        action="store_true",
        help="生成今日简报"
    )
    parser.add_argument(
        "--week",
        action="store_true",
        help="生成周报"
    )
    parser.add_argument(
        "--from",
        dest='from_date',
        help="开始日期 (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--to",
        dest='to_date',
        help="结束日期 (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="推送到 Obsidian"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="输出路径"
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help="数据库路径"
    )

    args = parser.parse_args()

    generator = DailyBriefGenerator(args.db_path)

    if args.week:
        generator.generate_weekly()
        return

    # 默认生成今日简报
    date = args.to_date or datetime.now().strftime('%Y-%m-%d')
    brief = generator.generate(date, push_to_obsidian=args.push)
    print(brief)


if __name__ == "__main__":
    main()
