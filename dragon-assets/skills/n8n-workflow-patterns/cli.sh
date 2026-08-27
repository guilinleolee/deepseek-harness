#!/bin/bash
# n8n-workflow-patterns CLI

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_PATH="$HOME/.claude/skills/n8n-workflow-patterns/index.db"

case "$1" in
  search)
    shift
    python3 "$SCRIPT_DIR/scripts/search.py" "$@"
    ;;
  categories)
    python3 "$SCRIPT_DIR/scripts/categories.py"
    ;;
  category)
    python3 "$SCRIPT_DIR/scripts/category.py" "$2"
    ;;
  generate)
    shift
    python3 "$SCRIPT_DIR/scripts/generate.py" "$@"
    ;;
  import)
    python3 "$SCRIPT_DIR/scripts/import.py" "$2"
    ;;
  index)
    python3 "$SCRIPT_DIR/scripts/build_index.py" build
    ;;
  *)
    echo "n8n-workflow-patterns CLI"
    echo ""
    echo "Usage:"
    echo "  n8n-search <keyword>          # 搜索工作流模板"
    echo "  n8n-categories                  # 列出所有分类"
    echo "  n8n-category <name>             # 查看特定分类"
    echo "  n8n-generate <description>      # 生成工作流"
    echo "  n8n-import <file.json>        # 导入到n8n"
    echo "  n8n-index build                # 构建搜索索引"
    ;;
esac