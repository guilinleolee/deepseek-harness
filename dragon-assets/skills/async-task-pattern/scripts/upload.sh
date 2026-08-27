#!/usr/bin/env bash
# upload.sh · async-task-pattern V1.0 原语 3
# 上传源文件到 provider storage，返回 {url, size, sha256}
# 用法：
#   bash upload.sh --file <path> --provider <p> [--mime <type>]
# 退出码：0=OK / 1=FAIL / 2=配置错

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
ADAPTERS_DIR="$SKILL_DIR/adapters"

FILE=""
PROVIDER=""
MIME=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --file)     FILE="$2"; shift 2 ;;
    --provider) PROVIDER="$2"; shift 2 ;;
    --mime)     MIME="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: bash upload.sh --file <path> --provider <p> [--mime <type>]"
      exit 0 ;;
    *) echo "❌ 未知参数: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$FILE" || -z "$PROVIDER" ]]; then
  echo "❌ 必须提供 --file 和 --provider" >&2
  exit 2
fi

if [[ ! -f "$FILE" ]]; then
  echo "❌ 文件不存在: $FILE" >&2
  exit 2
fi

# 自动推断 mime
if [[ -z "$MIME" ]]; then
  case "${FILE##*.}" in
    png|jpg|jpeg) MIME="image/${FILE##*.}" ;;
    mp4|mov)      MIME="video/mp4" ;;
    mp3|wav|m4a)  MIME="audio/mpeg" ;;
    json|txt|md)  MIME="text/plain" ;;
    *)            MIME="application/octet-stream" ;;
  esac
fi

ADAPTER="$ADAPTERS_DIR/${PROVIDER}.sh"
if [[ ! -f "$ADAPTER" ]]; then
  echo "❌ provider=$PROVIDER 对应 adapter 不存在" >&2
  exit 4
fi

echo "📤 upload · file=$FILE mime=$MIME provider=$PROVIDER"
exec bash "$ADAPTER" upload --file "$FILE" --mime "$MIME"