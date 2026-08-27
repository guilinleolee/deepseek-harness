#!/bin/bash
# instinct-import 命令 - 从文件导入模式

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# 显示帮助
show_help() {
  cat <<EOF
📥 Instinct Import - 从文件导入学习到的模式

用法:
  instinct-import <file.json>

参数:
  file.json    要导入的 instincts JSON 文件

示例:
  instinct-import backup-instincts.json
  instinct-import /tmp/team-patterns.json

说明:
  • 导入的文件必须符合 instincts schema
  • 已存在的模式会被更新（保留最高置信度）
  • 新模式会被添加到现有列表
  • 原始文件会被备份为 instincts.json.backup

EOF
}

# 检查参数
if [ $# -lt 1 ]; then
  show_help
  exit 1
fi

IMPORT_FILE="$1"
INSTINCTS_DIR="${INSTINCTS_DIR:-$HOME/.claude/instincts}"
INSTINCTS_FILE="$INSTINCTS_DIR/instincts.json"

# 检查导入文件是否存在
if [ ! -f "$IMPORT_FILE" ]; then
  echo -e "${RED}❌ 文件不存在: $IMPORT_FILE${NC}"
  exit 1
fi

# 验证 JSON 格式
if ! jq empty "$IMPORT_FILE" 2>/dev/null; then
  echo -e "${RED}❌ 无效的 JSON 格式: $IMPORT_FILE${NC}"
  exit 1
fi

echo -e "${BLUE}📥 导入 Instincts${NC}"
echo "================================"
echo ""
echo "导入文件: $IMPORT_FILE"
echo "目标文件: $INSTINCTS_FILE"
echo ""

# 检查目标文件是否存在
if [ ! -f "$INSTINCTS_FILE" ]; then
  echo -e "${YELLOW}⚠️  目标文件不存在，创建新文件${NC}"

  # 创建目录
  mkdir -p "$INSTINCTS_DIR"

  # 复制文件
  cp "$IMPORT_FILE" "$INSTINCTS_FILE"

  echo -e "${GREEN}✅ 导入成功${NC}"
  echo ""
  jq -r '.metadata.total_instincts' "$INSTINCTS_FILE" | xargs -I {} echo "  总模式数: {}"
  exit 0
fi

# 备份现有文件
BACKUP_FILE="$INSTINCTS_FILE.backup.$(date +%Y%m%d_%H%M%S)"
echo "备份现有文件到: $BACKUP_FILE"
cp "$INSTINCTS_FILE" "$BACKUP_FILE"

# 统计信息
OLD_COUNT=$(jq '.metadata.total_instincts' "$INSTINCTS_FILE")
IMPORT_COUNT=$(jq '.metadata.total_instincts' "$IMPORT_FILE")

echo ""
echo "现有模式: $OLD_COUNT"
echo "导入模式: $IMPORT_COUNT"
echo ""

# 合并 instincts
echo -e "${BLUE}🔄 合并模式...${NC}"
echo ""

# 使用 jq 合并两个文件
MERGED_JSON=$(jq -s '
  # 合并 instincts 数组
  def merge_instincts(existing, new):
    # 创建已存在 ID 的映射
    reduce existing[].id as $id ({}; .[$id] = true) as $existing_ids |
    # 遍历新模式
    reduce new[] as $new (
      existing;
      # 检查是否已存在
      if .[].id == $new.id then
        # 更新现有模式（保留最高置信度）
        map(if .id == $new.id then
          {
            id: .id,
            pattern: (if (.confidence >= $new.confidence) then .pattern else $new.pattern end),
            confidence: (if (.confidence >= $new.confidence) then .confidence else $new.confidence end),
            evidence_count: (.evidence_count + $new.evidence_count),
            last_seen: (if (.last_seen > $new.last_seen) then .last_seen else $new.last_seen end),
            category: .category,
            context: .context,
            examples: (.examples + $new.examples | unique_by(.description)),
            source_master: .source_master
          }
        else .
        end)
      else
        # 添加新模式
        . + [$new]
      end
    );

  # 执行合并
  {
    instincts: merge_instincts(.[0].instincts, .[1].instincts),
    metadata: {
      version: "2.0.0",
      last_updated: (now | todate),
      total_instincts: (merge_instincts(.[0].instincts, .[1].instincts) | length),
      avg_confidence: (merge_instincts(.[0].instincts, .[1].instincts) | map(.confidence) | add / length)
    }
  }
' "$INSTINCTS_FILE" "$IMPORT_FILE")

# 写入合并后的文件
echo "$MERGED_JSON" > "$INSTINCTS_FILE"

# 统计结果
NEW_COUNT=$(jq '.metadata.total_instincts' "$INSTINCTS_FILE")
NEW_AVG=$(jq '.metadata.avg_confidence' "$INSTINCTS_FILE")

echo -e "${GREEN}✅ 导入成功${NC}"
echo ""
echo "统计结果:"
echo "  原有模式: $OLD_COUNT"
echo "  导入模式: $IMPORT_COUNT"
echo "  合并后: $NEW_COUNT"
echo "  新增: $((NEW_COUNT - OLD_COUNT))"
echo "  平均置信度: $(echo "$NEW_AVG * 100" | bc)%"
echo ""

# 显示新增的模式
ADDED=$(jq -s '
  def merge_instincts(existing, new):
    reduce existing[].id as $id ({}; .[$id] = true) as $existing_ids |
    reduce new[] as $new (
      existing;
      if ([.[].id] | index($new.id)) == null then
        . + [$new]
      else .
      end
    );

  merge_instincts(.[0].instincts, .[1].instincts) | map(.pattern)
' "$INSTINCTS_FILE" "$IMPORT_FILE")

if [ -n "$ADDED" ]; then
  echo -e "${BLUE}🆕 新增模式:${NC}"
  echo "$ADDED" | while read -r pattern; do
    echo "  • $pattern"
  done
fi

echo ""
echo "备份文件: $BACKUP_FILE"
