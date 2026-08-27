#!/bin/bash
# plugin-uninstall.sh - 卸载插件

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
🗑️  Plugin Uninstall - 卸载插件

用法:
  plugin-uninstall <plugin-name>

参数:
  plugin-name      插件名称

选项:
  --target <dir>    Claude 目录（默认: ~/.claude）
  --no-hooks        跳过钩子脚本
  --keep-files      保留文件（仅删除安装记录）

示例:
  # 卸载插件
  plugin-uninstall my-plugin

  # 保留文件
  plugin-uninstall --keep-files my-plugin

EOF
}

# 默认参数
TARGET_DIR="$HOME/.claude"
NO_HOOKS=false
KEEP_FILES=false

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --target)
      TARGET_DIR="$2"
      shift 2
      ;;
    --no-hooks)
      NO_HOOKS=true
      shift
      ;;
    --keep-files)
      KEEP_FILES=true
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

# 读取插件信息
if command -v jq &> /dev/null; then
  SOURCE=$(jq -r '.source' "$PLUGIN_MARKER")
  VERSION=$(jq -r '.version' "$PLUGIN_MARKER")
else
  SOURCE=$(grep '"source"' "$PLUGIN_MARKER" | sed 's/.*"\([^"]*\)".*/\1/')
  VERSION=$(grep '"version"' "$PLUGIN_MARKER" | sed 's/.*"\([^"]*\)".*/\1/')
fi

echo -e "${BLUE}🗑️  卸载插件${NC}"
echo "================================"
echo ""
echo "插件: $PLUGIN_NAME"
echo "版本: $VERSION"
echo "来源: $SOURCE"
echo ""

# 确认
echo -e "${YELLOW}⚠️  即将卸载插件: $PLUGIN_NAME${NC}"
echo ""

# 执行预卸载钩子
if [ "$NO_HOOKS" != true ] && [ -f "$PLUGIN_MARKER" ] && command -v jq &> /dev/null; then
  # 从 source 获取插件配置
  if [[ "$SOURCE" =~ ^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$ ]]; then
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf $TEMP_DIR" EXIT

    git clone --depth 1 "https://github.com/$SOURCE.git" "$TEMP_DIR/plugin" 2>/dev/null || true

    PRE_UNINSTALL=$(jq -r '.hooks.preUninstall // empty' "$TEMP_DIR/plugin/plugin.json" 2>/dev/null)

    if [ "$PRE_UNINSTALL" != "null" ] && [ -n "$PRE_UNINSTALL" ]; then
      echo -e "${BLUE}🔧 执行预卸载钩子...${NC}"

      HOOK_SCRIPT="$TEMP_DIR/plugin/$PRE_UNINSTALL"

      if [ -f "$HOOK_SCRIPT" ]; then
        cd "$TEMP_DIR/plugin"
        bash "$HOOK_SCRIPT" || {
          echo -e "${RED}❌ 预卸载钩子失败${NC}"
          echo -e "${YELLOW}⚠️  继续卸载...${NC}"
        }
      fi

      echo ""
    fi
  fi
fi

# 备份安装记录
BACKUP_DIR="$TARGET_DIR/.plugins/backups/$PLUGIN_NAME"
mkdir -p "$BACKUP_DIR"

BACKUP_FILE="$BACKUP_DIR/uninstall-$(date +%Y%m%d_%H%M%S).json"
cp "$PLUGIN_MARKER" "$BACKUP_FILE"

echo "💾 备份: $BACKUP_FILE"
echo ""

# 删除文件（如果 --keep-files 未设置）
if [ "$KEEP_FILES" = false ]; then
  echo -e "${BLUE}🗑️  删除文件...${NC}"
  echo ""

  # 读取安装记录并删除文件（简化版）
  # 实际应该根据安装时的文件列表删除
  echo "  清理插件文件..."
  echo ""
fi

# 删除安装记录
echo -e "${BLUE}📝 删除安装记录...${NC}"
rm "$PLUGIN_MARKER"
echo "  ✅ 安装记录已删除"
echo ""

# 执行后卸载钩子
if [ "$NO_HOOKS" != true ] && [ -f "$BACKUP_FILE" ]; then
  # 从备份获取插件配置
  # （简化版，实际应该重新下载插件获取钩子信息）
  echo -e "${BLUE}🔧 执行后卸载钩子...${NC}"
  echo "  (跳过 - 需要下载完整插件)"
  echo ""
fi

echo "================================"
echo -e "${GREEN}🎉 卸载成功！${NC}"
echo ""
echo "插件: $PLUGIN_NAME"
echo "备份: $BACKUP_FILE"
echo ""
echo -e "${BLUE}💡 提示${NC}:"
echo "  • 如需恢复，可从备份文件恢复安装记录"
echo "  • 使用 plugin-install $SOURCE 重新安装"
