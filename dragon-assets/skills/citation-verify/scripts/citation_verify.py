#!/usr/bin/env python3
"""
引用验证独立脚本
可脱离天龙引擎独立运行

用法:
    python citation_verify.py references.bib
    python citation_verify.py references.bib --format json
    python citation_verify.py references.bib --auto-fix
"""

import sys
import json
import re
import time
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

try:
    import requests
except ImportError:
    print("请安装requests: pip install requests")
    sys.exit(1)


class VerifyStatus(Enum):
    """验证状态分类"""
    VERIFIED = "verified"        # 存在确认 + 标题相似度≥0.80
    SUSPICIOUS = "suspicious"    # 找到但元数据分歧 (0.50≤sim<0.80)
    HALLUCINATED = "hallucinated"  # 未找到或相似度<0.50
    SKIPPED = "skipped"          # 无法验证


@dataclass
class CitationEntry:
    """引用条目"""
    cite_key: str
    title: str
    author: str = ""
    year: str = ""
    doi: str = ""
    eprint: str = ""  # arXiv ID
    url: str = ""
    journal: str = "",
    booktitle: str = ""
    raw_text: str = ""


@dataclass
class VerifyResult:
    """验证结果"""
    cite_key: str
    title: str
    status: VerifyStatus
    confidence: float
    method: str
    matched_paper: Optional[Dict] = None
    details: str = ""


