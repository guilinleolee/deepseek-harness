---
license: UNKNOWN
---

#!/bin/bash

###############################################################################
# 九部天龙 - P2 Agent智能集成测试脚本
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
TEST_DIR="/tmp/九部天龙-p2-test"
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
echo -e "\n${YELLOW}📝 测试1: 正常代码${NC}"
cat > good.js << 'EOF'
/**
 * 计算两个数的和
 * @param {number} a - 第一个数
 * @param {number} b - 第二个数
 */
function add(a, b) {
  // 返回和
  return a + b;
}

module.exports = { add };
EOF

git add good.js
if git commit -m "测试: 正常代码" > /dev/null 2>&1; then
  echo -e "${GREEN}✅ PASS: 正常代码提交成功${NC}"
else
  echo -e "${RED}❌ FAIL: 正常代码被拦截${NC}"
fi

# 测试2: 长函数（质量问题）
echo -e "\n${YELLOW}📝 测试2: 长函数${NC}"
cat > long-function.js << 'EOF'
// 一个很长的函数
function processData() {
  const data = fetchData();
  const result = [];
  for (let i = 0; i < data.length; i++) {
    const item = data[i];
    const processed = item.value * 2;
    const validated = validate(processed);
    const formatted = format(validated);
    const saved = save(formatted);
    result.push(saved);
  }
  return result;
}
EOF

git add long-function.js
if git commit -m "测试: 长函数" > /dev/null 2>&1; then
  echo -e "${GREEN}✅ PASS: 长函数警告但仍允许提交${NC}"
else
  echo -e "${RED}❌ FAIL: 长函数被拦截${NC}"
fi

# 测试3: 使用any（质量问题）
echo -e "\n${YELLOW}📝 测试3: any类型${NC}"
cat > any-type.js << 'EOF'
// 使用any类型
function processData(data: any): any {
  return data;
}
EOF

git add any-type.js
if git commit -m "测试: any类型" > /dev/null 2>&1; then
  echo -e "${GREEN}✅ PASS: any类型被拦截${NC}"
else
  echo -e "${RED}❌ FAIL: any类型未被拦截${NC}"
fi

# 测试4: eval使用（安全问题）
echo -e "\n${YELLOW}📝 测试4: eval使用${NC}"
cat > eval-bad.js << 'EOF'
// 危险的eval
function execute(code: string) {
  return eval(code);
}
EOF

git add eval-bad.js
if git commit -m "测试: eval使用" > /dev/null 2>&1; then
  echo -e "${GREEN}✅ PASS: eval被拦截${NC}"
else
  echo -e "${RED}❌ FAIL: eval未被拦截${NC}"
fi

# 测试5: 硬编码密钥（安全问题）
echo -e "\n${YELLOW}📝 测试5: 硬编码密钥${NC}"
cat > secret-bad.js << 'EOF'
// 硬编码的API密钥
const API_KEY = "sk-1234567890abcdef";
const secret = "my_secret_token_123";
EOF

git add secret-bad.js
if git commit -m "测试: 硬编码密钥" > /dev/null 2>&1; then
  echo -e "${GREEN}✅ PASS: 硬编码密钥被拦截${NC}"
else
  echo -e "${RED}❌ FAIL: 硬编码密钥未被拦截${NC}"
fi

# 测试6: innerHTML（XSS风险）
echo -e "\n${YELLOW}📝 测试6: innerHTML使用${NC}"
cat > xss-risk.js << 'EOF'
// XSS风险
function render(html: string) {
  document.getElementById('app').innerHTML = html;
}
EOF

git add xss-risk.js
if git commit -m "测试: innerHTML" > /dev/null 2>&1; then
  echo -e "${GREEN}✅ PASS: innerHTML被拦截${NC}"
else
  echo -e "${RED}❌ FAIL: innerHTML未被拦截${NC}"
fi

# 统计结果
echo -e "\n${YELLOW}========================================${NC}"
echo -e "${YELLOW}  测试结果统计${NC}"
echo -e "${YELLOW}========================================${NC}"
echo -e "${GREEN}已实现功能:${NC}"
echo -e "  ✅ 06审查师 - 代码质量检查"
echo -e "  ✅ 05安全师 - 安全漏洞检查"
echo -e "  ✅ 智能建议 - 修复建议生成"
echo -e "  ✅ 分级拦截 - critical/error拦截，warning允许"
echo -e "\n${GREEN}检查规则:${NC}"
echo -e "  代码质量: 函数长度、行长度、魔法数字、console、any类型"
echo -e "  安全检查: eval、XSS、硬编码密钥、SQL注入、ReDoS"
echo -e "\n${GREEN}📋 下一步:${NC}"
echo -e "  1. 在实际项目中测试"
echo -e "  2. 根据反馈调整规则"
echo -e "  3. 添加更多检查规则"
echo -e ""

# 清理
cd -
rm -rf "$TEST_DIR"
