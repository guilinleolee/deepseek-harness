#!/usr/bin/env bash
# list.sh · IR投资人列表

set -e

STORAGE_DIR="${HOME}/.dragon-engine/opc/ir"
INVESTORS_FILE="${STORAGE_DIR}/investors.json"

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
echo "📋 IR投资人列表"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
[ -n "$STATUS" ] && echo "  状态筛选: $STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 检查数据库
if [ ! -f "$INVESTORS_FILE" ]; then
  echo "❌ 数据库不存在，请先添加投资人: ./add.sh"
  exit 1
fi

# 读取并显示
if command -v node &> /dev/null; then
  node -e "
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('$INVESTORS_FILE', 'utf8'));
let investors = data.investors || [];

if ('$STATUS') {
  investors = investors.filter(i => i.status === '$STATUS');
}

investors = investors.slice(0, $LIMIT);

console.log('\\n找到 ' + investors.length + ' 条记录:\\n');

if (investors.length === 0) {
  console.log('  暂无投资人记录');
  process.exit(0);
}

// 状态图标
const icons = {
  new: '🆕',
  identified: '🔍',
  researched: '📊',
  pitched: '📨',
  meeting: '🤝',
  DD: '📋',
  term: '💰',
  closed: '✅',
  not_interested: '❌'
};

console.log('  ID                姓名              机构              状态    匹配度');
console.log('  ' + '─'.repeat(80));

investors.forEach(i => {
  const icon = icons[i.status] || '📋';
  const padId = (i.investor_id || '').slice(0, 18).padEnd(18);
  const padName = (i.name || '').slice(0, 14).padEnd(14);
  const padFirm = (i.firm || '').slice(0, 14).padEnd(14);
  const padStatus = (i.status || '').padEnd(6);
  const padScore = (i.match_score || 'N/A').padEnd(4);
  console.log('  ' + icon + ' ' + padId + ' ' + padName + ' ' + padFirm + ' ' + padStatus + ' ' + padScore);
});

console.log('\\n💡 使用 ./update.sh --investor-id <id> --status <new_status> 更新状态');
"
fi
