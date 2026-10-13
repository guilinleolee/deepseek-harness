# ~/.claude/skills/neat-freak/scripts/drift_scanner.py
import json
import re
import sys
from pathlib import Path
from typing import Dict, List

def extract_version(file_path: str) -> str:
    """从文件中提取版本号"""
    patterns = [
        r'Version\s+([\d.]+)',
        r'V([\d.]+)\s',
        r'v([\d.]+)',
        r'([\d]+\.[\d]+)\s',
    ]
    try:
        content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return None
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            return match.group(1)
    return None


def extract_terms(file_path: str, terms: List[str]) -> Dict[str, int]:
    """提取术语及其出现频率"""
    try:
        content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return {}
    result = {}
    for term in terms:
        count = len(re.findall(term, content))
        if count > 0:
            result[term] = count
    return result


def scan_files(layer1_files: List[str], layer2_files: List[str], output: str = None):
    """扫描三层文档版本差异"""
    drift = {
        'version_drift': [],
        'capability_drift': [],
        'naming_drift': [],
        'constraint_drift': []
    }

    versions = {}
    for f in layer1_files + layer2_files:
        v = extract_version(f)
        if v:
            versions[f] = v

    unique_versions = set(versions.values())
    if len(unique_versions) > 1:
        latest = sorted(unique_versions)[-1]
        for f, v in versions.items():
            drift['version_drift'].append({
                'file': f,
                'version': v,
                'expected': latest,
                'layer': 'layer1' if f in layer1_files else 'layer2'
            })

    terms_to_check = ['调研师', '研究员', '分析师', '设计师', '构建师']
    term_files = {}
    for f in layer1_files + layer2_files:
        terms = extract_terms(f, terms_to_check)
        if terms:
            term_files[f] = terms

    if term_files:
        primary_terms = {}
        for f, terms in term_files.items():
            if f in layer1_files:
                primary_terms = terms
                break
        if primary_terms:
            for f, terms in term_files.items():
                if f in layer2_files:
                    for term, count in primary_terms.items():
                        if term in terms:
                            continue
                        drift['naming_drift'].append({
                            'layer1_term': term,
                            'layer2_term': list(terms.keys())[0] if terms else '未知',
                            'files': [f]
                        })

    result = {'drift': drift, 'versions': versions}
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"漂移报告已保存到: {output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    return result


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="neat-freak文档漂移扫描")
    parser.add_argument("--layer1", nargs='+', required=True, help="Layer1文件(CLAUDE.md等)")
    parser.add_argument("--layer2", nargs='+', required=True, help="Layer2文件(README.md等)")
    parser.add_argument("--output", help="输出JSON文件路径")
    args = parser.parse_args()

    scan_files(args.layer1, args.layer2, args.output)