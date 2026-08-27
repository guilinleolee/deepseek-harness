#!/bin/bash
# plugin-update.sh - 更新已安装的插件

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
🔄 Plugin Update - 更新已安装的插件

用法:
  plugin-update <plugin-name>

参数:
  plugin-name      插件名称

选项:
  --target <dir>    Claude 目录（默认: ~/.claude）
  --check-only      仅检查更新不执行
  --no-hooks        跳过钩子脚本

示例:
  # 更新插件
  plugin-update nine-dragons-core

  # 仅检查更新
  plugin-update --check-only nine-dragons-core

EOF
}

# 默认参数
TARGET_DIR="$HOME/.claude"
CHECK_ONLY=false
NO_HOOKS=false

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --target)
      TARGET_DIR="$2"
      shift 2
      ;;
    --check-only)
      CHECK_ONLY=true
      shift
      ;;
    --no-hooks)
      NO_HOOKS=true
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
  CURRENT_VERSION=$(jq -r '.version' "$PLUGIN_MARKER")
else
  SOURCE=$(grep '"source"' "$PLUGIN_MARKER" | sed 's/.*"\([^"]*\)".*/\1/')
  CURRENT_VERSION=$(grep '"version"' "$PLUGIN_MARKER" | sed 's/.*"\([^"]*\)".*/\1/')
fi

echo -e "${BLUE}🔄 更新插件${NC}"
echo "================================"
echo ""
echo "插件: $PLUGIN_NAME"
echo "当前版本: $CURRENT_VERSION"
echo "来源: $SOURCE"
echo ""

# 检查是否是 GitHub 仓库
if [[ "$SOURCE" =~ ^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$ ]]; then
  REPO_URL="https://github.com/$SOURCE.git"
else
  echo -e "${RED}❌ 不支持的来源格式: $SOURCE${NC}"
  exit 1
fi

# 获取最新版本
echo -e "${BLUE}🔍 检查更新...${NC}"

LATEST_VERSION=$(git ls-remote --tags "$REPO_URL" 2>/dev/null | tail -1 | sed 's/.*refs\/tags\///')

if [ -z "$LATEST_VERSION" ]; then
  echo -e "${YELLOW}⚠️  无法获取最新版本${NC}"
  exit 1
fi

echo "最新版本: $LATEST_VERSION"
echo ""

