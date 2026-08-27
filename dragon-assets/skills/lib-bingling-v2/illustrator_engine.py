# -*- coding: utf-8 -*-
"""
老李配图生成器 V1.0
认知锚点识别 + Shot List 生成 + PIL渲染
"""
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
import random


class AnchorType(Enum):
    """认知锚点类型"""
    CORE_JUDGMENT = "core_judgment"      # 核心判断
    PROCESS = "process"                  # 流程步骤
    COMPARISON = "comparison"             # 对比差异
    METAPHOR = "metaphor"                # 概念隐喻
    CASE_STUDY = "case_study"            # 案例故事
    PITFALL = "pitfall"                  # 常见误区
    EMOTIONAL = "emotional"              # 情感转折


@dataclass
class CognitiveAnchor:
    """认知锚点"""
    type: AnchorType
    concept: str
    description: str
    position: str = ""  # 在文章中的位置


@dataclass
class Shot:
    """配图Shot"""
    number: int
    position: str        # 插入位置
    type: str          # 图的类型
    concept: str        # 核心概念
    description: str   # 画面描述
    composition: str    # 构图建议
    color: str         # 主色调
    labels: List[str]  # 批注关键词
    keywords: List[str] # AI生图关键词


# ============================
# 一，认知锚点识别
# ============================

class ContentAnalyzer:
    """内容分析器 - 识别认知锚点"""

    # 关键词映射
    KEYWORD_PATTERNS = {
        AnchorType.CORE_JUDGMENT: [
            "是", "等于", "就是", "本质", "核心", "关键", "最重要",
            "副业是", "副业=", "主业是", "认知", "思维", "方法论"
        ],
        AnchorType.PROCESS: [
            "步骤", "流程", "方法", "怎么做", "如何", "首先", "其次",
            "第一", "第二", "第三", "7天", "30天", "落地", "执行"
        ],
        AnchorType.COMPARISON: [
            "vs", "对比", "不是", "而是", "之前", "之后", "错误",
            "正确", "优劣", "高效", "低效", "别人", "自己"
        ],
        AnchorType.METAPHOR: [
            "像", "如同", "比喻", "丹", "炉", "炼", "升级", "进化",
            "登山", "游泳", "开车", "打仗", "游戏"
        ],
        AnchorType.CASE_STUDY: [
            "案例", "故事", "例子", "我当年", "我有个", "朋友",
            "学员", "罗汉果", "19.80", "电商", "培训"
        ],
        AnchorType.PITFALL: [
            "坑", "误区", "错误", "不能", "不要", "避免", "陷阱",
            "降价", "白嫖", "免费", "盲目", "冲动"
        ],
        AnchorType.EMOTIONAL: [
            "低谷", "谷底", "反弹", "坚持", "失败", "成功", "勇气",
            "困难", "挑战", "突破", "成长", "蜕变"
        ]
    }

    def analyze(self, content: str) -> List[CognitiveAnchor]:
        """分析内容，识别认知锚点"""
        anchors = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue

            # 检测锚点类型
            for anchor_type, keywords in self.KEYWORD_PATTERNS.items():
                for keyword in keywords:
                    if keyword in line:
                        anchor = CognitiveAnchor(
                            type=anchor_type,
                            concept=self._extract_concept(line),
                            description=line,
                            position=self._detect_position(line, lines)
                        )
                        anchors.append(anchor)
                        break

        # 去重
        seen = set()
        unique_anchors = []
        for anchor in anchors:
            key = (anchor.type, anchor.concept)
            if key not in seen:
                seen.add(key)
                unique_anchors.append(anchor)

        return unique_anchors[:8]  # 最多8个

    def _extract_concept(self, line: str) -> str:
        """提取核心概念"""
        # 简化处理：取第一句或关键句
        if '。' in line:
            return line.split('。')[0][:50]
        return line[:50]

    def _detect_position(self, line: str, all_lines: List[str]) -> str:
        """检测在文章中的位置"""
        idx = all_lines.index(line) if line in all_lines else 0
        total = len(all_lines)

        if idx < total * 0.2:
            return "开篇"
        elif idx < total * 0.5:
            return "痛点"
        elif idx < total * 0.8:
            return "方法"
        else:
            return "结尾"


# ============================
# 二，Shot List 生成
# ============================

