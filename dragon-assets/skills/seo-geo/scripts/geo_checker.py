#!/usr/bin/env python3
"""
GEO Checker - AI搜索引擎优化检测工具
检测内容在AI搜索结果中的表现，生成优化建议

Usage:
    python geo_checker.py <url> [--output OUTPUT] [--format FORMAT]
    python geo_checker.py <url> --check-citations
    python geo_checker.py <url> --check-brand-mentions
    python geo_checker.py <url> --check-citable-blocks

Examples:
    python geo_checker.py https://example.com
    python geo_checker.py https://example.com --check-citations --format json
    python geo_checker.py https://example.com --output GEO-REPORT.md
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.error
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
from html.parser import HTMLParser


VERSION = "2.0.0"


@dataclass
class GEOCheckResult:
    url: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    geo_readiness_score: int = 0
    platform_scores: dict = field(default_factory=dict)
    ai_crawler_access: dict = field(default_factory=dict)
    llms_txt_status: str = ""
    brand_mentions: dict = field(default_factory=dict)
    citable_blocks: list = field(default_factory=list)
    ssr_check: dict = field(default_factory=dict)
    recommendations: list = field(default_factory=list)
    errors: list = field(default_factory=list)


class HTMLContentExtractor(HTMLParser):
    """提取HTML中的文本内容和结构"""

    def __init__(self):
        super().__init__()
        self.text_content = []
        self.structured_data = []
        self.headings = []
        self.current_heading_level = 0
        self.current_heading_text = ""
        self.in_script = False
        self.in_style = False
        self.in_noscript = False
        self.char_count = 0
        self.in_heading = False
        self.lists = []
        self.current_list = []
        self.in_list_item = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        if tag in ('script', 'style'):
            if tag == 'script':
                self.in_script = True
            else:
                self.in_style = True

        elif tag == 'noscript':
            self.in_noscript = True

        elif tag.startswith('h') and len(tag) == 2 and tag[1].isdigit():
            self.current_heading_level = int(tag[1])
            self.in_heading = True
            self.current_heading_text = ""

        elif tag == 'li':
            self.in_list_item = True
            if not self.current_list:
                self.lists.append({'type': 'ul', 'items': []})

        elif tag == 'p':
            self.char_count = 0

        elif tag == 'script' and attrs_dict.get('type') == 'application/ld+json':
            self.structured_data.append('json-ld')

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_script = False
        elif tag == 'style':
            self.in_style = False
        elif tag == 'noscript':
            self.in_noscript = False

        elif tag.startswith('h') and len(tag) == 2 and tag[1].isdigit():
            if self.current_heading_text.strip():
                self.headings.append({
                    'level': self.current_heading_level,
                    'text': self.current_heading_text.strip()
                })
            self.in_heading = False
            self.current_heading_text = ""

        elif tag == 'li':
            if self.current_list:
                self.lists[-1]['items'].append(self.current_list[-1] if self.current_list else "")
            self.in_list_item = False

        elif tag == 'p':
            pass

    def handle_data(self, data):
        if self.in_script or self.in_style or self.in_noscript:
            return

        stripped = data.strip()
        if not stripped:
            return

        if self.in_heading:
            self.current_heading_text += data
        else:
            self.text_content.append(data)
            self.char_count += len(stripped)


def fetch_url(url: str, user_agent: str = None) -> tuple[Optional[str], Optional[str]]:
    """获取URL内容"""
    if not user_agent:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode('utf-8', errors='ignore')
            return content, None
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return None, f"URL Error: {e.reason}"
    except Exception as e:
        return None, f"Error: {str(e)}"


def check_robots_txt(base_url: str) -> dict:
    """检查robots.txt中的AI爬虫配置"""
    from urllib.parse import urljoin

    robots_url = urljoin(base_url, '/robots.txt')
    content, error = fetch_url(robots_url)

    result = {
        'url': robots_url,
        'exists': content is not None,
        'crawlers': {}
    }

    if error:
        result['error'] = error
        return result

    ai_crawlers = {
        'GPTBot': 'OpenAI - ChatGPT',
        'OAI-SearchBot': 'OpenAI - OpenAI Search',
        'ChatGPT-User': 'OpenAI - ChatGPT User',
        'ClaudeBot': 'Anthropic - Claude',
        'PerplexityBot': 'Perplexity AI',
        'CCBot': 'Common Crawl - Training',
        'Bytespider': 'ByteDance - TikTok',
        'cohere-ai': 'Cohere',
        'anthropic-ai': 'Anthropic - Training',
    }

    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('User-agent:'):
            crawler = line.split(':', 1)[1].strip()
        elif line.startswith('Allow:') or line.startswith('Disallow:'):
            if crawler in ai_crawlers:
                if crawler not in result['crawlers']:
                    result['crawlers'][crawler] = {'allowed': [], 'disallowed': []}
                directive = 'allowed' if line.startswith('Allow:') else 'disallowed'
                path = line.split(':', 1)[1].strip()
                result['crawlers'][crawler][directive].append(path)

    return result


def check_llms_txt(base_url: str) -> dict:
    """检查llms.txt文件"""
    from urllib.parse import urljoin

    llms_url = urljoin(base_url, '/llms.txt')
    content, error = fetch_url(llms_url)

    return {
        'url': llms_url,
        'exists': content is not None,
        'content_preview': content[:500] if content else None,
        'error': error
    }


def analyze_content_structure(html: str) -> dict:
    """分析内容结构"""
    parser = HTMLContentExtractor()
    try:
        parser.feed(html)
    except Exception:
        pass

    full_text = ' '.join(parser.text_content)

    # 分割段落
    paragraphs = [p.strip() for p in full_text.split('\n\n') if p.strip()]

    # 分析段落长度分布
    paragraph_lengths = [len(p) for p in paragraphs]

    # 识别可引用块（134-167词）
    citable_blocks = []
    for i, para in enumerate(paragraphs):
        word_count = len(para.split())
        if 134 <= word_count <= 167:
            citable_blocks.append({
                'index': i,
                'word_count': word_count,
                'preview': para[:200] + '...' if len(para) > 200 else para
            })

    # 检查问题式标题
    question_headings = [h for h in parser.headings if h['text'].endswith('?')]

    # 检查FAQ部分
    has_faq = any('faq' in h['text'].lower() for h in parser.headings)

    return {
        'word_count': len(full_text.split()),
        'paragraph_count': len(paragraphs),
        'heading_count': len(parser.headings),
        'question_headings': len(question_headings),
        'has_faq': has_faq,
        'list_count': len(parser.lists),
        'citable_blocks': citable_blocks,
        'structured_data_types': parser.structured_data,
        'heading_hierarchy': parser.headings[:10]  # 前10个标题
    }


def calculate_geo_score(structure: dict, robots: dict, llms: dict) -> tuple[int, dict]:
    """计算GEO准备度评分"""
    scores = {
        'citability': 0,
        'structure': 0,
        'authority': 0,
        'multimodal': 0,
        'technical': 0
    }

    # 可引用性评分 (25%)
    citable_blocks_count = len(structure.get('citable_blocks', []))
    if citable_blocks_count >= 5:
        scores['citability'] = 25
    elif citable_blocks_count >= 3:
        scores['citability'] = 20
    elif citable_blocks_count >= 1:
        scores['citability'] = 15
    elif structure.get('question_headings', 0) > 0:
        scores['citability'] = 10
    else:
        scores['citability'] = 5

    # 结构可读性 (20%)
    structure_score = 0
    if structure.get('has_faq'):
        structure_score += 5
    if structure.get('question_headings', 0) >= 2:
        structure_score += 5
    if structure.get('list_count', 0) >= 2:
        structure_score += 5
    if structure.get('heading_count', 0) >= 5:
        structure_score += 5
    scores['structure'] = min(structure_score, 20)

    # 权威信号 (20%) - 基于结构推断
    authority_score = 10  # 基础分
    if structure.get('heading_count', 0) > 0:
        authority_score += 5
    if 'json-ld' in structure.get('structured_data_types', []):
        authority_score += 5
    scores['authority'] = min(authority_score, 20)

    # 多模态 (15%)
    multimodal_score = 5  # 基础分
    if 'json-ld' in structure.get('structured_data_types', []):
        multimodal_score += 5
    if structure.get('has_faq'):
        multimodal_score += 5
    scores['multimodal'] = min(multimodal_score, 15)

    # 技术可访问性 (20%)
    technical_score = 0

    # 检查AI爬虫访问
    allowed_crawlers = [c for c, v in robots.get('crawlers', {}).items()
                         if v.get('allowed') and not v.get('disallowed')]
    if len(allowed_crawlers) >= 4:
        technical_score += 10
    elif len(allowed_crawlers) >= 2:
        technical_score += 7
    elif len(allowed_crawlers) >= 1:
        technical_score += 5

    # llms.txt存在
    if llms.get('exists'):
        technical_score += 10

    scores['technical'] = min(technical_score, 20)

    total = sum(scores.values())
    return total, scores


def generate_recommendations(structure: dict, robots: dict, llms: dict,
                           platform_scores: dict) -> list:
    """生成优化建议"""
    recommendations = []

    # 可引用性建议
    citable_count = len(structure.get('citable_blocks', []))
    if citable_count < 3:
        recommendations.append({
            'priority': 'HIGH',
            'category': 'Citability',
            'issue': f'仅有{citable_count}个理想可引用块（建议5+）',
            'action': '创建134-167词的独立回答块，包含具体数据和来源归因'
        })

    # 结构建议
    if structure.get('question_headings', 0) < 2:
        recommendations.append({
            'priority': 'MEDIUM',
            'category': 'Structure',
            'issue': '问题式标题不足',
            'action': '添加基于问题的H2/H3标题（如"What is X?"）以匹配AI查询模式'
        })

    if not structure.get('has_faq'):
        recommendations.append({
            'priority': 'MEDIUM',
            'category': 'Structure',
            'issue': '缺少FAQ部分',
            'action': '添加FAQ部分，以清晰的Q&A格式呈现常见问题'
        })

    # 技术建议
    allowed = [c for c, v in robots.get('crawlers', {}).items()
               if v.get('allowed') and not v.get('disallowed')]
    missing_crawlers = [c for c in ['GPTBot', 'ClaudeBot', 'PerplexityBot']
                        if c not in allowed]

    if missing_crawlers:
        recommendations.append({
            'priority': 'HIGH',
            'category': 'Technical',
            'issue': f'缺少AI爬虫访问: {", ".join(missing_crawlers)}',
            'action': '在robots.txt中添加: User-agent: {crawler}\\nAllow: /'
        })

    if not llms.get('exists'):
        recommendations.append({
            'priority': 'MEDIUM',
            'category': 'Technical',
            'issue': '缺少llms.txt文件',
            'action': '创建/llms.txt文件，为AI爬虫提供结构化内容指导'
        })

    return recommendations[:10]  # 最多10条建议


def check_brand_mentions_html(html: str) -> dict:
    """从HTML内容中推断品牌提及信号"""
    text = ' '.join(HTMLContentExtractor().feed(html) or [''])

    # 这些是检测信号，不是完整的品牌分析
    signals = {
        'has_author_byline': bool(re.search(r'by\s+[\w\s]+', text, re.I)),
        'has_publication_date': bool(re.search(r'\d{4}-\d{2}-\d{2}|\d{1,2}\s+\w+\s+\d{4}', text)),
        'has_citations': bool(re.search(r'\[\d+\]|\(\d+\)', text)),  # [1] or (1)
        'has_statistics': bool(re.search(r'\d+%|\d+\s*(million|billion|thousand)', text, re.I)),
        'has_definitions': bool(re.search(r'is\s+(?:defined as|refers to|means)', text, re.I)),
    }

    return signals


def run_geo_check(url: str, check_citations: bool = False,
                   check_brand: bool = False) -> GEOCheckResult:
    """运行完整的GEO检查"""
    from urllib.parse import urlparse

    result = GEOCheckResult(url=url)

    # 解析base URL
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    # 1. 检查robots.txt
    result.ai_crawler_access = check_robots_txt(base_url)

    # 2. 检查llms.txt
    result.llms_txt_status = "present" if check_llms_txt(base_url).get('exists') else "missing"

    # 3. 获取并分析内容
    content, error = fetch_url(url)
    if error:
        result.errors.append(f"Content fetch failed: {error}")
        return result

    structure = analyze_content_structure(content)
    result.ssR_check = {
        'has_client_only_content': '<div id="app">' in content or 'ReactDOM' in content,
        'has_ssr_indicators': bool(re.search(r'ssr|server-side|__NEXT_DATA__', content, re.I))
    }

    # 4. 计算评分
    result.geo_readiness_score, result.platform_scores = calculate_geo_score(
        structure, result.ai_crawler_access,
        {'exists': result.llms_txt_status == 'present'}
    )

    # 5. 可引用块分析
    result.citable_blocks = structure.get('citable_blocks', [])

    # 6. 品牌提及检测
    if check_brand:
        result.brand_mentions = check_brand_mentions_html(content)

    # 7. 生成建议
    result.recommendations = generate_recommendations(
        structure, result.ai_crawler_access,
        {'exists': result.llms_txt_status == 'present'},
        result.platform_scores
    )

    return result


def format_report(result: GEOCheckResult, format: str = 'markdown') -> str:
    """格式化输出报告"""
    if format == 'json':
        return json.dumps(asdict(result), indent=2, ensure_ascii=False)

    # Markdown格式
    lines = [
        f"# GEO分析报告: {result.url}",
        f"",
        f"**生成时间**: {result.timestamp}",
        f"",
        f"## GEO准备度评分",
        f"",
        f"| 维度 | 评分 |",
        f"|------|------|",
        f"| **总分** | **{result.geo_readiness_score}/100** |",
        f"| 可引用性 (Citability) | {result.platform_scores.get('citability', 0)}/25 |",
        f"| 结构可读性 (Structure) | {result.platform_scores.get('structure', 0)}/20 |",
        f"| 权威信号 (Authority) | {result.platform_scores.get('authority', 0)}/20 |",
        f"| 多模态内容 (Multimodal) | {result.platform_scores.get('multimodal', 0)}/15 |",
        f"| 技术可访问性 (Technical) | {result.platform_scores.get('technical', 0)}/20 |",
        f"",
    ]

    # AI爬虫访问
    lines.extend([
        "## AI爬虫访问状态",
        "",
    ])

    if result.ai_crawler_access.get('crawlers'):
        for crawler, status in result.ai_crawler_access['crawlers'].items():
            allowed = '✅ Allowed' if status.get('allowed') and not status.get('disallowed') else '❌ Blocked'
            lines.append(f"- **{crawler}**: {allowed}")
    else:
        lines.append("- 无法获取爬虫配置")

    lines.extend([
        "",
        "## llms.txt状态",
        "",
        f"- **{result.llms_txt_status.upper()}**",
        "",
    ])

    # 可引用块
    if result.citable_blocks:
        lines.extend([
            "## 可引用段落 (134-167词)",
            "",
        ])
        for i, block in enumerate(result.citable_blocks[:5], 1):
            lines.append(f"**{i}.** ({block['word_count']}词)")
            lines.append(f"```")
            lines.append(block['preview'][:200] + "..." if len(block['preview']) > 200 else block['preview'])
            lines.append(f"```")
            lines.append("")
    else:
        lines.extend([
            "## 可引用段落",
            "",
            "- ❌ 未发现理想长度的可引用块（134-167词）",
            "",
        ])

    # 建议
    if result.recommendations:
        lines.extend([
            "## Top优化建议",
            "",
        ])
        for i, rec in enumerate(result.recommendations, 1):
            priority_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(rec['priority'], '⚪')
            lines.append(f"{priority_emoji} **{rec['priority']}** - {rec['category']}")
            lines.append(f"- 问题: {rec['issue']}")
            lines.append(f"- 操作: {rec['action']}")
            lines.append("")

    # 错误
    if result.errors:
        lines.extend([
            "## 错误",
            "",
        ])
        for error in result.errors:
            lines.append(f"- ❌ {error}")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='GEO Checker - AI搜索引擎优化检测工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('url', help='要检查的URL')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--format', '-f', choices=['markdown', 'json'],
                        default='markdown', help='输出格式')
    parser.add_argument('--check-citations', action='store_true',
                        help='检查AI引用情况')
    parser.add_argument('--check-brand-mentions', action='store_true',
                        help='检查品牌提及')
    parser.add_argument('--version', '-v', action='version',
                        version=f'GEO Checker v{VERSION}')

    args = parser.parse_args()

    # 运行检查
    result = run_geo_check(
        args.url,
        check_citations=args.check_citations,
        check_brand=args.check_brand_mentions
    )

    # 格式化输出
    report = format_report(result, args.format)

    # 输出
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"报告已保存到: {args.output}")
    else:
        print(report)

    # 返回退出码
    if result.errors and 'Content fetch failed' in result.errors[0]:
        sys.exit(1)

    return 0


if __name__ == '__main__':
    sys.exit(main() or 0)
