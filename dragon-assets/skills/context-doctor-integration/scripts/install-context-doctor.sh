#!/usr/bin/env bash
# Context Doctor 一键安装脚本（天龙阶段 26 · 2026-08-23）
#
# 适用环境：DSH >= 0.1.0-rc.6（含 0.1.1-rc 线）
# 安装位置：DSH 宿主（运行 dsh web 的机器），不是 DSH Web 客户端
# 安装目标：dsh web profile
#
# 用法：
#   bash install-context-doctor.sh          # 一键安装 + 验证
#   bash install-context-doctor.sh audit    # 安装后立即跑一次 audit
#   bash install-context-doctor.sh check    # 仅检查是否已安装

set -euo pipefail

PLUGIN_REPO="github:Zhenyu98/dsh-context-doctor#main"
PROFILE="${DSH_PROFILE:-web}"

red()    { printf "\033[31m%s\033[0m\n" "$*"; }
green()  { printf "\033[32m%s\033[0m\n" "$*"; }
yellow() { printf "\033[33m%s\033[0m\n" "$*"; }

# === 步骤 0: DSH 版本检查 ===
echo "==> 步骤 0: 检查 DSH 版本"
if ! command -v dsh >/dev/null 2>&1; then
  red "❌ 未找到 dsh 命令，请确认 DSH 已安装并在 PATH 中"
  exit 1
fi
DSH_VERSION=$(dsh --version 2>&1 | head -1 | grep -oE '0\.[0-9]+\.[0-9]+(-[a-z]+\.[0-9]+)?' || echo "unknown")
echo "    检测到 DSH 版本: ${DSH_VERSION}"
echo

# === 步骤 1: 检查是否已安装 ===
echo "==> 步骤 1: 检查 context-doctor 是否已安装"
if dsh --profile "$PROFILE" --dump-config 2>/dev/null | grep -q "context-doctor"; then
  yellow "⚠️  context-doctor 已安装，将跳过安装步骤"
else
  echo "==> 步骤 2: 安装插件（${PLUGIN_REPO}）"
  if ! dsh plugin --profile "$PROFILE" add "$PLUGIN_REPO"; then
    red "❌ 安装失败，请检查网络与 DSH 版本"
    exit 1
  fi
  green "✅ 安装成功"
fi
echo

# === 步骤 3: 验证合成树 ===
echo "==> 步骤 3: 验证合成树含 context-doctor"
if dsh --profile "$PROFILE" --dump-config | grep -q "context-doctor"; then
  green "✅ 合成树已含 context-doctor"
  dsh --profile "$PROFILE" --dump-config | grep -A 1 "context-doctor" || true
else
  red "❌ 合成树无 context-doctor，请重试步骤 2"
  exit 1
fi
echo

# === 步骤 4: 提示重启 ===
yellow "==> 步骤 4: 请手动重启 dsh web"
yellow "    Ctrl+C 终止当前 dsh web 进程 → 重新执行 'dsh web'"
echo

# === 可选: 立即跑 audit ===
if [[ "${1:-}" == "audit" ]]; then
  echo "==> 可选: 跑首次 context_audit（headless 模式）"
  echo "    请在新会话里让模型调用: context_audit detail=developer"
fi

if [[ "${1:-}" == "check" ]]; then
  echo "==> 仅检查模式完成"
  exit 0
fi

green "✅ Context Doctor 安装完成"
echo
echo "📖 下一步："
echo "  1. 重启 dsh web"
echo "  2. 进已有会话，composer 左侧应有 Context Doctor 圆环"
echo "  3. 在新会话让模型调用 context_audit 验证工具可用"
echo "  4. 把首次审计报告归档到 ~/.dsh/audit/2026-08-23-baseline.json"
echo
echo "📚 详见: dragon-engine/skills/context-doctor-integration/README.md"
