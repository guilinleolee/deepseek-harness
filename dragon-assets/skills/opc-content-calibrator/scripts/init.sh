#!/usr/bin/env bash
# init.sh · OPC Content Calibrator 初始化脚本

set -e

STORAGE_DIR="${HOME}/.dragon-engine/opc"
CONFIG_FILE="${STORAGE_DIR}/config.json"
RUBRIC_FILE="${STORAGE_DIR}/rubric.json"
SCORES_FILE="${STORAGE_DIR}/scores.json"

# 默认 rubric 配置
DEFAULT_RUBRIC='{
  "version": "1.0",
  "dimensions": {
    "er": { "name": "Engagement Rate", "max": 5, "threshold": 3.0, "weight": 1.0 },
    "hp": { "name": "Hook Power", "max": 5, "threshold": 3.5, "weight": 1.2 },
    "sr": { "name": "Scroll Retention", "max": 5, "threshold": 3.0, "weight": 1.0 },
    "ql": { "name": "Quality", "max": 5, "threshold": 3.5, "weight": 1.2 },
    "na": { "name": "Novelty", "max": 5, "threshold": 2.5, "weight": 0.8 },
    "ab": { "name": "Aesthetic Beauty", "max": 5, "threshold": 3.0, "weight": 1.0 },
    "pv": { "name": "Promotion Value", "max": 5, "threshold": 2.5, "weight": 0.8 }
  },
  "gates": {
    "min_total_score": 21,
    "fail_on_any_below_2": true,
    "require_er_above_3": true
  },
  "created_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
  "updated_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
}'

# 默认配置
DEFAULT_CONFIG='{
  "version": "1.0",
  "mode": "standard",
  "auto_evolve": true,
  "review_period_days": 3,
  "min_samples_for_evolution": 10,
  "created_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
}'

echo "📊 OPC Content Calibrator 初始化"

# 创建目录
mkdir -p "$STORAGE_DIR"
echo "  ✓ 存储目录: $STORAGE_DIR"

# 初始化配置
if [ ! -f "$CONFIG_FILE" ]; then
  echo "$DEFAULT_CONFIG" > "$CONFIG_FILE"
  echo "  ✓ 配置文件已创建"
else
  echo "  ℹ 配置文件已存在: $CONFIG_FILE"
fi

# 初始化 rubric
if [ ! -f "$RUBRIC_FILE" ]; then
  echo "$DEFAULT_RUBRIC" > "$RUBRIC_FILE"
  echo "  ✓ Rubric 已创建"
else
  echo "  ℹ Rubric 已存在: $RUBRIC_FILE"
fi

# 初始化分数记录
if [ ! -f "$SCORES_FILE" ]; then
  echo '{"version": "1.0", "scores": [], "created_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > "$SCORES_FILE"
  echo "  ✓ 分数记录已创建"
else
  echo "  ℹ 分数记录已存在: $SCORES_FILE"
fi

echo ""
echo "✅ OPC Content Calibrator 初始化完成"
echo ""
echo "下一步:"
echo "  ./score.sh --er 4 --hp 3 --sr 4 ..."
echo "  ./calibrate.sh --blind"
echo "  ./review.sh --draft-id xxx --actual-views 10000 ..."
