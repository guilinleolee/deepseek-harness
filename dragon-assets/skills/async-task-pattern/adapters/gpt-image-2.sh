#!/usr/bin/env bash
# adapter/gpt-image-2.sh · async-task-pattern V1.0
# 后端：OpenAI image generation API
# 异步方式：长轮询（OpenAI image generation API）
# KEY 需求：OPENAI_API_KEY
# 状态：**未接真后端**。submit/poll 只回显任务元数据，download 不产出文件。
#       未接真后端时退出码 4（未实现），与 async-task-pattern 协议一致。

set -euo pipefail

PROVIDER="gpt-image-2"

not_implemented() {
  echo "❌ $PROVIDER adapter 未接真后端：$1" >&2
  echo "   真实出图请用 dragon-assets/skills/render-deck 或 minimax-image adapter。" >&2
  exit 4
}

case "${1:-}" in
  submit)
    shift
    PAYLOAD=""
    while [[ $# -gt 0 ]]; do case $1 in --payload) PAYLOAD="$2"; shift 2 ;; *) shift ;; esac; done
    if [[ -z "${OPENAI_API_KEY:-}" ]]; then
      not_implemented "OPENAI_API_KEY 未设置"
    fi
    echo "{\"task_id\":\"${PROVIDER}-$(date +%s)-$RANDOM\",\"status\":\"queued\",\"provider\":\"$PROVIDER\",\"payload_size\":${#PAYLOAD}}"
    exit 0
    ;;
  poll)
    shift
    TASK_ID=""
    INTERVAL=5
    TIMEOUT=120
    while [[ $# -gt 0 ]]; do case $1 in
        --task-id) TASK_ID="$2"; shift 2 ;;
        --interval) INTERVAL="$2"; shift 2 ;;
        --timeout) TIMEOUT="$2"; shift 2 ;;
        *) shift ;;
      esac; done
    echo "{\"task_id\":\"$TASK_ID\",\"status\":\"completed\",\"provider\":\"$PROVIDER\",\"result_url\":\"openai://image/$TASK_ID\"}"
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
    if [[ ! -f "$FILE" ]]; then echo "❌ 文件不存在: $FILE" >&2; exit 1; fi
    SIZE=$(wc -c < "$FILE")
    SHA=$(sha256sum "$FILE" | awk '{print $1}')
    echo "{\"url\":\"file://$FILE\",\"size\":$SIZE,\"sha256\":\"$SHA\",\"provider\":\"$PROVIDER\"}"
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
    not_implemented "download 不产出文件（不写占位内容）"
    ;;
  *)
    echo "用法: bash $0 {submit|poll|upload|download} [options]" >&2
    exit 2
    ;;
esac
