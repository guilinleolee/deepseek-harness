#!/bin/bash
# ============================================================================
# 智能路由器 - 路由查询到最优搜索源
# ============================================================================

# 智能搜索（根据查询类型自动选择）
router_search_smart() {
    local query="$1"
    local query_type="$2"

    case "$query_type" in
        "memory")
            router_search_memory "$query"
            ;;
        "github")
            router_search_github "$query"
            ;;
        "local")
            router_search_local "$query"
            ;;
        "web_tech")
            # 技术内容优先使用 Exa
            search_web_exa "$query"
            ;;
        "web_general")
            # 通用内容使用 Brave
            search_web_brave "$query"
            ;;
        *)
            # 默认: 先本地，后 Web
            local local_result
            local_result=$(router_search_local "$query")
            if [[ -n "$local_result" ]]; then
                echo "$local_result"
            else
                search_web_brave "$query"
            fi
            ;;
    esac
}

# 搜索所有源（并行）
router_search_all() {
    local query="$1"

    # 并行执行所有搜索
    search_memory "$query" > /tmp/memory_result.json 2>/dev/null &
    search_local "$query" > /tmp/local_result.json 2>/dev/null &
    search_github "$query" > /tmp/github_result.json 2>/dev/null &
    search_web_brave "$query" > /tmp/web_brave_result.json 2>/dev/null &
    search_web_exa "$query" > /tmp/web_exa_result.json 2>/dev/null &

    # 等待所有搜索完成
    wait

    # 聚合结果
    jq -s '{
        memory: .[0] // [],
        local: .[1] // [],
        github: .[2] // [],
        web_brave: .[3] // [],
        web_exa: .[4] // []
    }' /tmp/memory_result.json /tmp/local_result.json /tmp/github_result.json \
        /tmp/web_brave_result.json /tmp/web_exa_result.json 2>/dev/null || echo '{}'
}

# 仅搜索知识图谱
router_search_memory() {
    local query="$1"
    search_memory "$query"
}

# 仅搜索本地代码
router_search_local() {
    local query="$1"
    search_local "$query"
}

# 仅搜索 GitHub
router_search_github() {
    local query="$1"
    search_github "$query"
}

# 仅搜索 Web（自动选择引擎）
router_search_web() {
    local query="$1"

    # 技术查询用 Exa
    if analyzer_is_tech "$query"; then
        search_web_exa "$query"
    else
        search_web_brave "$query"
    fi
}
