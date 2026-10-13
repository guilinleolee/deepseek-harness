#!/bin/bash
# =============================================================================
# Dragon Brain 更新脚本
# 用法: ./update-brain.sh [--project <id>] --field <path> --value <json_value>
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRAIN_DIR="${HOME}/.dragon-engine/projects"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }

# 解析参数
PROJECT_ID=""
FIELD=""
VALUE=""
OPERATION="set"

while [[ $# -gt 0 ]]; do
    case $1 in
        --project)
            PROJECT_ID="$2"
            shift 2
            ;;
        --field)
            FIELD="$2"
            shift 2
            ;;
        --value)
            VALUE="$2"
            shift 2
            ;;
        --append)
            OPERATION="append"
            shift
            ;;
        --delete)
            OPERATION="delete"
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# 获取当前项目
if [ -z "$PROJECT_ID" ]; then
    if [ -f "${HOME}/.dragon-engine/current_project" ]; then
        PROJECT_ID=$(cat "${HOME}/.dragon-engine/current_project")
    fi
fi

# 验证参数
if [ -z "$PROJECT_ID" ]; then
    log_error "未指定项目"
    echo "用法: ./update-brain.sh [--project <id>] --field <path> --value <json>"
    exit 1
fi

if [ -z "$FIELD" ]; then
    log_error "未指定字段"
    echo "用法: ./update-brain.sh --field <path> --value <json>"
    exit 1
fi

BRAIN_FILE="$BRAIN_DIR/$PROJECT_ID/brain.json"

if [ ! -f "$BRAIN_FILE" ]; then
    log_error "项目 Brain 不存在: $PROJECT_ID"
    exit 1
fi

# 检查 jq
if ! command -v jq &> /dev/null; then
    log_error "需要安装 jq"
    exit 1
fi

# 更新 Brain
TEMP_FILE=$(mktemp)
UPDATED_AT=$(date -u +%Y-%m-%dT%H:%M:%SZ)

case $OPERATION in
    set)
        if [ -z "$VALUE" ]; then
            log_error "未指定值"
            exit 1
        fi
        jq --argjson value "$VALUE" --arg updated "$UPDATED_AT" \
           ".$FIELD = \$value | .updated_at = \$updated" \
           "$BRAIN_FILE" > "$TEMP_FILE"
        ;;
    append)
        if [ -z "$VALUE" ]; then
            log_error "未指定追加值"
            exit 1
        fi
        jq --argjson value "$VALUE" --arg updated "$UPDATED_AT" \
           ".$FIELD += [\$value] | .updated_at = \$updated" \
           "$BRAIN_FILE" > "$TEMP_FILE"
        ;;
    delete)
        jq --arg updated "$UPDATED_AT" \
           "del(.$FIELD) | .updated_at = \$updated" \
           "$BRAIN_FILE" > "$TEMP_FILE"
        ;;
esac

# 验证并保存
if ! jq empty "$TEMP_FILE" 2>/dev/null; then
    log_error "更新后 JSON 格式错误"
    rm -f "$TEMP_FILE"
    exit 1
fi

mv "$TEMP_FILE" "$BRAIN_FILE"
log_info "Brain 已更新: $FIELD"

# 显示更新后的值
if [ -n "$VALUE" ]; then
    echo "  新值: $(echo "$VALUE" | jq -c . 2>/dev/null || echo "$VALUE")"
fi
