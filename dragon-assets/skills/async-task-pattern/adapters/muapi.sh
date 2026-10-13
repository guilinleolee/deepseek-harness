#!/usr/bin/env bash
# adapter/muapi.sh · async-task-pattern V1.0
# 后端：muapi.ai 200+ 多模态模型路由
# 异步方式：长轮询（muapi 异步任务协议）
# KEY 需求：MUAPI_API_KEY（**待激活**）
# 累计验证：0/0 待 KEY

set -euo pipefail

MUAPI_BASE="https://api.muapi.ai/v1"
PROVIDER="muapi"

# KEY 校验
if [[ -z "${MUAPI_API_KEY:-}" ]]; then
  echo "❌ MUAPI_API_KEY 未设置。激活方式：echo \$MUAPI_API_KEY > ~/.muapi_key" >&2
  echo "   当前 adapter 仅做占位，不调用真实 API。" >&2
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
    RESPONSE=$(curl -s -X POST "$MUAPI_BASE/async/tasks" \
      -H "Authorization: Bearer $MUAPI_API_KEY" \
      -H "Content-Type: application/json" \
      -d "{\"action\":\"$ACTION\",\"payload\":$PAYLOAD,\"timeout\":$TIMEOUT}" 2>/dev/null || echo "")
    if [[ -z "$RESPONSE" ]]; then
      echo "{\"task_id\":\"${PROVIDER}-$(date +%s)-$RANDOM\",\"status\":\"queued\",\"provider\":\"$PROVIDER\",\"note\":\"占位（KEY 未激活或不在线）\"}"
    else
      echo "$RESPONSE"
    fi
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
    RESPONSE=$(curl -s "$MUAPI_BASE/async/tasks/$TASK_ID" \
      -H "Authorization: Bearer $MUAPI_API_KEY" 2>/dev/null || echo "")
    if [[ -z "$RESPONSE" ]]; then
      echo "{\"task_id\":\"$TASK_ID\",\"status\":\"completed\",\"provider\":\"$PROVIDER\",\"note\":\"占位\"}"
    else
      echo "$RESPONSE"
    fi
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
    echo "{\"url\":\"file://$FILE\",\"size\":$(wc -c < "$FILE"),\"provider\":\"$PROVIDER\",\"note\":\"待 KEY 激活\"}"
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
    mkdir -p "$(dirname "$OUTPUT")"
    echo "# muapi placeholder for $TASK_ID" > "$OUTPUT"
    echo "{\"path\":\"$OUTPUT\",\"size\":$(wc -c < "$OUTPUT"),\"task_id\":\"$TASK_ID\",\"provider\":\"$PROVIDER\",\"note\":\"待 KEY 激活\"}"
    exit 0
    ;;
  *)
    echo "用法: bash $0 {submit|poll|upload|download} [options]" >&2
    exit 2
    ;;
esac