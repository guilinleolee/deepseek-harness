#!/bin/bash
# typeless-auto-submit 天龙引擎一键安装脚本
# 用途: 为 Claude Code 安装免手操作语音交互能力
# 版本: V1.0
# 日期: 2026-03-29

set -e

echo "🔧 typeless-auto-submit 天龙引擎安装脚本"
echo "========================================"

# 检查 macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ 错误: 此脚本仅支持 macOS"
    exit 1
fi

# 检查 Xcode Command Line Tools
if ! command -v swiftc &> /dev/null; then
    echo "❌ 错误: 需要安装 Xcode Command Line Tools"
    echo "   运行: xcode-select --install"
    exit 1
fi

# 创建目录
echo "📁 创建目录..."
mkdir -p ~/.claude/hooks

# 复制文件
echo "📦 复制文件..."
cp dictation-auto-submit ~/.claude/hooks/
cp voice-response.sh ~/.claude/hooks/
cp voice-toggle.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/dictation-auto-submit
chmod +x ~/.claude/hooks/voice-response.sh
chmod +x ~/.claude/hooks/voice-toggle.sh

# 检查 Claude Code 配置
echo "⚙️ 配置 Stop Hook..."
SETTINGS_FILE="$HOME/.claude/settings.json"

if [ -f "$SETTINGS_FILE" ]; then
    # 检查是否已有 Stop Hook
    if grep -q "voice-response.sh" "$SETTINGS_FILE" 2>/dev/null; then
        echo "✅ Stop Hook 已配置"
    else
        echo "⚠️ 请手动添加 Stop Hook 到 $SETTINGS_FILE:"
        echo '   "Stop": [{"hooks": [{"type": "command", "command": "bash ~/.claude/hooks/voice-response.sh", "async": true}]}]'
    fi
else
    echo "⚠️ 请手动创建 $SETTINGS_FILE 并添加 Stop Hook"
fi

echo ""
echo "✅ 安装完成!"
echo ""
echo "📋 后续步骤:"
echo "1. 系统设置 > Privacy & Security > Input Monitoring"
echo "   添加 terminal/iTerm2/Ghostty 等终端应用"
echo "2. 系统设置 > Privacy & Security > Accessibility"
echo "   添加 terminal/iTerm2/Ghostty 等终端应用"
echo "3. 启用语音模式: touch ~/.claude/voice-enabled"
echo "4. 启动服务: ~/.claude/hooks/dictation-auto-submit &"
echo ""
echo "📖 使用方法:"
echo "   按 Fn 键开始听写 → 说话 → 再按 Fn 结束"
echo "   等待 2.5 秒后自动提交到 Claude Code"
echo ""
