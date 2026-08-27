#!/usr/bin/env bash
# investigate.sh - AnySearch免配置调研链路
# 适用：天龙引擎01调研师 + 62-02行业研究员 + 32-01市场研究
# 用法：bash investigate.sh "研究主题" [--depth quick|normal|deep] [--domains business,finance,academic]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI="node \"$SCRIPT_DIR/anysearch_cli.js\""

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC}   $1"; }
warn()   { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error()  { echo -e "${RED}[ERROR]${NC} $1"; }
grill()  { echo -e "${CYAN}[GRILL]${NC} $1"; }

# 默认参数
TOPIC="${1:-}"
DEPTH="${2:-normal}"
DOMAINS="${DOMAINS:-business,finance,academic}"
OUTPUT_DIR="${OUTPUT_DIR:-$SCRIPT_DIR/../output/investigate/$(date +%Y%m%d_%H%M%S)}"

usage() {
    cat << EOF
用法: bash investigate.sh "研究主题" [depth] [--domains business,finance,academic]

参数:
  研究主题   必填，调研的核心主题
  depth     可选，调研深度
              quick  - 快速摸底（3个查询）
              normal - 标准调研（6个查询，默认）
              deep   - 深度调研（10个查询）
  --domains 可选，逗号分隔的领域，默认: business,finance,academic

示例:
  bash investigate.sh "AI Agent市场趋势"
  bash investigate.sh "新能源车市场" deep
  bash investigate.sh "半导体行业" --domains academic,finance

天龙引擎适用岗位:
  01调研师 / 62-02行业研究员 / 32-01市场研究 / 60-01投资总监
EOF
    exit 1
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case "$1" in
        --domains) shift; DOMAINS="$1" ;;
        --domains=*) DOMAINS="${1#*=}" ;;
        --depth) shift; DEPTH="$1" ;;
        --depth=*) DEPTH="${1#*=}" ;;
        --help|-h) usage ;;
        -*) warn "未知参数: $1" ;;
        *) [[ -z "$TOPIC" ]] && TOPIC="$1" ;;
    esac
    shift
done

[[ -z "$TOPIC" ]] && { error "研究主题不能为空"; usage; }

# 深度配置
case "$DEPTH" in
    quick)   MAX_RESULTS=5; QUERY_COUNT=3 ;;
    normal)  MAX_RESULTS=8; QUERY_COUNT=6 ;;
    deep)    MAX_RESULTS=10; QUERY_COUNT=10 ;;
    *)       MAX_RESULTS=8; QUERY_COUNT=6 ;;
esac

# 构建输出目录
mkdir -p "$OUTPUT_DIR"

info "天龙引擎 AnySearch 免配置调研链路"
info "主题: $TOPIC"
info "深度: $DEPTH (每域$MAX_RESULTS条结果)"
info "领域: $DOMAINS"
info "输出: $OUTPUT_DIR"
echo

# ═══════════════════════════════════════════════════════════════════════════
# 第一步：Grill Me 追问分析
# ═══════════════════════════════════════════════════════════════════════════
grill "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grill "  第一步：Grill Me 追问分析"
grill "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# 自动识别主题类型并生成追问
auto_grill() {
    local topic="$1"
    local grill_output="$OUTPUT_DIR/grill_analysis.md"

    # 关键词识别主题类型
    local l1_q=""
    local l2_q=""
    local l3_q=""

    # 检测金融相关
    if echo "$topic" | grep -qiE "融资|投资|估值|并购|IPO|PE|VC|基金|股票|债券"; then
        l1_q="这个${topic}领域的核心玩家是谁？"
        l2_q="最近12个月的融资/投资动态如何？"
        l3_q="估值倍率和市场机会在哪里？"
    # 检测商业市场相关
    elif echo "$topic" | grep -qiE "市场|竞争|商业|模式|渠道|用户|增长|营销|品牌"; then
        l1_q="${topic}的市场规模和增长率是多少？"
        l2_q="主要竞争对手有哪些？"
        l3_q="成功的商业模式和变现路径是什么？"
    # 检测学术技术相关
    elif echo "$topic" | grep -qiE "技术|算法|论文|研究|学术|科学|模型|框架"; then
        l1_q="${topic}的核心技术原理是什么？"
        l2_q="最新研究进展和论文有哪些？"
        l3_q="技术落地的挑战和解决方案？"
    # 检测政策法规相关
    elif echo "$topic" | grep -qiE "政策|法规|监管|合规|标准|政府|补贴"; then
        l1_q="${topic}领域的政策法规现状是什么？"
        l2_q="监管趋势和合规要求有哪些？"
        l3_q="政策变化对市场的影响？"
    # 默认通用问题
    else
        l1_q="${topic}的核心定义和范围是什么？"
        l2_q="${topic}的关键驱动因素和阻碍是什么？"
        l3_q="${topic}的未来发展趋势和机会？"
    fi

    cat > "$grill_output" << EOF
# Grill Me 追问分析：${topic}

## L1 表面问题
- Q: ${l1_q}

## L2 动机追问
- Q: ${l2_q}

## L3 边界追问
- 这个${topic}的边界是什么？
- 什么不算${topic}的核心？

## L4 影响追问
- ${topic}会影响哪些行业/领域？
- 主要利益相关方是谁？

## L5 反面追问
- 如果不做${topic}会怎样？
- 替代方案和风险？

EOF
    echo "$grill_output"
}

