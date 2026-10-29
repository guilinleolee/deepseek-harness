#!/usr/bin/env bash
# adapter/minimax.sh · async-task-pattern V1.0
# 后端：本地 Anthropic 兼容代理（CC Switch → MiniMax-M3）
# 异步方式：长轮询
# KEY 需求：无（PROXY_MANAGED）
# 状态：**未接真后端**。代理只提供文本模型，不提供 tts / image-gen；
#       download 不产出文件。未接真后端时退出码 4（未实现）。
#
# 真实出图见 adapters/minimax-image.sh —— 走 MiniMax 官方 API。

set -euo pipefail

PROXY_BASE="${ANTHROPIC_BASE_URL:-http://127.0.0.1:15721}"
PROVIDER="minimax"

not_implemented() {
  echo "❌ $PROVIDER adapter 未接真后端：$1" >&2
  echo "   代理 $PROXY_BASE 只提供文本模型，不提供 tts / image-gen。" >&2
  exit 4
}

case "${1:-}" in
  submit)
    shift
    # minimax 的 tts/image-gen 走 Claude Messages API
    # 这里简化为本地长轮询（实际由调用方传具体 action）
    ACTION=""
    PAYLOAD=""
    TIMEOUT=300
    while [[ $# -gt 0 ]]; do
      case $1 in
        --action) ACTION="$2"; shift 2 ;;
        --payload) PAYLOAD="$2"; shift 2 ;;
        --timeout) TIMEOUT="$2"; shift 2 ;;
        --callback) shift 2 ;;
        *) shift ;;
      esac
    done
    TASK_ID="${PROVIDER}-$(date +%s)-$RANDOM"
    echo "{\"task_id\":\"$TASK_ID\",\"status\":\"queued\",\"provider\":\"$PROVIDER\",\"action\":\"$ACTION\",\"timeout\":$TIMEOUT}"
    exit 0
    ;;
  poll)
    shift
    TASK_ID=""
    INTERVAL=5
    TIMEOUT=300
    while [[ $# -gt 0 ]]; do
      case $1 in
        --task-id) TASK_ID="$2"; shift 2 ;;
        --interval) INTERVAL="$2"; shift 2 ;;
        --timeout) TIMEOUT="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    # minimax 实际是同步响应，poll 直接返回 completed
    echo "{\"task_id\":\"$TASK_ID\",\"status\":\"completed\",\"provider\":\"$PROVIDER\",\"result_url\":\"file://local/$TASK_ID\"}"
    exit 0
    ;;
  upload)
    echo "❌ minimax adapter 不支持 upload 原语（同步协议）" >&2
    exit 4
    ;;
  download)
    shift
    TASK_ID=""
    OUTPUT=""
    while [[ $# -gt 0 ]]; do
      case $1 in
        --task-id) TASK_ID="$2"; shift 2 ;;
        --output) OUTPUT="$2"; shift 2 ;;
        *) shift ;;
      esac
    done
    not_implemented "download 不产出文件（不写占位内容）"
    ;;
  *)
    echo "用法: bash $0 {submit|poll|upload|download} [options]" >&2
    exit 2
    ;;
esac
