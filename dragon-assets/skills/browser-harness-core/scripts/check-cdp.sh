#!/usr/bin/env bash
# check-cdp.sh - CDP (Chrome DevTools Protocol) availability check
# Usage: bash scripts/check-cdp.sh

set -e

CDP_HOST="${CDP_HOST:-localhost}"
CDP_PORT="${CDP_PORT:-9222}"

echo "🔍 检查 Chrome CDP 可用性..."
echo "   目标: $CDP_HOST:$CDP_PORT"

# Check if CDP port is accessible
if command -v curl &> /dev/null; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://$CDP_HOST:$CDP_PORT/json" 2>/dev/null || echo "000")

    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ CDP 端口可访问 (HTTP 200)"

        # Get targets info
        echo ""
        echo "📋 可用 Targets:"
        TARGETS=$(curl -s "http://$CDP_HOST:$CDP_PORT/json" 2>/dev/null)

        if command -v jq &> /dev/null; then
            echo "$TARGETS" | jq -r '.[] | "   • \(.title // "无标题") [\(.type)] - \(.id)"' 2>/dev/null || echo "$TARGETS"
        else
            echo "$TARGETS"
        fi

        echo ""
        echo "✅ CDP 连接正常，可以执行浏览器自动化任务"
        exit 0
    elif [ "$HTTP_CODE" = "000" ]; then
        echo "❌ 无法连接到 CDP 端口"
        echo "   可能原因:"
        echo "   • Chrome 未在调试模式运行"
        echo "   • 防火墙阻止了连接"
        echo "   • CDP_HOST/CDP_PORT 配置错误"
        exit 1
    else
        echo "⚠️  CDP 端口返回 HTTP $HTTP_CODE"
        echo "   这可能表示连接问题"
        exit 1
    fi
else
    echo "❌ curl 未安装，无法检查 CDP"
    exit 1
fi