grill "识别主题类型并生成追问..."
GRILL_FILE=$(auto_grill "$TOPIC")
success "追问分析完成: $GRILL_FILE"
echo

# 显示追问
cat "$GRILL_FILE"
echo

# ═══════════════════════════════════════════════════════════════════════════
# 第二步：AnySearch 批量调研
# ═══════════════════════════════════════════════════════════════════════════
grill "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grill "  第二步：AnySearch 批量调研"
grill "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# 构建查询模板（基于深度）
build_queries() {
    local topic="$1"
    local count="$2"

    # 根据主题自动选择领域
    local domains=()
    if echo "$topic" | grep -qiE "融资|投资|估值|并购|IPO|基金|股票"; then
        domains+=(finance)
    fi
    if echo "$topic" | grep -qiE "市场|竞争|商业|模式|渠道|用户|增长"; then
        domains+=(business)
    fi
    if echo "$topic" | grep -qiE "技术|算法|论文|研究|学术|科学"; then
        domains+=(academic)
    fi
    if echo "$topic" | grep -qiE "代码|开发|框架|开源|API"; then
        domains+=(code)
    fi
    if echo "$topic" | grep -qiE "健康|医疗|医药|生物"; then
        domains+=(health)
    fi
    if echo "$topic" | grep -qiE "法律|法规|合规|合同"; then
        domains+=(legal)
    fi
    # 默认加business
    if [[ ${#domains[@]} -eq 0 ]]; then
        domains+=(business)
    fi

    # 构建JSON查询数组
    local queries="["
    local first=true

    for domain in "${domains[@]}"; do
        case "$domain" in
            finance)
                if $first; then first=false; else queries+=","; fi
                queries+="{\"query\":\"${topic} 融资 投资 估值 动态\",\"domain\":\"finance\",\"max_results\":$count}"
                ;;
            business)
                if $first; then first=false; else queries+=","; fi
                queries+="{\"query\":\"${topic} 市场规模 竞争格局 商业模式\",\"domain\":\"business\",\"max_results\":$count}"
                ;;
            academic)
                if $first; then first=false; else queries+=","; fi
                queries+="{\"query\":\"${topic} 论文 研究 技术趋势\",\"domain\":\"academic\",\"max_results\":$count}"
                ;;
            code)
                if $first; then first=false; else queries+=","; fi
                queries+="{\"query\":\"${topic} 技术栈 框架 开源\",\"domain\":\"code\",\"max_results\":$count}"
                ;;
            health)
                if $first; then first=false; else queries+=","; fi
                queries+="{\"query\":\"${topic} 健康 医疗 医药\",\"domain\":\"health\",\"max_results\":$count}"
                ;;
            legal)
                if $first; then first=false; else queries+=","; fi
                queries+="{\"query\":\"${topic} 法规 合规 政策\",\"domain\":\"legal\",\"max_results\":$count}"
                ;;
        esac
    done
    queries+="]"
    echo "$queries"
}

grill "自动识别领域并构建查询..."
QUERIES=$(build_queries "$TOPIC" "$MAX_RESULTS")
success "查询构建完成 (${QUERIES:0:100}...)"
echo

# 执行批量搜索
info "开始批量搜索..."
SEARCH_START=$(date +%s)
echo "$QUERIES" | eval "$CLI batch_search --queries @- 2>/dev/null" > "$OUTPUT_DIR/raw_results.json" || {
    error "批量搜索失败"
    exit 1
}
SEARCH_END=$(date +%s)
SEARCH_DURATION=$((SEARCH_END - SEARCH_START))
success "搜索完成 (${SEARCH_DURATION}秒)"
echo

# ═══════════════════════════════════════════════════════════════════════════
# 第三步：结果解析与报告生成
# ═══════════════════════════════════════════════════════════════════════════
grill "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grill "  第三步：结果解析与报告生成"
grill "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

REPORT_FILE="$OUTPUT_DIR/调研报告-${TOPIC// /_}.md"

# 解析结果并生成报告
python3 -c "
import json, sys, re
from datetime import datetime

topic = '''$TOPIC'''
depth = '$DEPTH'
domains = '$DOMAINS'.split(',')

