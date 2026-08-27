# -*- coding: utf-8 -*-
"""
Step4Analyzer — 分析管道
来源: blogger-distill-orchestration SKILL.md (lines 147-170)

分析管道：BloggerAnalyzer.analyze_data_materials() + _compute_note_stats()
输出: {blogger_name}_analysis.json + {blogger_name}_stats.json
"""

import json
import os
from typing import Any, Optional

from .step3_repairer import _is_empty_value


# ── 11维度分析常量 ────────────────────────────────────────────────────────────

# 标题策略评分权重
TITLE_KEYWORD_WEIGHTS = {
    "测评": 1.0,
    "种草": 1.0,
    "教程": 0.9,
    "攻略": 0.9,
    "分享": 0.8,
    "推荐": 0.8,
    "合集": 0.7,
    "干货": 0.7,
    "避坑": 0.8,
    "平替": 0.8,
    "对比": 0.7,
    "开箱": 0.9,
    "好物": 0.8,
    "回购": 0.8,
}

# 内容框架关键词
CONTENT_FRAMEWORK_KEYWORDS = {
    "问题解决": ["为什么", "怎么选", "如何", "是什么", "解决", "搞定"],
    "经验分享": ["我的", "用了", "坚持", "终于", "终于找到", "亲测"],
    "产品测评": ["测评", "对比", "使用感", "效果", "成分", "体验"],
    "知识干货": ["干货", "攻略", "技巧", "方法", "总结", "指南"],
}

# 视觉风格关键词
VISUAL_STYLE_KEYWORDS = {
    "真实生活": ["日常", "随手拍", "真实", "滤镜", "生活"],
    "精致文艺": ["氛围感", "ins风", "高级感", "简约", "干净"],
    "专业测评": ["对比图", "数据", "测评", "实验室", "检测"],
    "种草分享": ["好物", "推荐", "必买", "种草", "回购"],
}

# 互动策略关键词
INTERACT_STYLE_KEYWORDS = {
    "求助互动": ["求助", "你们觉得", "有人知道吗", "选哪个", "求推荐"],
    "分享推荐": ["推荐", "我觉得", "个人", "喜欢", "分享"],
    "知识科普": ["科普", "告诉你", "其实", "很多人不知道", "知识"],
    "真实分享": ["个人", "我的", "真实", "测评", "使用感"],
}

# 商业化潜力关键词
COMMERCIAL_KEYWORDS = {
    "高": ["推荐", "种草", "好物", "必买", "回购", "已买", "入坑"],
    "中": ["分享", "测评", "对比", "我的", "使用感"],
    "低": ["记录", "日常", "随手拍", "心情", "碎碎念"],
}

# 时间活跃度权重（按发布月份）
MONTH_WEIGHTS = {
    1: 0.8,   # 新年/元旦
    2: 0.7,   # 春节
    3: 0.9,   # 春季
    4: 0.95,  # 踏青季
    5: 1.0,   # 五一/母亲节
    6: 0.95,  # 夏季开始
    7: 0.9,   # 暑期
    8: 0.9,   # 暑期
    9: 0.95,  # 开学季
    10: 1.0,  # 国庆/双十一预热
    11: 1.0,  # 双十一
    12: 0.85, # 年末
}


# ── 统计分析 ──────────────────────────────────────────────────────────────

