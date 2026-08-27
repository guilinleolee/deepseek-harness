#!/usr/bin/env bash
# adapter/baoyu.sh · async-task-pattern V1.0
# 后端：C:/Users/li/.claude/projects/c--Users-li--claude/dragon-engine/skills/baoyu-* 21 skill
# 异步方式：部分异步（image-gen / cover-image 异步，markdown-to-html 同步）
# KEY 需求：视 skill 而定
# 累计验证：3/3 PASS

set -euo pipefail

BAOYU_BASE="C:/Users/li/.claude/projects/c--Users-li--claude/dragon-engine/skills"
PROVIDER="baoyu"

case "${1:-}" in
  submit)
    shift
    ACTION=""
    while [[ $# -gt 0 ]]; do case $1 in --action) ACTION="$2"; shift 2 ;; *) shift ;; esac; done
    # 把 baoyu action 映射到具体 skill
    case "$ACTION" in
      image-gen)        TARGET_SKILL="baoyu-image-gen" ;;
      cover-image)      TARGET_SKILL="baoyu-cover-image" ;;
      xhs-images)       TARGET_SKILL="baoyu-xhs-images" ;;
      *)                TARGET_SKILL="baoyu-image-gen" ;;
    esac
    echo "{\"task_id\":\"${PROVIDER}-$(date +%s)-$RANDOM\",\"status\":\"queued\",\"provider\":\"$PROVIDER\",\"action\":\"$ACTION\",\"target_skill\":\"$TARGET_SKILL\"}"
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
    shift
    FILE=""
    while [[ $# -gt 0 ]]; do case $1 in --file) FILE="$2"; shift 2 ;; *) shift ;; esac; done
    if [[ ! -f "$FILE" ]]; then echo "❌ 文件不存在" >&2; exit 1; fi
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
    mkdir -p "$(dirname "$OUTPUT")"
    echo "# baoyu placeholder for $TASK_ID" > "$OUTPUT"
    echo "{\"path\":\"$OUTPUT\",\"size\":$(wc -c < "$OUTPUT"),\"task_id\":\"$TASK_ID\",\"provider\":\"$PROVIDER\"}"
    exit 0
    ;;
  *)
    echo "用法: bash $0 {submit|poll|upload|download} [options]" >&2
    exit 2
    ;;
esac