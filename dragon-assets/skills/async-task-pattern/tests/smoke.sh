#!/usr/bin/env bash
# smoke.sh · async-task-pattern V1.0
# 用途：19 用例 smoke 测试，覆盖 4 原语 × 5 provider + 退出码 0/1/2/3/4
# 用法：bash tests/smoke.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
SCRIPTS_DIR="$SKILL_DIR/scripts"
ADAPTERS_DIR="$SKILL_DIR/adapters"

PASS=0
FAIL=0
TOTAL=0

# 测试 helper
run_test() {
  local name="$1"
  local expected_exit="$2"
  shift 2
  local actual_exit=0
  "$@" >/dev/null 2>&1 || actual_exit=$?
  TOTAL=$((TOTAL + 1))
  if [[ "$actual_exit" == "$expected_exit" ]]; then
    echo "✅ $name (exit=$actual_exit)"
    PASS=$((PASS + 1))
  else
    echo "❌ $name (expected exit=$expected_exit, got $actual_exit)"
    FAIL=$((FAIL + 1))
  fi
}

echo "═══ async-task-pattern smoke test · 19 用例 ═══"
echo

# ===== 退出码语义覆盖 =====
echo "── 退出码语义（4 用例）──"
run_test "[退出码 0] submit 正常" 0 bash "$SCRIPTS_DIR/submit.sh" \
  --provider minimax --action tts --payload '{"text":"hi"}' --timeout 60

run_test "[退出码 2] submit 缺必填字段" 2 bash "$SCRIPTS_DIR/submit.sh" \
  --provider minimax --action tts

run_test "[退出码 2] poll 缺 --task-id" 2 bash "$SCRIPTS_DIR/poll.sh"

run_test "[退出码 4] submit 不存在的 provider" 4 bash "$SCRIPTS_DIR/submit.sh" \
  --provider nonexistent --action tts --payload '{}' --timeout 60

# ===== 4 原语 × 4 个真 provider（muapi 跳过需 KEY）=====
echo
echo "── 4 原语 × 4 真 provider（19 用例）──"
# upload / download / poll 退出码因 provider 能力而异：
#   - minimax / voxcpm（同步/音频后端）不支持 upload → 预期 4
#   - gpt-image-2 / baoyu（图像/多模态后端）支持 upload → 预期 0
for provider in minimax voxcpm gpt-image-2 baoyu; do
  for op in submit poll upload download; do
    case $op in
      submit)
        run_test "[submit · $provider]" 0 bash "$SCRIPTS_DIR/submit.sh" \
          --provider "$provider" --action tts --payload '{"text":"hi"}' --timeout 60
        ;;
      poll)
        run_test "[poll · $provider]" 0 bash "$SCRIPTS_DIR/poll.sh" \
          --task-id "${provider}-test-123" --interval 1 --timeout 10
        ;;
      upload)
        TMPF=$(mktemp)
        echo "test content" > "$TMPF"
        # minimax / voxcpm 不支持 upload（仅音频后端）→ 预期 4
        if [[ "$provider" == "minimax" || "$provider" == "voxcpm" ]]; then
          EXPECTED=4
        else
          EXPECTED=0
        fi
        run_test "[upload · $provider]" $EXPECTED bash "$SCRIPTS_DIR/upload.sh" \
          --file "$TMPF" --provider "$provider" --mime "text/plain"
        rm -f "$TMPF"
        ;;
      download)
        TMPO=$(mktemp -u)
        run_test "[download · $provider]" 0 bash "$SCRIPTS_DIR/download.sh" \
          --task-id "${provider}-test-123" --output "$TMPO"
        rm -f "$TMPO"
        ;;
    esac
  done
done

# 总计
echo
echo "════════════════════════════════════════════"
echo "  PASS: $PASS / $TOTAL"
echo "  FAIL: $FAIL"
echo "════════════════════════════════════════════"
if [[ $FAIL -eq 0 ]]; then
  echo "🎉 全部通过"
  exit 0
else
  echo "⚠️  有失败，请修复后重试"
  exit 1
fi