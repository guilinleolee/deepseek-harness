#!/bin/bash
# plugin-install.sh - 安装九部天龙插件

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
📦 Plugin Install - 安装九部天龙插件

用法:
  plugin-install <source>

参数:
  source            插件来源

                    本地路径:
                      /path/to/plugin
                      ~/.claude/plugins/my-plugin

                    GitHub 仓库:
                      username/repo
                      https://github.com/username/repo.git

                    Git URL:
                      git://github.com/username/repo.git
                      ssh://git@github.com/username/repo.git

选项:
  --target <dir>     安装目标目录（默认: ~/.claude）
  --force            强制覆盖已安装的插件
  --no-hooks         跳过钩子脚本执行
  --dry-run          预览安装不执行

示例:
  # 从本地目录安装
  plugin-install ~/.claude/.claude-plugin/nine-dragons

  # 从 GitHub 仓库安装
  plugin-install username/nine-dragons-plugin

  # 从 Git URL 安装
  plugin-install https://github.com/username/repo.git

  # 预览安装
  plugin-install --dry-run username/repo

说明:
  • 自动验证 plugin.json 格式
  • 检查依赖关系
  • 执行安装钩子
  • 复制文件到目标位置

EOF
}

# 默认参数
TARGET_DIR="$HOME/.claude"
FORCE=false
NO_HOOKS=false
DRY_RUN=false

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --target)
      TARGET_DIR="$2"
      shift 2
      ;;
    --force)
      FORCE=true
      shift
      ;;
    --no-hooks)
      NO_HOOKS=true
      shift
      ;;
    --dry-run)
      DRY_RUN=true
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
      SOURCE="$1"
      shift
      ;;
  esac
done

# 检查参数
if [ -z "$SOURCE" ]; then
  echo -e "${RED}❌ 缺少插件来源${NC}"
  show_help
  exit 1
fi

echo -e "${BLUE}📦 插件安装${NC}"
echo "================================"
echo ""
echo "插件来源: $SOURCE"
echo "目标目录: $TARGET_DIR"
echo ""

# 临时目录
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# 1. 获取插件
echo -e "${BLUE}📥 获取插件...${NC}"
echo ""

if [ -d "$SOURCE" ]; then
  # 本地目录
  echo "从本地目录安装: $SOURCE"
  PLUGIN_DIR="$SOURCE"
else
  # Git 仓库
  if [[ "$SOURCE" =~ ^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$ ]]; then
    # GitHub 短格式
    REPO_URL="https://github.com/$SOURCE.git"
  else
    # 完整 URL
    REPO_URL="$SOURCE"
  fi

  echo "从 Git 仓库克隆: $REPO_URL"

  if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}🔍 Dry run - 不执行克隆${NC}"
    PLUGIN_DIR="$TEMP_DIR/plugin"
  else
    git clone --depth 1 "$REPO_URL" "$TEMP_DIR/plugin" 2>/dev/null || {
      echo -e "${RED}❌ 克隆失败: $REPO_URL${NC}"
      exit 1
    }
    PLUGIN_DIR="$TEMP_DIR/plugin"
  fi
fi

# 2. 验证插件
echo -e "${BLUE}🔍 验证插件...${NC}"
echo ""

PLUGIN_CONFIG="$PLUGIN_DIR/plugin.json"

if [ ! -f "$PLUGIN_CONFIG" ]; then
  echo -e "${RED}❌ 缺少 plugin.json${NC}"
  exit 1
fi

# 读取插件信息
if command -v jq &> /dev/null; then
  PLUGIN_NAME=$(jq -r '.name' "$PLUGIN_CONFIG")
  PLUGIN_VERSION=$(jq -r '.version' "$PLUGIN_CONFIG")
  PLUGIN_DISPLAY=$(jq -r '.displayName // .name' "$PLUGIN_CONFIG")
  PLUGIN_DESC=$(jq -r '.description' "$PLUGIN_CONFIG")
else
  # 没有 jq，使用 grep
  PLUGIN_NAME=$(grep '"name"' "$PLUGIN_CONFIG" | head -1 | sed 's/.*"\([^"]*\)".*/\1/')
  PLUGIN_VERSION=$(grep '"version"' "$PLUGIN_CONFIG" | head -1 | sed 's/.*"\([^"]*\)".*/\1/')
  PLUGIN_DISPLAY="$PLUGIN_NAME"
  PLUGIN_DESC=$(grep '"description"' "$PLUGIN_CONFIG" | head -1 | sed 's/.*"\([^"]*\)".*/\1/')
fi

echo "插件名称: $PLUGIN_NAME"
echo "显示名称: $PLUGIN_DISPLAY"
echo "版本: $PLUGIN_VERSION"
echo "描述: $PLUGIN_DESC"
echo ""

# 3. 检查依赖
if command -v jq &> /dev/null; then
  DEPS=$(jq -r '.dependencies // {}' "$PLUGIN_CONFIG")
  if [ "$DEPS" != "{}" ]; then
    echo -e "${BLUE}📦 检查依赖...${NC}"
    echo "$DEPS" | jq -r 'to_entries[] | "  • \(.key): \(.value)"'
    echo ""
  fi
fi

# 4. 检查是否已安装
INSTALLED_MARKER="$TARGET_DIR/.plugins/installed/$PLUGIN_NAME"

if [ -f "$INSTALLED_MARKER" ] && [ "$FORCE" != true ]; then
  INSTALLED_VERSION=$(cat "$INSTALLED_MARKER" | jq -r '.version')
  echo -e "${YELLOW}⚠️  插件已安装: $PLUGIN_NAME (版本: $INSTALLED_VERSION)${NC}"
  echo ""
  echo "使用 --force 强制重新安装"
  exit 1
