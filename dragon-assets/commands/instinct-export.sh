#!/bin/bash
# instinct-export 命令 - 导出模式到文件

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 显示帮助
show_help() {
  cat <<EOF
📤 Instinct Export - 导出学习到的模式到文件

用法:
  instinct-export [options] <output-file.json>

选项:
  --category <name>    仅导出指定类别
  --master <id>        仅导出指定宗师
  --min-conf <0-1>     仅导出高于此置信度的模式
  --format <json|csv>  输出格式（默认: json）

参数:
  output-file.json     输出文件路径

示例:
  # 导出所有模式
  instinct-export backup-instincts.json

  # 仅导出测试策略相关模式
  instinct-export --category testing-strategy testing-patterns.json

  # 仅导出 04-验证师的模式
  instinct-export --master 04-validator validator-patterns.json

  # 导出高置信度模式（>= 90%）
  instinct-export --min-conf 0.9 high-confidence.json

  # 导出为 CSV 格式
  instinct-export --format csv patterns.csv

说明:
  • 导出的文件可以分享给团队成员
  • 可通过 /instinct-import 在其他环境导入
  • 支持按类别、宗师、置信度过滤
  • JSON 格式支持完整数据，CSV 仅包含关键信息

EOF
}

# 默认参数
CATEGORY=""
MASTER=""
MIN_CONF=""
FORMAT="json"

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --category)
      CATEGORY="$2"
      shift 2
      ;;
    --master)
      MASTER="$2"
      shift 2
      ;;
    --min-conf)
      MIN_CONF="$2"
      shift 2
      ;;
    --format)
      FORMAT="$2"
      shift 2
      ;;
    --help|-h)
      show_help
      exit 0
      ;;
    -*)
      echo -e "${RED}❌ 未知选项: $1${NC}"
      show_help
      exit 1
      ;;
    *)
      OUTPUT_FILE="$1"
      shift
      ;;
  esac
done

# 检查输出文件
if [ -z "$OUTPUT_FILE" ]; then
  echo -e "${RED}❌ 缺少输出文件参数${NC}"
  show_help
  exit 1
fi

INSTINCTS_FILE="${INSTINCTS_FILE:-$HOME/.claude/instincts/instincts.json}"

# 检查源文件
if [ ! -f "$INSTINCTS_FILE" ]; then
  echo -e "${RED}❌ Instincts 文件不存在: $INSTINCTS_FILE${NC}"
  exit 1
fi

echo -e "${BLUE}📤 导出 Instincts${NC}"
echo "================================"
echo ""
echo "源文件: $INSTINCTS_FILE"
echo "输出文件: $OUTPUT_FILE"
echo ""

# 构建 jq 过滤器
FILTER=".instincts"

if [ -n "$CATEGORY" ]; then
  echo "过滤类别: $CATEGORY"
  FILTER="$FILTER | map(select(.category == \"$CATEGORY\"))"
fi

if [ -n "$MASTER" ]; then
  echo "过滤宗师: $MASTER"
  FILTER="$FILTER | map(select(.source_master == \"$MASTER\"))"
fi

if [ -n "$MIN_CONF" ]; then
  echo "最小置信度: $MIN_CONF"
  FILTER="$FILTER | map(select(.confidence >= $MIN_CONF))"
fi

# 导出逻辑
case "$FORMAT" in
  json)
    # JSON 格式 - 完整导出
    echo -e "${BLUE}📄 生成 JSON 格式...${NC}"

    # 构建完整的 JSON 输出
    EXPORT_JSON=$(jq "
      {
        instincts: $FILTER,
        metadata: {
          version: \"2.0.0\",
          exported_at: (now | todate),
          total_instincts: ($FILTER | length),
          export_filters: {
            category: \"$CATEGORY\",
            master: \"$MASTER\",
            min_confidence: \"$MIN_CONF\"
          }
        }
      }
    " "$INSTINCTS_FILE")

    echo "$EXPORT_JSON" > "$OUTPUT_FILE"

    # 统计
    COUNT=$(echo "$EXPORT_JSON" | jq '.metadata.total_instincts')
    ;;

  csv)
    # CSV 格式 - 简化导出
    echo -e "${BLUE}📄 生成 CSV 格式...${NC}"

    # CSV 表头
    echo "ID,Pattern,Category,Confidence,Evidence,Master" > "$OUTPUT_FILE"

    # CSV 数据
    jq -r "$FILTER | .[] | [
      .id,
      (.pattern | gsub(\"\\n\"; \" \") | gsub(\"\\\"\"; \"\\\\\\\"\")),
      .category,
      (.confidence * 100 | tostring + \"%\"),
      .evidence_count,
      .source_master
    ] | @csv" "$INSTINCTS_FILE" >> "$OUTPUT_FILE"

    COUNT=$(wc -l < "$OUTPUT_FILE")
    COUNT=$((COUNT - 1))  # 减去表头
    ;;

  *)
    echo -e "${RED}❌ 不支持的格式: $FORMAT${NC}"
    exit 1
    ;;
esac

echo -e "${GREEN}✅ 导出成功${NC}"
echo ""
echo "导出模式数: $COUNT"
echo "输出格式: $FORMAT"
echo "输出文件: $OUTPUT_FILE"
echo ""

# 显示预览
if [ "$FORMAT" = "json" ]; then
  echo -e "${BLUE}📋 导出预览:${NC}"
  echo ""
  echo "$EXPORT_JSON" | jq -r '.instincts[:3] | .[] | "  \(.confidence * 100 | floor)%\t\(.pattern)"' 2>/dev/null || echo ""

  if [ "$COUNT" -gt 3 ]; then
    echo "  ... 还有 $((COUNT - 3)) 个模式"
  fi
else
  echo -e "${BLUE}📋 前 5 行:${NC}"
  echo ""
  head -5 "$OUTPUT_FILE"
fi

echo ""
echo -e "${GREEN}💡 提示${NC}:"
echo "  • 使用 /instinct-import 在其他环境导入此文件"
echo "  • JSON 格式保留完整的示例和上下文信息"
echo "  • CSV 格式适合在 Excel 中分析和分享"