def _compute_note_stats(notes: list[dict]) -> dict:
    """
    计算笔记统计指标

    Returns:
        dict: 统计指标字典
    """
    if not notes:
        return {
            "total_notes": 0,
            "total_likes": 0,
            "total_collects": 0,
            "total_comments": 0,
            "total_shares": 0,
            "avg_likes": 0.0,
            "avg_collects": 0.0,
            "avg_comments": 0.0,
            "avg_shares": 0.0,
            "max_likes": 0,
            "max_collects": 0,
            "max_comments": 0,
            "max_shares": 0,
            "notes_with_video": 0,
            "notes_with_images": 0,
            "notes_with_tags": 0,
            "notes_repaired": 0,
            "engagement_rate_avg": 0.0,
        }

    total_likes = 0
    total_collects = 0
    total_comments = 0
    total_shares = 0
    max_likes = 0
    max_collects = 0
    max_comments = 0
    max_shares = 0
    notes_with_video = 0
    notes_with_images = 0
    notes_with_tags = 0
    notes_repaired = 0
    engagement_rates = []

    for note in notes:
        interact = note.get("interact", {})
        likes = interact.get("liked_count", 0) or 0
        collects = interact.get("collected_count", 0) or 0
        comments = interact.get("comment_count", 0) or 0
        shares = interact.get("share_count", 0) or 0

        total_likes += likes
        total_collects += collects
        total_comments += comments
        total_shares += shares

        max_likes = max(max_likes, likes)
        max_collects = max(max_collects, collects)
        max_comments = max(max_comments, comments)
        max_shares = max(max_shares, shares)

        note_type = note.get("type", note.get("note_type", "normal"))
        if note_type == "video":
            notes_with_video += 1

        images = note.get("images", [])
        if images and len(images) > 0:
            notes_with_images += 1

        tags = note.get("tags", [])
        if tags and len(tags) > 0:
            notes_with_tags += 1

        meta = note.get("_meta", {})
        if meta.get("repaired"):
            notes_repaired += 1

        # 互动率 = (点赞+收藏+评论+分享) / (粉丝数估算) 简化为总和
        engagement_rates.append(likes + collects + comments + shares)

    n = len(notes)
    avg_likes = round(total_likes / n, 2)
    avg_collects = round(total_collects / n, 2)
    avg_comments = round(total_comments / n, 2)
    avg_shares = round(total_shares / n, 2)

    # 平均互动量
    engagement_rate_avg = round(sum(engagement_rates) / n, 2) if n > 0 else 0.0

    return {
        "total_notes": n,
        "total_likes": total_likes,
        "total_collects": total_collects,
        "total_comments": total_comments,
        "total_shares": total_shares,
        "avg_likes": avg_likes,
        "avg_collects": avg_collects,
        "avg_comments": avg_comments,
        "avg_shares": avg_shares,
        "max_likes": max_likes,
        "max_collects": max_collects,
        "max_comments": max_comments,
        "max_shares": max_shares,
        "notes_with_video": notes_with_video,
        "notes_with_images": notes_with_images,
        "notes_with_tags": notes_with_tags,
        "notes_repaired": notes_repaired,
        "engagement_rate_avg": engagement_rate_avg,
    }


# ── 单维度评分 ──────────────────────────────────────────────────────────────

def _score_title_strategy(notes: list[dict]) -> dict:
    """D1: 标题策略评分"""
    total_score = 0.0
    title_types = {"测评型": 0, "种草型": 0, "教程型": 0, "经验型": 0, "其他": 0}

    for note in notes:
        title = note.get("title", "")
        content = note.get("content", "")
        text = (title + " " + content).lower()

        max_keyword_score = 0.0
        detected_type = "其他"

        for keyword, score in TITLE_KEYWORD_WEIGHTS.items():
            if keyword in text:
                if score > max_keyword_score:
                    max_keyword_score = score
                    if keyword in ["测评", "对比"]:
                        detected_type = "测评型"
                    elif keyword in ["种草", "好物", "必买", "回购"]:
                        detected_type = "种草型"
                    elif keyword in ["教程", "攻略", "技巧"]:
                        detected_type = "教程型"
                    elif keyword in ["分享", "我的", "使用感"]:
                        detected_type = "经验型"

        title_types[detected_type] += 1
        total_score += max_keyword_score

    avg_score = round(total_score / len(notes), 2) if notes else 0.0
    dominant_type = max(title_types, key=title_types.get) if notes else "其他"

    return {
        "dimension": "D1_标题策略",
        "score": avg_score,
        "dominant_type": dominant_type,
        "type_distribution": title_types,
        "summary": f"主要采用{detected_type}风格，平均关键词匹配度{avg_score:.0%}",
    }


