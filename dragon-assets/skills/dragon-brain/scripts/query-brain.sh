#!/bin/bash
# =============================================================================
# Dragon Brain 查询脚本
# 用法: ./query-brain.sh [--project <id>] [--field <path>] [--format <json|yaml|text>]
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
FORMAT="json"

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
        --format)
            FORMAT="$2"
            shift 2
            ;;
        *)
            if [ -z "$PROJECT_ID" ]; then
                PROJECT_ID="$1"
            fi
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

if [ -z "$PROJECT_ID" ]; then
    log_error "未指定项目且无当前项目"
    echo "用法: ./query-brain.sh [--project <id>] [--field <path>]"
    exit 1
fi

BRAIN_FILE="$BRAIN_DIR/$PROJECT_ID/brain.json"

if [ ! -f "$BRAIN_FILE" ]; then
    log_error "项目 Brain 不存在: $PROJECT_ID"
    echo "可用项目:"
    ls -1 "$BRAIN_DIR" 2>/dev/null | sed 's/^/  - /' || echo "  (无)"
    exit 1
fi

# 检查 jq
if ! command -v jq &> /dev/null; then
    log_error "需要安装 jq"
    echo "  apt install jq  # Debian/Ubuntu"
    echo "  brew install jq # macOS"
    exit 1
fi

# 执行查询
if [ -n "$FIELD" ]; then
    # 字段查询
    case $FORMAT in
        yaml)
            jq -r "$FIELD" "$BRAIN_FILE" 2>/dev/null | grep -v "^null$" || echo "(空)"
            ;;
        text)
            jq -r "$FIELD" "$BRAIN_FILE" 2>/dev/null | grep -v "^null$" || echo "(空)"
            ;;
        *)
            jq -r "$FIELD" "$BRAIN_FILE" 2>/dev/null
            ;;
    esac
else
    # 输出完整 Brain
    jq . "$BRAIN_FILE"
fi
