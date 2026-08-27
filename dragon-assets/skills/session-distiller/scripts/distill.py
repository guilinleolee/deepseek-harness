#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
session-distiller - 会话蒸馏核心脚本

将 AI 会话自动蒸馏为结构化笔记
灵感来源: BuilderPulse 信号提取逻辑
"""
import io
import sys

# 设置标准输出编码为 UTF-8 (只在非测试环境)
try:
    if hasattr(sys.stdout, 'buffer') and not sys.stdout.closed:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except Exception:
    pass

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ============ 配置 ============
DEFAULT_DB_PATH = Path.home() / ".claude" / "session-distiller" / "memory.db"
DEFAULT_OUTPUT_PATH = Path.home() / ".claude" / "session-distiller" / "notes"


class SessionDistiller:
    """会话蒸馏器核心类"""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # 原始会话表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                source TEXT,
                metadata TEXT
            )
        """)

        # L1 关键点表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS keypoints (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,  -- decision, todo, info
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)

        # L2 结构化知识表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_cards (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT,  -- JSON array
                source_session_id TEXT,
                opportunity_signal TEXT,  -- BuilderPulse 风格
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
        """)

        # L3 每日洞察表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_insights (
                id TEXT PRIMARY KEY,
                date TEXT NOT NULL UNIQUE,
                insights TEXT NOT NULL,  -- JSON array
                decisions TEXT,  -- JSON array
                opportunities TEXT,  -- JSON array
                created_at TEXT NOT NULL
            )
        """)

        # FTS5 全文索引
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS sessions_fts USING fts5(
                content,
                session_id UNINDEXED
            )
        """)

        conn.commit()
        conn.close()

    def distill(
        self,
        content: str,
        source: str = "manual",
        metadata: Optional[dict] = None
    ) -> dict:
        """
        蒸馏单个会话

        Args:
            content: 原始会话内容
            source: 来源标识
            metadata: 元数据

        Returns:
            蒸馏结果，包含 L1, L2, L3 结构
        """
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 1. 存储 L0 原始
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO sessions (id, content, created_at, source, metadata)
               VALUES (?, ?, ?, ?, ?)""",
            (session_id, content, datetime.now().isoformat(), source,
             json.dumps(metadata) if metadata else None)
        )

        # 更新 FTS 索引
        cursor.execute(
            "INSERT INTO sessions_fts (content, session_id) VALUES (?, ?)",
            (content, session_id)
        )

        # 2. 提取 L1 关键点 (简化版，实际应调用 LLM)
        keypoints = self._extract_keypoints(content)

        for kp in keypoints:
            kp_id = f"kp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{keypoints.index(kp)}"
            cursor.execute(
                """INSERT INTO keypoints
                   (id, session_id, content, category, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (kp_id, session_id, kp['content'], kp['category'], datetime.now().isoformat())
            )

        # 3. 生成 L2 知识卡片
        knowledge_cards = self._generate_knowledge_cards(content, keypoints, session_id)

        for card in knowledge_cards:
            card_id = f"card_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{knowledge_cards.index(card)}"
            cursor.execute(
                """INSERT INTO knowledge_cards
                   (id, title, content, tags, source_session_id, opportunity_signal, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (card_id, card['title'], card['content'],
                 json.dumps(card['tags']), session_id,
                 card.get('opportunity_signal', ''), datetime.now().isoformat())
            )

        conn.commit()
        conn.close()

        return {
            "session_id": session_id,
            "l1_keypoints": keypoints,
            "l2_cards": knowledge_cards,
            "status": "success"
        }

    def _extract_keypoints(self, content: str) -> list:
        """
        提取关键点 (简化实现)

        实际应调用 LLM 进行智能提取
        """
        keypoints = []

        # 简化规则提取 (演示用)
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检测决策 (以 - [决策] 或 Decision 开头)
            if line.startswith('### Decision') or '[决策]' in line:
                keypoints.append({
                    'category': 'decision',
                    'content': line.replace('### Decision', '').replace('[决策]', '').strip()
                })

            # 检测待办 (以 - [ ] 或 - [ ] 开头)
            elif line.startswith('- [ ]') or '- [ ]' in line:
                keypoints.append({
                    'category': 'todo',
                    'content': line.replace('- [ ]', '').replace('- [ ]', '').strip()
                })

            # 检测关键信息 (以 ** 开头)
            elif line.startswith('**') and ':' in line:
                keypoints.append({
                    'category': 'info',
                    'content': line.strip()
                })

        # 如果没有提取到，添加默认关键点
        if not keypoints:
            keypoints.append({
                'category': 'summary',
                'content': content[:200] + '...' if len(content) > 200 else content
            })

        return keypoints

    def _generate_knowledge_cards(
        self,
        content: str,
        keypoints: list,
        session_id: str
    ) -> list:
        """
        生成知识卡片 (BuilderPulse 风格)
        """
        cards = []

        # 基于关键点生成卡片
        decisions = [kp for kp in keypoints if kp['category'] == 'decision']
        todos = [kp for kp in keypoints if kp['category'] == 'todo']

        if decisions:
            card = {
                'title': '决策记录',
                'content': '\n'.join([d['content'] for d in decisions]),
                'tags': ['决策', '记录'],
                'opportunity_signal': self._extract_opportunity_signal(content)
            }
            cards.append(card)

        if todos:
            card = {
                'title': '待办追踪',
                'content': '\n'.join([t['content'] for t in todos]),
                'tags': ['待办', '追踪'],
                'opportunity_signal': ''
            }
            cards.append(card)

        # 生成整体摘要卡
        summary_card = {
            'title': '会话摘要',
            'content': content[:500] + '...' if len(content) > 500 else content,
            'tags': ['摘要', '会话'],
            'opportunity_signal': self._extract_opportunity_signal(content)
        }
        cards.append(summary_card)

        return cards

    def _extract_opportunity_signal(self, content: str) -> str:
        """
        提取机会信号 (BuilderPulse 核心逻辑)

        分析内容中的时效性信号和机会点
        """
        signals = []

        # 检测时间敏感词
        time_sensitive = ['现在', '当前', '最近', '紧急', '重要']
        for word in time_sensitive:
            if word in content:
                signals.append(f"时间敏感: {word}")

        # 检测机会词
        opportunity_words = ['机会', '改进', '优化', '新功能', '升级']
        for word in opportunity_words:
            if word in content:
                signals.append(f"机会: {word}")

        # 检测决策紧迫性
        decision_words = ['决定', '选择', '采用', '废弃']
        for word in decision_words:
            if word in content:
                signals.append(f"决策: {word}")

        if signals:
            return f"**信号**: {', '.join(signals)}"

        return "**信号**: 一般性会话"

    def search(self, query: str, limit: int = 10) -> list:
        """搜索记忆"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # FTS5 搜索
        cursor.execute(
            """SELECT session_id, content FROM sessions_fts
               WHERE sessions_fts MATCH ?
               LIMIT ?""",
            (query, limit)
        )

        results = []
        for row in cursor.fetchall():
            results.append({
                'session_id': row[0],
                'content': row[1][:200] + '...'
            })

        conn.close()
        return results

    def get_session(self, session_id: str) -> Optional[dict]:
        """获取会话详情"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM sessions WHERE id = ?",
            (session_id,)
        )
        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        # 获取关联关键点
        cursor.execute(
            "SELECT * FROM keypoints WHERE session_id = ?",
            (session_id,)
        )
        keypoints = [
            {'id': r[0], 'content': r[2], 'category': r[3]}
            for r in cursor.fetchall()
        ]

        # 获取关联知识卡片
        cursor.execute(
            "SELECT * FROM knowledge_cards WHERE source_session_id = ?",
            (session_id,)
        )
        cards = [
            {
                'id': r[0], 'title': r[1], 'content': r[2],
                'tags': json.loads(r[3]) if r[3] else []
            }
            for r in cursor.fetchall()
        ]

        conn.close()

        return {
            'id': row[0],
            'content': row[1],
            'created_at': row[2],
            'source': row[3],
            'metadata': json.loads(row[4]) if row[4] else None,
            'keypoints': keypoints,
            'cards': cards
        }

    def get_daily_insights(self, date: str = None) -> Optional[dict]:
        """获取每日洞察"""
        date = date or datetime.now().strftime('%Y-%m-%d')

        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM daily_insights WHERE date = ?",
            (date,)
        )
        row = cursor.fetchone()

        conn.close()

        if not row:
            return None

        return {
            'id': row[0],
            'date': row[1],
            'insights': json.loads(row[2]),
            'decisions': json.loads(row[3]) if row[3] else [],
            'opportunities': json.loads(row[4]) if row[4] else []
        }

    def stats(self) -> dict:
        """获取统计信息"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM sessions")
        session_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM keypoints")
        keypoint_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM knowledge_cards")
        card_count = cursor.fetchone()[0]

        conn.close()

        return {
            'sessions': session_count,
            'keypoints': keypoint_count,
            'knowledge_cards': card_count,
            'db_path': str(self.db_path)
        }


def main():
    parser = argparse.ArgumentParser(
        description="Session Distiller - 会话蒸馏器"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="初始化数据库"
    )
    parser.add_argument(
        "--input",
        help="输入文件路径"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="交互式输入"
    )
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="从剪贴板读取"
    )
    parser.add_argument(
        "--search",
        help="搜索关键词"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="显示统计信息"
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DEFAULT_DB_PATH,
        help="数据库路径"
    )

    args = parser.parse_args()

    distiller = SessionDistiller(args.db_path)

    if args.init:
        print("✅ 数据库初始化完成")
        return

    if args.stats:
        stats = distiller.stats()
        print("📊 记忆统计:")
        print(f"   会话数: {stats['sessions']}")
        print(f"   关键点数: {stats['keypoints']}")
        print(f"   知识卡片: {stats['knowledge_cards']}")
        print(f"   数据库: {stats['db_path']}")
        return

    if args.search:
        results = distiller.search(args.search)
        print(f"🔍 搜索 '{args.search}' 的结果:")
        for i, r in enumerate(results, 1):
            print(f"   {i}. {r['content'][:100]}...")
        return

    if args.interactive:
        print("📝 输入会话内容 (输入空行结束):")
        lines = []
        while True:
            try:
                line = input()
                if not line.strip():
                    break
                lines.append(line)
            except EOFError:
                break

        content = '\n'.join(lines)
        result = distiller.distill(content, source="interactive")
        print(f"\n✅ 蒸馏完成!")
        print(f"   Session ID: {result['session_id']}")
        print(f"   L1 关键点: {len(result['l1_keypoints'])}")
        print(f"   L2 卡片: {len(result['l2_cards'])}")
        return

    if args.input:
        path = Path(args.input)
        if not path.exists():
            print(f"❌ 文件不存在: {path}")
            sys.exit(1)

        content = path.read_text(encoding='utf-8')
        result = distiller.distill(content, source=str(path))
        print(f"✅ 蒸馏完成!")
        print(f"   Session ID: {result['session_id']}")
        print(f"   L1 关键点: {len(result['l1_keypoints'])}")
        print(f"   L2 卡片: {len(result['l2_cards'])}")
        return

    # 无参数时显示帮助
    parser.print_help()


if __name__ == "__main__":
    main()