def _score_content_framework(notes: list[dict]) -> dict:
    """D2: 内容框架评分"""
    total_score = 0.0
    frameworks_detected = []

    for note in notes:
        content = note.get("content", "")
        text = content.lower()

        max_matches = 0
        detected_framework = "其他"

        for framework, keywords in CONTENT_FRAMEWORK_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in text)
            if matches > max_matches:
                max_matches = matches
                detected_framework = framework

        frameworks_detected.append(detected_framework)
        # 得分 = 匹配关键词数 / 期望数(3)
        score = min(1.0, max_matches / 3)
        total_score += score

    avg_score = round(total_score / len(notes), 2) if notes else 0.0

    from collections import Counter
    framework_dist = dict(Counter(frameworks_detected))
    dominant_framework = max(framework_dist, key=framework_dist.get) if framework_dist else "其他"

    return {
        "dimension": "D2_内容框架",
        "score": avg_score,
        "dominant_framework": dominant_framework,
        "framework_distribution": framework_dist,
        "summary": f"内容框架以{dominant_framework}为主，平均结构化程度{avg_score:.0%}",
    }


def _score_visual_style(notes: list[dict]) -> dict:
    """D3: 视觉风格评分"""
    total_score = 0.0
    styles_detected = []

    for note in notes:
        content = note.get("content", "")
        images = note.get("images", [])
        text = content.lower()

        max_matches = 0
        detected_style = "其他"

        for style, keywords in VISUAL_STYLE_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in text)
            if matches > max_matches:
                max_matches = matches
                detected_style = style

        styles_detected.append(detected_style)
        # 有图片加分
        has_images = 1 if images and len(images) > 0 else 0
        score = min(1.0, (max_matches / 2 + has_images * 0.5))
        total_score += score

    avg_score = round(total_score / len(notes), 2) if notes else 0.0

    from collections import Counter
    style_dist = dict(Counter(styles_detected))
    dominant_style = max(style_dist, key=style_dist.get) if style_dist else "其他"

    return {
        "dimension": "D3_视觉风格",
        "score": avg_score,
        "dominant_style": dominant_style,
        "style_distribution": style_dist,
        "summary": f"视觉风格以{dominant_style}为主，平均匹配度{avg_score:.0%}",
    }


def _score_interaction_strategy(notes: list[dict]) -> dict:
    """D4: 互动策略评分"""
    total_score = 0.0
    strategies_detected = []

    for note in notes:
        content = note.get("content", "")
        interact = note.get("interact", {})
        text = content.lower()

        max_matches = 0
        detected_strategy = "其他"

        for strategy, keywords in INTERACT_STYLE_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in text)
            if matches > max_matches:
                max_matches = matches
                detected_strategy = strategy

        strategies_detected.append(detected_strategy)
        # 互动量也影响评分
        total_interact = (
            (interact.get("liked_count", 0) or 0)
            + (interact.get("comment_count", 0) or 0)
        )
        interact_bonus = min(1.0, total_interact / 1000)
        score = min(1.0, (max_matches / 2 + interact_bonus * 0.5))
        total_score += score

    avg_score = round(total_score / len(notes), 2) if notes else 0.0

    from collections import Counter
    strategy_dist = dict(Counter(strategies_detected))
    dominant_strategy = max(strategy_dist, key=strategy_dist.get) if strategy_dist else "其他"

    return {
        "dimension": "D4_互动策略",
        "score": avg_score,
        "dominant_strategy": dominant_strategy,
        "strategy_distribution": strategy_dist,
        "summary": f"互动策略以{dominant_strategy}为主，平均策略有效性{avg_score:.0%}",
    }


def _score_commercial_potential(notes: list[dict]) -> dict:
    """D5: 商业化潜力评估"""
    total_score = 0.0
    levels_detected = []

    for note in notes:
        content = note.get("content", "")
        text = content.lower()

        max_matches = 0
        detected_level = "低"

        for level, keywords in COMMERCIAL_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in text)
            if matches > max_matches:
                max_matches = matches
                detected_level = level

        levels_detected.append(detected_level)

        # 高=1.0, 中=0.6, 低=0.3
        level_score = {"高": 1.0, "中": 0.6, "低": 0.3}.get(detected_level, 0.3)
        score = min(1.0, level_score * (1 + max_matches * 0.1))
        total_score += score

    avg_score = round(total_score / len(notes), 2) if notes else 0.0

    from collections import Counter
    level_dist = dict(Counter(levels_detected))

    return {
        "dimension": "D5_商业化潜力",
        "score": avg_score,
        "level_distribution": level_dist,
        "summary": f"商业化潜力{'高' if level_dist.get('高', 0) > len(notes) * 0.3 else '中低'}，平均潜力{avg_score:.0%}",
    }