fi

# Dry run 检查
if [ "$DRY_RUN" = true ]; then
  echo -e "${YELLOW}🔍 Dry run 模式${NC}"
  echo ""
  echo "将要安装的文件:"

  if command -v jq &> /dev/null; then
    jq -r '.files[]? | "  • \(.path) → \(.target)"' "$PLUGIN_CONFIG" 2>/dev/null || echo "  (无文件列表)"
  fi

  echo ""
  echo "预览完成，使用 plugin-install $SOURCE 执行安装"
  exit 0
fi

# 5. 执行预安装钩子
if [ "$NO_HOOKS" != true ] && command -v jq &> /dev/null; then
  PRE_INSTALL=$(jq -r '.hooks.preInstall // empty' "$PLUGIN_CONFIG")

  if [ "$PRE_INSTALL" != "null" ] && [ -n "$PRE_INSTALL" ]; then
    echo -e "${BLUE}🔧 执行预安装钩子...${NC}"

    HOOK_SCRIPT="$PLUGIN_DIR/$PRE_INSTALL"

    if [ -f "$HOOK_SCRIPT" ]; then
      cd "$PLUGIN_DIR"
      bash "$HOOK_SCRIPT" || {
        echo -e "${RED}❌ 预安装钩子失败${NC}"
        exit 1
      }
    else
      echo -e "${YELLOW}⚠️  钩子脚本不存在: $PRE_INSTALL${NC}"
    fi

    echo ""
  fi
fi

# 6. 安装文件
echo -e "${BLUE}📦 安装文件...${NC}"
echo ""

mkdir -p "$TARGET_DIR/.plugins/installed"
mkdir -p "$TARGET_DIR/agents"
mkdir -p "$TARGET_DIR/skills"
mkdir -p "$TARGET_DIR/commands"
mkdir -p "$TARGET_DIR/rules"
mkdir -p "$TARGET_DIR/hooks"

if command -v jq &> /dev/null; then
  # 使用 jq 解析文件列表
  jq -c '.files[]?' "$PLUGIN_CONFIG" 2>/dev/null | while read -r file_info; do
    FILE_PATH=$(echo "$file_info" | jq -r '.path')
    FILE_TYPE=$(echo "$file_info" | jq -r '.type')
    TARGET=$(echo "$file_info" | jq -r '.target // empty')

    if [ "$TARGET" = "null" ]; then
      # 根据类型确定目标
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
      # 创建目标目录
      DEST_DIR=$(dirname "$DEST_FILE")
      mkdir -p "$DEST_DIR"

      # 复制文件
      cp "$SOURCE_FILE" "$DEST_FILE"
      echo "  ✅ $FILE_PATH → $DEST_FILE"
    else
      echo -e "${YELLOW}  ⚠️  文件不存在: $FILE_PATH${NC}"
    fi
  done
else
  # 没有 jq，复制整个目录
  echo "  复制所有文件..."
  cp -r "$PLUGIN_DIR"/* "$TARGET_DIR/"
fi

# 7. 安装 Instincts（如果有）
if [ -f "$PLUGIN_DIR/instincts.json" ]; then
  echo -e "${BLUE}📝 安装 Instincts...${NC}"

  INSTINCTS_DIR="$TARGET_DIR/instincts"
  mkdir -p "$INSTINCTS_DIR"

  cp "$PLUGIN_DIR/instincts.json" "$INSTINCTS_DIR/instincts.json"
  echo "  ✅ instincts.json → $INSTINCTS_DIR/"
  echo ""
fi

# 8. 执行后安装钩子
if [ "$NO_HOOKS" != true ] && command -v jq &> /dev/null; then
  POST_INSTALL=$(jq -r '.hooks.postInstall // empty' "$PLUGIN_CONFIG")

  if [ "$POST_INSTALL" != "null" ] && [ -n "$POST_INSTALL" ]; then
    echo -e "${BLUE}🔧 执行后安装钩子...${NC}"

    HOOK_SCRIPT="$PLUGIN_DIR/$POST_INSTALL"

    if [ -f "$HOOK_SCRIPT" ]; then
      cd "$PLUGIN_DIR"
      bash "$HOOK_SCRIPT" || {
        echo -e "${RED}❌ 后安装钩子失败${NC}"
        exit 1
      }
    else
      echo -e "${YELLOW}⚠️  钩子脚本不存在: $POST_INSTALL${NC}"
    fi

    echo ""
  fi
fi

# 9. 记录安装
echo -e "${BLUE}📝 记录安装...${NC}"

INSTALL_INFO=$(cat <<EOF
{
  "name": "$PLUGIN_NAME",
  "version": "$PLUGIN_VERSION",
  "installed_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "source": "$SOURCE"
}
EOF
)

echo "$INSTALL_INFO" > "$INSTALLED_MARKER"

echo "  ✅ 安装信息已记录"
echo ""

echo "================================"
echo -e "${GREEN}🎉 安装成功！${NC}"
echo ""
echo "插件: $PLUGIN_DISPLAY"
echo "版本: $PLUGIN_VERSION"
echo "位置: $TARGET_DIR"
echo ""
echo -e "${BLUE}💡 后续操作${NC}:"
echo "  • 查看已安装插件: plugin-list"
echo "  • 更新插件: plugin-update $PLUGIN_NAME"
echo "  • 卸载插件: plugin-uninstall $PLUGIN_NAME"
