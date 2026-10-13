#!/usr/bin/env bash
# add.sh · 添加BD潜客

set -e

STORAGE_DIR="${HOME}/.dragon-engine/opc/bd"
LEADS_FILE="${STORAGE_DIR}/leads.json"

# 参数
PLATFORM=""
CREATOR_ID=""
NICKNAME=""
QUALIFIED=0
INDUSTRY=""
NOTES=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --platform) PLATFORM="$2"; shift 2 ;;
    --creator-id) CREATOR_ID="$2"; shift 2 ;;
    --nickname) NICKNAME="$2"; shift 2 ;;
    --qualified) QUALIFIED="$2"; shift 2 ;;
    --industry) INDUSTRY="$2"; shift 2 ;;
    --notes) NOTES="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [ -z "$CREATOR_ID" ]; then
  echo "❌ 请提供 --creator-id 参数"
  exit 1
fi

# 初始化存储
mkdir -p "$STORAGE_DIR"
if [ ! -f "$LEADS_FILE" ]; then
  echo '{"version": "1.0", "leads": [], "created_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > "$LEADS_FILE"
fi

# 生成潜客ID
LEAD_ID="lead_$(date +%Y%m%d%H%M%S)"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo ""
echo "📝 添加BD潜客"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  潜客ID: $LEAD_ID"
[ -n "$PLATFORM" ] && echo "  平台: $PLATFORM"
echo "  创作者ID: $CREATOR_ID"
[ -n "$NICKNAME" ] && echo "  昵称: $NICKNAME"
echo "  符合条件: $([ "$QUALIFIED" = "1" ] && echo '✅ 是' || echo '❌ 否')"
[ -n "$INDUSTRY" ] && echo "  行业: $INDUSTRY"
[ -n "$NOTES" ] && echo "  备注: $NOTES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 保存到数据库
if command -v node &> /dev/null; then
  node -e "
const fs = require('fs');
const lead = {
  lead_id: '$LEAD_ID',
  platform: '${PLATFORM:-unknown}',
  creator_id: '$CREATOR_ID',
  nickname: '${NICKNAME:-unknown}',
  qualified: ${QUALIFIED},
  industry: '${INDUSTRY:-general}',
  notes: '${NOTES:-}',
  status: 'new',
  created_at: '$TIMESTAMP',
  updated_at: '$TIMESTAMP'
};
let data;
try {
  data = JSON.parse(fs.readFileSync('$LEADS_FILE', 'utf8'));
} catch(e) {
  data = { version: '1.0', leads: [] };
}
data.leads.push(lead);
fs.writeFileSync('$LEADS_FILE', JSON.stringify(data, null, 2));
console.log('✅ 潜客已添加: $LEAD_ID');
"
else
  echo "⚠️ Node.js 不可用，仅显示记录"
fi

echo ""
echo "💡 下一步:"
echo "   ./contact.sh --lead-id $LEAD_ID --channel dm --content '发送邀约'"
echo "   ./update.sh --lead-id $LEAD_ID --status contacted"
