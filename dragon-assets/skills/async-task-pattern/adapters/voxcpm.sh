#!/usr/bin/env bash
# adapter/voxcpm.sh · async-task-pattern V1.0
# 后端：VoxCPM TTS
# 异步方式：同步（< 30s）→ 模拟异步接口（submit 后立即 completed）
# KEY 需求：无
# 状态：**未接真后端**。submit/poll 只回显任务元数据，download 不产出文件。
#       未接真后端时退出码 4（未实现），与 async-task-pattern 协议一致。

set -euo pipefail

PROVIDER="voxcpm"

not_implemented() {
  echo "❌ $PROVIDER adapter 未接真后端：$1" >&2
  echo "   真实配音请接入 VoxCPM 服务后重跑本 adapter。" >&2
  exit 4
}

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
    not_implemented "download 不产出文件（不写占位内容）"
    ;;
  *)
    echo "用法: bash $0 {submit|poll|upload|download} [options]" >&2
    exit 2
    ;;
esac
