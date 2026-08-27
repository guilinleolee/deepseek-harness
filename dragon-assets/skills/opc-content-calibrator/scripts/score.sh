#!/usr/bin/env bash
# score.sh · 7维打分脚本

set -e

STORAGE_DIR="${HOME}/.dragon-engine/opc"
RUBRIC_FILE="${STORAGE_DIR}/rubric.json"
SCORES_FILE="${STORAGE_DIR}/scores.json"

# 默认值
ER=0
HP=0
SR=0
QL=0
NA=0
AB=0
PV=0
DRAFT_ID=""
PLATFORM=""

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --er) ER="$2"; shift 2 ;;
    --hp) HP="$2"; shift 2 ;;
    --sr) SR="$2"; shift 2 ;;
    --ql) QL="$2"; shift 2 ;;
    --na) NA="$2"; shift 2 ;;
    --ab) AB="$2"; shift 2 ;;
    --pv) PV="$2"; shift 2 ;;
    --draft-id) DRAFT_ID="$2"; shift 2 ;;
    --platform) PLATFORM="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# 计算总分
TOTAL=$(echo "scale=1; $ER + $HP + $SR + $QL + $NA + $AB + $PV" | bc)
MAX_SCORE=35
PERCENT=$(echo "scale=1; ($TOTAL / $MAX_SCORE) * 100" | bc)

# 加载 rubric 检查阈值
if [ -f "$RUBRIC_FILE" ]; then
  THRESHOLD_ER=$(grep -o '"threshold": [0-9.]*' "$RUBRIC_FILE" | head -1 | grep -o '[0-9.]*' || echo "3")
  THRESHOLD_HP=$(grep -o '"threshold": [0-9.]*' "$RUBRIC_FILE" | head -2 | tail -1 | grep -o '[0-9.]*' || echo "3.5")
  THRESHOLD_QL=$(grep -o '"threshold": [0-9.]*' "$RUBRIC_FILE" | head -4 | tail -1 | grep -o '[0-9.]*' || echo "3.5")
  GATE_TOTAL=$(grep -o '"min_total_score": [0-9]*' "$RUBRIC_FILE" | grep -o '[0-9]*' | head -1 || echo "21")
else
  THRESHOLD_ER=3; THRESHOLD_HP=3.5; THRESHOLD_QL=3.5; GATE_TOTAL=21
fi

# 判断是否达标
PASSED=true
FAIL_REASONS=""

# 检查各维度
check_dim() {
  local score=$1
  local threshold=$2
  local name=$3
  local result=$(echo "$score >= $threshold" | bc -l)
  if [ "$result" != "1" ]; then
    PASSED=false
    FAIL_REASONS="$FAIL_REASONS\n  - $name ($score/$threshold)"
  fi
}

check_dim $ER $THRESHOLD_ER "ER"
check_dim $HP $THRESHOLD_HP "HP"
check_dim $QL $THRESHOLD_QL "QL"

# 检查总分
if (( $(echo "$TOTAL < $GATE_TOTAL" | bc -l) )); then
  PASSED=false
  FAIL_REASONS="$FAIL_REASONS\n  - 总分 ($TOTAL/$GATE_TOTAL)"
fi

# 输出结果
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 OPC 7维打分结果"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
printf "  %-5s %-8s %-12s\n" "维度" "得分" "状态"
echo "  ──────────────────────────────────────"
printf "  %-5s %-8s %-12s\n" "ER" "$ER/5" "$( [ $(echo "$ER >= $THRESHOLD_ER" | bc -l) == 1 ] && echo '✅' || echo '❌')"
printf "  %-5s %-8s %-12s\n" "HP" "$HP/5" "$( [ $(echo "$HP >= $THRESHOLD_HP" | bc -l) == 1 ] && echo '✅' || echo '❌')"
printf "  %-5s %-8s %-12s\n" "SR" "$SR/5" "$( [ $(echo "$SR >= 3" | bc -l) == 1 ] && echo '✅' || echo '⚠️')"
printf "  %-5s %-8s %-12s\n" "QL" "$QL/5" "$( [ $(echo "$QL >= $THRESHOLD_QL" | bc -l) == 1 ] && echo '✅' || echo '❌')"
printf "  %-5s %-8s %-12s\n" "NA" "$NA/5" "$( [ $(echo "$NA >= 2.5" | bc -l) == 1 ] && echo '✅' || echo '⚠️')"
printf "  %-5s %-8s %-12s\n" "AB" "$AB/5" "$( [ $(echo "$AB >= 3" | bc -l) == 1 ] && echo '✅' || echo '⚠️')"
printf "  %-5s %-8s %-12s\n" "PV" "$PV/5" "$( [ $(echo "$PV >= 2.5" | bc -l) == 1 ] && echo '✅' || echo '⚠️')"
echo ""
echo "  ──────────────────────────────────────"
printf "  %-5s %-8s %-12s\n" "总分" "$TOTAL/35" "(${PERCENT}%)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$PASSED" = true ]; then
  echo "🎉 状态: PASS ✅"
  echo ""
  echo "建议: 可以发布，建议同步到审核队列"
  RESULT="PASS"
else
  echo "⚠️ 状态: FAIL ❌"
  echo ""
  echo "不达标原因:$FAIL_REASONS"
  echo ""
  echo "建议: 优化内容后重新打分"
  RESULT="FAIL"
fi
echo ""

# 保存记录
if [ -f "$SCORES_FILE" ]; then
  # 追加到 scores 数组
  TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  NEW_SCORE=$(cat <<EOF
{
  "timestamp": "$TIMESTAMP",
  "draft_id": "${DRAFT_ID:-auto}",
  "platform": "${PLATFORM:-unknown}",
  "scores": {
    "er": $ER, "hp": $HP, "sr": $SR, "ql": $QL, "na": $NA, "ab": $AB, "pv": $PV
  },
  "total": $TOTAL,
  "max": 35,
  "percent": $PERCENT,
  "result": "$RESULT"
}
EOF
)

  # 使用 node 处理 JSON 追加（如果可用）
  if command -v node &> /dev/null; then
    node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('$SCORES_FILE', 'utf8'));
data.scores.push($NEW_SCORE);
fs.writeFileSync('$SCORES_FILE', JSON.stringify(data, null, 2));
"
  fi
fi

exit $([ "$RESULT" = "PASS" ] && echo 0 || echo 1)
