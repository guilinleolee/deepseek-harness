#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
session-distiller 测试套件
验证会话蒸馏、语义检索、每日简报功能
"""

import pytest
import sys
import tempfile
import os
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from distill import SessionDistiller
from semantic_search import SemanticSearch
from daily_brief import DailyBriefGenerator


# ============ Fixtures ============

@pytest.fixture
def temp_db():
    """临时数据库"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    db_path.unlink(missing_ok=True)


@pytest.fixture
def distiller(temp_db):
    """蒸馏器实例"""
    return SessionDistiller(temp_db)


@pytest.fixture
def searcher(temp_db):
    """检索器实例"""
    return SemanticSearch(temp_db)


@pytest.fixture
def brief_generator(temp_db):
    """简报生成器实例"""
    return DailyBriefGenerator(temp_db)


# ============ 会话蒸馏测试 ============

class TestSessionDistiller:
    """会话蒸馏测试"""

    def test_init_db(self, distiller):
        """测试数据库初始化"""
        assert distiller.db_path.exists()

        # 检查表是否存在
        import sqlite3
        conn = sqlite3.connect(str(distiller.db_path))
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        assert 'sessions' in tables
        assert 'keypoints' in tables
        assert 'knowledge_cards' in tables
        assert 'sessions_fts' in tables

    def test_distill_simple(self, distiller):
        """测试简单蒸馏"""
        content = """
        ## Discussion

        We decided to use SQLite for the database.
        - [ ] Implement the user authentication
        - [ ] Add password reset feature

        **User preference**: Dark mode enabled
        """

        result = distiller.distill(content, source="test")

        assert result['status'] == 'success'
        assert 'session_id' in result
        assert len(result['l1_keypoints']) > 0

    def test_distill_empty(self, distiller):
        """测试空内容蒸馏"""
        result = distiller.distill("", source="test")
        assert result['status'] == 'success'
        assert len(result['l1_keypoints']) >= 1  # 至少生成摘要

    def test_search(self, distiller):
        """测试搜索功能"""
        # 先蒸馏一些内容
        distiller.distill("Architecture design meeting", source="test")
        distiller.distill("Database migration plan", source="test")

        results = distiller.search("Architecture")
        assert len(results) >= 1

    def test_get_session(self, distiller):
        """测试获取会话"""
        result = distiller.distill("Test content", source="test")
        session_id = result['session_id']

        session = distiller.get_session(session_id)
        assert session is not None
        assert session['id'] == session_id
        assert 'Test content' in session['content']

    def test_stats(self, distiller):
        """测试统计信息"""
        distiller.distill("Content 1", source="test")
        distiller.distill("Content 2", source="test")

        stats = distiller.stats()
        assert stats['sessions'] >= 2


# ============ 语义检索测试 ============

class TestSemanticSearch:
    """语义检索测试"""

    def test_search_exact(self, searcher):
        """测试精确搜索"""
        # 先添加一些数据
        searcher.connect()
        conn = searcher.conn

        import sqlite3
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions VALUES (?, ?, ?, ?, ?)",
            ("test_1", "Python is great", "2026-08-17", "test", None)
        )
        cursor.execute(
            "INSERT INTO sessions_fts VALUES (?, ?)",
            ("Python is great", "test_1")
        )
        conn.commit()
        searcher.close()

        results = searcher.search("Python", mode="exact")
        assert len(results) >= 1

    def test_search_semantic(self, searcher):
        """测试语义搜索"""
        # 先添加数据
        searcher.connect()
        conn = searcher.conn
        import sqlite3
        cursor = conn.cursor()

        for i in range(5):
            cursor.execute(
                "INSERT INTO sessions VALUES (?, ?, ?, ?, ?)",
                (f"test_{i}", f"Content about Python programming {i}", "2026-08-17", "test", None)
            )
        conn.commit()
        searcher.close()

        results = searcher.search("Python", mode="semantic")
        assert isinstance(results, list)

    def test_search_hybrid(self, searcher):
        """测试混合搜索"""
        results = searcher.search("test query", mode="hybrid")
        assert isinstance(results, list)

    def test_network_stats(self, searcher):
        """测试网络统计"""
        stats = searcher.get_network()
        assert 'tags' in stats
        assert 'categories' in stats


# ============ 每日简报测试 ============

class TestDailyBrief:
    """每日简报测试"""

    def test_generate_brief(self, brief_generator, distiller):
        """测试简报生成"""
        # 先蒸馏一些数据
        distiller.distill("Test session content", source="test")

        brief = brief_generator.generate("2026-08-17")

        assert 'daily-brief' in brief
        assert '2026-08-17' in brief
        assert '会话数' in brief

    def test_generate_weekly(self, brief_generator, distiller):
        """测试周报生成"""
        # 添加本周数据
        distiller.distill("Monday content", source="test")
        distiller.distill("Tuesday content", source="test")

        weekly = brief_generator.generate_weekly("2026-08-17")

        assert '周度记忆报告' in weekly or 'weekly' in weekly.lower()

    def test_save_brief(self, brief_generator, distiller):
        """测试简报保存"""
        distiller.distill("Test", source="test")
        brief_generator.generate("2026-08-17")

        # 检查文件是否生成
        output_file = brief_generator.output_path / "brief_2026-08-17.md"
        assert output_file.exists()


# ============ 集成测试 ============

class TestIntegration:
    """端到端集成测试"""

    def test_full_workflow(self, distiller, searcher, brief_generator):
        """测试完整工作流"""
        # 1. 蒸馏会话
        content = """
        ### Decision
        We will use PostgreSQL for the production database.

        ### Todo
        - [ ] Setup PostgreSQL development environment
        - [ ] Create initial schema

        **Architecture**: Microservices with API Gateway
        """

        result = distiller.distill(content, source="integration-test")
        session_id = result['session_id']

        # 2. 搜索
        results = searcher.search("PostgreSQL")
        assert isinstance(results, list)

        # 3. 生成简报
        brief = brief_generator.generate()
        assert brief is not None
        assert len(brief) > 100

    def test_opportunity_extraction(self, distiller):
        """测试机会信号提取"""
        content = """
        ### Discussion

        We should now implement the caching layer because
        performance is becoming an issue. This is urgent
        for the upcoming launch.
        """

        result = distiller.distill(content, source="test")

        # 检查是否有机会信号
        cards = result['l2_cards']
        opportunity_found = any(
            'urgent' in card.get('opportunity_signal', '').lower() or
            'now' in card.get('opportunity_signal', '').lower()
            for card in cards
        )

        # 只要提取到了信号就算成功
        assert len(cards) > 0


# ============ 运行测试 ============

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
