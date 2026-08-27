#!/usr/bin/env python3
"""
free-claude-remote-session - IM平台远程Claude Code会话桥接守护进程
支持: Telegram / Discord / 飞书 / QQ
端口: Dragon Gateway 37778
"""

import argparse
import asyncio
import json
import os
import sqlite3
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

# ============ 配置路径 ============
SKILL_DIR = Path(__file__).parent.parent
SCRIPT_DIR = SKILL_DIR / "scripts"
CONFIG_DIR = SKILL_DIR / "configs"
LOG_DIR = SKILL_DIR / "logs"
DB_PATH = LOG_DIR / "sessions.db"

PLATFORMS = ["telegram", "discord", "feishu", "qq"]


# ============ 数据模型 ============
@dataclass
class SessionInfo:
    session_id: str
    im_platform: str
    im_user_id: str
    im_chat_id: str
    status: str  # created, running, paused, waiting_input, completed, failed, cancelled
    created_at: str
    updated_at: str
    task_summary: str = ""


@dataclass
class PlatformStatus:
    platform: str
    enabled: bool
    running: bool
    pid: Optional[int]
    last_heartbeat: Optional[str]
    error: Optional[str]


# ============ 数据库 ============
def get_db():
    """获取数据库连接"""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库"""
    conn = get_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            im_platform TEXT NOT NULL,
            im_user_id TEXT NOT NULL,
            im_chat_id TEXT NOT NULL,
            status TEXT DEFAULT 'created',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            task_summary TEXT DEFAULT ''
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS platform_status (
            platform TEXT PRIMARY KEY,
            enabled INTEGER DEFAULT 0,
            running INTEGER DEFAULT 0,
            pid INTEGER,
            last_heartbeat TEXT,
            error TEXT
        )
    """)
    for p in PLATFORMS:
        c.execute("INSERT OR IGNORE INTO platform_status (platform) VALUES (?)", (p,))
    conn.commit()
    conn.close()


# ============ 配置文件模板 ============
def create_template_config(platform: str) -> str:
    """创建平台配置模板"""
    templates = {
        "telegram": '''# ===== Telegram Bot 配置 =====
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_SESSION_TIMEOUT=3600
TELEGRAM_ALLOWED_USERS=user_id_1,user_id_2
TELEGRAM_ADMIN_USERS=admin_user_id

# Dragon Gateway 连接
DRAGON_GATEWAY_HOST=localhost
DRAGON_GATEWAY_PORT=37778
DRAGON_GATEWAY_TOKEN=

# 会话配置
SESSION_TIMEOUT=3600
MAX_CONCURRENT_SESSIONS=5
STREAM_FORMAT=telegram
''',
        "discord": '''# ===== Discord Bot 配置 =====
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_GUILD_ID=your_guild_id
DISCORD_ALLOWED_ROLES=role_id_1,role_id_2
DISCORD_ADMIN_ROLES=admin_role_id
DISCORD_CHANNEL_WHITELIST=channel_id_1,channel_id_2

# Dragon Gateway 连接
DRAGON_GATEWAY_HOST=localhost
DRAGON_GATEWAY_PORT=37778
DRAGON_GATEWAY_TOKEN=

# 会话配置
SESSION_TIMEOUT=3600
MAX_CONCURRENT_SESSIONS=5
STREAM_FORMAT=discord
''',
        "feishu": '''# ===== 飞书/Lark 配置 =====
FEISHU_APP_ID=cli_xxxxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
FEISHU_VERIFICATION_TOKEN=xxxxxxxxxxxxxxxx
FEISHU_ENCRYPT_KEY=xxxxxxxxxxxxxxxxxxxxxxxx
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx

# Dragon Gateway 连接
DRAGON_GATEWAY_HOST=localhost
DRAGON_GATEWAY_PORT=37778
DRAGON_GATEWAY_TOKEN=

# 会话配置
SESSION_TIMEOUT=3600
MAX_CONCURRENT_SESSIONS=5
STREAM_FORMAT=feishu
''',
        "qq": '''# ===== QQ (OpenClaw) 配置 =====
QQ_BOT_ID=your_qq_bot_id
QQ_APP_ID=your_app_id
QQ_APP_KEY=your_app_key
QQ_TOKEN=your_token

# Dragon Gateway 连接
DRAGON_GATEWAY_HOST=localhost
DRAGON_GATEWAY_PORT=37778
DRAGON_GATEWAY_TOKEN=

# 会话配置
SESSION_TIMEOUT=3600
MAX_CONCURRENT_SESSIONS=5
STREAM_FORMAT=qq
'''
    }
    return templates.get(platform, "")


