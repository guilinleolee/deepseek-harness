# -*- coding: utf-8 -*-
"""
Step3Repairer — 补全/自愈合并管道
来源: blogger-distill-orchestration SKILL.md (lines 121-145)

自愈管道：repair_incomplete_notes + merge_note_supplement + _is_empty_value
输出: {blogger_name}_repaired.json + repair_summary.json
"""

import json
import os
import time
from typing import Any, Optional

from .step1_collector import UniversalApiClient


# ── 空值判定阈值 ──────────────────────────────────────────────────────────────

# 正文完整度下限（低于此值触发补全）
CONTENT_MIN_CHARS = 50

# 标签数量下限
TAGS_MIN_COUNT = 1

# 图片数量下限
IMAGES_MIN_COUNT = 0  # 0张不触发


# ── 补全策略 ────────────────────────────────────────────────────────────────

# 交互数据缺失时的占位值
INTERACT_DEFAULTS = {
    "liked_count": 0,
    "collected_count": 0,
    "comment_count": 0,
    "share_count": 0,
}


def _is_empty_value(value: Any) -> bool:
    """
    判断字段是否为空
    核心逻辑: 交互数字"0"视为空，触发补全
    """
    if value is None:
        return True
    if isinstance(value, (int, float)) and value == 0:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    if isinstance(value, list) and len(value) == 0:
        return True
    if isinstance(value, dict) and len(value) == 0:
        return True
    return False


def merge_note_supplement(note: dict, supplement: dict) -> dict:
    """
    合并补全数据到笔记
    策略: 只填充空字段，保留原始高优先级数据

    Args:
        note: 原始笔记（含 _quality 评分）
        supplement: API返回的补全数据

    Returns:
        dict: 合并后的笔记
    """
    merged = dict(note)

    # 遍历补全字段
    for key, value in supplement.items():
        if key.startswith("_"):
            # 元字段不合并
            continue

        if key == "interact":
            # 交互字段: 只补零值
            existing = merged.get("interact", {})
            if not isinstance(existing, dict):
                existing = {}
            for sub_key, sub_value in value.items():
                if _is_empty_value(existing.get(sub_key)):
                    existing[sub_key] = sub_value
            merged["interact"] = existing
        elif key == "tags":
            # 标签: 追加不重复
            existing = set(merged.get("tags", []))
            if isinstance(value, list):
                for tag in value:
                    if tag not in existing:
                        existing.add(tag)
            merged["tags"] = list(existing)
        elif key == "images":
            # 图片: 保留现有，追加新的
            existing = merged.get("images", [])
            if isinstance(value, list):
                existing_ids = {img.get("url", img.get("id", "")) for img in existing}
                for img in value:
                    img_id = img.get("url", img.get("id", ""))
                    if img_id not in existing_ids:
                        existing.append(img)
            merged["images"] = existing
        elif key == "content":
            # 正文: 现有太短则替换
            existing_content = merged.get("content", "")
            if len(existing_content) < len(str(value)):
                merged["content"] = value
        else:
            # 其他字段: 空则填充
            if _is_empty_value(merged.get(key)):
                merged[key] = value

    # 标记已补全
    if "_meta" not in merged:
        merged["_meta"] = {}
    merged["_meta"]["repaired"] = True
    merged["_meta"]["supplement_keys"] = list(supplement.keys())
    return merged


# ── 单条笔记补全评估 ──────────────────────────────────────────────────────

def assess_repair_need(note: dict) -> dict:
    """
    评估单条笔记的补全需求

    Returns:
        dict: {needs_repair, reasons, priority}
    """
    reasons = []
    priority = 0

    # V1: 正文内容不完整
    content = note.get("content", "")
    if len(content) < CONTENT_MIN_CHARS:
        reasons.append(f"正文过短({len(content)}<{CONTENT_MIN_CHARS})")
        priority = max(priority, 2)

    # V2: 标题缺失或过短
    title = note.get("title", "")
    if not title or len(title) < 5:
        reasons.append(f"标题{'缺失' if not title else '过短'}")
        priority = max(priority, 1)

    # V3: 时间字段缺失
    if _is_empty_value(note.get("created_at")):
        reasons.append("时间字段缺失")
        priority = max(priority, 1)

    # V4: 图片缺失
    images = note.get("images", [])
    if _is_empty_value(images) or len(images) < IMAGES_MIN_COUNT:
        reasons.append(f"图片缺失({len(images)}张)")
        priority = max(priority, 0)

    # V5: 标签缺失
    tags = note.get("tags", [])
    if len(tags) < TAGS_MIN_COUNT:
        reasons.append(f"标签缺失({len(tags)}<{TAGS_MIN_COUNT})")
        priority = max(priority, 1)

    # V6: 互动数据缺失或全零
    interact = note.get("interact", {})
    if _is_empty_value(interact) or all(
        _is_empty_value(interact.get(k)) for k in ["liked_count", "collected_count", "comment_count"]
    ):
        reasons.append("互动数据缺失")
        priority = max(priority, 2)

    return {
        "needs_repair": len(reasons) > 0,
        "reasons": reasons,
        "priority": priority,
    }


# ── 批量补全 ───────────────────────────────────────────────────────────

