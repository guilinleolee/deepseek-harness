---
license: UNKNOWN
---

#!/bin/bash

###############################################################################
# 九部天龙 - Git Pre-commit Hook
#
# 在提交前自动检查代码质量
# 不符合标准将阻止提交
#
# P0: 注释覆盖率检查
# P1: 静态代码分析（06审查师 + 05安全师）
###############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT_HOOKS_DIR="$PROJECT_ROOT/.claude/hooks"
GLOBAL_HOOKS_DIR="$HOME/.claude/hooks"

echo -e "${YELLOW}🔍 九部天龙代码质量检查...${NC}\n"

# 优先使用项目级配置，回退到全局配置
RULES_FILE=""
CHECK_COMMENTS_SCRIPT=""
STATIC_ANALYZER_SCRIPT=""

if [ -f "$PROJECT_HOOKS_DIR/code-rules.json" ]; then
  RULES_FILE="$PROJECT_HOOKS_DIR/code-rules.json"
  CHECK_COMMENTS_SCRIPT="$PROJECT_HOOKS_DIR/check-comments.js"
  STATIC_ANALYZER_SCRIPT="$PROJECT_HOOKS_DIR/static-analyzer.js"
  HOOKS_DIR="$PROJECT_HOOKS_DIR"
elif [ -f "$GLOBAL_HOOKS_DIR/code-rules.json" ]; then
  RULES_FILE="$GLOBAL_HOOKS_DIR/code-rules.json"
  CHECK_COMMENTS_SCRIPT="$GLOBAL_HOOKS_DIR/check-comments.js"
  STATIC_ANALYZER_SCRIPT="$GLOBAL_HOOKS_DIR/static-analyzer.js"
  HOOKS_DIR="$GLOBAL_HOOKS_DIR"
else
  echo -e "${YELLOW}⚠️  未找到规则配置文件,跳过检查${NC}"
  exit 0
fi

# 获取暂存的JavaScript/TypeScript文件
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(js|jsx|ts|tsx)$' || true)

if [ -z "$STAGED_FILES" ]; then
  echo -e "${GREEN}✅ 没有JS/TS文件需要检查${NC}\n"
  exit 0
fi

# ============================================================================
# 检查1: 注释覆盖率 (P0)
# ============================================================================
echo -e "${YELLOW}📝 1/2 注释覆盖率检查...${NC}"

# 读取最小覆盖率要求
MIN_COVERAGE=$(node -e "
  const fs = require('fs');
  const rules = JSON.parse(fs.readFileSync('$RULES_FILE', 'utf8'));
  console.log(rules.rules.comment_coverage.minCoverage || 0.2);
" 2>/dev/null || echo "0.2")

# 导出环境变量
export COMMENT_MIN_COVERAGE=$MIN_COVERAGE

# 运行检查脚本
if ! node "$CHECK_COMMENTS_SCRIPT" $STAGED_FILES; then
  echo -e "\n${RED}❌ 注释覆盖率检查失败${NC}"
  echo -e "${YELLOW}💡 请添加注释后重试,或使用 git commit --no-verify 跳过检查${NC}\n"
  exit 1
fi

# ============================================================================
# 检查2: 静态代码分析 (P1)
# ============================================================================
echo -e "${YELLOW}🤖 2/2 静态代码分析...${NC}"

# 检查是否启用静态分析
STATIC_ENABLED=$(node -e "
  const fs = require('fs');
  const rules = JSON.parse(fs.readFileSync('$RULES_FILE', 'utf8'));
  console.log(rules.rules.static_analysis?.enabled !== false);
" 2>/dev/null || echo "true")

if [ "$STATIC_ENABLED" = "true" ]; then
  if ! node "$STATIC_ANALYZER_SCRIPT" $STAGED_FILES; then
    echo -e "\n${RED}❌ 静态代码分析失败${NC}"
    echo -e "${YELLOW}💡 请修复问题后重试,或使用 git commit --no-verify 跳过检查${NC}\n"
    exit 1
  fi
else
  echo -e "${YELLOW}⏭️  静态代码分析已禁用${NC}"
fi

# ============================================================================
# 所有检查通过
# ============================================================================
echo -e "\n${GREEN}✅ 2/2 所有检查通过${NC}\n"
exit 0
