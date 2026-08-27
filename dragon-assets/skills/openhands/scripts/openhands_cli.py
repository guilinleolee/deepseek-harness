#!/usr/bin/env python3
"""
OpenHands CLI Wrapper for 天龙引擎
Usage: python openhands_cli.py --task "task description" [--mode mode]
"""

import argparse
import os
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description='OpenHands CLI for 天龙引擎')
    parser.add_argument('--task', required=True, help='Task description')
    parser.add_argument('--repo-path', default='.', help='Repository path')
    parser.add_argument('--mode', default='interactive',
                        choices=['interactive', 'read-only', 'auto'],
                        help='Execution mode')
    parser.add_argument('--model', default='claude-sonnet-4-20250514',
                        help='LLM model to use')
    parser.add_argument('--max-steps', type=int, default=50,
                        help='Maximum steps')

    args = parser.parse_args()

    # Build command
    cmd = ['openhands']

    if args.mode == 'read-only':
        cmd.extend(['--mode', 'readonly'])
    elif args.mode == 'auto':
        cmd.extend(['--mode', 'auto'])
    else:
        cmd.extend(['--mode', 'interactive'])

    cmd.extend(['--task', args.task])
    cmd.extend(['--repo', args.repo_path])
    cmd.extend(['--model', args.model])
    cmd.extend(['--max-steps', str(args.max_steps)])

    print(f"🎯 天龙引擎 × OpenHands")
    print(f"📋 任务: {args.task}")
    print(f"📂 路径: {args.repo_path}")
    print(f"⚙️ 模式: {args.mode}")
    print()

    # Execute
    try:
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("❌ OpenHands未安装")
        print("💡 安装命令: pip install openhands")
        sys.exit(1)

if __name__ == '__main__':
    main()
