#!/usr/bin/env python3
"""
Swarms CLI Wrapper for 天龙引擎
Usage: python swarms_cli.py --task "task" --mode mode [--agent-count N]
"""

import argparse
import os
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description='Swarms CLI for 天龙引擎')
    parser.add_argument('--task', required=True, help='Task description')
    parser.add_argument('--mode', default='hierarchical',
                        choices=['sequential', 'parallel', 'hierarchical', 'swarm'],
                        help='Orchestration mode')
    parser.add_argument('--agent-count', type=int, default=10,
                        help='Number of agents')
    parser.add_argument('--timeout', type=int, default=3600,
                        help='Timeout in seconds')
    parser.add_argument('--output', default='./swarms_results/',
                        help='Output directory')

    args = parser.parse_args()

    # Build command
    cmd = ['swarms']
    cmd.extend(['--mode', args.mode])
    cmd.extend(['--agents', str(args.agent_count)])
    cmd.extend(['--timeout', str(args.timeout)])
    cmd.extend(['--output', args.output])

    print(f"🎯 天龙引擎 × Swarms")
    print(f"📋 任务: {args.task}")
    print(f"⚙️ 模式: {args.mode}")
    print(f"🤖 Agent数: {args.agent_count}")
    print()

    # Execute
    try:
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("❌ Swarms未安装")
        print("💡 安装命令: pip install swarms")
        sys.exit(1)

if __name__ == '__main__':
    main()
