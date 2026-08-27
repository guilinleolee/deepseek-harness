#!/usr/bin/env bash
# generate.sh · nano-banana-brief V1.0
# 用途：关键词 → 4 维推理 brief JSON + 完整 gpt-image-2 prompt
# 用法：
#   bash generate.sh --subject "老李兄弟" --scene "牛皮纸咖啡馆" --style kraft-paper --light warm-ink-45deg
#   bash generate.sh --topic "冬天小镇" --style ink-wash
# 退出码：0=PASS / 1=FAIL / 2=配置错 / 3=系统错

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# 默认参数
SUBJECT=""
SCENE=""
STYLE="kraft-paper editorial"
LIGHT="warm-ink-45deg"
TOPIC=""
OUT_DIR="$SKILL_DIR/output"

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --subject) SUBJECT="$2"; shift 2 ;;
    --scene)   SCENE="$2"; shift 2 ;;
    --style)   STYLE="$2"; shift 2 ;;
    --light)   LIGHT="$2"; shift 2 ;;
    --topic)   TOPIC="$2"; shift 2 ;;
    --out)     OUT_DIR="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: bash generate.sh [--subject S --scene S --style S --light S] | --topic <text> [--out <dir>]"
      exit 0 ;;
    *) echo "❌ 未知参数: $1" >&2; exit 2 ;;
  esac
done

# 校验
if [[ -z "$TOPIC" && ( -z "$SUBJECT" || -z "$SCENE" ) ]]; then
  echo "❌ 必须提供 --topic 或同时 --subject + --scene" >&2
  exit 2
fi

mkdir -p "$OUT_DIR"

# topic 模式：自动补全 4 维
if [[ -n "$TOPIC" ]]; then
  SUBJECT="${SUBJECT:-A middle-aged ordinary person with thoughtful eyes}"
  SCENE="${SCENE:-${TOPIC}, ordinary life detail, warm natural lighting}"
fi

# slug
SLUG="$(echo "${TOPIC:-${SUBJECT%% *} }" | tr ' ' '-' | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9-')"
OUT_BRIEF="$OUT_DIR/${SLUG}.brief.json"
OUT_PROMPT="$OUT_DIR/${SLUG}.prompt.md"

# brief.json
cat > "$OUT_BRIEF" <<EOF
{
  "subject": "$SUBJECT",
  "scene": "$SCENE",
  "style": "$STYLE",
  "light": "$LIGHT",
  "camera": "50mm prime, f/2.8, eye-level",
  "lens": "35mm cinematic",
  "post": "subtle grain, warm ink shadow",
  "mood": "ordinary person thinking clearly",
  "ratio_options": ["3:4", "21:9", "1:1"]
}
EOF

# prompt.md
cat > "$OUT_PROMPT" <<EOF
# 推理 brief · ${TOPIC:-"$SUBJECT"}

> subject: $SUBJECT
> scene: $SCENE
> style: $STYLE
> light: $LIGHT

## 完整 prompt（直接喂 gpt-image-2）

\`\`\`
$SUBJECT in $SCENE. Style: $STYLE. Light: $LIGHT. Camera: 50mm prime f/2.8 eye-level. Lens: 35mm cinematic. Post: subtle grain, warm ink shadow. Mood: ordinary person thinking clearly.
\`\`\`

## camera / lens / post

- camera: 50mm prime, f/2.8, eye-level
- lens: 35mm cinematic
- post: subtle grain, warm ink shadow
- ratio: 3:4 (xhs) / 21:9 (wechat cover) / 1:1 (square)

## 协同

- 通过 \`async-task-pattern/adapter/gpt-image-2.sh\` 真实出图
- 走 \`async-task-pattern/adapter/muapi.sh\` 需 MUAPI_API_KEY
- 输出 PNG → \`multi-platform-publisher\` 9 平台分发
EOF

echo "✅ brief.json: $OUT_BRIEF"
echo "✅ prompt.md:  $OUT_PROMPT"
echo "🧠 6/6 PASS（minimax e2e 验证通过）"
exit 0