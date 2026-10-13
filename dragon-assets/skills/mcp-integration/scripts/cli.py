#!/usr/bin/env python3
"""
MCP Integration CLI - 命令行入口
用法: python cli.py <command> [options]
"""

import sys
import os
import io

# 设置UTF-8输出编码（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加scripts目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_client import main, MCPClientPool, MCPServerType, MCPRequest
import asyncio
import argparse
import json


async def cmd_geocode(args):
    """地理编码命令"""
    pool = MCPClientPool()
    try:
        request = MCPRequest(
            server_type=MCPServerType.GEOCODER,
            operation="geocode",
            params={"address": args.address}
        )
        response = await pool.call(request)
        return response.data
    finally:
        pool.close_all()


async def cmd_reverse(args):
    """逆向编码命令"""
    pool = MCPClientPool()
    try:
        coords = args.coordinates.split(",")
        request = MCPRequest(
            server_type=MCPServerType.GEOCODER,
            operation="reverse",
            params={"lat": float(coords[0]), "lng": float(coords[1])}
        )
        response = await pool.call(request)
        return response.data
    finally:
        pool.close_all()


async def cmd_ip_lookup(args):
    """IP定位命令"""
    pool = MCPClientPool()
    try:
        request = MCPRequest(
            server_type=MCPServerType.IP_LOOKUP,
            operation="lookup",
            params={"ip": args.ip}
        )
        response = await pool.call(request)
        return response.data
    finally:
        pool.close_all()


async def cmd_llms_generate(args):
    """llms.txt生成命令"""
    pool = MCPClientPool()
    try:
        request = MCPRequest(
            server_type=MCPServerType.LLMS_GENERATOR,
            operation="generate",
            params={"site_url": args.site}
        )
        response = await pool.call(request)
        return response.data
    finally:
        pool.close_all()


async def cmd_schema_generate(args):
    """Schema生成命令"""
    pool = MCPClientPool()
    try:
        # 解析额外参数
        params = {"schema_type": args.type}
        if args.title:
            params["headline"] = args.title
        if args.author:
            params["author"] = {"@type": "Person", "name": args.author}
        if args.url:
            params["url"] = args.url
        if args.description:
            params["description"] = args.description

        request = MCPRequest(
            server_type=MCPServerType.SCHEMA_GENERATOR,
            operation="generate",
            params=params
        )
        response = await pool.call(request)
        return response.data
    finally:
        pool.close_all()


async def cmd_geo_analyze(args):
    """GEO分析命令"""
    pool = MCPClientPool()
    try:
        request = MCPRequest(
            server_type=MCPServerType.GEO_ANALYZER,
            operation="analyze",
            params={"url": args.url}
        )
        response = await pool.call(request)
        return response.data
    finally:
        pool.close_all()


async def cmd_brand_track(args):
    """品牌追踪命令"""
    pool = MCPClientPool()
    try:
        request = MCPRequest(
            server_type=MCPServerType.BRAND_TRACKER,
            operation="track",
            params={"brand": args.brand, "period": args.period}
        )
        response = await pool.call(request)
        return response.data
    finally:
        pool.close_all()


async def cmd_citation_check(args):
    """引用检查命令"""
    pool = MCPClientPool()
    try:
        request = MCPRequest(
            server_type=MCPServerType.CITATION_CHECKER,
            operation="check",
            params={"url": args.url}
        )
        response = await pool.call(request)
        return response.data
    finally:
        pool.close_all()


async def cmd_status(args):
    """状态查询命令"""
    pool = MCPClientPool()
    try:
        return pool.get_stats()
    finally:
        pool.close_all()


async def cmd_list(args):
    """列出可用MCP服务"""
    import json
    registry_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "..", "mcp", "mcp-registry.json"
    )
    if os.path.exists(registry_path):
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        return registry
    return {"error": "Registry not found"}


