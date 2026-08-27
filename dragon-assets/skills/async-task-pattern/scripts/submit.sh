#!/usr/bin/env bash
# submit.sh · async-task-pattern V1.0 原语 1
# 提交异步任务，返回 {task_id, status: queued}
# 用法：
#   bash submit.sh --provider <p> --action <a> --payload <json> [--timeout N] [--callback <path>]
# 退出码：0=queued / 2=配置错 / 3=系统错 / 4=未实现

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
ADAPTERS_DIR="$SKILL_DIR/adapters"

PROVIDER=""
ACTION=""
PAYLOAD=""
TIMEOUT=300
CALLBACK=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --provider)  PROVIDER="$2"; shift 2 ;;
    --action)    ACTION="$2"; shift 2 ;;
    --payload)   PAYLOAD="$2"; shift 2 ;;
    --timeout)   TIMEOUT="$2"; shift 2 ;;
    --callback)  CALLBACK="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: bash submit.sh --provider <p> --action <a> --payload <json> [--timeout N] [--callback <path>]"
      echo "退出码：0=queued / 2=配置错 / 3=系统错 / 4=未实现"
      exit 0 ;;
    *) echo "❌ 未知参数: $1" >&2; exit 2 ;;
  esac
done

# 校验必填 5 字段
if [[ -z "$PROVIDER" || -z "$ACTION" || -z "$PAYLOAD" || -z "$TIMEOUT" ]]; then
  echo "❌ JSON 契约 5 必填字段缺失（provider/action/payload/timeout）" >&2
  exit 2
fi

# 校验 adapter 存在
ADAPTER="$ADAPTERS_DIR/${PROVIDER}.sh"
if [[ ! -f "$ADAPTER" ]]; then
  echo "❌ provider=$PROVIDER 对应 adapter 不存在：$ADAPTER" >&2
  exit 4
fi

# 委托给 adapter
echo "📤 submit · provider=$PROVIDER action=$ACTION timeout=${TIMEOUT}s"
exec bash "$ADAPTER" submit --action "$ACTION" --payload "$PAYLOAD" --timeout "$TIMEOUT" --callback "${CALLBACK:-}"