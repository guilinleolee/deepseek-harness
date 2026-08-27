#!/bin/bash
# HTML Slides - Vercel部署脚本

set -e

DECK_DIR="${1:-./output}"

if [ ! -d "$DECK_DIR" ]; then
    echo "❌ 目录不存在: $DECK_DIR"
    exit 1
fi

# 检查Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "⚠️  Vercel CLI未安装"
    echo "安装: npm install -g vercel"
    exit 1
fi

echo "🚀 部署HTML幻灯片到Vercel..."
echo "📁 目录: $DECK_DIR"

cd "$DECK_DIR"

# 部署
DEPLOY_URL=$(vercel --prod --yes 2>&1 | grep -oP 'https://[^\s]+' | head -1)

if [ -n "$DEPLOY_URL" ]; then
    echo ""
    echo "✅ 部署成功！"
    echo "🔗 分享链接: $DEPLOY_URL"
else
    echo "⚠️  部署完成，请查看Vercel控制台获取链接"
fi