#!/bin/bash
# evolve 命令 - 将 Instincts 聚类进化为 Skills

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m'

# 显示帮助
show_help() {
  cat <<EOF
🧬 Evolve - 将 Instincts 进化为 Skills

用法:
  evolve [options] <output-directory>

选项:
  --category <name>      仅进化指定类别
  --min-evidence <n>     最小证据数（默认: 5）
  --min-confidence <0-1> 最小置信度（默认: 0.7）
  --cluster-size <n>     每个技能的最小模式数（默认: 3）
  --dry-run             仅分析不生成文件

参数:
  output-directory       输出目录（将创建在此目录下）

示例:
  # 进化所有模式
  evolve ~/.claude/skills/evolved

  # 仅进化测试策略相关模式
  evolve --category testing-strategy ~/.claude/skills/testing

  # 高置信度模式，每个技能至少 5 个模式
  evolve --min-confidence 0.9 --cluster-size 5 ~/.claude/skills/premium

  # 预览将生成的技能
  evolve --dry-run ~/.claude/skills

说明:
  • 根据类别和标签自动聚类相关模式
  • 生成符合 Skills 规范的 SKILL.md 文件
  • 保留置信度、证据和示例信息
  • 生成的技能可直接使用 /skills 管理

EOF
}

# 默认参数
CATEGORY=""
MIN_EVIDENCE=5
MIN_CONFIDENCE=0.7
CLUSTER_SIZE=3
DRY_RUN=false

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --category)
      CATEGORY="$2"
      shift 2
      ;;
    --min-evidence)
      MIN_EVIDENCE="$2"
      shift 2
      ;;
    --min-confidence)
      MIN_CONFIDENCE="$2"
      shift 2
      ;;
    --cluster-size)
      CLUSTER_SIZE="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
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
      OUTPUT_DIR="$1"
      shift
      ;;
  esac
done

# 检查输出目录
if [ -z "$OUTPUT_DIR" ]; then
  echo -e "${RED}❌ 缺少输出目录参数${NC}"
  show_help
  exit 1
fi

INSTINCTS_FILE="${INSTINCTS_FILE:-$HOME/.claude/instincts/instincts.json}"

# 检查源文件
if [ ! -f "$INSTINCTS_FILE" ]; then
  echo -e "${RED}❌ Instincts 文件不存在: $INSTINCTS_FILE${NC}"
  exit 1
fi

echo -e "${PURPLE}🧬 Instinct Evolution${NC}"
echo "================================"
echo ""
echo "源文件: $INSTINCTS_FILE"
echo "输出目录: $OUTPUT_DIR"
echo "最小证据数: $MIN_EVIDENCE"
echo "最小置信度: $MIN_CONFIDENCE"
echo "聚类大小: $CLUSTER_SIZE"
echo ""

# 过滤和聚类
echo -e "${BLUE}🔍 分析并聚类模式...${NC}"
echo ""

