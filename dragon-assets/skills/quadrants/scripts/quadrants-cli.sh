#!/bin/bash
# Quadrants CLI — 天龙引擎 V8.17 集成版
# Usage: bash quadrants-cli.sh <action> [args...]

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

API_URL="${QUADRANTS_API_URL:-https://quadrants.ch}"
API_KEY="${QUADRANTS_API_KEY:-}"
SERVICE_ENDPOINT="${API_URL}/api/service"

if [ -z "$API_KEY" ]; then
  echo -e "${RED}Error: QUADRANTS_API_KEY not set${NC}"
  echo "Set it in TOOLS.md or export QUADRANTS_API_KEY=<key>"
  exit 1
fi

call_api() {
  local payload="$1"
  curl -s -X POST "$SERVICE_ENDPOINT" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: $API_KEY" \
    -d "$payload"
}

print_quadrant() {
  local urgency="$1"
  local importance="$2"

  if [ "$urgency" -gt 50 ] && [ "$importance" -gt 50 ]; then
    echo -e "${RED}Q1 立即执行${NC}"
  elif [ "$urgency" -le 50 ] && [ "$importance" -gt 50 ]; then
    echo -e "${YELLOW}Q2 计划安排${NC}"
  elif [ "$urgency" -gt 50 ] && [ "$importance" -le 50 ]; then
    echo -e "${BLUE}Q3 委托他人${NC}"
  else
    echo -e "${GREEN}Q4 删除放弃${NC}"
  fi
}

ACTION="${1:-help}"
shift || true

case "$ACTION" in
  projects)
    echo -e "${GREEN}📋 项目列表${NC}"
    call_api '{"action":"projects"}' | jq -r '.projects[] | "  • \(.name) (ID: \(.id))"' 2>/dev/null || call_api '{"action":"projects"}'
    ;;

  tasks)
    PROJECT_ID="${1:?Error: projectId required}"
    echo -e "${GREEN}📋 项目任务: $PROJECT_ID${NC}"
    call_api "{\"action\":\"tasks\",\"projectId\":\"$PROJECT_ID\"}"
    ;;

  priority)
    echo -e "${GREEN}🔥 优先任务 (Top 5)${NC}"
    echo -e "${GREEN}───────────────────────────────────────${NC}"
    call_api '{"action":"priority"}'
    ;;

  create)
    PROJECT_ID="${1:?Error: projectId required}"
    DESCRIPTION="${2:?Error: description required}"
    URGENCY="${3:-50}"
    IMPORTANCE="${4:-50}"
    echo -e "${YELLOW}📝 创建任务${NC}"
    echo "  描述: $DESCRIPTION"
    echo -n "  象限: "
    print_quadrant "$URGENCY" "$IMPORTANCE"
    call_api "{\"action\":\"create\",\"projectId\":\"$PROJECT_ID\",\"description\":$(echo "$DESCRIPTION" | jq -Rs .),\"urgency\":$URGENCY,\"importance\":$IMPORTANCE}"
    ;;

  bulk-create)
    PROJECT_ID="${1:?Error: projectId required}"
    TASKS_JSON="${2:?Error: tasks JSON required}"
    echo -e "${YELLOW}📝 批量创建任务${NC}"
    call_api "{\"action\":\"bulk-create\",\"projectId\":\"$PROJECT_ID\",\"tasks\":$TASKS_JSON}"
    ;;

  complete)
    TASK_ID="${1:?Error: taskId required}"
    echo -e "${GREEN}✅ 完成任务: $TASK_ID${NC}"
    call_api "{\"action\":\"complete\",\"taskId\":$TASK_ID}"
    ;;

  update)
    TASK_ID="${1:?Error: taskId required}"
    UPDATES="${2:?Error: updates JSON required}"
    echo -e "${BLUE}🔄 更新任务: $TASK_ID${NC}"
    call_api "{\"action\":\"update\",\"taskId\":$TASK_ID,\"updates\":$UPDATES}"
    ;;

  delete)
    TASK_ID="${1:?Error: taskId required}"
    echo -e "${RED}🗑️ 删除任务: $TASK_ID${NC}"
    call_api "{\"action\":\"delete\",\"taskId\":$TASK_ID}"
    ;;

  overview)
    PROJECT_ID="${1:?Error: projectId required}"
    echo -e "${GREEN}📊 项目概览: $PROJECT_ID${NC}"
    echo -e "${GREEN}───────────────────────────────────────${NC}"
    call_api "{\"action\":\"overview\",\"projectId\":\"$PROJECT_ID\"}"
    ;;

  help|*)
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}  Quadrants CLI (天龙引擎 V8.17)       ${NC}"
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo ""
    echo "用法: quadrants-cli.sh <action> [args...]"
    echo ""
    echo "命令:"
    echo "  projects                              列出所有项目"
    echo "  tasks <projectId>                     列出项目任务"
    echo "  priority                              优先任务 (Top 5)"
    echo "  create <projectId> <desc> [urg] [imp] 创建任务"
    echo "  bulk-create <projectId> <json>        批量创建"
    echo "  complete <taskId>                     完成任务"
    echo "  update <taskId> <json>                更新任务"
    echo "  delete <taskId>                       删除任务"
    echo "  overview <projectId>                  项目概览"
    echo ""
    echo "四象限分类:"
    echo -e "  ${RED}Q1 立即执行${NC}  紧急>50 & 重要>50"
    echo -e "  ${YELLOW}Q2 计划安排${NC}  紧急≤50 & 重要>50"
    echo -e "  ${BLUE}Q3 委托他人${NC}  紧急>50 & 重要≤50"
    echo -e "  ${GREEN}Q4 删除放弃${NC}  紧急≤50 & 重要≤50"
    echo ""
    echo "天龙岗位调用:"
    echo "  [@发布师] 使用 Quadrants 查看优先任务"
    echo "  [@09-02] 使用 Quadrants 创建任务"
    ;;
esac