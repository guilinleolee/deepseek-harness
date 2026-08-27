#!/bin/bash
# ============================================================================
# 缓存管理器 - 管理搜索结果缓存
# ============================================================================

# 缓存配置
CACHE_DIR="${CACHE_DIR:-$HOME/.cache/unified-search}"
CACHE_TTL="${CACHE_TTL:-3600}"  # 1小时
CACHE_MAX_SIZE="${CACHE_MAX_SIZE:-1000}"

# 初始化缓存
cache_init() {
    mkdir -p "$CACHE_DIR"

    # 创建缓存索引
    local index_file="$CACHE_DIR/index.json"
    if [[ ! -f "$index_file" ]]; then
        echo '{"cache_stats": {"hits": 0, "misses": 0, "total": 0}}' > "$index_file"
    fi
}

# 生成缓存 Key
cache_key() {
    local query="$1"
    echo "$query" | md5sum | cut -d' ' -f1
}

# 获取缓存
cache_get() {
    local query="$1"
    local key=$(cache_key "$query")
    local cache_file="$CACHE_DIR/$key.json"

    if [[ ! -f "$cache_file" ]]; then
        cache_increment_miss
        return 1
    fi

    # 检查是否过期
    local cache_time=$(stat -c %Y "$cache_file" 2>/dev/null || stat -f %m "$cache_file" 2>/dev/null)
    local current_time=$(date +%s)
    local age=$((current_time - cache_time))

    if [[ $age -gt $CACHE_TTL ]]; then
        rm -f "$cache_file"
        cache_increment_miss
        return 1
    fi

    cache_increment_hit
    cat "$cache_file"
}

# 设置缓存
cache_set() {
    local query="$1"
    local result="$2"
    local key=$(cache_key "$query")
    local cache_file="$CACHE_DIR/$key.json"

    echo "$result" > "$cache_file"

    # 更新索引
    cache_update_index "$key" "$query"
}

# 清空缓存
cache_clear() {
    rm -rf "$CACHE_DIR"/*
    cache_init
    echo "✓ 缓存已清空"
}

# 缓存统计
cache_stats() {
    local index_file="$CACHE_DIR/index.json"
    local cache_count=$(ls -1 "$CACHE_DIR"/*.json 2>/dev/null | wc -l)

    echo "📊 缓存统计"
    echo ""
    echo "缓存文件数: $cache_count"
    echo "缓存目录: $CACHE_DIR"
    echo "缓存 TTL: ${CACHE_TTL}s"

    if [[ -f "$index_file" ]]; then
        local stats=$(jq -r '.cache_stats' "$index_file" 2>/dev/null)
        echo ""
        echo "命中次数: $(echo "$stats" | jq -r '.hits // 0')"
        echo "未命中次数: $(echo "$stats" | jq -r '.misses // 0')"
        local total=$(echo "$stats" | jq -r '.total // 1')
        local hits=$(echo "$stats" | jq -r '.hits // 0')
        if [[ $total -gt 0 ]]; then
            local hit_rate=$((hits * 100 / total))
            echo "命中率: ${hit_rate}%"
        fi
    fi
}

# 更新缓存索引
cache_update_index() {
    local key="$1"
    local query="$2"
    local index_file="$CACHE_DIR/index.json"

    jq --arg key "$key" --arg query "$query" --arg time "$(date +%s)" \
       '.cache[$key] = {query: $query, time: ($time | tonumber)}' \
       "$index_file" > "$index_file.tmp" && mv "$index_file.tmp" "$index_file"
}

# 增加命中计数
cache_increment_hit() {
    local index_file="$CACHE_DIR/index.json"
    jq '.cache_stats.hits += 1 | .cache_stats.total += 1' "$index_file" > "$index_file.tmp" && mv "$index_file.tmp" "$index_file"
}

# 增加未命中计数
cache_increment_miss() {
    local index_file="$CACHE_DIR/index.json"
    jq '.cache_stats.misses += 1 | .cache_stats.total += 1' "$index_file" > "$index_file.tmp" && mv "$index_file.tmp" "$index_file"
}
