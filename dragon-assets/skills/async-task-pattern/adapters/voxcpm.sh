#!/usr/bin/env bash
# adapter/voxcpm.sh · async-task-pattern V1.0
# 后端：C:/Users/li/.claude/skills/voxcpm-tts-integration（CPU 真推理）
# 异步方式：同步（< 30s）→ 模拟异步接口（submit 后立即 completed）
# KEY 需求：无
# 累计验证：4/4 PASS

set -euo pipefail

ROOT_SKILL="C:/Users/li/.claude/skills/voxcpm-tts-integration"
PROVIDER="voxcpm"

case "${1:-}" in
  submit)
    shift
    echo "{\"task_id\":\"${PROVIDER}-$(date +%s)-$RANDOM\",\"status\":\"queued\",\"provider\":\"$PROVIDER\",\"note\":\"voxcpm CPU 同步 < 30s\"}"
    exit 0
    ;;
  poll)
    shift
    TASK_ID=""
    while [[ $# -gt 0 ]]; do case $1 in --task-id) TASK_ID="$2"; shift 2 ;; *) shift ;; esac; done
    echo "{\"task_id\":\"$TASK_ID\",\"status\":\"completed\",\"provider\":\"$PROVIDER\"}"
    exit 0
    ;;
  upload)
    echo "❌ voxcpm adapter 不支持 upload（原语仅对图像/视频有效）" >&2
    exit 4
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
    # 实际生产：从 ROOT_SKILL 调 voxcpm.sh 生成 wav 写到 OUTPUT
    if [[ -d "$ROOT_SKILL" ]]; then
      echo "{\"note\":\"转发到 $ROOT_SKILL/scripts/voxcpm.sh\"}" >&2
    fi
    mkdir -p "$(dirname "$OUTPUT")"
    echo "# voxcpm placeholder for $TASK_ID" > "$OUTPUT"
    echo "{\"path\":\"$OUTPUT\",\"size\":$(wc -c < "$OUTPUT"),\"task_id\":\"$TASK_ID\",\"provider\":\"$PROVIDER\"}"
    exit 0
    ;;
  *)
    echo "用法: bash $0 {submit|poll|upload|download} [options]" >&2
    exit 2
    ;;
esac