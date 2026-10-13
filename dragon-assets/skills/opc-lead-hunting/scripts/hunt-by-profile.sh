#!/usr/bin/env bash
# hunt-by-profile.sh · 按创作者画像挖掘潜客

set -e

STORAGE_DIR="${HOME}/.dragon-engine/opc/leads"
INDEX_FILE="${STORAGE_DIR}/index.json"

# 参数
COMPETITOR=""
MIN_FOLLOWERS=""
INDUSTRIES=""
PLATFORM="xiaohongshu"
LIMIT=50

while [[ $# -gt 0 ]]; do
  case $1 in
    --competitor) COMPETITOR="$2"; shift 2 ;;
    --min-followers) MIN_FOLLOWERS="$2"; shift 2 ;;
    --industries) INDUSTRIES="$2"; shift 2 ;;
    --platform) PLATFORM="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [ -z "$COMPETITOR" ]; then
  echo "❌ 请提供 --competitor 参数"
  exit 1
fi

echo ""
echo "🎯 潜客挖掘 - 创作者画像匹配"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  竞对博主: $COMPETITOR"
echo "  平台: $PLATFORM"
[ -n "$MIN_FOLLOWERS" ] && echo "  最低粉丝: $MIN_FOLLOWERS"
[ -n "$INDUSTRIES" ] && echo "  行业: $INDUSTRIES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 初始化存储
mkdir -p "$STORAGE_DIR/profiles"
if [ ! -f "$INDEX_FILE" ]; then
  echo '{"version": "1.0", "leads": [], "created_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > "$INDEX_FILE"
fi

# TODO: 接入天龙引擎 MCP 获取竞对数据
# 目前为模拟数据
echo "📡 正在连接平台数据..."

# 生成模拟潜客数据
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
LEAD_ID="lead_$(date +%Y%m%d%H%M%S)"

cat <<EOF
{
  "lead_id": "$LEAD_ID",
  "source": "competitor_analysis",
  "competitor": "$COMPETITOR",
  "platform": "$PLATFORM",
  "profile": {
    "nickname": "潜在客户_${RANDOM:0:4}",
    "followers": $((RANDOM % 50000 + 5000)),
    "following": $((RANDOM % 1000 + 100)),
    "avg_engagement": "$((RANDOM % 10 + 2))%"
  },
  "match_score": $((RANDOM % 30 + 70)),
  "industries": ["${INDUSTRIES:-电商}"],
  "discovery_keywords": ["${INDUSTRIES:-电商}", "创业"],
  "status": "new",
  "discovered_at": "$TIMESTAMP"
}
EOF

echo ""
echo "✅ 潜客已记录: $LEAD_ID"

# 保存到数据库
if command -v node &> /dev/null; then
  mkdir -p "$STORAGE_DIR/profiles"
  node -e "
const fs = require('fs');
const lead = {
  lead_id: '$LEAD_ID',
  source: 'competitor_analysis',
  competitor: '$COMPETITOR',
  platform: '$PLATFORM',
  status: 'new',
  discovered_at: '$TIMESTAMP'
};
let data;
try {
  data = JSON.parse(fs.readFileSync('$INDEX_FILE', 'utf8'));
} catch(e) {
  data = { version: '1.0', leads: [] };
}
data.leads.push(lead);
fs.writeFileSync('$INDEX_FILE', JSON.stringify(data, null, 2));
console.log('✅ 已更新潜客索引');
"
fi

echo ""
echo "💡 下一步: ./rank-leads.sh 排序潜客"
echo "   或: ./hunt-by-comments.sh 评论区挖掘"
