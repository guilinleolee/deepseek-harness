#!/usr/bin/env bash
# adapter/minimax-image.sh · async-task-pattern V1.0
# 后端：MiniMax image generation API（image-01）
# 异步方式：同步返回（数秒到数十秒）
# KEY 需求：MINIMAX_API_KEY
# 状态：**已接真后端**。submit 调 MiniMax 生成端点并把产物下载到 --output，
#       失败时退出码 4 并附真实错误，不再回退成假任务。
#
# 端点：POST https://api.minimax.chat/v1/image_generation
# 认证：Authorization: Bearer $MINIMAX_API_KEY
# 比例：1:1 / 16:9 / 4:3 / 3:4 / 9:16 / 21:9
#       3:4 对应小红书，9:16 对应视频号/抖音，21:9 对应公众号主封面
#
# 与 minimax.sh 的分工：minimax.sh 走本地 Anthropic 兼容代理，只提供文本模型；
# 本 adapter 走 MiniMax 官方 API，提供真实出图能力。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELPER="$SCRIPT_DIR/../scripts/minimax_image.py"
PROVIDER="minimax-image"

not_implemented() {
  echo "❌ $PROVIDER adapter 未接真后端：$1" >&2
  exit 4
}

require_key() {
  if [[ -z "${MINIMAX_API_KEY:-}" ]]; then
    echo "❌ MINIMAX_API_KEY 未设置" >&2
    echo "   设置方式：export MINIMAX_API_KEY=<key>" >&2
    exit 4
  fi
}

case "${1:-}" in
  submit)
    shift
    ACTION=""
    PAYLOAD=""
    OUTPUT=""
    while [[ $# -gt 0 ]]; do case $1 in
        --action) ACTION="$2"; shift 2 ;;
        --payload) PAYLOAD="$2"; shift 2 ;;
        --output) OUTPUT="$2"; shift 2 ;;
        --timeout) shift 2 ;;
        --callback) shift 2 ;;
        *) shift ;;
      esac; done
    require_key

    if [[ -z "$PAYLOAD" || "$PAYLOAD" == "{}" ]]; then
      not_implemented "submit 需要 --payload（含 prompt）"
    fi
    if [[ ! -f "$HELPER" ]]; then
      not_implemented "缺少调用器：$HELPER"
    fi

    ARGS=(--payload "$PAYLOAD")
    if [[ -n "$OUTPUT" ]]; then
      ARGS+=(--output "$OUTPUT")
    fi

    RESULT=$(python "$HELPER" "${ARGS[@]}" 2>&1) || {
      echo "$RESULT" >&2
      exit 4
    }
    echo "$RESULT"
    exit 0
    ;;
  poll)
    shift
    TASK_ID=""
    while [[ $# -gt 0 ]]; do case $1 in
        --task-id) TASK_ID="$2"; shift 2 ;;
        --interval) shift 2 ;;
        --timeout) shift 2 ;;
        *) shift ;;
      esac; done
    echo "{\"task_id\":\"$TASK_ID\",\"status\":\"completed\",\"provider\":\"$PROVIDER\",\"note\":\"MiniMax 出图为同步接口，submit 已返回产物\"}"
    exit 0
    ;;
  upload)
    shift
    FILE=""
    MIME=""
    while [[ $# -gt 0 ]]; do case $1 in
        --file) FILE="$2"; shift 2 ;;
        --mime) shift 2 ;;
        *) shift ;;
      esac; done
    if [[ ! -f "$FILE" ]]; then echo "❌ 文件不存在" >&2; exit 1; fi
    SIZE=$(wc -c < "$FILE")
    SHA=$(sha256sum "$FILE" | awk '{print $1}')
    echo "{\"url\":\"file://$FILE\",\"size\":$SIZE,\"sha256\":\"$SHA\",\"provider\":\"$PROVIDER\"}"
    exit 0
    ;;
  download)
    shift
    echo "❌ minimax-image 无独立 download：产物在 submit 时随 --output 落盘。" >&2
    exit 4
    ;;
  *)
    echo "用法: bash $0 {submit|poll|upload|download} [options]" >&2
    echo "  submit --payload '<json>' [--output <file>]" >&2
    echo "  payload 示例: {\"model\":\"image-01\",\"prompt\":\"...\",\"aspect_ratio\":\"3:4\",\"n\":1}" >&2
    exit 2
    ;;
esac
