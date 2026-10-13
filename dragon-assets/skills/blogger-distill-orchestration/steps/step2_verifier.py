# -*- coding: utf-8 -*-
"""
Step2Verifier — 质量门控验证管道
来源: blogger-distill-orchestration SKILL.md (lines 90-119)

质量门控: QualityGateRunner + check_note_quality + V1-V6六门控
输出: {blogger_name}_verified.json + quality_report.json + failed_notes.json
"""

import json
import os
import sys
from typing import Any, Optional

# ── 质量门控常量 ──────────────────────────────────────────────────────────────

THRESHOLD_V1_CONTENT_COMPLETENESS = 0.5   # 正文完整度阈值
THRESHOLD_V3_TIME_FIELD = 0.8              # 时间字段阈值


# ── 质量等级 ────────────────────────────────────────────────────────────────

class QualityLevel:
    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"


# ── 单条笔记质量评估 ────────────────────────────────────────────────────────

def check_note_quality(note: dict) -> dict:
    """
    检查单条笔记质量，返回分级和六维评分

    质量门控 (SKILL.md lines 98-103):
      - V1 阻断: 正文完整度 <50% → sys.exit(1)
      - V2 警告: 标题完整度
      - V3 警告: 时间字段
      - V4 警告: 图片数量
      - V5 警告: 标签覆盖率
      - V6 阻断: 产出文件不存在 → sys.exit(1)

    质量等级:
      - complete: 所有字段完整
      - partial: 必需字段有，次要字段缺
      - failed: 核心字段缺失或质量严重不足

    Returns:
        dict: {level, scores, reason, blocking}
    """
    scores = {}
    blocking = []
    warnings = []

    # ── V1: 正文完整度 (阻断) ──────────────────────────────────────────────
    content = note.get("content", "")
    content_len = len(content) if content else 0
    # 正文完整度: 字符数/期望长度 (假设期望>=200字符)
    v1_score = min(1.0, content_len / 200.0)
    scores["v1_content_completeness"] = v1_score
    if v1_score < THRESHOLD_V1_CONTENT_COMPLETENESS:
        blocking.append(f"V1阻断: 正文完整度={v1_score:.2f} < {THRESHOLD_V1_CONTENT_COMPLETENESS}")

    # ── V2: 标题完整度 (警告) ────────────────────────────────────────────
    title = note.get("title", "")
    v2_score = 1.0 if (title and len(title) >= 5) else 0.0
    scores["v2_title_completeness"] = v2_score
    if v2_score < 0.5:
        warnings.append(f"V2警告: 标题{'缺失' if not title else '过短'}")

    # ── V3: 时间字段 (警告) ───────────────────────────────────────────────
    created_at = note.get("created_at", "")
    v3_score = 1.0 if created_at else 0.0
    scores["v3_time_field"] = v3_score
    if v3_score < THRESHOLD_V3_TIME_FIELD:
        warnings.append(f"V3警告: 时间字段{'缺失' if not created_at else '无效'}")

    # ── V4: 图片数量 (警告) ─────────────────────────────────────────────
    images = note.get("images", [])
    v4_score = min(1.0, len(images) / 3.0)  # 3张图=满分
    scores["v4_image_count"] = v4_score
    if v4_score < 0.5:
        warnings.append(f"V4警告: 图片数量={len(images)} < 3")

    # ── V5: 标签覆盖率 (警告) ───────────────────────────────────────────
    tags = note.get("tags", [])
    v5_score = min(1.0, len(tags) / 3.0)  # 3个标签=满分
    scores["v5_tag_coverage"] = v5_score
    if v5_score < 0.3:
        warnings.append(f"V5警告: 标签数量={len(tags)} < 1")

    # ── V6: 互动数据完整性 (阻断) ───────────────────────────────────────
    interact = note.get("interact", {})
    v6_score = 1.0 if (interact and interact.get("liked_count") is not None) else 0.0
    scores["v6_interact_data"] = v6_score
    if v6_score == 0.0:
        blocking.append("V6阻断: 互动数据缺失")

    # ── 质量等级判定 ──────────────────────────────────────────────────────
    if blocking:
        # 有阻断门控触发
        return {
            "level": QualityLevel.FAILED,
            "scores": scores,
            "blocking": blocking,
            "warnings": warnings,
            "reason": "; ".join(blocking + warnings),
        }
    elif warnings:
        return {
            "level": QualityLevel.PARTIAL,
            "scores": scores,
            "blocking": [],
            "warnings": warnings,
            "reason": "; ".join(warnings),
        }
    else:
        return {
            "level": QualityLevel.COMPLETE,
            "scores": scores,
            "blocking": [],
            "warnings": [],
            "reason": "所有门控通过",
        }


