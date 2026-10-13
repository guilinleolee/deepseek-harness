#!/usr/bin/env bash
# contact.sh · IR触达记录

set -e

STORAGE_DIR="${HOME}/.dragon-engine/opc/ir"
OUTREACH_FILE="${STORAGE_DIR}/outreach.json"

# 参数
INVESTOR_ID=""
CHANNEL="email"  # email, linkedin, meeting, phone
CONTENT=""
TIMESTAMP=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --investor-id) INVESTOR_ID="$2"; shift 2 ;;
    --channel) CHANNEL="$2"; shift 2 ;;
    --content) CONTENT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [ -z "$INVESTOR_ID" ] || [ -z "$CONTENT" ]; then
  echo "❌ 请提供 --investor-id 和 --content 参数"
  exit 1
fi

# 初始化存储
mkdir -p "$STORAGE_DIR"
if [ ! -f "$OUTREACH_FILE" ]; then
  echo '{"version": "1.0", "contacts": [], "created_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > "$OUTREACH_FILE"
fi

TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo ""
echo "📝 IR触达记录"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  投资人ID: $INVESTOR_ID"
echo "  渠道: $CHANNEL"
echo "  内容: $CONTENT"
echo "  时间: $TIMESTAMP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 渠道图标
CHANNEL_ICON="📧"
case $CHANNEL in
  email) CHANNEL_ICON="📧" ;;
  linkedin) CHANNEL_ICON="💼" ;;
  meeting) CHANNEL_ICON="🤝" ;;
  phone) CHANNEL_ICON="📞" ;;
  wechat) CHANNEL_ICON="💚" ;;
esac

# 保存记录
if command -v node &> /dev/null; then
  node -e "
const fs = require('fs');
const contact = {
  investor_id: '$INVESTOR_ID',
  channel: '$CHANNEL',
  content: '$CONTENT',
  timestamp: '$TIMESTAMP'
};
let data;
try {
  data = JSON.parse(fs.readFileSync('$OUTREACH_FILE', 'utf8'));
} catch(e) {
  data = { version: '1.0', contacts: [] };
}
data.contacts.push(contact);
fs.writeFileSync('$OUTREACH_FILE', JSON.stringify(data, null, 2));
console.log('✅ 触达记录已保存');
"
fi

echo ""
echo "💡 下一步: ./update.sh --investor-id $INVESTOR_ID --status pitched"
