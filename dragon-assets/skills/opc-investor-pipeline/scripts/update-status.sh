#!/usr/bin/env bash
# update-status.sh · 更新投资人状态

set -e

STORAGE_DIR="${HOME}/.dragon-engine/opc/investors"
INDEX_FILE="${STORAGE_DIR}/index.json"

# 参数
INVESTOR_ID=""
STATUS=""
NOTES=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --investor-id) INVESTOR_ID="$2"; shift 2 ;;
    --status) STATUS="$2"; shift 2 ;;
    --notes) NOTES="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [ -z "$INVESTOR_ID" ] || [ -z "$STATUS" ]; then
  echo "❌ 请提供 --investor-id 和 --status 参数"
  echo ""
  echo "可用状态:"
  echo "  new → identified → researched → pitched → meeting → DD → term → closed"
  echo "                                                              ↓"
  echo "                                                    not_interested"
  exit 1
fi

echo ""
echo "📝 更新投资人状态"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  投资人ID: $INVESTOR_ID"
echo "  新状态: $STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 更新数据库
if [ -f "$INDEX_FILE" ] && command -v node &> /dev/null; then
  node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('$INDEX_FILE', 'utf8'));
const inv = data.investors.find(i => i.investor_id === '$INVESTOR_ID');
if (inv) {
  const oldStatus = inv.status;
  inv.status = '$STATUS';
  inv.updated_at = '$(date -u +%Y-%m-%dT%H:%M:%SZ)';
  if ('$NOTES') inv.notes = '$NOTES';
  fs.writeFileSync('$INDEX_FILE', JSON.stringify(data, null, 2));
  console.log('✅ 状态已更新: ' + oldStatus + ' → $STATUS');
  console.log('');
  console.log('📊 当前状态机进度:');
  const stages = ['new', 'identified', 'researched', 'pitched', 'meeting', 'DD', 'term', 'closed'];
  const current = stages.indexOf('$STATUS');
  if (current >= 0) {
    const bar = '█'.repeat(current + 1) + '░'.repeat(7 - current);
    console.log('   [' + bar + '] ' + (current + 1) + '/8');
  }
} else {
  console.log('❌ 未找到投资人: $INVESTOR_ID');
  process.exit(1);
}
"
else
  echo "❌ 数据库文件不存在或无法更新"
  exit 1
fi

echo ""
echo "💡 下一步:"
echo "   ./view.sh --investor-id $INVESTOR_ID  查看完整记录"