# ── 批量质量评估器 ─────────────────────────────────────────────────────────

class QualityGateRunner:
    """
    批量质量评估器
    执行V1-V6六门控，V1/V6阻断，V2-V5警告
    """

    def __init__(
        self,
        threshold_v1: float = THRESHOLD_V1_CONTENT_COMPLETENESS,
        threshold_v3: float = THRESHOLD_V3_TIME_FIELD,
        blocking: bool = True,
    ):
        self.threshold_v1 = threshold_v1
        self.threshold_v3 = threshold_v3
        self.blocking = blocking

    def run_all(self, notes: list[dict], blogger_profile: Optional[dict] = None) -> dict:
        """
        批量执行质量门控

        Args:
            notes: 笔记列表（来自 step1 raw 输出）
            blogger_profile: 博主画像（可选）

        Returns:
            dict: {
                passed: bool,
                summary: str,
                passed_notes: list[dict],
                failed_notes: list[dict],
                quality_report: dict
            }
        """
        passed_notes = []
        failed_notes = []
        quality_details = []

        v1_blocking = []
        v6_blocking = []
        v2_warnings = []
        v3_warnings = []
        v4_warnings = []
        v5_warnings = []

        for note in notes:
            result = check_note_quality(note)

            # 添加质量评分到笔记
            note_with_quality = dict(note)
            note_with_quality["_quality"] = result

            # 统计门控
            if result["level"] == QualityLevel.FAILED:
                # 检查是否有阻断门控
                for b in result["blocking"]:
                    if b.startswith("V1"):
                        v1_blocking.append((note.get("id", ""), b))
                    elif b.startswith("V6"):
                        v6_blocking.append((note.get("id", ""), b))

                failed_notes.append({
                    "note_id": note.get("id", ""),
                    "reason": result["reason"],
                    "blocking": result["blocking"],
                    "scores": result["scores"],
                })
                quality_details.append({
                    "note_id": note.get("id", ""),
                    "level": result["level"],
                    "scores": result["scores"],
                    "reason": result["reason"],
                    "passed": False,
                })
            else:
                passed_notes.append(note_with_quality)
                quality_details.append({
                    "note_id": note.get("id", ""),
                    "level": result["level"],
                    "scores": result["scores"],
                    "reason": result["reason"],
                    "passed": True,
                })

            # 收集警告
            for w in result["warnings"]:
                if w.startswith("V2"):
                    v2_warnings.append((note.get("id", ""), w))
                elif w.startswith("V3"):
                    v3_warnings.append((note.get("id", ""), w))
                elif w.startswith("V4"):
                    v4_warnings.append((note.get("id", ""), w))
                elif w.startswith("V5"):
                    v5_warnings.append((note.get("id", ""), w))

        # 汇总报告
        total = len(notes)
        passed_count = len(passed_notes)
        failed_count = len(failed_notes)
        complete_count = sum(1 for d in quality_details if d["level"] == QualityLevel.COMPLETE)
        partial_count = sum(1 for d in quality_details if d["level"] == QualityLevel.PARTIAL)

        summary_parts = []
        if v1_blocking:
            summary_parts.append(f"V1阻断: {len(v1_blocking)}条")
        if v6_blocking:
            summary_parts.append(f"V6阻断: {len(v6_blocking)}条")
        if v2_warnings:
            summary_parts.append(f"V2警告: {len(v2_warnings)}条")
        if v3_warnings:
            summary_parts.append(f"V3警告: {len(v3_warnings)}条")
        if v4_warnings:
            summary_parts.append(f"V4警告: {len(v4_warnings)}条")
        if v5_warnings:
            summary_parts.append(f"V5警告: {len(v5_warnings)}条")

        summary = f"通过{passed_count}/{total}条(complete:{complete_count}, partial:{partial_count}, failed:{failed_count})"
        if summary_parts:
            summary += " | " + ", ".join(summary_parts)

        # 构建质量报告
        quality_report = {
            "total": total,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "complete_count": complete_count,
            "partial_count": partial_count,
            "v1_blocking_count": len(v1_blocking),
            "v6_blocking_count": len(v6_blocking),
            "v2_warning_count": len(v2_warnings),
            "v3_warning_count": len(v3_warnings),
            "v4_warning_count": len(v4_warnings),
            "v5_warning_count": len(v5_warnings),
            "v1_blocking": v1_blocking,
            "v6_blocking": v6_blocking,
            "v2_warnings": v2_warnings[:20],   # 只记录前20条
            "v3_warnings": v3_warnings[:20],
            "v4_warnings": v4_warnings[:20],
            "v5_warnings": v5_warnings[:20],
            "details": quality_details,
            "blogger_profile": blogger_profile or {},
        }

        # 判断是否通过（无阻断门控）
        passed = len(v1_blocking) == 0 and len(v6_blocking) == 0

        return {
            "passed": passed,
            "summary": summary,
            "passed_notes": passed_notes,
            "failed_notes": failed_notes,
            "quality_report": quality_report,
        }