def _score_tag_quality(notes: list[dict]) -> dict:
    """D6: 标签质量评估"""
    total_score = 0.0
    total_tag_count = 0
    notes_with_good_tags = 0

    for note in notes:
        tags = note.get("tags", [])
        tag_count = len(tags) if tags else 0
        total_tag_count += tag_count

        # 标签数量评分 (3-8个为最佳)
        if tag_count == 0:
            count_score = 0.0
        elif 1 <= tag_count <= 2:
            count_score = 0.5
        elif 3 <= tag_count <= 8:
            count_score = 1.0
        else:  # > 8
            count_score = 0.7

        if tag_count >= 3:
            notes_with_good_tags += 1

        total_score += count_score

    avg_score = round(total_score / len(notes), 2) if notes else 0.0
    avg_tag_count = round(total_tag_count / len(notes), 1) if notes else 0.0
    good_tag_ratio = round(notes_with_good_tags / len(notes), 2) if notes else 0.0

    return {
        "dimension": "D6_标签质量",
        "score": avg_score,
        "avg_tag_count": avg_tag_count,
        "good_tag_ratio": good_tag_ratio,
        "total_tags": total_tag_count,
        "summary": f"平均{avg_tag_count}个标签/笔记，{good_tag_ratio:.0%}的笔记标签质量达标",
    }


def _score_temporal_distribution(notes: list[dict]) -> dict:
    """D7: 时间分布评估"""
    if not notes:
        return {
            "dimension": "D7_时间分布",
            "score": 0.0,
            "months_active": 0,
            "distribution": {},
            "summary": "无时间数据",
        }

    from collections import Counter
    months = []
    for note in notes:
        created_at = note.get("created_at", "")
        if created_at:
            # 支持 YYYY-MM-DD 和 YYYY/MM/DD 格式
            parts = created_at.replace("/", "-").split("-")
            if len(parts) >= 2:
                try:
                    month = int(parts[1])
                    if 1 <= month <= 12:
                        months.append(month)
                except (ValueError, IndexError):
                    pass

    if not months:
        return {
            "dimension": "D7_时间分布",
            "score": 0.0,
            "months_active": 0,
            "distribution": {},
            "summary": "无法解析时间数据",
        }

    month_dist = dict(Counter(months))
    months_active = len(month_dist)

    # 评分: 活跃月份越多且分布均匀越好
    if months_active == 0:
        temporal_score = 0.0
    elif months_active == 1:
        temporal_score = 0.3
    elif months_active <= 3:
        temporal_score = 0.5
    elif months_active <= 6:
        temporal_score = 0.7
    else:
        temporal_score = 1.0

    # 活跃月份加权得分
    weighted_score = 0.0
    for month, count in month_dist.items():
        weight = MONTH_WEIGHTS.get(month, 0.8)
        weighted_score += count * weight

    total_notes = sum(month_dist.values())
    weighted_avg = round(weighted_score / total_notes, 2) if total_notes > 0 else 0.0

    return {
        "dimension": "D7_时间分布",
        "score": round(temporal_score * weighted_avg, 2),
        "months_active": months_active,
        "distribution": month_dist,
        "weighted_avg": weighted_avg,
        "summary": f"覆盖{months_active}个月份发布，{'淡旺季' if months_active <= 3 else '全年稳定'}更新",
    }


