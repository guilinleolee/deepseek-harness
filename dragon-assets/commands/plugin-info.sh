#!/bin/bash
# plugin-info.sh - 查看插件详细信息

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
📖 Plugin Info - 查看插件详细信息

用法:
  plugin-info <plugin-name>

参数:
  plugin-name      插件名称

选项:
  --target <dir>    Claude 目录（默认: ~/.claude）
  --json           输出 JSON 格式

示例:
  # 查看插件信息
  plugin-info nine-dragons-core

  # 输出 JSON 格式
  plugin-info --json nine-dragons-core

EOF
}

# 默认参数
TARGET_DIR="$HOME/.claude"
OUTPUT_FORMAT="table"

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --target)
      TARGET_DIR="$2"
      shift 2
      ;;
    --json)
      OUTPUT_FORMAT="json"
      shift
      ;;
    --help|-h)
      show_help
      exit 0
      ;;
    -*)
      echo -e "${RED}❌ 未知选项: $1${NC}"
      show_help
      exit 1
      ;;
    *)
      PLUGIN_NAME="$1"
      shift
      ;;
  esac
done

# 检查参数
if [ -z "$PLUGIN_NAME" ]; then
  echo -e "${RED}❌ 缺少插件名称${NC}"
  show_help
  exit 1
fi

PLUGIN_MARKER="$TARGET_DIR/.plugins/installed/$PLUGIN_NAME"

# 检查插件是否已安装
if [ ! -f "$PLUGIN_MARKER" ]; then
  echo -e "${RED}❌ 插件未安装: $PLUGIN_NAME${NC}"
  exit 1
fi

# 读取安装信息
if command -v jq &> /dev/null; then
  INSTALL_INFO=$(cat "$PLUGIN_MARKER")
  PLUGIN_NAME=$(jq -r '.name' "$PLUGIN_MARKER")
  PLUGIN_VERSION=$(jq -r '.version' "$PLUGIN_MARKER")
  INSTALLED_AT=$(jq -r '.installed_at' "$PLUGIN_MARKER")
  SOURCE=$(jq -r '.source' "$PLUGIN_MARKER")
else
  PLUGIN_NAME=$(grep '"name"' "$PLUGIN_MARKER" | sed 's/.*"\([^"]*\)".*/\1/')
  PLUGIN_VERSION=$(grep '"version"' "$PLUGIN_MARKER" | sed 's/.*"\([^"]*\)".*/\1/')
  INSTALLED_AT=$(grep '"installed_at"' "$PLUGIN_MARKER" | sed 's/.*"\([^"]*\)".*/\1/')
  SOURCE=$(grep '"source"' "$PLUGIN_MARKER" | sed 's/.*"\([^"]*\)".*/\1/')
fi

# 获取插件配置
PLUGIN_CONFIG=""
if [[ "$SOURCE" =~ ^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$ ]]; then
  # GitHub 仓库
  TEMP_DIR=$(mktemp -d)
  trap "rm -rf $TEMP_DIR" EXIT

  git clone --depth 1 "https://github.com/$SOURCE.git" "$TEMP_DIR/plugin" 2>/dev/null || true

  if [ -f "$TEMP_DIR/plugin/plugin.json" ]; then
    PLUGIN_CONFIG="$TEMP_DIR/plugin/plugin.json"
  fi
fi

# 输出格式
if [ "$OUTPUT_FORMAT" = "json" ]; then
  # JSON 输出
  if [ -n "$PLUGIN_CONFIG" ] && command -v jq &> /dev/null; then
    jq ". + {installed_at: \"$INSTALLED_AT\"}" "$PLUGIN_CONFIG"
  else
    cat <<EOF
{
  "name": "$PLUGIN_NAME",
  "installed_version": "$PLUGIN_VERSION",
  "installed_at": "$INSTALLED_AT",
  "source": "$SOURCE"
}
EOF
  fi
else
  # 表格输出
  echo -e "${BLUE}📖 插件信息${NC}"
  echo "================================"
  echo ""
  echo -e "${GREEN}插件名称${NC}"
  echo "  $PLUGIN_NAME"
  echo ""
  echo -e "${GREEN}安装版本${NC}"
  echo "  $PLUGIN_VERSION"
  echo ""
  echo -e "${GREEN}安装时间${NC}"
  echo "  $INSTALLED_AT"
  echo ""
  echo -e "${GREEN}插件来源${NC}"
  echo "  $SOURCE"
  echo ""

  # 显示插件配置详情
  if [ -n "$PLUGIN_CONFIG" ]; then
    if command -v jq &> /dev/null; then
      DISPLAY_NAME=$(jq -r '.displayName // .name' "$PLUGIN_CONFIG")
      DESCRIPTION=$(jq -r '.description' "$PLUGIN_CONFIG")
      AUTHOR=$(jq -r '.author // "Unknown"' "$PLUGIN_CONFIG")
      LICENSE=$(jq -r '.license // "Unknown"' "$PLUGIN_CONFIG")

      echo -e "${GREEN}插件详情${NC}"
      echo "  显示名称: $DISPLAY_NAME"
      echo "  描述: $DESCRIPTION"
      echo "  作者: $AUTHOR"
      echo "  许可证: $LICENSE"
      echo ""

      # 文件列表
      FILES_COUNT=$(jq '.files | length' "$PLUGIN_CONFIG" 2>/dev/null || echo "0")
      if [ "$FILES_COUNT" -gt 0 ]; then
        echo -e "${GREEN}包含文件 ($FILES_COUNT)${NC}"
        jq -r '.files[]? | "  • \(.path) (\(.type))"' "$PLUGIN_CONFIG" 2>/dev/null
        echo ""
      fi

      # 命令列表
      COMMANDS_COUNT=$(jq '.commands | length' "$PLUGIN_CONFIG" 2>/dev/null || echo "0")
      if [ "$COMMANDS_COUNT" -gt 0 ]; then
        echo -e "${GREEN}提供命令 ($COMMANDS_COUNT)${NC}"
        jq -r '.commands[]? | "  • \(.name): \(.description)"' "$PLUGIN_CONFIG" 2>/dev/null
        echo ""
      fi

      # Instincts 支持
      INSTINCTS=$(jq '.instincts.enabled // false' "$PLUGIN_CONFIG" 2>/dev/null)
      if [ "$INSTINCTS" = "true" ]; then
        echo -e "${GREEN}✨ Instincts 集成${NC}"
        echo "  状态: 已启用"
        INSTINCTS_FILE=$(jq -r '.instincts.file // "instincts.json"' "$PLUGIN_CONFIG")
        echo "  文件: $INSTINCTS_FILE"
        echo ""
      fi

      # 依赖关系
      DEPS_COUNT=$(jq '.dependencies | length' "$PLUGIN_CONFIG" 2>/dev/null || echo "0")
      if [ "$DEPS_COUNT" -gt 0 ]; then
        echo -e "${GREEN}依赖 ($DEPS_COUNT)${NC}"
        jq -r '.dependencies | to_entries[]? | "  • \(.key): \(.value)"' "$PLUGIN_CONFIG" 2>/dev/null
        echo ""
      fi
    fi
  fi

  # 备份信息
  BACKUP_DIR="$TARGET_DIR/.plugins/backups/$PLUGIN_NAME"
  if [ -d "$BACKUP_DIR" ]; then
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR" 2>/dev/null | wc -l)
    echo -e "${GREEN}备份历史${NC}"
    echo "  备份数: $BACKUP_COUNT"
    echo "  位置: $BACKUP_DIR"
    echo ""
  fi
fi
echo "================================"
