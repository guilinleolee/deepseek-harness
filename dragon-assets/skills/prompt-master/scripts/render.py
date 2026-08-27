#!/usr/bin/env python3
"""
提词师模板渲染引擎

功能:
1. 加载Markdown模板
2. 解析YAML frontmatter
3. 使用Jinja2渲染变量
4. 输出完整的提示词

使用方法:
    python render.py --template problem-decomposition --task "设计一个用户认证系统"
    python render.py --template system-design --task "电商系统" --qps "10000"
    python render.py --list  # 列出所有模板
"""

import argparse
import io
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# 修复Windows编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import yaml
from jinja2 import Environment, FileSystemLoader, Template

# 模板目录
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
P0_DIR = TEMPLATE_DIR / "p0"
P1_DIR = TEMPLATE_DIR / "p1"
P2_DIR = TEMPLATE_DIR / "p2"


class PromptTemplate:
    """提示词模板类"""

    def __init__(self, template_path: Path):
        self.path = template_path
        self.metadata = {}
        self.content = ""
        self.template = None
        self._load()

    def _load(self):
        """加载模板文件"""
        with open(self.path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                self.metadata = yaml.safe_load(parts[1])
                self.content = parts[2].strip()
            else:
                self.content = content
        else:
            self.content = content

        # 创建Jinja2模板
        self.template = Template(self.content)

    def render(self, **kwargs) -> str:
        """渲染模板"""
        return self.template.render(**kwargs)

    @property
    def name(self) -> str:
        """模板名称"""
        return self.metadata.get('name', self.path.stem)

    @property
    def framework(self) -> str:
        """使用的框架"""
        return self.metadata.get('framework', 'Unknown')

    @property
    def priority(self) -> str:
        """优先级"""
        return self.metadata.get('priority', 'P3')

    @property
    def rating(self) -> int:
        """评分"""
        return self.metadata.get('rating', 0)

    @property
    def tags(self) -> list:
        """标签"""
        return self.metadata.get('tags', [])

    def __repr__(self) -> str:
        return f"PromptTemplate(name={self.name}, framework={self.framework}, rating={self.rating})"


class TemplateManager:
    """模板管理器"""

    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_all()

    def _load_all(self):
        """加载所有模板"""
        for priority_dir in [P0_DIR, P1_DIR, P2_DIR]:
            if not priority_dir.exists():
                continue

            for template_file in priority_dir.glob("*.md"):
                template = PromptTemplate(template_file)
                self.templates[template.path.stem] = template

    def list_templates(self, priority: Optional[str] = None) -> list:
        """列出模板"""
        templates = list(self.templates.values())

        if priority:
            templates = [t for t in templates if t.priority == priority]

        # 按评分降序
        templates.sort(key=lambda t: t.rating, reverse=True)

        return templates

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """获取模板"""
        return self.templates.get(name)

    def search_templates(self, keyword: str) -> list:
        """搜索模板"""
        keyword = keyword.lower()

        results = []
        for template in self.templates.values():
            # 匹配名称、标签、框架
            if (keyword in template.name.lower() or
                any(keyword in tag.lower() for tag in template.tags) or
                keyword in template.framework.lower()):
                results.append(template)

        return results


def render_template(name: str, variables: Dict[str, Any]) -> str:
    """渲染单个模板"""
    manager = TemplateManager()
    template = manager.get_template(name)

    if not template:
        print(f"❌ 错误: 模板 '{name}' 不存在", file=sys.stderr)
        print(f"   使用 --list 查看所有可用模板", file=sys.stderr)
        sys.exit(1)

    # 设置默认值
    defaults = {
        'language': 'python',
        'framework': '未指定',
        'context_description': '未提供上下文',
        'issues': '未明确，请分析',
        'review_focus': '全面审查：功能、性能、安全、可维护性',
        'test_requirements': '完整覆盖功能、性能、安全',
        'special_requirements': '无',
        'audience': '技术开发人员',
        'tried_solutions': '无',
        'error_logs': '无日志',
        'os': '未指定',
        'version': '未指定',
        'reproduction_steps': '未指定',
        'user_scale': '未指定',
        'qps': '未指定',
        'data_scale': '未指定',
        'budget': '未指定',
        'team_size': '未指定',
        'time_constraint': '未指定',
        'budget_constraint': '未指定',
        'resource_constraint': '未指定',
        'target_users': '未指定',
        'business_context': '未指定',
        'key_info': '请根据主题生成',
        'tech_stack': '未指定',
        'deployment': '未指定',
        'scale': '未指定',
        'performance_requirement': '未指定',
        'availability_requirement': '未指定',
        'scalability_requirement': '未指定',
        'team_stack': '未指定',
        'timeline': '未指定',
    }

    # 合并变量
    variables = {**defaults, **variables}

    # 渲染
    return template.render(**variables)


def list_templates(priority: Optional[str] = None):
    """列出所有模板"""
    manager = TemplateManager()
    templates = manager.list_templates(priority)

    if not templates:
        print("❌ 未找到模板")
        return

    print(f"\n📋 共找到 {len(templates)} 个模板\n")

    # 按优先级分组
    groups = {
        'P0': [],
        'P1': [],
        'P2': [],
    }

    for template in templates:
        groups[template.priority].append(template)

    for pri in ['P0', 'P1', 'P2']:
        if priority and priority != pri:
            continue

        templates_in_group = groups[pri]
        if not templates_in_group:
            continue

        print(f"\n{'='*60}")
        print(f" {pri} 核心模板")
        print(f"{'='*60}\n")

        for template in templates_in_group:
            print(f"📄 {template.name}")
            print(f"   框架: {template.framework}")
            print(f"   评分: {template.rating}/100")
            print(f"   标签: {', '.join(template.tags)}")
            print(f"   文件: {template.path.relative_to(TEMPLATE_DIR.parent.parent.parent)}")
            print()


def show_template_info(name: str):
    """显示模板详情"""
    manager = TemplateManager()
    template = manager.get_template(name)

    if not template:
        print(f"❌ 错误: 模板 '{name}' 不存在")
        return

    print(f"\n📄 模板: {template.name}")
    print(f"{'='*60}")
    print(f"框架: {template.framework}")
    print(f"优先级: {template.priority}")
    print(f"评分: {template.rating}/100")
    print(f"标签: {', '.join(template.tags)}")
    print(f"文件: {template.path}")
    print()

    print(f"元数据:")
    for key, value in template.metadata.items():
        if key not in ['name', 'framework', 'priority', 'rating', 'tags']:
            print(f"  {key}: {value}")

    print()
    print("必需变量:")
    # 提取模板中的变量
    variables = set()
    import re
    pattern = r'\{\{\s*(\w+)\s*(?:\|[^}]+)?\}\}'
    matches = re.findall(pattern, template.content)
    for var in set(matches):
        print(f"  - {var}")


def search_templates(keyword: str):
    """搜索模板"""
    manager = TemplateManager()
    results = manager.search_templates(keyword)

    if not results:
        print(f"❌ 未找到与 '{keyword}' 相关的模板")
        return

    print(f"\n🔍 搜索 '{keyword}' 找到 {len(results)} 个结果:\n")

    for template in results:
        print(f"📄 {template.name} ({template.priority})")
        print(f"   {template.framework} - 评分: {template.rating}/100")
        print(f"   标签: {', '.join(template.tags)}")
        print()


def interactive_mode():
    """交互式模式"""
    manager = TemplateManager()

    print("\n🎨 提词师 - 交互式模式\n")
    print("="*60)

    # 选择模板
    print("\n可用模板:")
    templates = manager.list_templates('P0')  # 默认只显示P0

    for i, template in enumerate(templates, 1):
        print(f"{i:2}. {template.name} ({template.framework})")

    choice = input("\n请选择模板编号 (或输入关键词搜索): ").strip()

    # 搜索
    if not choice.isdigit():
        search_templates(choice)
        return

    # 渲染
    idx = int(choice) - 1
    if idx < 0 or idx >= len(templates):
        print("❌ 无效的选择")
        return

    template = templates[idx]

    print(f"\n✅ 已选择: {template.name}")
    print(f"   框架: {template.framework}")
    print(f"   评分: {template.rating}/100")

    # 收集变量
    print("\n请提供以下信息:")
    print("(直接回车使用默认值)\n")

    variables = {}

    # 提取模板中的变量
    import re
    pattern = r'\{\{\s*(\w+)\s*(?:\|[^}]+)?\}\}'
    matches = re.findall(pattern, template.content)

    for var in set(matches):
        value = input(f"{var}: ").strip()
        if value:
            variables[var] = value

    # 渲染
    print("\n" + "="*60)
    print("📝 渲染结果:")
    print("="*60 + "\n")

    result = template.render(**variables)
    print(result)

    # 保存选项
    save = input("\n是否保存到文件? (y/n): ").strip().lower()
    if save == 'y':
        filename = input("请输入文件名 (默认: prompt.md): ").strip() or "prompt.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"✅ 已保存到 {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='提词师模板渲染引擎',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 渲染模板
  python render.py -t problem-decomposition -v task="设计用户认证系统"

  # 列出所有模板
  python render.py --list

  # 只显示P0模板
  python render.py --list --priority P0

  # 搜索模板
  python render.py --search "代码"

  # 查看模板详情
  python render.py --info problem-decomposition

  # 交互式模式
  python render.py --interactive
        """
    )

    parser.add_argument('-t', '--template', help='模板名称')
    parser.add_argument('-v', '--var', nargs='*', metavar='KEY=VALUE',
                       help='模板变量 (如: task="设计系统" language="java")')
    parser.add_argument('--list', action='store_true', help='列出所有模板')
    parser.add_argument('--priority', choices=['P0', 'P1', 'P2'],
                       help='按优先级筛选')
    parser.add_argument('--search', metavar='KEYWORD', help='搜索模板')
    parser.add_argument('--info', metavar='TEMPLATE', help='查看模板详情')
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='交互式模式')

    args = parser.parse_args()

    # 解析变量
    variables = {}
    if args.var:
        for item in args.var:
            if '=' in item:
                key, value = item.split('=', 1)
                variables[key.strip()] = value.strip()

    # 执行操作
    if args.interactive:
        interactive_mode()
    elif args.list:
        list_templates(args.priority)
    elif args.search:
        search_templates(args.search)
    elif args.info:
        show_template_info(args.info)
    elif args.template:
        result = render_template(args.template, variables)
        print(result)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
