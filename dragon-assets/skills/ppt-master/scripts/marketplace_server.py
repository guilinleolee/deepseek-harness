#!/usr/bin/env python3
"""
PPT Template Marketplace MCP Server

模板市场MCP服务器 - 提供模板发布、发现、评分等功能
"""

import argparse
import hashlib
import json
import logging
import os
import shutil
import sqlite3
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional
import zipfile

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库路径
DB_PATH = Path(__file__).parent / "marketplace.db"
TEMPLATES_DIR = Path(__file__).parent / "templates"


class TemplateStatus(Enum):
    """模板状态"""
    DRAFT = "draft"           # 草稿
    PENDING = "pending"       # 待审核
    APPROVED = "approved"      # 已发布
    REJECTED = "rejected"    # 已拒绝
    ARCHIVED = "archived"     # 已归档


class TemplateType(Enum):
    """模板类型"""
    BRAND = "brand"
    LAYOUT = "layout"
    DECK = "deck"
    CHART = "chart"


@dataclass
class Template:
    """模板实体"""
    id: str
    name: str
    type: TemplateType
    summary: str
    description: str
    tags: list
    author: str
    status: TemplateStatus
    category: str
    thumbnail: Optional[str] = None
    downloads: int = 0
    rating: float = 0.0
    rating_count: int = 0
    created_at: str = ""
    updated_at: str = ""
    version: str = "1.0.0"
    file_path: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            **asdict(self),
            "type": self.type.value,
            "status": self.status.value
        }


