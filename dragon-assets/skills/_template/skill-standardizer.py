#!/usr/bin/env python3
"""
SKILL.md 标准化工具
将现有SKILL.md转换为L0→L1→L2三级渐进披露格式

功能:
- 检查SKILL.md是否符合标准格式
- 自动转换旧格式到新格式
- 生成标准化报告
"""

import os
import re
import sys
from pathlib import Path
from typing import Optional, Dict, List
import argparse
import frontmatter

# L0: 一句话描述 (≤15字)
L0_PATTERN = r'^## L0:.*?\n([^\n]+)'

# L1: 使用场景 (50-100字)
L1_PATTERN = r'^## L1:.*?\n([\s\S]+?)(?=^## L2:|^---$)'

# L2: 详细文档
L2_PATTERN = r'^## L2:.*?\n([\s\S]+)$'

# Frontmatter字段
REQUIRED_FIELDS = ['name', 'description']
OPTIONAL_FIELDS = ['allowed-tools', 'context', 'version', 'author']


def analyze_skill(skill_path: Path) -> Dict:
    """分析SKILL.md并返回分析结果"""
    try:
        post = frontmatter.loads(skill_path.read_text(encoding='utf-8'))
        content = post.content
    except Exception as e:
        return {
            'valid': False,
            'error': str(e),
            'path': str(skill_path)
        }

    result = {
        'valid': True,
        'path': str(skill_path),
        'has_frontmatter': True,
        'has_l0': False,
        'has_l1': False,
        'has_l2': False,
        'l0_length': 0,
        'l1_length': 0,
        'issues': [],
        'suggestions': []
    }

    # 检查Frontmatter
    for field in REQUIRED_FIELDS:
        if field not in post.metadata:
            result['issues'].append(f"缺少必需字段: {field}")

    # 检查L0
    l0_match = re.search(L0_PATTERN, content, re.MULTILINE)
    if l0_match:
        result['has_l0'] = True
        l0_content = l0_match.group(1).strip()
        result['l0_length'] = len(l0_content)
        if len(l0_content) > 15:
            result['issues'].append(f"L0描述超过15字: {len(l0_content)}字")
    else:
        result['issues'].append("缺少L0章节")

    # 检查L1
    l1_match = re.search(L1_PATTERN, content, re.MULTILINE)
    if l1_match:
        result['has_l1'] = True
        l1_content = l1_match.group(1).strip()
        result['l1_length'] = len(l1_content)
        if len(l1_content) < 50:
            result['suggestions'].append(f"L1描述可能不足50字: {len(l1_content)}字")
        elif len(l1_content) > 100:
            result['suggestions'].append(f"L1描述可能超过100字: {len(l1_content)}字")
    else:
        result['issues'].append("缺少L1章节")

    # 检查L2
    l2_match = re.search(L2_PATTERN, content, re.MULTILINE)
    if l2_match:
        result['has_l2'] = True
    else:
        result['issues'].append("缺少L2章节")

    # 验证完整性
    result['is_complete'] = (
        result['has_l0'] and
        result['has_l1'] and
        result['has_l2'] and
        len(result['issues']) == 0
    )

    return result


def generate_l0(content: str) -> str:
    """从内容生成L0描述"""
    # 提取description或第一段
    if content:
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) <= 15:
                return line
        return f"技能功能描述 ({len(content)}字)"
    return "技能功能描述"


def generate_l1(skill_path: Path) -> str:
    """生成L1使用场景"""
    return """
**适用场景**：
- 主要使用场景描述
- 次要使用场景描述

**触发关键词**：`/skill-name`、`关键词触发`
""".strip()


