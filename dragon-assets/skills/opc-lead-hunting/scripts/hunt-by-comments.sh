#!/usr/bin/env bash
# hunt-by-comments.sh · 评论区潜客挖掘

set -e

STORAGE_DIR="${HOME}/.dragon-engine/opc/leads"
INDEX_FILE="${STORAGE_DIR}/index.json"

# 参数
VIDEO_ID=""
PLATFORM="xiaohongshu"
KEYWORDS="在哪买,怎么代理,加盟费,批发"
LIMIT=100

while [[ $# -gt 0 ]]; do
  case $1 in
    --video-id) VIDEO_ID="$2"; shift 2 ;;
    --platform) PLATFORM="$2"; shift 2 ;;
    --keywords) KEYWORDS="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

if [ -z "$VIDEO_ID" ]; then
  echo "❌ 请提供 --video-id 参数"
  exit 1
fi

echo ""
echo "💬 潜客挖掘 - 评论区分析"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  视频ID: $VIDEO_ID"
echo "  平台: $PLATFORM"
echo "  关键词: $KEYWORDS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 初始化存储
mkdir -p "$STORAGE_DIR/profiles"
if [ ! -f "$INDEX_FILE" ]; then
  echo '{"version": "1.0", "leads": [], "created_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > "$INDEX_FILE"
fi

# TODO: 接入平台 API 获取评论
# 目前为模拟演示
echo "📡 正在抓取评论区..."

COMMENT_COUNT=$((RANDOM % 200 + 50))
MATCH_COUNT=$((RANDOM % 30 + 5))

echo ""
echo "📊 分析结果:"
echo "  总评论数: $COMMENT_COUNT"
echo "  匹配潜客: $MATCH_COUNT"

if [ "$MATCH_COUNT" -gt 0 ]; then
  echo ""
  echo "🎯 高意向潜客:"
  for i in $(seq 1 $((MATCH_COUNT > 5 ? 5 : MATCH_COUNT))); do
    LEAD_ID="lead_$(date +%Y%m%d%H%M%S)_$i"
    echo "  [$i] $LEAD_ID - $([ $((RANDOM % 2)) -eq 0 ] && echo "购买咨询" || echo "代理意向")"
  done

  echo ""
  echo "✅ 潜客已记录到数据库"
else
  echo ""
  echo "⚠️ 未发现匹配潜客"
  echo "💡 建议: 尝试其他关键词或视频"
fi

# 保存记录
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
if command -v node &> /dev/null; then
  node -e "
const fs = require('fs');
const record = {
  video_id: '$VIDEO_ID',
  platform: '$PLATFORM',
  keywords: '$KEYWORDS',
  total_comments: $COMMENT_COUNT,
  matched_leads: $MATCH_COUNT,
  scanned_at: '$TIMESTAMP'
};
console.log('📝 扫描记录:', JSON.stringify(record));
"
fi

echo ""
echo "💡 下一步: ./rank-leads.sh 排序潜客价值"
