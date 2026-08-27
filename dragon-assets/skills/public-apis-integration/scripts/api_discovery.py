#!/usr/bin/env python3
"""
public-apis-integration: 免费公共API发现与集成引擎
基于 public-apis/public-apis (65k+ Stars, MIT License)

L0: 免费公共API发现与集成引擎，50+分类1,000+API索引
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# 数据文件路径
SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
CATEGORIES_FILE = DATA_DIR / "categories.json"


def load_categories() -> dict:
    """加载分类数据"""
    if not CATEGORIES_FILE.exists():
        print(f"警告: 分类数据文件不存在: {CATEGORIES_FILE}")
        return {"categories": {}, "apis": []}

    with open(CATEGORIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def search_by_category(
    data: dict,
    category: str,
    cors: Optional[str] = None,
    auth: Optional[str] = None,
    https: bool = True,
    limit: int = 20
) -> list:
    """按分类搜索API"""
    results = []

    for api in data.get("apis", []):
        # 分类匹配
        api_cats = [c.lower() for c in api.get("categories", [])]
        if category.lower() not in api_cats:
            continue

        # CORS过滤
        if cors:
            api_cors = api.get("cors", "").lower()
            if cors.lower() == "yes" and api_cors not in ["yes", "any"]:
                continue
            if cors.lower() == "no" and api_cors != "no":
                continue

        # 认证过滤
        if auth:
            api_auth = api.get("auth", "").lower()
            if auth.lower() not in api_auth:
                continue

        # HTTPS过滤
        if https:
            if not api.get("https", True):
                continue

        results.append(api)

        if limit and len(results) >= limit:
            break

    return results


def search_by_name(data: dict, name: str) -> list:
    """按名称精确查询"""
    name_lower = name.lower()
    results = []

    for api in data.get("apis", []):
        api_name = api.get("API", "").lower()
        if name_lower in api_name:
            results.append(api)

    return results


def search_by_auth(data: dict, auth_type: str, limit: int = 20) -> list:
    """按认证方式筛选"""
    auth_lower = auth_type.lower()
    results = []

    for api in data.get("apis", []):
        api_auth = api.get("auth", "").lower()
        if auth_lower in api_auth:
            results.append(api)

        if limit and len(results) >= limit:
            break

    return results


def check_api_health(api: dict) -> dict:
    """检查API健康状态"""
    import urllib.request
    import urllib.error

    result = {
        "API": api.get("API"),
        "URL": api.get("URL"),
        "https": api.get("https", True),
        "status": "unknown"
    }

    # 如果没有URL，无法检查
    url = api.get("URL")
    if not url:
        result["status"] = "no_url"
        return result

    # 检查HTTPS
    if not api.get("https", True):
        result["status"] = "http_only"
        return result

    try:
        req = urllib.request.Request(
            url,
            method="HEAD",
            headers={"User-Agent": "Tianlong-Engine/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            result["status"] = "healthy"
            result["status_code"] = response.status
    except urllib.error.HTTPError as e:
        result["status"] = "http_error"
        result["status_code"] = e.code
    except urllib.error.URLError:
        result["status"] = "unreachable"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


def print_api(api: dict, verbose: bool = False):
    """打印API信息"""
    print(f"\n{'='*60}")
    print(f"📌 {api.get('API', 'Unknown')}")
    print(f"{'='*60}")

    if verbose:
        print(f"🔗 URL: {api.get('URL', 'N/A')}")
        print(f"📝 描述: {api.get('Description', 'N/A')}")
        print(f"🔐 认证: {api.get('Auth', 'N/A') or '无需认证'}")
        print(f"🌐 HTTPS: {'✅ 支持' if api.get('HTTPS') else '❌ 不支持'}")
        print(f"🔄 CORS: {api.get('Cors', 'N/A')}")
        print(f"📂 分类: {', '.join(api.get('Categories', []))}")
    else:
        print(f"   {api.get('Description', 'N/A')[:70]}...")


def main():
    parser = argparse.ArgumentParser(
        description="public-apis-integration: 免费公共API发现与集成引擎"
    )
    parser.add_argument("--category", "-c", help="按分类搜索API")
    parser.add_argument("--auth", "-a", help="按认证方式筛选 (apiKey/OAuth/JWT/Bearer)")
    parser.add_argument("--cors", help="CORS过滤 (yes/no/unknown)")
    parser.add_argument("--name", "-n", help="API名称精确查询")
    parser.add_argument("--check-all", action="store_true", help="检查所有API健康状态")
    parser.add_argument("--check", help="检查指定API健康状态")
    parser.add_argument("--https", action="store_true", default=True, help="仅返回HTTPS API (默认开启)")
    parser.add_argument("--all-https", dest="https", action="store_false", help="返回所有API (包括HTTP)")
    parser.add_argument("--limit", "-l", type=int, default=20, help="返回结果数量限制")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细信息输出")

    args = parser.parse_args()

    # 加载数据
    data = load_categories()

    # 按名称查询
    if args.name:
        results = search_by_name(data, args.name)
        print(f"\n🔍 搜索 '{args.name}' 的结果: {len(results)} 个API\n")
        for api in results:
            print_api(api, verbose=True)
        return

    # 按分类搜索
    if args.category:
        results = search_by_category(
            data,
            args.category,
            cors=args.cors,
            auth=args.auth,
            https=args.https,
            limit=args.limit
        )
        print(f"\n🔍 分类 '{args.category}' 的结果: {len(results)} 个API\n")
        for api in results:
            print_api(api, verbose=args.verbose)
        return

    # 按认证筛选
    if args.auth:
        results = search_by_auth(data, args.auth, limit=args.limit)
        print(f"\n🔍 认证方式 '{args.auth}' 的结果: {len(results)} 个API\n")
        for api in results:
            print_api(api, verbose=args.verbose)
        return

    # 检查健康状态
    if args.check:
        results = search_by_name(data, args.check)
        if not results:
            print(f"未找到名为 '{args.check}' 的API")
            return

        print(f"\n🏥 检查 '{args.check}' 健康状态...\n")
        for api in results[:5]:  # 最多检查5个
            health = check_api_health(api)
            status_emoji = {
                "healthy": "✅",
                "http_error": "⚠️",
                "unreachable": "❌",
                "error": "❌",
                "http_only": "⚠️",
                "no_url": "⚠️"
            }.get(health["status"], "❓")
            print(f"{status_emoji} {health['API']}: {health['status']}")
            if "status_code" in health:
                print(f"   HTTP状态码: {health['status_code']}")
        return

    if args.check_all:
        print("\n🏥 检查所有API健康状态 (仅检查前20个)...\n")
        for i, api in enumerate(data.get("apis", [])[:20]):
            health = check_api_health(api)
            status_emoji = {
                "healthy": "✅",
                "http_error": "⚠️",
                "unreachable": "❌",
                "error": "❌"
            }.get(health["status"], "❓")
            print(f"{status_emoji} {health['API']}: {health['status']}")
        return

    # 无参数时显示帮助
    parser.print_help()
    print("\n\n📚 示例用法:")
    print("  python api_discovery.py --category 'Finance' --cors 'yes'")
    print("  python api_discovery.py --auth 'OAuth' --limit 20")
    print("  python api_discovery.py --name 'Alpha Vantage'")
    print("  python api_discovery.py --check 'Alpha Vantage'")


if __name__ == "__main__":
    main()
