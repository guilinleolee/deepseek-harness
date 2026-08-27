#!/bin/bash
# HTML Slides - PDF导出脚本

set -e

HTML_FILE="${1:-./output/index.html}"
OUTPUT_PDF="${2:-./presentation.pdf}"

if [ ! -f "$HTML_FILE" ]; then
    echo "❌ HTML文件不存在: $HTML_FILE"
    exit 1
fi

# 检查Playwright
if ! command -v npx &> /dev/null; then
    echo "❌ 需要安装Node.js和npx"
    exit 1
fi

echo "📄 导出PDF..."
echo "📁 HTML: $HTML_FILE"
echo "📄 PDF: $OUTPUT_PDF"

# 使用Playwright导出
npx playwright pdf "$HTML_FILE" "$OUTPUT_PDF" \
    --format=A4 \
    --print-background=true \
    --margin-top=0 \
    --margin-bottom=0 \
    --margin-left=0 \
    --margin-right=0

echo ""
echo "✅ PDF导出成功！"
echo "📄 文件: $OUTPUT_PDF"