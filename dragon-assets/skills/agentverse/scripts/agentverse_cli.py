#!/usr/bin/env python3
"""
AgentVerse CLI Wrapper for 天龙引擎
Usage: python agentverse_cli.py --task "task" --template template [--agents N]
"""

import argparse
import os
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description='AgentVerse CLI for 天龙引擎')
    parser.add_argument('--task', required=True, help='Task description')
    parser.add_argument('--template', default='research',
                        choices=['debate', 'research', 'troubleshooting', 'design', 'negotiation'],
                        help='Simulation template')
    parser.add_argument('--agents', type=int, default=4,
                        help='Number of agents')
    parser.add_argument('--max-turns', type=int, default=20,
                        help='Maximum turns')
    parser.add_argument('--output', default='./simulation_results/',
                        help='Output directory')

    args = parser.parse_args()

    # Build command
    cmd = ['agentverse']
    cmd.extend(['--template', args.template])
    cmd.extend(['--agents', str(args.agents)])
    cmd.extend(['--max-turns', str(args.max_turns)])
    cmd.extend(['--output', args.output])

    print(f"🎯 天龙引擎 × AgentVerse")
    print(f"📋 任务: {args.task}")
    print(f"📋 模板: {args.template}")
    print(f"🤖 Agent数: {args.agents}")
    print()

    # Execute simulation
    try:
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("❌ AgentVerse未安装")
        print("💡 安装命令: pip install agentverse")
        sys.exit(1)

if __name__ == '__main__':
    main()