def parse_bibtex_entries(bib_text: str) -> List[CitationEntry]:
    """解析BibTeX条目"""
    entries = []

    # 匹配BibTeX条目
    pattern = r'@(\w+)\s*\{\s*([^,]+)\s*,([^@]*?)\n\}'
    matches = re.findall(pattern, bib_text, re.DOTALL)

    for entry_type, cite_key, fields_text in matches:
        entry = CitationEntry(cite_key=cite_key.strip(), title="", raw_text=f"@{entry_type}{{{cite_key},{fields_text}\n}}")

        # 解析字段
        field_patterns = {
            'title': r'title\s*=\s*[{\"]([^}\"]+)[}\"]',
            'author': r'author\s*=\s*[{\"]([^}\"]+)[}\"]',
            'year': r'year\s*=\s*[{\"]?(\d+)[}\"]?',
            'doi': r'doi\s*=\s*[{\"]([^}\"]+)[}\"]',
            'eprint': r'eprint\s*=\s*[{\"]([^}\"]+)[}\"]',
            'url': r'url\s*=\s*[{\"]([^}\"]+)[}\"]',
            'journal': r'journal\s*=\s*[{\"]([^}\"]+)[}\"]',
            'booktitle': r'booktitle\s*=\s*[{\"]([^}\"]+)[}\"]',
        }

        for field, pattern in field_patterns.items():
            match = re.search(pattern, fields_text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                setattr(entry, field, value)

        entries.append(entry)

    return entries


def title_similarity(expected: str, found: str) -> float:
    """
    计算标题相似度 (Jaccard-like word overlap)
    返回 0.0-1.0
    """
    if not expected or not found:
        return 0.0

    # 标准化
    def normalize(text):
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return set(text.split())

    words_expected = normalize(expected)
    words_found = normalize(found)

    if not words_expected or not words_found:
        return 0.0

    intersection = words_expected & words_found
    union = words_expected | words_found

    return len(intersection) / len(union) if union else 0.0


class CitationVerifier:
    """引用验证器"""

    def __init__(self, timeout: int = 20, retry: int = 3):
        self.timeout = timeout
        self.retry = retry
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CitationVerify/1.0 (Tianlong Engine)'
        })

    def verify_arxiv(self, arxiv_id: str) -> Optional[Dict]:
        """L1: arXiv ID检查"""
        try:
            url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                # 解析XML响应
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)

                entries = root.findall('{http://www.w3.org/2005/Atom}entry')
                if entries:
                    entry = entries[0]
                    title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                    if title_elem is not None:
                        return {
                            'title': title_elem.text.strip() if title_elem.text else '',
                            'source': 'arXiv',
                            'arxiv_id': arxiv_id
                        }
        except Exception as e:
            pass
        return None

    def verify_doi(self, doi: str) -> Optional[Dict]:
        """L2: DOI解析"""
        try:
            # CrossRef API
            url = f"https://api.crossref.org/works/{doi}"
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                message = data.get('message', {})
                title_list = message.get('title', [])
                if title_list:
                    return {
                        'title': title_list[0],
                        'source': 'CrossRef',
                        'doi': doi
                    }
        except Exception:
            pass

        # DataCite备用
        try:
            url = f"https://api.datacite.org/dois/{doi}"
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                attrs = data.get('data', {}).get('attributes', {})
                title = attrs.get('titles', [{}])[0].get('title', '')
                if title:
                    return {
                        'title': title,
                        'source': 'DataCite',
                        'doi': doi
                    }
        except Exception:
            pass

        return None

    def verify_title_search(self, title: str) -> Optional[Dict]:
        """L3: 标题搜索"""
        # Semantic Scholar API
        try:
            url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={title}&limit=1"
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                papers = data.get('data', [])
                if papers:
                    paper = papers[0]
                    return {
                        'title': paper.get('title', ''),
                        'source': 'Semantic Scholar',
                        'paper_id': paper.get('paperId', '')
                    }
        except Exception:
            pass

        # arXiv标题搜索
        try:
            url = f"http://export.arxiv.org/api/query?search_query=ti:{title}&max_results=1"
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                entries = root.findall('{http://www.w3.org/2005/Atom}entry')
                if entries:
                    entry = entries[0]
                    title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                    if title_elem is not None and title_elem.text:
                        return {
                            'title': title_elem.text.strip(),
                            'source': 'arXiv'
                        }
        except Exception:
            pass

        return None

    def verify_entry(self, entry: CitationEntry) -> VerifyResult:
        """验证单个引用条目"""

        # L1: arXiv ID检查
        if entry.eprint:
            result = self.verify_arxiv(entry.eprint)
            if result:
                sim = title_similarity(entry.title, result.get('title', ''))
                status = VerifyStatus.VERIFIED if sim >= 0.80 else (VerifyStatus.SUSPICIOUS if sim >= 0.50 else VerifyStatus.HALLUCINATED)
                return VerifyResult(
                    cite_key=entry.cite_key,
                    title=entry.title,
                    status=status,
                    confidence=sim,
                    method='arxiv_id',
                    matched_paper=result,
                    details=f"arXiv ID: {entry.eprint}, 相似度: {sim:.2f}"
                )

        # L2: DOI解析
        if entry.doi:
            result = self.verify_doi(entry.doi)
            if result:
                sim = title_similarity(entry.title, result.get('title', ''))
                status = VerifyStatus.VERIFIED if sim >= 0.80 else (VerifyStatus.SUSPICIOUS if sim >= 0.50 else VerifyStatus.HALLUCINATED)
                return VerifyResult(
                    cite_key=entry.cite_key,
                    title=entry.title,
                    status=status,
                    confidence=sim,
                    method='doi',
                    matched_paper=result,
                    details=f"DOI: {entry.doi}, 相似度: {sim:.2f}"
                )

        # L3: 标题搜索
        if entry.title:
            result = self.verify_title_search(entry.title)
            if result:
                sim = title_similarity(entry.title, result.get('title', ''))
                status = VerifyStatus.VERIFIED if sim >= 0.80 else (VerifyStatus.SUSPICIOUS if sim >= 0.50 else VerifyStatus.HALLUCINATED)
                return VerifyResult(
                    cite_key=entry.cite_key,
                    title=entry.title,
                    status=status,
                    confidence=sim,
                    method='title_search',
                    matched_paper=result,
                    details=f"标题搜索匹配, 相似度: {sim:.2f}"
                )

        # 无法验证
        return VerifyResult(
            cite_key=entry.cite_key,
            title=entry.title,
            status=VerifyStatus.SKIPPED,
            confidence=0.0,
            method='none',
            details="无法验证：缺少DOI/arXiv ID或标题搜索失败"
        )

    def verify_file(self, bib_file: str) -> 'VerificationReport':
        """验证BibTeX文件"""
        with open(bib_file, 'r', encoding='utf-8') as f:
            bib_text = f.read()

        entries = parse_bibtex_entries(bib_text)
        results = []

        for entry in entries:
            result = self.verify_entry(entry)
            results.append(result)
            time.sleep(0.5)  # 避免API速率限制

        return VerificationReport(results=results)


