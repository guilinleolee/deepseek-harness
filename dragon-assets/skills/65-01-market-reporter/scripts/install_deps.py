#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""65-01 市场复盘分析师 - 依赖安装脚本"""

import subprocess
import sys
import os


def check_and_install():
    """检查并安装所需依赖"""

    print("=" * 60)
    print("[65-01] Market Reporter - Dependency Check")
    print("=" * 60)

    # 必需依赖
    required = {
        "httpx": "HTTP client (API calls)",
        "pandas": "Data processing",
        "requests": "HTTP requests",
    }

    # 可选依赖（已有则跳过）
    optional = {
        "PyYAML": "YAML config parsing",
    }

    print("\n[*] Checking required dependencies...")
    all_ok = True

    for pkg, desc in required.items():
        try:
            __import__(pkg)
            print(f"  [OK] {pkg:12} - {desc}")
        except ImportError:
            print(f"  [X] {pkg:12} - Missing, installing...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", pkg],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"     [OK] Installed successfully")
            else:
                print(f"     [X] Failed: {result.stderr}")
                all_ok = False

    print("\n[*] Checking optional dependencies...")
    for pkg, desc in optional.items():
        try:
            __import__(pkg)
            print(f"  [OK] {pkg:12} - {desc}")
        except ImportError:
            print(f"  [!] {pkg:12} - Optional ({desc})")

    print("\n" + "=" * 60)
    if all_ok:
        print("[OK] All required dependencies are ready!")
        print("\n[*] Usage:")
        print("  1. Direct call: [@市场复盘] generate daily review")
        print("  2. Or use a-stock-data-bridge:")
        print("     python skills/a-stock-data-bridge/em_base.py --help")
    else:
        print("[X] Some dependencies failed to install")
    print("=" * 60)

    return all_ok


def test_connection():
    """测试数据连接"""
    print("\n[*] Testing data source connection...")

    try:
        import httpx
        import asyncio

        async def test():
            client = httpx.AsyncClient(timeout=10)
            try:
                # Test Eastmoney data source
                response = await client.get(
                    "https://push2.eastmoney.com/api/qt/clist/get",
                    params={
                        "pn": 1,
                        "pz": 5,
                        "po": 1,
                        "np": 1,
                        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                        "fltt": 2,
                        "invt": 2,
                        "fid": "f3",
                        "fs": "m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23",
                        "fields": "f1,f2,f3,f12,f14",
                    }
                )
                if response.status_code == 200:
                    print("  [OK] Eastmoney data source - Available")
                    return True
            except Exception as e:
                print(f"  [!] Eastmoney data source - {e}")

            await client.aclose()
            return True

        result = asyncio.run(test())
        print("\n[OK] Connection test completed")
        return result

    except Exception as e:
        print(f"\n[X] Connection test failed: {e}")
        return False


if __name__ == "__main__":
    ok = check_and_install()
    if ok:
        test_connection()
    sys.exit(0 if ok else 1)
