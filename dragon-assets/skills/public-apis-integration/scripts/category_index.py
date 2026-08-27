#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
category_index.py - API分类索引构建工具
用于构建和维护API分类索引
"""

import json
import sys
import io
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

# Windows UTF-8 support
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def build_category_index(apis: List[dict]) -> Dict:
    """构建分类索引"""
    index = defaultdict(lambda: {
        "count": 0,
        "auth_distribution": defaultdict(int),
        "cors_distribution": defaultdict(int),
        "https_count": 0,
        "apis": []
    })

    for api in apis:
        categories = api.get("Categories", [])
        auth = api.get("Auth", "")
        cors = api.get("Cors", "")
        https = api.get("HTTPS", True)

        for cat in categories:
            index[cat]["count"] += 1
            index[cat]["auth_distribution"][auth or "none"] += 1
            index[cat]["cors_distribution"][cors or "unknown"] += 1
            if https:
                index[cat]["https_count"] += 1

            index[cat]["apis"].append({
                "name": api.get("API"),
                "auth": auth,
                "cors": cors,
                "https": https
            })

    # 转换为普通字典
    return dict(index)


def generate_stats(apis: List[dict]) -> dict:
    """生成API统计信息"""
    stats = {
        "total_apis": len(apis),
        "by_auth": defaultdict(int),
        "by_cors": defaultdict(int),
        "https_count": 0,
        "category_count": 0
    }

    categories = set()
    for api in apis:
        auth = api.get("Auth", "") or "none"
        cors = api.get("Cors", "") or "unknown"
        https = api.get("HTTPS", True)

        stats["by_auth"][auth] += 1
        stats["by_cors"][cors] += 1
        if https:
            stats["https_count"] += 1

        categories.update(api.get("Categories", []))

    stats["category_count"] = len(categories)
    return dict(stats)


def print_category_report(index: Dict):
    """打印分类报告"""
    print("\n" + "="*60)
    print("📂 API 分类索引报告")
    print("="*60)

    # 按数量排序
    sorted_cats = sorted(
        index.items(),
        key=lambda x: x[1]["count"],
        reverse=True
    )

    total_apis = sum(cat["count"] for _, cat in sorted_cats)

    print(f"\n总计: {total_apis} 个API, {len(index)} 个分类\n")

    print(f"{'分类':<30} {'数量':>6} {'HTTPS':>6} {'免费':>6}")
    print("-" * 60)

    for cat_name, cat_data in sorted_cats:
        free_count = cat_data["count"] - cat_data["auth_distribution"]["apiKey"]
        print(f"{cat_name:<30} {cat_data['count']:>6} {cat_data['https_count']:>6} {free_count:>6}")

    print("\n" + "="*60)
    print("认证方式分布 (Top 5)")
    print("="*60)

    all_auth = defaultdict(int)
    for cat_name, cat_data in index.items():
        for auth, count in cat_data["auth_distribution"].items():
            all_auth[auth] += count

    for auth, count in sorted(all_auth.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {auth or 'none':<20} {count:>6}")

    print("\n" + "="*60)
    print("CORS 状态分布")
    print("="*60)

    all_cors = defaultdict(int)
    for cat_name, cat_data in index.items():
        for cors, count in cat_data["cors_distribution"].items():
            all_cors[cors] += count

    for cors, count in sorted(all_cors.items(), key=lambda x: x[1], reverse=True):
        pct = count / total_apis * 100
        bar = "█" * int(pct / 2)
        print(f"  {cors:<10} {count:>6} ({pct:5.1f}%) {bar}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="API分类索引构建工具")
    parser.add_argument("--input", "-i", help="输入JSON文件路径")
    parser.add_argument("--output", "-o", help="输出索引文件路径")
    parser.add_argument("--stats", "-s", action="store_true", help="显示统计信息")
    parser.add_argument("--report", "-r", action="store_true", help="显示分类报告")

    args = parser.parse_args()

    # 加载数据
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        # 使用默认路径
        data_file = Path(__file__).parent.parent / "data" / "categories.json"
        if data_file.exists():
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            print("错误: 未找到数据文件")
            return

    apis = data.get("apis", [])

    # 生成统计
    if args.stats:
        stats = generate_stats(apis)
        print("\n📊 API 统计信息")
        print("="*40)
        print(f"  总API数量: {stats['total_apis']}")
        print(f"  分类数量: {stats['category_count']}")
        print(f"  HTTPS支持: {stats['https_count']}")
        print(f"  占比: {stats['https_count']/stats['total_apis']*100:.1f}%")

    # 生成索引
    index = build_category_index(apis)

    # 输出索引
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 索引已保存到: {args.output}")

    # 显示报告
    if args.report:
        print_category_report(index)

    # 默认行为
    if not args.stats and not args.report and not args.output:
        parser.print_help()


if __name__ == "__main__":
    main()
