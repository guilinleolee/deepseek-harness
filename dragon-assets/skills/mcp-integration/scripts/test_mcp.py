#!/usr/bin/env python3
"""
MCP集成快速测试脚本
测试所有MCP服务的可用性
"""

import sys
import os

# 设置UTF-8编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加scripts目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_client import MCPClientPool, MCPServerType, MCPRequest
import asyncio


async def test_geocoder():
    """测试地理编码服务"""
    pool = MCPClientPool()
    try:
        request = MCPRequest(
            server_type=MCPServerType.GEOCODER,
            operation="geocode",
            params={"address": "北京市朝阳区"}
        )
        response = await pool.call(request)
        return response.success and response.data.get("success")
    finally:
        pool.close_all()


async def test_ip_lookup():
    """测试IP定位服务"""
    pool = MCPClientPool()
    try:
        request = MCPRequest(
            server_type=MCPServerType.IP_LOOKUP,
            operation="lookup",
            params={"ip": "1.1.1.1"}
        )
        response = await pool.call(request)
        return response.success and response.data.get("success")
    finally:
        pool.close_all()


async def test_schema_generator():
    """测试Schema生成服务"""
    pool = MCPClientPool()
    try:
        request = MCPRequest(
            server_type=MCPServerType.SCHEMA_GENERATOR,
            operation="generate",
            params={"schema_type": "Article"}
        )
        response = await pool.call(request)
        return response.success and response.data.get("success")
    finally:
        pool.close_all()


async def test_llms_generator():
    """测试llms.txt生成服务"""
    pool = MCPClientPool()
    try:
        request = MCPRequest(
            server_type=MCPServerType.LLMS_GENERATOR,
            operation="generate",
            params={"site_url": "https://example.com"}
        )
        response = await pool.call(request)
        return response.success and response.data.get("success")
    finally:
        pool.close_all()


async def test_geo_analyzer():
    """测试GEO分析服务"""
    pool = MCPClientPool()
    try:
        request = MCPRequest(
            server_type=MCPServerType.GEO_ANALYZER,
            operation="analyze",
            params={"url": "https://example.com"}
        )
        response = await pool.call(request)
        return response.success and response.data.get("success")
    finally:
        pool.close_all()


async def test_connection_pool():
    """测试连接池"""
    pool = MCPClientPool()
    try:
        stats = pool.get_stats()
        return "total_calls" in stats
    finally:
        pool.close_all()


async def main():
    """运行所有测试"""
    tests = [
        ("连接池", test_connection_pool),
        ("地理编码", test_geocoder),
        ("IP定位", test_ip_lookup),
        ("Schema生成", test_schema_generator),
        ("llms.txt生成", test_llms_generator),
        ("GEO分析", test_geo_analyzer),
    ]

    print("=" * 50)
    print("MCP集成测试")
    print("=" * 50)

    results = []
    for name, test_func in tests:
        try:
            result = await test_func()
            status = "OK" if result else "FAIL"
            results.append((name, status))
            print(f"  [{status}] {name}")
        except Exception as e:
            results.append((name, f"ERROR: {e}"))
            print(f"  [ERROR] {name}: {e}")

    print("=" * 50)
    passed = sum(1 for _, r in results if r == "OK")
    print(f"结果: {passed}/{len(results)} 通过")
    print("=" * 50)

    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
