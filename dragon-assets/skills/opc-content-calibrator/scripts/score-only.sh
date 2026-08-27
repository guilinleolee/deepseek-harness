#!/usr/bin/env bash
# =============================================================================
# content-calibrator/score-only.sh - 打分结果校验脚本
# 来源: xiaobei/TeamWiseFlow (OpenClaw)
# 融合: dragon-engine OPC增强
# 日期: 2026-08-17
# =============================================================================

set -euo pipefail

# 默认值
PLATFORM=""
CONTENT_PATH=""
CAL_ER=""
CAL_HP=""
CAL_SR=""
CAL_QL=""
CAL_NA=""
CAL_AB=""
CAL_PV=""
SCORE_THRESHOLD=0  # 默认0=不拦截

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        --content-path)
            CONTENT_PATH="$2"
            shift 2
            ;;
        --cal-er)
            CAL_ER="$2"
            shift 2
            ;;
        --cal-hp)
            CAL_HP="$2"
            shift 2
            ;;
        --cal-sr)
            CAL_SR="$2"
            shift 2
            ;;
        --cal-ql)
            CAL_QL="$2"
            shift 2
            ;;
        --cal-na)
            CAL_NA="$2"
            shift 2
            ;;
        --cal-ab)
            CAL_AB="$2"
            shift 2
            ;;
        --cal-pv)
            CAL_PV="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# 校验必需参数
if [[ -z "$CAL_ER" ]] || [[ -z "$CAL_HP" ]] || [[ -z "$CAL_SR" ]] || \
   [[ -z "$CAL_QL" ]] || [[ -z "$CAL_NA" ]] || [[ -z "$CAL_AB" ]] || [[ -z "$CAL_PV" ]]; then
    echo "Error: All --cal-* parameters are required" >&2
    echo "Usage: $0 --cal-er N --cal-hp N --cal-sr N --cal-ql N --cal-na N --cal-ab N --cal-pv N [--platform X] [--content-path X]" >&2
    exit 1
fi

# 校验分数范围 (0-5)
for score in "$CAL_ER" "$CAL_HP" "$CAL_SR" "$CAL_QL" "$CAL_NA" "$CAL_AB" "$CAL_PV"; do
    if ! [[ "$score" =~ ^[0-5]$ ]]; then
        echo "Error: Score must be 0-5, got: $score" >&2
        exit 1
    fi
done

# 计算 composite
# formula: (ER×1.5 + HP×1.5 + SR×1.5 + QL + NA + AB + PV) / 8.5 × 2.0
COMPOSITE=$(python3 -c "
er = $CAL_ER
hp = $CAL_HP
sr = $CAL_SR
ql = $CAL_QL
na = $CAL_NA
ab = $CAL_AB
pv = $CAL_PV

composite = (er*1.5 + hp*1.5 + sr*1.5 + ql + na + ab + pv) / 8.5 * 2.0
print(round(composite, 2))
")

# 计算各维度是否通过阈值
PASSED=true
FAILING_DIMS="[]"
FAILING_DIMS_ARR=()

if [[ "$SCORE_THRESHOLD" -gt 0 ]]; then
    for dim in er hp sr ql na ab pv; do
        case $dim in
            er) score=$CAL_ER ;;
            hp) score=$CAL_HP ;;
            sr) score=$CAL_SR ;;
            ql) score=$CAL_QL ;;
            na) score=$CAL_NA ;;
            ab) score=$CAL_AB ;;
            pv) score=$CAL_PV ;;
        esac
        if [[ "$score" -le "$SCORE_THRESHOLD" ]]; then
            PASSED=false
            FAILING_DIMS_ARR+=(\"$dim\")
        fi
    done

    if [[ ${#FAILING_DIMS_ARR[@]} -gt 0 ]]; then
        FAILING_DIMS="[$(IFS=,; echo "${FAILING_DIMS_ARR[*]}")]"
    fi
fi

# 输出JSON
cat <<EOF
{
  "passed": $PASSED,
  "failing_dims": $FAILING_DIMS,
  "composite": $COMPOSITE,
  "scores": {
    "er": $CAL_ER,
    "hp": $CAL_HP,
    "sr": $CAL_SR,
    "ql": $CAL_QL,
    "na": $CAL_NA,
    "ab": $CAL_AB,
    "pv": $CAL_PV
  },
  "formula": "(ER×1.5 + HP×1.5 + SR×1.5 + QL + NA + AB + PV) / 8.5 × 2.0",
  "threshold": $SCORE_THRESHOLD
}
EOF
