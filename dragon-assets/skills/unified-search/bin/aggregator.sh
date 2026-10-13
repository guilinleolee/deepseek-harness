#!/bin/bash
# ============================================================================
# 结果聚合器 - 聚合和格式化搜索结果
# ============================================================================

# 格式化输出
aggregator_format() {
    local results_json="$1"
    local format="${2:-markdown}"
    local query="$3"

    case "$format" in
        "json")
            echo "$results_json"
            ;;
        "markdown"|*)
            aggregator_format_markdown "$results_json" "$query"
            ;;
    esac
}

# Markdown 格式化
aggregator_format_markdown() {
    local results_json="$1"
    local query="$2"

    echo "## 🔍 搜索结果: $query"
    echo ""

    # 知识图谱结果
    local memory_count=$(echo "$results_json" | jq -r '.memory | length' 2>/dev/null || echo "0")
    if [[ "$memory_count" -gt 0 ]]; then
        echo "### 📚 知识图谱 ($memory_count 条)"
        echo ""
        echo "$results_json" | jq -r '.memory[] | "- \(.name // .title // .text // .)"' 2>/dev/null
        echo ""
    fi

    # 本地代码结果
    local local_count=$(echo "$results_json" | jq -r '.local | length' 2>/dev/null || echo "0")
    if [[ "$local_count" -gt 0 ]]; then
        echo "### 💻 本地代码 ($local_count 条)"
        echo ""
        echo "$results_json" | jq -r '.local[] | "- \`[\(.file // "file")]\((.path // .file // "."))\`: \(.text // .match // .)"' 2>/dev/null
        echo ""
    fi

    # GitHub 结果
    local github_count=$(echo "$results_json" | jq -r '.github | length' 2>/dev/null || echo "0")
    if [[ "$github_count" -gt 0 ]]; then
        echo "### 🐙 GitHub ($github_count 条)"
        echo ""
        echo "$results_json" | jq -r '.github[] | "- [\(.name // .title // .)](\(.url // .html_url // "."))"' 2>/dev/null
        echo ""
    fi

    # Web Brave 结果
    local web_brave_count=$(echo "$results_json" | jq -r '.web_brave | length' 2>/dev/null || echo "0")
    if [[ "$web_brave_count" -gt 0 ]]; then
        echo "### 🌐 Web 搜索 - Brave ($web_brave_count 条)"
        echo ""
        echo "$results_json" | jq -r '.web_brave[]? | "- [\(.title? // .)](\(.url? // .))"' 2>/dev/null
        echo ""
    fi

    # Web Exa 结果
    local web_exa_count=$(echo "$results_json" | jq -r '.web_exa | length' 2>/dev/null || echo "0")
    if [[ "$web_exa_count" -gt 0 ]]; then
        echo "### 🤖 Web 搜索 - Exa ($web_exa_count 条)"
        echo ""
        echo "$results_json" | jq -r '.web_exa[]? | "- [\(.title? // .)](\(.url? // .))"' 2>/dev/null
        echo ""
    fi

    # 如果没有任何结果
    if [[ "$memory_count" -eq 0 && "$local_count" -eq 0 && "$github_count" -eq 0 && "$web_brave_count" -eq 0 && "$web_exa_count" -eq 0 ]]; then
        echo "❌ 未找到相关结果"
        echo ""
        echo "建议:"
        echo "- 尝试使用不同的关键词"
        echo "- 使用 \`--all\` 搜索所有源"
        echo "- 使用 \`--web\` 仅搜索网络"
    fi
}

# 去重结果
aggregator_dedup() {
    local results_json="$1"

    # 按 URL 去重（适用于 Web 结果）
    echo "$results_json" | jq 'unique_by(.url // .path // .id)' 2>/dev/null
}

# 按相关性排序
aggregator_sort_by_relevance() {
    local results_json="$1"

    echo "$results_json" | jq 'sort_by(.score // .relevance // 0) | reverse' 2>/dev/null
}