def _score_content_diversity(notes: list[dict]) -> dict:
    """D8: 内容多样性评估"""
    if not notes:
        return {
            "dimension": "D8_内容多样性",
            "score": 0.0,
            "unique_content_words": 0,
            "content_types": {},
            "summary": "无数据",
        }

    from collections import Counter

    # 统计内容类型分布
    content_types = Counter()
    all_words = []

    for note in notes:
        content = note.get("content", "")
        title = note.get("title", "")

        # 分类
        text = (content + " " + title).lower()
        if any(kw in text for kw in ["测评", "对比", "使用感"]):
            content_types["测评类"] += 1
        elif any(kw in text for kw in ["教程", "攻略", "怎么", "如何"]):
            content_types["教程类"] += 1
        elif any(kw in text for kw in ["种草", "好物", "推荐"]):
            content_types["种草类"] += 1
        elif any(kw in text for kw in ["日常", "分享", "我的"]):
            content_types["日常类"] += 1
        else:
            content_types["其他"] += 1

        # 简单词统计
        words = text.split()
        all_words.extend(words[:50])  # 每篇取前50词

    n = len(notes)
    type_diversity = len(content_types) / 5.0  # 最多5类
    word_diversity = len(set(all_words)) / max(len(all_words), 1)

    # 综合得分
    score = round((type_diversity + word_diversity) / 2, 2)

    return {
        "dimension": "D8_内容多样性",
        "score": score,
        "type_diversity": round(type_diversity, 2),
        "word_diversity": round(word_diversity, 2),
        "content_types": dict(content_types),
        "summary": f"内容类型分布{len(content_types)}种，词汇多样性{word_diversity:.0%}",
    }


def _score_image_quality(notes: list[dict]) -> dict:
    """D9: 图片质量评估"""
    total_score = 0.0
    notes_with_multiple_images = 0
    total_images = 0

    for note in notes:
        images = note.get("images", [])
        image_count = len(images) if images else 0
        total_images += image_count

        if image_count >= 3:
            notes_with_multiple_images += 1
            # 3-9张为最佳
            count_score = 1.0
        elif image_count == 2:
            count_score = 0.7
        elif image_count == 1:
            count_score = 0.4
        else:
            count_score = 0.0

        total_score += count_score

    avg_score = round(total_score / len(notes), 2) if notes else 0.0
    multi_image_ratio = round(notes_with_multiple_images / len(notes), 2) if notes else 0.0
    avg_images_per_note = round(total_images / len(notes), 1) if notes else 0.0

    return {
        "dimension": "D9_图片质量",
        "score": avg_score,
        "avg_images_per_note": avg_images_per_note,
        "multi_image_ratio": multi_image_ratio,
        "total_images": total_images,
        "summary": f"平均{avg_images_per_note}张图/笔记，{multi_image_ratio:.0%}笔记有多图",
    }


def _score_engagement_rate(notes: list[dict]) -> dict:
    """D10: 互动率评估"""
    if not notes:
        return {
            "dimension": "D10_互动率",
            "score": 0.0,
            "avg_engagement": 0.0,
            "summary": "无数据",
        }

    engagement_scores = []

    for note in notes:
        interact = note.get("interact", {})
        likes = interact.get("liked_count", 0) or 0
        collects = interact.get("collected_count", 0) or 0
        comments = interact.get("comment_count", 0) or 0
        shares = interact.get("share_count", 0) or 0

        total = likes + collects + comments + shares

        # 互动量评分 (对数刻度, 1000+为满分)
        import math
        if total == 0:
            score = 0.0
        else:
            score = min(1.0, math.log10(total + 1) / 3.0)  # log10(1000+1)≈3

        engagement_scores.append(score)

    avg_score = round(sum(engagement_scores) / len(engagement_scores), 2) if notes else 0.0
    avg_engagement = round(sum(e.get("liked_count", 0) or 0 + e.get("collected_count", 0) or 0 + e.get("comment_count", 0) or 0 + e.get("share_count", 0) or 0 for e in [n.get("interact", {}) for n in notes]) / len(notes), 1) if notes else 0.0

    return {
        "dimension": "D10_互动率",
        "score": avg_score,
        "avg_interaction": avg_engagement,
        "summary": f"平均互动量{avg_engagement:.0f}，互动率评分{avg_score:.0%}",
    }


