#!/usr/bin/env bash
# download.sh · async-task-pattern V1.0 原语 4
# 拉取任务结果到本地文件，返回 {path, size}
# 用法：
#   bash download.sh --task-id <id> --output <path> [--provider <p>]
# 退出码：0=OK / 1=FAIL / 3=网络错

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
ADAPTERS_DIR="$SKILL_DIR/adapters"

TASK_ID=""
OUTPUT=""
PROVIDER=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --task-id)   TASK_ID="$2"; shift 2 ;;
    --output)    OUTPUT="$2"; shift 2 ;;
    --provider)  PROVIDER="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: bash download.sh --task-id <id> --output <path> [--provider <p>]"
      exit 0 ;;
    *) echo "❌ 未知参数: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$TASK_ID" || -z "$OUTPUT" ]]; then
  echo "❌ 必须提供 --task-id 和 --output" >&2
  exit 2
fi

# 从 task_id 前缀推断 provider（按 adapter 文件名匹配）
# 例：gpt-image-2-test-123 匹配 adapters/gpt-image-2.sh
if [[ -z "$PROVIDER" ]]; then
  for f in "$ADAPTERS_DIR"/*.sh; do
    [[ -f "$f" ]] || continue
    candidate=$(basename "$f" .sh)
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

echo "📥 download · task_id=$TASK_ID output=$OUTPUT provider=$PROVIDER"
exec bash "$ADAPTER" download --task-id "$TASK_ID" --output "$OUTPUT"