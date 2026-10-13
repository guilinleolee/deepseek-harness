#!/usr/bin/env bash
# =============================================================================
# bd-record/scripts/check-creator.sh - 检查创作者是否已记录
# 来源: xiaobei/TeamWiseFlow (OpenClaw)
# 融合: dragon-engine OPC增强
# 日期: 2026-08-17
# =============================================================================

set -euo pipefail

PLATFORM=""
CREATOR_ID=""

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
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [[ -z "$PLATFORM" ]] || [[ -z "$CREATOR_ID" ]]; then
    echo "Usage: $0 --platform <platform> --creator-id <id>"
    exit 1
fi

DB_FILE="db/bd_record.db"

# 检查数据库是否存在
if [[ ! -f "$DB_FILE" ]]; then
    echo '{"exists": false}'
    exit 0
fi

# 查询
RESULT=$(sqlite3 -json "$DB_FILE" \
    "SELECT COUNT(*) as count FROM lead_creators WHERE platform='$PLATFORM' AND creator_id='$CREATOR_ID';" 2>/dev/null || echo '{"exists": false}')

if [[ -z "$RESULT" ]]; then
    echo '{"exists": false}'
    exit 0
fi

COUNT=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['count'] if d else 0)" 2>/dev/null || echo "0")

if [[ "$COUNT" -gt 0 ]]; then
    echo '{"exists": true}'
else
    echo '{"exists": false}'
fi
