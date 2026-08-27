#!/usr/bin/env python3
"""
RTK Token Killer - 天龙引擎集成客户端
功能: 调用rtk命令并分析Token节省情况
"""

import subprocess
import sys
import json
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """执行命令并返回 (返回码, stdout, stderr)"""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def check_installation() -> bool:
    """检查RTK是否已安装"""
    code, _, _ = run_command(["rtk", "--version"])
    return code == 0


def init_for_claude_code() -> bool:
    """初始化Claude Code集成"""
    code, out, err = run_command(["rtk", "init", "-g", "--show"])
    if code == 0:
        print("✅ RTK已成功初始化Claude Code集成")
        print(out)
        return True
    else:
        print("❌ RTK初始化失败")
        print(err)
        return False


def show_savings() -> None:
    """显示Token节省统计"""
    code, out, err = run_command(["rtk", "gain"])
    if code == 0:
        print(out)
    else:
        print(f"⚠️ 获取节省统计失败: {err}")


def show_graph() -> None:
    """显示节省图表"""
    code, out, err = run_command(["rtk", "gain", "--graph"])
    if code == 0:
        print(out)
    else:
        print(f"⚠️ 获取图表失败: {err}")


def discover_opportunities() -> None:
    """发现优化机会"""
    code, out, err = run_command(["rtk", "discover"])
    if code == 0:
        print(out)
    else:
        print(f"⚠️ 发现优化机会失败: {err}")


def show_session_adoption() -> None:
    """显示会话采用情况"""
    code, out, err = run_command(["rtk", "session"])
    if code == 0:
        print(out)
    else:
        print(f"⚠️ 获取会话信息失败: {err}")


def main():
    if len(sys.argv) < 2:
        print("RTK Token Killer - 天龙引擎集成")
        print("用法: python rtk_client.py <command>")
        print("")
        print("命令:")
        print("  status     - 检查安装状态")
        print("  init       - 初始化Claude Code集成")
        print("  gain       - 显示Token节省统计")
        print("  graph      - 显示节省图表")
        print("  discover   - 发现优化机会")
        print("  session    - 显示会话采用情况")
        print("  all        - 显示所有统计")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "status":
        if check_installation():
            print("✅ RTK已安装")
        else:
            print("❌ RTK未安装，请运行: brew install rtk")

    elif cmd == "init":
        init_for_claude_code()

    elif cmd == "gain":
        show_savings()

    elif cmd == "graph":
        show_graph()

    elif cmd == "discover":
        discover_opportunities()

    elif cmd == "session":
        show_session_adoption()

    elif cmd == "all":
        print("📊 RTK Token Killer - 全局统计")
        print("=" * 50)
        show_savings()
        print("")
        show_graph()
        print("")
        discover_opportunities()
        print("")
        show_session_adoption()

    else:
        print(f"❌ 未知命令: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()