# ============ 平台进程管理 ============
def get_platform_pid(platform: str) -> Optional[int]:
    """获取平台进程的PID"""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT pid FROM platform_status WHERE platform = ?", (platform,))
    row = c.fetchone()
    conn.close()
    return row["pid"] if row else None


def set_platform_status(platform: str, running: bool, pid: Optional[int] = None, error: Optional[str] = None):
    """更新平台状态"""
    conn = get_db()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("""
        UPDATE platform_status
        SET running = ?, pid = ?, last_heartbeat = ?, error = ?
        WHERE platform = ?
    """, (1 if running else 0, pid, now, error, platform))
    conn.commit()
    conn.close()


def is_process_running(pid: int) -> bool:
    """检查进程是否在运行"""
    try:
        if sys.platform == "win32":
            result = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"],
                                    capture_output=True, text=True)
            return str(pid) in result.stdout
        else:
            os.kill(pid, 0)
            return True
    except (ProcessLookupError, PermissionError, OSError):
        return False


def start_platform(platform: str) -> tuple[bool, Optional[int], Optional[str]]:
    """启动平台桥接"""
    config_file = CONFIG_DIR / f".env.{platform}"

    if not config_file.exists():
        config_file.write_text(create_template_config(platform))
        return False, None, f"配置文件不存在，已创建模板: {config_file}"

    adapter_script = SCRIPT_DIR / "platform_adapters" / f"{platform}_adapter.py"
    if not adapter_script.exists():
        return False, None, f"适配器脚本不存在: {adapter_script}"

    try:
        env = os.environ.copy()
        env_file = config_file.read_text()
        for line in env_file.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip()

        proc = subprocess.Popen(
            [sys.executable, str(adapter_script)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(1)
        if proc.poll() is None:
            set_platform_status(platform, True, proc.pid)
            return True, proc.pid, None
        else:
            stdout, stderr = proc.communicate()
            return False, None, f"启动失败: {stderr[:200]}"
    except Exception as e:
        return False, None, str(e)


def stop_platform(platform: str) -> tuple[bool, Optional[str]]:
    """停止平台桥接"""
    pid = get_platform_pid(platform)
    if not pid:
        return False, "进程未运行"

    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/PID", str(pid), "/F"],
                          capture_output=True)
        else:
            os.kill(pid, 9)
        set_platform_status(platform, False, None)
        return True, None
    except Exception as e:
        set_platform_status(platform, False, None, str(e))
        return False, str(e)


# ============ 命令实现 ============
def cmd_start(platform: str, all_platforms: bool) -> bool:
    """启动命令"""
    init_db()
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    if all_platforms:
        results = []
        for p in PLATFORMS:
            ok, pid, err = start_platform(p)
            status = f"[{p}] {'启动成功' if ok else '启动失败'}"
            if err:
                status += f": {err}"
            results.append(status)
        output = "\n".join(results)
        print(output)
        return all(r.startswith(f"[{p}] 启动成功") for r in results for p in PLATFORMS)

    ok, pid, err = start_platform(platform)
    if ok:
        print(f"[{platform}] 启动成功 (PID: {pid})")
        return True
    else:
        print(f"[{platform}] 启动失败: {err}")
        return False


def cmd_stop(platform: str, all_platforms: bool) -> bool:
    """停止命令"""
    if all_platforms:
        results = []
        for p in PLATFORMS:
            ok, err = stop_platform(p)
            status = f"[{p}] {'停止成功' if ok else '停止失败'}"
            if err:
                status += f": {err}"
            results.append(status)
        output = "\n".join(results)
        print(output)
        return all(r.startswith(f"[{p}] 停止成功") for r in results for p in PLATFORMS)

    ok, err = stop_platform(platform)
    if ok:
        print(f"[{platform}] 停止成功")
        return True
    else:
        print(f"[{platform}] 停止失败: {err}")
        return False


def cmd_status() -> bool:
    """状态命令"""
    init_db()
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM platform_status")
    rows = c.fetchall()
    conn.close()

    print("\n" + "=" * 60)
    print("  IM Remote Session Platform Status")
    print("=" * 60)

    if not rows:
        print("  无平台状态记录")
        print("=" * 60 + "\n")
        return True

    for row in rows:
        p = row["platform"]
        running = bool(row["running"])
        pid = row["pid"]
        heartbeat = row["last_heartbeat"]
        error = row["error"]

        status_icon = "🟢" if running else "⚪"
        pid_str = f"PID: {pid}" if pid else ""

        print(f"  {status_icon} {p.upper():10s} {pid_str:15s}")

        if heartbeat:
            print(f"      心跳: {heartbeat[:19]}")
        if error:
            print(f"      错误: {error[:50]}")

    print("=" * 60)

    # 会话统计
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as total FROM sessions")
    total = c.fetchone()["total"]
    c.execute("SELECT status, COUNT(*) as cnt FROM sessions GROUP BY status")
    stats = {r["status"]: r["cnt"] for r in c.fetchall()}
    conn.close()

    print(f"\n  会话统计:")
    print(f"    总计: {total}")
    for s, cnt in stats.items():
        print(f"    {s}: {cnt}")
    print()

    return True


def cmd_logs(platform: Optional[str], lines: int) -> bool:
    """日志命令"""
    log_file = LOG_DIR / "remote-session.log"

    if platform:
        log_file = LOG_DIR / f"{platform}.log"

    if not log_file.exists():
        print(f"日志文件不存在: {log_file}")
        return False

    content = log_file.read_text()
    log_lines = content.strip().split("\n")
    tail = log_lines[-lines:] if lines > 0 else log_lines

    print(f"-- [{platform or 'all'}] 最近 {lines} 行日志 --")
    print("\n".join(tail))
    return True


def cmd_reconfigure(platform: str) -> bool:
    """重新配置命令"""
    config_file = CONFIG_DIR / f".env.{platform}"
    template = create_template_config(platform)

    if config_file.exists():
        print(f"配置文件已存在: {config_file}")
        print("是否覆盖? (y/N): ", end="")
        response = input().strip().lower()
        if response != "y":
            print("取消覆盖")
            return False

    config_file.write_text(template)
    print(f"已创建配置模板: {config_file}")
    print("请编辑配置文件填入实际参数")
    return True


def cmd_doctor() -> bool:
    """诊断命令"""
    print("\n" + "=" * 60)
    print("  IM Remote Session Doctor")
    print("=" * 60)

    issues = []
    warnings = []

    # 检查目录
    for d, label in [(CONFIG_DIR, "配置目录"), (SCRIPT_DIR, "脚本目录"),
                      (LOG_DIR, "日志目录")]:
        if d.exists():
            print(f"  ✅ {label}: {d}")
        else:
            issues.append(f"{label} 不存在: {d}")

    # 检查脚本
    for p in PLATFORMS:
        adapter = SCRIPT_DIR / "platform_adapters" / f"{p}_adapter.py"
        if adapter.exists():
            print(f"  ✅ {p} 适配器: {adapter.name}")
        else:
            warnings.append(f"{p} 适配器不存在: {adapter}")

    # 检查配置文件
    for p in PLATFORMS:
        config = CONFIG_DIR / f".env.{p}"
        if config.exists():
            print(f"  ✅ {p} 配置: {config.name}")
        else:
            warnings.append(f"{p} 配置不存在: {config}")

    # 检查数据库
    if DB_PATH.exists():
        try:
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM sessions")
            c.execute("SELECT COUNT(*) FROM platform_status")
            conn.close()
            print(f"  ✅ 数据库: {DB_PATH}")
        except Exception as e:
            issues.append(f"数据库错误: {e}")
    else:
        print(f"  ⚠️  数据库未初始化（首次运行会自动创建）")

    # 检查 Dragon Gateway
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("localhost", 37778))
        sock.close()
        if result == 0:
            print(f"  ✅ Dragon Gateway: localhost:37778 可达")
        else:
            warnings.append("Dragon Gateway 端口 37778 不可达")
    except Exception as e:
        warnings.append(f"Dragon Gateway 检查失败: {e}")

    # 输出诊断结果
    print("=" * 60)
    if issues:
        print(f"\n  🔴 问题 ({len(issues)}):")
        for i in issues:
            print(f"    - {i}")

    if warnings:
        print(f"\n  🟡 警告 ({len(warnings)}):")
        for w in warnings:
            print(f"    - {w}")

    if not issues and not warnings:
        print(f"\n  🟢 所有检查通过!")
    elif not issues:
        print(f"\n  🟡 有 {len(warnings)} 个警告但可正常运行")
    else:
        print(f"\n  🔴 有 {len(issues)} 个问题需要修复")

    print()
    return len(issues) == 0


