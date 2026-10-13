#!/usr/bin/env python3
"""
douyin-adapter - 抖音平台适配器
内容发布与数据采集适配层

Usage:
    python douyin-adapter.py fetch --content-id <ID> --metrics <metrics>
    python douyin-adapter.py batch --date-range <start,end> --platform 抖音
    python douyin-adapter.py export --content-id <ID> --format json --output <path>
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ============ 权重配置 ============
# 抖音: HP×2.0完播优先, ER×1.5, NA×1.5, SAT×0.5
WEIGHTS = {
    "ER": 1.5,
    "SR": 1.5,
    "HP": 2.0,   # 抖音权重提升
    "QL": 1.0,
    "NA": 1.5,
    "AB": 1.0,
    "SAT": 0.5,  # 抖音权重降低
}
WEIGHT_SUM = sum(WEIGHTS.values())  # 8.5
SCORE_DIVISOR = 8.5
SCORE_MULTIPLIER = 2.0

# 平台配置
PLATFORM_ID = "douyin"
DISPLAY_NAME = "抖音"

# 数据路径
DATA_BASE = Path.home() / ".claude" / "skills" / "cheat-on-content" / "platforms" / "douyin"
CONTENT_METRICS_FILE = DATA_BASE / "content-metrics.json"
TREND_ANALYSIS_FILE = DATA_BASE / "trend-analysis.json"
COMPETITOR_FILE = DATA_BASE / "competitor-benchmark.json"

# ============ 评分引擎 ============
def calculate_score(er: float, sr: float, hp: float, ql: float, na: float, ab: float, sat: float) -> float:
    """计算抖音内容综合评分"""
    weighted = (
        er * WEIGHTS["ER"] +
        sr * WEIGHTS["SR"] +
        hp * WEIGHTS["HP"] +
        ql * WEIGHTS["QL"] +
        na * WEIGHTS["NA"] +
        ab * WEIGHTS["AB"] +
        sat * WEIGHTS["SAT"]
    )
    return (weighted / SCORE_DIVISOR) * SCORE_MULTIPLIER


def score_from_metrics(metrics: dict) -> dict:
    """从原始指标计算评分"""
    # 抖音特有指标映射
    play_count = metrics.get("play_count", 0)
    dig_count = metrics.get("dig_count", 0)
    comment_count = metrics.get("comment_count", 0)
    collect_count = metrics.get("collect_count", 0)
    share_count = metrics.get("share_count", 0)
    finish_rate = metrics.get("finish_rate", 0.0)  # 完播率 P0
    follow_count = metrics.get("follow_count", 0)
    product_click = metrics.get("product_click", 0)

    # 计算7维度 (0-10分制)
    # ER: 曝光率 (播放量相对值)
    er = min(10.0, (play_count / 10000) * 2)

    # SR: 互动率 (点赞+评论+收藏+分享/播放)
    total_interactions = dig_count + comment_count + collect_count + share_count
    sr = min(10.0, (total_interactions / max(play_count, 1)) * 100)

    # HP: 完播率 (P0指标)
    hp = min(10.0, finish_rate * 10)

    # QL: 质量分 (视频质量评估)
    ql = min(10.0, (comment_count / max(play_count, 1)) * 200 + 5)

    # NA: 数值锚
    na = min(10.0, (play_count / 1000) * 0.1 + 5)

    # AB: 行动率 (关注转化+商品点击)
    ab = min(10.0, ((follow_count + product_click) / max(play_count, 1)) * 200 + 5)

    # SAT: 满意度
    sat = min(10.0, (collect_count + dig_count) / max(play_count, 1) * 100 + 5)

    total_score = calculate_score(er, sr, hp, ql, na, ab, sat)

    return {
        "ER": round(er, 2),
        "SR": round(sr, 2),
        "HP": round(hp, 2),
        "QL": round(ql, 2),
        "NA": round(na, 2),
        "AB": round(ab, 2),
        "SAT": round(sat, 2),
        "total": round(total_score, 2),
    }


# ============ 数据采集 ============
def fetch_content_metrics(content_id: str, metrics: list) -> dict:
    """采集内容数据"""
    # 模拟API调用 (实际需对接抖音开放平台API)
    print(f"[douyin-adapter] 采集内容 {content_id} 数据...")
    print(f"[douyin-adapter] 指标: {', '.join(metrics)}")

    # 实际应调用抖音开放API
    # https://open.douyin.com/platform/docs/api/content-management

    data = {
        "content_id": content_id,
        "platform": PLATFORM_ID,
        "fetched_at": datetime.now().isoformat(),
        "metrics": {
            "play_count": 0,
            "dig_count": 0,
            "comment_count": 0,
            "collect_count": 0,
            "share_count": 0,
            "finish_rate": 0.0,
            "follow_count": 0,
            "product_click": 0,
        }
    }

    return data


def fetch_real_data(content_id: str, api_key: str = None) -> dict:
    """获取实际数据"""
    import os
    if not api_key:
        api_key = os.environ.get("DOUYIN_API_KEY", "")

    if not api_key:
        print("[douyin-adapter] ⚠️ 未配置DOUYIN_API_KEY，使用模拟数据")
        return None

    # TODO: 实现抖音API调用
    return None


def batch_collect(start_date: str, end_date: str) -> dict:
    """批量采集日期范围数据"""
    print(f"[douyin-adapter] 批量采集 {start_date} ~ {end_date}")

    results = []
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    current = start
    while current <= end:
        # 模拟每日数据
        results.append({
            "date": current.strftime("%Y-%m-%d"),
            "platform": PLATFORM_ID,
            "count": 0,  # 实际从API获取
        })
        current += timedelta(days=1)

    return {"results": results, "total": len(results)}


# ============ 数据导出 ============
def export_to_prediction(content_id: str, format: str, output: str) -> None:
    """导出到预测追踪格式"""
    print(f"[douyin-adapter] 导出内容 {content_id} 到 {output}")

    metrics = fetch_content_metrics(content_id, [])
    scores = score_from_metrics(metrics["metrics"])

    export_data = {
        "content_id": content_id,
        "platform": PLATFORM_ID,
        "platform_display": DISPLAY_NAME,
        "exported_at": datetime.now().isoformat(),
        "scores": scores,
        "weights": WEIGHTS,
        "formula": f"(ER×{WEIGHTS['ER']} + SR×{WEIGHTS['SR']} + HP×{WEIGHTS['HP']} + QL×{WEIGHTS['QL']} + NA×{WEIGHTS['NA']} + AB×{WEIGHTS['AB']} + SAT×{WEIGHTS['SAT']}) / {SCORE_DIVISOR} × {SCORE_MULTIPLIER}",
    }

    DATA_BASE.mkdir(parents=True, exist_ok=True)
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if format == "json":
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
    else:
        print(f"[douyin-adapter] ⚠️ 不支持的格式: {format}")
        return

    print(f"[douyin-adapter] ✅ 导出成功: {output_path}")


# ============ CLI入口 ============
def main():
    parser = argparse.ArgumentParser(description="抖音平台适配器")
    sub = parser.add_subparsers(dest="command", help="子命令")

    # fetch
    p_fetch = sub.add_parser("fetch", help="采集内容数据")
    p_fetch.add_argument("--content-id", required=True, help="内容ID")
    p_fetch.add_argument("--metrics", help="指标列表，逗号分隔")

    # batch
    p_batch = sub.add_parser("batch", help="批量采集")
    p_batch.add_argument("--date-range", required=True, help="日期范围 YYYY-MM-DD,YYYY-MM-DD")
    p_batch.add_argument("--platform", default="抖音", help="平台名称")

    # export
    p_export = sub.add_parser("export", help="导出到预测追踪")
    p_export.add_argument("--content-id", required=True, help="内容ID")
    p_export.add_argument("--format", default="json", help="导出格式")
    p_export.add_argument("--output", required=True, help="输出路径")

    args = parser.parse_args()

    if args.command == "fetch":
        metrics = args.metrics.split(",") if args.metrics else []
        result = fetch_content_metrics(args.content_id, metrics)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "batch":
        start, end = args.date_range.split(",")
        result = batch_collect(start.strip(), end.strip())
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "export":
        export_to_prediction(args.content_id, args.format, args.output)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
