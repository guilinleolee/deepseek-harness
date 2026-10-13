#!/bin/bash
# 修复路径问题

echo "修复unified-search技能路径问题..."

# 切换到脚本目录
cd "$(dirname "$0")"

# 检查所有脚本文件
echo "检查脚本文件..."
for file in *.sh; do
    echo "检查: $file"
    # 修复Windows路径到Unix路径的转换问题
    sed -i 's|$(cd "$(dirname "${BASH_SOURCE[0]}")" /c/Users/li/.openclaw/skills/unified-search/c/Users/li/.openclaw/skills/unified-search cd .. /c/Users/li/.openclaw/skills/unified-search/c/Users/li/.openclaw/skills/unified-search pwd)|$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)|g' "$file"
done

echo "修复lib目录引用..."
# 修复lib目录引用
sed -i 's|source "$LIB_DIR/search_memory.sh"|source "../lib/search_memory.sh"|g' unified-search.sh
sed -i 's|source "$LIB_DIR/search_local.sh"|source "../lib/search_local.sh"|g' unified-search.sh
sed -i 's|source "$LIB_DIR/search_web.sh"|source "../lib/search_web.sh"|g' unified-search.sh
sed -i 's|source "$LIB_DIR/search_github.sh"|source "../lib/search_github.sh"|g' unified-search.sh

echo "修复完成！"