#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简化的模板测试脚本"""

import sys
import os
from pathlib import Path

# 添加scripts目录到路径
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

# 修复Windows编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from render import TemplateManager

def main():
    print("\n" + "="*70)
    print("提词师模板测试")
    print("="*70 + "\n")

    try:
        manager = TemplateManager()
        templates = manager.list_templates()

        print(f"找到 {len(templates)} 个模板\n")

        for template in templates:
            print(f"✅ {template.name}")
            print(f"   框架: {template.framework}")
            print(f"   评分: {template.rating}/100")
            print(f"   优先级: {template.priority}")
            print()

        print("="*70)
        print("所有模板加载成功！")
        print("="*70 + "\n")

        # 测试渲染
        print("测试渲染功能...\n")

        template = manager.get_template('problem-decomposition')
        if template:
            result = template.render(
                task_description="测试任务：设计一个用户认证系统",
                context="Web应用，支持多种认证方式"
            )
            print(f"✅ 渲染成功，输出长度: {len(result)} 字符\n")
        else:
            print("❌ 找不到 problem-decomposition 模板\n")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
