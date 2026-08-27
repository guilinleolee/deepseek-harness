#!/bin/bash
# ============================================================================
# 查询分析器 - 分析查询意图和类型
# ============================================================================

# 分析查询类型
analyzer_analyze() {
    local query="$1"

    # 转换为小写进行匹配
    local query_lower=$(echo "$query" | tr '[:upper:]' '[:lower:]')

    # 优先级 1: 知识图谱关键词
    if echo "$query_lower" | grep -qiE "记住|之前|历史|我们|讨论|说过|记录"; then
        echo "memory"
    # 优先级 2: GitHub 关键词
    elif echo "$query_lower" | grep -qiE "repo|仓库|github|pr|issue|开源项目"; then
        echo "github"
    # 优先级 3: 本地代码关键词
    elif echo "$query_lower" | grep -qiE "代码|函数|文件|项目|实现|todo|fixme|hack|本地"; then
        echo "local"
    # 优先级 4: 技术内容关键词
    elif echo "$query_lower" | grep -qiE "编程|api|教程|文档|框架|库|最佳实践|怎么用|如何|best practices|tutorial|guide"; then
        echo "web_tech"
    # 默认: Web 通用搜索
    else
        echo "web_general"
    fi
}

# 提取关键词
analyzer_extract_keywords() {
    local query="$1"

    # 移除停用词
    local stopwords="的|了|是|在|和|与|或|但是|然后|因为|所以"
    echo "$query" | sed "s/\b\($stopwords\)\b//gi"
}

# 分析查询复杂度
analyzer_complexity() {
    local query="$1"
    local word_count=$(echo "$query" | wc -w)

    if [[ $word_count -le 3 ]]; then
        echo "simple"
    elif [[ $word_count -le 8 ]]; then
        echo "medium"
    else
        echo "complex"
    fi
}

# 检测是否为问题
analyzer_is_question() {
    local query="$1"
    echo "$query" | grep -qiE "\?$|怎么|如何|什么|为什么|哪个|哪些|是否|可以|能否"
}

# 检测是否为技术查询
analyzer_is_tech() {
    local query="$1"
    echo "$query" | grep -qiE "编程|代码|api|框架|库|函数|类|接口|algorithm|data structure|programming"
}

# 检测是否为新闻查询
analyzer_is_news() {
    local query="$1"
    echo "$query" | grep -qiE "新闻|资讯|最新|today|news|breaking"
}
