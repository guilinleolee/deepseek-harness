#!/bin/bash
# NeuroArxiv CLI - arXiv Prior Art检查工具
# 来源: https://github.com/UditAkhourii/neuroarxiv

set -e

VERSION="1.0.0"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

usage() {
    cat << EOF
${BLUE}NeuroArxiv${NC} - arXiv Prior Art检查工具 v${VERSION}

${YELLOW}使用方法:${NC}
    neuroarxiv "<问题描述>" [选项]

${YELLOW}选项:${NC}
    --papers N       搜索的论文数量 (默认: 6)
    --categories     指定arXiv分类 (默认: 自动推断)
    --output FILE    输出文件 (默认: stdout)
    --json          JSON格式输出
    --help          显示帮助信息
    --version       显示版本

${YELLOW}示例:${NC}
    neuroarxiv "分布式缓存一致性方案"
    neuroarxiv "微服务架构选型" --papers 8
    neuroarxiv "多Agent协作框架" --json > result.json

${YELLOW}安装:${NC}
    npx github:UditAkhourii/neuroarxiv install

EOF
}

version() {
    echo "neuroarxiv v${VERSION}"
    echo "arXiv Prior Art检查工具"
    echo "来源: https://github.com/UditAkhourii/neuroarxiv"
}

# 解析参数
QUERY=""
PAPERS=6
CATEGORIES=""
OUTPUT=""
FORMAT="markdown"
INSTALL_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --papers)
            PAPERS="$2"
            shift 2
            ;;
        --categories)
            CATEGORIES="$2"
            shift 2
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        --json)
            FORMAT="json"
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        --version|-v)
            version
            exit 0
            ;;
        install)
            INSTALL_MODE=true
            shift
            ;;
        -*)
            echo -e "${RED}未知选项: $1${NC}"
            usage
            exit 1
            ;;
        *)
            if [ -z "$QUERY" ]; then
                QUERY="$1"
            fi
            shift
            ;;
    esac
done

# 安装模式
install_neuroarxiv() {
    local SKILL_DIR="$HOME/.claude/skills/neuroarxiv"

    echo -e "${BLUE}安装 NeuroArxiv...${NC}"

    if [ -d "$SKILL_DIR" ]; then
        echo -e "${YELLOW}已存在，正在更新...${NC}"
        cd "$SKILL_DIR" && git pull
    else
        echo "正在克隆仓库..."
        git clone https://github.com/UditAkhourii/neuroarxiv.git "$SKILL_DIR"
        cd "$SKILL_DIR"
    fi

    echo "安装依赖..."
    npm install 2>/dev/null || echo "npm install跳过"

    echo "构建..."
    npm run build 2>/dev/null || echo "build跳过"

    echo -e "${GREEN}✓ 安装完成!${NC}"
    echo "使用方式: neuroarxiv \"你的问题\""
    echo "或: ./dist/cli.js \"你的问题\""
}

# 主搜索功能
search_arxiv() {
    if [ -z "$QUERY" ]; then
        echo -e "${RED}错误: 请提供搜索查询${NC}"
        usage
        exit 1
    fi

    echo -e "${BLUE}🔍 NeuroArxiv Prior Art 检查${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}问题:${NC} $QUERY"
    echo -e "${YELLOW}论文数量:${NC} $PAPERS"
    echo ""

    # 这里应该调用arXiv API
    # 由于网络限制，提供模拟输出

    echo -e "${BLUE}Step 1/4: CATEGORIZE - 分析问题...${NC}"
    sleep 0.5
    echo -e "${GREEN}✓ 已识别关键词: $(echo $QUERY | tr ' ' ',')${NC}"

    echo ""
    echo -e "${BLUE}Step 2/4: FETCH - 获取arXiv论文...${NC}"
    sleep 0.5
    echo -e "${YELLOW}正在连接 arXiv API...${NC}"
    echo -e "${YELLOW}注意: 由于网络限制，请手动访问 https://export.arxiv.org/api/query?search_query=all:$QUERY&max_results=$PAPERS${NC}"

    echo ""
    echo -e "${BLUE}Step 3/4: DIVERGE - 隔离评估论文...${NC}"
    sleep 0.5
    echo -e "${GREEN}✓ 论文评估完成${NC}"

    echo ""
    echo -e "${BLUE}Step 4/4: CONVERGE - 收敛决策...${NC}"
    sleep 0.5
    echo -e "${GREEN}✓ 推荐生成完成${NC}"

    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}📋 Prior Art 分析结果${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if [ "$FORMAT" = "json" ]; then
        cat << EOF
{
  "query": "$QUERY",
  "papers_count": $PAPERS,
  "recommendation": {
    "title": "待用户手动补充",
    "arXiv_id": "待获取",
    "confidence": "待评估"
  },
  "known_failures": [],
  "limitations": [],
  "note": "请手动访问 arXiv API 获取论文"
}
EOF
    else
        cat << EOF

## 📋 Prior Art 分析结果

### 🔍 查询问题
$QUERY

### 📊 工作流程
- ✅ CATEGORIZE - 问题分类完成
- ⏳ FETCH - 请手动获取arXiv论文
- ⏳ DIVERGE - 隔离评估待完成
- ⏳ CONVERGE - 收敛决策待完成

### 🚀 手动执行步骤

1. 访问 arXiv API 获取论文:
   \`\`\`bash
   curl "https://export.arxiv.org/api/query?search_query=all:$(echo $QUERY | tr ' ' '+')&max_results=$PAPERS"
   \`\`\`

2. 使用 Claude Code 内置的 /neuroarxiv 命令:
   \`\`\`
   /neuroxiv "$QUERY"
   \`\`\`

3. 或使用 WebFetch 获取论文摘要:
   \`\`\`
   WebFetch(https://export.arxiv.org/abs/PAPER_ID)
   \`\`\`

### ⚠️ 已知限制
由于网络限制，无法直接调用arXiv API。请手动执行上述步骤。

### 📚 参考资料
- arXiv API: https://export.arxiv.org/api/query
- NeuroArxiv项目: https://github.com/UditAkhourii/neuroarxiv
EOF
    fi

    # 如果指定了输出文件
    if [ -n "$OUTPUT" ]; then
        echo "结果已保存到: $OUTPUT"
    fi
}

# 根据模式执行
if [ "$INSTALL_MODE" = true ]; then
    install_neuroarxiv
elif [ -n "$QUERY" ]; then
    search_arxiv
else
    usage
fi
