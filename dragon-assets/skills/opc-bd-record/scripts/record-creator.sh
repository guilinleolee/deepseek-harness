#!/usr/bin/env bash
# =============================================================================
# bd-record/scripts/record-creator.sh - 记录创作者
# 来源: xiaobei/TeamWiseFlow (OpenClaw)
# 融合: dragon-engine OPC增强
# 日期: 2026-08-17
# =============================================================================

set -euo pipefail

PLATFORM=""
CREATOR_ID=""
NICKNAME=""
HOMEPAGE_URL=""
QUALIFIED="0"
NOTES=""

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --creator-id)
            CREATOR_ID="$2"
            shift 2
            ;;
        --nickname)
            NICKNAME="$2"
            shift 2
            ;;
        --homepage-url)
            HOMEPAGE_URL="$2"
            shift 2
            ;;
        --qualified)
            QUALIFIED="$2"
            shift 2
            ;;
        --notes)
            NOTES="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [[ -z "$PLATFORM" ]] || [[ -z "$CREATOR_ID" ]] || [[ -z "$HOMEPAGE_URL" ]]; then
    echo "Usage: $0 --platform <p> --creator-id <id> --homepage-url <url> [--nickname <n>] [--qualified 0|1] [--notes <notes>]"
    exit 1
fi

DB_FILE="db/bd_record.db"

# 确保数据库存在
if [[ ! -f "$DB_FILE" ]]; then
    bash "$(dirname "$0")/init-db.sh"
fi

# 插入或更新记录
RESULT=$(sqlite3 "$DB_FILE" "
INSERT INTO lead_creators (platform, creator_id, nickname, homepage_url, qualified, notes)
VALUES ('$PLATFORM', '$CREATOR_ID', '$NICKNAME', '$HOMEPAGE_URL', $QUALIFIED, '$NOTES')
ON CONFLICT(platform, creator_id) DO UPDATE SET
    nickname=excluded.nickname,
    homepage_url=excluded.homepage_url,
    qualified=excluded.qualified,
    notes=excluded.notes;
SELECT last_insert_rowid();
" 2>&1)

if [[ "$RESULT" =~ ^[0-9]+$ ]]; then
    echo "{\"ok\": true, \"id\": $RESULT}"
else
    echo "{\"ok\": false, \"error\": \"$RESULT\"}"
fi
