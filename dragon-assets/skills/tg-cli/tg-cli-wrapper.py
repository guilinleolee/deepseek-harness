#!/usr/bin/env python3
"""
tg-cli 安全封装器 - 天龙引擎 V8.22
提供速率限制、风险提示和安全调用

使用方式:
    python tg-cli-wrapper.py search "关键词" --yaml
    python tg-cli-wrapper.py refresh --max-chats 50
    python tg-cli-wrapper.py export "GroupName" -f yaml -o out.yaml
"""

import subprocess
import sys
import os
import time
from pathlib import Path

# 安全配置
DEFAULT_MAX_CHATS = 50
DEFAULT_DELAY = 1  # 秒
MAX_DAILY_SYNCS = 2  # 每天最多同步次数

# 风险命令列表（需要额外确认）
RISKY_COMMANDS = ['send', 'sync-all', 'purge']

# 只读命令列表（安全）
SAFE_COMMANDS = ['chats', 'status', 'whoami', 'history', 'search', 'filter',
                 'recent', 'today', 'stats', 'top', 'timeline', 'info', 'export']


def check_daily_sync_limit():
    """检查每日同步限制"""
    limit_file = Path.home() / '.tg-cli-daily-sync'
    today = time.strftime('%Y-%m-%d')

    if limit_file.exists():
        content = limit_file.read_text().strip().split('\n')
        if content[0] == today:
            sync_count = int(content[1]) if len(content) > 1 else 0
            if sync_count >= MAX_DAILY_SYNCS:
                return False, sync_count
            return True, sync_count

    return True, 0


def increment_daily_sync():
    """增加每日同步计数"""
    limit_file = Path.home() / '.tg-cli-daily-sync'
    today = time.strftime('%Y-%m-%d')

    if limit_file.exists():
        content = limit_file.read_text().strip().split('\n')
        if content[0] == today:
            sync_count = int(content[1]) if len(content) > 1 else 0
            sync_count += 1
        else:
            sync_count = 1
    else:
        sync_count = 1

    limit_file.write_text(f"{today}\n{sync_count}")


def print_risk_warning(command):
    """打印风险警告"""
    warnings = {
        'send': "⚠️  警告: 发送消息会使用您的个人账号，请确认内容合规。",
        'sync-all': "⚠️  警告: 批量同步可能触发速率限制，建议使用 --max-chats 限制数量。",
        'purge': "⚠️  警告: 清除缓存将删除本地数据，此操作不可逆。",
    }
    print(warnings.get(command, "⚠️  警告: 此操作存在风险，请确认后继续。"))
    print("按 Enter 继续，Ctrl+C 取消...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n已取消。")
        sys.exit(1)


def run_safe_command(args):
    """运行只读命令（安全）"""
    cmd = ['tg'] + args

    # 添加默认参数
    if '--yaml' not in args and '--json' not in args:
        cmd.append('--yaml')

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode


def run_sync_command(args):
    """运行同步命令（带速率限制）"""
    # 检查每日限制
    can_sync, count = check_daily_sync_limit()
    if not can_sync:
        print(f"❌ 错误: 今日同步次数已达上限 ({MAX_DAILY_SYNCS}次/天)")
        print("建议: 明天再试或调整 MAX_DAILY_SYNCS 配置")
        return 1

    print(f"📊 今日已同步 {count} 次，剩余 {MAX_DAILY_SYNCS - count} 次")

    # 添加速率限制参数
    if '--max-chats' not in args:
        args = ['--max-chats', str(DEFAULT_MAX_CHATS)] + args

    cmd = ['tg'] + args
    print(f"🔄 执行: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode == 0:
        increment_daily_sync()

    return result.returncode


def main():
    if len(sys.argv) < 2:
        print("用法: tg-cli-wrapper.py <command> [args...]")
        print("\n可用命令:")
        print("  只读命令（安全）: chats, status, whoami, history, search, filter,")
        print("                    recent, today, stats, top, timeline, info, export")
        print("  同步命令（速率限制）: refresh, sync, sync-all")
        print("  风险命令（需确认）: send, purge")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[1:]

    # 安全检查
    if command in RISKY_COMMANDS:
        print_risk_warning(command)

    # 分类处理
    if command in ['refresh', 'sync', 'sync-all']:
        sys.exit(run_sync_command(args))
    elif command in SAFE_COMMANDS:
        sys.exit(run_safe_command(args))
    elif command in RISKY_COMMANDS:
        sys.exit(run_safe_command(args))
    else:
        # 未知命令，直接执行
        print(f"⚠️  未知命令: {command}")
        sys.exit(run_safe_command(args))


if __name__ == '__main__':
    main()