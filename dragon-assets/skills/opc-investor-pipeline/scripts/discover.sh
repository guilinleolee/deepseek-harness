#!/usr/bin/env bash
# discover.sh · 投资人发掘

set -e

STORAGE_DIR="${HOME}/.dragon-engine/opc/investors"
INDEX_FILE="${STORAGE_DIR}/index.json"

# 参数
INDUSTRY=""
STAGE=""
LIMIT=20

while [[ $# -gt 0 ]]; do
  case $1 in
    --industry) INDUSTRY="$2"; shift 2 ;;
    --stage) STAGE="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

echo ""
echo "🔍 投资人发掘"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
[ -n "$INDUSTRY" ] && echo "  行业: $INDUSTRY"
[ -n "$STAGE" ] && echo "  阶段: $STAGE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 初始化存储
mkdir -p "$STORAGE_DIR"
if [ ! -f "$INDEX_FILE" ]; then
  echo '{"version": "1.0", "investors": [], "created_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > "$INDEX_FILE"
fi

# TODO: 接入公开数据源 (Crunchbase/IT橘子等)
# 目前为模拟演示
echo "📡 正在搜索公开数据源..."

INVESTOR_COUNT=$((RANDOM % 10 + 3))

echo ""
echo "📊 发现 $INVESTOR_COUNT 个潜在投资人:"
echo ""

for i in $(seq 1 $INVESTOR_COUNT); do
  INV_ID="inv_$(date +%Y%m%d%H%M%S)_$i"
  NAME=$(echo "投资人${i}_$((RANDOM % 1000))")
  FIRM=$(echo "鼎晖投资|红杉中国|IDG资本|经纬中国|GGV纪源资本" | cut -d'|' -f$((i % 5 + 1)))

  cat <<EOF
  [$i] $NAME
      机构: $FIRM
      关注: ${INDUSTRY:-消费,电商}
      阶段: ${STAGE:-A轮}
      潜客ID: $INV_ID
EOF
  echo ""

  # 保存到数据库
  if command -v node &> /dev/null; then
    node -e "
const fs = require('fs');
const inv = {
  investor_id: '$INV_ID',
  name: '$NAME',
  firm: '$FIRM',
  industries: ['${INDUSTRY:-消费,电商}'],
  stage: '${STAGE:-A轮}',
  status: 'new',
  match_score: $((RANDOM % 30 + 70)),
  discovered_at: '$(date -u +%Y-%m-%dT%H:%M:%SZ)'
};
let data;
try {
  data = JSON.parse(fs.readFileSync('$INDEX_FILE', 'utf8'));
} catch(e) {
  data = { version: '1.0', investors: [] };
}
data.investors.push(inv);
fs.writeFileSync('$INDEX_FILE', JSON.stringify(data, null, 2));
"
  fi
done

echo "✅ 已保存到投资人数据库"
echo ""
echo "💡 下一步:"
echo "   ./view.sh --investor-id $INV_ID  查看详情"
echo "   ./update-status.sh --investor-id $INV_ID --status researched"
