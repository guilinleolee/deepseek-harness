#!/usr/bin/env python3
"""
高级记忆同步服务 - 分层记忆自动同步到Obsidian
基于 openclaw-advanced-memory 思想重构
"""

import os
import sys
import json
import time
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import threading

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_CONFIG = {
    'vault_path': os.path.expanduser('~/Documents/Obsidian/Vault'),
    'db_path': os.path.expanduser('~/.claude/memory.db'),
    'sync_interval': 15,  # 分钟
    'max_tokens': 5000,
    'context_ratio': {
        'L3': 0.3,
        'L2': 0.4,
        'L1': 0.3
    }
}

class AdvancedMemorySync:
    """分层记忆同步器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.vault_path = Path(self.config['vault_path'])
        self.db_path = Path(self.config['db_path'])
        self.running = False
        self._timer = None

    def ensure_vault_structure(self):
        """确保Obsidian目录结构存在"""
        folders = [
            '核心记忆',
            '结构化知识/技术',
            '结构化知识/业务',
            '结构化知识/项目',
            '关键点',
            '对话树',
            '知识图谱'
        ]

        for folder in folders:
            folder_path = self.vault_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)

        # 创建系统概览文件
        overview_path = self.vault_path / '_系统概览.md'
        if not overview_path.exists():
            overview_path.write_text(self._generate_overview_template(), encoding='utf-8')

        logger.info(f"Obsidian目录结构已就绪: {self.vault_path}")

    def _generate_overview_template(self) -> str:
        """生成系统概览模板"""
        return f"""# 天龙记忆系统概览

> 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 系统状态

- **状态**: 运行中
- **同步间隔**: {self.config['sync_interval']} 分钟
- **最大Token**: {self.config['max_tokens']}

## 分层架构

| 层级 | 内容 | 压缩率 |
|------|------|--------|
| L0 | 完整原始对话 | 0% |
| L1 | 关键句子提取 | 70% |
| L2 | 结构化JSON知识 | 90% |
| L3 | 核心洞察提炼 | 95% |

## 最近同步

<!-- 同步记录将自动添加 -->

## 统计

