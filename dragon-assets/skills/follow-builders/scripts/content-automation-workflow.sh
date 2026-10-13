#!/bin/bash
# follow-builders 内容自动化工作流
# 用法: bash content-automation-workflow.sh [topic] [platform]

set -e

SKILL_DIR="$HOME/.claude/skills/follow-builders"
OUTPUT_DIR="$HOME/.claude/skills/follow-builders/output"
TOPIC="${1:-AI Agent}"
PLATFORM="${2:-wechat}"

echo "🚀 follow-builders 内容自动化工作流"
echo "========================================"
echo "主题: $TOPIC"
echo "平台: $PLATFORM"
echo ""

# Step 1: 获取最新Builder动态
echo "📊 Step 1: 获取最新AI Builder动态..."
cd "$SKILL_DIR"
if [ -f "scripts/prepare-digest.js" ]; then
    node scripts/prepare-digest.js > "$OUTPUT_DIR/digest.json" 2>/dev/null || echo "动态获取完成"
fi

# Step 2: 搜索相关内容
echo "🔍 Step 2: 搜索'$TOPIC'相关内容..."
if [ -f "feed-x.json" ]; then
    grep -i -A 5 "$TOPIC" feed-x.json > "$OUTPUT_DIR/related-content.json" 2>/dev/null || echo "无相关内容"
fi

# Step 3: 生成选题建议
echo "💡 Step 3: 生成选题建议..."
cat << EOF > "$OUTPUT_DIR/topic-suggestions.md"
# $TOPIC 选题建议

## 基于 follow-builders 数据源

### 热门Builder观点
$(grep -i "$TOPIC" feed-x.json 2>/dev/null | head -5 || echo "暂无相关观点")

### 推荐选题
1. $TOPIC 最新发展趋势分析
2. 25位AI Builder如何看待$TOPIC
3. $TOPIC 对开发者的意义
4. $TOPIC 商业化机会探讨

### 可引用素材
- 来源: follow-builders feed-x.json
- 更新时间: $(date '+%Y-%m-%d %H:%M:%S')
EOF

echo "✅ 选题建议已生成: $OUTPUT_DIR/topic-suggestions.md"

# Step 4: 协同deep-research
echo "📚 Step 4: 准备deep-research协同数据..."
cat << EOF > "$OUTPUT_DIR/research-context.json"
{
  "topic": "$TOPIC",
  "source": "follow-builders",
  "builders": [
    "Karpathy", "Swyx", "Andreessen", "Josh Woodward",
    "Harrison Chase", "Jerry Liu"
  ],
  "generated_at": "$(date -Iseconds)",
  "synergy_skills": [
    "deep-research",
    "research-to-wechat",
    "xiaohu-wechat-format"
  ]
}
EOF

echo "✅ 协同数据已生成: $OUTPUT_DIR/research-context.json"

# Step 5: 输出下一步指引
echo ""
echo "📋 下一步操作:"
echo "   1. 深度研究: /deep-research \"$TOPIC\" --source follow-builders"
echo "   2. 写作文章: /research-to-wechat --topic \"$TOPIC\""
echo "   3. 公众号排版: /xiaohu-wechat-format --input article.md --gallery"
echo ""
echo "📁 输出文件:"
echo "   - $OUTPUT_DIR/digest.json"
echo "   - $OUTPUT_DIR/related-content.json"
echo "   - $OUTPUT_DIR/topic-suggestions.md"
echo "   - $OUTPUT_DIR/research-context.json"