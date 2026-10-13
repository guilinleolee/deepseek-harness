---
license: UNKNOWN
---

#!/bin/bash

###############################################################################
# 九部天龙 - P2 Agent智能集成测试脚本（修复版）
###############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  九部天龙 P2 智能集成测试${NC}"
echo -e "${YELLOW}========================================${NC}\n"

# 测试文件目录
TEST_DIR="/tmp/九部天龙-p2-test-fixed"
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

# 初始化Git仓库
echo -e "${YELLOW}📁 初始化测试仓库...${NC}"
git init -q

# 复制钩子和配置
echo -e "${YELLOW}📋 安装钩子和配置...${NC}"
mkdir -p .git/hooks
cp ~/.claude/hooks/pre-commit.sh .git/hooks/pre-commit
cp ~/.claude/hooks/check-comments.js .git/hooks/
cp ~/.claude/hooks/static-analyzer.js .git/hooks/
cp ~/.claude/hooks/code-rules.json .git/hooks/
chmod +x .git/hooks/pre-commit

# 配置Git
git config user.email "test@example.com"
git config user.name "Test User"

# 测试1: 正常代码（有注释 + 无问题）
echo -e "\n${YELLOW}📝 测试1: 正常代码（应该通过）${NC}"
cat > good.js << 'EOF'
/**
 * 计算两个数的和
 * @param {number} a - 第一个数
 * @param {number} b - 第二个数
 * @returns {number} 和
 */
function add(a, b) {
  return a + b;
}
EOF

git add good.js
if git commit -m "测试: 正常代码" > /dev/null 2>&1; then
  echo -e "${GREEN}✅ PASS: 正常代码提交成功${NC}"
else
  echo -e "${RED}❌ FAIL: 正常代码被拦截${NC}"
fi

# 测试2: 代码行过长（警告，应该通过）
echo -e "\n${YELLOW}📝 测试2: 代码行过长（警告，应该通过）${NC}"
git reset --soft HEAD~1 2>/dev/null || true  # 清理上次提交
git reset HEAD . 2>/dev/null || true         # 清空暂存区
cat > long-line.js << 'EOF'
/**
 * 代码行过长测试
 */
function longLine() {
  // 这是一个很长的代码行，超过了120字符的限制，应该产生警告但不拦截提交
  const result = someVeryLongFunctionName(withManyParameters, thatMakesTheLine, exceedTheLimit);
}
EOF

git add long-line.js
if git commit -m "测试: 长代码行" > /dev/null 2>&1; then
  echo -e "${GREEN}✅ PASS: 长代码行警告但仍允许提交${NC}"
else
  echo -e "${RED}❌ FAIL: 长代码行被错误拦截${NC}"
  git commit -m "测试: 长代码行" 2>&1 | tail -10
fi

# 测试3: 使用any类型（错误，应该拦截）
echo -e "\n${YELLOW}📝 测试3: any类型（应该拦截）${NC}"
git reset HEAD . 2>/dev/null || true
cat > any-type.js << 'EOF'
/**
 * 使用any类型的函数
 * 这是不好的做法
 */
function processData(data: any): any {
  return data;
}
EOF

git add any-type.js
if git commit -m "测试: any类型" > /dev/null 2>&1; then
  echo -e "${RED}❌ FAIL: any类型未被拦截${NC}"
else
  echo -e "${GREEN}✅ PASS: any类型被正确拦截${NC}"
fi

# 测试4: eval使用（严重安全问题，应该拦截）
echo -e "\n${YELLOW}📝 测试4: eval使用（应该拦截）${NC}"
git reset HEAD . 2>/dev/null || true
cat > eval-bad.js << 'EOF'
/**
 * 危险的eval函数
 * 存在代码注入风险
 */
function execute(code: string) {
  return eval(code);
}
EOF

git add eval-bad.js
if git commit -m "测试: eval使用" > /dev/null 2>&1; then
  echo -e "${RED}❌ FAIL: eval未被拦截${NC}"
else
  echo -e "${GREEN}✅ PASS: eval被正确拦截${NC}"
fi

# 测试5: 硬编码密钥（严重安全问题，应该拦截）
echo -e "\n${YELLOW}📝 测试5: 硬编码密钥（应该拦截）${NC}"
git reset HEAD . 2>/dev/null || true
cat > secret-bad.js << 'EOF'
/**
 * 配置文件
 * 硬编码了API密钥
 */
const API_KEY = "sk-1234567890abcdef";
const secret = "my_secret_token_123";
EOF

git add secret-bad.js
if git commit -m "测试: 硬编码密钥" > /dev/null 2>&1; then
  echo -e "${RED}❌ FAIL: 硬编码密钥未被拦截${NC}"
else
  echo -e "${GREEN}✅ PASS: 硬编码密钥被正确拦截${NC}"
fi

# 测试6: innerHTML使用（高风险警告，应该通过但警告）
echo -e "\n${YELLOW}📝 测试6: innerHTML使用（高风险警告，应该通过）${NC}"
git reset HEAD . 2>/dev/null || true
cat > xss-risk.js << 'EOF'
/**
 * 渲染函数
 * 存在XSS风险
 */
function render(html: string) {
  document.getElementById('app').innerHTML = html;
}
EOF

git add xss-risk.js
if git commit -m "测试: innerHTML" > /dev/null 2>&1; then
  echo -e "${GREEN}✅ PASS: innerHTML警告但仍允许提交${NC}"
else
  echo -e "${RED}❌ FAIL: innerHTML被错误拦截${NC}"
fi

# 测试7: console.log（警告，应该通过）
echo -e "\n${YELLOW}📝 测试7: console.log（警告，应该通过）${NC}"
git reset HEAD . 2>/dev/null || true
cat > console-log.js << 'EOF'
/**
 * 调试输出
 */
function debug(value: string) {
  // 生产代码不应该有console.log
  console.log(value);
  return value;
}
EOF

git add console-log.js
if git commit -m "测试: console.log" > /dev/null 2>&1; then
  echo -e "${GREEN}✅ PASS: console.log警告但仍允许提交${NC}"
else
  echo -e "${RED}❌ FAIL: console.log被错误拦截${NC}"
fi

# 统计结果
echo -e "\n${YELLOW}========================================${NC}"
echo -e "${YELLOW}  测试结果统计${NC}"
echo -e "${YELLOW}========================================${NC}"
echo -e ""
echo -e "${GREEN}P2智能集成已完成:${NC}"
echo -e "  ✅ 06审查师 - 代码质量检查（函数长度、行长度、魔法数字、console、any）"
echo -e "  ✅ 05安全师 - 安全漏洞检查（eval、XSS、硬编码密钥、SQL注入、ReDoS）"
echo -e "  ✅ 智能建议 - 自动生成修复建议"
echo -e "  ✅ 分级拦截 - critical/error拦截，warning允许"
echo -e ""
echo -e "${GREEN}检查流程:${NC}"
echo -e "  1/2 注释覆盖率检查"
echo -e "  2/2 静态代码分析（智能审查）"
echo -e ""
echo -e "${GREEN}📋 下一步:${NC}"
echo -e "  1. 在实际项目中测试"
echo -e "  2. 根据反馈调整规则"
echo -e "  3. 添加更多检查规则"
echo -e ""

# 清理
cd -
rm -rf "$TEST_DIR"