def _score_follower_correlation(notes: list[dict]) -> dict:
    """D11: 粉丝互动相关性评估"""
    if not notes:
        return {
            "dimension": "D11_粉丝相关性",
            "score": 0.5,
            "correlations": {},
            "summary": "无数据，使用默认值",
        }

    # 评估点赞/收藏/评论比例是否健康
    total_likes = 0
    total_collects = 0
    total_comments = 0
    total_shares = 0

    for note in notes:
        interact = note.get("interact", {})
        total_likes += interact.get("liked_count", 0) or 0
        total_collects += interact.get("collected_count", 0) or 0
        total_comments += interact.get("comment_count", 0) or 0
        total_shares += interact.get("share_count", 0) or 0

    grand_total = total_likes + total_collects + total_comments + total_shares
    if grand_total == 0:
        return {
            "dimension": "D11_粉丝相关性",
            "score": 0.5,
            "correlations": {"likes_ratio": 0, "collects_ratio": 0, "comments_ratio": 0, "shares_ratio": 0},
            "summary": "无互动数据，使用默认值",
        }

    likes_ratio = round(total_likes / grand_total, 2)
    collects_ratio = round(total_collects / grand_total, 2)
    comments_ratio = round(total_comments / grand_total, 2)
    shares_ratio = round(total_shares / grand_total, 2)

    # 健康比例: 点赞50-70%, 收藏15-25%, 评论5-15%, 分享2-8%
    likes_health = 1.0 if 0.5 <= likes_ratio <= 0.7 else (0.5 if 0.3 <= likes_ratio <= 0.8 else 0.2)
    collects_health = 1.0 if 0.15 <= collects_ratio <= 0.25 else (0.5 if 0.1 <= collects_ratio <= 0.35 else 0.2)
    comments_health = 1.0 if 0.05 <= comments_ratio <= 0.15 else (0.5 if 0.02 <= comments_ratio <= 0.25 else 0.2)
    shares_health = 1.0 if 0.02 <= shares_ratio <= 0.08 else (0.5 if 0.01 <= shares_ratio <= 0.15 else 0.2)

    overall_score = round((likes_health + collects_health + comments_health + shares_health) / 4, 2)

    return {
        "dimension": "D11_粉丝相关性",
        "score": overall_score,
        "correlations": {
            "likes_ratio": likes_ratio,
            "collects_ratio": collects_ratio,
            "comments_ratio": comments_ratio,
            "shares_ratio": shares_ratio,
        },
        "health_assessment": {
            "likes": "健康" if likes_health == 1.0 else "偏高或偏低",
            "collects": "健康" if collects_health == 1.0 else "偏高或偏低",
            "comments": "健康" if comments_health == 1.0 else "偏高或偏低",
            "shares": "健康" if shares_health == 1.0 else "偏高或偏低",
        },
        "summary": f"互动结构{'健康' if overall_score >= 0.75 else '需优化'}，收藏率{collects_ratio:.0%}偏高关注转化{'强' if collects_ratio > 0.2 else '一般'}",
    }


# ── Step4 主类 ────────────────────────────────────────────────────────────

