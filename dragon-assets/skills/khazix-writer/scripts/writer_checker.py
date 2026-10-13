# ~/.claude/skills/khazix-writer/scripts/writer_checker.py
import re
from typing import List, Tuple

FORBIDDEN_WORDS = [
    '说白了', '本质上', '这意味着', '换句话说', '不可否认',
    '首先', '其次', '最后', '近年来', '随着',
    '我们可以看到', '从某种意义上', '归根结底', '众所周知',
    '不得不承认', '事实上', '实际上', '当然',
    '从整体来看', '不难发现', '有鉴于此', '基于此', '据此',
    '在此基础上', '值得一提的是', '值得注意的是',
    '毫无疑问', '显而易见'
]

FORBIDDEN_PATTERNS = [
    r'首先[\s\S]{0,5}其次[\s\S]{0,5}最后',
    r'近年来', r'随着', r'在\w+时代',
    r'我们可以看到', r'从某种意义上',
    r'毫无疑问[地]?', r'显而易见[地]?'
]

FORBIDDEN_PUNCTUATION = [':', '——', '"', '"', '"', '"']

PATTERNS_COMPILED = [re.compile(p) for p in FORBIDDEN_PATTERNS]


def L1_hard_rules(text: str) -> Tuple[bool, List[str]]:
    """L1层硬规则审查"""
    violations = []
    for word in FORBIDDEN_WORDS:
        if word in text:
            violations.append(f"禁词: {word}")
    for i, pattern in enumerate(PATTERNS_COMPILED):
        matches = pattern.findall(text)
        for m in matches:
            violations.append(f"禁模式: {m[:20]}...")
    for p in FORBIDDEN_PUNCTUATION:
        count = text.count(p)
        if count > 1:
            violations.append(f"禁标点'{p}'出现{count}次")
    return len(violations) == 0, violations


def L2_style_check(text: str) -> Tuple[bool, List[str]]:
    """L2层风格一致性审查"""
    issues = []
    short_sentences = re.findall(r'[^。！？]+[。！？]', text)
    for i, s in enumerate(short_sentences[:-1]):
        next_s = short_sentences[i + 1]
        if len(s) < 15 and len(next_s) < 15:
            issues.append("可能过度对仗的短句")
    return len(issues) == 0, issues


def L3_content_check(text: str) -> Tuple[bool, List[str]]:
    """L3层内容质量审查"""
    issues = []
    has_specific = bool(re.search(r'[人名地名公司名产品名]', text))
    if not has_specific:
        issues.append("缺少具体案例支撑")
    paragraphs = text.split('\n\n')
    long_count = sum(1 for p in paragraphs if len(p) > 500)
    if long_count >= 2:
        issues.append("多个段落过长，可能缺少过渡")
    return len(issues) == 0, issues


def L4_living_check(text: str) -> Tuple[bool, List[str]]:
    """L4层活人感终审"""
    issues = []
    unique_chars = len(set(text))
    density = unique_chars / len(text) if len(text) > 0 else 0
    if density < 0.3:
        issues.append("文字重复度过高，可能缺乏个性化表达")
    return len(issues) == 0, issues


def full_review(text: str) -> dict:
    """完整四层审查"""
    result = {
        'L1_pass': False, 'L1_issues': [],
        'L2_pass': False, 'L2_issues': [],
        'L3_pass': False, 'L3_issues': [],
        'L4_pass': False, 'L4_issues': []
    }
    l1_pass, l1_issues = L1_hard_rules(text)
    result['L1_pass'] = l1_pass
    result['L1_issues'] = l1_issues

    if l1_pass:
        l2_pass, l2_issues = L2_style_check(text)
        result['L2_pass'] = l2_pass
        result['L2_issues'] = l2_issues

        if l2_pass:
            l3_pass, l3_issues = L3_content_check(text)
            result['L3_pass'] = l3_pass
            result['L3_issues'] = l3_issues

            if l3_pass:
                l4_pass, l4_issues = L4_living_check(text)
                result['L4_pass'] = l4_pass
                result['L4_issues'] = l4_issues

    return result


def review_file(file_path: str) -> dict:
    """审查文件内容"""
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    return full_review(text)


if __name__ == "__main__":
    import argparse, json
    parser = argparse.ArgumentParser(description="khazix-writer文章审查")
    parser.add_argument("file", help="文章文件路径")
    parser.add_argument("--report", action="store_true", help="输出详细报告")
    args = parser.parse_args()

    result = review_file(args.file)
    if args.report:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        passed = sum([result.get(f'L{i}_pass', False) for i in [1,2,3,4]])
        print(f"L1硬规则: {'✅' if result['L1_pass'] else '❌'} | L2风格: {'✅' if result['L2_pass'] else '❌'} | L3内容: {'✅' if result['L3_pass'] else '❌'} | L4活人感: {'✅' if result['L4_pass'] else '❌'}")
        if not result['L1_pass']:
            print("禁词/禁模式问题:", result['L1_issues'][:3])