def cmd_test(platform: str) -> bool:
    """测试平台连接"""
    print(f"\n  测试 {platform} 平台连接...")
    config_file = CONFIG_DIR / f".env.{platform}"

    if not config_file.exists():
        print(f"  🔴 配置文件不存在: {config_file}")
        return False

    # 读取配置
    config = {}
    for line in config_file.read_text().strip().split("\n"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()

    # 验证必要配置
    if platform == "telegram":
        required = ["TELEGRAM_BOT_TOKEN"]
    elif platform == "discord":
        required = ["DISCORD_BOT_TOKEN"]
    elif platform == "feishu":
        required = ["FEISHU_APP_ID", "FEISHU_APP_SECRET"]
    elif platform == "qq":
        required = ["QQ_BOT_ID"]
    else:
        required = []

    missing = [k for k in required if not config.get(k) or config.get(k, "").startswith("your_")]

    if missing:
        print(f"  🔴 缺少配置: {missing}")
        print(f"  请编辑 {config_file} 填入实际值")
        return False

    print(f"  🟢 配置完整")
    return True


# ============ 主入口 ============
def main():
    parser = argparse.ArgumentParser(
        description="IM Remote Session Daemon - IM平台远程Claude Code会话桥接"
    )
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # start
    p_start = subparsers.add_parser("start", help="启动IM桥接服务")
    p_start.add_argument("--all", action="store_true", help="启动所有平台")
    p_start.add_argument("--platform", choices=PLATFORMS, help="指定平台")

    # stop
    p_stop = subparsers.add_parser("stop", help="停止IM桥接服务")
    p_stop.add_argument("--all", action="store_true", help="停止所有平台")
    p_stop.add_argument("--platform", choices=PLATFORMS, help="指定平台")

    # status
    subparsers.add_parser("status", help="查看状态")

    # logs
    p_logs = subparsers.add_parser("logs", help="查看日志")
    p_logs.add_argument("--platform", choices=PLATFORMS, help="指定平台")
    p_logs.add_argument("--lines", type=int, default=50, help="显示行数")

    # reconfigure
    p_rec = subparsers.add_parser("reconfigure", help="重新配置")
    p_rec.add_argument("--platform", choices=PLATFORMS, required=True, help="指定平台")

    # doctor
    subparsers.add_parser("doctor", help="诊断检查")

    # test
    p_test = subparsers.add_parser("test", help="测试连接")
    p_test.add_argument("--platform", choices=PLATFORMS, required=True, help="指定平台")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    success = False

    if args.command == "start":
        all_plat = getattr(args, "all", False)
        plat = getattr(args, "platform", None)
        if not all_plat and not plat:
            print("请指定 --all 或 --platform <name>")
            return
        success = cmd_start(plat, all_plat)

    elif args.command == "stop":
        all_plat = getattr(args, "all", False)
        plat = getattr(args, "platform", None)
        if not all_plat and not plat:
            print("请指定 --all 或 --platform <name>")
            return
        success = cmd_stop(plat, all_plat)

    elif args.command == "status":
        success = cmd_status()

    elif args.command == "logs":
        plat = getattr(args, "platform", None)
        lines = getattr(args, "lines", 50)
        success = cmd_logs(plat, lines)

    elif args.command == "reconfigure":
        success = cmd_reconfigure(args.platform)

    elif args.command == "doctor":
        success = cmd_doctor()

    elif args.command == "test":
        success = cmd_test(args.platform)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
