#!/usr/bin/env python3
"""
last30days_setup.py - API密钥配置向导

配置last30days技能所需的API密钥。
"""

import os
import sys
from pathlib import Path

# Windows encoding fix
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def print_banner():
    print("""
+===============================================================+
|              last30days API 密钥配置向导                       |
|                                                                |
|   配置10+平台30天时效性研究所需的API密钥                         |
+===============================================================+
""")


def check_env_file():
    """检查.env文件是否存在"""
    env_path = Path.home() / ".claude" / ".env"
    if env_path.exists():
        print(f"[OK] 找到配置文件: {env_path}")
        return env_path
    else:
        print(f"[!] 配置文件不存在: {env_path}")
        return env_path


def check_existing_keys():
    """检查现有API密钥"""
    keys = {
        "SCRAPECREATORS_API_KEY": os.environ.get("SCRAPECREATORS_API_KEY"),
        "XAI_API_KEY": os.environ.get("XAI_API_KEY"),
        "BRAVE_API_KEY": os.environ.get("BRAVE_API_KEY"),
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
    }

    print("\n[*] 现有API密钥状态:\n")
    for key, value in keys.items():
        if value:
            masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"  [OK] {key}: {masked}")
        else:
            print(f"  [  ] {key}: 未配置")

    return keys


def get_key_status():
    """返回密钥状态摘要"""
    required = ["SCRAPECREATORS_API_KEY"]
    optional = ["XAI_API_KEY", "BRAVE_API_KEY", "OPENAI_API_KEY"]

    status = {
        "required_ok": all(os.environ.get(k) for k in required),
        "optional_count": sum(1 for k in optional if os.environ.get(k)),
    }
    return status


def print_key_instructions():
    """打印获取API密钥的说明"""
    print("""
+===============================================================+
|                    如何获取API密钥                             |
+===============================================================+
|                                                               |
|  [1] SCRAPECREATORS_API_KEY (必需 - Reddit搜索)               |
|      1. 访问 https://scrapecreators.com                       |
|      2. 注册账户                                              |
|      3. 获取API密钥（100免费额度）                             |
|                                                               |
|  [2] XAI_API_KEY (可选 - X/Twitter搜索)                       |
|      1. 访问 https://console.x.ai                             |
|      2. 创建API密钥                                           |
|                                                               |
|  [3] BRAVE_API_KEY (可选 - 网页搜索)                          |
|      1. 访问 https://brave.com/search/api                     |
|      2. 申请API访问                                           |
|                                                               |
|  [4] OPENAI_API_KEY (可选 - 回退搜索)                         |
|      1. 访问 https://platform.openai.com                      |
|      2. 创建API密钥                                           |
|                                                               |
+===============================================================+
""")


def print_env_instructions():
    """打印环境变量配置说明"""
    print("""
+===============================================================+
|                    配置方法                                    |
+===============================================================+
|                                                               |
|  方法1: 环境变量（临时）                                       |
|  --------------------------------------------------------------|
|  export SCRAPECREATORS_API_KEY="your-key"                     |
|  export XAI_API_KEY="your-key"                                |
|  export BRAVE_API_KEY="your-key"                              |
|                                                               |
|  方法2: .env文件（永久）                                       |
|  --------------------------------------------------------------|
|  编辑 ~/.claude/.env 文件，添加：                              |
|                                                               |
|  SCRAPECREATORS_API_KEY=your-key                              |
|  XAI_API_KEY=your-key                                         |
|  BRAVE_API_KEY=your-key                                       |
|                                                               |
|  方法3: Windows系统环境变量                                    |
|  --------------------------------------------------------------|
|  setx SCRAPECREATORS_API_KEY "your-key"                       |
|  setx XAI_API_KEY "your-key"                                  |
|  setx BRAVE_API_KEY "your-key"                                |
|                                                               |
+===============================================================+
""")


def print_platform_status():
    """打印平台可用性状态"""
    print("""
+===============================================================+
|                    平台可用性状态                              |
+===============================================================+
|                                                               |
|  [OK] 免费平台（无需API密钥）                                  |
|  --------------------------------------------------------------|
|  * YouTube (yt-dlp本地)                                       |
|  * Hacker News (Algolia API)                                  |
|  * Polymarket (Gamma API)                                     |
|  * Bluesky (公开API)                                          |
|  * Web (DuckDuckGo)                                           |
|                                                               |
|  [!] 需要API密钥的平台                                         |
|  --------------------------------------------------------------|
|  * Reddit -> SCRAPECREATORS_API_KEY                           |
|  * X/Twitter -> XAI_API_KEY                                   |
|  * TikTok -> SCRAPECREATORS_API_KEY                           |
|  * Instagram -> SCRAPECREATORS_API_KEY                        |
|                                                               |
+===============================================================+
""")


def main():
    print_banner()

    # 检查现有密钥
    keys = check_existing_keys()
    env_path = check_env_file()

    # 检查状态
    status = get_key_status()

    print(f"\n[*] 配置状态摘要:")
    print(f"    * 必需密钥: {'[OK] 已配置' if status['required_ok'] else '[X] 未配置'}")
    print(f"    * 可选密钥: {status['optional_count']}/3 已配置")

    # 显示平台状态
    print_platform_status()

    # 显示密钥获取说明
    print_key_instructions()

    # 显示配置方法
    print_env_instructions()

    # 最终建议
    print("\n[*] 建议:")
    if not status["required_ok"]:
        print("   1. 首先配置 SCRAPECREATORS_API_KEY 以启用Reddit搜索")
    if status["optional_count"] < 3:
        print("   2. 配置可选密钥以增强搜索能力")
    print("   3. 即使不配置密钥，仍可使用免费平台（YouTube、Hacker News等）")

    return 0


if __name__ == "__main__":
    sys.exit(main())