class Step3Repairer:
    """
    Step 3 补全/自愈合并管道

    依赖:
      - UniversalApiClient (step1_collector)
      - merge_note_supplement()
      - _is_empty_value()

    输入:
      - {blogger_name}_verified.json (Step2 产出)

    处理:
      1. assess_repair_need() → 评估每条笔记补全需求
      2. 只对 partial 笔记补全（complete 不动）
      3. merge_note_supplement() → 合并补全数据
      4. 交互数字"0" 视为空，触发补全

    输出:
      - {blogger_name}_repaired.json — 补全后的笔记列表
      - repair_summary.json — 补全摘要

    关键参数:
      - api_token: API认证令牌（用于补全API调用）
      - repair_priority: 仅补全>=此优先级的字段（默认0=全部）
    """

    def __init__(
        self,
        api_token: Optional[str] = None,
        output_dir: str = "./output",
        repair_priority: int = 0,
    ):
        self.api_token = api_token
        self.output_dir = output_dir
        self.repair_priority = repair_priority
        self.client = UniversalApiClient(api_token=api_token)
        os.makedirs(output_dir, exist_ok=True)

    def run(self, verified: dict) -> dict:
        """
        执行补全流程

        Args:
            verified: 从 {blogger_name}_verified.json 加载的数据
                    包含 {blogger_id, blogger_name, notes}

        Returns:
            dict: 补全结果摘要
        """
        blogger_name = verified.get("blogger_name", verified.get("blogger_id", "unknown"))
        notes = verified.get("notes", [])
        total = len(notes)
        print(f"[Step3Repairer] 开始补全 blogger={blogger_name}, 总数={total}")

        repaired_notes = []
        repair_details = []
        skipped = 0

        for note in notes:
            assessment = assess_repair_need(note)

            if not assessment["needs_repair"]:
                # complete笔记跳过
                note["_meta"] = note.get("_meta", {})
                note["_meta"]["repaired"] = False
                note["_meta"]["repaired_reason"] = "quality_complete"
                skipped += 1
                repaired_notes.append(note)
                continue

            if assessment["priority"] < self.repair_priority:
                # 优先级不足跳过
                note["_meta"] = note.get("_meta", {})
                note["_meta"]["repaired"] = False
                note["_meta"]["repaired_reason"] = "priority_low"
                skipped += 1
                repaired_notes.append(note)
                continue

            # 需要补全
            note_id = note.get("id", f"note_{note.get('title', '')[:20]}")
            print(f"[Step3Repairer] 补全笔记: {note_id}, 原因: {assessment['reasons']}")

            supplement = self._fetch_supplement(note)
            repaired_note = merge_note_supplement(note, supplement)

            # 验证补全效果
            post_repair = assess_repair_need(repaired_note)

            repair_details.append({
                "note_id": note_id,
                "priority": assessment["priority"],
                "pre_reasons": assessment["reasons"],
                "supplement_keys": list(supplement.keys()),
                "post_repaired": not post_repair["needs_repair"],
                "post_reasons": post_repair["reasons"],
            })

            repaired_notes.append(repaired_note)

        # 写入补全数据
        repaired_path = os.path.join(self.output_dir, f"{blogger_name}_repaired.json")
        with open(repaired_path, "w", encoding="utf-8") as f:
            json.dump({
                "blogger_id": verified.get("blogger_id"),
                "blogger_name": blogger_name,
                "total": total,
                "repaired_count": total - skipped,
                "skipped_count": skipped,
                "notes": repaired_notes,
            }, f, ensure_ascii=False, indent=2)

        # 写入补全摘要
        summary_path = os.path.join(self.output_dir, f"{blogger_name}_repair_summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump({
                "blogger_name": blogger_name,
                "total": total,
                "repaired_count": total - skipped,
                "skipped_count": skipped,
                "high_priority": sum(1 for d in repair_details if d["priority"] >= 2),
                "medium_priority": sum(1 for d in repair_details if d["priority"] == 1),
                "low_priority": sum(1 for d in repair_details if d["priority"] == 0),
                "successfully_repaired": sum(1 for d in repair_details if d["post_repaired"]),
                "still_needs_work": sum(1 for d in repair_details if not d["post_repaired"]),
                "details": repair_details,
            }, f, ensure_ascii=False, indent=2)

        print(f"[Step3Repairer] 完成: 补全{total - skipped}条, 跳过{skipped}条")
        print(f"[Step3Repairer] 产出: {repaired_path}")

        return {
            "blogger_name": blogger_name,
            "total": total,
            "repaired_count": total - skipped,
            "skipped_count": skipped,
            "repaired_path": repaired_path,
            "repair_summary_path": summary_path,
        }

    def _fetch_supplement(self, note: dict) -> dict:
        """
        获取补全数据（模拟实现）
        实际使用时应调用真实的小红书补全API
        """
        note_id = note.get("id", "")
        supplement = {}

        try:
            # 模拟API调用获取详情
            detail = self.client.fetch_note_detail(note_id)

            # 只取空字段
            if _is_empty_value(note.get("content")) and not _is_empty_value(detail.get("content")):
                supplement["content"] = detail.get("content", "")

            if _is_empty_value(note.get("created_at")) and not _is_empty_value(detail.get("created_at")):
                supplement["created_at"] = detail.get("created_at", "")

            interact = note.get("interact", {})
            detail_interact = detail.get("interact", {})
            if isinstance(detail_interact, dict):
                interact_patch = {}
                for k, v in INTERACT_DEFAULTS.items():
                    if _is_empty_value(interact.get(k)) and not _is_empty_value(detail_interact.get(k)):
                        interact_patch[k] = detail_interact.get(k, v)
                if interact_patch:
                    supplement["interact"] = interact_patch

            if _is_empty_value(note.get("tags")) and not _is_empty_value(detail.get("tags")):
                supplement["tags"] = detail.get("tags", [])

            if _is_empty_value(note.get("images")) and not _is_empty_value(detail.get("images")):
                supplement["images"] = detail.get("images", [])

        except Exception:
            # API失败时使用默认值
            if _is_empty_value(note.get("interact", {}).get("liked_count")):
                supplement["interact"] = INTERACT_DEFAULTS.copy()

        return supplement
