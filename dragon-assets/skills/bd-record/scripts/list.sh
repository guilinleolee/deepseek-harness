#!/usr/bin/env bash
# list.sh · BD潜客列表

set -e

STORAGE_DIR="${HOME}/.dragon-engine/opc/bd"
LEADS_FILE="${STORAGE_DIR}/leads.json"

# 参数
STATUS=""
LIMIT=50

while [[ $# -gt 0 ]]; do
  case $1 in
    --status) STATUS="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

echo ""
echo "📋 BD潜客列表"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
[ -n "$STATUS" ] && echo "  状态筛选: $STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查数据库
if [ ! -f "$LEADS_FILE" ]; then
  echo "❌ 数据库不存在，请先添加潜客: ./add.sh"
  exit 1
fi

# 读取并显示
if command -v node &> /dev/null; then
  node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('$LEADS_FILE', 'utf8'));
let leads = data.leads || [];

if ('$STATUS') {
  leads = leads.filter(l => l.status === '$STATUS');
}

leads = leads.slice(0, $LIMIT);

console.log('\\n找到 ' + leads.length + ' 条记录:\\n');

if (leads.length === 0) {
  console.log('  暂无潜客记录');
  process.exit(0);
}

// 状态图标
const icons = {
  new: '🆕',
  contacted: '📨',
  interested: '🤝',
  negotiating: '💰',
  closed: '✅',
  not_fit: '❌'
};

console.log('  ID                状态    平台    昵称                    跟进');
console.log('  ' + '─'.repeat(75));

leads.forEach(l => {
  const icon = icons[l.status] || '📋';
  const padId = (l.lead_id || '').slice(0, 18).padEnd(18);
  const padStatus = (l.status || '').padEnd(6);
  const padPlatform = (l.platform || '').padEnd(6);
  const padNickname = (l.nickname || 'unknown').slice(0, 20).padEnd(20);
  console.log('  ' + icon + ' ' + padId + ' ' + padStatus + ' ' + padPlatform + ' ' + padNickname);
});

console.log('\\n💡 使用 ./update.sh --lead-id <id> --status <new_status> 更新状态');
"
fi
