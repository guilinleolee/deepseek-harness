---
license: UNKNOWN
name: web-fetch
description: 网页抓取工具 - 替代 Fetch MCP。提供 HTTP 请求、HTML 解析、内容提取、文件下载等功能。
version: 1.0.0
author: 九部天龙
created: 2026-02-26
tools: - curl: HTTP 客户端
- jq: JSON 处理
- pup: HTML 解析（可选）
triggers: ["web fetch", "Web Fetch Skill"]
---

# Web Fetch Skill

## 技能定位

通过 `curl` 和 `jq` 提供网页抓取能力，替代 Fetch MCP 服务器。

## 核心功能

### 1. 基本 HTTP 请求
```bash
# GET 请求
curl -s "https://api.example.com/data" \
  -H "Accept: application/json" \
  -H "User-Agent: Mozilla/5.0"

# POST JSON
curl -s -X POST "https://api.example.com/create" \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'

# 带认证
curl -s "https://api.example.com/protected" \
  -H "Authorization: Bearer $TOKEN"
```

### 2. HTML 解析
```bash
# 使用 pup（推荐）
# 安装: go install github.com/ericchiang/pup@latest

# 提取标题
curl -s "https://example.com" | pup 'title text{}'

# 提取链接
curl -s "https://example.com" | pup 'a attr{href}'

# 提取所有文本
curl -s "https://example.com" | pup 'text{}'

# CSS 选择器组合
curl -s "https://example.com" | pup 'div.content h1 text{}'

# 或使用 grep/sed（无依赖）
curl -s "https://example.com" | \
  grep -oP '<title>\K[^<]*(?=<\/title>)'
```

### 3. JSON API 处理
```bash
# 提取字段
curl -s "https://api.example.com/data" | jq '.key'

# 嵌套访问
curl -s "https://api.example.com/data" | jq '.user.name'

# 数组操作
curl -s "https://api.example.com/items" | jq '.items[] | .name'

# 过滤
curl -s "https://api.example.com/users" | \
  jq '.users[] | select(.age > 18)'

# 格式化输出
curl -s "https://api.example.com/data" | jq -r '.[] | "\(.id): \(.name)"'
```

### 4. 文件下载
```bash
# 下载文件
curl -O https://example.com/file.pdf

# 指定输出文件名
curl -o output.pdf https://example.com/file.pdf

# 显示进度
curl -# -o file.zip https://example.com/large.zip

# 断点续传
curl -C - -o file.zip https://example.com/large.zip
```

### 5. 网页抓取实战
```bash
#!/bin/bash
# scrape-website.sh

URL=$1

# 获取网页内容
HTML=$(curl -s "$URL")

# 提取标题
TITLE=$(echo "$HTML" | grep -oP '<title>\K[^<]*(?=<\/title>)')
echo "标题: $TITLE"

# 提取描述
DESCRIPTION=$(echo "$HTML" | grep -oP '<meta name="description" content="\K[^"]*')
echo "描述: $DESCRIPTION"

# 提取所有链接
echo "链接:"
echo "$HTML" | grep -oP 'href="\K[^"]*' | head -20
```

## 使用场景

### 场景 1：API 数据获取
```bash
# 获取用户信息
get_user() {
  local user_id=$1
  curl -s "https://api.github.com/users/$user_id" | \
    jq '{name, bio, repos: .public_repos}'
}

get_user "torvalds"
```

### 场景 2：网页内容监控
```bash
# 监控网页变化
monitor_website() {
  local url=$1
  local cache_file="/tmp/web_cache/$(echo "$url" | md5sum | cut -d' ' -f1)"

  mkdir -p "$(dirname "$cache_file")"

  if [ -f "$cache_file" ]; then
    old_content=$(cat "$cache_file")
  else
    old_content=""
  fi

  new_content=$(curl -s "$url")

  if [ "$old_content" != "$new_content" ]; then
    echo "🔄 网页已更新: $url"
    echo "$new_content" > "$cache_file"
    return 1
  fi

  return 0
}
```

### 场景 3：批量抓取
```bash
# 批量下载图片
download_images() {
  local url=$1
  local output_dir=$2

  mkdir -p "$output_dir"

  # 提取图片 URL
  curl -s "$url" | \
    grep -oP 'src="\K[^"]*\.(jpg|png|webp)' | \
    sort -u | \
    while read img_url; do
      filename=$(basename "$img_url")
      echo "下载: $filename"
      curl -s -o "$output_dir/$filename" "$img_url"
    done
}
```

### 场景 4：JSON 数据聚合
```bash
# 聚合多个 API 端点
aggregate_apis() {
  local base_url=$1

  # 并行请求
  curl -s "$base_url/users" > /tmp/users.json &
  curl -s "$base_url/posts" > /tmp/posts.json &
  curl -s "$base_url/comments" > /tmp/comments.json &

  wait

  # 合并结果
  jq -s '{
    users: .[0],
    posts: .[1],
    comments: .[2]
  }' /tmp/users.json /tmp/posts.json /tmp/comments.json
}
```

### 场景 5：网页内容提取
```bash
# 提取文章内容
extract_article() {
  local url=$1

  curl -s "$url" | \
    pup 'article text{}' | \
    sed 's/<[^>]*>//g' | \
    tr -s ' \n' | \
    head -c 5000
}
```