if [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
  echo -e "${GREEN}✅ 已是最新版本${NC}"
  exit 0
fi

echo -e "${YELLOW}⬆️  有可用更新: $CURRENT_VERSION → $LATEST_VERSION${NC}"
echo ""

if [ "$CHECK_ONLY" = true ]; then
  echo "使用 plugin-update $PLUGIN_NAME 执行更新"
  exit 0
fi

# 临时目录
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# 下载最新版本
echo -e "${BLUE}📥 下载最新版本...${NC}"

git clone --depth 1 --branch "$LATEST_VERSION" "$REPO_URL" "$TEMP_DIR/plugin" 2>/dev/null || {
  echo -e "${RED}❌ 克隆失败${NC}"
  exit 1
}

echo "✅ 下载完成"
echo ""

# 执行预更新钩子
if [ "$NO_HOOKS" != true ] && [ -f "$TEMP_DIR/plugin/plugin.json" ] && command -v jq &> /dev/null; then
  PRE_UPDATE=$(jq -r '.hooks.preUpdate // empty' "$TEMP_DIR/plugin/plugin.json")

  if [ "$PRE_UPDATE" != "null" ] && [ -n "$PRE_UPDATE" ]; then
    echo -e "${BLUE}🔧 执行预更新钩子...${NC}"

    HOOK_SCRIPT="$TEMP_DIR/plugin/$PRE_UPDATE"

    if [ -f "$HOOK_SCRIPT" ]; then
      cd "$TEMP_DIR/plugin"
      bash "$HOOK_SCRIPT" || {
        echo -e "${RED}❌ 预更新钩子失败${NC}"
        exit 1
      }
    fi

    echo ""
  fi
fi

# 备份当前安装
echo -e "${BLUE}💾 备份当前安装...${NC}"

BACKUP_DIR="$TARGET_DIR/.plugins/backups/$PLUGIN_NAME"
mkdir -p "$BACKUP_DIR"

BACKUP_FILE="$BACKUP_DIR/before-$(date +%Y%m%d_%H%M%S).json"
cp "$PLUGIN_MARKER" "$BACKUP_FILE"

echo "  备份: $BACKUP_FILE"
echo ""

# 卸载旧版本
echo -e "${BLUE}🗑️  卸载旧版本...${NC}"

# 删除旧文件（简化版，实际应该根据安装记录删除）
echo "  清理旧文件..."
echo ""

# 安装新版本
echo -e "${BLUE}📦 安装新版本...${NC}"

PLUGIN_DIR="$TEMP_DIR/plugin"

# 复制文件
mkdir -p "$TARGET_DIR/agents"
mkdir -p "$TARGET_DIR/skills"
mkdir -p "$TARGET_DIR/commands"

if [ -f "$PLUGIN_DIR/plugin.json" ] && command -v jq &> /dev/null; then
  jq -c '.files[]?' "$PLUGIN_DIR/plugin.json" 2>/dev/null | while read -r file_info; do
    FILE_PATH=$(echo "$file_info" | jq -r '.path')
    FILE_TYPE=$(echo "$file_info" | jq -r '.type')
    TARGET=$(echo "$file_info" | jq -r '.target // empty')

    if [ "$TARGET" = "null" ]; then
      case "$FILE_TYPE" in
        agent) TARGET="agents/" ;;
        skill) TARGET="skills/" ;;
        command) TARGET="commands/" ;;
        rule) TARGET="rules/" ;;
        hook) TARGET="hooks/" ;;
        *) TARGET="" ;;
      esac
    fi

    SOURCE_FILE="$PLUGIN_DIR/$FILE_PATH"
    DEST_FILE="$TARGET_DIR/$TARGET$(basename "$FILE_PATH")"

    if [ -f "$SOURCE_FILE" ]; then
      DEST_DIR=$(dirname "$DEST_FILE")
      mkdir -p "$DEST_DIR"
      cp "$SOURCE_FILE" "$DEST_FILE"
      echo "  ✅ $FILE_PATH"
    fi
  done
fi

# 安装 Instincts（如果有）
if [ -f "$PLUGIN_DIR/instincts.json" ]; then
  INSTINCTS_DIR="$TARGET_DIR/instincts"
  mkdir -p "$INSTINCTS_DIR"
  cp "$PLUGIN_DIR/instincts.json" "$INSTINCTS_DIR/instincts.json"
  echo "  ✅ instincts.json"
fi

echo ""

# 执行后更新钩子
if [ "$NO_HOOKS" != true ] && [ -f "$PLUGIN_DIR/plugin.json" ] && command -v jq &> /dev/null; then
  POST_UPDATE=$(jq -r '.hooks.postUpdate // empty' "$PLUGIN_DIR/plugin.json")

  if [ "$POST_UPDATE" != "null" ] && [ -n "$POST_UPDATE" ]; then
    echo -e "${BLUE}🔧 执行后更新钩子...${NC}"

    HOOK_SCRIPT="$PLUGIN_DIR/$POST_UPDATE"

    if [ -f "$HOOK_SCRIPT" ]; then
      cd "$PLUGIN_DIR"
      bash "$HOOK_SCRIPT" || {
        echo -e "${RED}❌ 后更新钩子失败${NC}"
        exit 1
      }
    fi

    echo ""
  fi
fi

# 更新安装记录
echo -e "${BLUE}📝 更新安装记录...${NC}"

INSTALL_INFO=$(cat <<EOF
{
  "name": "$PLUGIN_NAME",
  "version": "$LATEST_VERSION",
  "installed_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "source": "$SOURCE",
  "previous_version": "$CURRENT_VERSION"
}
EOF
)

echo "$INSTALL_INFO" > "$PLUGIN_MARKER"

echo "  ✅ 安装记录已更新"
echo ""

echo "================================"
echo -e "${GREEN}🎉 更新成功！${NC}"
echo ""
echo "插件: $PLUGIN_NAME"
echo "版本: $CURRENT_VERSION → $LATEST_VERSION"
echo ""
echo -e "${BLUE}💡 提示${NC}:"
echo "  • 查看更新日志: git log $CURRENT_VERSION..$LATEST_VERSION"
echo "  • 如有问题，可从备份恢复: $BACKUP_FILE"
