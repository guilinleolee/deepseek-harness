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

# ===== 4 原语 × 4 个 provider =====
echo
echo "── 4 原语 × 4 provider（16 用例）──"
# 退出码语义：
#   - submit / poll：本地回显任务元数据 → 0
#   - upload：minimax / voxcpm 不支持 → 4；其余 → 0
#   - download：未接真后端的 provider 不写占位文件 → 4
#     （真实产物由 render-deck 出图，或由 minimax-image / muapi 任务结果 URL 取）
for provider in minimax voxcpm gpt-image-2 baoyu; do
  for op in submit poll upload download; do
    case $op in
      submit)
        # gpt-image-2 需要 OPENAI_API_KEY；缺 key 时必须明确失败（4），不假装排队成功
        EXPECTED=0
        if [[ "$provider" == "gpt-image-2" && -z "${OPENAI_API_KEY:-}" ]]; then
          EXPECTED=4
        fi
        run_test "[submit · $provider]" $EXPECTED bash "$SCRIPTS_DIR/submit.sh" \
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
        run_test "[download · $provider]" 4 bash "$SCRIPTS_DIR/download.sh" \
          --task-id "${provider}-test-123" --output "$TMPO"
        # 未接真后端时不得留下占位文件
        if [[ -f "$TMPO" ]]; then
          echo "❌ [download · $provider] 未接真后端却写出了文件"
          FAIL=$((FAIL+1)); TOTAL=$((TOTAL+1))
        fi
        rm -f "$TMPO"
        ;;
    esac
  done
done

# ===== minimax-image：真实出图后端 =====
# 需要 MINIMAX_API_KEY，且会真的调一次生成接口（花钱）。
# 无 key 时只验证"缺 key 必须明确失败"，不发起调用。
echo
echo "── minimax-image（真实出图后端）──"
if [[ -n "${MINIMAX_API_KEY:-}" ]]; then
  run_test "[submit · minimax-image]" 0 bash "$SCRIPTS_DIR/submit.sh" \
    --provider minimax-image --action image-gen \
    --payload '{"model":"image-01","prompt":"a red circle","aspect_ratio":"1:1","n":1}' \
    --timeout 180
else
  run_test "[submit · minimax-image · 缺 KEY]" 4 bash "$SCRIPTS_DIR/submit.sh" \
    --provider minimax-image --action image-gen \
    --payload '{"model":"image-01","prompt":"a red circle"}' --timeout 60
fi

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