# ── Step2 主类 ─────────────────────────────────────────────────────────────

class Step2Verifier:
    """
    Step 2 质量门控验证管道

    依赖:
      - QualityGateRunner (crawler-quality-grader P1-1)
      - check_note_quality()

    输入:
      - notes_raw.json (Step1 产出)

    处理:
      1. QualityGateRunner.run_all() → 批量质量评估（V1-V6六门控）
      2. V1/V6 阻断门控：正文完整度<50% 或 互动数据缺失 → sys.exit(1)
      3. V2-V5 警告门控：记录但不阻断
      4. check_note_quality() → 单条分级 complete/partial/failed

    输出:
      - {blogger_name}_verified.json — 通过质量门控的笔记
      - quality_report.json — V1-V6 质量报告
      - failed_notes.json — failed 笔记（含 reason）

    关键参数:
      - threshold_v1: V1 正文完整度阈值（默认0.5）
      - threshold_v3: V3 时间字段阈值（默认0.8）
      - blocking: 是否启用阻断门控（默认True）
    """

    def __init__(
        self,
        output_dir: str = "./output",
        threshold_v1: float = THRESHOLD_V1_CONTENT_COMPLETENESS,
        threshold_v3: float = THRESHOLD_V3_TIME_FIELD,
        blocking: bool = True,
    ):
        self.output_dir = output_dir
        self.threshold_v1 = threshold_v1
        self.threshold_v3 = threshold_v3
        self.blocking = blocking
        os.makedirs(output_dir, exist_ok=True)

    def run(self, notes_raw: dict) -> dict:
        """
        执行质量门控流程

        Args:
            notes_raw: 从 {blogger_name}_raw.json 加载的数据
                     包含 {blogger_id, blogger_name, total_list, collected, failed, notes}

        Returns:
            dict: 验证结果摘要
        """
        blogger_name = notes_raw.get("blogger_name", notes_raw.get("blogger_id", "unknown"))
        print(f"[Step2Verifier] 开始质量门控 blogger={blogger_name}")

        notes = notes_raw.get("notes", [])
        total = len(notes)
        print(f"[Step2Verifier] 待验证笔记: {total} 条")

        # 执行批量质量评估
        runner = QualityGateRunner(
            threshold_v1=self.threshold_v1,
            threshold_v3=self.threshold_v3,
            blocking=self.blocking,
        )
        result = runner.run_all(notes, blogger_profile=notes_raw.get("blogger_id"))

        passed_notes = result["passed_notes"]
        failed_notes = result["failed_notes"]
        quality_report = result["quality_report"]

        print(f"[Step2Verifier] 质量评估完成: {result['summary']}")

        # ── V1/V6 阻断门控检查 ────────────────────────────────────────────
        if not result["passed"] and self.blocking:
            v1_blocks = quality_report.get("v1_blocking_count", 0)
            v6_blocks = quality_report.get("v6_blocking_count", 0)

            if v1_blocks > 0 or v6_blocks > 0:
                blocking_reasons = []
                if v1_blocks > 0:
                    blocking_reasons.append(f"V1正文完整度阻断({v1_blocks}条)")
                if v6_blocks > 0:
                    blocking_reasons.append(f"V6互动数据阻断({v6_blocks}条)")

                print(f"\n[阻断错误] V1/V6质量门控失败: {'; '.join(blocking_reasons)}")
                print(f"[阻断错误] {result['summary']}")

                # 写入失败笔记
                failed_path = os.path.join(
                    self.output_dir, f"{blogger_name}_failed_notes.json"
                )
                with open(failed_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "blogger_name": blogger_name,
                        "total": total,
                        "failed_count": len(failed_notes),
                        "failed_notes": failed_notes,
                        "blocking_reason": "; ".join(blocking_reasons),
                        "quality_report": quality_report,
                    }, f, ensure_ascii=False, indent=2)

                sys.exit(1)  # 阻断后续流程

        # ── 写入验证通过的笔记 ────────────────────────────────────────────
        verified_path = os.path.join(
            self.output_dir, f"{blogger_name}_verified.json"
        )
        verified_data = {
            "blogger_id": notes_raw.get("blogger_id"),
            "blogger_name": blogger_name,
            "total_input": total,
            "total_passed": len(passed_notes),
            "total_failed": len(failed_notes),
            "notes": passed_notes,
        }
        with open(verified_path, "w", encoding="utf-8") as f:
            json.dump(verified_data, f, ensure_ascii=False, indent=2)

        # ── 写入质量报告 ────────────────────────────────────────────────
        report_path = os.path.join(
            self.output_dir, f"{blogger_name}_quality_report.json"
        )
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(quality_report, f, ensure_ascii=False, indent=2)

        # ── 写入失败笔记（含 reason）─────────────────────────────────────
        failed_path = os.path.join(
            self.output_dir, f"{blogger_name}_failed_notes.json"
        )
        with open(failed_path, "w", encoding="utf-8") as f:
            json.dump({
                "blogger_name": blogger_name,
                "total": total,
                "failed_count": len(failed_notes),
                "failed_notes": failed_notes,
            }, f, ensure_ascii=False, indent=2)

        print(f"[Step2Verifier] 完成: 通过{len(passed_notes)}条, 失败{len(failed_notes)}条")
        print(f"[Step2Verifier] 产出: {verified_path}")
        print(f"[Step2Verifier] 报告: {report_path}")

        return {
            "blogger_name": blogger_name,
            "total_input": total,
            "passed": len(passed_notes),
            "failed": len(failed_notes),
            "complete": quality_report.get("complete_count", 0),
            "partial": quality_report.get("partial_count", 0),
            "verified_path": verified_path,
            "quality_report_path": report_path,
            "failed_notes_path": failed_path,
        }