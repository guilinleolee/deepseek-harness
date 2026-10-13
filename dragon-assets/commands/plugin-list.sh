#!/bin/bash
# plugin-list.sh - 列出已安装的插件

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 显示帮助
show_help() {
  cat <<EOF
📋 Plugin List - 列出已安装的插件

用法:
  plugin-list [options]

选项:
  --verbose         显示详细信息
  --json            输出 JSON 格式
  --check-updates   检查更新

示例:
  # 列出所有插件
  plugin-list

  # 显示详细信息
  plugin-list --verbose

  # 输出 JSON 格式
  plugin-list --json

EOF
}

# 默认参数
VERBOSE=false
OUTPUT_FORMAT="table"
CHECK_UPDATES=false

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --verbose|-v)
      VERBOSE=true
      shift
      ;;
    --json)
      OUTPUT_FORMAT="json"
      shift
      ;;
    --check-updates)
      CHECK_UPDATES=true
      shift
      ;;
    --help|-h)
      show_help
      exit 0
      ;;
    *)
      echo -e "${RED}❌ 未知选项: $1${NC}"
      show_help
      exit 1
      ;;
  esac
done

PLUGIN_DIR="$HOME/.claude/.plugins/installed"

# 检查插件目录
if [ ! -d "$PLUGIN_DIR" ]; then
  echo -e "${YELLOW}⚠️  未安装任何插件${NC}"
  echo ""
  echo "使用 plugin-install 安装插件"
  exit 0
fi

# 统计
TOTAL_PLUGINS=$(ls -1 "$PLUGIN_DIR" 2>/dev/null | wc -l)

if [ "$TOTAL_PLUGINS" -eq 0 ]; then
  echo -e "${YELLOW}⚠️  未安装任何插件${NC}"
  exit 0
fi

# 输出格式
if [ "$OUTPUT_FORMAT" = "json" ]; then
  echo "["
  first=true
  for marker in "$PLUGIN_DIR"/*; do
    if [ -f "$marker" ]; then
      if [ "$first" = false ]; then
        echo ","
      fi
      first=false
      cat "$marker"
    fi
  done
  echo ""
  echo "]"
else
  # 表格输出
  echo -e "${BLUE}📋 已安装插件 ($TOTAL_PLUGINS)${NC}"
  echo ""
  printf "%-20s %-10s %-20s %-10s\n" "插件名称" "版本" "安装时间" "来源"
  echo "--------------------------------------------------------------------------------"

  for marker in "$PLUGIN_DIR"/*; do
    if [ -f "$marker" ] && command -v jq &> /dev/null; then
      NAME=$(jq -r '.name' "$marker")
      VERSION=$(jq -r '.version' "$marker")
      INSTALLED_AT=$(jq -r '.installed_at' "$marker" | cut -d'T' -f1)
      SOURCE=$(jq -r '.source' "$marker")

      # 格式化来源
      if [[ "$SOURCE" =~ ^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$ ]]; then
        SOURCE_DISPLAY="GitHub: $SOURCE"
      elif [ "$SOURCE" != "null" ]; then
        SOURCE_DISPLAY=$(basename "$SOURCE")
      else
        SOURCE_DISPLAY="local"
      fi

      printf "%-20s %-10s %-20s %-10s\n" "$NAME" "$VERSION" "$INSTALLED_AT" "$SOURCE_DISPLAY"

      # 详细信息
      if [ "$VERBOSE" = true ]; then
        echo "  来源: $SOURCE"
        echo "  配置: $marker"
        echo ""
      fi
    fi
  done

  echo ""
  echo -e "${BLUE}总计: $TOTAL_PLUGINS 个插件${NC}"
fi

# 检查更新
if [ "$CHECK_UPDATES" = true ]; then
  echo ""
  echo -e "${BLUE}🔄 检查更新...${NC}"

  for marker in "$PLUGIN_DIR"/*; do
    if [ -f "$marker" ] && command -v jq &> /dev/null; then
      SOURCE=$(jq -r '.source' "$marker")

      if [[ "$SOURCE" =~ ^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$ ]]; then
        REPO="https://github.com/$SOURCE"

        # 获取最新版本（从 GitHub releases）
        LATEST=$(git ls-remote --tags "$REPO" 2>/dev/null | tail -1 | sed 's/.*refs\/tags\///')

        if [ -n "$LATEST" ]; then
          CURRENT=$(jq -r '.version' "$marker")
          NAME=$(jq -r '.name' "$marker")

          if [ "$CURRENT" != "$LATEST" ]; then
            echo -e "${YELLOW}⬆️  $NAME: $CURRENT → $LATEST${NC}"
          else
            echo -e "${GREEN}✅ $NAME: 已是最新${NC}"
          fi
        fi
      fi
    fi
  done
fi
