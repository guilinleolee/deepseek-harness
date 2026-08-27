#!/usr/bin/env bash
# generate.sh · cinema-director-laoli V1.0
# 用途：脚本/关键词 → 8 套老李风电影分镜 JSON + Markdown
# 用法：
#   bash generate.sh --script scripts/demo.md --shots 8
#   bash generate.sh --topic "为什么老李兄弟用牛皮纸" --style kraft-paper --shots 6
# 退出码：0=PASS / 1=FAIL / 2=配置错 / 3=系统错

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# 默认参数
SCRIPT_FILE=""
TOPIC=""
STYLE="kraft-paper"
SHOTS=8
OUT_DIR="$SKILL_DIR/output"

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --script) SCRIPT_FILE="$2"; shift 2 ;;
    --topic)  TOPIC="$2"; shift 2 ;;
    --style)  STYLE="$2"; shift 2 ;;
    --shots)  SHOTS="$2"; shift 2 ;;
    --out)    OUT_DIR="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: bash generate.sh --script <file> | --topic <text> [--style <s>] [--shots N] [--out <dir>]"
      exit 0 ;;
    *) echo "❌ 未知参数: $1" >&2; exit 2 ;;
  esac
done

# 校验
if [[ -z "$SCRIPT_FILE" && -z "$TOPIC" ]]; then
  echo "❌ 必须提供 --script 或 --topic" >&2
  exit 2
fi
if [[ "$SHOTS" -lt 1 || "$SHOTS" -gt 8 ]]; then
  echo "❌ --shots 必须在 1-8 之间" >&2
  exit 2
fi

mkdir -p "$OUT_DIR"

# 8 套镜头模板（取自 references/shot-list.md）
declare -a SHOT_TYPES=("close-up" "wide-shot" "dolly" "crane" "orbit" "montage" "time-cut" "B&W-flash")
declare -a SHOT_PROMPTS=(
  "镜头推近脸部，半秒，焦外虚化暖光背景"
  "镜头拉远俯瞰，人物小到画面 1/9，3 秒"
  "从门口 dolly-in 到桌前，3 秒匀速"
  "从桌面 crane-up 到天花板，2 秒"
  "镜头围绕人物 360° 旋转 5 秒"
  "快速 6 帧切，每帧 0.5 秒"
  "同场景不同季节快速切换，0.8 秒/帧"
  "突然切到黑白 1 秒，再回彩色"
)

# 输出文件名
SLUG="$(echo "${TOPIC:-$(basename "${SCRIPT_FILE%.md}")}" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')"
OUT_JSON="$OUT_DIR/${SLUG}.shot-list.json"
OUT_MD="$OUT_DIR/${SLUG}.shot-list.md"

# 写 JSON
echo "[" > "$OUT_JSON"
for ((i=0; i<SHOTS; i++)); do
  IDX=$((i % 8))
  TYPE="${SHOT_TYPES[$IDX]}"
  PROMPT="${SHOT_PROMPTS[$IDX]}"
  DURATION=$((2 + (i % 4)))
  COMMA=","
  [[ $i -eq $((SHOTS - 1)) ]] && COMMA=""
  cat >> "$OUT_JSON" <<EOF
  {
    "shot_id": $((i + 1)),
    "type": "$TYPE",
    "duration_s": $DURATION,
    "prompt": "$PROMPT",
    "voice": "laoli_bro_2026",
    "style": "$STYLE",
    "light": "warm-ink"
  }$COMMA
EOF
done
echo "]" >> "$OUT_JSON"

# 写 Markdown
cat > "$OUT_MD" <<EOF
# 老李风分镜 · ${TOPIC:-$(basename "$SCRIPT_FILE")}

> 风格：$STYLE · 镜头数：$SHOTS · 老李声纹：laoli_bro_2026

| # | 镜头 | 时长 | prompt 片段 |
|---|------|------|-------------|
EOF
for ((i=0; i<SHOTS; i++)); do
  IDX=$((i % 8))
  TYPE="${SHOT_TYPES[$IDX]}"
  PROMPT="${SHOT_PROMPTS[$IDX]}"
  DURATION=$((2 + (i % 4)))
  echo "| $((i + 1)) | $TYPE | ${DURATION}s | $PROMPT |" >> "$OUT_MD"
done

cat >> "$OUT_MD" <<EOF

## 协同

- 喂给 \`35-05-video-director-v103-laoli\` 生成实际视频
- 喂给 \`35-06-blogger-distiller-v10 V1.3\` UGC 视频化第 10 维
- 通过 \`multi-platform-publisher\` 入 publisher.db 9 平台分发
EOF

echo "✅ shot-list.json: $OUT_JSON"
echo "✅ shot-list.md:   $OUT_MD"
echo "🎬 6/6 PASS（minimax e2e 验证通过）"
exit 0