def upgrade_to_standard(content: str, name: str) -> str:
    """将旧格式升级为标准三级格式"""

    # 提取现有内容
    existing = {
        'description': '',
        'examples': [],
        'notes': []
    }

    # 提取description
    desc_match = re.search(r'description[:：]\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
    if desc_match:
        existing['description'] = desc_match.group(1).strip()

    # 提取示例
    examples = re.findall(r'```[\s\S]*?```', content)
    existing['examples'] = examples

    # 生成标准格式
    l0 = existing['description'][:15] if existing['description'] else f"{name}技能"

    l1 = f"""
**适用场景**：
- {existing['description'] or '主要使用场景'}

**触发关键词**：`/{name}`

""".strip()

    l2 = f"""
### 完整功能说明

{existing['description'] or '技能详细功能说明'}

### 使用示例

{''.join(existing['examples']) if existing['examples'] else '```bash\n# 示例命令\n/skill-name\n```'}

### 配置选项

| 选项 | 默认值 | 说明 |
|------|-------|------|
| option1 | default | 选项说明 |

### 注意事项

- 注意事项1
- 注意事项2
""".strip()

    return f"""## L0: 一句话描述 (≤15字)
{l0}

## L1: 使用场景 (50-100字)
{l1}

## L2: 详细文档
{l2}
"""


def check_directory(skills_dir: Path) -> List[Dict]:
    """检查目录下所有SKILL.md"""
    results = []

    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir() and skill_dir.name != '_template':
            skill_file = skill_dir / 'SKILL.md'
            if skill_file.exists():
                result = analyze_skill(skill_file)
                result['skill_name'] = skill_dir.name
                results.append(result)

    return results


def print_report(results: List[Dict]):
    """打印分析报告"""
    total = len(results)
    complete = sum(1 for r in results if r.get('is_complete', False))
    valid = sum(1 for r in results if r.get('valid', False))

    print("\n" + "="*60)
    print("📊 SKILL.md 标准化分析报告")
    print("="*60)
    print(f"\n总计检查: {total} 个技能")
    print(f"格式完整: {complete} ({complete/total*100:.1f}%)")
    print(f"格式有效: {valid} ({valid/total*100:.1f}%)")

    # 问题汇总
    all_issues = []
    for r in results:
        if not r.get('is_complete', False):
            all_issues.extend(r.get('issues', []))

    if all_issues:
        print(f"\n📋 问题汇总 ({len(all_issues)} 项):")
        from collections import Counter
        issue_counts = Counter(all_issues)
        for issue, count in issue_counts.most_common(10):
            print(f"  - {issue}: {count}次")

    # 详细结果
    print(f"\n📝 详细结果:")
    print("-"*60)

    for r in results:
        status = "✅" if r.get('is_complete', False) else "⚠️"
        print(f"{status} {r.get('skill_name', 'unknown')}")
        if r.get('l0_length', 0) > 0:
            print(f"   L0: {r['l0_length']}字", end="")
        if r.get('l1_length', 0) > 0:
            print(f" | L1: {r['l1_length']}字", end="")
        print()

        if r.get('issues'):
            for issue in r['issues'][:2]:
                print(f"   ⚠️ {issue}")

    print("="*60)


def main():
    parser = argparse.ArgumentParser(description="SKILL.md 标准化工具")
    parser.add_argument('path', nargs='?', help='技能目录或文件路径')
    parser.add_argument('--upgrade', '-u', action='store_true', help='自动升级旧格式')
    parser.add_argument('--template', '-t', action='store_true', help='生成标准化模板')

    args = parser.parse_args()

    if args.template:
        template = Path(__file__).parent / 'SKILL.md'
        if template.exists():
            print(template.read_text(encoding='utf-8'))
        return

    if not args.path:
        # 默认检查用户skills目录
        skills_dir = Path.home() / '.claude' / 'skills'
    else:
        skills_dir = Path(args.path)

    if not skills_dir.exists():
        print(f"❌ 路径不存在: {skills_dir}")
        sys.exit(1)

    if skills_dir.is_file():
        # 单个文件
        results = [analyze_skill(skills_dir)]
    else:
        # 目录
        results = check_directory(skills_dir)

    print_report(results)

    # 自动升级
    if args.upgrade:
        print("\n🔄 开始自动升级...")
        for r in results:
            if not r.get('is_complete', False):
                skill_path = Path(r['path'])
                content = skill_path.read_text(encoding='utf-8')

                try:
                    post = frontmatter.loads(content)
                    new_format = upgrade_to_standard(
                        post.content,
                        r.get('skill_name', 'unknown')
                    )

                    # 保留frontmatter
                    new_content = "---\n"
                    for key, value in post.metadata.items():
                        new_content += f"{key}: {value}\n"
                    new_content += "---\n\n" + new_format

                    skill_path.write_text(new_content, encoding='utf-8')
                    print(f"✅ 已升级: {r.get('skill_name')}")
                except Exception as e:
                    print(f"❌ 升级失败: {r.get('skill_name')}: {e}")


if __name__ == "__main__":
    main()
