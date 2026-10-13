#!/usr/bin/env python3
"""
安装脚本 - 安装依赖并配置CLI命令
"""

import subprocess
import sys
from pathlib import Path

def main():
    print("📚 安装 ebook-search 技能...")
    print()

    skill_dir = Path(__file__).parent
    requirements_file = skill_dir / "requirements.txt"

    # 安装依赖
    print("📦 安装依赖...")
    if requirements_file.exists():
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ 依赖安装成功")
        else:
            print(f"⚠️ 部分依赖安装失败: {result.stderr}")
    else:
        print("⚠️ 未找到 requirements.txt")

    # 安装 Playwright 浏览器（用于 Z-Library）
    print()
    print("🌐 安装 Playwright 浏览器...")
    result = subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("✅ Playwright 浏览器安装成功")
    else:
        print(f"⚠️ Playwright 安装失败（可能已安装）: {result.stderr[:200]}")

    # 创建 CLI 命令
    print()
    print("🔗 配置 CLI 命令...")

    cli_script = skill_dir / "scripts" / "cli.py"

    # Windows: 创建批处理文件
    if sys.platform == "win32":
        bat_file = skill_dir / "ebook-search.bat"
        bat_content = f'''@echo off
python "{cli_script}" %*
'''
        with open(bat_file, 'w') as f:
            f.write(bat_content)
        print(f"✅ 已创建: {bat_file}")
        print(f"   将 {skill_dir} 添加到 PATH 即可使用 'ebook-search' 命令")

    # Unix: 创建符号链接建议
    else:
        print(f"💡 将以下内容添加到 ~/.bashrc 或 ~/.zshrc:")
        print(f'   alias ebook-search="python3 {cli_script}"')

    print()
    print("✨ 安装完成！")
    print()
    print("📖 使用示例:")
    print('   ebook-search "Python编程"')
    print('   ebook-search "机器学习" -f pdf')
    print('   ebook-search "Stephen King" -t author')
    print()
    print("⚠️ 首次使用 Z-Library 需要登录:")
    print("   cd ~/.claude/skills/zlibrary-to-notebooklm")
    print("   python scripts/login.py")
    print()

if __name__ == "__main__":
    main()