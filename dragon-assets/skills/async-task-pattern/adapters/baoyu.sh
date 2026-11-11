#!/usr/bin/env bash
# adapter/baoyu.sh · async-task-pattern V1.0
# 后端：baoyu-* 系列（仓库内 dragon-assets/skills/baoyu-*）
# 异步方式：部分异步（image-gen / cover-image 异步，markdown-to-html 同步）
# KEY 需求：视 skill 而定
# 状态：**未接真后端**。submit/poll 只回显任务元数据，download 不产出文件。
#       未接真后端时退出码 4（未实现），与 async-task-pattern 协议一致。
#
# 真实出图路径见 dragon-assets/skills/render-deck —— 用系统 headless Chrome
# 把 HTML 渲染成 PNG，不依赖本 adapter。

set -euo pipefail

BAOYU_BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROVIDER="baoyu"

not_implemented() {
  echo "❌ $PROVIDER adapter 未接真后端：$1" >&2
  echo "   真实出图请用 dragon-assets/skills/render-deck（系统 headless Chrome）。" >&2
  exit 4
}

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
    if [[ ! -d "$BAOYU_BASE/$TARGET_SKILL" ]]; then
      not_implemented "目标 skill 不存在：$BAOYU_BASE/$TARGET_SKILL"
    fi
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
    not_implemented "download 不产出文件（不写占位内容）"
    ;;
  *)
    echo "用法: bash $0 {submit|poll|upload|download} [options]" >&2
    exit 2
    ;;
esac
