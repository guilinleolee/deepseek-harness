#!/usr/bin/env bash
# =============================================================================
# content-calibrator/cal-toggle.sh - 平台校准开关管理
# 来源: xiaobei/TeamWiseFlow (OpenClaw)
# 融合: dragon-engine OPC增强
# 日期: 2026-08-17
# =============================================================================

set -euo pipefail

CALIBRATION_DIR="calibration"
STATE_FILE="$CALIBRATION_DIR/.cheat-state.json"

# 操作类型
ACTION=""
PLATFORM=""
THRESHOLD=""
REDUCTION_THRESHOLD=""

# 帮助信息
show_help() {
    cat << 'EOF'
content-calibrator - 平台校准开关管理

Usage:
  cal-toggle.sh --list                           # 列出所有平台状态
  cal-toggle.sh --platform <p> --enable         # 启用某平台校准
  cal-toggle.sh --platform <p> --disable          # 禁用某平台校准
  cal-toggle.sh --platform <p> --status          # 查看某平台状态
  cal-toggle.sh --set-threshold <N>              # 设置全局阈值(0-5)
  cal-toggle.sh --threshold                       # 查看当前阈值

Supported platforms: wx_mp, xhs, douyin, bilibili, zhihu, youtube, kuaishou, toutiao

Examples:
  # 启用小红书校准
  ./cal-toggle.sh --platform xhs --enable

  # 设置阈值:每维需>3才放行
  ./cal-toggle.sh --set-threshold 3

  # 查看所有平台
  ./cal-toggle.sh --list
EOF
}

# 列出所有平台
list_platforms() {
    echo "📊 Content Calibrator 状态"
    echo ""

    # 全局阈值
    if [[ -f "$STATE_FILE" ]]; then
        THRESHOLD=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('score_threshold', 0))")
        RUBRIC_VERSION=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('rubric_version', 'v0'))")
        SAMPLES=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('calibration_samples', 0))")
    else
        THRESHOLD=0
        RUBRIC_VERSION="v0"
        SAMPLES=0
    fi

    echo "【全局 rubric】"
    echo "  Rubric: $RUBRIC_VERSION"
    echo "  校准样本: $SAMPLES"
    echo ""
    echo "【全局阈值】每维需 >$THRESHOLD 才放行"
    echo ""
    echo "【平台】"

    for platform_dir in "$CALIBRATION_DIR"/*/; do
        [[ -d "$platform_dir" ]] || continue
        platform=$(basename "$platform_dir")
        [[ "$platform" == *.json ]] && continue

        state_file="$platform_dir/.platform-state.json"
        if [[ -f "$state_file" ]]; then
            enabled=$(python3 -c "import json; d=json.load(open('$state_file')); print(d.get('enabled', False))")
            baseline=$(python3 -c "import json; d=json.load(open('$state_file')); print(d.get('baseline', '未定'))")
            if [[ "$enabled" == "True" ]] || [[ "$enabled" == "true" ]]; then
                echo "  $platform ✅ 已启用  baseline: $baseline"
            else
                echo "  $platform ❌ 未启用  baseline: $baseline"
            fi
        else
            echo "  $platform ❌ 未初始化"
        fi
    done
    echo ""
}

# 启用平台
enable_platform() {
    if [[ -z "$PLATFORM" ]]; then
        echo "Error: --platform required" >&2
        exit 1
    fi

    state_file="$CALIBRATION_DIR/$PLATFORM/.platform-state.json"
    if [[ ! -f "$state_file" ]]; then
        echo "Error: Platform not initialized. Run init.sh first." >&2
        exit 1
    fi

    python3 -c "
import json
with open('$state_file', 'r') as f:
    d = json.load(f)
d['enabled'] = True
with open('$state_file', 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
"
    echo "✓ Enabled calibration for platform: $PLATFORM"
}

# 禁用平台
disable_platform() {
    if [[ -z "$PLATFORM" ]]; then
        echo "Error: --platform required" >&2
        exit 1
    fi

    state_file="$CALIBRATION_DIR/$PLATFORM/.platform-state.json"
    if [[ ! -f "$state_file" ]]; then
        echo "Error: Platform not initialized. Run init.sh first." >&2
        exit 1
    fi

    python3 -c "
import json
with open('$state_file', 'r') as f:
    d = json.load(f)
d['enabled'] = False
with open('$state_file', 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
"
    echo "✓ Disabled calibration for platform: $PLATFORM"
}

# 平台状态
status_platform() {
    if [[ -z "$PLATFORM" ]]; then
        echo "Error: --platform required" >&2
        exit 1
    fi

    state_file="$CALIBRATION_DIR/$PLATFORM/.platform-state.json"
    if [[ ! -f "$state_file" ]]; then
        echo "Platform not initialized: $PLATFORM"
        exit 1
    fi

    cat "$state_file" | python3 -m json.tool
}

# 设置阈值
set_threshold() {
    if [[ -z "$THRESHOLD" ]]; then
        echo "Error: --set-threshold <N> required" >&2
        exit 1
    fi

    if ! [[ "$THRESHOLD" =~ ^[0-5]$ ]]; then
        echo "Error: threshold must be 0-5" >&2
        exit 1
    fi

    mkdir -p "$CALIBRATION_DIR"

    if [[ -f "$STATE_FILE" ]]; then
        python3 -c "
import json
with open('$STATE_FILE', 'r') as f:
    d = json.load(f)
d['score_threshold'] = $THRESHOLD
with open('$STATE_FILE', 'w') as f:
    json.dump(d, f, indent=2, ensure_ascii=False)
"
    else
        cat > "$STATE_FILE" << EOF
{
  "mode": "cold-start",
  "calibration_samples": 0,
  "rubric_version": "v0",
  "last_bump_at": null,
  "score_threshold": $THRESHOLD
}
EOF
    fi

    echo "✓ Set global threshold to: $THRESHOLD (每维需 >$THRESHOLD 才放行)"
}

# 查看阈值
show_threshold() {
    if [[ -f "$STATE_FILE" ]]; then
        THRESHOLD=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('score_threshold', 0))")
        echo "Current global threshold: $THRESHOLD"
    else
        echo "Current global threshold: 0 (default, 不拦截)"
    fi
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --list)
            ACTION="list"
            shift
            ;;
        --enable)
            ACTION="enable"
            shift
            ;;
        --disable)
            ACTION="disable"
            shift
            ;;
        --status)
            ACTION="status"
            shift
            ;;
        --threshold)
            ACTION="show_threshold"
            shift
            ;;
        --set-threshold)
            THRESHOLD="$2"
            ACTION="set_threshold"
            shift 2
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            show_help
            exit 1
            ;;
    esac
done

# 执行操作
case "$ACTION" in
    list)
        list_platforms
        ;;
    enable)
        enable_platform
        ;;
    disable)
        disable_platform
        ;;
    status)
        status_platform
        ;;
    set_threshold)
        set_threshold
        ;;
    show_threshold)
        show_threshold
        ;;
    *)
        show_help
        exit 1
        ;;
esac