class Database:
    """数据库管理"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 模板表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                summary TEXT,
                description TEXT,
                tags TEXT,
                author TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'draft',
                category TEXT,
                thumbnail TEXT,
                downloads INTEGER DEFAULT 0,
                rating REAL DEFAULT 0.0,
                rating_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                version TEXT DEFAULT '1.0.0',
                file_path TEXT,
                metadata TEXT
            )
        """)

        # 评分表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                id TEXT PRIMARY KEY,
                template_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                rating INTEGER NOT NULL,
                comment TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (template_id) REFERENCES templates(id)
            )
        """)

        # 收藏表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id TEXT PRIMARY KEY,
                template_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (template_id) REFERENCES templates(id)
            )
        """)

        # 用户表（简化版）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'user',
                created_at TEXT NOT NULL
            )
        """)

        # 索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_templates_type ON templates(type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_templates_status ON templates(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_templates_author ON templates(author)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_templates_category ON templates(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ratings_template ON ratings(template_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_favorites_user ON favorites(user_id)")

        conn.commit()
        conn.close()

    def get_connection(self):
        return sqlite3.connect(self.db_path)


class TemplateMarketplace:
    """模板市场核心类"""

    def __init__(self, db_path: Path, templates_dir: Path):
        self.db = Database(db_path)
        self.templates_dir = templates_dir
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    # ========== 发布相关 ==========

    def publish_template(
        self,
        name: str,
        type: TemplateType,
        summary: str,
        author: str,
        files: list,
        category: str = "general",
        tags: list = None,
        description: str = ""
    ) -> Template:
        """发布模板"""
        template_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        tags = tags or []

        # 创建模板目录
        template_dir = self.templates_dir / template_id
        template_dir.mkdir(parents=True, exist_ok=True)

        # 复制文件
        for file_path in files:
            src = Path(file_path)
            if src.exists():
                dst = template_dir / src.name
                if src.suffix == '.zip':
                    # 解压zip
                    with zipfile.ZipFile(src, 'r') as z:
                        z.extractall(template_dir)
                else:
                    shutil.copy2(src, dst)

        # 生成缩略图（取第一张图片）
        thumbnail = None
        for ext in ['.png', '.jpg', '.jpeg', '.svg']:
            thumb_files = list(template_dir.glob(f"*{ext}"))
            if thumb_files:
                thumbnail = str(thumb_files[0].relative_to(self.templates_dir))
                break

        # 提取颜色（从design_spec.md）
        colors = self._extract_colors(template_dir)

        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO templates
            (id, name, type, summary, description, tags, author, status, category,
             thumbnail, created_at, updated_at, file_path, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            template_id, name, type.value, summary, description,
            json.dumps(tags), author, TemplateStatus.PENDING.value,
            category, thumbnail, now, now, str(template_dir),
            json.dumps({"colors": colors})
        ))
        conn.commit()
        conn.close()

        return self.get_template(template_id)

    def _extract_colors(self, template_dir: Path) -> dict:
        """从design_spec提取颜色"""
        spec_file = template_dir / "design_spec.md"
        colors = {}

        if spec_file.exists():
            content = spec_file.read_text()
            # 简单提取 HEX 颜色
            import re
            hex_colors = re.findall(r'#[0-9A-Fa-f]{6}', content)
            if hex_colors:
                colors["primary"] = hex_colors[0]
                if len(hex_colors) > 1:
                    colors["secondary"] = hex_colors[1]
                if len(hex_colors) > 2:
                    colors["accent"] = hex_colors[2]

        return colors

    # ========== 查询相关 ==========

    def get_template(self, template_id: str) -> Optional[Template]:
        """获取模板"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM templates WHERE id = ?", (template_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_template(row)
        return None

    def list_templates(
        self,
        type: TemplateType = None,
        status: TemplateStatus = TemplateStatus.APPROVED,
        category: str = None,
        search: str = None,
        page: int = 1,
        page_size: int = 20
    ) -> list[Template]:
        """列出模板"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM templates WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status.value)

        if type:
            query += " AND type = ?"
            params.append(type.value)

        if category:
            query += " AND category = ?"
            params.append(category)

        if search:
            query += " AND (name LIKE ? OR summary LIKE ? OR tags LIKE ?)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern])

        query += " ORDER BY downloads DESC, rating DESC"
        query += f" LIMIT {page_size} OFFSET {(page-1) * page_size}"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_template(row) for row in rows]

    def _row_to_template(self, row: tuple) -> Template:
        """行转模板对象"""
        return Template(
            id=row[0],
            name=row[1],
            type=TemplateType(row[2]),
            summary=row[3] or "",
            description=row[4] or "",
            tags=json.loads(row[5]) if row[5] else [],
            author=row[6],
            status=TemplateStatus(row[7]),
            category=row[8] or "",
            thumbnail=row[9],
            downloads=row[10],
            rating=row[11],
            rating_count=row[12],
            created_at=row[13],
            updated_at=row[14],
            version=row[15] or "1.0.0",
            file_path=row[16],
            metadata=json.loads(row[17]) if row[17] else {}
        )

    # ========== 审核相关 ==========

    def approve_template(self, template_id: str, reviewer: str) -> bool:
        """审核通过"""
        return self._update_status(template_id, TemplateStatus.APPROVED)

    def reject_template(self, template_id: str, reviewer: str, reason: str) -> bool:
        """审核拒绝"""
        return self._update_status(template_id, TemplateStatus.REJECTED)

    def _update_status(self, template_id: str, status: TemplateStatus) -> bool:
        """更新状态"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE templates SET status = ?, updated_at = ? WHERE id = ?
        """, (status.value, now, template_id))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

    # ========== 评分相关 ==========

    def rate_template(
        self,
        template_id: str,
        user_id: str,
        rating: int,
        comment: str = ""
    ) -> bool:
        """评分"""
        if rating < 1 or rating > 5:
            return False

        rating_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conn = self.db.get_connection()
        cursor = conn.cursor()

        # 插入或更新评分
        cursor.execute("""
            INSERT OR REPLACE INTO ratings (id, template_id, user_id, rating, comment, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (rating_id, template_id, user_id, rating, comment, now))

        # 更新模板平均分
        cursor.execute("""
            SELECT AVG(rating), COUNT(*) FROM ratings WHERE template_id = ?
        """, (template_id,))
        avg_rating, count = cursor.fetchone()

        cursor.execute("""
            UPDATE templates SET rating = ?, rating_count = ? WHERE id = ?
        """, (avg_rating or 0, count, template_id))

        conn.commit()
        conn.close()
        return True

    def get_ratings(self, template_id: str) -> list:
        """获取评分列表"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM ratings WHERE template_id = ? ORDER BY created_at DESC
        """, (template_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    # ========== 收藏相关 ==========

    def favorite(self, template_id: str, user_id: str) -> bool:
        """收藏"""
        favorite_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO favorites (id, template_id, user_id, created_at)
                VALUES (?, ?, ?, ?)
            """, (favorite_id, template_id, user_id, now))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False  # 已收藏

    def unfavorite(self, template_id: str, user_id: str) -> bool:
        """取消收藏"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM favorites WHERE template_id = ? AND user_id = ?
        """, (template_id, user_id))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

    def get_favorites(self, user_id: str) -> list[Template]:
        """获取收藏列表"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.* FROM templates t
            JOIN favorites f ON t.id = f.template_id
            WHERE f.user_id = ?
            ORDER BY f.created_at DESC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_template(row) for row in rows]

    # ========== 下载相关 ==========

    def increment_downloads(self, template_id: str) -> bool:
        """增加下载数"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE templates SET downloads = downloads + 1 WHERE id = ?
        """, (template_id,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

    def download_template(self, template_id: str, user_id: str) -> Optional[Path]:
        """下载模板"""
        template = self.get_template(template_id)
        if not template or not template.file_path:
            return None

        # 增加下载计数
        self.increment_downloads(template_id)

        return Path(template.file_path)

    # ========== 统计相关 ==========

    def get_stats(self) -> dict:
        """获取统计数据"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM templates")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM templates WHERE status = ?",
                     (TemplateStatus.APPROVED.value,))
        published = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM templates WHERE status = ?",
                     (TemplateStatus.PENDING.value,))
        pending = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(downloads) FROM templates")
        total_downloads = cursor.fetchone()[0] or 0

        conn.close()

        return {
            "total_templates": total,
            "published_templates": published,
            "pending_templates": pending,
            "total_downloads": total_downloads
        }


# ========== MCP 工具函数 ==========

def tool_list_templates(args: dict) -> dict:
    """列出模板工具"""
    marketplace = TemplateMarketplace(DB_PATH, TEMPLATES_DIR)

    type_filter = None
    if args.get('type'):
        try:
            type_filter = TemplateType(args['type'])
        except ValueError:
            pass

    templates = marketplace.list_templates(
        type=type_filter,
        category=args.get('category'),
        search=args.get('search'),
        page=args.get('page', 1),
        page_size=args.get('page_size', 20)
    )

    return {
        "templates": [t.to_dict() for t in templates],
        "count": len(templates)
    }


def tool_publish_template(args: dict) -> dict:
    """发布模板工具"""
    marketplace = TemplateMarketplace(DB_PATH, TEMPLATES_DIR)

    template = marketplace.publish_template(
        name=args['name'],
        type=TemplateType(args['type']),
        summary=args.get('summary', ''),
        author=args['author'],
        files=args.get('files', []),
        category=args.get('category', 'general'),
        tags=args.get('tags', []),
        description=args.get('description', '')
    )

    return {
        "success": True,
        "template": template.to_dict()
    }


def tool_get_template(args: dict) -> dict:
    """获取模板详情"""
    marketplace = TemplateMarketplace(DB_PATH, TEMPLATES_DIR)
    template = marketplace.get_template(args['id'])

    if template:
        return {"template": template.to_dict()}
    return {"error": "Template not found"}


def tool_rate_template(args: dict) -> dict:
    """评分工具"""
    marketplace = TemplateMarketplace(DB_PATH, TEMPLATES_DIR)

    success = marketplace.rate_template(
        template_id=args['id'],
        user_id=args['user_id'],
        rating=args['rating'],
        comment=args.get('comment', '')
    )

    return {"success": success}


def tool_favorite(args: dict) -> dict:
    """收藏工具"""
    marketplace = TemplateMarketplace(DB_PATH, TEMPLATES_DIR)

    action = args.get('action', 'add')
    if action == 'add':
        success = marketplace.favorite(args['id'], args['user_id'])
    else:
        success = marketplace.unfavorite(args['id'], args['user_id'])

    return {"success": success}


def tool_stats() -> dict:
    """统计数据工具"""
    marketplace = TemplateMarketplace(DB_PATH, TEMPLATES_DIR)
    return marketplace.get_stats()


# MCP工具映射
TOOLS = {
    "list": tool_list_templates,
    "publish": tool_publish_template,
    "get": tool_get_template,
    "rate": tool_rate_template,
    "favorite": tool_favorite,
    "stats": tool_stats
}


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='PPT模板市场MCP服务器')
    parser.add_argument('command', choices=list(TOOLS.keys()))
    parser.add_argument('--args', type=str, help='JSON参数')

    args = parser.parse_args()

    # 解析参数
    params = {}
    if args.args:
        params = json.loads(args.args)

    # 执行命令
    result = TOOLS[args.command](params)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
