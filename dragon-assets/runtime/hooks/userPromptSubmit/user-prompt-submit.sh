---
license: UNKNOWN
---

#!/bin/bash

# 读取用户输入
USER_INPUT="$"
if [ -z "$USER_INPUT" ]; then
    USER_INPUT=$(cat)
fi

# 智能过滤：简短问题不优化（<30字）
INPUT_LENGTH=${#USER_INPUT}
if [ "$INPUT_LENGTH" -lt 10 ]; then
    echo "$USER_INPUT"
    exit 0
fi

# 简单回复不优化
case "$USER_INPUT" in
    好的|是的|继续|谢谢|ok|yes|no|确认|取消)
        echo "$USER_INPUT"
        exit 0
        ;;
esac

# 读取优化提示词模板
OPTIMIZER_PROMPT=$(cat ".claude/prompt-optimizer-meta.md")

# 构建优化请求
OPTIMIZATION_REQUEST="$OPTIMIZER_PROMPT

---

用户原始输入：$USER_INPUT

---

请严格按照格式输出优化结果。"

# 输出优化请求
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 提示词自动优化中..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "$OPTIMIZATION_REQUEST"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 优化完成，自动继续执行..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"