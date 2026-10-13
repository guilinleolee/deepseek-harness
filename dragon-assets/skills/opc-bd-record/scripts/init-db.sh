#!/usr/bin/env bash
# =============================================================================
# bd-record/scripts/init-db.sh - 初始化BD记录数据库
# 来源: xiaobei/TeamWiseFlow (OpenClaw)
# 融合: dragon-engine OPC增强
# 日期: 2026-08-17
# =============================================================================

set -euo pipefail

DB_DIR="db"
DB_FILE="$DB_DIR/bd_record.db"

# 创建数据库目录
mkdir -p "$DB_DIR"

# 创建数据库和表
sqlite3 "$DB_FILE" << 'EOF'
-- 创作者探索表
CREATE TABLE IF NOT EXISTS lead_creators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    creator_id TEXT NOT NULL,
    nickname TEXT,
    homepage_url TEXT NOT NULL,
    qualified INTEGER DEFAULT 0,
    notes TEXT,
    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    UNIQUE(platform, creator_id)
);

-- 帖子互动表
CREATE TABLE IF NOT EXISTS comment_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    post_title TEXT,
    post_url TEXT NOT NULL,
    strategy TEXT NOT NULL,
    replied INTEGER DEFAULT 0,
    reply_content TEXT,
    reply_target_id TEXT,
    created_at TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    UNIQUE(platform, post_url)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_creators_platform ON lead_creators(platform);
CREATE INDEX IF NOT EXISTS idx_creators_qualified ON lead_creators(qualified);
CREATE INDEX IF NOT EXISTS idx_posts_platform ON comment_posts(platform);
CREATE INDEX IF NOT EXISTS idx_posts_replied ON comment_posts(replied);
EOF

echo "✓ BD Record 数据库初始化完成: $DB_FILE"
echo ""
echo "表结构："
echo "  - lead_creators: 创作者探索记录"
echo "  - comment_posts: 帖子互动记录"
