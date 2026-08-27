#!/usr/bin/env bash
# poll.sh · async-task-pattern V1.0 原语 2
# 轮询任务状态，返回 {task_id, status, result_url?, error?}
# 用法：
#   bash poll.sh --task-id <id> [--interval N] [--timeout N]
# 退出码：0=completed / 1=FAIL / 3=超时

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
ADAPTERS_DIR="$SKILL_DIR/adapters"

TASK_ID=""
INTERVAL=5
TIMEOUT=300
PROVIDER=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --task-id)   TASK_ID="$2"; shift 2 ;;
    --interval)  INTERVAL="$2"; shift 2 ;;
    --timeout)   TIMEOUT="$2"; shift 2 ;;
    --provider)  PROVIDER="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: bash poll.sh --task-id <id> [--interval N] [--timeout N] [--provider <p>]"
      exit 0 ;;
    *) echo "❌ 未知参数: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$TASK_ID" ]]; then
  echo "❌ 必须提供 --task-id" >&2
  exit 2
fi

# 从 task_id 前缀推断 provider（按 adapter 文件名匹配）
# 例：gpt-image-2-test-123 匹配 adapters/gpt-image-2.sh
# 例：minimax-abc123 匹配 adapters/minimax.sh
if [[ -z "$PROVIDER" ]]; then
  for f in "$ADAPTERS_DIR"/*.sh; do
    [[ -f "$f" ]] || continue
    candidate=$(basename "$f" .sh)
    # TASK_ID 必须以 "${candidate}-" 开头
    if [[ "$TASK_ID" == "${candidate}-"* ]]; then
      PROVIDER="$candidate"
      break
    fi
  done
fi

ADAPTER="$ADAPTERS_DIR/${PROVIDER}.sh"
if [[ ! -f "$ADAPTER" ]]; then
  echo "❌ provider=$PROVIDER 对应 adapter 不存在" >&2
  exit 4
fi

# 委托给 adapter
echo "🔄 poll · task_id=$TASK_ID interval=${INTERVAL}s timeout=${TIMEOUT}s"
exec bash "$ADAPTER" poll --task-id "$TASK_ID" --interval "$INTERVAL" --timeout "$TIMEOUT"