@dataclass
class VerificationReport:
    """验证报告"""
    results: List[VerifyResult]

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def verified(self) -> int:
        return sum(1 for r in self.results if r.status == VerifyStatus.VERIFIED)

    @property
    def suspicious(self) -> int:
        return sum(1 for r in self.results if r.status == VerifyStatus.SUSPICIOUS)

    @property
    def hallucinated(self) -> int:
        return sum(1 for r in self.results if r.status == VerifyStatus.HALLUCINATED)

    @property
    def skipped(self) -> int:
        return sum(1 for r in self.results if r.status == VerifyStatus.SKIPPED)

    @property
    def integrity_score(self) -> float:
        """完整性评分"""
        if self.total == 0:
            return 0.0
        return self.verified / self.total

    def to_dict(self) -> Dict:
        return {
            'summary': {
                'total': self.total,
                'verified': self.verified,
                'suspicious': self.suspicious,
                'hallucinated': self.hallucinated,
                'skipped': self.skipped,
                'integrity_score': round(self.integrity_score, 4)
            },
            'results': [
                {
                    'cite_key': r.cite_key,
                    'title': r.title,
                    'status': r.status.value,
                    'confidence': round(r.confidence, 4),
                    'method': r.method,
                    'matched_paper': r.matched_paper,
                    'details': r.details
                }
                for r in self.results
            ]
        }


def format_text_report(report: VerificationReport, verbose: bool = False) -> str:
    """生成文本报告"""
    lines = [
        "=" * 60,
        "引用验证报告",
        "=" * 60,
        f"总计: {report.total}",
        f"验证通过: {report.verified}",
        f"可疑: {report.suspicious}",
        f"幻觉: {report.hallucinated}",
        f"跳过: {report.skipped}",
        f"完整性评分: {report.integrity_score:.2%}",
        "",
    ]

    if verbose:
        lines.append("详细结果:")
        lines.append("-" * 60)
        for r in report.results:
            status_icon = {
                VerifyStatus.VERIFIED: "✅",
                VerifyStatus.SUSPICIOUS: "⚠️",
                VerifyStatus.HALLUCINATED: "❌",
                VerifyStatus.SKIPPED: "⏭️"
            }.get(r.status, "❓")

            lines.append(f"\n{status_icon} [{r.status.value.upper()}] {r.cite_key}")
            lines.append(f"  标题: {r.title}")
            lines.append(f"  方法: {r.method}")
            lines.append(f"  置信度: {r.confidence:.2f}")
            if r.details:
                lines.append(f"  详情: {r.details}")

    return "\n".join(lines)


def fix_bib_file(bib_text: str, report: VerificationReport, output_path: str):
    """移除幻觉引用"""
    hallucinated_keys = {r.cite_key for r in report.results if r.status == VerifyStatus.HALLUCINATED}

    if not hallucinated_keys:
        print("没有幻觉引用需要移除")
        return

    # 移除幻觉引用
    lines = bib_text.split('\n')
    new_lines = []
    skip_until_brace = 0
    current_entry = ""

    for line in lines:
        if line.strip().startswith('@'):
            match = re.match(r'@\w+\s*\{\s*([^,]+)\s*,', line)
            if match:
                current_entry = match.group(1).strip()
                if current_entry in hallucinated_keys:
                    skip_until_brace = 1
                    continue

        if skip_until_brace > 0:
            skip_until_brace += line.count('{') - line.count('}')
            if skip_until_brace <= 0:
                skip_until_brace = 0
            continue

        new_lines.append(line)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))

    print(f"已移除 {len(hallucinated_keys)} 个幻觉引用，保存到: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="引用验证工具")
    parser.add_argument("file", help="BibTeX文件路径")
    parser.add_argument("--format", "-f", choices=["json", "yaml", "text"], default="text", help="输出格式")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--auto-fix", action="store_true", help="自动移除幻觉引用")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--timeout", type=int, default=20, help="API超时时间(秒)")
    parser.add_argument("--retry", type=int, default=3, help="失败重试次数")

    args = parser.parse_args()

    # 验证文件存在
    bib_path = Path(args.file)
    if not bib_path.exists():
        print(f"错误: 文件不存在: {args.file}")
        sys.exit(1)

    # 初始化验证器
    verifier = CitationVerifier(timeout=args.timeout, retry=args.retry)

    print(f"正在验证: {args.file}")
    report = verifier.verify_file(args.file)

    # 输出结果
    if args.format == "json":
        output = json.dumps(report.to_dict(), indent=2, ensure_ascii=False)
    else:
        output = format_text_report(report, args.verbose)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"报告已保存到: {args.output}")
    else:
        print(output)

    # 自动修复
    if args.auto_fix and report.hallucinated > 0:
        with open(args.file, 'r', encoding='utf-8') as f:
            bib_text = f.read()
        fix_path = args.file.replace('.bib', '_fixed.bib')
        fix_bib_file(bib_text, report, fix_path)


if __name__ == "__main__":
    main()