try:
    with open('$OUTPUT_DIR/raw_results.json', 'r', encoding='utf-8') as f:
        raw = f.read()

    # 尝试解析JSON
    try:
        results = json.loads(raw)
    except:
        # 可能是文本响应，尝试提取
        results = {'raw': raw[:5000]}

    # 统计结果数量
    total_results = 0
    domain_stats = {}
    if isinstance(results, list):
        for item in results:
            if isinstance(item, dict):
                domain = item.get('domain', 'unknown')
                content = item.get('result', item.get('content', []))
                if isinstance(content, list):
                    cnt = len(content)
                else:
                    cnt = 1
                domain_stats[domain] = cnt
                total_results += cnt
    elif isinstance(results, dict) and 'content' in results:
        content = results.get('content', [])
        if isinstance(content, list):
            total_results = len(content)

    # 生成报告
    report = f'''# 调研报告：{topic}

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 调研深度: {depth}
> 数据来源: AnySearch 批量调研

---

## 调研概要

**研究主题**: {topic}
**调研深度**: {depth}
**调研领域**: {', '.join(d.strip() for d in domains)}
**总结果数**: {total_results}

### 分领域统计

'''

    for domain, cnt in domain_stats.items():
        report += f'| {domain:12} | {cnt} 条结果 |\n'

    report += '''
---

## Grill Me 追问分析

> 见 `grill_analysis.md` 获取完整追问框架

### 核心问题
- L1: 主题定义和边界是什么？
- L2: 关键驱动因素和动机？
- L3: 边界情况和边缘案例？
- L4: 影响范围和利益相关方？
- L5: 替代方案和风险？

---

## 调研结果摘要

'''

    # 尝试提取文本内容
    if isinstance(results, list):
        for item in results:
            if isinstance(item, dict):
                domain = item.get('domain', 'unknown')
                content = item.get('result', item.get('content', ''))
                if isinstance(content, str):
                    # 截取前500字符
                    preview = content[:500].replace('\n', ' ')
                    if len(content) > 500:
                        preview += '...'
                    report += f'### {domain.upper()} 领域\n\n>{preview}\n\n'
                elif isinstance(content, list) and len(content) > 0:
                    report += f'### {domain.upper()} 领域\n\n'
                    for c in content[:3]:
                        if isinstance(c, dict):
                            text = c.get('text', str(c))[:300]
                            report += f'- {text}...\n\n'
                        elif isinstance(c, str):
                            report += f'- {c[:300]}...\n\n'
    elif isinstance(results, dict):
        text = results.get('result', results.get('content', str(results)))[:2000]
        report += f'### 主要发现\n\n{text}\n\n'

    report += '''---

## 下一步建议

- [ ] 使用 Deep Research 进行深度调研
- [ ] 采集竞品具体数据进行对比分析
- [ ] 交叉验证关键数据和结论
- [ ] 归档到天龙引擎知识库

---

> 🤖 本报告由天龙引擎 AnySearch 免配置调研链路自动生成
'''

    with open('$REPORT_FILE', 'w', encoding='utf-8') as f:
        f.write(report)

    print('REPORT_GENERATED')
    print(f'TOTAL:{total_results}')
    for d, c in domain_stats.items():
        print(f'{d}:{c}')

except Exception as e:
    print(f'PARSE_ERROR:{e}', file=sys.stderr)
    # 生成基础报告
    report = f'''# 调研报告：{topic}

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 调研深度: {depth}
> 数据来源: AnySearch 批量调研

---

## 调研概要

**研究主题**: {topic}
**调研深度**: {depth}
**调研领域**: {', '.join(d.strip() for d in domains)}

> ⚠️ 结果解析遇到问题，请查看 raw_results.json 获取完整数据

'''
    with open('$REPORT_FILE', 'w', encoding='utf-8') as f:
        f.write(report)
    print('REPORT_GENERATED')
    print('TOTAL:0')
" 2>/dev/null || {
    warn "Python解析失败，使用基础报告模板"
    cat > "$REPORT_FILE" << EOF
# 调研报告：${TOPIC}

> 生成时间: $(date '+%Y-%m-%d %H:%M:%S')
> 调研深度: ${DEPTH}
> 数据来源: AnySearch 批量调研

---

## 调研概要

**研究主题**: ${TOPIC}
**调研深度**: ${DEPTH}
**调研领域**: ${DOMAINS}

> 原始数据已保存至 raw_results.json

## Grill Me 追问分析

见 grill_analysis.md 获取完整追问框架

## 调研结果

> 请查看 raw_results.json 获取 AnySearch 返回的原始数据

EOF
}

success "报告已生成: $REPORT_FILE"
echo

# ═══════════════════════════════════════════════════════════════════════════
# 第四步：输出汇总
# ═══════════════════════════════════════════════════════════════════════════
grill "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grill "  调研完成"
grill "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

info "输出文件:"
ls -la "$OUTPUT_DIR/"
echo

# 统计
if [[ -f "$REPORT_FILE" ]]; then
    LINES=$(wc -l < "$REPORT_FILE" 2>/dev/null || echo "?")
    success "报告行数: $LINES"
fi

TOTAL_TIME=$(($(date +%s) - SEARCH_START))
success "总耗时: ${TOTAL_TIME}秒"

echo
info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
success "  调研完成！主题: $TOPIC"
info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "📁 输出目录: $OUTPUT_DIR"
echo "📄 报告文件: $REPORT_FILE"
echo "📋 Grill分析: $GRILL_FILE"
echo "🔍 原始数据: $OUTPUT_DIR/raw_results.json"
echo
echo "天龙引擎适用岗位: 01调研师 / 62-02行业研究员 / 32-01市场研究"
