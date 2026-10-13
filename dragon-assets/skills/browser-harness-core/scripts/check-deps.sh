#!/usr/bin/env bash
# check-deps.sh - Dependency check for browser-harness-core
# Usage: bash scripts/check-deps.sh

set -e

echo "🔍 检查 browser-harness-core 依赖..."

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js: $NODE_VERSION"

    # Check Node.js version (22+ recommended)
    NODE_MAJOR=$(echo $NODE_VERSION | sed 's/v\([0-9]*\).*/\1/')
    if [ "$NODE_MAJOR" -ge 22 ]; then
        echo "✅ Node.js 版本满足要求 (>=22)"
    else
        echo "⚠️  Node.js 版本较低 (建议 >=22，原生 WebSocket 支持更好)"
    fi
else
    echo "❌ Node.js 未安装"
    echo "   安装: https://nodejs.org/"
    exit 1
fi

# Check Chrome
if command -v google-chrome &> /dev/null; then
    CHROME_VERSION=$(google-chrome --version 2>/dev/null || echo "unknown")
    echo "✅ Chrome: $CHROME_VERSION"
elif command -v chrome &> /dev/null; then
    echo "✅ Chrome (chrome 命令可用)"
elif [ -d "/c/Program Files/Google/Chrome/Application" ]; then
    echo "✅ Chrome (Windows 安装目录存在)"
elif [ -d "/Applications/Google Chrome.app" ]; then
    echo "✅ Chrome (macOS 安装目录存在)"
else
    echo "⚠️  Chrome 未检测到 (CDP 需要 Chrome)"
    echo "   下载: https://www.google.com/chrome/"
fi

# Check Chrome remote debugging port
if command -v lsof &> /dev/null; then
    if lsof -i :9222 &> /dev/null; then
        echo "✅ Chrome CDP 端口 9222 已被占用 (Chrome 已在调试模式运行)"
    else
        echo "⚠️  Chrome CDP 端口 9222 未被占用"
        echo "   请在 Chrome 中打开 chrome://inspect/#remote-debugging"
        echo "   并勾选 'Allow remote debugging for this browser instance'"
    fi
elif command -v netstat &> /dev/null; then
    if netstat -an 2>/dev/null | grep -q ":9222"; then
        echo "✅ Chrome CDP 端口 9222 已在使用"
    else
        echo "⚠️  Chrome CDP 端口 9222 未被占用"
    fi
fi

# Check jq (for JSON parsing)
if command -v jq &> /dev/null; then
    echo "✅ jq: $(jq --version)"
else
    echo "⚠️  jq 未安装 (task.sh 输出格式需要)"
    echo "   安装: https://stedolan.github.io/jq/"
fi

# Check curl
if command -v curl &> /dev/null; then
    CURL_VERSION=$(curl --version | head -n1)
    echo "✅ curl: $CURL_VERSION"
else
    echo "❌ curl 未安装"
    exit 1
fi

echo ""
echo "✅ 依赖检查完成"
echo ""
echo "💡 快速启动:"
echo "   1. 启动 Chrome 调试模式: chrome --remote-debugging-port=9222"
echo "   2. 创建会话: bash scripts/session.sh create --name 'my-session'"
echo "   3. 执行任务: bash scripts/task.sh execute --session <id> --steps '...'"
