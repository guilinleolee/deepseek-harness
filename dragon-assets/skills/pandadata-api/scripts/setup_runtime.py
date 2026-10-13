#!/usr/bin/env python3
"""
Pandadata Runtime 设置脚本

自动安装依赖、配置环境变量、验证连接

Usage:
    python setup_runtime.py
    python setup_runtime.py --api-key YOUR_KEY
    python setup_runtime.py --check
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


def print_step(msg: str, status: str = "info"):
    """打印步骤信息"""
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
    }
    print(f"{icons.get(status, 'ℹ️')} {msg}")


def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_step(f"Python {version.major}.{version.minor} 不满足要求（需要 >= 3.8）", "error")
        return False
    print_step(f"Python {version.major}.{version.minor}.{version.micro} ✓", "success")
    return True


def check_dependencies():
    """检查依赖"""
    required = ["requests"]
    missing = []

    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        print_step(f"缺少依赖: {', '.join(missing)}", "warning")
        return False
    return True


def install_dependencies():
    """安装依赖"""
    print_step("安装依赖...")

    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "requests", "pandas"],
            check=True,
            capture_output=True
        )
        print_step("依赖安装成功", "success")
        return True
    except subprocess.CalledProcessError as e:
        print_step(f"依赖安装失败: {e}", "error")
        return False


def check_api_key(api_key: str = None):
    """检查 API Key"""
    key = api_key or os.environ.get("PANDADATA_API_KEY", "")

    if not key:
        print_step("未设置 PANDADATA_API_KEY", "warning")
        print_step("请设置环境变量或在 .env 文件中添加:")
        print_step("  PANDADATA_API_KEY=your-api-key", "info")
        return False

    print_step("API Key 已配置 ✓", "success")
    return True


def test_connection():
    """测试连接"""
    print_step("测试连接...")

    try:
        from pandadata_runtime import PandadataRuntime

        runtime = PandadataRuntime()
        result = runtime.call("get_last_trade_date")

        if result:
            print_step(f"连接成功！最近交易日: {result}", "success")
            return True
        else:
            print_step("连接测试返回空数据", "warning")
            return False

    except Exception as e:
        print_step(f"连接失败: {e}", "error")
        return False


def setup_env_file(api_key: str = None):
    """设置 .env 文件"""
    env_file = Path(".env")

    if env_file.exists():
        print_step(".env 文件已存在", "info")
        with open(env_file, "r") as f:
            content = f.read()

        if "PANDADATA_API_KEY" in content:
            print_step("PANDADATA_API_KEY 已配置 ✓", "success")
            return True
    else:
        content = ""

    if api_key:
        if content and not content.endswith("\n"):
            content += "\n"
        content += f"PANDADATA_API_KEY={api_key}\n"

        with open(env_file, "w") as f:
            f.write(content)

        print_step(".env 文件已更新", "success")
        return True

    return False


def setup_shell_completion():
    """设置 Shell 自动补全"""
    shell = os.environ.get("SHELL", "")

    if "zsh" in shell:
        rc_file = Path.home() / ".zshrc"
        completion_line = 'eval "$(_pandadata_runtime_completion)"'
    elif "bash" in shell:
        rc_file = Path.home() / ".bashrc"
        completion_line = 'eval "$(_pandadata_runtime_completion)"'
    else:
        print_step("不支持的 Shell，跳过自动补全配置", "warning")
        return False

    if rc_file.exists():
        with open(rc_file, "r") as f:
            content = f.read()

        if completion_line in content:
            print_step("Shell 自动补全已配置 ✓", "success")
            return True

    print_step(f"可手动添加以下内容到 {rc_file}:", "info")
    print_step(f"  {completion_line}", "info")
    return False


def main():
    parser = argparse.ArgumentParser(description="Pandadata Runtime 设置")
    parser.add_argument("--api-key", help="Pandadata API Key")
    parser.add_argument("--check", action="store_true", help="仅检查状态")
    parser.add_argument("--install", action="store_true", help="安装依赖")

    args = parser.parse_args()

    print("=" * 50)
    print("Pandadata Runtime 设置")
    print("=" * 50)

    # 步骤 1: 检查 Python 版本
    print("\n[1/5] 检查 Python 版本...")
    if not check_python_version():
        sys.exit(1)

    # 步骤 2: 检查/安装依赖
    print("\n[2/5] 检查依赖...")
    if not check_dependencies() or args.install:
        if not install_dependencies():
            sys.exit(1)

    # 步骤 3: 设置 API Key
    print("\n[3/5] 检查 API Key...")
    if args.api_key:
        setup_env_file(args.api_key)
    check_api_key(args.api_key)

    # 步骤 4: 测试连接
    print("\n[4/5] 测试连接...")
    test_connection()

    # 步骤 5: Shell 自动补全
    print("\n[5/5] Shell 自动补全...")
    setup_shell_completion()

    print("\n" + "=" * 50)
    print("设置完成！")
    print("=" * 50)
    print("\n使用示例:")
    print("  from pandadata_runtime import PandadataRuntime")
    print("  runtime = PandadataRuntime()")
    print("  data = runtime.get_stock_daily('600519')")


if __name__ == "__main__":
    main()
