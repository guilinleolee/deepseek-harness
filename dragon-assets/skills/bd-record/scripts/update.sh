#!/usr/bin/env bash
# update.sh · BD潜客状态更新

set -e

STORAGE_DIR="${HOME}/.dragon-engine/opc/bd"
LEADS_FILE="${STORAGE_DIR}/leads.json"

# 参数
LEAD_ID=""
STATUS=""
NOTES=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --lead-id) LEAD_ID="$2"; shift 2 ;;
    --status) STATUS="$2"; shift 2 ;;
    --notes) NOTES="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [ -z "$LEAD_ID" ] || [ -z "$STATUS" ]; then
  echo "❌ 请提供 --lead-id 和 --status 参数"
  echo ""
  echo "可用状态:"
  echo "  new → contacted → interested → negotiating → closed"
  echo "                                      ↓"
  echo "                                  not_fit"
  exit 1
fi

TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo ""
echo "📝 更新潜客状态"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  潜客ID: $LEAD_ID"
echo "  新状态: $STATUS"
[ -n "$NOTES" ] && echo "  备注: $NOTES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 状态图标
STATUS_ICON="📋"
case $STATUS in
  new) STATUS_ICON="🆕" ;;
  contacted) STATUS_ICON="📨" ;;
  interested) STATUS_ICON="🤝" ;;
  negotiating) STATUS_ICON="💰" ;;
  closed) STATUS_ICON="✅" ;;
  not_fit) STATUS_ICON="❌" ;;
esac

# 更新数据库
if [ -f "$LEADS_FILE" ] && command -v node &> /dev/null; then
  node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('$LEADS_FILE', 'utf8'));
const lead = data.leads.find(l => l.lead_id === '$LEAD_ID');
if (lead) {
  const oldStatus = lead.status;
  lead.status = '$STATUS';
  lead.updated_at = '$TIMESTAMP';
  if ('$NOTES') lead.notes = '$NOTES';
  fs.writeFileSync('$LEADS_FILE', JSON.stringify(data, null, 2));
  console.log('✅ 状态已更新: ' + oldStatus + ' → $STATUS');
} else {
  console.log('❌ 未找到潜客: $LEAD_ID');
  process.exit(1);
}
"
else
  echo "⚠️ 数据库文件不存在或无法更新"
fi

echo ""
echo "💡 下一步: ./contact.sh --lead-id $LEAD_ID --channel dm --content '跟进联系'"
