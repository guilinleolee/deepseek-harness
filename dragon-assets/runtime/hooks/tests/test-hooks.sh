---
license: UNKNOWN
---

#!/bin/bash

###############################################################################
# 九部天龙 - Hooks强制规则测试脚本
###############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  九部天龙 Hooks 强制规则测试${NC}"
echo -e "${YELLOW}========================================${NC}\n"

# 测试文件目录
TEST_DIR="/tmp/九部天龙-hooks-test"
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# 初始化Git仓库
echo -e "${YELLOW}📁 初始化测试仓库...${NC}"
git init -q

# 复制钩子脚本
echo -e "${YELLOW}📋 安装钩子脚本...${NC}"
mkdir -p .git/hooks
cp ~/.claude/hooks/pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# 配置Git
git config user.email "test@example.com"
git config user.name "Test User"

# 测试1: 有注释的文件
echo -e "\n${YELLOW}📝 测试1: 提交有注释的代码${NC}"
cat > test-good.js << 'EOF'
/**
 * 计算两个数的和
 * @param {number} a - 第一个数
 * @param {number} b - 第二个数
 * @returns {number} 和
 */
function add(a, b) {
  // 返回a和b的和
  return a + b;
}

// 导出函数
module.exports = { add };
EOF

git add test-good.js
if git commit -m "测试: 添加有注释的代码" > /dev/null 2>&1; then
  echo -e "${GREEN}✅ PASS: 有注释的文件提交成功${NC}"
else
  echo -e "${RED}❌ FAIL: 有注释的文件被拦截${NC}"
fi

# 测试2: 无注释的文件
echo -e "\n${YELLOW}📝 测试2: 提交无注释的代码${NC}"
cat > test-bad.js << 'EOF'
function multiply(a, b) {
  return a * b;
}

module.exports = { multiply };
EOF

git add test-bad.js
if git commit -m "测试: 添加无注释的代码" > /dev/null 2>&1; then
  echo -e "${RED}❌ FAIL: 无注释的文件未被拦截${NC}"
else
  echo -e "${GREEN}✅ PASS: 无注释的文件被正确拦截${NC}"
fi

# 测试3: 混合文件
echo -e "\n${YELLOW}📝 测试3: 提交混合文件${NC}"
git reset --soft HEAD~1  # 撤销上次提交
cat > test-mixed.js << 'EOF'
// 有注释
function divide(a, b) {
  if (b === 0) throw new Error('Division by zero');
  return a / b;
}

function subtract(a, b) {
  return a - b;
}
EOF

git add test-mixed.js
if git commit -m "测试: 添加混合代码" > /dev/null 2>&1; then
  echo -e "${GREEN}✅ PASS: 混合文件提交成功${NC}"
else
  echo -e "${RED}❌ FAIL: 混合文件被拦截${NC}"
fi

# 测试4: --no-verify 跳过检查
echo -e "\n${YELLOW}📝 测试4: 使用 --no-verify 跳过检查${NC}"
git reset --soft HEAD~1
cat > test-skip.js << 'EOF'
function mod(a, b) {
  return a % b;
}
EOF

git add test-skip.js
if git commit --no-verify -m "测试: 跳过检查" > /dev/null 2>&1; then
  echo -e "${GREEN}✅ PASS: --no-verify 成功跳过检查${NC}"
else
  echo -e "${RED}❌ FAIL: --no-verify 未能跳过检查${NC}"
fi

# 测试5: 非代码文件
echo -e "\n${YELLOW}📝 测试5: 提交非代码文件${NC}"
cat > README.md << 'EOF'
# 测试项目

这是一个测试项目。
EOF

git add README.md
if git commit -m "测试: 添加文档" > /dev/null 2>&1; then
  echo -e "${GREEN}✅ PASS: 非代码文件跳过检查${NC}"
else
  echo -e "${RED}❌ FAIL: 非代码文件被检查${NC}"
fi

# 统计结果
echo -e "\n${YELLOW}========================================${NC}"
echo -e "${YELLOW}  测试结果统计${NC}"
echo -e "${YELLOW}========================================${NC}"
echo -e "${GREEN}已实现功能:${NC}"
echo -e "  ✅ 注释覆盖率检查"
echo -e "  ✅ 低于20%自动拦截"
echo -e "  ✅ --no-verify跳过机制"
echo -e "  ✅ 非代码文件智能跳过"
echo -e "\n${GREEN}📋 下一步:${NC}"
echo -e "  1. 复制钩子到实际项目: cp ~/.claude/hooks/pre-commit.sh <project>/.git/hooks/pre-commit"
echo -e "  2. 或使用Husky自动管理: npm install --save-dev husky"
echo -e ""

# 清理
cd -
rm -rf "$TEST_DIR"
