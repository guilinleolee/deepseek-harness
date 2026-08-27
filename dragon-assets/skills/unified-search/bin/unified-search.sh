#!/bin/bash
# ============================================================================
# 超能搜 (unified-search) - 智能统一搜索入口
# ============================================================================
# 功能: 自动分析查询意图，智能路由到最优搜索源，聚合结果
# 作者: 九部天龙
# 版本: 1.0.0
# ============================================================================

set -euo pipefail

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/../lib"
CONFIG_DIR="$SCRIPT_DIR/../config"

# 引入核心模块
source "../lib/search_memory.sh"
source "../lib/search_local.sh"
source "../lib/search_web.sh"
source "../lib/search_github.sh"
source "./analyzer.sh"
source "./router.sh"
source "./aggregator.sh"
source "./cache.sh"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ============================================================================
# 帮助信息
# ============================================================================
show_help() {
    cat << 'EOF'
🔍 超能搜 (unified-search) - 智能统一搜索

用法:
    超能搜 [选项] "查询内容"

选项:
    --all              搜索所有源（默认: 智能选择）
    --local            仅搜索本地代码
    --web              仅搜索 Web
    --memory           仅搜索知识图谱
    --github           仅搜索 GitHub
    --cache-stats      显示缓存统计
    --cache-clear      清空缓存
    --no-cache         禁用缓存
    --format json      输出 JSON 格式
    --verbose          显示详细过程
    -h, --help         显示帮助信息

示例:
    超能搜 "React 最佳实践"
    超能搜 --all "微服务架构"
    超能搜 --local "TODO 注释"
    超能搜 --web "AI 新闻"

搜索源优先级:
    1. 知识图谱 (memory/agentdb)
    2. 本地代码 (mgrep/github-cli)
    3. 搜索缓存
    4. Web 搜索 (Brave + Exa)

更多信息: https://github.com/九部天龙/unified-search
EOF
}

# ============================================================================
# 日志函数
# ============================================================================
log_info() {
    echo -e "${BLUE}ℹ${NC} $*"
}

log_success() {
    echo -e "${GREEN}✓${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $*"
}

log_error() {
    echo -e "${RED}✗${NC} $*" >&2
}

log_debug() {
    if [[ "${VERBOSE:-false}" == "true" ]]; then
        echo -e "${CYAN}▶${NC} $*"
    fi
}

# ============================================================================
# 主函数
# ============================================================================
main() {
    local query=""
    local search_all=false
    local search_local=false
    local search_web=false
    local search_memory=false
    local search_github=false
    local format="markdown"
    local use_cache=true
    local VERBOSE=false

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            --all)
                search_all=true
                shift
                ;;
            --local)
                search_local=true
                shift
                ;;
            --web)
                search_web=true
                shift
                ;;
            --memory)
                search_memory=true
                shift
                ;;
            --github)
                search_github=true
                shift
                ;;
            --cache-stats)
                cache_stats
                exit 0
                ;;
            --cache-clear)
                cache_clear
                exit 0
                ;;
            --no-cache)
                use_cache=false
                shift
                ;;
            --format)
                format="$2"
                shift 2
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            -*)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
            *)
                query="$*"
                break
                ;;
        esac
    done

    # 检查查询
    if [[ -z "$query" ]]; then
        log_error "请提供查询内容"
        show_help
        exit 1
    fi

    # 初始化缓存
    cache_init

    # 输出标题
    echo ""
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${MAGENTA}🔍  超能搜 - 智能统一搜索${NC}"
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${CYAN}查询:${NC} $query"
    echo ""

    # 检查缓存
    if [[ "$use_cache" == "true" ]]; then
        local cached_result
        cached_result=$(cache_get "$query")
        if [[ -n "$cached_result" ]]; then
            log_success "从缓存获取结果"
            echo ""
            echo "$cached_result"
            return 0
        fi
    fi

    # 分析查询类型
    local query_type
    query_type=$(analyzer_analyze "$query")
    log_debug "查询类型: $query_type"

    # 执行搜索
    local results_json="{}"
    local start_time=$(date +%s)

    if [[ "$search_all" == "true" ]]; then
        log_info "并行搜索所有源..."
        results_json=$(router_search_all "$query")
    elif [[ "$search_local" == "true" ]]; then
        log_info "搜索本地代码..."
        results_json=$(router_search_local "$query")
    elif [[ "$search_web" == "true" ]]; then
        log_info "搜索 Web..."
        results_json=$(router_search_web "$query")
    elif [[ "$search_memory" == "true" ]]; then
        log_info "搜索知识图谱..."
        results_json=$(router_search_memory "$query")
    elif [[ "$search_github" == "true" ]]; then
        log_info "搜索 GitHub..."
        results_json=$(router_search_github "$query")
    else
        # 智能路由
        log_info "智能路由到最优搜索源..."
        results_json=$(router_search_smart "$query" "$query_type")
    fi

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    # 聚合结果
    local output
    output=$(aggregator_format "$results_json" "$format" "$query")

    # 输出结果
    echo ""
    echo "$output"
    echo ""
    echo -e "${CYAN}耗时:${NC} ${duration}s"
    echo ""

    # 缓存结果
    if [[ "$use_cache" == "true" ]]; then
        cache_set "$query" "$output"
        log_debug "结果已缓存"
    fi
}

# ============================================================================
# 执行主函数
# ============================================================================
main "$@"
