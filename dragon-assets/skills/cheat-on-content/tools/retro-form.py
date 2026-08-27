#!/usr/bin/env python3
"""
retro-form - T+3d/T+7d复盘表单生成器
基于cheat-on-content预测追踪系统

Usage:
    python retro-form.py generate --prediction-id <ID> --type t3d
    python retro-form.py generate-pending --platform <platform>
    python retro-form.py fill --id <ID> --actual ER=<val> --actual SR=<val>
    python retro-form.py list --platform <platform>
    python retro-form.py pending --platform <platform>
    python retro-form.py show --id <ID>
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ============ 数据路径配置 ============
DATA_BASE = Path.home() / ".claude" / "skills" / "cheat-on-content"
PREDICTIONS_DIR = DATA_BASE / "predictions"
RETROS_DIR = DATA_BASE / "retrospectives"

# 复盘模板
T3D_TEMPLATE = """# T+3d 复盘表单

## 内容信息
- **预测ID**: {prediction_id}
- **平台**: {platform}
- **内容类型**: {content_type}
- **提交时间**: {submitted_at}
- **复盘时间**: {retro_at}
- **内容概要**: {content_summary}

---

## 实际数据填写

### 7维度评分 (0-10分)

| 维度 | 预测值 | 实际值 | 偏差 | 说明 |
|------|--------|--------|------|------|
| ER (曝光率) | {pred_er} | ___ | ___ | 曝光量相对值 |
| SR (互动率) | {pred_sr} | ___ | ___ | 点赞/评论/收藏/分享率 |
| HP (完播率) | {pred_hp} | ___ | ___ | 内容完成度 |
| QL (质量分) | {pred_ql} | ___ | ___ | 内容质量主观评分 |
| NA (数值锚) | {pred_na} | ___ | ___ | 数字吸引效果 |
| AB (行动率) | {pred_ab} | ___ | ___ | 关注/点击转化 |
| SAT (满意度) | {pred_sat} | ___ | ___ | 用户反馈满意度 |

### 综合评分
- **预测总分**: {pred_total}
- **实际总分**: ___
- **偏差**: ___

---

## 平台特有指标

{platform_extra_fields}

---

## 复盘分析

### 高偏差维度 (偏差>2分)
___

### 低偏差维度 (偏差<1分)
___

### 主要发现
___

### 改进建议
___

---

## Buffer状态
- [ ] T+3d 复盘完成
- [ ] T+7d 复盘待填写
"""

T7D_TEMPLATE = """# T+7d 复盘表单

## 内容信息
- **预测ID**: {prediction_id}
- **平台**: {platform}
- **内容类型**: {content_type}
- **提交时间**: {submitted_at}
- **T+3d复盘时间**: {t3d_at}
- **T+7d复盘时间**: {retro_at}

---

## T+3d 复盘摘要
- **T+3d实际总分**: {t3d_total}
- **偏差**: {t3d_deviation}

---

## T+7d 数据更新

### 7维度评分

| 维度 | T+3d | T+7d | 趋势 | 说明 |
|------|------|------|------|------|
| ER | {t3d_er} | ___ | ___ | |
| SR | {t3d_sr} | ___ | ___ | |
| HP | {t3d_hp} | ___ | ___ | |
| QL | {t3d_ql} | ___ | ___ | |
| NA | {t3d_na} | ___ | ___ | |
| AB | {t3d_ab} | ___ | ___ | |
| SAT | {t3d_sat} | ___ | ___ | |

### T+7d 综合评分
- **T+7d总分**: ___
- **相对T+3d变化**: ___

---

## 长期趋势分析

### 内容生命周期
___

### 与同类内容对比
___

### 最终评分预测
___

---

## Rubric健康检查
- [ ] T+7d 复盘完成
- [ ] 评分偏差已分析
- [ ] Rubric准确性验证
"""

# 平台特有字段映射
PLATFORM_EXTRA_FIELDS = {
    "douyin": """### 抖音特有指标
| 指标 | 值 | 说明 |
|------|---|---|
| play_count (播放量) | ___ | |
| dig_count (点赞数) | ___ | |
| comment_count (评论数) | ___ | |
| collect_count (收藏数) | ___ | |
| share_count (分享数) | ___ | |
| finish_rate (完播率) | ___ | |
| early_finish_rate (5秒完播率) | ___ | |""",

    "youtube": """### YouTube特有指标
| 指标 | 值 | 说明 |
|------|---|---|
| view_count (观看次数) | ___ | |
| like_count (点赞数) | ___ | |
| comment_count (评论数) | ___ | |
| average_view_duration (平均观看时长) | ___ | |
| watch_time_percentage (完播率) | ___ | |
| subscriber_count (订阅转化) | ___ | |""",

    "twitter": """### Twitter/X特有指标
| 指标 | 值 | 说明 |
|------|---|---|
| impressions (曝光量) | ___ | |
| like_count (点赞数) | ___ | |
| retweet_count (转发数) | ___ | |
| reply_count (回复数) | ___ | |
| bookmark_count (书签数) | ___ | |
| share_rate (转发率) | ___ | |""",

    "weibo": """### 微博特有指标