## 错误处理

```bash
# 安全请求包装器
safe_fetch() {
  local url=$1
  local max_retries=3
  local retry_count=0
  local timeout=10

  while [ $retry_count -lt $max_retries ]; do
    response=$(curl -s -S --max-time $timeout "$url" 2>&1)
    exit_code=$?

    if [ $exit_code -eq 0 ]; then
      echo "$response"
      return 0
    fi

    retry_count=$((retry_count + 1))
    echo "⚠️  请求失败 ($retry_count/$max_retries): $response" >&2
    sleep 2
  done

  echo "❌ 请求失败: 已达到最大重试次数" >&2
  return 1
}

# HTTP 状态码检查
check_status() {
  local url=$1
  local status=$(curl -s -o /dev/null -w "%{http_code}" "$url")

  if [ "$status" -ge 200 ] && [ "$status" -lt 300 ]; then
    return 0
  else
    echo "❌ HTTP $status: $url" >&2
    return 1
  fi
}
```

## 性能优化

```bash
# 并行请求
parallel_fetch() {
  local urls=("$@")
  local pids=()

  for url in "${urls[@]}"; do
    curl -s "$url" > "/tmp/$(echo "$url" | md5sum | cut -d' ' -f1)" &
    pids+=($!)
  done

  for pid in "${pids[@]}"; do
    wait $pid
  done
}

# 连接复用
curl -s "https://api.example.com/endpoint1" \
  --cookie-jar /tmp/cookies.txt

curl -s "https://api.example.com/endpoint2" \
  --cookie /tmp/cookies.txt

# 压缩传输
curl -s "https://api.example.com/data" \
  --compressed \
  -H "Accept-Encoding: gzip, deflate"
```

## 安全建议

```bash
# 验证 SSL 证书（默认启用）
curl -s "https://example.com"

# 仅开发环境跳过验证
curl -s -k "https://self-signed.example.com"

# 避免泄露敏感信息
# ❌ 错误：命令历史会记录 token
curl -s "https://api.example.com?token=abc123"

# ✅ 正确：使用环境变量
curl -s "https://api.example.com" \
  -H "Authorization: Bearer $TOKEN"

# 输入验证
sanitize_url() {
  local url=$1
  if echo "$url" | grep -qE '^https?://'; then
    echo "$url"
  else
    echo "❌ 无效的 URL: $url" >&2
    return 1
  fi
}
```

## 高级技巧

### 1. 流式处理
```bash
# 流式 JSON 解析（大文件）
curl -s "https://api.example.com/large-data" | \
  jq -c '.[]' | \
  while read -r item; do
    process_item "$item"
  done
```

### 2. 请求限流
```bash
# 令牌桶限流
rate_limited_fetch() {
  local url=$1
  local rate=2  # 每秒请求数

  while true; do
    current_time=$(date +%s)
    last_request_time=$(cat /tmp/last_request 2>/dev/null || echo "0")
    time_diff=$((current_time - last_request_time))

    if [ $time_diff -ge $((1 / rate)) ]; then
      echo "$current_time" > /tmp/last_request
      curl -s "$url"
      break
    fi

    sleep 0.1
  done
}
```

### 3. 智能重试
```bash
# 指数退避重试
exponential_backoff_fetch() {
  local url=$1
  local max_retries=5
  local retry_count=0

  while [ $retry_count -lt $max_retries ]; do
    response=$(curl -s "$url")
    if [ $? -eq 0 ]; then
      echo "$response"
      return 0
    fi

    wait_time=$((2 ** retry_count))
    echo "重试 $retry_count，等待 ${wait_time}s..." >&2
    sleep $wait_time
    retry_count=$((retry_count + 1))
  done

  return 1
}
```

## 与原 Fetch MCP 对比

| 功能 | Fetch MCP | web-fetch Skill |
|------|-----------|-----------------|
| HTTP 请求 | ✅ | ✅ |
| JSON 解析 | ✅ | ✅ (jq) |
| HTML 解析 | ✅ | ✅ (pup/grep) |
| 文件下载 | ✅ | ✅ |
| 流式处理 | ❌ | ✅ |
| 并行请求 | ❌ | ✅ |
| 启动速度 | 需启动进程 | 即时 |
| 可扩展性 | 需更新 MCP | 修改 Shell 即可 |

## 依赖检查

```bash
# 检查 curl
curl --version

# 检查 jq
jq --version

# 检查 pup（可选）
pup --version 2>/dev/null || echo "pup 未安装，使用 grep/sed 替代"
```

## 示例对话

**用户**: 获取 GitHub 用户信息

**AI**:
```bash
curl -s "https://api.github.com/users/torvalds" | \
  jq '{name: .name, bio: .bio, repos: .public_repos, location: .location}'
```

**用户**: 抓取网页所有链接

**AI**:
```bash
curl -s "https://example.com" | \
  pup 'a attr{href}' | \
  grep -E '^https?://' | \
  sort -u
```

**用户**: 下载文件并显示进度

**AI**:
```bash
curl -# -o downloaded.pdf https://example.com/file.pdf
```