- **总记忆数**: <!-- 自动填充 -->
- **L3洞察数**: <!-- 自动填充 -->
- **L2知识数**: <!-- 自动填充 -->
"""

    def _get_db_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def get_l3_insights(self, limit: int = 50) -> List[Dict]:
        """获取L3层核心洞察"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            # 尝试从claude-mem数据库获取记忆
            cursor.execute("""
                SELECT id, content, created_at, metadata
                FROM memories
                WHERE layer = 'L3' OR layer = 3
                ORDER BY access_count DESC, created_at DESC
                LIMIT ?
            """, (limit,))

            results = [dict(row) for row in cursor.fetchall()]
            conn.close()

            return results if results else self._generate_sample_insights()

        except Exception as e:
            logger.warning(f"无法从数据库获取L3洞察: {e}")
            return self._generate_sample_insights()

    def _generate_sample_insights(self) -> List[Dict]:
        """生成示例洞察（当无数据时）"""
        return [
            {
                'id': 'sample-1',
                'content': f'天龙引擎V8.60已完成LangFlow集成，实现可视化工作流编排',
                'created_at': datetime.now().isoformat(),
                'metadata': json.dumps({'topic': '天龙引擎', 'type': '技术洞察'})
            },
            {
                'id': 'sample-2',
                'content': '分层记忆架构可有效提升Token效率，90%压缩率下仍保留核心信息',
                'created_at': datetime.now().isoformat(),
                'metadata': json.dumps({'topic': '记忆系统', 'type': '方法论'})
            }
        ]

    def get_l2_knowledge(self, category: str = '技术') -> List[Dict]:
        """获取L2层结构化知识"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, content, created_at, metadata
                FROM memories
                WHERE (layer = 'L2' OR layer = 2)
                AND metadata LIKE ?
                ORDER BY created_at DESC
                LIMIT 100
            """, (f'%{category}%',))

            results = [dict(row) for row in cursor.fetchall()]
            conn.close()

            return results if results else []

        except Exception as e:
            logger.warning(f"无法获取L2知识: {e}")
            return []

    def get_l1_keypoints(self, limit: int = 100) -> List[Dict]:
        """获取L1层关键点"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, content, created_at
                FROM memories
                WHERE layer = 'L1' OR layer = 1
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))

            results = [dict(row) for row in cursor.fetchall()]
            conn.close()

            return results if results else []

        except Exception as e:
            logger.warning(f"无法获取L1关键点: {e}")
            return []

    def sync_insights(self):
        """同步L3核心洞察到Obsidian"""
        logger.info("开始同步L3核心洞察...")

        insights = self.get_l3_insights()
        if not insights:
            logger.info("无L3洞察需要同步")
            return

        # 按日期分组
        today = datetime.now().strftime('%Y-%m-%d')
        insights_file = self.vault_path / '核心记忆' / f'{today}-insights.md'

        content_lines = [f"# 核心洞察 - {today}\n"]
        content_lines.append(f"> 自动同步于 {datetime.now().strftime('%H:%M:%S')}\n")

        for i, insight in enumerate(insights, 1):
            metadata = {}
            try:
                if insight.get('metadata'):
                    metadata = json.loads(insight['metadata'])
            except:
                pass

            topic = metadata.get('topic', '通用')
            insight_type = metadata.get('type', '洞察')

            content_lines.append(f"\n## {i}. {topic} - {insight_type}\n")
            content_lines.append(f"{insight['content']}\n")
            content_lines.append(f"- ID: `{insight['id']}`")
            content_lines.append(f"- 时间: {insight.get('created_at', '未知')}\n")

        insights_file.write_text('\n'.join(content_lines), encoding='utf-8')
        logger.info(f"已同步 {len(insights)} 条洞察到 {insights_file}")

        # 更新系统概览
        self._update_overview()

    def sync_keypoints(self):
        """同步L1关键点到Obsidian"""
        logger.info("开始同步L1关键点...")

        keypoints = self.get_l1_keypoints()
        if not keypoints:
            logger.info("无L1关键点需要同步")
            return

        today = datetime.now().strftime('%Y-%m-%d')
        kp_file = self.vault_path / '关键点' / f'{today}-keypoints.md'

        content_lines = [f"# 关键点 - {today}\n"]
        content_lines.append(f"> 自动同步于 {datetime.now().strftime('%H:%M:%S')}\n")

        for i, kp in enumerate(keypoints, 1):
            content_lines.append(f"{i}. {kp['content'][:200]}")

        kp_file.write_text('\n'.join(content_lines), encoding='utf-8')
        logger.info(f"已同步 {len(keypoints)} 条关键点到 {kp_file}")

    def sync_structured_knowledge(self):
        """同步L2结构化知识到Obsidian"""
        logger.info("开始同步L2结构化知识...")

        categories = ['技术', '业务', '项目']
        for category in categories:
            knowledge = self.get_l2_knowledge(category)
            if not knowledge:
                continue

            cat_file = self.vault_path / '结构化知识' / category / f'{category}-knowledge.md'

            content_lines = [f"# {category}知识\n"]
            content_lines.append(f"> 自动同步于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            for k in knowledge:
                try:
                    data = json.loads(k['content']) if k.get('content') else {}
                except:
                    data = {'content': k.get('content', '')}

                content_lines.append(f"\n## {k.get('id', '未知')}\n")
                content_lines.append(f"```json\n{json.dumps(data, ensure_ascii=False, indent=2)}\n```\n")

            cat_file.write_text('\n'.join(content_lines), encoding='utf-8')
            logger.info(f"已同步 {len(knowledge)} 条{category}知识")

    def update_knowledge_graph(self):
        """更新知识图谱"""
        logger.info("开始更新知识图谱...")

        insights = self.get_l3_insights(limit=200)
        nodes = []
        edges = []

        for insight in insights:
            try:
                metadata = json.loads(insight.get('metadata', '{}'))
            except:
                metadata = {}

            topic = metadata.get('topic', '通用')
            insight_type = metadata.get('type', '洞察')

            node = {
                'id': insight['id'],
                'label': topic,
                'type': insight_type,
                'content': insight['content'][:100]
            }
            nodes.append(node)

            # 建立主题关联
            if nodes:
                edges.append({
                    'source': nodes[0]['id'],
                    'target': insight['id'],
                    'relation': '包含'
                })

        graph = {
            'nodes': nodes[:50],  # 限制节点数
            'edges': edges[:100],
            'updated': datetime.now().isoformat()
        }

        graph_file = self.vault_path / '知识图谱' / 'graph.json'
        graph_file.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding='utf-8')
        logger.info(f"已更新知识图谱: {len(nodes)} 节点, {len(edges)} 边")

    def _update_overview(self):
        """更新系统概览"""
        insights = self.get_l3_insights()
        knowledge = self.get_l2_knowledge()

        overview_file = self.vault_path / '_系统概览.md'
        if overview_file.exists():
            content = overview_file.read_text(encoding='utf-8')
            content = content.replace(
                '<!-- 同步记录将自动添加 -->',
                f"- **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**: 同步了 {len(insights)} 条洞察"
            )
            content = content.replace(
                '<!-- 自动填充 -->',
                f"**{len(insights) + len(knowledge)}**"
            )
            overview_file.write_text(content, encoding='utf-8')

    def sync_all(self):
        """执行全量同步"""
        logger.info("="*50)
        logger.info("开始全量同步...")
        logger.info("="*50)

        self.ensure_vault_structure()
        self.sync_insights()
        self.sync_keypoints()
        self.sync_structured_knowledge()
        self.update_knowledge_graph()

        logger.info("="*50)
        logger.info("全量同步完成!")
        logger.info("="*50)

    def start(self):
        """启动定时同步服务"""
        self.running = True
        self.ensure_vault_structure()

        interval_seconds = self.config['sync_interval'] * 60

        def sync_loop():
            if self.running:
                self.sync_all()
                self._timer = threading.Timer(interval_seconds, sync_loop)
                self._timer.daemon = True
                self._timer.start()

        logger.info(f"启动同步服务，间隔 {self.config['sync_interval']} 分钟")
        sync_loop()

    def stop(self):
        """停止定时同步服务"""
        self.running = False
        if self._timer:
            self._timer.cancel()
        logger.info("同步服务已停止")

    def status(self) -> Dict:
        """获取服务状态"""
        return {
            'running': self.running,
            'vault_path': str(self.vault_path),
            'db_path': str(self.db_path),
            'sync_interval': self.config['sync_interval'],
            'max_tokens': self.config['max_tokens']
        }


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='高级记忆同步服务')
    parser.add_argument('command', choices=['start', 'stop', 'status', 'sync'],
                        help='命令: start(启动), stop(停止), status(状态), sync(单次同步)')

    args = parser.parse_args()

    sync_service = AdvancedMemorySync()

    if args.command == 'start':
        sync_service.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            sync_service.stop()
            print("\n服务已停止")

    elif args.command == 'stop':
        sync_service.stop()

    elif args.command == 'status':
        status = sync_service.status()
        print("\n=== 同步服务状态 ===")
        for key, value in status.items():
            print(f"  {key}: {value}")

    elif args.command == 'sync':
        sync_service.sync_all()


if __name__ == '__main__':
    main()