# 使用 jq 进行聚类分析
CLUSTERS=$(jq -r "
  .instincts
  | map(select(.evidence_count >= $MIN_EVIDENCE and .confidence >= $MIN_CONFIDENCE))
  | $(if [ -n "$CATEGORY" ]; then echo "map(select(.category == \"$CATEGORY\"))"; else echo "."; fi)
  | group_by(.category)
  | map({
      category: .[0].category,
      count: length,
      instincts: .
    })
  | map(select(.count >= $CLUSTER_SIZE))
" "$INSTINCTS_FILE")

# 统计
TOTAL_CLUSTERS=$(echo "$CLUSTERS" | jq 'length')
TOTAL_INSTINCTS=$(echo "$CLUSTERS" | jq '[.[].instincts | length] | add')

echo "发现聚类: $TOTAL_CLUSTERS"
echo "涉及模式: $TOTAL_INSTINCTS"
echo ""

if [ "$TOTAL_CLUSTERS" -eq 0 ]; then
  echo -e "${YELLOW}⚠️  没有找到符合条件的模式聚类${NC}"
  echo "提示: 尝试降低 --min-evidence 或 --min-confidence"
  exit 0
fi

# 显示聚类预览
echo -e "${BLUE}📋 聚类预览:${NC}"
echo ""

echo "$CLUSTERS" | jq -r '.[] | "
  📂 \(.category)
     模式数: \(.count)
     平均置信度: \([.instincts[].confidence] | add / length * 100 | floor)%
"' | sed 's/^/  /'

echo ""

# Dry run 模式
if [ "$DRY_RUN" = true ]; then
  echo -e "${YELLOW}🔍 Dry run 模式 - 不生成文件${NC}"
  exit 0
fi

# 生成 Skills
echo -e "${BLUE}🚀 开始进化...${NC}"
echo ""

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 为每个聚类生成 Skill
echo "$CLUSTERS" | jq -c '.[]' | while read -r cluster; do
  CATEGORY=$(echo "$cluster" | jq -r '.category')
  COUNT=$(echo "$cluster" | jq -r '.count')
  AVG_CONF=$(echo "$cluster" | jq '[.instincts[].confidence] | add / length * 100')

  # 技能名称（转义为文件名）
  SKILL_NAME=$(echo "$CATEGORY" | sed 's/[^a-zA-Z0-9]/-/g' | tr '[:upper:]' '[:lower:]')
  SKILL_DIR="$OUTPUT_DIR/$SKILL_NAME"
  SKILL_FILE="$SKILL_DIR/SKILL.md"

  echo -e "${GREEN}📦 生成技能: $CATEGORY${NC}"

  # 创建技能目录
  mkdir -p "$SKILL_DIR"

  # 生成 SKILL.md
  cat > "$SKILL_FILE" <<EOF
---
name: $SKILL_NAME
description: 从九部天龙 Instincts 学习系统进化而来的 $CATEGORY 模式集合
version: 2.0.0
author: 九部天龙 Evolution Engine
license: MIT
evolved_from: instincts
confidence: ${AVG_CONF}%
pattern_count: $COUNT
---

# $CATEGORY Patterns

## 🎯 概述

本技能由九部天龙 Instinct 学习系统自动生成，聚类了 $COUNT 个高置信度的 $CATEGORY 相关模式。

**进化统计**:
- 平均置信度: ${AVG_CONF}%
- 总证据数: $(echo "$cluster" | jq '[.instincts[].evidence_count] | add')
- 来源宗师: $(echo "$cluster" | jq '[.instincts[].source_master] | unique | join(", ")')

## 📚 模式集合

EOF

  # 添加每个模式
  echo "$cluster" | jq -r '.instincts[]' | while read -r instinct; do
    PATTERN=$(echo "$instinct" | jq -r '.pattern')
    CONFIDENCE=$(echo "$instinct" | jq -r '.confidence * 100')
    EVIDENCE=$(echo "$instinct" | jq -r '.evidence_count')
    SOURCE=$(echo "$instinct" | jq -r '.source_master')
    ID=$(echo "$instinct" | jq -r '.id')

    cat >> "$SKILL_FILE" <<EOF

### $(echo "$instinct" | jq -r '.pattern') **(${CONFIDENCE}% 置信度, ${EVIDENCE} 证据)**

**来源**: ${SOURCE}
**模式ID**: ${ID}

EOF

    # 添加示例
    EXAMPLES=$(echo "$instinct" | jq -r '.examples[]? // empty')
    if [ -n "$EXAMPLES" ]; then
      echo "**示例**:" >> "$SKILL_FILE"
      echo "" >> "$SKILL_FILE"
      echo "$instinct" | jq -r '.examples[]? |
"#### \(.description)

\`\`\`[.language]
\(.code)
\`\`\`

"
' | sed 's/\[.language\]/'$(echo "$instinct" | jq -r '.context.language // "text"')'/g' >> "$SKILL_FILE"
    fi

    # 添加标签
    TAGS=$(echo "$instinct" | jq -r '.context.tags[]? // empty' | paste -sd ',' -)
    if [ -n "$TAGS" ]; then
      echo "**标签**: \`${TAGS}\`" >> "$SKILL_FILE"
      echo "" >> "$SKILL_FILE"
    fi
  done

  # 添加使用说明
  cat >> "$SKILL_FILE" <<EOF

## 🔧 使用方法

本技能可用于以下场景：

EOF

  # 根据类别添加特定使用说明
  case "$CATEGORY" in
    testing-strategy)
      cat >> "$SKILL_FILE" <<EOF
- TDD 工作流规划
- 测试覆盖率分析
- 验证策略选择
EOF
      ;;
    ui-pattern)
      cat >> "$SKILL_FILE" <<EOF
- React 组件开发
- UI 状态管理
- 用户体验优化
EOF
      ;;
    error-handling)
      cat >> "$SKILL_FILE" <<EOF
- 异常处理设计
- 防御性编程
- 错误恢复策略
EOF
      ;;
    *)
      cat >> "$SKILL_FILE" <<EOF
- 代码审查
- 最佳实践参考
- 团队知识共享
EOF
      ;;
  esac

  # 添加元信息
  cat >> "$SKILL_FILE" <<EOF

## 📊 学习来源

本技能从以下宗师的实践中学习而来：

EOF

  echo "$cluster" | jq -r '[.instincts[].source_master] | unique | .[]' | while read -r master; do
    COUNT=$(echo "$cluster" | jq "[.instincts[] | select(.source_master == \"$master\")] | length")
    echo "- **${master}**: ${COUNT} 个模式" >> "$SKILL_FILE"
  done

  cat >> "$SKILL_FILE" <<EOF

## 🔄 持续进化

本技能由 Instinct 学习系统自动生成和更新。当有新的高置信度模式被学习时，技能将自动进化。

**最后进化**: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
**进化版本**: 2.0.0

---

**维护者**: 九部天龙 Evolution Engine
**原始数据**: ~/.claude/instincts/instincts.json
EOF

  echo "  ✅ 生成: $SKILL_FILE"
  echo "     模式数: $COUNT"
  echo ""
done

echo "================================"
echo -e "${GREEN}🎉 进化完成！${NC}"
echo ""
echo "生成目录: $OUTPUT_DIR"
echo "生成技能数: $TOTAL_CLUSTERS"
echo "涉及模式数: $TOTAL_INSTINCTS"
echo ""
echo -e "${BLUE}💡 后续操作${NC}:"
echo "  1. 检查生成的技能: ls $OUTPUT_DIR"
echo "  2. 测试技能: /skills install $OUTPUT_DIR/<skill-name>"
echo "  3. 分享技能: /skills publish $OUTPUT_DIR/<skill-name>"
