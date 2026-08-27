#!/bin/bash
# ============================================================================
# 超能搜测试脚本
# ============================================================================

set -e

# 颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# 测试计数
TESTS_PASSED=0
TESTS_FAILED=0

# 测试函数
test_case() {
    local name="$1"
    local result

    echo "Testing: $name"

    $2 && {
        echo -e "${GREEN}✓${NC} $name"
        ((TESTS_PASSED++))
    } || {
        echo -e "${RED}✗${NC} $name"
        ((TESTS_FAILED++))
    }
}

# 切换到脚本目录
cd "$(dirname "$0")/../bin"

echo "========================================="
echo "超能搜 (unified-search) 测试套件"
echo "========================================="
echo ""

# 测试分析器
test_case "查询分析器 - 本地代码" "bash analyzer.sh | grep -q 'analyzer_analyze'"
test_case "查询分析器 - 技术内容" "bash analyzer.sh | grep -q 'analyzer_is_tech'"
test_case "查询分析器 - 新闻查询" "bash analyzer.sh | grep -q 'analyzer_is_news'"

# 测试路由器
test_case "智能路由器 - 路由函数" "bash router.sh | grep -q 'router_search_smart'"
test_case "智能路由器 - 全源搜索" "bash router.sh | grep -q 'router_search_all'"

# 测试聚合器
test_case "结果聚合器 - Markdown 格式" "bash aggregator.sh | grep -q 'aggregator_format_markdown'"
test_case "结果聚合器 - 去重" "bash aggregator.sh | grep -q 'aggregator_dedup'"

# 测试缓存管理器
test_case "缓存管理器 - 初始化" "bash cache.sh | grep -q 'cache_init'"
test_case "缓存管理器 - Key 生成" "bash cache.sh | grep -q 'cache_key'"

# 测试搜索封装
test_case "知识图谱搜索" "bash ../lib/search_memory.sh | grep -q 'search_memory'"
test_case "本地代码搜索" "bash ../lib/search_local.sh | grep -q 'search_local'"
test_case "Web 搜索" "bash ../lib/search_web.sh | grep -q 'search_web'"
test_case "GitHub 搜索" "bash ../lib/search_github.sh | grep -q 'search_github'"

# 输出结果
echo ""
echo "========================================="
echo "测试结果"
echo "========================================="
echo -e "${GREEN}通过: $TESTS_PASSED${NC}"
echo -e "${RED}失败: $TESTS_FAILED${NC}"
echo "总计: $((TESTS_PASSED + TESTS_FAILED))"
echo ""

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}所有测试通过!${NC}"
    exit 0
else
    echo -e "${RED}有测试失败${NC}"
    exit 1
fi
