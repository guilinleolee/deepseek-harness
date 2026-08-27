#!/bin/bash
# =============================================================================
# Dragon Brain 切换脚本
# 用法: ./switch-project.sh <project_id>
# =============================================================================

set -e

BRAIN_DIR="${HOME}/.dragon-engine/projects"
CURRENT_FILE="${HOME}/.dragon-engine/current_project"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }

PROJECT_ID="$1"

if [ -z "$PROJECT_ID" ]; then
    log_error "请提供项目 ID"
    echo "用法: ./switch-project.sh <project_id>"
    echo ""
    echo "可用项目:"
    ls -1 "$BRAIN_DIR" 2>/dev/null | sed 's/^/  - /' || echo "  (无)"
    exit 1
fi

BRAIN_FILE="$BRAIN_DIR/$PROJECT_ID/brain.json"

if [ ! -f "$BRAIN_FILE" ]; then
    log_error "项目不存在: $PROJECT_ID"
    echo ""
    echo "可用项目:"
    ls -1 "$BRAIN_DIR" 2>/dev/null | sed 's/^/  - /' || echo "  (无)"
    exit 1
fi

# 确保目录存在
mkdir -p "$(dirname "$CURRENT_FILE")"

# 写入当前项目
echo "$PROJECT_ID" > "$CURRENT_FILE"

# 获取项目名称显示
PROJECT_NAME=$(jq -r '.project_name // .project_id' "$BRAIN_FILE" 2>/dev/null)

log_info "已切换到项目: $PROJECT_NAME ($PROJECT_ID)"
