#!/usr/bin/env bash
# add.sh · 添加投资人

set -e

STORAGE_DIR="${HOME}/.dragon-engine/opc/ir"
INVESTORS_FILE="${STORAGE_DIR}/investors.json"

# 参数
NAME=""
FIRM=""
TYPE="VC"  # VC, PE, CVC, Angel
MATCH_SCORE="medium"  # high, medium, low
STATUS="new"
LINKEDIN=""
NOTES=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --name) NAME="$2"; shift 2 ;;
    --firm) FIRM="$2"; shift 2 ;;
    --type) TYPE="$2"; shift 2 ;;
    --match-score) MATCH_SCORE="$2"; shift 2 ;;
    --status) STATUS="$2"; shift 2 ;;
    --linkedin) LINKEDIN="$2"; shift 2 ;;
    --notes) NOTES="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [ -z "$NAME" ]; then
  echo "❌ 请提供 --name 参数"
  exit 1
fi

# 初始化存储
mkdir -p "$STORAGE_DIR"
if [ ! -f "$INVESTORS_FILE" ]; then
  echo '{"version": "1.0", "investors": [], "created_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > "$INVESTORS_FILE"
fi

# 生成投资人ID
INVESTOR_ID="inv_$(date +%Y%m%d%H%M%S)"
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo ""
echo "📝 添加投资人"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  投资人ID: $INVESTOR_ID"
echo "  姓名: $NAME"
[ -n "$FIRM" ] && echo "  机构: $FIRM"
echo "  类型: $TYPE"
echo "  匹配度: $MATCH_SCORE"
echo "  状态: $STATUS"
[ -n "$LINKEDIN" ] && echo "  LinkedIn: $LINKEDIN"
[ -n "$NOTES" ] && echo "  备注: $NOTES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 保存到数据库
if command -v node &> /dev/null; then
  node -e "
const fs = require('fs');
const inv = {
  investor_id: '$INVESTOR_ID',
  name: '$NAME',
  firm: '${FIRM:-unknown}',
  type: '$TYPE',
  match_score: '$MATCH_SCORE',
  status: '$STATUS',
  linkedin: '${LINKEDIN:-}',
  notes: '${NOTES:-}',
  created_at: '$TIMESTAMP',
  updated_at: '$TIMESTAMP'
};
let data;
try {
  data = JSON.parse(fs.readFileSync('$INVESTORS_FILE', 'utf8'));
} catch(e) {
  data = { version: '1.0', investors: [] };
}
data.investors.push(inv);
fs.writeFileSync('$INVESTORS_FILE', JSON.stringify(data, null, 2));
console.log('✅ 投资人已添加: $INVESTOR_ID');
"
else
  echo "⚠️ Node.js 不可用，仅显示记录"
fi

echo ""
echo "💡 下一步:"
echo "   ./contact.sh --investor-id $INVESTOR_ID --channel email"
echo "   ./update.sh --investor-id $INVESTOR_ID --status researched"