| 指标 | 值 | 说明 |
|------|---|---|
| impressions (曝光量) | ___ | |
| reposts_count (转发数) | ___ | |
| comments_count (评论数) | ___ | |
| attitudes_count (点赞数) | ___ | |
| read_count (阅读数) | ___ | |
| hot_search_probability (上热搜概率) | ___ | |""",

    "xiaohongshu": """### 小红书特有指标
| 指标 | 值 | 说明 |
|------|---|---|
| show_count (曝光量) | ___ | |
| liked_count (点赞数) | ___ | |
| collected_count (收藏数) | ___ | |
| comment_count (评论数) | ___ | |
| share_count (分享数) | ___ | |
| collection_rate (收藏率) | ___ | |
| engagement_rate (互动率) | ___ | |""",
}


def get_prediction(prediction_id: str) -> dict:
    """获取预测数据"""
    # 搜索所有预测文件
    for month_dir in PREDICTIONS_DIR.glob("*"):
        if not month_dir.is_dir():
            continue
        pred_file = month_dir / f"{prediction_id}.json"
        if pred_file.exists():
            with open(pred_file, encoding="utf-8") as f:
                return json.load(f)

        # 也搜索submitted文件
        for f in month_dir.glob("*-submitted.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if data.get("prediction_id") == prediction_id or data.get("id") == prediction_id:
                    return data
            except:
                continue

    return None


def generate_t3d_form(prediction_id: str) -> str:
    """生成T+3d复盘表单"""
    pred = get_prediction(prediction_id)

    if not pred:
        return f"❌ 未找到预测ID: {prediction_id}"

    scores = pred.get("scores", {})
    platform = pred.get("platform", "unknown")

    # 平台特有字段
    platform_extra = PLATFORM_EXTRA_FIELDS.get(platform, "")

    # 提交时间
    submitted_at = pred.get("submitted_at", datetime.now().isoformat())

    return T3D_TEMPLATE.format(
        prediction_id=prediction_id,
        platform=pred.get("platform_display", platform),
        content_type=pred.get("content_type", "unknown"),
        submitted_at=submitted_at,
        retro_at=datetime.now().isoformat(),
        content_summary=pred.get("content_summary", ""),
        pred_er=scores.get("ER", 0),
        pred_sr=scores.get("SR", 0),
        pred_hp=scores.get("HP", 0),
        pred_ql=scores.get("QL", 0),
        pred_na=scores.get("NA", 0),
        pred_ab=scores.get("AB", 0),
        pred_sat=scores.get("SAT", 0),
        pred_total=scores.get("total", 0),
        platform_extra_fields=platform_extra,
    )


def generate_t7d_form(prediction_id: str) -> str:
    """生成T+7d复盘表单"""
    pred = get_prediction(prediction_id)

    if not pred:
        return f"❌ 未找到预测ID: {prediction_id}"

    scores = pred.get("scores", {})
    t3d_scores = pred.get("t3d_scores", scores)
    platform = pred.get("platform", "unknown")

    # 提交时间
    submitted_at = pred.get("submitted_at", datetime.now().isoformat())
    t3d_at = pred.get("t3d_at", "")

    return T7D_TEMPLATE.format(
        prediction_id=prediction_id,
        platform=pred.get("platform_display", platform),
        content_type=pred.get("content_type", "unknown"),
        submitted_at=submitted_at,
        t3d_at=t3d_at,
        retro_at=datetime.now().isoformat(),
        t3d_total=t3d_scores.get("total", 0),
        t3d_deviation=round(t3d_scores.get("total", 0) - scores.get("total", 0), 1),
        t3d_er=t3d_scores.get("ER", 0),
        t3d_sr=t3d_scores.get("SR", 0),
        t3d_hp=t3d_scores.get("HP", 0),
        t3d_ql=t3d_scores.get("QL", 0),
        t3d_na=t3d_scores.get("NA", 0),
        t3d_ab=t3d_scores.get("AB", 0),
        t3d_sat=t3d_scores.get("SAT", 0),
    )


def generate_pending(platform: str = None) -> list:
    """获取待复盘列表"""
    pending = []

    today = datetime.now()
    t3d_threshold = today - timedelta(days=3)
    t7d_threshold = today - timedelta(days=7)

    for month_dir in PREDICTIONS_DIR.glob("*"):
        if not month_dir.is_dir():
            continue

        for f in month_dir.glob("*-submitted.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                submitted_at = datetime.fromisoformat(data.get("submitted_at", "2020-01-01"))

                # 平台过滤
                if platform and data.get("platform") != platform:
                    continue

                # 检查复盘状态
                has_t3d = "t3d_completed" in data and data["t3d_completed"]
                has_t7d = "t7d_completed" in data and data["t7d_completed"]

                pending_type = []
                if not has_t3d and submitted_at <= t3d_threshold:
                    pending_type.append("t3d")
                if has_t3d and not has_t7d and submitted_at <= t7d_threshold:
                    pending_type.append("t7d")

                if pending_type:
                    pending.append({
                        "prediction_id": data.get("prediction_id") or data.get("id"),
                        "platform": data.get("platform"),
                        "submitted_at": submitted_at.strftime("%Y-%m-%d"),
                        "pending": pending_type,
                    })
            except:
                continue

    return pending


def fill_actual(prediction_id: str, retro_type: str, actuals: dict) -> dict:
    """填写实际数据"""
    # 找到预测文件
    pred_file = None
    for month_dir in PREDICTIONS_DIR.glob("*"):
        if not month_dir.is_dir():
            continue
        for f in month_dir.glob("*-submitted.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                pid = data.get("prediction_id") or data.get("id")
                if pid == prediction_id:
                    pred_file = f
                    pred = data
                    break
            except:
                continue

    if not pred_file:
        return {"success": False, "error": f"未找到预测ID: {prediction_id}"}

    # 更新数据
    if retro_type == "t3d":
        pred["t3d_scores"] = actuals
        pred["t3d_at"] = datetime.now().isoformat()
        pred["t3d_completed"] = True
    elif retro_type == "t7d":
        pred["t7d_scores"] = actuals
        pred["t7d_at"] = datetime.now().isoformat()
        pred["t7d_completed"] = True

    # 保存
    with open(pred_file, "w", encoding="utf-8") as f:
        json.dump(pred, f, ensure_ascii=False, indent=2)

    return {"success": True, "prediction_id": prediction_id, "type": retro_type}


def list_retros(platform: str = None) -> list:
    """列出所有复盘"""
    retros = []

    for month_dir in RETROS_DIR.glob("*"):
        if not month_dir.is_dir():
            continue

        for f in month_dir.glob("*.md"):
            content = f.read_text(encoding="utf-8")

            # 提取预测ID
            pred_id = None
            for line in content.split("\n"):
                if "预测ID" in line:
                    pred_id = line.split("**")[-1].rstrip("**")
                    break

            retros.append({
                "file": str(f),
                "prediction_id": pred_id,
                "platform": platform,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d"),
            })

    return retros


# ============ CLI入口 ============
def main():
    parser = argparse.ArgumentParser(description="T+3d/T+7d 复盘表单生成器")
    sub = parser.add_subparsers(dest="command", help="子命令")

    # generate
    p_gen = sub.add_parser("generate", help="生成复盘表单")
    p_gen.add_argument("--prediction-id", required=True, help="预测ID")
    p_gen.add_argument("--type", choices=["t3d", "t7d"], default="t3d", help="复盘类型")

    # generate-pending
    p_genp = sub.add_parser("generate-pending", help="生成待复盘列表的表单")
    p_genp.add_argument("--platform", help="平台过滤")

    # fill
    p_fill = sub.add_parser("fill", help="填写实际数据")
    p_fill.add_argument("--id", required=True, help="预测ID")
    p_fill.add_argument("--type", choices=["t3d", "t7d"], default="t3d", help="复盘类型")
    p_fill.add_argument("--actual", action="append", help="实际值 ER=<val> SR=<val>")

    # list
    p_list = sub.add_parser("list", help="列出复盘")
    p_list.add_argument("--platform", help="平台过滤")

    # pending
    p_pending = sub.add_parser("pending", help="查看待复盘")
    p_pending.add_argument("--platform", help="平台过滤")

    # show
    p_show = sub.add_parser("show", help="查看复盘详情")
    p_show.add_argument("--id", required=True, help="预测ID")

    args = parser.parse_args()

    if args.command == "generate":
        if args.type == "t3d":
            print(generate_t3d_form(args.prediction_id))
        else:
            print(generate_t7d_form(args.prediction_id))

    elif args.command == "generate-pending":
        pending = generate_pending(args.platform)
        print(f"[retro-form] 待复盘数量: {len(pending)}")
        for p in pending:
            print(f"  - {p['prediction_id']} ({p['platform']}) @ {p['submitted_at']} [{', '.join(p['pending'])}]")

    elif args.command == "fill":
        actuals = {}
        if args.actual:
            for a in args.actual:
                if "=" in a:
                    key, val = a.split("=", 1)
                    actuals[key.upper()] = float(val)

        result = fill_actual(args.id, args.type, actuals)
        if result["success"]:
            print(f"✅ 已填写 {args.type} 实际数据: {args.id}")
        else:
            print(f"❌ 填写失败: {result['error']}")

    elif args.command == "list":
        retros = list_retros(args.platform)
        print(f"[retro-form] 复盘数量: {len(retros)}")
        for r in retros:
            print(f"  - {r['prediction_id']} ({r['platform']}) @ {r['modified']}")

    elif args.command == "pending":
        pending = generate_pending(args.platform)
        if pending:
            print(f"[retro-form] 待复盘列表:")
            for p in pending:
                print(f"  - {p['prediction_id']} ({p['platform']}) [{', '.join(p['pending'])}]")
        else:
            print("✅ 暂无待复盘内容")

    elif args.command == "show":
        # 先尝试T+7d表单
        content = generate_t7d_form(args.id)
        if "❌" in content:
            content = generate_t3d_form(args.id)
        print(content)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
