#!/usr/bin/env python3
"""
Mastra CLI Wrapper for 天龙引擎
Usage: python mastra_cli.py --task "task" --template template [--project project_name]
"""

import argparse
import os
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description='Mastra CLI for 天龙引擎')
    parser.add_argument('--task', required=True, help='Task description')
    parser.add_argument('--template', default='agent',
                        choices=['agent', 'tool', 'workflow', 'fullstack'],
                        help='Project template')
    parser.add_argument('--project', default='mastra-app',
                        help='Project name')
    parser.add_argument('--model', default='claude-sonnet-4-20250514',
                        help='LLM model')

    args = parser.parse_args()

    print(f"🎯 天龙引擎 × Mastra")
    print(f"📋 任务: {args.task}")
    print(f"📋 模板: {args.template}")
    print(f"📂 项目: {args.project}")
    print()

    if args.template == 'fullstack':
        # Create full-stack project
        cmd = ['npx', 'create-mastra-app', args.project]
        subprocess.run(cmd, check=False)
    else:
        # Use mastra CLI
        cmd = ['mastra', 'new', f'--template={args.template}', f'--name={args.project}']
        try:
            result = subprocess.run(cmd, check=False)
            sys.exit(result.returncode)
        except FileNotFoundError:
            print("❌ Mastra未安装")
            print("💡 安装命令: npm install -g @mastra/cli && npm install @mastra/core")
            sys.exit(1)

if __name__ == '__main__':
    main()
