#!/usr/bin/env bash
# review.sh · T+3d 复盘脚本

set -e

STORAGE_DIR="${HOME}/.dragon-engine/opc"
REVIEWS_FILE="${STORAGE_DIR}/reviews.json"
SCORES_FILE="${STORAGE_DIR}/scores.json"

# 参数
DRAFT_ID=""
ACTUAL_VIEWS=""
ACTUAL_LIKES=""
ACTUAL_COMMENTS=""
ACTUAL_SHARES=""
ACTUAL_PLATFORM=""
NOTES=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --draft-id) DRAFT_ID="$2"; shift 2 ;;
    --actual-views) ACTUAL_VIEWS="$2"; shift 2 ;;
    --actual-likes) ACTUAL_LIKES="$2"; shift 2 ;;
    --actual-comments) ACTUAL_COMMENTS="$2"; shift 2 ;;
    --actual-shares) ACTUAL_SHARES="$2"; shift 2 ;;
    --actual-platform) ACTUAL_PLATFORM="$2"; shift 2 ;;
    --notes) NOTES="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [ -z "$DRAFT_ID" ]; then
  echo "❌ 请提供 --draft-id 参数"
  exit 1
fi

# 计算实际互动率
if [ -n "$ACTUAL_VIEWS" ] && [ -n "$ACTUAL_LIKES" ]; then
  ACTUAL_ER=$(echo "scale=2; ($ACTUAL_LIKES / $ACTUAL_VIEWS) * 100" | bc)
else
  ACTUAL_ER="N/A"
fi

# 构建复盘记录
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
REVIEW_RECORD=$(cat <<EOF
{
  "timestamp": "$TIMESTAMP",
  "draft_id": "$DRAFT_ID",
  "actual": {
    "views": ${ACTUAL_VIEWS:-0},
    "likes": ${ACTUAL_LIKES:-0},
    "comments": ${ACTUAL_COMMENTS:-0},
    "shares": ${ACTUAL_SHARES:-0},
    "platform": "${ACTUAL_PLATFORM:-unknown}",
    "er": "${ACTUAL_ER}"
  },
  "notes": "${NOTES}"
}
EOF
)

echo ""
echo "📋 T+3d 复盘记录"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  草稿ID: $DRAFT_ID"
echo "  平台: ${ACTUAL_PLATFORM:-unknown}"
echo "  时间: $TIMESTAMP"
echo ""
echo "  实际数据:"
echo "    播放量: ${ACTUAL_VIEWS:-0}"
echo "    点赞数: ${ACTUAL_LIKES:-0}"
echo "    评论数: ${ACTUAL_COMMENTS:-0}"
echo "    转发数: ${ACTUAL_SHARES:-0}"
echo "    互动率: ${ACTUAL_ER}%"
echo ""

if [ -n "$NOTES" ]; then
  echo "  备注: $NOTES"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 保存复盘记录
mkdir -p "$STORAGE_DIR"
if [ ! -f "$REVIEWS_FILE" ]; then
  echo '{"version": "1.0", "reviews": [], "created_at": "'$TIMESTAMP'"}' > "$REVIEWS_FILE"
fi

if command -v node &> /dev/null; then
  node -e "
const fs = require('fs');
let data;
try {
  data = JSON.parse(fs.readFileSync('$REVIEWS_FILE', 'utf8'));
} catch(e) {
  data = { version: '1.0', reviews: [], created_at: '$TIMESTAMP' };
}
data.reviews.push($REVIEW_RECORD);
fs.writeFileSync('$REVIEWS_FILE', JSON.stringify(data, null, 2));
console.log('✅ 复盘记录已保存');
"
fi

echo ""
echo "💡 提示: 运行 ./evolve.sh --period 7d 可基于复盘数据优化 rubric"