class ShotListGenerator:
    """Shot List 生成器"""

    # 老李品牌概念库
    BRAND_CONCEPTS = {
        AnchorType.CORE_JUDGMENT: [
            ("副业=第二颗丹", "画出丹炉，两颗丹，一大一小"),
            ("用以致学", "画出学习→实践→结果的循环"),
            ("定价=价值包装", "画出产品包装盒，金色蝴蝶结"),
        ],
        AnchorType.PROCESS: [
            ("7天落地", "画出7个脚印或7颗星星"),
            ("价值方程", "画出天平，两边分别是分子和分母"),
            ("ADJUST方法", "画出齿轮咬合"),
        ],
        AnchorType.METAPHOR: [
            ("炼丹", "画出丹炉，火焰，金光"),
            ("筑基", "画出山峰，攀登者"),
            ("修炼", "画出成长曲线，向上箭头"),
        ],
        AnchorType.PITFALL: [
            ("降价求量", "画出价格崩塌，箭头向下"),
            ("白嫖思维", "画出免费标签，零元"),
            ("盲目跟风", "画出人群，跟随"),
        ],
    }

    # 配色方案
    COLOR_SCHEMES = {
        AnchorType.CORE_JUDGMENT: ("金色", "#FFD700"),
        AnchorType.PROCESS: ("橙色", "#DD6B20"),
        AnchorType.COMPARISON: ("蓝色", "#3182CE"),
        AnchorType.METAPHOR: ("紫色", "#805AD5"),
        AnchorType.CASE_STUDY: ("金色", "#FFD700"),
        AnchorType.PITFALL: ("红色", "#E53E3E"),
        AnchorType.EMOTIONAL: ("橙色", "#DD6B20"),
    }

    def generate(self, anchors: List[CognitiveAnchor]) -> List[Shot]:
        """根据锚点生成Shot List"""
        shots = []

        for i, anchor in enumerate(anchors, 1):
            shot = Shot(
                number=i,
                position=anchor.position,
                type=anchor.type.value,
                concept=anchor.concept,
                description=self._generate_description(anchor),
                composition=self._generate_composition(anchor),
                color=self.COLOR_SCHEMES.get(anchor.type, ("金色", "#FFD700"))[1],
                labels=self._generate_labels(anchor),
                keywords=self._generate_keywords(anchor)
            )
            shots.append(shot)

        return shots

    def _generate_description(self, anchor: CognitiveAnchor) -> str:
        """生成画面描述"""
        # 从品牌概念库匹配
        for anchor_type, concepts in self.BRAND_CONCEPTS.items():
            if anchor.type == anchor_type:
                for concept, desc in concepts:
                    if concept in anchor.concept:
                        return desc

        # 默认描述
        return f"画出'{anchor.concept}'的核心含义"

    def _generate_composition(self, anchor: CognitiveAnchor) -> str:
        """生成构图建议"""
        compositions = {
            AnchorType.CORE_JUDGMENT: "居中构图，核心概念突出",
            AnchorType.PROCESS: "流程图式，步骤清晰",
            AnchorType.COMPARISON: "左右分栏，对比鲜明",
            AnchorType.METAPHOR: "隐喻场景，创意可视化",
            AnchorType.CASE_STUDY: "故事场景，有情境感",
            AnchorType.PITFALL: "警示风格，红色强调",
            AnchorType.EMOTIONAL: "情感表达，氛围渲染",
        }
        return compositions.get(anchor.type, "居中构图")

    def _generate_labels(self, anchor: CognitiveAnchor) -> List[str]:
        """生成批注关键词"""
        labels = []

        if anchor.type == AnchorType.CORE_JUDGMENT:
            labels = ["核心", "关键", anchor.concept[:5]]
        elif anchor.type == AnchorType.PROCESS:
            labels = ["步骤", "流程", "方法"]
        elif anchor.type == AnchorType.COMPARISON:
            labels = ["对比", "差异"]
        elif anchor.type == AnchorType.METAPHOR:
            labels = ["隐喻", "象征"]
        elif anchor.type == AnchorType.PITFALL:
            labels = ["坑", "误区", "注意"]
        elif anchor.type == AnchorType.EMOTIONAL:
            labels = ["突破", "成长"]

        return labels[:3]

    def _generate_keywords(self, anchor: CognitiveAnchor) -> List[str]:
        """生成AI生图关键词"""
        keywords = [
            "老李品牌", "商务手绘", "16:9", "白底",
            "黑色手绘线条", "金色强调", "留白充足"
        ]

        if anchor.type == AnchorType.CORE_JUDGMENT:
            keywords.extend(["概念图", "核心观点"])
        elif anchor.type == AnchorType.PROCESS:
            keywords.extend(["流程图", "步骤图"])
        elif anchor.type == AnchorType.COMPARISON:
            keywords.extend(["对比图", "左右分栏"])
        elif anchor.type == AnchorType.METAPHOR:
            keywords.extend(["隐喻图", "创意图"])
        elif anchor.type == AnchorType.PITFALL:
            keywords.extend(["警示图", "误区图"])
        elif anchor.type == AnchorType.EMOTIONAL:
            keywords.extend(["情感图", "励志图"])

        return keywords


# ============================
# 三，老李配图生成器
# ============================

class LaoLiIllustrator:
    """老李配图生成器"""

    def __init__(self):
        self.analyzer = ContentAnalyzer()
        self.shot_generator = ShotListGenerator()

    def analyze(self, content: str) -> List[CognitiveAnchor]:
        """分析内容，识别认知锚点"""
        return self.analyzer.analyze(content)

    def generate_shot_list(self, content: str) -> List[Shot]:
        """生成Shot List"""
        anchors = self.analyze(content)
        return self.shot_generator.generate(anchors)

    def print_shot_list(self, shots: List[Shot]) -> str:
        """格式化输出Shot List"""
        output = []
        output.append("\n" + "="*60)
        output.append("📋 老李配图 Shot List")
        output.append("="*60)

        for shot in shots:
            output.append(f"\n【Shot {shot.number}】")
            output.append(f"  位置: {shot.position}")
            output.append(f"  类型: {shot.type}")
            output.append(f"  概念: {shot.concept}")
            output.append(f"  描述: {shot.description}")
            output.append(f"  构图: {shot.composition}")
            output.append(f"  配色: {shot.color}")
            output.append(f"  批注: {', '.join(shot.labels)}")
            output.append(f"  关键词: {', '.join(shot.keywords)}")

        output.append("\n" + "="*60)
        return "\n".join(output)


# ============================
# 四，导出
# ============================

__all__ = [
    "CognitiveAnchor",
    "Shot",
    "AnchorType",
    "ContentAnalyzer",
    "ShotListGenerator",
    "LaoLiIllustrator",
]
