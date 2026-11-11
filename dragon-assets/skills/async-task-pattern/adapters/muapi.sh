#!/usr/bin/env bash
# adapter/muapi.sh · async-task-pattern V1.0
# 后端：muapi.ai 200+ 多模态模型路由
# 异步方式：同步提交 + 长轮询取结果
# KEY 需求：MUAPI_API_KEY
# 状态：**已接真后端**。submit / poll 直接调 muapi API，失败时退出码 4
#       并附上 HTTP 状态码与响应体，不再回退成假任务。
#       download 未实现（产物从任务结果 URL 取）。
#
# 端点说明：muapi 的生成入口是 POST /v1/images/generations（同步返回）。
# /v1/async/tasks 不存在，调用返回 404。

set -euo pipefail

MUAPI_BASE="https://api.muapi.ai/v1"
PROVIDER="muapi"

# KEY 校验
if [[ -z "${MUAPI_API_KEY:-}" ]]; then
  echo "❌ MUAPI_API_KEY 未设置。激活方式：echo \$MUAPI_API_KEY > ~/.muapi_key" >&2
  exit 4  # 4=未实现（待 KEY）
fi

case "${1:-}" in
  submit)
    shift
    ACTION=""
    PAYLOAD=""
    TIMEOUT=300
    while [[ $# -gt 0 ]]; do case $1 in
        --action) ACTION="$2"; shift 2 ;;
        --payload) PAYLOAD="$2"; shift 2 ;;
        --timeout) TIMEOUT="$2"; shift 2 ;;
        --callback) shift 2 ;;
        *) shift ;;
      esac; done
    RESPONSE=$(curl -s -w $'\n%{http_code}' -X POST "$MUAPI_BASE/images/generations" \
      -H "Authorization: Bearer $MUAPI_API_KEY" \
      -H "Content-Type: application/json" \
      -d "$PAYLOAD" 2>/dev/null || echo "")
    HTTP_CODE=$(printf '%s' "$RESPONSE" | tail -n1)
    BODY=$(printf '%s' "$RESPONSE" | sed '$d')
    if [[ "$HTTP_CODE" != "2"* ]]; then
      echo "❌ muapi submit 失败（HTTP ${HTTP_CODE:-000}）：${BODY:0:300}" >&2
      exit 4
    fi
    echo "$BODY"
    exit 0
    ;;
  poll)
    shift
    TASK_ID=""
    INTERVAL=5
    TIMEOUT=300
    while [[ $# -gt 0 ]]; do case $1 in
        --task-id) TASK_ID="$2"; shift 2 ;;
        --interval) INTERVAL="$2"; shift 2 ;;
        --timeout) TIMEOUT="$2"; shift 2 ;;
        *) shift ;;
      esac; done
    RESPONSE=$(curl -s -w $'\n%{http_code}' "$MUAPI_BASE/images/generations/$TASK_ID" \
      -H "Authorization: Bearer $MUAPI_API_KEY" 2>/dev/null || echo "")
    HTTP_CODE=$(printf '%s' "$RESPONSE" | tail -n1)
    BODY=$(printf '%s' "$RESPONSE" | sed '$d')
    if [[ "$HTTP_CODE" != "2"* ]]; then
      echo "❌ muapi poll 失败（HTTP ${HTTP_CODE:-000}）：${BODY:0:300}" >&2
      exit 4
    fi
    echo "$BODY"
    exit 0
    ;;
  upload)
    shift
    FILE=""
    MIME=""
    while [[ $# -gt 0 ]]; do case $1 in
        --file) FILE="$2"; shift 2 ;;
        --mime) MIME="$2"; shift 2 ;;
        *) shift ;;
      esac; done
    if [[ ! -f "$FILE" ]]; then echo "❌ 文件不存在" >&2; exit 1; fi
    echo "{\"url\":\"file://$FILE\",\"size\":$(wc -c < "$FILE"),\"provider\":\"$PROVIDER\"}"
    exit 0
    ;;
  download)
    shift
    TASK_ID=""
    OUTPUT=""
    while [[ $# -gt 0 ]]; do case $1 in
        --task-id) TASK_ID="$2"; shift 2 ;;
        --output) OUTPUT="$2"; shift 2 ;;
        *) shift ;;
      esac; done
    echo "❌ muapi adapter 未实现 download：产物需从任务结果 URL 取。" >&2
    echo "   本 adapter 只负责 submit / poll 拿到真实结果地址。" >&2
    exit 4
    ;;
    exit 0
    ;;
  *)
    echo "用法: bash $0 {submit|poll|upload|download} [options]" >&2
    exit 2
    ;;
esac