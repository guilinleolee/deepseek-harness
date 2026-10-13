#!/usr/bin/env bash
# market-research.sh - AnySearch市场研究批量调研工作流
# 适用：天龙引擎32-01市场研究岗位
# 用法：bash market-research.sh "研究主题" [--domains business,finance,academic]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI="node \"$SCRIPT_DIR/anysearch_cli.js\""

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC}   $1"; }
warn()   { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error()  { echo -e "${RED}[ERROR]${NC} $1"; }

# 默认参数
TOPIC="${1:-}"
DOMAINS="${2:-business,finance,academic}"
MAX_RESULTS=5
OUTPUT_DIR="${OUTPUT_DIR:-$SCRIPT_DIR/../output/market-research/$(date +%Y%m%d_%H%M%S)}"

usage() {
    cat << EOF
用法: bash market-research.sh "研究主题" [domains] [--max-results N] [--output DIR]

参数:
  研究主题     必填，研究查询的核心主题

  domains     可选，逗号分隔的领域列表
              默认: business,finance,academic
              可选: code,travel,home,ecommerce,gaming,film,
                    music,finance,academic,legal,business,ip,
                    health,geo,environment,energy

  --max-results N  可选，每领域最大结果数，默认5

  --output DIR    可选，输出目录，默认自动生成

示例:
  bash market-research.sh "AI Agent市场趋势"
  bash market-research.sh "新能源车市场" "business,finance"
  bash market-research.sh "半导体行业研究" --domains academic,finance --max-results 8

天龙引擎适用岗位:
  32-01市场研究 / 62-02行业研究员 / 60-01投资总监
EOF
    exit 1
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case "$1" in
        --domains) shift; DOMAINS="$1" ;;
        --max-results) shift; MAX_RESULTS="$1" ;;
        --output) shift; OUTPUT_DIR="$1" ;;
        --help|-h) usage ;;
        -*) warn "未知参数: $1" ;;
        *) TOPIC="$1" ;;
    esac
    shift
done

[[ -z "$TOPIC" ]] && { error "研究主题不能为空"; usage; }

# 构建输出目录
mkdir -p "$OUTPUT_DIR"

info "天龙引擎 AnySearch 市场研究批量调研"
info "主题: $TOPIC"
info "领域: $DOMAINS"
info "输出: $OUTPUT_DIR"
echo

# 领域 → 查询词模板
declare -A DOMAIN_QUERIES=(
    ["business"]="\"${TOPIC} 市场规模 竞争格局 商业模式\""
    ["finance"]="\"${TOPIC} 融资 投资 并购 估值\""
    ["academic"]="\"${TOPIC} 研究 论文 技术趋势 学术观点\""
    ["code"]="\"${TOPIC} 技术栈 开源 框架 开发工具\""
    ["health"]="\"${TOPIC} 健康 医疗 医药\""
    ["ecommerce"]="\"${TOPIC} 电商 平台 用户增长\""
    ["legal"]="\"${TOPIC} 法规 合规 政策 监管\""
    ["ip"]="\"${TOPIC} 知识产权 专利 商标\""
    ["news"]="\"${TOPIC} 新闻 动态 事件 最新\""
)

# 构建批量查询JSON
QUERIES_JSON="["
first=true
for domain in $(echo "$DOMAINS" | tr ',' ' '); do
    domain=$(echo "$domain" | tr -d '[:space:]')
    if [[ -n "${DOMAIN_QUERIES[$domain]}" ]]; then
        if $first; then first=false; else QUERIES_JSON+=","; fi
        QUERIES_JSON+="{\"query\":${DOMAIN_QUERIES[$domain]},\"domain\":\"$domain\",\"max_results\":$MAX_RESULTS}"
        info "  添加领域: $domain"
    else
        warn "  跳过未知领域: $domain"
    fi
done
QUERIES_JSON+="]"

if [[ "$QUERIES_JSON" == "[]" ]]; then
    error "没有有效的领域查询"
    exit 1
fi

echo
info "开始批量搜索..."
echo "$QUERIES_JSON" | eval "$CLI batch_search --queries @- 2>/dev/null" > "$OUTPUT_DIR/raw_results.json" || {
    error "批量搜索失败"
    exit 1
}

success "搜索完成"
echo

# 解析结果
REPORT_FILE="$OUTPUT_DIR/研究-${TOPIC// /_}.md"

cat > "$REPORT_FILE" << EOF
# 市场研究报告：${TOPIC}

> 生成时间: $(date '+%Y-%m-%d %H:%M:%S')
> 数据来源: AnySearch 批量调研
> 领域覆盖: ${DOMAINS}

---

## 调研概要

**研究主题**: ${TOPIC}
**调研领域**: ${DOMAINS}
**数据时间**: $(date '+%Y-%m-%d')

EOF

# 尝试解析各领域结果
for domain in $(echo "$DOMAINS" | tr ',' ' '); do
    domain=$(echo "$domain" | tr -d '[:space:]')
    [[ -z "$domain" ]] && continue

    DOMAIN_LABEL="${domain}"
    DOMAIN_RESULTS="$OUTPUT_DIR/${domain}_results.json"

    # 从原始结果提取该领域内容
    if command -v python3 &>/dev/null; then
        python3 -c "
import json, sys
try:
    with open('$OUTPUT_DIR/raw_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    # 尝试解析JSON数组格式
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item.get('domain', item.get('query', '').startswith('$domain'):
                with open('$DOMAIN_RESULTS', 'w', encoding='utf-8') as out:
                    json.dump(item, out, ensure_ascii=False, indent=2)
                break
    else:
        with open('$DOMAIN_RESULTS', 'w', encoding='utf-8') as out:
            json.dump(data, out, ensure_ascii=False, indent=2)
except Exception as e:
    pass
" 2>/dev/null || true
    fi

    if [[ -f "$DOMAIN_RESULTS" ]] && [[ -s "$DOMAIN_RESULTS" ]]; then
        success "  领域 [$domain]: 有结果"
    else
        warn "  领域 [$domain]: 无结构化结果"
    fi
done

cat >> "$REPORT_FILE" << 'EOF'

## 原始数据

原始批量搜索结果已保存至: `raw_results.json`

---

## 研究结论

> ⚠️ 此部分需要天龙引擎分析师基于原始数据进行深入分析

### 关键发现
（基于批量调研数据整理）

### 市场规模与趋势
（填写市场规模、增长率、关键驱动因素）

### 竞争格局
（填写主要参与者、市场份额、竞争壁垒）

### 投资与融资动态
（填写最新融资事件、投资热点、估值趋势）

### 技术与学术前沿
（填写技术趋势、学术研究成果、专利布局）

---

## 下一步建议

- [ ] 使用 Deep Research 进行深度调研
- [ ] 采集竞品具体数据进行对比分析
- [ ] 交叉验证关键数据和结论
- [ ] 归档到天龙引擎知识库

EOF

success "报告已生成: $REPORT_FILE"
echo
info "输出文件:"
ls -la "$OUTPUT_DIR/"
echo
info "批量调研完成"