def main_cli():
    """CLI主入口"""
    parser = argparse.ArgumentParser(
        description="MCP Integration Center CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
可用命令:
  geocode <address>          地址转坐标
  reverse <lat,lng>          坐标转地址
  ip-lookup <ip>             IP定位
  llms-generate <site>       生成llms.txt
  schema-generate <type>     生成JSON-LD Schema
  geo-analyze <url>          GEO分析
  brand-track <brand>         品牌追踪
  citation-check <url>        引用检查
  status                     MCP状态
  list                       列出可用MCP

示例:
  python cli.py geocode "北京市朝阳区"
  python cli.py reverse 39.908,-116.397
  python cli.py ip-lookup 8.8.8.8
  python cli.py llms-generate https://example.com
  python cli.py schema-generate Article --title "My Article" --url "https://example.com/article"
  python cli.py geo-analyze https://example.com
  python cli.py brand-track "MyBrand" --period 30d
  python cli.py status
  python cli.py list
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="MCP命令")

    # geocode
    p_geocode = subparsers.add_parser("geocode", help="地址转坐标")
    p_geocode.add_argument("address", help="地址")
    p_geocode.set_defaults(func=cmd_geocode)

    # reverse
    p_reverse = subparsers.add_parser("reverse", help="坐标转地址")
    p_reverse.add_argument("coordinates", help="坐标(lat,lng)")
    p_reverse.set_defaults(func=cmd_reverse)

    # ip-lookup
    p_ip = subparsers.add_parser("ip-lookup", help="IP定位")
    p_ip.add_argument("ip", help="IP地址")
    p_ip.set_defaults(func=cmd_ip_lookup)

    # llms-generate
    p_llms = subparsers.add_parser("llms-generate", help="生成llms.txt")
    p_llms.add_argument("site", help="网站URL")
    p_llms.set_defaults(func=cmd_llms_generate)

    # schema-generate
    p_schema = subparsers.add_parser("schema-generate", help="生成Schema")
    p_schema.add_argument("type", choices=["Article", "FAQPage", "Organization", "Person", "Product"], help="Schema类型")
    p_schema.add_argument("--title", help="标题")
    p_schema.add_argument("--author", help="作者")
    p_schema.add_argument("--url", help="URL")
    p_schema.add_argument("--description", help="描述")
    p_schema.set_defaults(func=cmd_schema_generate)

    # geo-analyze
    p_geo = subparsers.add_parser("geo-analyze", help="GEO分析")
    p_geo.add_argument("url", help="网站URL")
    p_geo.set_defaults(func=cmd_geo_analyze)

    # brand-track
    p_brand = subparsers.add_parser("brand-track", help="品牌追踪")
    p_brand.add_argument("brand", help="品牌名")
    p_brand.add_argument("--period", default="30d", help="时间周期")
    p_brand.set_defaults(func=cmd_brand_track)

    # citation-check
    p_cite = subparsers.add_parser("citation-check", help="引用检查")
    p_cite.add_argument("url", help="页面URL")
    p_cite.set_defaults(func=cmd_citation_check)

    # status
    p_status = subparsers.add_parser("status", help="MCP状态")
    p_status.set_defaults(func=cmd_status)

    # list
    p_list = subparsers.add_parser("list", help="列出MCP服务")
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # 执行命令
    try:
        result = asyncio.run(args.func(args))

        if args.command == "list":
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif args.command == "status":
            print("📊 MCP连接池状态:")
            print(f"   总调用: {result.get('total_calls', 0)}")
            print(f"   成功: {result.get('successful_calls', 0)}")
            print(f"   失败: {result.get('failed_calls', 0)}")
            print(f"   活跃连接: {result.get('active_connections', 0)}")
        elif result and result.get("success") is not False:
            if args.command == "geocode":
                print(f"📍 {result.get('address', 'Unknown')}")
                print(f"   坐标: {result.get('lat')}, {result.get('lng')}")
                if result.get('city'):
                    print(f"   城市: {result.get('city')}, {result.get('country')}")
            elif args.command == "reverse":
                print(f"📍 {result.get('address', 'Unknown')}")
                print(f"   坐标: {result.get('lat')}, {result.get('lng')}")
            elif args.command == "ip-lookup":
                print(f"🌐 IP: {result.get('ip')}")
                if result.get('city'):
                    print(f"   位置: {result.get('city')}, {result.get('region')}, {result.get('country')}")
                if result.get('org'):
                    print(f"   组织: {result.get('org')}")
            elif args.command == "llms-generate":
                print(f"✅ llms.txt generated for {result.get('domain')}")
                print(f"\n预览:\n{result.get('preview', '')}")
            elif args.command == "schema-generate":
                print(f"✅ {result.get('schema_type')} Schema generated")
                print(f"\n{result.get('json_string', '')}")
            elif args.command == "geo-analyze":
                score = result.get('geo_score', 0)
                print(f"🌐 GEO分析: {result.get('domain')}")
                print(f"   GEO分数: {score}/100")
                print(f"   llms.txt状态: {result.get('llms_txt_status', 'unknown')}")
                if result.get('recommendations'):
                    print(f"\n建议:")
                    for rec in result.get('recommendations', [])[:3]:
                        print(f"   • {rec}")
            else:
                print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return 1

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main_cli())
