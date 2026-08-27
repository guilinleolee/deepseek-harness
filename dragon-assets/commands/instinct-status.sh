#!/bin/bash
# instinct-status 命令 - 显示学习到的模式

set -e

INSTINCTS_FILE="${INSTINCTS_FILE:-$HOME/.claude/instincts/instincts.json}"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查文件是否存在
if [ ! -f "$INSTINCTS_FILE" ]; then
  echo -e "${RED}❌ Instincts 文件不存在: $INSTINCTS_FILE${NC}"
  echo "提示: 运行 /learn 命令开始学习模式"
  exit 1
fi

# 解析 JSON
echo -e "${BLUE}🧠 九部天龙 Instinct 学习状态${NC}"
echo "================================"
echo ""

# 统计信息
TOTAL=$(jq '.metadata.total_instincts' "$INSTINCTS_FILE")
AVG_CONF=$(jq '.metadata.avg_confidence' "$INSTINCTS_FILE")
LAST_UPDATE=$(jq -r '.metadata.last_updated' "$INSTINCTS_FILE" | cut -d'T' -f1)

echo -e "${GREEN}📊 总体统计${NC}"
echo "  总模式数: $TOTAL"
echo "  平均置信度: $(echo "$AVG_CONF * 100" | bc)%"
echo "  最后更新: $LAST_UPDATE"
echo ""

# 按类别分组
echo -e "${BLUE}📁 按类别分组${NC}"
echo ""

jq -r '.instincts[] | "\(.category):\t\(.pattern)\t\(.confidence * 100)%\t\(.evidence_count) 证据"' "$INSTINCTS_FILE" | \
  awk -F'\t' '{
    category = $1
    pattern = $2
    confidence = $3
    evidence = $4

    if (category != prev_category) {
      if (prev_category != "") print ""
      printf "  📂 %s\n", category
      prev_category = category
    }

    # 置信度颜色
    if (confidence >= 90) color = "\033[0;32m"    # Green
    else if (confidence >= 70) color = "\033[1;33m"  # Yellow
    else color = "\033[0;31m"                      # Red

    printf "    • %s %s %s %s证据\033[0m\n", pattern, color, confidence, evidence
  }'

echo ""
echo ""

# 高置信度模式（>= 90%）
echo -e "${GREEN}🌟 高置信度模式 (>= 90%)${NC}"
echo ""

jq -r '.instincts[] | select(.confidence >= 0.9) | "\(.pattern)|\(.confidence * 100)|\(.evidence_count)|\(.source_master)"' "$INSTINCTS_FILE" | \
  awk -F'|' '{
    printf "  ✅ %s (%.0f%%, %d 证据, 来自 %s)\n", $1, $2, $3, $4
  }'

echo ""
echo ""

# 需要更多证据的模式（< 20 证据）
echo -e "${YELLOW}⚠️  需要更多证据的模式 (< 20 证据)${NC}"
echo ""

NEED_EVIDENCE=$(jq -r '.instincts[] | select(.evidence_count < 20) | "\(.pattern)|\(.evidence_count)"' "$INSTINCTS_FILE")

if [ -z "$NEED_EVIDENCE" ]; then
  echo "  🎉 所有模式都有充足的证据！"
else
  echo "$NEED_EVIDENCE" | awk -F'|' '{
    printf "  • %s (仅 %d 证据)\n", $1, $2
  }'
fi

echo ""
echo ""

# 按来源宗师统计
echo -e "${BLUE}🎭 按来源宗师统计${NC}"
echo ""

jq -r '.instincts[] | .source_master' "$INSTINCTS_FILE" | sort | uniq -c | sort -rn | \
  awk '{
    count = $1
    master = $2

    # 宗师名称映射
    split(master, parts, "-")
    name = parts[2]

    printf "  %s: %d 个模式\n", master, count
  }'

echo ""
echo ""

# 最近更新的模式
echo -e "${BLUE}🕐 最近学习到的模式${NC}"
echo ""

jq -r '.instincts[] | "\(.last_seen)|\(.pattern)|\(.evidence_count)"' "$INSTINCTS_FILE" | \
  sort -r | head -5 | \
  awk -F'|' '{
    datetime = $1
    pattern = $2
    evidence = $3
    date = substr(datetime, 1, 10)

    printf "  📅 %s: %s (%d 证据)\n", date, pattern, evidence
  }'

echo ""
echo "================================"
echo -e "${GREEN}💡 提示${NC}:"
echo "  • 使用 /instinct-export 导出模式到文件"
echo "  • 使用 /instinct-import 从文件导入模式"
echo "  • 使用 /evolve 将模式进化为 Skills"
echo "  • 使用 /learn 在对话中学习新模式"