class BloggerAnalyzer:
    """
    11维度博主分析器

    依赖:
      - _score_title_strategy()
      - _score_content_framework()
      - _score_visual_style()
      - _score_interaction_strategy()
      - _score_commercial_potential()
      - _score_tag_quality()
      - _score_temporal_distribution()
      - _score_content_diversity()
      - _score_image_quality()
      - _score_engagement_rate()
      - _score_follower_correlation()
      - _compute_note_stats()

    输入:
      - notes: list[dict] (来自 step3 repaired 输出)

    输出:
      - 11维度分析结果
      - 统计指标
    """

    def __init__(
        self,
        output_dir: str = "./output",
    ):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def analyze_data_materials(self, notes: list[dict]) -> dict:
        """
        执行11维度分析

        Args:
            notes: 修复后的笔记列表

        Returns:
            dict: {dimensions: [...11维度], overall_score, summary}
        """
        print(f"[BloggerAnalyzer] 开始11维度分析, 笔记数={len(notes)}")

        # 逐维度计算
        dimension_scores = [
            _score_title_strategy(notes),
            _score_content_framework(notes),
            _score_visual_style(notes),
            _score_interaction_strategy(notes),
            _score_commercial_potential(notes),
            _score_tag_quality(notes),
            _score_temporal_distribution(notes),
            _score_content_diversity(notes),
            _score_image_quality(notes),
            _score_engagement_rate(notes),
            _score_follower_correlation(notes),
        ]

        # 综合得分 (各维度等权平均)
        overall = round(sum(d["score"] for d in dimension_scores) / len(dimension_scores), 2)

        print(f"[BloggerAnalyzer] 分析完成, 综合得分={overall:.2f}")
        for d in dimension_scores:
            print(f"  {d['dimension']}: {d['score']:.2f}")

        return {
            "dimensions": dimension_scores,
            "overall_score": overall,
            "summary": self._generate_summary(dimension_scores, overall),
        }

    def _generate_summary(self, dimensions: list[dict], overall: float) -> str:
        """生成分析摘要"""
        high_dims = [d for d in dimensions if d["score"] >= 0.7]
        low_dims = [d for d in dimensions if d["score"] < 0.5]

        summary_parts = [
            f"博主内容综合质量{overall:.0%}",
        ]
        if high_dims:
            high_names = [d["dimension"] for d in high_dims]
            summary_parts.append(f"优势: {', '.join(high_names)}")
        if low_dims:
            low_names = [d["dimension"] for d in low_dims]
            summary_parts.append(f"待提升: {', '.join(low_names)}")

        return "; ".join(summary_parts)


class Step4Analyzer:
    """
    Step 4 分析管道

    依赖:
      - BloggerAnalyzer
      - _compute_note_stats()

    输入:
      - {blogger_name}_repaired.json (Step3 产出)

    处理:
      1. BloggerAnalyzer.analyze_data_materials() → 11维度分析
      2. _compute_note_stats() → 数值统计
      3. 输出分析报告 + 统计文件

    输出:
      - {blogger_name}_analysis.json — 11维度分析报告
      - {blogger_name}_stats.json — 数值统计
    """

    def __init__(
        self,
        output_dir: str = "./output",
    ):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def run(self, repaired: dict) -> dict:
        """
        执行分析流程

        Args:
            repaired: 从 {blogger_name}_repaired.json 加载的数据
                    包含 {blogger_id, blogger_name, notes}

        Returns:
            dict: 分析结果摘要
        """
        blogger_name = repaired.get("blogger_name", repaired.get("blogger_id", "unknown"))
        notes = repaired.get("notes", [])
        print(f"[Step4Analyzer] 开始分析 blogger={blogger_name}, 笔记数={len(notes)}")

        # 11维度分析
        analyzer = BloggerAnalyzer(output_dir=self.output_dir)
        analysis_result = analyzer.analyze_data_materials(notes)

        # 数值统计
        stats = _compute_note_stats(notes)

        # 写入分析报告
        analysis_path = os.path.join(self.output_dir, f"{blogger_name}_analysis.json")
        with open(analysis_path, "w", encoding="utf-8") as f:
            json.dump({
                "blogger_name": blogger_name,
                "blogger_id": repaired.get("blogger_id"),
                "total_notes": len(notes),
                "overall_score": analysis_result["overall_score"],
                "summary": analysis_result["summary"],
                "dimensions": analysis_result["dimensions"],
            }, f, ensure_ascii=False, indent=2)

        # 写入统计文件
        stats_path = os.path.join(self.output_dir, f"{blogger_name}_stats.json")
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump({
                "blogger_name": blogger_name,
                "blogger_id": repaired.get("blogger_id"),
                "stats": stats,
            }, f, ensure_ascii=False, indent=2)

        print(f"[Step4Analyzer] 完成: 综合得分={analysis_result['overall_score']:.2f}")
        print(f"[Step4Analyzer] 产出: {analysis_path}")
        print(f"[Step4Analyzer] 统计: {stats_path}")

        return {
            "blogger_name": blogger_name,
            "total_notes": len(notes),
            "overall_score": analysis_result["overall_score"],
            "analysis_path": analysis_path,
            "stats_path": stats_path,
        }
